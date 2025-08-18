"""
Sistema Principal AI Trading
Orquestra todos os componentes do sistema
"""

import argparse
import sys
import logging
from datetime import datetime
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

from core.config import get_config, TradingConfig

def setup_logging(config):
    """Configura sistema de logging"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_test_mode(config):
    """Executa modo de teste básico"""
    print("🧪 MODO TESTE")
    print("-" * 40)
    
    try:
        # Teste básico de importação
        from core.ai_trader_dqn import AITrader
        from core.hybrid_trading_system import HybridTradingSystem
        from core.binance_ai_bot import BinanceAIBot
        
        print("✅ Importações OK")
        print("✅ Sistema pronto para operar")
        
        # Teste rápido de configuração
        print(f"📊 Modo: {'TESTNET' if config.TESTNET_MODE else 'LIVE'}")
        print(f"🔑 API configurada: {len(config.BINANCE_API_KEY) > 10}")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    
    return True

def run_train_mode(config, initial_capital=None):
    """Executa treinamento do AI"""
    print("🎓 MODO TREINAMENTO")
    print("-" * 40)
    
    try:
        from core.ai_trader_dqn import train_ai_trader
        from core.hybrid_trading_system import train_hybrid_system
        import yfinance as yf
        
        symbol = 'BTC/USDT'
        print(f"Carregando dados para {symbol}...")
        
        # Converte símbolo para formato Yahoo Finance
        yf_symbol = config.YFINANCE_SYMBOLS.get(symbol, symbol)
        print(f"📊 Usando símbolo Yahoo Finance: {yf_symbol}")
        
        # Baixa dados históricos
        print("📊 Baixando dados históricos...")
        ticker = yf.Ticker(yf_symbol)
        data = ticker.history(period='1y')
        
        if data.empty:
            print(f"❌ Falha ao baixar dados para {symbol}")
            return None, None
        
        # Usa apenas preços de fechamento
        prices = data['Close'].values
        print(f"✅ {len(prices)} pontos de dados baixados")
        
        # Executa treinamento
        trader, equities = train_hybrid_system(
            prices,
            episodes=config.AI_EPISODES,
            window_size=config.AI_WINDOW_SIZE,
            initial_capital=initial_capital
        )
        
        print("✅ Treinamento concluído!")
        
        # Salva modelo
        model_path = f"models/ai_model_{symbol.replace('/', '_')}.h5"
        import os
        os.makedirs('models', exist_ok=True)
        trader.model.save(model_path)
        print(f"💾 Modelo salvo: {model_path}")
        
        return trader, equities
        
    except Exception as e:
        print(f"❌ Erro no treinamento: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def run_backtest_mode(config, symbol='BTC-USD'):
    """Executa backtest do sistema híbrido"""
    print("📈 MODO BACKTEST")
    print("-" * 40)
    
    try:
        from core.hybrid_trading_system import HybridTradingSystem
        
        # Cria sistema híbrido
        hybrid_system = HybridTradingSystem(
            ai_weight=config.AI_WEIGHT,
            momentum_weight=config.MOMENTUM_WEIGHT
        )
        
        print(f"🔄 Executando backtest para {symbol}")
        
        # Baixa dados para backtest
        data = hybrid_system.download_data(period='1y')
        
        # Treina o sistema primeiro
        print("🎓 Treinando sistema para backtest...")
        hybrid_system.train_hybrid_system(data, episodes=10, initial_capital=config.INITIAL_CAPITAL)
        
        # Executa backtest
        trades, metrics, equity = hybrid_system.backtest_hybrid(
            data=data,
            initial_capital=config.INITIAL_CAPITAL
        )
        
        results = metrics
        
        print("📊 RESULTADOS DO BACKTEST:")
        print(f"💰 Retorno Total: {results['total_return']:.2%}")
        print(f"📈 Sharpe Ratio: {results['sharpe_ratio']:.3f}")
        print(f"📉 Max Drawdown: {results['max_drawdown']:.2%}")
        print(f"🎯 Trades: {results['num_trades']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Erro no backtest: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_live_trading(config, duration=24):
    """Executa trading ao vivo"""
    print("🚀 MODO TRADING AO VIVO")
    print("-" * 40)
    
    if config.TESTNET_MODE:
        print("🧪 Executando em TESTNET (simulado)")
    else:
        print("💰 Executando em LIVE (dinheiro real)")
        confirm = input("⚠️ Confirma execução com dinheiro real? (digite 'CONFIRMO'): ")
        if confirm != 'CONFIRMO':
            print("❌ Execução cancelada")
            return
    
    try:
        from core.binance_ai_bot import BinanceAIBot
        
        # Cria bot de trading com parâmetros corretos
        bot = BinanceAIBot(
            api_key=config.BINANCE_API_KEY,
            api_secret=config.BINANCE_API_SECRET,
            testnet=config.TESTNET_MODE
        )
        
        print("🔗 Conectando à Binance...")
        if hasattr(bot, 'connect'):
            if not bot.connect():
                print("❌ Falha na conexão com Binance")
                return
        else:
            # Tenta operação simples para validar
            try:
                _ = bot.get_account_balance()
                print("✅ Conexão validada por fetch de saldo")
            except Exception as e:
                print(f"❌ Falha na conexão: {e}")
                return
        
        print("✅ Conectado com sucesso!")
        print(f"⏰ Iniciando sessão de trading ({duration}h)")
        
        # Executa trading
        bot.run_trading_session(duration_hours=duration)
        
    except Exception as e:
        print(f"❌ Erro no trading ao vivo: {e}")
        import traceback
        traceback.print_exc()

def run_dashboard_mode(config):
    """Executa dashboard Streamlit"""
    print("📊 MODO DASHBOARD")
    print("-" * 40)
    
    try:
        import subprocess
        import sys
        
        dashboard_path = Path(__file__).parent / "dashboard" / "main_dashboard.py"
        
        print(f"🌐 Iniciando dashboard: {dashboard_path}")
        print(f"🔗 URL: http://localhost:{config.DASHBOARD_PORT}")
        
        # Executa Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", str(config.DASHBOARD_PORT)
        ])
        
    except Exception as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")

def main():
    """Função principal do sistema"""
    
    print("🤖 AI TRADING SYSTEM")
    print("=" * 60)
    print("Sistema de Trading com Deep Q-Learning + Análise Técnica")
    print("=" * 60)
    
    # Parser de argumentos
    parser = argparse.ArgumentParser(description='AI Trading System')
    parser.add_argument('--mode', choices=['test', 'train', 'backtest', 'live', 'dashboard'], 
                       default='test', help='Modo de operação')
    parser.add_argument('--env', choices=['dev', 'test', 'prod'], 
                       default='prod', help='Ambiente de configuração')
    parser.add_argument('--symbol', default='BTC-USD', help='Símbolo para análise')
    parser.add_argument('--episodes', type=int, default=None, help='Episódios de treinamento')
    parser.add_argument('--duration', type=int, default=24, help='Duração do trading (horas)')
    
    args = parser.parse_args()
    
    # Carrega configuração
    config = get_config(args.env)  # retorna classe
    config = config()  # instancia
    
    if args.episodes:
        config.AI_EPISODES = args.episodes
    
    # Configura logging
    setup_logging(config)
    
    # Valida configuração
    print("⚙️ Validando configuração...")
    errors = config.validate_config()
    
    if errors:
        print("❌ ERROS DE CONFIGURAÇÃO:")
        for error in errors:
            print(f"  {error}")
        print("\n💡 Verifique as configurações antes de continuar!")
        return
    
    config.print_config()
    
    # Executa modo selecionado
    try:
        if args.mode == 'test':
            success = run_test_mode(config)
            if not success:
                sys.exit(1)
                
        elif args.mode == 'train':
            run_train_mode(config, config.INITIAL_CAPITAL)
            
        elif args.mode == 'backtest':
            run_backtest_mode(config, args.symbol)
            
        elif args.mode == 'live':
            run_live_trading(config, args.duration)
            
        elif args.mode == 'dashboard':
            run_dashboard_mode(config)
            
    except KeyboardInterrupt:
        print("\n👋 Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
