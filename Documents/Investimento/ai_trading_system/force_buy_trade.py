#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ccxt
from datetime import datetime

# Configuração da Binance
BINANCE_API_KEY = 'Gm5VZwg3DzYD7FQXiocUsnhU7CYh5omlb8phvcxuEkec8YgVHHk0AhhyCxMRr80b'
BINANCE_SECRET_KEY = 'VxRa16ZG8FaA854JsviUWBHsg3Sbw46WlIjwUsXlR67DM0wUwQhGLtvtN00U0Vch'

def force_buy_trade():
    """Forçar um trade de compra"""
    print("🚀 FORÇANDO TRADE DE COMPRA")
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
        
        # Definir quantidade para compra (aumentada para atender ao mínimo)
        amount = 0.0001  # 10x maior que antes
        usdt_value = amount * current_price
        
        print(f"🎯 Trade de COMPRA:")
        print(f"💰 Quantidade: {amount} BTC")
        print(f"💲 Valor: ${usdt_value:.2f}")
        
        # Verificar saldo
        balance = exchange.fetch_balance()
        usdt_balance = balance.get('USDT', {}).get('free', 0)
        print(f"💰 Saldo USDT: ${usdt_balance}")
        
        if usdt_balance < usdt_value:
            print(f"❌ Saldo insuficiente!")
            return False
            
        print(f"✅ Saldo suficiente!")
        
        # Executar COMPRA
        print(f"🟢 Executando COMPRA...")
        order = exchange.create_market_buy_order('BTC/USDT', amount)
        
        print(f"🎉 COMPRA EXECUTADA COM SUCESSO!")
        print(f"📋 Order ID: {order['id']}")
        print(f"💰 Preço: ${order['price']}")
        print(f"📊 Status: {order['status']}")
        print(f"📈 Quantidade: {order['amount']} BTC")
        
        return order
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🎯 Vamos fazer um trade real de COMPRA!")
    print("=" * 50)
    
    response = input("🤔 Quer fazer uma COMPRA de ~$11.60 em BTC? (s/n): ")
    
    if response.lower() == 's':
        order = force_buy_trade()
        
        if order:
            print("\n✅ TRADE REAL EXECUTADO COM SUCESSO!")
            print("🎯 Sistema funcionando perfeitamente!")
            print("🚀 Pronto para operar oficialmente!")
        else:
            print("\n❌ Falha no trade")
    else:
        print("👌 Trade cancelado")

if __name__ == "__main__":
    main()
