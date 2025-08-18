#!/usr/bin/env python3
"""
🤖 AI Trading System - Quick Start
Sistema de Trading Automatizado com Deep Q-Learning
"""

import os
import sys
from pathlib import Path

def quick_start():
    """Guia de início rápido"""
    
    print("🤖 AI TRADING SYSTEM - QUICK START")
    print("=" * 60)
    
    # Verifica se está no diretório correto
    if not Path("core/config.py").exists():
        print("❌ Execute este script dentro do diretório ai_trading_system/")
        return False
    
    # Verifica .env
    if not Path(".env").exists():
        print("⚠️ Arquivo .env não encontrado!")
        print("💡 Copie .env.example para .env e configure suas API keys")
        return False
    
    # Verifica dependências
    print("🔍 Verificando dependências...")
    try:
        import tensorflow
        import pandas
        import numpy
        import ccxt
        import streamlit
        print("✅ Dependências principais instaladas")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("💡 Execute: pip install -r requirements.txt")
        return False
    
    # Menu de opções
    print("\n🎯 OPÇÕES DISPONÍVEIS:")
    print("1️⃣ Teste básico do sistema")
    print("2️⃣ Treinar AI (20 episódios)")
    print("3️⃣ Executar backtest")
    print("4️⃣ Iniciar dashboard")
    print("5️⃣ Trading ao vivo (TESTNET)")
    print("6️⃣ Trading ao vivo (REAL) ⚠️")
    print("0️⃣ Sair")
    
    while True:
        try:
            choice = input("\n🤔 Escolha uma opção (0-6): ").strip()
            
            if choice == "0":
                print("👋 Até logo!")
                break
                
            elif choice == "1":
                os.system("python main.py --mode test")
                
            elif choice == "2":
                os.system("python main.py --mode train --episodes 20")
                
            elif choice == "3":
                os.system("python main.py --mode backtest")
                
            elif choice == "4":
                os.system("python main.py --mode dashboard")
                
            elif choice == "5":
                os.system("python main.py --mode live --env test")
                
            elif choice == "6":
                confirm = input("⚠️ ATENÇÃO: Trading com dinheiro real! Digite 'CONFIRMO' para continuar: ")
                if confirm == "CONFIRMO":
                    os.system("python main.py --mode live --env prod")
                else:
                    print("❌ Operação cancelada")
                    
            else:
                print("❌ Opção inválida! Escolha entre 0-6")
                
        except KeyboardInterrupt:
            print("\n👋 Sistema interrompido!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    return True

def show_help():
    """Mostra ajuda detalhada"""
    
    help_text = """
🤖 AI TRADING SYSTEM - AJUDA DETALHADA

📋 COMANDOS PRINCIPAIS:

🧪 TESTE BÁSICO:
   python main.py --mode test
   → Verifica se sistema está funcionando

🎓 TREINAMENTO AI:
   python main.py --mode train --episodes 20
   → Treina rede neural com 20 episódios

📈 BACKTEST:
   python main.py --mode backtest --symbol BTC-USD
   → Testa estratégia em dados históricos

📊 DASHBOARD:
   python main.py --mode dashboard
   → Interface web em http://localhost:8501

🚀 TRADING AO VIVO:
   python main.py --mode live --env test    # TESTNET
   python main.py --mode live --env prod    # REAL ⚠️

⚙️ CONFIGURAÇÕES:

📁 Arquivo .env:
   BINANCE_API_KEY=sua_api_key
   BINANCE_API_SECRET=sua_api_secret
   TESTNET_MODE=true
   LIVE_TRADING=false

📊 Parâmetros em core/config.py:
   AI_EPISODES = 20
   MAX_POSITION_SIZE = 0.02  # 2%
   STOP_LOSS_PCT = 0.05      # 5%

🔗 LINKS ÚTEIS:

📋 Binance API: https://www.binance.com/en/my/settings/api-management
🧪 Testnet: https://testnet.binance.vision/
📊 Dashboard: http://localhost:8501

⚠️ AVISOS IMPORTANTES:

🧪 SEMPRE teste no TESTNET primeiro
🔑 Mantenha API keys seguras
💰 Use apenas capital que pode perder
📊 Monitore via dashboard
🛡️ Configure stop-loss adequado

📞 SUPORTE:

🐛 Problemas? Verifique logs em logs/
📋 Documentação completa no README.md
"""
    
    print(help_text)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_help()
    else:
        quick_start()
