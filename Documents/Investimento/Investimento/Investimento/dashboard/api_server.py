from flask import Flask, jsonify, request
from flask_cors import CORS
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import time

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuração da Binance
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

# Inicializar exchange
exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET_KEY,
    'sandbox': False,  # True para testnet, False para produção
    'enableRateLimit': True
})

def get_account_balance():
    """Obter saldo da conta Binance"""
    try:
        balance = exchange.fetch_balance()
        
        # Filtrar apenas moedas com saldo > 0
        non_zero_balances = {}
        total_usdt_value = 0
        
        for currency, amount in balance['total'].items():
            if amount > 0:
                if currency == 'USDT':
                    non_zero_balances[currency] = {
                        'amount': amount,
                        'usdt_value': amount
                    }
                    total_usdt_value += amount
                else:
                    try:
                        # Obter preço atual em USDT
                        ticker = exchange.fetch_ticker(f'{currency}/USDT')
                        usdt_value = amount * ticker['last']
                        non_zero_balances[currency] = {
                            'amount': amount,
                            'usdt_value': usdt_value,
                            'price_usdt': ticker['last']
                        }
                        total_usdt_value += usdt_value
                    except:
                        # Se não conseguir obter preço, usar valor 0
                        non_zero_balances[currency] = {
                            'amount': amount,
                            'usdt_value': 0,
                            'price_usdt': 0
                        }
        
        # Calcular percentuais
        for currency in non_zero_balances:
            if total_usdt_value > 0:
                non_zero_balances[currency]['percentage'] = (
                    non_zero_balances[currency]['usdt_value'] / total_usdt_value * 100
                )
            else:
                non_zero_balances[currency]['percentage'] = 0
        
        return {
            'balances': non_zero_balances,
            'total_usdt_value': total_usdt_value
        }
    except Exception as e:
        print(f"Erro ao obter saldo: {e}")
        return None

def get_recent_trades(symbol='BTC/USDT', limit=50):
    """Obter trades recentes"""
    try:
        trades = exchange.fetch_my_trades(symbol, limit=limit)
        
        formatted_trades = []
        for trade in trades:
            formatted_trades.append({
                'id': trade['id'],
                'symbol': trade['symbol'],
                'side': trade['side'],  # 'buy' ou 'sell'
                'amount': trade['amount'],
                'price': trade['price'],
                'cost': trade['cost'],
                'fee': trade['fee'],
                'timestamp': trade['timestamp'],
                'datetime': trade['datetime']
            })
        
        return formatted_trades
    except Exception as e:
        print(f"Erro ao obter trades: {e}")
        return []

def get_ohlcv_data(symbol='BTC/USDT', timeframe='1h', limit=100):
    """Obter dados OHLCV para gráficos"""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Calcular indicadores técnicos
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Momentum
        df['momentum'] = df['close'].pct_change(periods=1) * 100
        
        return df.to_dict('records')
    except Exception as e:
        print(f"Erro ao obter dados OHLCV: {e}")
        return []

def calculate_metrics():
    """Calcular métricas de performance"""
    try:
        # Obter trades dos últimos 30 dias
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        # Simular métricas baseadas em trades (em produção, calcularia baseado em trades reais)
        total_trades = 45
        winning_trades = 32
        losing_trades = 13
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Simular profit/loss (em produção, calcularia baseado em trades reais)
        total_profit = 1245.67
        total_loss = -567.89
        net_pnl = total_profit + total_loss
        
        # Sharpe ratio simplificado (em produção, calcularia baseado em retornos diários)
        sharpe_ratio = 0.82
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'net_pnl': net_pnl,
            'sharpe_ratio': sharpe_ratio
        }
    except Exception as e:
        print(f"Erro ao calcular métricas: {e}")
        return None

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Endpoint para obter dados do portfolio"""
    try:
        balance_data = get_account_balance()
        if balance_data:
            return jsonify({
                'success': True,
                'data': balance_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Não foi possível obter dados do portfolio'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Endpoint para obter trades recentes"""
    try:
        symbol = request.args.get('symbol', 'BTC/USDT')
        limit = int(request.args.get('limit', 20))
        
        trades = get_recent_trades(symbol, limit)
        return jsonify({
            'success': True,
            'data': trades
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/chart-data', methods=['GET'])
def get_chart_data():
    """Endpoint para obter dados de gráfico"""
    try:
        symbol = request.args.get('symbol', 'BTC/USDT')
        timeframe = request.args.get('timeframe', '1h')
        limit = int(request.args.get('limit', 100))
        
        chart_data = get_ohlcv_data(symbol, timeframe, limit)
        return jsonify({
            'success': True,
            'data': chart_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Endpoint para obter métricas de performance"""
    try:
        metrics = calculate_metrics()
        if metrics:
            return jsonify({
                'success': True,
                'data': metrics
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Não foi possível calcular métricas'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/current-price', methods=['GET'])
def get_current_price():
    """Endpoint para obter preço atual"""
    try:
        symbol = request.args.get('symbol', 'BTC/USDT')
        ticker = exchange.fetch_ticker(symbol)
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'price': ticker['last'],
                'change_24h': ticker['percentage'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low'],
                'volume_24h': ticker['baseVolume']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Endpoint para verificar status da conexão"""
    try:
        # Testar conexão com Binance
        exchange.load_markets()
        
        return jsonify({
            'success': True,
            'data': {
                'binance_connected': True,
                'api_key_configured': bool(BINANCE_API_KEY),
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {
                'binance_connected': False,
                'api_key_configured': bool(BINANCE_API_KEY),
                'timestamp': datetime.now().isoformat()
            }
        })

if __name__ == '__main__':
    print("🚀 Iniciando servidor API para dashboard...")
    print(f"📊 Binance API Key configurada: {'✅' if BINANCE_API_KEY else '❌'}")
    print(f"🔑 Binance Secret configurado: {'✅' if BINANCE_SECRET_KEY else '❌'}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
