#!/usr/bin/env python3
"""
Script para iniciar o Dashboard com dados reais da Binance
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Instalar dependências do servidor API"""
    print("📦 Instalando dependências do servidor API...")
    
    requirements_file = Path(__file__).parent / "requirements-api.txt"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def check_env_file():
    """Verificar se o arquivo .env existe"""
    env_file = Path(__file__).parent.parent / ".env"
    
    if not env_file.exists():
        print("⚠️  Arquivo .env não encontrado!")
        print("📝 Criando arquivo .env com template...")
        
        template = """# Binance API Configuration
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here

# Trading Configuration
INITIAL_CAPITAL=10000
RISK_PERCENTAGE=2
MAX_POSITION_SIZE=10

# AI Model Configuration
MODEL_PATH=models/
LOG_PATH=logs/
"""
        
        with open(env_file, 'w') as f:
            f.write(template)
        
        print("📄 Arquivo .env criado!")
        print("🔑 Configure suas chaves da Binance no arquivo .env")
        return False
    
    return True

def start_api_server():
    """Iniciar servidor API"""
    print("🚀 Iniciando servidor API...")
    
    api_server = Path(__file__).parent / "api_server.py"
    
    try:
        subprocess.Popen([
            sys.executable, str(api_server)
        ])
        print("✅ Servidor API iniciado em http://localhost:5000")
        return True
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor API: {e}")
        return False

def main():
    """Função principal"""
    print("🎯 AI Trading Dashboard - Setup")
    print("=" * 50)
    
    # Verificar arquivo .env
    if not check_env_file():
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Configure suas chaves da Binance no arquivo .env")
        print("2. Execute este script novamente")
        return
    
    # Instalar dependências
    if not install_requirements():
        print("❌ Falha na instalação das dependências")
        return
    
    # Iniciar servidor API
    if not start_api_server():
        print("❌ Falha ao iniciar servidor API")
        return
    
    print("\n🎉 SETUP CONCLUÍDO!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Abra o VS Code na pasta do projeto")
    print("2. Navegue até dashboard/index.html")
    print("3. Use 'Go Live' para abrir o dashboard")
    print("4. O dashboard se conectará automaticamente com a Binance")
    
    print("\n🔗 URLs:")
    print("- Dashboard: http://localhost:5500/dashboard/index.html")
    print("- API Server: http://localhost:5000")
    
    print("\n⚠️  IMPORTANTE:")
    print("- Certifique-se de que suas chaves da Binance estão configuradas no .env")
    print("- O servidor API deve estar rodando para o dashboard funcionar")
    print("- Use Ctrl+C para parar o servidor quando necessário")

if __name__ == "__main__":
    main()
