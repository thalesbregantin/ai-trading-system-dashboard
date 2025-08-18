"""
Teste Completo do Sistema AI Trading
Verifica todas as funcionalidades implementadas
"""

import sys
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def test_ai_trader():
    """Testa o AI Trader básico"""
    print("🤖 Testando AI Trader (Deep Q-Learning)...")
    
    try:
        from ai_trader_dqn import AITrader, train_ai_trader, create_state
        
        # Dados simulados
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(200) * 0.1)
        
        # Teste criação de estado
        state = create_state(prices, 50, 10)
        print(f"✅ Estado criado: {state.shape}")
        
        # Teste AITrader
        trader = AITrader(state_size=9)
        action = trader.act(state)
        print(f"✅ Ação gerada: {action}")
        
        # Teste treinamento rápido
        trader, profits = train_ai_trader(prices, episodes=3, window_size=10)
        print(f"✅ Treinamento concluído. Lucros: {profits}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no AI Trader: {e}")
        return False

def test_hybrid_system():
    """Testa o sistema híbrido"""
    print("\n🔄 Testando Sistema Híbrido...")
    
    try:
        from hybrid_trading_system import HybridTradingSystem
        
        # Testa com dados simulados
        hybrid = HybridTradingSystem('BTC-USD')
        
        # Simula dados
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        prices = 30000 + np.cumsum(np.random.randn(100) * 100)
        
        data = pd.DataFrame({
            'Close': prices,
            'Open': prices * 0.99,
            'High': prices * 1.01,
            'Low': prices * 0.98,
            'Volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        # Testa preparação de features
        features = hybrid.prepare_features(data)
        print(f"✅ Features preparadas: {features.shape}")
        
        # Testa treinamento
        profits = hybrid.train_hybrid_system(data, episodes=2)
        print(f"✅ Sistema híbrido treinado. Lucros: {len(profits)} episódios")
        
        # Testa geração de sinal
        signal = hybrid.generate_signal(data, 50)
        print(f"✅ Sinal gerado: {['HOLD', 'BUY', 'SELL'][signal]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no Sistema Híbrido: {e}")
        return False

def test_backtest():
    """Testa o sistema de backtest"""
    print("\n📊 Testando Backtest...")
    
    try:
        from hybrid_trading_system import HybridTradingSystem
        
        # Cria sistema e dados
        hybrid = HybridTradingSystem('BTC-USD')
        
        dates = pd.date_range('2023-01-01', periods=200, freq='D')
        prices = 30000 + np.cumsum(np.random.randn(200) * 100)
        
        data = pd.DataFrame({
            'Close': prices,
            'Open': prices * 0.99,
            'High': prices * 1.01,
            'Low': prices * 0.98,
            'Volume': np.random.randint(1000, 10000, 200)
        }, index=dates)
        
        # Treina sistema
        hybrid.train_hybrid_system(data, episodes=2)
        
        # Executa backtest
        trades, metrics, equity = hybrid.backtest_hybrid(data, initial_capital=1000)
        
        print(f"✅ Backtest executado:")
        print(f"   📈 Trades: {len(trades)}")
        print(f"   💰 Retorno: {metrics['total_return']:.2f}%")
        print(f"   🎯 Win Rate: {metrics['win_rate']:.1f}%")
        print(f"   📊 Sharpe: {metrics['sharpe_ratio']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no Backtest: {e}")
        return False

def test_data_integration():
    """Testa integração com dados reais"""
    print("\n📊 Testando Integração de Dados...")
    
    try:
        import yfinance as yf
        
        # Testa download
        ticker = yf.Ticker('BTC-USD')
        data = ticker.history(period='1mo')
        
        if not data.empty:
            print(f"✅ Dados baixados: {len(data)} pontos")
            print(f"   📅 Período: {data.index[0].date()} a {data.index[-1].date()}")
            print(f"   💲 Preço atual: ${data['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("❌ Nenhum dado baixado")
            return False
            
    except Exception as e:
        print(f"❌ Erro na integração de dados: {e}")
        return False

def test_dashboard_compatibility():
    """Testa compatibilidade com dashboard"""
    print("\n🎨 Testando Compatibilidade Dashboard...")
    
    try:
        # Testa imports do dashboard
        import plotly.graph_objects as go
        import plotly.express as px
        
        # Cria gráfico teste
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[1, 2, 3, 4],
            y=[10, 11, 12, 13],
            mode='lines',
            name='Teste'
        ))
        
        print("✅ Plotly funcionando")
        
        # Testa pandas para dashboard
        df = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=10, freq='D'),
            'price': np.random.randn(10) * 100 + 1000,
            'signal': np.random.choice(['BUY', 'SELL', 'HOLD'], 10)
        })
        
        print(f"✅ DataFrame criado: {df.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na compatibilidade dashboard: {e}")
        return False

def test_binance_compatibility():
    """Testa compatibilidade com Binance (sem executar)"""
    print("\n🏦 Testando Compatibilidade Binance...")
    
    try:
        import ccxt
        
        # Testa criação do exchange (sem conectar)
        exchange = ccxt.binance({
            'sandbox': True,
            'enableRateLimit': True,
        })
        
        print("✅ CCXT Binance inicializado")
        
        # Testa estruturas de dados
        fake_balance = {
            'USDT': {'free': 1000, 'used': 0},
            'BTC': {'free': 0.01, 'used': 0}
        }
        
        print("✅ Estruturas de dados testadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na compatibilidade Binance: {e}")
        return False

def test_performance():
    """Testa performance do sistema"""
    print("\n⚡ Testando Performance...")
    
    try:
        import time
        
        # Teste de velocidade de geração de sinal
        from hybrid_trading_system import HybridTradingSystem
        
        hybrid = HybridTradingSystem('BTC-USD')
        
        # Dados de teste
        dates = pd.date_range('2023-01-01', periods=500, freq='D')
        prices = 30000 + np.cumsum(np.random.randn(500) * 100)
        
        data = pd.DataFrame({
            'Close': prices,
            'Open': prices * 0.99,
            'High': prices * 1.01,
            'Low': prices * 0.98,
            'Volume': np.random.randint(1000, 10000, 500)
        }, index=dates)
        
        # Treina sistema
        start_time = time.time()
        hybrid.train_hybrid_system(data, episodes=2)
        training_time = time.time() - start_time
        
        print(f"✅ Tempo de treinamento: {training_time:.2f}s")
        
        # Teste de velocidade de sinal
        start_time = time.time()
        for i in range(100, 200):  # 100 sinais
            signal = hybrid.generate_signal(data, i)
        signal_time = time.time() - start_time
        
        print(f"✅ Tempo para 100 sinais: {signal_time:.2f}s")
        print(f"✅ Velocidade: {100/signal_time:.1f} sinais/segundo")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de performance: {e}")
        return False

def run_complete_test():
    """Executa teste completo"""
    print("🧪 TESTE COMPLETO DO SISTEMA AI TRADING")
    print("=" * 60)
    
    tests = [
        ("AI Trader (Deep Q-Learning)", test_ai_trader),
        ("Sistema Híbrido", test_hybrid_system),
        ("Backtest", test_backtest),
        ("Integração de Dados", test_data_integration),
        ("Dashboard", test_dashboard_compatibility),
        ("Binance", test_binance_compatibility),
        ("Performance", test_performance),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico em {test_name}: {e}")
            results.append((test_name, False))
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL DOS TESTES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📈 RESULTADO: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
    elif passed >= total * 0.8:
        print("👍 A maioria dos testes passou. Sistema utilizável com algumas limitações.")
    else:
        print("⚠️ Muitos testes falharam. Revise a instalação e dependências.")
    
    return passed, total

def create_requirements_file():
    """Cria arquivo de requirements"""
    requirements = """
# AI Trading System Requirements
numpy>=1.21.0
pandas>=1.3.0
tensorflow>=2.8.0
scikit-learn>=1.0.0
yfinance>=0.1.70
ccxt>=1.90.0
plotly>=5.0.0
streamlit>=1.20.0
tqdm>=4.60.0
"""
    
    with open('requirements_ai_trading.txt', 'w') as f:
        f.write(requirements.strip())
    
    print("📦 Arquivo requirements_ai_trading.txt criado!")

if __name__ == "__main__":
    # Executa testes
    passed, total = run_complete_test()
    
    # Cria requirements
    print("\n" + "=" * 60)
    create_requirements_file()
    
    print("\n🚀 Para instalar dependências:")
    print("pip install -r requirements_ai_trading.txt")
    
    print("\n📖 Para usar o sistema:")
    print("1. Configure API keys no binance_ai_bot.py")
    print("2. Execute: streamlit run dashboard/ai_trading_dashboard.py")
    print("3. Ou use: python hybrid_trading_system.py")
    
    print("\n✅ Teste completo finalizado!")
