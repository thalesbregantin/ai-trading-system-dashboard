#!/usr/bin/env python3
"""
Monitor de Trading ao Vivo
Monitora o status do sistema de trading em tempo real
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Adiciona o diretório do projeto
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

try:
    from config import TradingConfig
    
    def show_live_status():
        """Mostra status atual do sistema"""
        print("\n🚀 STATUS DO TRADING AO VIVO")
        print("=" * 50)
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 TESTNET_MODE: {TradingConfig.TESTNET_MODE}")
        print(f"💰 LIVE_TRADING: {TradingConfig.LIVE_TRADING}")
        print(f"🌐 URL Binance: {TradingConfig.get_binance_url()}")
        print(f"📊 Pares: {', '.join(TradingConfig.TRADING_PAIRS)}")
        print(f"💵 Capital: ${TradingConfig.INITIAL_CAPITAL:,.2f}")
        print(f"🎯 Max Position: {TradingConfig.MAX_POSITION_SIZE:.1%}")
        
        # Status do modo
        if not TradingConfig.TESTNET_MODE and TradingConfig.LIVE_TRADING:
            print("\n🔥 SISTEMA EM MODO LIVE!")
            print("⚠️ TRADING COM DINHEIRO REAL!")
            print("💡 URL: https://api.binance.com")
        elif TradingConfig.TESTNET_MODE and TradingConfig.LIVE_TRADING:
            print("\n🧪 SISTEMA EM TESTNET")
            print("💡 Trading simulado (sem dinheiro real)")
            print("💡 URL: https://testnet.binance.vision")
        else:
            print("\n❌ SISTEMA DESABILITADO")
        
        # Verifica se há logs recentes
        log_file = f"trading_log_{datetime.now().strftime('%Y%m%d')}.log"
        if os.path.exists(log_file):
            file_size = os.path.getsize(log_file)
            print(f"\n📝 Log: {log_file} ({file_size} bytes)")
            
            # Mostra últimas linhas do log
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    if lines:
                        print("📋 Últimas atividades:")
                        for line in lines[-3:]:
                            print(f"   {line.strip()}")
            except Exception as e:
                print(f"   ⚠️ Erro ao ler log: {e}")
        else:
            print(f"\n📝 Log: {log_file} (não encontrado)")
        
        print("=" * 50)
    
    # Mostra status inicial
    show_live_status()
    
    # Opção de monitoramento contínuo
    try:
        choice = input("\n💡 Monitorar em tempo real? (s/n): ").lower().strip()
        if choice in ['s', 'sim', 'y', 'yes']:
            print("🔄 Monitoramento ativo (Ctrl+C para parar)...")
            while True:
                time.sleep(10)  # Atualiza a cada 10 segundos
                os.system('cls' if os.name == 'nt' else 'clear')  # Limpa tela
                show_live_status()
    except KeyboardInterrupt:
        print("\n👋 Monitoramento interrompido!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

except ImportError as e:
    print(f"❌ Erro ao importar configuração: {e}")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
