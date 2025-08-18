from flask import Flask, jsonify, request
from flask_cors import CORS
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time

app = Flask(__name__)
CORS(app)

# Configuração da Binance (chaves hardcoded para teste)
BINANCE_API_KEY = "Gm5VZwg3DzYD7FQXiocUsnhU7CYh5omlb8phvcxuEkec8YgVHHk0AhhyCxMRr80b"
BINANCE_SECRET_KEY = "VxRa16ZG8FaA854JsviUWBHsg3Sbw46WlIjwUsXlR67DM0wUwQhGLtvtN00U0Vch"

# Inicializar exchange
exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET_KEY,
    'sandbox': False,
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
        # Para teste, usar dados simulados baseados no saldo real
        balance_data = get_account_balance()
        if balance_data:
            total_value = balance_data['total_usdt_value']
            
            # Simular métricas baseadas no valor atual
            total_trades = 5  # Poucos trades para conta pequena
            winning_trades = 3
            losing_trades = 2
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Simular profit/loss baseado no valor atual
            total_profit = total_value * 0.1  # 10% de lucro
            total_loss = -total_value * 0.05  # 5% de perda
            net_pnl = total_profit + total_loss
            
            # Sharpe ratio simplificado
            sharpe_ratio = 0.75
            
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

@app.route('/api/balance', methods=['GET'])
def get_balance():
    """Endpoint para obter saldo da conta (alias para portfolio)"""
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
                'error': 'Não foi possível obter saldo da conta'
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
                'api_key_configured': True,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {
                'binance_connected': False,
                'api_key_configured': True,
                'timestamp': datetime.now().isoformat()
            }
        })

if __name__ == '__main__':
    print("🚀 Iniciando servidor API para dashboard...")
    print(f"📊 Binance API Key configurada: ✅")
    print(f"🔑 Binance Secret configurado: ✅")
    print("💰 Testando conexão com sua conta...")
    
    # Testar conexão inicial
    try:
        balance = get_account_balance()
        if balance:
            print(f"✅ Conectado! Saldo total: ${balance['total_usdt_value']:.2f} USDT")
        else:
            print("❌ Erro ao obter saldo")
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
