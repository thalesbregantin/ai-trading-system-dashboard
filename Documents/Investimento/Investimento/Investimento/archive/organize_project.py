#!/usr/bin/env python3
"""
Organizador do Projeto AI Trading
Identifica e organiza arquivos essenciais vs. experimentais
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def organize_project():
    """Organiza o projeto mantendo apenas arquivos essenciais"""
    
    print("🧹 ORGANIZANDO PROJETO AI TRADING")
    print("=" * 50)
    
    # Arquivos ESSENCIAIS para o sistema funcionar
    essential_files = {
        # Core do sistema
        'ai_trader_dqn.py': 'core/',
        'hybrid_trading_system.py': 'core/',
        'binance_ai_bot.py': 'core/',
        'main.py': 'core/',
        'config.py': 'core/',
        
        # Dashboard
        'dashboard/main_dashboard.py': 'dashboard/',
        'dashboard/ai_trading_dashboard.py': 'dashboard/',
        'dashboard/.streamlit/': 'dashboard/.streamlit/',
        
        # Configuração e setup
        '.env': 'config/',
        'requirements_ai_trading.txt': 'config/',
        
        # Scripts utilitários
        'quick_setup.py': 'utils/',
        'test_binance_connection.py': 'utils/',
        'check_trading_permissions.py': 'utils/',
        'monitor_trading.py': 'utils/',
    }
    
    # Arquivos EXPERIMENTAIS/TESTE (mover para pasta archive)
    experimental_files = [
        'benchmark_vs_btc.py',
        'binance_testnet_executor.py',
        'crypto_sma_starter.py',
        'validation_out_of_sample.py',
        'binance_executor_*.py',
        'binance_r100_signals.py',
        'test_*.py',
        'simple_test.py',
        'quick_test.py',
        'run_*.py',
        'check_live.py',
        'status_live.py',
        'save_status.py',
    ]
    
    # Documentação (mover para docs)
    doc_files = [
        '*.md',
        '*.json',
        'reports/',
        'data/',
    ]
    
    print("📋 Arquivos identificados:")
    print(f"  ✅ Essenciais: {len(essential_files)}")
    print(f"  🧪 Experimentais: {len(experimental_files)}")
    print(f"  📄 Documentação: {len(doc_files)}")
    
    return essential_files, experimental_files, doc_files

def create_new_structure():
    """Cria nova estrutura de diretórios"""
    
    new_structure = {
        'ai_trading_system/': 'Sistema principal',
        'ai_trading_system/core/': 'Arquivos principais do sistema',
        'ai_trading_system/dashboard/': 'Interface web Streamlit',
        'ai_trading_system/config/': 'Configurações e setup',
        'ai_trading_system/utils/': 'Scripts utilitários',
        'ai_trading_system/logs/': 'Logs do sistema',
        'archive/': 'Arquivos experimentais',
        'docs/': 'Documentação e relatórios',
    }
    
    print("\n🏗️ NOVA ESTRUTURA:")
    for folder, description in new_structure.items():
        print(f"  📁 {folder:<30} - {description}")
    
    return new_structure

def show_final_structure():
    """Mostra estrutura final organizada"""
    
    final_structure = """
📁 ai_trading_system/                 # Sistema Principal
├── 📁 core/                         # Núcleo do Sistema
│   ├── 🤖 ai_trader_dqn.py          # Deep Q-Learning AI
│   ├── 🔄 hybrid_trading_system.py  # Sistema Híbrido AI+Momentum
│   ├── 🔗 binance_ai_bot.py         # Bot de Trading Binance
│   ├── 🚀 main.py                   # Orquestrador Principal
│   └── ⚙️ config.py                 # Configurações
│
├── 📁 dashboard/                    # Interface Web
│   ├── 📊 main_dashboard.py         # Dashboard Principal
│   ├── 🎯 ai_trading_dashboard.py   # Dashboard AI Específico
│   └── 📁 .streamlit/               # Configurações Streamlit
│
├── 📁 config/                       # Configuração e Setup
│   ├── 🔐 .env                      # Variáveis de Ambiente
│   └── 📦 requirements.txt          # Dependências Python
│
├── 📁 utils/                        # Utilitários
│   ├── 🔧 quick_setup.py            # Setup Rápido
│   ├── 🔍 test_binance_connection.py # Teste API
│   ├── 🛡️ check_trading_permissions.py # Verificar Permissões
│   └── 📊 monitor_trading.py        # Monitor em Tempo Real
│
└── 📁 logs/                         # Logs do Sistema
    ├── 📝 trading_log_YYYYMMDD.log  # Logs de Trading
    └── 📈 ai_training.log           # Logs de Treinamento AI

📁 archive/                          # Arquivos Experimentais
├── 🧪 test_files/                   # Scripts de teste
├── 🔬 experimental/                 # Experimentos
└── 📊 old_analysis/                 # Análises antigas

📁 docs/                             # Documentação
├── 📋 user_guides/                  # Guias do usuário
├── 📊 reports/                      # Relatórios
└── 📝 technical_docs/               # Documentação técnica
"""
    
    print("\n🎯 ESTRUTURA FINAL ORGANIZADA:")
    print(final_structure)

if __name__ == "__main__":
    print("🗂️ ANÁLISE DE ORGANIZAÇÃO DO PROJETO")
    print("=" * 60)
    
    # Analisa arquivos atuais
    essential, experimental, docs = organize_project()
    
    # Mostra nova estrutura
    new_structure = create_new_structure()
    
    # Mostra estrutura final
    show_final_structure()
    
    print("\n💡 PRÓXIMAS AÇÕES RECOMENDADAS:")
    print("1️⃣ Criar diretório 'ai_trading_system'")
    print("2️⃣ Mover arquivos essenciais para nova estrutura")
    print("3️⃣ Arquivar arquivos experimentais")
    print("4️⃣ Organizar documentação")
    print("5️⃣ Atualizar imports nos arquivos")
    print("6️⃣ Testar sistema na nova estrutura")
    
    choice = input("\n❓ Executar reorganização? (s/n): ").lower().strip()
    if choice in ['s', 'sim', 'y', 'yes']:
        print("🚀 Iniciando reorganização...")
        # Aqui implementaríamos a reorganização real
        print("⚠️ Reorganização automática não implementada por segurança.")
        print("💡 Execute manualmente seguindo a estrutura acima.")
    else:
        print("👋 Reorganização cancelada.")
