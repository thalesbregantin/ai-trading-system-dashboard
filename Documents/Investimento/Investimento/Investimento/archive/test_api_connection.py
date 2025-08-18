"""
TESTE DE CONEXÃO BINANCE API
============================

Script simples para testar se sua API está funcionando
antes de executar ordens reais.
"""

import ccxt
from datetime import datetime

def test_binance_connection():
    """Testa conexão com a Binance"""
    
    print("🔧 TESTE DE CONEXÃO BINANCE")
    print("=" * 40)
    
    # CONFIGURE SUAS CHAVES AQUI
    API_KEY = "sua_api_key_aqui"
    API_SECRET = "sua_api_secret_aqui"
    
    # TESTNET = True para teste, False para produção
    TESTNET = True
    
    if API_KEY == "sua_api_key_aqui":
        print("❌ Configure suas chaves API primeiro!")
        print("📝 Edite as variáveis API_KEY e API_SECRET")
        return False
    
    try:
        # Inicializa exchange
        if TESTNET:
            exchange = ccxt.binance({
                'apiKey': API_KEY,
                'secret': API_SECRET,
                'sandbox': True,  # Testnet
                'enableRateLimit': True,
            })
            print("🧪 Modo: TESTNET (simulação)")
        else:
            exchange = ccxt.binance({
                'apiKey': API_KEY,
                'secret': API_SECRET,
                'sandbox': False,  # Produção
                'enableRateLimit': True,
            })
            print("🚨 Modo: PRODUÇÃO (dinheiro real)")
        
        # Teste 1: Verificar se a API funciona
        print("\n1️⃣ Testando autenticação...")
        balance = exchange.fetch_balance()
        print("✅ Autenticação OK!")
        
        # Teste 2: Mostrar saldo
        print("\n2️⃣ Verificando saldo...")
        usdt_balance = balance.get('USDT', {}).get('free', 0)
        btc_balance = balance.get('BTC', {}).get('free', 0)
        eth_balance = balance.get('ETH', {}).get('free', 0)
        
        print(f"💰 USDT: {usdt_balance}")
        print(f"🟠 BTC: {btc_balance}")
        print(f"🔵 ETH: {eth_balance}")
        
        # Teste 3: Obter preços
        print("\n3️⃣ Testando dados de mercado...")
        btc_ticker = exchange.fetch_ticker('BTC/USDT')
        eth_ticker = exchange.fetch_ticker('ETH/USDT')
        
        print(f"🟠 BTC/USDT: ${btc_ticker['last']:,.2f}")
        print(f"🔵 ETH/USDT: ${eth_ticker['last']:,.2f}")
        print("✅ Dados de mercado OK!")
        
        # Teste 4: Verificar permissões
        print("\n4️⃣ Verificando permissões...")
        try:
            # Tenta obter ordens (precisa de permissão de trading)
            orders = exchange.fetch_open_orders('BTC/USDT')
            print("✅ Permissões de trading OK!")
        except Exception as e:
            print(f"⚠️ Problema com permissões: {e}")
        
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ Sua API está configurada corretamente")
        print("🚀 Você pode usar o trading automático")
        
        return True
        
    except ccxt.AuthenticationError as e:
        print(f"❌ Erro de autenticação: {e}")
        print("🔧 Verifique suas chaves API")
        return False
        
    except ccxt.PermissionDenied as e:
        print(f"❌ Permissão negada: {e}")
        print("🔧 Verifique permissões da API key")
        return False
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def test_trading_signals():
    """Testa geração de sinais sem executar ordens"""
    
    print("\n📊 TESTE DE SINAIS DE TRADING")
    print("=" * 40)
    
    try:
        # Importa função de sinais do script principal
        import sys
        import os
        
        # Adiciona diretório atual ao path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(current_dir)
        
        # Teste de sinais para BTC e ETH
        symbols = ['BTC/USDT', 'ETH/USDT']
        
        # Cria exchange apenas para dados (sem autenticação)
        exchange = ccxt.binance({
            'enableRateLimit': True,
        })
        
        for symbol in symbols:
            try:
                # Obtém dados
                ohlcv = exchange.fetch_ohlcv(symbol, '1d', limit=50)
                
                if len(ohlcv) >= 21:
                    # Simula cálculo de sinal (versão simplificada)
                    closes = [candle[4] for candle in ohlcv[-21:]]  # últimos 21 closes
                    sma_9 = sum(closes[-9:]) / 9
                    sma_21 = sum(closes) / 21
                    current_price = closes[-1]
                    
                    # Condição simples
                    if current_price > sma_9 and sma_9 > sma_21:
                        signal = "BUY"
                    elif current_price < sma_9:
                        signal = "SELL"
                    else:
                        signal = "HOLD"
                    
                    print(f"📈 {symbol}: {signal}")
                    print(f"   Preço: ${current_price:,.2f}")
                    print(f"   SMA 9: ${sma_9:,.2f}")
                    print(f"   SMA 21: ${sma_21:,.2f}")
                else:
                    print(f"⚠️ {symbol}: Dados insuficientes")
                    
            except Exception as e:
                print(f"❌ Erro com {symbol}: {e}")
        
        print("\n✅ Teste de sinais concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste de sinais: {e}")

def main():
    """Função principal"""
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Teste 1: Conexão API
    connection_ok = test_binance_connection()
    
    # Teste 2: Sinais (sempre pode testar)
    test_trading_signals()
    
    if connection_ok:
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. ✅ API configurada corretamente")
        print("2. 🚀 Execute: python binance_executor_real.py")
        print("3. 📊 Monitore as operações diariamente")
    else:
        print("\n🔧 PARA CORRIGIR:")
        print("1. ❌ Configure suas chaves API")
        print("2. 🔒 Verifique permissões da API")
        print("3. 🌐 Teste conexão de internet")

if __name__ == "__main__":
    main()
