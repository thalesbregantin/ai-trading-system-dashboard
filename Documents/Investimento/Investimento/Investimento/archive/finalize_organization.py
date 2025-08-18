#!/usr/bin/env python3
"""
Script de Organização Final do Projeto
Move arquivos essenciais para nova estrutura
"""

import os
import shutil
from pathlib import Path

def organize_files():
    """Organiza arquivos na nova estrutura"""
    
    print("🗂️ ORGANIZANDO ARQUIVOS DO PROJETO")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    ai_system_dir = base_dir / "ai_trading_system"
    
    # Arquivos para mover/copiar
    file_moves = {
        # Core files
        "ai_trader_dqn.py": ai_system_dir / "core" / "ai_trader_dqn.py",
        "hybrid_trading_system.py": ai_system_dir / "core" / "hybrid_trading_system.py", 
        "binance_ai_bot.py": ai_system_dir / "core" / "binance_ai_bot.py",
        
        # Configuração
        ".env": ai_system_dir / ".env",
        
        # Dashboard
        "dashboard/main_dashboard.py": ai_system_dir / "dashboard" / "main_dashboard.py",
        "dashboard/ai_trading_dashboard.py": ai_system_dir / "dashboard" / "ai_trading_dashboard.py",
        "dashboard/.streamlit": ai_system_dir / "dashboard" / ".streamlit",
        
        # Utils
        "quick_setup.py": ai_system_dir / "utils" / "setup.py",
        "monitor_trading.py": ai_system_dir / "utils" / "monitor.py",
        "test_binance_connection.py": ai_system_dir / "utils" / "test_connection.py",
        "check_trading_permissions.py": ai_system_dir / "utils" / "check_permissions.py",
    }
    
    print("📋 Arquivos a serem organizados:")
    moved_count = 0
    
    for source, destination in file_moves.items():
        source_path = base_dir / source
        
        if source_path.exists():
            # Cria diretório de destino se não existir
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                if source_path.is_dir():
                    if destination.exists():
                        shutil.rmtree(destination)
                    shutil.copytree(source_path, destination)
                else:
                    shutil.copy2(source_path, destination)
                
                print(f"✅ {source} -> {destination.relative_to(base_dir)}")
                moved_count += 1
                
            except Exception as e:
                print(f"❌ Erro movendo {source}: {e}")
        else:
            print(f"⚠️ Arquivo não encontrado: {source}")
    
    print(f"\n📊 Total de arquivos organizados: {moved_count}")
    
    # Criar diretórios adicionais
    additional_dirs = [
        ai_system_dir / "logs",
        ai_system_dir / "data", 
        ai_system_dir / "models",
        base_dir / "archive" / "tests",
        base_dir / "archive" / "experimental",
        base_dir / "docs" / "guides",
        base_dir / "docs" / "reports"
    ]
    
    print("\n📁 Criando diretórios adicionais:")
    for dir_path in additional_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ {dir_path.relative_to(base_dir)}")

def create_env_example():
    """Cria arquivo .env.example"""
    
    env_example_content = """# AI Trading System - Environment Variables
# Copie este arquivo para .env e configure suas credenciais

# Binance API Credentials
BINANCE_API_KEY=sua_api_key_aqui
BINANCE_API_SECRET=sua_api_secret_aqui

# Trading Configuration
INITIAL_CAPITAL=1000
MAX_POSITION_SIZE=0.02
STOP_LOSS_PCT=0.05

# AI Configuration  
AI_EPISODES=20
AI_WEIGHT=0.6

# System Configuration
LOG_LEVEL=INFO
DASHBOARD_PORT=8501

# Mode Configuration
TESTNET_MODE=true
LIVE_TRADING=false
"""
    
    base_dir = Path(__file__).parent
    env_example_path = base_dir / "ai_trading_system" / ".env.example"
    
    with open(env_example_path, 'w') as f:
        f.write(env_example_content)
    
    print(f"✅ Criado: {env_example_path.relative_to(base_dir)}")

def create_gitignore():
    """Cria arquivo .gitignore"""
    
    gitignore_content = """# AI Trading System - Git Ignore

# Environment Variables
.env
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# Jupyter Notebook
.ipynb_checkpoints

# Trading Data
logs/
*.log
data/
models/
*.h5
*.pkl

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.bak
*.swp
*~

# Trading specific
trading_*.json
backtest_results/
ai_models/
"""
    
    base_dir = Path(__file__).parent
    gitignore_path = base_dir / "ai_trading_system" / ".gitignore"
    
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content)
    
    print(f"✅ Criado: {gitignore_path.relative_to(base_dir)}")

def show_final_structure():
    """Mostra estrutura final"""
    
    print("\n🎯 ESTRUTURA FINAL ORGANIZADA:")
    print("=" * 50)
    
    structure = """
📁 ai_trading_system/                 # ✅ Sistema Principal
├── 📁 core/                         # ✅ Núcleo do Sistema  
│   ├── 🤖 ai_trader_dqn.py          # ✅ Deep Q-Learning
│   ├── 🔄 hybrid_trading_system.py  # ✅ Sistema Híbrido
│   ├── 🔗 binance_ai_bot.py         # ✅ Bot Binance
│   └── ⚙️ config.py                 # ✅ Configurações
│
├── 📁 dashboard/                    # ✅ Interface Web
│   ├── 📊 main_dashboard.py         # ✅ Dashboard Principal
│   ├── 🎯 ai_trading_dashboard.py   # ✅ Dashboard AI
│   └── 📁 .streamlit/               # ✅ Config Streamlit
│
├── 📁 utils/                        # ✅ Utilitários
│   ├── 🔧 setup.py                  # ✅ Setup Sistema
│   ├── 📊 monitor.py                # ✅ Monitor Tempo Real
│   ├── 🔍 test_connection.py        # ✅ Teste API
│   └── 🛡️ check_permissions.py      # ✅ Check Permissões
│
├── 📁 logs/                         # ✅ Logs Sistema
├── 📁 data/                         # ✅ Dados Trading
├── 📁 models/                       # ✅ Modelos AI
│
├── 🚀 main.py                       # ✅ Arquivo Principal
├── 📦 requirements.txt              # ✅ Dependências
├── 📋 README.md                     # ✅ Documentação
├── 🔐 .env.example                  # ✅ Template Env
├── 🚫 .gitignore                    # ✅ Git Ignore
└── ⚙️ .env                          # ✅ Configurações

📁 archive/                          # ✅ Arquivos Antigos
├── 📁 tests/                        # ✅ Scripts de teste
├── 📁 experimental/                 # ✅ Código experimental
└── 📁 old_versions/                 # ✅ Versões antigas

📁 docs/                             # ✅ Documentação
├── 📁 guides/                       # ✅ Guias usuário
└── 📁 reports/                      # ✅ Relatórios
"""
    
    print(structure)

def main():
    """Função principal"""
    
    print("🧹 SCRIPT DE ORGANIZAÇÃO FINAL")
    print("=" * 60)
    
    try:
        # Organiza arquivos
        organize_files()
        
        # Cria arquivos de configuração
        print("\n🔧 Criando arquivos de configuração:")
        create_env_example()
        create_gitignore()
        
        # Mostra estrutura final
        show_final_structure()
        
        print("\n✅ ORGANIZAÇÃO CONCLUÍDA!")
        print("=" * 60)
        print("🎯 Próximos passos:")
        print("1️⃣ cd ai_trading_system")
        print("2️⃣ cp .env.example .env")
        print("3️⃣ Configure suas API keys no .env")
        print("4️⃣ pip install -r requirements.txt")
        print("5️⃣ python main.py --mode test")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erro durante organização: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
