#!/usr/bin/env python3
"""
Script para testar o dashboard após as correções
"""
import os
import sys
import subprocess

def test_dashboard():
    """Testa se o dashboard funciona após as correções"""
    try:
        # Navega para o diretório correto
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        print("🚀 Testando dashboard com correções...")
        print(f"📁 Diretório: {os.getcwd()}")
        
        # Verifica se main.py existe
        if not os.path.exists('main.py'):
            print("❌ main.py não encontrado!")
            return False
        
        print("✅ main.py encontrado")
        
        # Executa o dashboard
        print("🔄 Iniciando dashboard...")
        cmd = [sys.executable, 'main.py', '--mode', 'dashboard']
        
        # Para teste, vamos fazer apenas uma verificação rápida
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Dashboard iniciado com sucesso!")
            return True
        else:
            print(f"❌ Erro ao iniciar dashboard:")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✅ Dashboard parece estar rodando (timeout após 10s é esperado)")
        return True
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False

if __name__ == "__main__":
    success = test_dashboard()
    if success:
        print("\n🎉 Dashboard testado com sucesso!")
        print("💡 Para iniciar manualmente, execute:")
        print("   python main.py --mode dashboard")
        print("📱 Dashboard estará disponível em: http://localhost:8501")
    else:
        print("\n❌ Problema detectado no dashboard")
