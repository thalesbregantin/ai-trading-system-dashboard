#!/usr/bin/env python3
"""
Início Direto do Dashboard com Dados Reais
"""

import subprocess
import sys
import os

def start_dashboard():
    """Inicia o dashboard diretamente"""
    try:
        print("🚀 INICIANDO AI TRADING DASHBOARD")
        print("=" * 50)
        
        # Verifica se está no diretório correto
        if not os.path.exists('dashboard/main_dashboard.py'):
            print("❌ Arquivo dashboard não encontrado!")
            print("💡 Execute este script no diretório ai_trading_system")
            return False
        
        print("✅ Arquivo dashboard encontrado")
        
        # Instala dependências se necessário
        try:
            import ccxt
            print("✅ CCXT já instalado")
        except ImportError:
            print("📦 Instalando CCXT...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'ccxt'], check=True)
        
        try:
            import streamlit
            print("✅ Streamlit já instalado")
        except ImportError:
            print("📦 Instalando Streamlit...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'streamlit'], check=True)
        
        # Inicia o dashboard
        print("\n🌐 Iniciando dashboard...")
        print("📱 Dashboard estará disponível em: http://localhost:8501")
        print("🔄 Para conectar dados reais, aguarde carregar...")
        
        # Executa streamlit
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 
            'dashboard/main_dashboard.py',
            '--server.port', '8501',
            '--server.headless', 'true'
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")

if __name__ == "__main__":
    start_dashboard()
