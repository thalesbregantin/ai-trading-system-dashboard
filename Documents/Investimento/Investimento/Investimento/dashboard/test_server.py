#!/usr/bin/env python3
"""
Servidor de teste simples para verificar se Flask está funcionando
"""

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        'message': 'Teste do servidor funcionando!',
        'status': 'success'
    })

@app.route('/api/test')
def test():
    return jsonify({
        'success': True,
        'message': 'API funcionando!'
    })

if __name__ == '__main__':
    print("🚀 Iniciando servidor de teste...")
    print("🌐 URL: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
