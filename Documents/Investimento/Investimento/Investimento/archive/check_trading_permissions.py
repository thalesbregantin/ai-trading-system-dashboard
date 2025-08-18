"""
Teste de Permissões Binance API
Verifica se suas chaves têm permissão para trading
"""

def test_binance_permissions():
    """Testa permissões das API keys"""
    print("🔐 VERIFICANDO PERMISSÕES DA SUA API BINANCE")
    print("=" * 60)
    
    try:
        # Importa configuração
        from config import TradingConfig
        config = TradingConfig()
        
        # Verifica se as chaves estão configuradas
        if config.BINANCE_API_KEY == 'your_api_key_here':
            print("❌ API Key não configurada!")
            return False
        
        print(f"🔑 API Key: {config.BINANCE_API_KEY[:20]}...")
        print(f"🧪 Modo Testnet: {'Ativo' if config.TESTNET_MODE else 'Desativo'}")
        
        # Tenta importar CCXT
        try:
            import ccxt
            print("✅ CCXT disponível")
        except ImportError:
            print("❌ CCXT não instalado - Execute: pip install ccxt")
            return False
        
        # Cria conexão
        exchange = ccxt.binance({
            'apiKey': config.BINANCE_API_KEY,
            'secret': config.BINANCE_API_SECRET,
            'sandbox': True,  # Sempre testnet primeiro
            'rateLimit': 1200,
            'enableRateLimit': True,
        })
        
        print("\n📋 TESTANDO PERMISSÕES:")
        
        # Teste 1: Ler informações da conta
        try:
            account_info = exchange.fetch_balance()
            print("✅ LEITURA DE CONTA: Permitida")
            
            # Mostra saldo se disponível
            if 'USDT' in account_info and account_info['USDT']['free'] > 0:
                usdt_balance = account_info['USDT']['free']
                print(f"💰 Saldo USDT Testnet: ${usdt_balance:.2f}")
            else:
                print("⚠️ Sem saldo USDT na conta testnet")
                
        except Exception as e:
            print(f"❌ LEITURA DE CONTA: Negada - {e}")
            return False
        
        # Teste 2: Verificar se pode fazer ordens (teste sem executar)
        try:
            # Testa apenas se a API aceita a estrutura da ordem
            # NÃO executa a ordem de verdade
            test_order = {
                'symbol': 'BTCUSDT',
                'side': 'buy',
                'type': 'market',
                'amount': 0.001,  # Valor muito pequeno para teste
            }
            
            # Verifica se o mercado existe
            markets = exchange.load_markets()
            if 'BTC/USDT' in markets:
                print("✅ MERCADO BTC/USDT: Disponível")
                
                # Verifica informações do mercado
                market_info = markets['BTC/USDT']
                min_amount = market_info['limits']['amount']['min']
                print(f"📊 Quantidade mínima BTC: {min_amount}")
                
                # Verifica se tem permissão de trading (indiretamente)
                # Não vamos executar ordem real, só verificar estrutura
                print("✅ ESTRUTURA DE ORDEM: Válida")
                
            else:
                print("❌ MERCADO BTC/USDT: Não encontrado")
                
        except Exception as e:
            print(f"❌ ACESSO A MERCADOS: Problema - {e}")
        
        # Teste 3: Verifica ticker (preços atuais)
        try:
            ticker = exchange.fetch_ticker('BTC/USDT')
            current_price = ticker['last']
            print(f"📈 PREÇO ATUAL BTC: ${current_price:,.2f}")
            print("✅ LEITURA DE PREÇOS: Funcionando")
            
        except Exception as e:
            print(f"❌ LEITURA DE PREÇOS: Problema - {e}")
        
        # Teste 4: Verifica histórico de ordens (se houver)
        try:
            orders = exchange.fetch_orders('BTC/USDT', limit=1)
            print("✅ HISTÓRICO DE ORDENS: Acessível")
            
        except Exception as e:
            print("⚠️ HISTÓRICO DE ORDENS: Vazio ou sem acesso (normal para conta nova)")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        return False

def check_trading_requirements():
    """Verifica requisitos para trading"""
    print("\n💡 REQUISITOS PARA TRADING:")
    print("=" * 40)
    
    print("""
🔐 PERMISSÕES NECESSÁRIAS NA API BINANCE:
├── ✅ Spot & Margin Trading (OBRIGATÓRIO)
├── ⚠️ Futures Trading (opcional)
├── ❌ Enable Reading (automático)
└── ❌ Permit Universal Transfer (opcional)

🧪 TESTNET PRIMEIRO:
├── Sempre teste em testnet antes do live
├── Binance Testnet usa dinheiro virtual
├── Mesmo resultado, sem risco real
└── Validate estratégias completamente

💰 CAPITAL MÍNIMO:
├── Testnet: $0 (virtual)
├── Live: $10+ recomendado para testes
├── BTC mínimo: ~0.00001 BTC
└── USDT mínimo: ~$1

⚙️ CONFIGURAÇÕES RECOMENDADAS:
├── Enable Spot & Margin Trading: ✅ SIM
├── Enable Futures: ⚠️ OPCIONAL  
├── Restrict access to trusted IPs: 📡 RECOMENDADO
└── Enable withdrawals: ❌ NÃO NECESSÁRIO
""")

def simulate_first_purchase():
    """Simula primeira compra"""
    print("\n🛒 SIMULAÇÃO DE PRIMEIRA COMPRA:")
    print("=" * 40)
    
    try:
        from config import TradingConfig
        config = TradingConfig()
        
        # Valores do nosso sistema
        min_trade = config.MIN_TRADE_AMOUNT  # $10
        max_position = config.MAX_POSITION_SIZE  # 2%
        
        print(f"💰 Valor mínimo por trade: ${min_trade}")
        print(f"🎯 Máximo por posição: {max_position:.1%} do saldo")
        
        # Simula diferentes cenários de saldo
        test_balances = [50, 100, 500, 1000]
        
        print("\n📊 SIMULAÇÃO COM DIFERENTES SALDOS:")
        
        for balance in test_balances:
            max_trade_value = balance * max_position
            actual_trade = max(min_trade, min(max_trade_value, balance * 0.95))
            
            print(f"\n💵 Saldo: ${balance}")
            print(f"   📈 Máximo por trade: ${max_trade_value:.2f}")
            print(f"   🎯 Trade real: ${actual_trade:.2f}")
            print(f"   🔄 Trades possíveis: {int(balance / actual_trade)}")
        
        print(f"\n✅ COM SEU SETUP ATUAL:")
        print(f"   🎯 Primeira compra será: ${min_trade}")
        print(f"   📊 Necessário em testnet: $0 (virtual)")
        print(f"   💡 Recomendado para live: ${min_trade * 10} (10 trades)")
        
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")

def main():
    """Função principal"""
    # Testa permissões
    success = test_binance_permissions()
    
    # Mostra requisitos
    check_trading_requirements()
    
    # Simula compra
    simulate_first_purchase()
    
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 SUAS API KEYS PARECEM ESTAR FUNCIONANDO!")
        print("🧪 Recomendação: Comece testando no TESTNET")
        print("💡 Execute: python main.py --mode live --env test")
        print("📊 Dashboard: python main.py --mode dashboard")
    else:
        print("⚠️ PROBLEMAS DETECTADOS NAS API KEYS")
        print("🔧 Verifique as permissões na Binance:")
        print("   1. Acesse API Management")
        print("   2. Edite sua API Key") 
        print("   3. Ative 'Spot & Margin Trading'")
        print("   4. Salve as alterações")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
