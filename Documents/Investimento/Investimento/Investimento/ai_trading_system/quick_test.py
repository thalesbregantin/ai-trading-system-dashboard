#!/usr/bin/env python3
"""
Teste rápido do sistema antes de operar com dinheiro real
"""

import sys
from pathlib import Path

# Adiciona o diretório do projeto
sys.path.append(str(Path(__file__).parent))

def test_system():
    """Testa componentes principais"""
    
    print("🧪 TESTE RÁPIDO DO SISTEMA")
    print("=" * 50)
    
    # 1. Teste de importações
    print("1️⃣ Testando importações...")
    try:
        from core.config import TradingConfig
        from core.ai_trader_dqn import AITrader
        from core.hybrid_trading_system import HybridTradingSystem
        from core.binance_ai_bot import BinanceAIBot
        print("✅ Todas as importações OK")
    except Exception as e:
        print(f"❌ Erro de importação: {e}")
        return False
    
    # 2. Teste de configuração
    print("\n2️⃣ Testando configuração...")
    try:
        config = TradingConfig()
        print(f"✅ Configuração carregada")
        print(f"   • Live Trading: {config.LIVE_TRADING}")
        print(f"   • Testnet Mode: {config.TESTNET_MODE}")
        print(f"   • API Key: {config.BINANCE_API_KEY[:15]}...")
    except Exception as e:
        print(f"❌ Erro de configuração: {e}")
        return False
    
    # 3. Teste de conexão Binance
    print("\n3️⃣ Testando conexão Binance...")
    try:
        bot = BinanceAIBot(config)
        if bot.connect():
            print("✅ Conexão com Binance OK")
            
            # Verifica saldo
            balance = bot.get_balance()
            if balance:
                print(f"💰 Saldo USDT: ${balance.get('USDT', 0):.2f}")
            
        else:
            print("❌ Falha na conexão com Binance")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    
    # 4. Teste de sistema híbrido
    print("\n4️⃣ Testando sistema híbrido...")
    try:
        hybrid = HybridTradingSystem()
        print("✅ Sistema híbrido inicializado")
    except Exception as e:
        print(f"❌ Erro no sistema híbrido: {e}")
        return False
    
    print("\n🎉 TODOS OS TESTES PASSARAM!")
    print("✅ Sistema pronto para operar!")
    return True

def show_next_steps():
    """Mostra próximos passos"""
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("=" * 50)
    print("1️⃣ Treinar AI (recomendado):")
    print("   python main.py --mode train --episodes 10")
    print()
    print("2️⃣ Ver dashboard:")
    print("   python main.py --mode dashboard")
    print()
    print("3️⃣ Iniciar trading (CUIDADO - DINHEIRO REAL!):")
    print("   python main.py --mode live --env prod")
    print()
    print("⚠️ IMPORTANTE:")
    print("   • Você tem $100 na conta")
    print("   • Sistema está em MODO LIVE")
    print("   • Monitore sempre via dashboard")
    print("   • Max 2% por trade = $2 por operação")

if __name__ == "__main__":
    success = test_system()
    
    if success:
        show_next_steps()
        
        print("\n🤔 O que você quer fazer agora?")
        print("A) Treinar AI primeiro (recomendado)")
        print("B) Ver dashboard")
        print("C) Iniciar trading direto")
        
        choice = input("\nEscolha (A/B/C): ").upper().strip()
        
        if choice == "A":
            print("🎓 Iniciando treinamento da AI...")
            import subprocess
            subprocess.run(["python", "main.py", "--mode", "train", "--episodes", "10"])
        elif choice == "B":
            print("📊 Abrindo dashboard...")
            import subprocess
            subprocess.run(["python", "main.py", "--mode", "dashboard"])
        elif choice == "C":
            confirm = input("⚠️ CONFIRMA trading com dinheiro real? Digite 'SIM': ")
            if confirm == "SIM":
                print("🚀 Iniciando trading ao vivo...")
                import subprocess
                subprocess.run(["python", "main.py", "--mode", "live", "--env", "prod"])
            else:
                print("❌ Trading cancelado")
    else:
        print("\n❌ Sistema não está pronto!")
        print("💡 Verifique as configurações e tente novamente")
