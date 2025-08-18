#!/usr/bin/env python3
"""
Teste Simples de Conexão
"""

try:
    import ccxt
    print("✅ CCXT importado com sucesso")
    
    # Testa configuração básica
    api_key = "Jsga4pAg9nndc0JmoWVt9w8rd9xQHxNFK7oxn11lKWtwS86MpruPbEdGXnkdkOzM"
    api_secret = "7q8w7cWMkUvytSG1bFzYOosRzLrl4AOWk6v3Q1EMYOQcDer0R88EL5b7TP5opU2M"
    
    print(f"🔑 API Key: {api_key[:10]}...")
    print(f"🔐 Secret: {api_secret[:10]}...")
    
    # Cria exchange
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
    })
    
    print("✅ Exchange criado")
    
    # Testa markets
    markets = exchange.load_markets()
    print(f"✅ Markets carregados: {len(markets)} pares")
    
    # Testa saldo
    try:
        balance = exchange.fetch_balance()
        print(f"✅ Saldo obtido com sucesso")
        
        # Mostra USDT se existir
        if 'USDT' in balance:
            usdt_balance = balance['USDT']
            print(f"💰 USDT: {usdt_balance['total']:.2f} (Free: {usdt_balance['free']:.2f})")
        
        # Conta moedas com saldo
        currencies_with_balance = 0
        for currency, amounts in balance.items():
            if isinstance(amounts, dict) and amounts.get('total', 0) > 0:
                currencies_with_balance += 1
        
        print(f"💼 Moedas com saldo: {currencies_with_balance}")
        
    except Exception as e:
        print(f"❌ Erro ao obter saldo: {e}")
    
    print("\n🎉 Teste básico concluído!")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
except Exception as e:
    print(f"❌ Erro geral: {e}")
