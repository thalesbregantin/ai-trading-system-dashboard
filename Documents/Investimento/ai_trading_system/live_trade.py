#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import ccxt
import time
from datetime import datetime
import logging

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import get_config
from core.ai_trader_simple import SimpleAITrader
from core.hybrid_trading_system import HybridTradingSystem

# Configuração da Binance
BINANCE_API_KEY = 'Gm5VZwg3DzYD7FQXiocUsnhU7CYh5omlb8phvcxuEkec8YgVHHk0AhhyCxMRr80b'
BINANCE_SECRET_KEY = 'VxRa16ZG8FaA854JsviUWBHsg3Sbw46WlIjwUsXlR67DM0wUwQhGLtvtN00U0Vch'

def setup_binance():
    """Configurar conexão com Binance"""
    try:
        exchange = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_SECRET_KEY,
            'sandbox': False,  # False = produção real
            'enableRateLimit': True
        })
        
        # Testar conexão
        balance = exchange.fetch_balance()
        print(f"✅ Conexão com Binance estabelecida!")
        print(f"💰 Saldo USDT: {balance.get('USDT', {}).get('free', 0)}")
        return exchange
    except Exception as e:
        print(f"❌ Erro ao conectar com Binance: {e}")
        return None

def get_ai_signal():
    """Obter sinal da IA"""
    try:
        config = get_config('prod')
        ai_trader = SimpleAITrader(config)
        
        # Obter sinal para BTC
        signal = ai_trader.get_current_signal("BTC-USD")
        print(f"🧠 Sinal da IA: {signal}")
        
        return signal
    except Exception as e:
        print(f"❌ Erro ao obter sinal da IA: {e}")
        return None

def place_ai_trade(exchange, signal, symbol='BTC/USDT', amount=0.00001):
    """Fazer trade baseado na IA"""
    try:
        print(f"🎯 Executando trade baseado na IA...")
        print(f"📊 Signal: {signal}")
        print(f"💰 Symbol: {symbol}")
        print(f"📈 Amount: {amount} BTC")
        
        # Obter preço atual
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        print(f"💵 Preço atual: ${current_price}")
        
        # Calcular valor em USDT
        usdt_value = amount * current_price
        print(f"💲 Valor em USDT: ${usdt_value:.2f}")
        
        # Verificar saldo
        balance = exchange.fetch_balance()
        usdt_balance = balance.get('USDT', {}).get('free', 0)
        
        if usdt_balance < usdt_value:
            print(f"❌ Saldo insuficiente! Temos ${usdt_balance}, precisamos ${usdt_value:.2f}")
            return False
            
        print(f"✅ Saldo suficiente! Temos ${usdt_balance}")
        
        # Executar trade baseado no sinal
        if signal == 'BUY':
            order = exchange.create_market_buy_order(symbol, amount)
            print(f"🟢 COMPRA executada!")
        elif signal == 'SELL':
            order = exchange.create_market_sell_order(symbol, amount)
            print(f"🔴 VENDA executada!")
        else:
            print(f"⏸️ HOLD - Nenhum trade executado")
            return None
        
        print(f"🎉 Trade executado com sucesso!")
        print(f"📋 Order ID: {order['id']}")
        print(f"💰 Preço: ${order['price']}")
        print(f"📊 Status: {order['status']}")
        
        return order
        
    except Exception as e:
        print(f"❌ Erro ao fazer trade: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 AI TRADING SYSTEM - TRADE REAL")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 1. Configurar Binance
    print("\n1️⃣ Configurando Binance...")
    exchange = setup_binance()
    if not exchange:
        return
    
    # 2. Obter sinal da IA
    print("\n2️⃣ Consultando IA...")
    signal = get_ai_signal()
    if not signal:
        print("❌ Não foi possível obter sinal da IA")
        return
    
    # 3. Mostrar informações da conta
    print("\n3️⃣ Informações da conta:")
    balance = exchange.fetch_balance()
    for currency in ['USDT', 'BTC', 'ETH']:
        if currency in balance:
            free = balance[currency]['free']
            if free > 0:
                print(f"💰 {currency}: {free}")
    
    print("\n" + "=" * 50)
    
    # 4. Perguntar se quer executar o trade
    print(f"🧠 Sinal da IA: {signal}")
    print(f"💰 Trade sugerido: {symbol} - {amount} BTC (~$0.50)")
    
    response = input("\n🤔 Quer executar este trade da IA? (s/n): ")
    
    if response.lower() == 's':
        # 5. Executar trade
        print("\n4️⃣ Executando trade...")
        order = place_ai_trade(exchange, signal, 'BTC/USDT', 0.00001)
        
        if order:
            print("\n✅ TRADE REAL EXECUTADO COM SUCESSO!")
            print("🎯 Sistema de IA funcionando perfeitamente!")
            print("🚀 Pronto para operar oficialmente!")
        else:
            print("\n❌ Falha no trade")
    else:
        print("👌 Trade cancelado pelo usuário")

if __name__ == "__main__":
    main()
