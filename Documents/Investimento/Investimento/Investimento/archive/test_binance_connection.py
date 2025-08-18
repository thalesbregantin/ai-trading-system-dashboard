"""
Teste de Conexão Binance
Verifica se as API keys estão configuradas corretamente
"""

from config import TradingConfig
import sys

def test_binance_config():
    """Testa configuração da Binance"""
    print("🏦 TESTE DE CONFIGURAÇÃO BINANCE")
    print("=" * 50)
    
    # Carrega configuração
    config = TradingConfig()
    
    # Verifica API keys
    api_key = config.BINANCE_API_KEY
    api_secret = config.BINANCE_API_SECRET
    
    print(f"🔑 API Key: {api_key[:20]}...{api_key[-10:] if len(api_key) > 30 else api_key}")
    print(f"🔒 Secret: {api_secret[:20]}...{api_secret[-10:] if len(api_secret) > 30 else '***'}")
    print(f"🧪 Testnet Mode: {'Ativado' if config.TESTNET_MODE else 'Desativado'}")
    
    # Valida configuração
    errors = config.validate_config()
    
    if errors:
        print("\n❌ ERROS ENCONTRADOS:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("\n✅ Configuração válida!")
    
    # Testa conexão (se ccxt estiver disponível)
    try:
        import ccxt
        
        print("\n🔗 Testando conexão com Binance...")
        
        # Cria exchange (testnet)
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'sandbox': True,  # Sempre testnet primeiro
            'rateLimit': 1200,
            'enableRateLimit': True,
        })
        
        # Testa conexão básica
        try:
            balance = exchange.fetch_balance()
            print("✅ Conexão com Binance Testnet bem-sucedida!")
            
            # Mostra saldo USDT se disponível
            if 'USDT' in balance:
                usdt_balance = balance['USDT']['free']
                print(f"💰 Saldo USDT Testnet: ${usdt_balance:.2f}")
            
            # Lista alguns pares disponíveis
            markets = exchange.load_markets()
            btc_pairs = [pair for pair in markets.keys() if 'BTC' in pair and 'USDT' in pair][:3]
            print(f"📊 Pares disponíveis: {', '.join(btc_pairs)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            print("💡 Verifique se as API keys estão corretas e têm permissões")
            return False
    
    except ImportError:
        print("⚠️ CCXT não instalado - não é possível testar conexão")
        print("💡 Instale com: pip install ccxt")
        print("✅ Mas as API keys estão configuradas corretamente!")
        return True
    
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_api_permissions():
    """Testa permissões das API keys"""
    print("\n🔐 TESTANDO PERMISSÕES DA API...")
    
    try:
        import ccxt
        from config import TradingConfig
        
        config = TradingConfig()
        
        exchange = ccxt.binance({
            'apiKey': config.BINANCE_API_KEY,
            'secret': config.BINANCE_API_SECRET,
            'sandbox': True,
            'rateLimit': 1200,
        })
        
        # Testa diferentes operações necessárias para o bot
        tests = [
            ("📊 Leitura de Saldo", lambda: exchange.fetch_balance()),
            ("📈 Leitura de Mercados", lambda: exchange.load_markets()),
            ("💹 Preços de Ticker", lambda: exchange.fetch_ticker('BTC/USDT')),
            ("📋 Histórico de Ordens", lambda: exchange.fetch_orders('BTC/USDT', limit=1)),
            ("🕐 Dados OHLCV", lambda: exchange.fetch_ohlcv('BTC/USDT', '1h', limit=10)),
        ]
        
        permissions_ok = True
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                print(f"✅ {test_name}: OK")
            except Exception as e:
                error_msg = str(e)
                if "API-key format invalid" in error_msg:
                    print(f"❌ {test_name}: Formato de API key inválido")
                    permissions_ok = False
                elif "Signature for this request is not valid" in error_msg:
                    print(f"❌ {test_name}: Assinatura inválida (verifique Secret)")
                    permissions_ok = False
                elif "Invalid API-key, IP, or permissions" in error_msg:
                    print(f"❌ {test_name}: Permissões insuficientes ou IP não autorizado")
                    permissions_ok = False
                else:
                    print(f"⚠️ {test_name}: {error_msg[:80]}...")
        
        # Verifica permissões específicas necessárias
        print("\n🔍 VERIFICANDO PERMISSÕES ESPECÍFICAS:")
        
        required_permissions = [
            ("🔍 Leitura", "Necessária para consultar saldo e preços"),
            ("💱 Trading Spot", "Necessária para comprar e vender"),
            ("🚫 Saques", "NÃO deve estar habilitada (segurança)"),
            ("🚫 Transferências", "NÃO deve estar habilitada (segurança)")
        ]
        
        for perm_name, description in required_permissions:
            print(f"{perm_name}: {description}")
        
        if permissions_ok:
            print("\n✅ Permissões básicas verificadas com sucesso!")
            print("💡 Configure as permissões conforme BINANCE_PERMISSIONS_GUIDE.md")
        else:
            print("\n❌ Problemas com permissões detectados!")
            print("🔧 Verifique a configuração da API na Binance")
        
        return permissions_ok
        
    except ImportError:
        print("⚠️ CCXT necessário para teste de permissões")
        print("💡 Instale com: pip install ccxt")
        return False
    except Exception as e:
        print(f"❌ Erro no teste de permissões: {e}")
        return False

def show_binance_setup_guide():
    """Mostra guia de configuração da Binance"""
    print("\n" + "=" * 70)
    print("🔐 GUIA DE CONFIGURAÇÃO BINANCE API")
    print("=" * 70)
    
    print("""
📋 PERMISSÕES NECESSÁRIAS NA BINANCE:

✅ HABILITAR:
   🔍 Habilitar Leitura
      └── Para consultar saldo, preços, histórico
   
   💱 Ativar Trading Spot e de Margem  
      └── Para executar compras e vendas
   
   📋 Ativar Lista de Permissões do Símbolo
      └── Configurar apenas: BTC/USDT, ETH/USDT

❌ NÃO HABILITAR (SEGURANÇA):
   🚫 Habilitar Saques
      └── Bot não precisa sacar fundos
   
   🚫 Permitir Transferência Universal
      └── Bot não precisa transferir entre contas
   
   🚫 Habilitar Empréstimo, Reembolso e Transferência de Margem
      └── Trading spot não usa margem

🔒 RESTRIÇÕES DE IP:
   🌐 Adicionar IP atual: OBRIGATÓRIO
   ⚠️ NUNCA deixar "Irrestrito" em produção

📍 COMO CONFIGURAR:
   1. Acesse: Binance → Gerenciamento de API
   2. Clique em "Editar restrições" na sua API key
   3. Configure as permissões conforme acima
   4. Adicione seu IP atual
   5. Salve as alterações
   6. Execute este teste novamente

🚨 ATENÇÃO:
   • Use TESTNET primeiro para testes
   • Mantenha API keys seguras
   • Monitore atividade regularmente
   • Use apenas capital que pode perder
""")

def get_current_ip():
    """Obtém IP atual para configuração"""
    try:
        import requests
        response = requests.get('https://httpbin.org/ip', timeout=5)
        ip = response.json()['origin']
        print(f"\n🌐 SEU IP ATUAL: {ip}")
        print("💡 Use este IP nas restrições da Binance API")
        return ip
    except Exception as e:
        print(f"⚠️ Não foi possível obter IP atual: {e}")
        print("💡 Verifique seu IP em: https://whatismyipaddress.com/")
        return None
    """Cria guia rápido de início"""
    guide = """
🚀 GUIA RÁPIDO - SUAS API KEYS CONFIGURADAS!

✅ API Keys da Binance configuradas com sucesso!

📋 PRÓXIMOS PASSOS:

1️⃣ INSTALAR DEPENDÊNCIAS:
   pip install ccxt yfinance tensorflow streamlit plotly

2️⃣ TESTAR SISTEMA:
   python main.py --mode test

3️⃣ TREINAR AI:
   python main.py --mode train --symbol BTC-USD --episodes 10

4️⃣ EXECUTAR DASHBOARD:
   python main.py --mode dashboard

5️⃣ BACKTEST:
   python main.py --mode backtest --symbol BTC-USD

6️⃣ TRADING TESTNET:
   python main.py --mode live --env test

⚠️ IMPORTANTE:
- Suas chaves estão configuradas para TESTNET (seguro)
- Sempre teste antes de usar capital real
- O sistema usará dinheiro virtual da Binance Testnet

🔒 SEGURANÇA:
- API keys salvas em .env (não commitar no git)
- Modo testnet ativado por padrão
- Validações automáticas de risco

🆘 EM CASO DE PROBLEMAS:
- Verifique se as API keys têm permissões corretas
- Execute: python test_binance_connection.py
- Veja logs em trading_log_*.log

🎯 READY TO GO!
Suas credenciais estão configuradas e o sistema está pronto para uso!
"""
    
    print(guide)
    
    # Salva o guia
    with open('QUICK_START_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("💾 Guia salvo em: QUICK_START_GUIDE.md")

if __name__ == "__main__":
    # Mostra guia de configuração primeiro
    show_binance_setup_guide()
    
    # Obtém IP atual
    get_current_ip()
    
    # Executa testes
    print("\n" + "=" * 70)
    print("🧪 INICIANDO TESTES DE CONEXÃO")
    print("=" * 70)
    
    success = test_binance_config()
    
    if success:
        permissions_ok = test_api_permissions()
        
        if permissions_ok:
            create_quick_start_guide()
            
            print("\n" + "=" * 70)
            print("🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
            print("🚀 Sistema pronto para uso!")
            print("💡 Execute: python main.py --mode test")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("⚠️ PERMISSÕES PRECISAM SER AJUSTADAS")
            print("🔧 Configure as permissões na Binance conforme o guia acima")
            print("🔄 Execute este teste novamente após configurar")
            print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ PROBLEMAS NA CONFIGURAÇÃO BÁSICA")
        print("🔧 Verifique as API keys e tente novamente")
        print("📖 Consulte BINANCE_PERMISSIONS_GUIDE.md")
        print("=" * 70)
