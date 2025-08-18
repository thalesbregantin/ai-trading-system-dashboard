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
            'used_balance': 0,
            'total_usdt_value': 98.60
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
            'total_trades': 0,
            'win_rate': 0.0,
            'total_profit': 0.0,
            'sharpe_ratio': 0.0
        }
    })

@app.route('/api/trades')
def trades():
    return jsonify({
        'success': True,
        'data': []
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
