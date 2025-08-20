#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ccxt
from datetime import datetime

# Configuração da Binance
BINANCE_API_KEY = 'Gm5VZwg3DzYD7FQXiocUsnhU7CYh5omlb8phvcxuEkec8YgVHHk0AhhyCxMRr80b'
BINANCE_SECRET_KEY = 'VxRa16ZG8FaA854JsviUWBHsg3Sbw46WlIjwUsXlR67DM0wUwQhGLtvtN00U0Vch'

def test_limit_order():
    """Testar ordem LIMIT"""
    print("🔍 TESTANDO ORDEM LIMIT")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Configurar exchange
        exchange = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_SECRET_KEY,
            'sandbox': False,
            'enableRateLimit': True
        })
        
        # Obter preço atual
        ticker = exchange.fetch_ticker('BTC/USDT')
        current_price = ticker['last']
        print(f"💵 Preço atual BTC: ${current_price}")
        
        # Criar ordem LIMIT com preço muito baixo (não será executada)
        limit_price = current_price * 0.5  # 50% do preço atual
        amount = 0.00001  # Quantidade mínima
        
        print(f"🎯 Tentando criar ordem LIMIT:")
        print(f"💰 Preço: ${limit_price}")
        print(f"📈 Quantidade: {amount} BTC")
        print(f"💲 Valor: ${limit_price * amount:.2f}")
        
        # Criar ordem LIMIT BUY
        order = exchange.create_limit_buy_order('BTC/USDT', amount, limit_price)
        
        print(f"✅ Ordem LIMIT criada com sucesso!")
        print(f"📋 Order ID: {order['id']}")
        print(f"📊 Status: {order['status']}")
        
        # Cancelar a ordem imediatamente
        print(f"🔄 Cancelando ordem...")
        canceled = exchange.cancel_order(order['id'], 'BTC/USDT')
        print(f"✅ Ordem cancelada!")
        
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ API tem permissão para criar ordens!")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("\n🔧 O problema pode ser:")
        print("1. API key não tem permissão para 'Enable Spot & Margin Trading'")
        print("2. IP não está liberado")
        print("3. API key está desabilitada")

if __name__ == "__main__":
    test_limit_order()
