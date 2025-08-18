#!/usr/bin/env python3
"""
Teste simples para verificar conexão com Binance
"""

import ccxt
import os

# Configurar chaves diretamente
BINANCE_API_KEY = "Gm5VZwg3DzYD7FQXiocUsnhU7CYh5omlb8phvcxuEkec8YgVHHk0AhhyCxMRr80b"
BINANCE_SECRET_KEY = "VxRa16ZG8FaA854JsviUWBHsg3Sbw46WlIjwUsXlR67DM0wUwQhGLtvtN00U0Vch"

def test_binance_connection():
    """Testar conexão com Binance"""
    print("🔗 Testando conexão com Binance...")
    
    try:
        # Inicializar exchange
        exchange = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_SECRET_KEY,
            'sandbox': False,
            'enableRateLimit': True
        })
        
        print("✅ Exchange inicializado")
        
        # Testar carregamento de mercados
        print("📊 Carregando mercados...")
        exchange.load_markets()
        print("✅ Mercados carregados")
        
        # Obter saldo da conta
        print("💰 Obtendo saldo da conta...")
        balance = exchange.fetch_balance()
        
        print("\n📈 SALDO DA CONTA:")
        print("=" * 50)
        
        total_usdt = 0
        for currency, amount in balance['total'].items():
            if amount > 0:
                if currency == 'USDT':
                    usdt_value = amount
                    total_usdt += usdt_value
                    print(f"💵 {currency}: {amount:.8f} (${usdt_value:.2f})")
                else:
                    try:
                        # Tentar obter preço em USDT
                        ticker = exchange.fetch_ticker(f'{currency}/USDT')
                        usdt_value = amount * ticker['last']
                        total_usdt += usdt_value
                        print(f"💵 {currency}: {amount:.8f} (${usdt_value:.2f}) - Preço: ${ticker['last']:.4f}")
                    except:
                        print(f"💵 {currency}: {amount:.8f} (Preço não disponível)")
        
        print("=" * 50)
        print(f"💰 TOTAL EM USDT: ${total_usdt:.2f}")
        
        # Obter preço atual do BTC
        print("\n📊 PREÇO ATUAL BTC/USDT:")
        btc_ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"💎 BTC: ${btc_ticker['last']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

if __name__ == "__main__":
    test_binance_connection()
