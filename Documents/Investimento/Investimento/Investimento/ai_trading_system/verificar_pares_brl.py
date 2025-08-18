#!/usr/bin/env python3
"""
Verificar pares disponíveis com BRL na Binance
"""

import ccxt

API_KEY = "Jsga4pAg9nndc0JmoWVt9w8rd9xQHxNFK7oxn11lKWtwS86MpruPbEdGXnkdkOzM"
API_SECRET = "7q8w7cWMkUvytSG1bFzYOosRzLrl4AOWk6v3Q1EMYOQcDer0R88EL5b7TP5opU2M"

def verificar_pares_brl():
    """Verifica quais pares com BRL estão disponíveis"""
    print("🔍 VERIFICANDO PARES DISPONÍVEIS COM BRL")
    print("=" * 50)
    
    try:
        exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
        })
        
        # Carrega todos os mercados
        markets = exchange.load_markets()
        
        # Filtra pares com BRL
        pares_brl = []
        for symbol in markets:
            if 'BRL' in symbol:
                pares_brl.append(symbol)
        
        print(f"📊 Encontrados {len(pares_brl)} pares com BRL:")
        
        if pares_brl:
            for par in sorted(pares_brl):
                try:
                    ticker = exchange.fetch_ticker(par)
                    print(f"   {par}: {ticker['last']:.8f}")
                except:
                    print(f"   {par}: (sem preço)")
        else:
            print("❌ Nenhum par com BRL encontrado")
        
        # Verifica especificamente alguns pares importantes
        print(f"\n🔍 Verificando pares específicos:")
        
        pares_teste = ['BTC/BRL', 'ETH/BRL', 'USDT/BRL', 'BNB/BRL']
        
        for par in pares_teste:
            try:
                ticker = exchange.fetch_ticker(par)
                print(f"✅ {par}: {ticker['last']:.2f}")
            except Exception as e:
                print(f"❌ {par}: não disponível")
        
        # Sugestões para conversão
        print(f"\n💡 SUGESTÕES PARA CONVERSÃO:")
        
        if 'BTC/BRL' in pares_brl:
            ticker_btc_brl = exchange.fetch_ticker('BTC/BRL')
            ticker_btc_usdt = exchange.fetch_ticker('BTC/USDT')
            
            print(f"📊 Opção 1: BRL → BTC → USDT")
            print(f"   BTC/BRL: R$ {ticker_btc_brl['last']:,.2f}")
            print(f"   BTC/USDT: $ {ticker_btc_usdt['last']:,.2f}")
            
            # Calcula conversão estimada
            brl_amount = 100
            btc_amount = brl_amount / ticker_btc_brl['last']
            usdt_amount = btc_amount * ticker_btc_usdt['last']
            
            print(f"   R$ {brl_amount:.2f} → {btc_amount:.8f} BTC → $ {usdt_amount:.2f} USDT")
        
        if 'USDT/BRL' in pares_brl:
            ticker_usdt_brl = exchange.fetch_ticker('USDT/BRL')
            
            print(f"📊 Opção 2: Comprar USDT diretamente")
            print(f"   USDT/BRL: R$ {ticker_usdt_brl['last']:.4f}")
            
            brl_amount = 100
            usdt_amount = brl_amount / ticker_usdt_brl['last']
            print(f"   R$ {brl_amount:.2f} → $ {usdt_amount:.2f} USDT")
        
        print(f"\n💡 COMO FAZER A CONVERSÃO:")
        print(f"1. 📱 Use o app da Binance (mais fácil)")
        print(f"2. 💻 Use o site da Binance")
        print(f"3. 🔧 Use a API (mais técnico)")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_pares_brl()
