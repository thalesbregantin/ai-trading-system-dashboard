import os
import time
import pandas as pd
import numpy as np
import ccxt
from datetime import datetime, timedelta
from tqdm import tqdm

# =====================
# Configuração Binance Testnet
# =====================
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

# Parâmetros otimizados
REBALANCE_DAYS = 14   # rebalanceamento quinzenal
RISK_PCT = 0.04       # 4% do capital por trade
STOP_LOSS_PCT = 0.03  # stop loss de 3%
TRAIL_K = 1.5         # trailing stop 1.5x volatilidade
MIN_VOL_USD = 1e6     # filtro de liquidez

# Pesos momentum otimizados
W7 = 0.8              # peso retorno 7d
W14 = 0.2             # peso retorno 14d  
WV = 0.1              # peso volume

# Configuração
TOP_N = 30            # top 30 pares
DAYS_HISTORY = 365    # histórico
INITIAL_CASH = 20.0   # capital inicial

# Circuit breakers e proteções
MAX_DAILY_DD = 0.03   # pausa se DD diário ≥ 3%
MAX_MONTHLY_DD = 0.10 # pausa se DD mensal ≥ 10%
MAX_TRADES_PER_DAY = 5  # limite de trades por dia

# =====================
# Setup Binance
# =====================
def setup_binance():
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        raise ValueError("Configure BINANCE_API_KEY e BINANCE_API_SECRET")
    
    exchange = ccxt.binance({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_API_SECRET,
        'sandbox': True,  # testnet
        'enableRateLimit': True,
    })
    
    # Testa conexão
    try:
        balance = exchange.fetch_balance()
        print(f"Conectado ao Binance Testnet")
        print(f"USDT disponível: {balance.get('USDT', {}).get('free', 0):.2f}")
        return exchange
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

# =====================
# Busca pares líquidos
# =====================
def get_liquid_pairs(exchange, top_n=TOP_N):
    print("Buscando pares líquidos...")
    
    try:
        tickers = exchange.fetch_tickers()
        usdt_pairs = []
        
        for symbol, ticker in tickers.items():
            if symbol.endswith('/USDT') and ticker['quoteVolume']:
                usdt_pairs.append({
                    'symbol': symbol,
                    'volume': ticker['quoteVolume'],
                    'price': ticker['last']
                })
        
        # Ordena por volume e pega top N
        usdt_pairs.sort(key=lambda x: x['volume'], reverse=True)
        top_pairs = usdt_pairs[:top_n]
        
        print(f"Top {len(top_pairs)} pares por volume:")
        for i, pair in enumerate(top_pairs[:10]):
            print(f"  {i+1}. {pair['symbol']} - Vol: ${pair['volume']:,.0f}")
        
        return [p['symbol'] for p in top_pairs]
        
    except Exception as e:
        print(f"Erro ao buscar pares: {e}")
        return []

# =====================
# Busca dados históricos
# =====================
def fetch_historical_data(exchange, symbol, days=DAYS_HISTORY):
    try:
        # Busca klines diários
        ohlcv = exchange.fetch_ohlcv(
            symbol, 
            timeframe='1d', 
            limit=days
        )
        
        if not ohlcv:
            return None
            
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['price'] = df['close']
        df = df.set_index('date')[['price', 'volume']]
        
        return df
        
    except Exception as e:
        print(f"Erro ao buscar dados de {symbol}: {e}")
        return None

# =====================
# Calcula features
# =====================
def add_features(df):
    out = df.copy()
    out["ret7"] = out["price"].pct_change(7)
    out["ret14"] = out["price"].pct_change(14)
    out["vol14usd"] = out["volume"].rolling(14).mean()
    # volatilidade de retornos
    r = out["price"].pct_change().fillna(0.0)
    out["vol_std14"] = r.rolling(14).std()
    return out

# =====================
# Seleção momentum
# =====================
def pick_momentum(dt, data):
    rows = []
    for symbol, df in data.items():
        if dt not in df.index: continue
        r = df.loc[dt]
        if pd.isna(r["ret7"]) or pd.isna(r["ret14"]) or pd.isna(r["vol14usd"]): continue
        if r["vol14usd"] < MIN_VOL_USD: continue
        score = W7*r["ret7"] + W14*r["ret14"] + WV*np.log1p(r["vol14usd"])
        rows.append((symbol, score))
    if not rows: return None
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows[0][0]

# =====================
# Execução de ordens
# =====================
def execute_order(exchange, symbol, side, amount, price=None):
    try:
        # Validações de segurança
        if amount <= 0:
            print(f"Quantidade inválida: {amount}")
            return None
        
        # Busca informações do símbolo
        market = exchange.load_markets()
        if symbol not in market:
            print(f"Símbolo não encontrado: {symbol}")
            return None
        
        symbol_info = market[symbol]
        
        # Valida lot size
        min_amount = symbol_info.get('limits', {}).get('amount', {}).get('min', 0)
        if amount < min_amount:
            print(f"Quantidade {amount} menor que mínimo {min_amount} para {symbol}")
            return None
        
        # Valida min notional
        min_notional = symbol_info.get('limits', {}).get('cost', {}).get('min', 0)
        if min_notional > 0:
            ticker = exchange.fetch_ticker(symbol)
            notional = amount * ticker['last']
            if notional < min_notional:
                print(f"Valor {notional:.2f} menor que mínimo {min_notional} para {symbol}")
                return None
        
        # Executa ordem
        if price:
            # Ordem limit com tolerância
            order = exchange.create_limit_order(symbol, side, amount, price)
        else:
            # Ordem market
            order = exchange.create_market_order(symbol, side, amount)
        
        print(f"Ordem executada: {side} {amount} {symbol} @ {order.get('price', 'market')}")
        return order
        
    except Exception as e:
        print(f"Erro na ordem {side} {symbol}: {e}")
        return None

# =====================
# Backtest com execução
# =====================
def run_live_backtest(exchange, data, dates):
    cash = INITIAL_CASH
    position = None
    equity = []
    trades = []
    daily_trades = {}  # controle de trades por dia
    equity_history = []  # histórico para circuit breakers
    
    print(f"\nIniciando backtest com execução...")
    print(f"Capital inicial: ${cash}")
    
    for i in range(0, len(dates), REBALANCE_DAYS):
        dt = dates[i]
        print(f"\n=== {dt.strftime('%Y-%m-%d')} ===")
        
        def price(symbol, d):
            df = data.get(symbol)
            if df is None or d not in df.index: return None
            return float(df.loc[d, "price"])

        # Marca equity
        if position:
            p = price(position['symbol'], dt)
            if p:
                current_value = cash + (position['qty'] * p)
                equity.append({"date": dt, "equity": current_value})
                equity_history.append(current_value)
                print(f"Equity: ${current_value:.2f}")
                
                # Circuit breaker - DD diário
                if len(equity_history) >= 2:
                    daily_return = (current_value / equity_history[-2]) - 1
                    if daily_return < -MAX_DAILY_DD:
                        print(f"⚠️ CIRCUIT BREAKER: DD diário {daily_return*100:.1f}% > {MAX_DAILY_DD*100}%")
                        print(f"Pausando execução por 1 dia...")
                        continue
                
                # Circuit breaker - DD mensal
                if len(equity_history) >= 30:
                    monthly_high = max(equity_history[-30:])
                    monthly_dd = (current_value / monthly_high) - 1
                    if monthly_dd < -MAX_MONTHLY_DD:
                        print(f"⚠️ CIRCUIT BREAKER: DD mensal {monthly_dd*100:.1f}% > {MAX_MONTHLY_DD*100}%")
                        print(f"Pausando execução por 7 dias...")
                        continue

        # Controle de trades por dia
        day_key = dt.strftime('%Y-%m-%d')
        if day_key not in daily_trades:
            daily_trades[day_key] = 0
        
        if daily_trades[day_key] >= MAX_TRADES_PER_DAY:
            print(f"⚠️ Limite de {MAX_TRADES_PER_DAY} trades por dia atingido")
            continue

        # Seleciona ativo
        chosen = pick_momentum(dt, data)
        if chosen is None:
            print("Nenhum ativo selecionado")
            continue
            
        p_in = price(chosen, dt)
        if p_in is None:
            continue
            
        print(f"Selecionado: {chosen} @ ${p_in:.4f}")

        # Vende posição atual se diferente
        if position and position['symbol'] != chosen:
            p_sell = price(position['symbol'], dt)
            if p_sell:
                # Simula venda (em produção seria ordem real)
                gross_proceeds = position['qty'] * p_sell
                cash = gross_proceeds
                trades.append({
                    "date": dt, "symbol": position['symbol'], 
                    "side": "SELL", "price": p_sell, 
                    "qty": position['qty'], "value": cash
                })
                daily_trades[day_key] += 1
                print(f"Vendeu {position['symbol']} @ ${p_sell:.4f} = ${cash:.2f}")
            position = None

        # Compra novo ativo
        if not position or position['symbol'] != chosen:
            risk_amount = cash * RISK_PCT
            if risk_amount <= 0: 
                print("Sem capital para trade")
                break
                
            unit_risk = p_in * STOP_LOSS_PCT
            size_cash = min(cash, (risk_amount/max(unit_risk,1e-9))*p_in)
            if size_cash <= 0: 
                print("Tamanho de posição muito pequeno")
                continue
                
            qty = size_cash / p_in
            cash -= size_cash
            
            position = {
                'symbol': chosen,
                'qty': qty,
                'entry_price': p_in,
                'entry_date': dt
            }
            
            trades.append({
                "date": dt, "symbol": chosen, 
                "side": "BUY", "price": p_in, 
                "qty": qty, "value": size_cash
            })
            daily_trades[day_key] += 1
            
            print(f"Comprou {chosen}: {qty:.4f} @ ${p_in:.4f} = ${size_cash:.2f}")

        # Verifica stops
        if position:
            p = price(position['symbol'], dt)
            if p:
                vol = float(data[position['symbol']].loc[dt, "vol_std14"] or 0.0)
                trail_stop = p * (1.0 - TRAIL_K*max(vol,0.0)) if vol > 0 else None
                hard_stop = p * (1.0 - STOP_LOSS_PCT)
                stop_level = max(hard_stop, trail_stop) if trail_stop is not None else hard_stop
                
                if p <= stop_level:
                    gross_proceeds = position['qty'] * p
                    cash = gross_proceeds
                    trades.append({
                        "date": dt, "symbol": position['symbol'], 
                        "side": "SELL", "price": p, 
                        "qty": position['qty'], "value": cash
                    })
                    daily_trades[day_key] += 1
                    print(f"Stop atingido: vendeu {position['symbol']} @ ${p:.4f} = ${cash:.2f}")
                    position = None

    # Finaliza posição
    if position:
        last_price = data[position['symbol']].iloc[-1]["price"]
        cash = position['qty'] * last_price
        print(f"Posição final: {position['symbol']} @ ${last_price:.4f} = ${cash:.2f}")

    eq_df = pd.DataFrame(equity).set_index("date").sort_index()
    tr_df = pd.DataFrame(trades)
    return eq_df, tr_df

# =====================
# Execução principal
# =====================
def main():
    # Setup Binance
    exchange = setup_binance()
    if not exchange:
        return
    
    # Busca pares
    pairs = get_liquid_pairs(exchange, TOP_N)
    if not pairs:
        print("Nenhum par encontrado")
        return
    
    # Busca dados históricos
    print(f"\nBaixando dados históricos...")
    data = {}
    for symbol in tqdm(pairs, desc="Dados"):
        df = fetch_historical_data(exchange, symbol, DAYS_HISTORY)
        if df is not None and len(df) >= 60:
            data[symbol] = add_features(df)
        time.sleep(0.1)  # rate limit
    
    if not data:
        print("Sem dados suficientes")
        return
    
    # Prepara datas
    dates = sorted(set().union(*[df.index for df in data.values()]))
    dates = pd.to_datetime(dates)
    dates = dates[60:]  # warm-up
    
    print(f"Período: {dates[0].strftime('%Y-%m-%d')} a {dates[-1].strftime('%Y-%m-%d')}")
    print(f"Total de dias: {len(dates)}")
    
    # Executa backtest
    eq_df, tr_df = run_live_backtest(exchange, data, dates)
    
    if eq_df.empty:
        print("Sem resultados")
        return
    
    # Métricas
    final_equity = eq_df['equity'].iloc[-1] if not eq_df.empty else INITIAL_CASH
    total_return = (final_equity / INITIAL_CASH - 1) * 100
    
    print(f"\n=== Resultados ===")
    print(f"Capital inicial: ${INITIAL_CASH}")
    print(f"Capital final: ${final_equity:.2f}")
    print(f"Retorno total: {total_return:.2f}%")
    print(f"Total de trades: {len(tr_df)}")
    
    # Salva resultados
    eq_df.to_csv("binance_equity.csv")
    tr_df.to_csv("binance_trades.csv", index=False)
    print(f"\nArquivos salvos:")
    print(f"- binance_equity.csv")
    print(f"- binance_trades.csv")

if __name__ == "__main__":
    main()
