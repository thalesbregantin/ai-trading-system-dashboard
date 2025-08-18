#!/usr/bin/env python3
"""
Crypto Momentum Strategy Dashboard Launcher
===========================================

Este script inicializa o dashboard Streamlit para análise da estratégia de momentum crypto.

Para executar:
    python run_dashboard.py

Ou:
    streamlit run dashboard/main_dashboard.py

Requisitos:
    - Python 3.8+
    - Streamlit
    - Plotly
    - Pandas
    - NumPy

"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    required_packages = [
        'streamlit',
        'plotly',
        'pandas',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_data_files():
    """Verifica se os arquivos de dados existem"""
    data_path = Path(__file__).parent / 'data'
    
    required_files = [
        'equity_momentum_optimized.csv',
        'trades_momentum_optimized.csv',
        'momentum_correlation.csv',
        'trades_multi_asset.csv',
        'advanced_metrics_report.csv'
    ]
    
    missing_files = []
    
    for file in required_files:
        if not (data_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required data files:")
        for file in missing_files:
            print(f"   - data/{file}")
        print("\n💡 Make sure to run the strategy analysis first to generate data files.")
        return False
    
    return True

def main():
    """Função principal"""
    print("🚀 Crypto Momentum Strategy Dashboard Launcher")
    print("=" * 50)
    
    # Verifica dependências
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies installed")
    
    # Verifica arquivos de dados
    print("\n📊 Checking data files...")
    if not check_data_files():
        print("\n⚠️  Warning: Some data files are missing.")
        print("The dashboard may not display complete information.")
        
        response = input("\nDo you want to continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print("✅ All data files found")
    
    # Configurações do dashboard
    dashboard_path = Path(__file__).parent / 'dashboard' / 'main_dashboard.py'
    
    print(f"\n🎯 Starting dashboard...")
    print(f"📁 Dashboard path: {dashboard_path}")
    
    # Comando para executar o Streamlit
    cmd = [
        sys.executable, 
        "-m", 
        "streamlit", 
        "run", 
        str(dashboard_path),
        "--server.port=8501",
        "--server.address=localhost",
        "--browser.serverAddress=localhost",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false"
    ]
    
    try:
        print("\n🌐 Dashboard will open in your browser at: http://localhost:8501")
        print("🛑 Press Ctrl+C to stop the dashboard")
        print("=" * 50)
        
        # Executa o comando
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        print("\n💡 Try running manually with:")
        print(f"   streamlit run {dashboard_path}")

if __name__ == "__main__":
    main()
