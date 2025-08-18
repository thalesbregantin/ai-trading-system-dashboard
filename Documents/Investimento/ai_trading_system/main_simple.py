#!/usr/bin/env python3
"""
AI Trading System - Versão Simplificada (sem TensorFlow)
"""

import sys
import os
import logging
from datetime import datetime
import argparse

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import get_config
from core.ai_trader_simple import SimpleAITrader
from core.hybrid_trading_system import HybridTradingSystem

def setup_logging():
    """Configura logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/trading_simple.log'),
            logging.StreamHandler()
        ]
    )

def run_test_mode(config):
    """Executa modo de teste básico"""
    print("🧪 MODO TESTE - VERSÃO SIMPLIFICADA")
    print("-" * 50)
    
    try:
        # Testar AI Trader simplificado
        ai_trader = SimpleAITrader(config)
        print("✅ AI Trader simplificado criado")
        
        # Testar sinais para BTC
        signal = ai_trader.get_current_signal("BTC-USD")
        print(f"✅ Sinal BTC-USD: {signal}")
        
        # Testar sistema híbrido
        hybrid_system = HybridTradingSystem(config)
        print("✅ Sistema híbrido criado")
        
        print("✅ Sistema pronto para operar (versão simplificada)")
        print(f"📊 Modo: {'TESTNET' if config.TESTNET_MODE else 'LIVE'}")
        print(f"🔑 API configurada: {len(config.BINANCE_API_KEY) > 10}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def run_dashboard_mode(config):
    """Executa modo dashboard"""
    print("📊 INICIANDO DASHBOARD")
    print("-" * 30)
    
    try:
        import streamlit as st
        import subprocess
        
        # Iniciar Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            "dashboard/main_dashboard.py",
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ]
        
        print("🚀 Iniciando Streamlit...")
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='AI Trading System - Versão Simplificada')
    parser.add_argument('--mode', choices=['test', 'dashboard'], default='test',
                       help='Modo de execução')
    parser.add_argument('--config', choices=['dev', 'test', 'prod'], default='test',
                       help='Configuração a usar')
    
    args = parser.parse_args()
    
    # Setup
    setup_logging()
    config = get_config(args.config)
    
    print("🤖 AI TRADING SYSTEM - VERSÃO SIMPLIFICADA")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⚙️ Configuração: {args.config}")
    print(f"🎯 Modo: {args.mode}")
    print("=" * 50)
    
    if args.mode == 'test':
        success = run_test_mode(config)
        if success:
            print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        else:
            print("\n❌ TESTE FALHOU!")
            sys.exit(1)
    
    elif args.mode == 'dashboard':
        run_dashboard_mode(config)

if __name__ == "__main__":
    main()
