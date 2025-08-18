
import itertools
import math
import time
from typing import Dict, Tuple, List

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

# =====================
# Configuração geral
# =====================
VS_CCY = "usd"
TOP_N = 20            # para otimização, use menor universo (mais rápido)
DAYS_HISTORY = 365    # aumente janela (ex.: 365-720) para mais robustez
MIN_VOL_USD = 8e5     # filtro de liquidez base
EXCLUDE_STABLES = {"tether","usd-coin","binance-usd","dai","true-usd","frax","usdd","paxos-standard"}
CG_BASE = "https://api.coingecko.com/api/v3"

INITIAL_CASH = 20.0

# =====================
# Funções CoinGecko
# =====================
def cg_get_markets(vs_currency="usd", per_page=100, page=1):
    url = f"{CG_BASE}/coins/markets"
    params = {"vs_currency": vs_currency, "order": "volume_desc",
              "per_page": per_page, "page": page, "price_change_percentage": "24h"}
    
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            time.sleep(2.0)  # delay para evitar rate limit
            return r.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < 2:
                print(f"Rate limit atingido, aguardando... (tentativa {attempt+1}/3)")
                time.sleep(60)  # espera 1 minuto
                continue
            raise

def cg_get_market_chart(coin_id, vs_currency="usd", days=180):
    url = f"{CG_BASE}/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days}
    
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            time.sleep(2.0)  # delay para evitar rate limit
            return r.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < 2:
                print(f"Rate limit atingido, aguardando... (tentativa {attempt+1}/3)")
                time.sleep(60)  # espera 1 minuto
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
def load_universe(top_n=TOP_N, days=DAYS_HISTORY) -> Dict[str, pd.DataFrame]:
    # universo
    mkts, page = [], 1
    while len(mkts) < top_n:
        batch = cg_get_markets(vs_currency=VS_CCY, per_page=100, page=page)
        if not batch: break
        mkts += batch
        page += 1
    universe = [m for m in mkts if m["id"] not in EXCLUDE_STABLES][:top_n]

    data = {}
    for m in tqdm(universe, desc="Baixando histórico"):
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

# =====================
# Features e métricas
# =====================
def add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ret7"] = out["price"].pct_change(7)
    out["ret14"] = out["price"].pct_change(14)
    out["vol14usd"] = out["volume"].rolling(14).mean()
    out["don_high20"] = out["price"].rolling(20).max()
    # volatilidade de retornos (proxy para trailing)
    r = out["price"].pct_change().fillna(0.0)
    out["vol_std14"] = r.rolling(14).std()
    return out

def metrics(series: pd.Series) -> Dict[str, float]:
    s = series.dropna()
    if len(s) < 2:
        return {}
    ret = s.pct_change().dropna()
    total = s.iloc[-1]/s.iloc[0]-1
    vol = ret.std()*np.sqrt(365) if len(ret)>0 else np.nan
    dd = (s/s.cummax()-1).min()
    sharpe = (ret.mean()*365)/vol if vol and vol>0 else np.nan
    return {
        "Initial": float(round(s.iloc[0],2)),
        "Final": float(round(s.iloc[-1],2)),
        "Total%": float(round(total*100,2)),
        "Vol%pa": float(round(vol*100,2)) if pd.notna(vol) else np.nan,
        "MaxDD%": float(round(dd*100,2)) if pd.notna(dd) else np.nan,
        "Sharpe≈": float(round(sharpe,2)) if pd.notna(sharpe) else np.nan
    }

# =====================
# Estratégias
# =====================
def pick_momentum(dt, data, min_vol_usd, w7, w14, wv):
    rows = []
    for cid, df in data.items():
        if dt not in df.index: continue
        r = df.loc[dt]
        if pd.isna(r["ret7"]) or pd.isna(r["ret14"]) or pd.isna(r["vol14usd"]): continue
        if r["vol14usd"] < min_vol_usd: continue
        score = w7*r["ret7"] + w14*r["ret14"] + wv*np.log1p(r["vol14usd"])
        rows.append((cid, score))
    if not rows: return None
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows[0][0]

def pick_breakout(dt, data, min_vol_usd, win, w_str, w_vol):
    rows = []
    for cid, df in data.items():
        if dt not in df.index: continue
        r = df.loc[dt]
        don_high = df["price"].rolling(win).max().loc[dt]
        if pd.isna(don_high) or pd.isna(r["vol14usd"]): continue
        if r["vol14usd"] < min_vol_usd: continue
        if r["price"] >= don_high:
            strength = (r["price"]/don_high) - 1.0
            score = w_str*strength + w_vol*np.log1p(r["vol14usd"])
            rows.append((cid, score))
    if not rows: return None
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows[0][0]

# =====================
# Backtest
# =====================
def run_backtest(data, dates, picker, rebalance_days, stop_loss_pct, trail_k, risk_pct):
    cash = INITIAL_CASH
    coin, qty = None, 0.0
    equity = []
    for i in range(0, len(dates), rebalance_days):
        dt = dates[i]

        def price(cid, d):
            df = data.get(cid)
            if df is None or d not in df.index: return None
            return float(df.loc[d, "price"])

        # marca equity intra-janelas
        if coin is not None:
            for j in range(rebalance_days):
                if i+j >= len(dates): break
                dtn = dates[i+j]
                p = price(coin, dtn)
                equity.append({"date": dtn, "equity": cash + (qty*p if p else 0.0)})

        # decide ativo
        chosen = picker(dt)
        if chosen is None:
            continue
        p_in = price(chosen, dt)
        if p_in is None:
            continue

        # se posicionado em outro, zera
        if coin is not None and coin != chosen and qty > 0.0:
            p_sell = price(coin, dt)
            if p_sell:
                cash = qty * p_sell
            coin, qty = None, 0.0

        # compra com sizing por risco
        if coin != chosen:
            risk_amount = cash * risk_pct
            if risk_amount <= 0: break
            unit_risk = p_in * stop_loss_pct
            size_cash = min(cash, (risk_amount/max(unit_risk,1e-9))*p_in)
            if size_cash <= 0: continue
            qty = size_cash / p_in
            cash -= size_cash
            coin = chosen

        # trailing e stop intra-janela
        for j in range(rebalance_days):
            if i+j >= len(dates): break
            dtn = dates[i+j]
            p = price(coin, dtn)
            # volatilidade dos retornos 14d
            vol = float(data[coin].loc[dtn, "vol_std14"] if coin else 0.0)  # já calculado
            trail_stop = p * (1.0 - trail_k*max(vol,0.0)) if p is not None else None
            hard_stop = p * (1.0 - stop_loss_pct) if p is not None else None
            stop_level = max(hard_stop, trail_stop) if (hard_stop is not None and trail_stop is not None) else (hard_stop or trail_stop)
            if p is not None and stop_level is not None and p <= stop_level:
                cash = qty * p
                coin, qty = None, 0.0
                # preenche equity restante como caixa
                for k in range(j+1, rebalance_days):
                    if i+k >= len(dates): break
                    equity.append({"date": dates[i+k], "equity": cash})
                break

    # flush final
    if coin is not None and qty > 0.0:
        last_price = data[coin].iloc[-1]["price"]
        equity.append({"date": dates[-1], "equity": cash + qty*last_price})
    eq_df = pd.DataFrame(equity).drop_duplicates(subset=["date"]).set_index("date").sort_index()
    return eq_df

# =====================
# Grid de parâmetros
# =====================
GRID = {
    "rebalance_days": [3, 7, 14],
    "stop_loss_pct": [0.03, 0.05, 0.08],
    "trail_k": [1.5, 2.0, 2.5],
    "risk_pct": [0.02, 0.04, 0.06],
    # específicos momentum
    "w7": [0.6, 0.8],
    "w14": [0.2, 0.3],
    "wv": [0.1],
    # específicos breakout
    "don_win": [20, 30],
    "w_str": [0.7, 0.9],
    "w_vol": [0.1, 0.3],
    # filtro
    "min_vol_usd": [5e5, 1e6, 2e6]
}

def main():
    # Carrega dados
    raw = load_universe(TOP_N, DAYS_HISTORY)
    # adiciona features
    data = {cid: add_features(df) for cid, df in raw.items()}
    dates = sorted(set().union(*[df.index for df in data.values()]))
    dates = pd.to_datetime(dates)
    dates = dates[60:]  # warm-up

    results = []

    # Otimiza Momentum
    print("\n== Otimizando Momentum ==")
    for reb, sl, tk, rp, w7, w14, wv, minv in itertools.product(
        GRID["rebalance_days"], GRID["stop_loss_pct"], GRID["trail_k"], GRID["risk_pct"],
        GRID["w7"], GRID["w14"], GRID["wv"], GRID["min_vol_usd"]
    ):
        def picker(dt):
            return pick_momentum(dt, data, minv, w7, w14, wv)
        eq = run_backtest(data, dates, picker, reb, sl, tk, rp)
        if eq.empty: 
            continue
        m = metrics(eq["equity"])
        m.update({
            "strategy": "momentum",
            "rebalance_days": reb, "stop_loss_pct": sl, "trail_k": tk, "risk_pct": rp,
            "w7": w7, "w14": w14, "wv": wv, "min_vol_usd": minv
        })
        results.append(m)

    # Otimiza Breakout
    print("\n== Otimizando Breakout ==")
    for reb, sl, tk, rp, donw, wstr, wvol, minv in itertools.product(
        GRID["rebalance_days"], GRID["stop_loss_pct"], GRID["trail_k"], GRID["risk_pct"],
        GRID["don_win"], GRID["w_str"], GRID["w_vol"], GRID["min_vol_usd"]
    ):
        def picker(dt):
            return pick_breakout(dt, data, minv, donw, wstr, wvol)
        eq = run_backtest(data, dates, picker, reb, sl, tk, rp)
        if eq.empty: 
            continue
        m = metrics(eq["equity"])
        m.update({
            "strategy": "breakout",
            "rebalance_days": reb, "stop_loss_pct": sl, "trail_k": tk, "risk_pct": rp,
            "don_win": donw, "w_str": wstr, "w_vol": wvol, "min_vol_usd": minv
        })
        results.append(m)

    if not results:
        print("Sem resultados (verifique internet e limites da API).")
        return

    res_df = pd.DataFrame(results).sort_values(["Final","Sharpe≈"], ascending=[False, False])
    res_path = "opt_results.csv"
    res_df.to_csv(res_path, index=False)
    print(f"\nTop 10 configurações:\n{res_df.head(10)}")
    print(f"\nArquivo salvo: {res_path}")

if __name__ == "__main__":
    main()
