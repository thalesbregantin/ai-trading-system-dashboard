import pandas as pd
import numpy as np
import requests
import time
from tqdm import tqdm
from datetime import datetime, timedelta

# =====================
# Parâmetros otimizados (congelados)
# =====================
VS_CCY = "usd"
TOP_N = 30
REBALANCE_DAYS = 14
RISK_PCT = 0.04
STOP_LOSS_PCT = 0.03
TRAIL_K = 1.5
MIN_VOL_USD = 1e6
FEE_PCT = 0.001

# Pesos momentum otimizados
W7 = 0.8
W14 = 0.2
WV = 0.1

EXCLUDE_STABLES = {"tether","usd-coin","binance-usd","dai","true-usd","frax","usdd","paxos-standard"}
CG_BASE = "https://api.coingecko.com/api/v3"
INITIAL_CASH = 20.0

# =====================
# Funções CoinGecko (mesmas)
# =====================
def cg_get_markets(vs_currency="usd", per_page=100, page=1):
    url = f"{CG_BASE}/coins/markets"
    params = {"vs_currency": vs_currency, "order": "volume_desc",
              "per_page": per_page, "page": page, "price_change_percentage": "24h"}
    
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            time.sleep(2.0)
            return r.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < 2:
                print(f"Rate limit atingido, aguardando... (tentativa {attempt+1}/3)")
                time.sleep(60)
                continue
            raise

def cg_get_market_chart(coin_id, vs_currency="usd", days=180):
    url = f"{CG_BASE}/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days}
    
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            time.sleep(2.0)
            return r.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < 2:
                print(f"Rate limit atingido, aguardando... (tentativa {attempt+1}/3)")
                time.sleep(60)
                continue
            raise

def to_daily_series(chart):
    prices = pd.DataFrame(chart["prices"], columns=["ts","price"])
    vols = pd.DataFrame(chart["total_volumes"], columns=["ts","volume"])
    prices["date"] = pd.to_datetime(prices["ts"], unit="ms").dt.tz_localize("UTC").dt.normalize()
    vols["date"] = pd.to_datetime(vols["ts"], unit="ms").dt.tz_localize("UTC").dt.normalize()
    pr = prices.groupby("date")["price"].last().to_frame()
    vo = vols.groupby("date")["volume"].last().to_frame()
    df = pr.join(vo, how="inner")
    df.index.name = "date"
    return df

# =====================
# Preparação de dados
# =====================
def load_universe(top_n=TOP_N, days=365):
    print("Baixando universo top por volume...")
    mkts, page = [], 1
    while len(mkts) < top_n:
        batch = cg_get_markets(vs_currency=VS_CCY, per_page=100, page=page)
        if not batch: break
        mkts += batch
        page += 1
    universe = [m for m in mkts if m["id"] not in EXCLUDE_STABLES][:top_n]
    print(f"Universo: {len(universe)} moedas")

    data = {}
    for m in tqdm(universe, desc="Histórico"):
        cid = m["id"]
        try:
            ch = cg_get_market_chart(cid, vs_currency=VS_CCY, days=days)
            df = to_daily_series(ch)
            if len(df) < 60: 
                continue
            data[cid] = df
        except Exception:
            continue
    return data

def add_features(df):
    out = df.copy()
    out["ret7"] = out["price"].pct_change(7)
    out["ret14"] = out["price"].pct_change(14)
    out["vol14usd"] = out["volume"].rolling(14).mean()
    r = out["price"].pct_change().fillna(0.0)
    out["vol_std14"] = r.rolling(14).std()
    return out

# =====================
# Estratégia Momentum (congelada)
# =====================
def pick_momentum(dt, data):
    rows = []
    for cid, df in data.items():
        if dt not in df.index: continue
        r = df.loc[dt]
        if pd.isna(r["ret7"]) or pd.isna(r["ret14"]) or pd.isna(r["vol14usd"]): continue
        if r["vol14usd"] < MIN_VOL_USD: continue
        score = W7*r["ret7"] + W14*r["ret14"] + WV*np.log1p(r["vol14usd"])
        rows.append((cid, score))
    if not rows: return None
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows[0][0]

# =====================
# Backtest (mesmo código)
# =====================
def run_backtest(data, dates):
    cash = INITIAL_CASH
    coin, qty = None, 0.0
    equity = []
    trades = []
    
    for i in range(0, len(dates), REBALANCE_DAYS):
        dt = dates[i]

        def price(cid, d):
            df = data.get(cid)
            if df is None or d not in df.index: return None
            return float(df.loc[d, "price"])

        # marca equity intra-janelas
        if coin is not None:
            for j in range(REBALANCE_DAYS):
                if i+j >= len(dates): break
                dtn = dates[i+j]
                p = price(coin, dtn)
                equity.append({"date": dtn, "equity": cash + (qty*p if p else 0.0)})

        # decide ativo
        chosen = pick_momentum(dt, data)
        if chosen is None:
            continue
        p_in = price(chosen, dt)
        if p_in is None:
            continue

        # se posicionado em outro, zera
        if coin is not None and coin != chosen and qty > 0.0:
            p_sell = price(coin, dt)
            if p_sell:
                gross_proceeds = qty * p_sell
                fee = gross_proceeds * FEE_PCT
                cash = gross_proceeds - fee
                trades.append({"date": dt, "coin": coin, "side": "SELL", "price": p_sell, "qty": qty, "value": cash, "fee": fee})
            coin, qty = None, 0.0

        # compra com sizing por risco
        if coin != chosen:
            risk_amount = cash * RISK_PCT
            if risk_amount <= 0: break
            unit_risk = p_in * STOP_LOSS_PCT
            size_cash = min(cash, (risk_amount/max(unit_risk,1e-9))*p_in)
            if size_cash <= 0: continue
            fee = size_cash * FEE_PCT
            net_cash = size_cash - fee
            qty = net_cash / p_in
            cash -= size_cash
            coin = chosen
            trades.append({"date": dt, "coin": coin, "side": "BUY", "price": p_in, "qty": qty, "value": size_cash, "fee": fee})

        # trailing e stop intra-janela
        for j in range(REBALANCE_DAYS):
            if i+j >= len(dates): break
            dtn = dates[i+j]
            p = price(coin, dtn)
            vol = float(data[coin].loc[dtn, "vol_std14"] if coin else 0.0)
            trail_stop = p * (1.0 - TRAIL_K*max(vol,0.0)) if p is not None else None
            hard_stop = p * (1.0 - STOP_LOSS_PCT) if p is not None else None
            stop_level = max(hard_stop, trail_stop) if (hard_stop is not None and trail_stop is not None) else (hard_stop or trail_stop)
            if p is not None and stop_level is not None and p <= stop_level:
                gross_proceeds = qty * p
                fee = gross_proceeds * FEE_PCT
                cash = gross_proceeds - fee
                trades.append({"date": dtn, "coin": coin, "side": "SELL", "price": p, "qty": qty, "value": cash, "fee": fee})
                coin, qty = None, 0.0
                for k in range(j+1, REBALANCE_DAYS):
                    if i+k >= len(dates): break
                    equity.append({"date": dates[i+k], "equity": cash})
                break

    # flush final
    if coin is not None and qty > 0.0:
        last_price = data[coin].iloc[-1]["price"]
        equity.append({"date": dates[-1], "equity": cash + qty*last_price})
    
    eq_df = pd.DataFrame(equity).drop_duplicates(subset=["date"]).set_index("date").sort_index()
    tr_df = pd.DataFrame(trades)
    return eq_df, tr_df

# =====================
# Métricas
# =====================
def metrics(series):
    s = series.dropna()
    if len(s) < 2:
        return {}
    ret = s.pct_change().dropna()
    total = s.iloc[-1]/s.iloc[0]-1
    vol = ret.std()*np.sqrt(365) if len(ret)>0 else np.nan
    dd = (s/s.cummax()-1).min()
    sharpe = (ret.mean()*365)/vol if vol and vol>0 else np.nan
    return {
        "Initial": round(s.iloc[0],2),
        "Final": round(s.iloc[-1],2),
        "Total%": round(total*100,2),
        "Vol%pa": round(vol*100,2) if pd.notna(vol) else np.nan,
        "MaxDD%": round(dd*100,2) if pd.notna(dd) else np.nan,
        "Sharpe≈": round(sharpe,2) if pd.notna(sharpe) else np.nan
    }

# =====================
# Validação fora da amostra
# =====================
def validate_out_of_sample():
    print("=== VALIDAÇÃO FORA DA AMOSTRA ===")
    print("Testando estratégia em janelas diferentes...")
    
    # Janelas de teste
    windows = [
        {"name": "540-720 dias", "days": 720, "start_offset": 540},
        {"name": "720-900 dias", "days": 900, "start_offset": 720},
        {"name": "365-540 dias", "days": 540, "start_offset": 365},
    ]
    
    results = []
    
    for window in windows:
        print(f"\n--- Testando {window['name']} ---")
        
        # Carrega dados
        raw = load_universe(TOP_N, window["days"])
        if not raw:
            print("Sem dados suficientes.")
            continue
        
        # Adiciona features
        data = {cid: add_features(df) for cid, df in raw.items()}
        dates = sorted(set().union(*[df.index for df in data.values()]))
        dates = pd.to_datetime(dates)
        
        # Aplica offset para janela específica
        if len(dates) > window["start_offset"]:
            dates = dates[window["start_offset"]:]
        
        dates = dates[60:]  # warm-up
        
        if len(dates) < 30:
            print("Período muito curto após filtros.")
            continue
        
        print(f"Período: {dates[0].strftime('%Y-%m-%d')} a {dates[-1].strftime('%Y-%m-%d')}")
        print(f"Total de dias: {len(dates)}")
        
        # Executa backtest
        eq_df, tr_df = run_backtest(data, dates)
        
        if eq_df.empty:
            print("Sem resultados.")
            continue
        
        # Métricas
        m = metrics(eq_df["equity"])
        m["window"] = window["name"]
        m["period_days"] = len(dates)
        m["trades"] = len(tr_df)
        
        if not tr_df.empty and 'fee' in tr_df.columns:
            total_fees = tr_df['fee'].sum()
            total_volume = tr_df['value'].sum()
            fee_pct = (total_fees / total_volume) * 100 if total_volume > 0 else 0
            m["total_fees"] = round(total_fees, 2)
            m["fee_pct"] = round(fee_pct, 2)
        
        results.append(m)
        
        print(f"Resultados: {m['Total%']}% retorno, Sharpe {m['Sharpe≈']}, MaxDD {m['MaxDD%']}%")
        
        # Salva arquivos específicos
        eq_df.to_csv(f"equity_{window['name'].replace(' ', '_').replace('-', '_')}.csv")
        tr_df.to_csv(f"trades_{window['name'].replace(' ', '_').replace('-', '_')}.csv", index=False)
    
    # Resumo
    if results:
        print(f"\n=== RESUMO VALIDAÇÃO ===")
        df_results = pd.DataFrame(results)
        print(df_results[["window", "Total%", "Sharpe≈", "MaxDD%", "trades"]].to_string(index=False))
        
        # Salva resumo
        df_results.to_csv("validation_results.csv", index=False)
        print(f"\nArquivo salvo: validation_results.csv")
        
        # Análise de robustez
        avg_return = df_results["Total%"].mean()
        avg_sharpe = df_results["Sharpe≈"].mean()
        avg_dd = df_results["MaxDD%"].mean()
        
        print(f"\nMédias:")
        print(f"Retorno: {avg_return:.1f}%")
        print(f"Sharpe: {avg_sharpe:.2f}")
        print(f"MaxDD: {avg_dd:.1f}%")
        
        # Verifica consistência
        consistent = (df_results["Total%"] > 0).all() and (df_results["Sharpe≈"] > 0.5).all()
        print(f"Consistente: {'✅ SIM' if consistent else '❌ NÃO'}")
    else:
        print("Nenhum resultado válido obtido.")

if __name__ == "__main__":
    validate_out_of_sample()
