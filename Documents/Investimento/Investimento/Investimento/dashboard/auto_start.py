#!/usr/bin/env python3
"""
Script para configurar inicialização automática do servidor API
"""

import os
import sys
import winreg
from pathlib import Path

def add_to_startup():
    """Adiciona o servidor à inicialização do Windows"""
    
    try:
        # Caminhos
        current_dir = Path(__file__).parent
        python_exe = sys.executable
        server_script = current_dir / "simple_api_server.py"
        
        # Criar comando
        command = f'"{python_exe}" "{server_script}"'
        
        # Abrir registro do Windows
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        # Adicionar à inicialização
        winreg.SetValueEx(key, "AITradingAPI", 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        
        print("✅ Servidor adicionado à inicialização do Windows")
        print(f"🔧 Comando: {command}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar inicialização: {e}")
        return False

def remove_from_startup():
    """Remove o servidor da inicialização do Windows"""
    
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.DeleteValue(key, "AITradingAPI")
        winreg.CloseKey(key)
        
        print("✅ Servidor removido da inicialização do Windows")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao remover da inicialização: {e}")
        return False

def main():
    print("🤖 AI Trading API - Configurador de Inicialização")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "remove":
        remove_from_startup()
    else:
        add_to_startup()
        print("\n💡 Para remover da inicialização: python auto_start.py remove")

if __name__ == "__main__":
    main()
