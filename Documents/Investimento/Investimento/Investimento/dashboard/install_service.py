#!/usr/bin/env python3
"""
Script para instalar o servidor API como serviço do Windows
Execute como administrador: python install_service.py
"""

import os
import sys
import subprocess
from pathlib import Path

def install_windows_service():
    """Instala o servidor API como serviço do Windows"""
    
    # Verificar se está rodando como administrador
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    
    if not is_admin:
        print("❌ Este script precisa ser executado como ADMINISTRADOR")
        print("💡 Clique com botão direito no PowerShell e selecione 'Executar como administrador'")
        return False
    
    # Caminhos
    current_dir = Path(__file__).parent
    server_script = current_dir / "simple_api_server.py"
    python_exe = sys.executable
    
    # Verificar se o arquivo existe
    if not server_script.exists():
        print(f"❌ Arquivo não encontrado: {server_script}")
        return False
    
    # Comando para instalar o serviço
    service_name = "AITradingAPI"
    display_name = "AI Trading API Server"
    description = "Servidor API para o sistema de trading com IA"
    
    install_cmd = [
        "sc", "create", service_name,
        f"binPath= \"{python_exe}\" \"{server_script}\"",
        f"DisplayName= \"{display_name}\"",
        "start= auto",
        f"obj= LocalSystem"
    ]
    
    try:
        print("🔧 Instalando serviço do Windows...")
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Serviço instalado com sucesso!")
            
            # Configurar descrição
            subprocess.run(["sc", "description", service_name, description])
            
            # Iniciar o serviço
            print("🚀 Iniciando serviço...")
            start_result = subprocess.run(["sc", "start", service_name], capture_output=True, text=True)
            
            if start_result.returncode == 0:
                print("✅ Serviço iniciado com sucesso!")
                print(f"🌐 API disponível em: http://localhost:5000")
                print(f"📊 Dashboard: http://localhost:5500 (Live Server)")
                print("\n📋 Comandos úteis:")
                print(f"   Parar: sc stop {service_name}")
                print(f"   Iniciar: sc start {service_name}")
                print(f"   Status: sc query {service_name}")
                print(f"   Remover: sc delete {service_name}")
                return True
            else:
                print(f"⚠️ Serviço instalado mas não iniciou: {start_result.stderr}")
                return False
        else:
            print(f"❌ Erro ao instalar serviço: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def create_batch_file():
    """Cria arquivo .bat para iniciar o servidor facilmente"""
    
    current_dir = Path(__file__).parent
    batch_file = current_dir / "start_api_server.bat"
    python_exe = sys.executable
    server_script = current_dir / "simple_api_server.py"
    
    batch_content = f"""@echo off
echo 🚀 Iniciando AI Trading API Server...
echo 📍 Diretório: {current_dir}
echo 🌐 URL: http://localhost:5000
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

cd /d "{current_dir}"
"{python_exe}" "{server_script}"

pause
"""
    
    try:
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        print(f"✅ Arquivo batch criado: {batch_file}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar arquivo batch: {e}")
        return False

def main():
    print("🤖 AI Trading API Server - Instalador")
    print("=" * 50)
    
    # Criar arquivo batch
    create_batch_file()
    
    # Tentar instalar como serviço
    if install_windows_service():
        print("\n🎉 INSTALAÇÃO CONCLUÍDA!")
        print("O servidor agora iniciará automaticamente com o Windows")
    else:
        print("\n⚠️ INSTALAÇÃO COMO SERVIÇO FALHOU")
        print("Você pode usar o arquivo 'start_api_server.bat' para iniciar manualmente")

if __name__ == "__main__":
    main()
