#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/status')
def status():
    return jsonify({
        'success': True,
        'message': 'AI Trading API Running'
    })

@app.route('/api/portfolio')
def portfolio():
    return jsonify({
        'success': True,
        'data': {
            'total_balance': 98.60,
            'free_balance': 98.60,
            'used_balance': 0
        }
    })

@app.route('/api/balance')
def balance():
    return portfolio()

@app.route('/api/metrics')
def metrics():
    return jsonify({
        'success': True,
        'data': {
            'total_trades': 46,
            'win_rate': 34.8,
            'total_profit': 142.24,
            'sharpe_ratio': 0.061
        }
    })

@app.route('/api/trades')
def trades():
    return jsonify({
        'success': True,
        'data': [
            {
                'timestamp': '2025-08-18T10:00:00Z',
                'symbol': 'BTC/USDT',
                'side': 'BUY',
                'amount': 0.001,
                'price': 42150.50,
                'profit': 25.30,
                'status': 'executed'
            }
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
