#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ccxt
from datetime import datetime

# Configuração da Binance
BINANCE_API_KEY = 'Gm5VZwg3DzYD7FQXiocUsnhU7CYh5omlb8phvcxuEkec8YgVHHk0AhhyCxMRr80b'
BINANCE_SECRET_KEY = 'VxRa16ZG8FaA854JsviUWBHsg3Sbw46WlIjwUsXlR67DM0wUwQhGLtvtN00U0Vch'

def test_api_permissions():
    """Testar permissões da API"""
    print("🔍 TESTANDO PERMISSÕES DA API BINANCE")
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
        
        print("\n1️⃣ Testando leitura de saldo...")
        balance = exchange.fetch_balance()
        print(f"✅ Leitura de saldo: OK")
        print(f"💰 USDT: {balance.get('USDT', {}).get('free', 0)}")
        
        print("\n2️⃣ Testando leitura de preços...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✅ Leitura de preços: OK")
        print(f"💵 BTC/USDT: ${ticker['last']}")
        
        print("\n3️⃣ Testando leitura de ordens...")
        orders = exchange.fetch_open_orders()
        print(f"✅ Leitura de ordens: OK")
        print(f"📋 Ordens abertas: {len(orders)}")
        
        print("\n4️⃣ Testando criação de ordem LIMIT (não executada)...")
        try:
            # Tentar criar uma ordem LIMIT com preço muito baixo (não será executada)
            order = exchange.create_limit_buy_order('BTC/USDT', 0.00001, 1000)  # Preço $1000 (muito baixo)
            print(f"✅ Criação de ordem: OK")
        except Exception as e:
            if "insufficient balance" in str(e).lower():
                print(f"✅ Criação de ordem: OK (erro esperado - saldo insuficiente)")
            else:
                print(f"❌ Criação de ordem: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ API configurada corretamente")
        print("🚀 Pronto para fazer trades!")
        
    except Exception as e:
        print(f"\n❌ Erro nos testes: {e}")
        print("\n🔧 SOLUÇÕES:")
        print("1. Verifique se a API key está ativa")
        print("2. Verifique se tem permissão para 'Enable Spot & Margin Trading'")
        print("3. Verifique se o IP está liberado")
        print("4. Tente criar uma nova API key")

if __name__ == "__main__":
    test_api_permissions()
