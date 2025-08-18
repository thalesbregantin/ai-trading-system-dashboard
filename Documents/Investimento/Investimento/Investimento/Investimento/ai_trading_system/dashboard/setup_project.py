#!/usr/bin/env python3
"""
Script para configurar o projeto AI Trading System
"""

import os
import json
import subprocess
import sys

def check_requirements():
    """Verificar se os requisitos estão instalados"""
    print("🔍 Verificando dependências...")
    
    required_packages = [
        'flask', 'flask-cors', 'ccxt', 'pandas', 
        'numpy', 'firebase-admin', 'gunicorn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Faltando")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Instalando pacotes faltantes...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Dependências instaladas!")
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar dependências")
            return False
    
    return True

def check_firebase_config():
    """Verificar configuração do Firebase"""
    print("\n🔥 Verificando Firebase...")
    
    if not os.path.exists('firebase-service-account.json'):
        print("❌ Arquivo firebase-service-account.json não encontrado!")
        print("\n📋 Para obter o arquivo:")
        print("1. Acesse: https://console.firebase.google.com/")
        print("2. Vá em Configurações do Projeto > Contas de Serviço")
        print("3. Clique em 'Gerar nova chave privada'")
        print("4. Baixe e renomeie para 'firebase-service-account.json'")
        print("5. Coloque na pasta dashboard/")
        return False
    
    try:
        with open('firebase-service-account.json', 'r') as f:
            config = json.load(f)
        
        project_id = config.get('project_id', 'N/A')
        print(f"✅ Firebase configurado: {project_id}")
        
        # Testar conexão
        from firebase_config import test_firebase
        if test_firebase():
            print("✅ Conexão Firebase OK!")
            return True
        else:
            print("❌ Erro na conexão Firebase")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar Firebase: {e}")
        return False

def check_binance_config():
    """Verificar configuração da Binance"""
    print("\n💰 Verificando Binance...")
    
    # Verificar se as chaves estão no código (temporário)
    try:
        with open('cloud_api_server.py', 'r') as f:
            content = f.read()
            
        if 'Gm5VZwg3DzYD7FQXiocUsnhU7CYh5omlb8phvcxuEkec8YgVHHk0AhhyCxMRr80b' in content:
            print("✅ Chaves da Binance configuradas (hardcoded)")
            print("⚠️  ATENÇÃO: Para produção, use variáveis de ambiente!")
            return True
        else:
            print("❌ Chaves da Binance não encontradas")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar Binance: {e}")
        return False

def create_env_example():
    """Criar arquivo .env.example"""
    print("\n📝 Criando arquivo .env.example...")
    
    env_content = """# 🔐 CONFIGURAÇÃO DE AMBIENTE
# Copie este arquivo para .env e preencha com suas chaves

# Binance API Keys
BINANCE_API_KEY=sua_binance_api_key_aqui
BINANCE_SECRET_KEY=sua_binance_secret_key_aqui

# Configurações do Sistema
FLASK_ENV=development
DEBUG=True
PORT=5000

# ⚠️ IMPORTANTE:
# 1. NUNCA commite o arquivo .env no GitHub
# 2. Use variáveis de ambiente em produção
# 3. Mantenha suas chaves seguras
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env.example criado!")

def test_server():
    """Testar servidor local"""
    print("\n🧪 Testando servidor local...")
    
    try:
        # Teste rápido do servidor
        from cloud_api_server import app
        print("✅ Servidor Flask carregado!")
        
        # Testar endpoint de status
        with app.test_client() as client:
            response = client.get('/api/status')
            if response.status_code == 200:
                print("✅ Endpoint /api/status funcionando!")
                return True
            else:
                print(f"❌ Erro no endpoint: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao testar servidor: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Setup AI Trading System")
    print("=" * 40)
    
    # Verificar dependências
    if not check_requirements():
        print("\n❌ Falha na verificação de dependências")
        return False
    
    # Verificar Firebase
    if not check_firebase_config():
        print("\n❌ Falha na configuração do Firebase")
        return False
    
    # Verificar Binance
    if not check_binance_config():
        print("\n❌ Falha na configuração da Binance")
        return False
    
    # Criar arquivo .env.example
    create_env_example()
    
    # Testar servidor
    if not test_server():
        print("\n❌ Falha no teste do servidor")
        return False
    
    print("\n🎉 Setup concluído com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Configure suas chaves da Binance")
    print("2. Teste o servidor: python cloud_api_server.py")
    print("3. Abra o dashboard: index.html")
    print("4. Deploy no Railway/Vercel")
    print("\n📖 Consulte o README.md para mais detalhes")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup falhou! Verifique os erros acima.")
        sys.exit(1)
