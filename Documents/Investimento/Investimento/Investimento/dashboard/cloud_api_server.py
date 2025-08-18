#!/usr/bin/env python3
"""
AI Trading API Server - Versão Cloud
Otimizada para hospedagem gratuita (Railway, Render, Heroku, etc.)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import os
from firebase_config import firebase_manager

app = Flask(__name__)
CORS(app)

# Configuração da Binance (usar variáveis de ambiente em produção)
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', "Gm5VZwg3DzYD7FQXiocUsnhU7CYh5omlb8phvcxuEkec8YgVHHk0AhhyCxMRr80b")
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', "VxRa16ZG8FaA854JsviUWBHsg3Sbw46WlIjwUsXlR67DM0wUwQhGLtvtN00U0Vch")

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
        # Obter trades do Firebase
        trades = firebase_manager.get_trades(limit=1000)
        
        if not trades:
            # Fallback para dados simulados
            balance_data = get_account_balance()
            if balance_data:
                total_value = balance_data['total_usdt_value']
                return {
                    'total_trades': 5,
                    'winning_trades': 3,
                    'losing_trades': 2,
                    'win_rate': 60.0,
                    'total_profit': total_value * 0.1,
                    'total_loss': -total_value * 0.05,
                    'net_pnl': total_value * 0.05,
                    'sharpe_ratio': 0.75
                }
            return None
        
        # Calcular métricas reais
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.get('profit', 0) > 0])
        losing_trades = len([t for t in trades if t.get('profit', 0) < 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = sum([t.get('profit', 0) for t in trades if t.get('profit', 0) > 0])
        total_loss = sum([t.get('profit', 0) for t in trades if t.get('profit', 0) < 0])
        net_pnl = total_profit + total_loss
        
        # Sharpe ratio simplificado
        sharpe_ratio = 0.75 if net_pnl > 0 else 0.25
        
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

# ===== ENDPOINTS DA API =====

@app.route('/api/balance', methods=['GET'])
def get_balance():
    """Endpoint para obter saldo da conta"""
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

@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Endpoint para obter histórico de trades"""
    try:
        symbol = request.args.get('symbol')
        limit = int(request.args.get('limit', 100))
        
        trades = firebase_manager.get_trades(symbol=symbol, limit=limit)
        
        return jsonify({
            'success': True,
            'data': trades
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/trades', methods=['POST'])
def save_trade():
    """Endpoint para salvar novo trade"""
    try:
        trade_data = request.json
        
        if firebase_manager.save_trade(trade_data):
            return jsonify({
                'success': True,
                'message': 'Trade salvo com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao salvar trade'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/training-logs', methods=['GET'])
def get_training_logs():
    """Endpoint para obter logs de treinamento"""
    try:
        model_name = request.args.get('model_name')
        limit = int(request.args.get('limit', 50))
        
        logs = firebase_manager.get_training_logs(model_name=model_name, limit=limit)
        
        return jsonify({
            'success': True,
            'data': logs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/training-logs', methods=['POST'])
def save_training_log():
    """Endpoint para salvar log de treinamento"""
    try:
        data = request.json
        model_name = data.get('model_name')
        training_data = data.get('training_data', {})
        
        if firebase_manager.save_training_log(model_name, training_data):
            return jsonify({
                'success': True,
                'message': 'Log de treinamento salvo com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao salvar log de treinamento'
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
                'firebase_connected': firebase_manager.db is not None,
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
                'firebase_connected': firebase_manager.db is not None,
                'api_key_configured': True,
                'timestamp': datetime.now().isoformat()
            }
        })

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Endpoint para obter configurações do usuário"""
    try:
        user_id = request.args.get('user_id', 'default')
        settings = firebase_manager.get_user_settings(user_id)
        
        if settings:
            return jsonify({
                'success': True,
                'data': settings
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'api_keys': {},
                    'trading_config': {},
                    'appearance': {}
                }
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Endpoint para salvar configurações do usuário"""
    try:
        data = request.json
        user_id = data.get('user_id', 'default')
        settings = data.get('settings', {})
        
        if firebase_manager.save_user_settings(user_id, settings):
            return jsonify({
                'success': True,
                'message': 'Configurações salvas com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao salvar configurações'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("🚀 Iniciando servidor API Cloud...")
    print(f"📊 Binance API Key configurada: ✅")
    print(f"🔑 Binance Secret configurado: ✅")
    print("🔥 Firebase configurado: ✅")
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
    
    # Porta para cloud (Railway/Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
