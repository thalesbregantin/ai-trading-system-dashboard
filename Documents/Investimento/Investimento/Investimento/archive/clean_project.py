#!/usr/bin/env python3
"""
Script de Limpeza Final do Projeto
Remove arquivos antigos e mantém apenas o sistema organizado
"""

import os
import shutil
from pathlib import Path

def clean_project():
    """Limpa arquivos antigos e mantém apenas o sistema organizado"""
    
    print("🧹 LIMPEZA FINAL DO PROJETO")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    
    # Arquivos/pastas para MANTER (não deletar)
    keep_items = {
        'ai_trading_system',     # Sistema principal organizado
        '.venv',                 # Ambiente virtual
        'clean_project.py',      # Este script
        '__pycache__',          # Cache Python (será removido separadamente)
        '.git',                 # Git (se existir)
        '.gitignore',           # Git ignore
    }
    
    # Arquivos/pastas para MOVER para archive (não deletar completamente)
    archive_items = [
        # Scripts de teste antigos
        'test_*.py',
        'quick_test.py',
        'simple_test.py',
        'run_*.py',
        
        # Executores antigos
        'binance_executor_*.py',
        'binance_testnet_executor.py',
        'binance_r100_signals.py',
        'crypto_sma_starter.py',
        'benchmark_vs_btc.py',
        'validation_out_of_sample.py',
        
        # Scripts utilitários antigos  
        'check_live.py',
        'status_live.py',
        'save_status.py',
        'monitor_trading.py',
        'quick_setup.py',
        'organize_project.py',
        'finalize_organization.py',
        'copy_files.py',
        
        # Análises antigas
        'analysis_*.json',
        'trading_config.json',
        
        # Logs antigos
        '*.log',
    ]
    
    # Documentação para mover para docs
    doc_items = [
        '*.md',
        'reports/',
        'data/',
    ]
    
    # Pastas antigas para remover
    old_folders = [
        'config/',
        'src/',
        '__pycache__/',
    ]
    
    # Arquivos duplicados (já estão no ai_trading_system)
    duplicate_files = [
        'ai_trader_dqn.py',
        'hybrid_trading_system.py', 
        'binance_ai_bot.py',
        'main.py',
        'config.py',
        'requirements_ai_trading.txt',
        'dashboard/',
        '.env',  # Mantém no ai_trading_system
    ]
    
    print("📋 Analisando arquivos para limpeza...")
    
    # Criar pasta archive se não existir
    archive_dir = base_dir / 'archive'
    archive_dir.mkdir(exist_ok=True)
    
    # Criar pasta docs se não existir
    docs_dir = base_dir / 'docs'
    docs_dir.mkdir(exist_ok=True)
    
    # Move arquivos experimentais para archive
    moved_to_archive = 0
    for item_pattern in archive_items:
        if '*' in item_pattern:
            # Padrão com wildcard
            import glob
            matches = glob.glob(str(base_dir / item_pattern))
            for match in matches:
                item_path = Path(match)
                if item_path.exists() and item_path.name not in keep_items:
                    try:
                        dest_path = archive_dir / item_path.name
                        if item_path.is_dir():
                            if dest_path.exists():
                                shutil.rmtree(dest_path)
                            shutil.move(str(item_path), str(dest_path))
                        else:
                            shutil.move(str(item_path), str(dest_path))
                        print(f"📦 {item_path.name} -> archive/")
                        moved_to_archive += 1
                    except Exception as e:
                        print(f"❌ Erro movendo {item_path.name}: {e}")
        else:
            # Item específico
            item_path = base_dir / item_pattern
            if item_path.exists() and item_path.name not in keep_items:
                try:
                    dest_path = archive_dir / item_path.name
                    if item_path.is_dir():
                        if dest_path.exists():
                            shutil.rmtree(dest_path)
                        shutil.move(str(item_path), str(dest_path))
                    else:
                        shutil.move(str(item_path), str(dest_path))
                    print(f"📦 {item_path.name} -> archive/")
                    moved_to_archive += 1
                except Exception as e:
                    print(f"❌ Erro movendo {item_path.name}: {e}")
    
    # Move documentação para docs
    moved_to_docs = 0
    for item_pattern in doc_items:
        if '*' in item_pattern:
            import glob
            matches = glob.glob(str(base_dir / item_pattern))
            for match in matches:
                item_path = Path(match)
                if item_path.exists() and item_path.name not in keep_items:
                    try:
                        dest_path = docs_dir / item_path.name
                        if item_path.is_dir():
                            if dest_path.exists():
                                shutil.rmtree(dest_path)
                            shutil.move(str(item_path), str(dest_path))
                        else:
                            shutil.move(str(item_path), str(dest_path))
                        print(f"📄 {item_path.name} -> docs/")
                        moved_to_docs += 1
                    except Exception as e:
                        print(f"❌ Erro movendo {item_path.name}: {e}")
    
    # Remove arquivos duplicados
    removed_duplicates = 0
    for item in duplicate_files:
        item_path = base_dir / item
        if item_path.exists():
            try:
                if item_path.is_dir():
                    shutil.rmtree(item_path)
                else:
                    item_path.unlink()
                print(f"🗑️ Removido: {item} (duplicado)")
                removed_duplicates += 1
            except Exception as e:
                print(f"❌ Erro removendo {item}: {e}")
    
    # Remove pastas antigas
    removed_folders = 0
    for folder in old_folders:
        folder_path = base_dir / folder
        if folder_path.exists():
            try:
                shutil.rmtree(folder_path)
                print(f"🗂️ Pasta removida: {folder}")
                removed_folders += 1
            except Exception as e:
                print(f"❌ Erro removendo pasta {folder}: {e}")
    
    print(f"\n📊 RESUMO DA LIMPEZA:")
    print(f"  📦 Arquivos movidos para archive: {moved_to_archive}")
    print(f"  📄 Arquivos movidos para docs: {moved_to_docs}")
    print(f"  🗑️ Duplicados removidos: {removed_duplicates}")
    print(f"  🗂️ Pastas antigas removidas: {removed_folders}")
    
    return True

def show_final_structure():
    """Mostra estrutura final limpa"""
    
    print("\n🎯 ESTRUTURA FINAL LIMPA:")
    print("=" * 50)
    
    structure = """
📁 Investimento/                      # Diretório Principal
├── 📁 ai_trading_system/             # ✅ SISTEMA PRINCIPAL (ÚNICO)
│   ├── 📁 core/                     # Núcleo do sistema
│   │   ├── 🤖 ai_trader_dqn.py      # Deep Q-Learning
│   │   ├── 🔄 hybrid_trading_system.py # Sistema híbrido
│   │   ├── 🔗 binance_ai_bot.py     # Bot Binance
│   │   └── ⚙️ config.py             # Configurações
│   │
│   ├── 📁 dashboard/                # Interface web
│   ├── 📁 utils/                    # Utilitários
│   ├── 📁 logs/                     # Logs sistema
│   │
│   ├── 🚀 main.py                   # Orquestrador
│   ├── 🎯 start.py                  # Início rápido
│   ├── 📦 requirements.txt          # Dependências
│   ├── 📋 README.md                 # Documentação
│   └── 🔐 .env                      # Configurações
│
├── 📁 archive/                      # Arquivos antigos preservados
│   ├── 🧪 test_*.py                 # Scripts de teste
│   ├── 🔬 experimental_*.py         # Código experimental
│   └── 📊 old_analysis/             # Análises antigas
│
├── 📁 docs/                         # Documentação
│   ├── 📋 *.md                      # Guias e READMEs
│   └── 📊 reports/                  # Relatórios
│
└── 📁 .venv/                        # Ambiente virtual Python
"""
    
    print(structure)

def main():
    """Função principal"""
    
    try:
        # Executa limpeza
        success = clean_project()
        
        if success:
            # Mostra estrutura final
            show_final_structure()
            
            print("\n✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
            print("=" * 60)
            print("🎯 AGORA SEU PROJETO ESTÁ LIMPO E ORGANIZADO!")
            print()
            print("📍 Para usar o sistema:")
            print("   cd ai_trading_system")
            print("   python start.py")
            print()
            print("📦 Arquivos antigos preservados em archive/")
            print("📄 Documentação organizada em docs/")
            print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Confirma antes de executar
    print("🧹 LIMPEZA FINAL DO PROJETO")
    print("=" * 50)
    print("⚠️ Este script irá:")
    print("  • Mover arquivos antigos para archive/")
    print("  • Mover documentação para docs/")
    print("  • Remover arquivos duplicados")
    print("  • Manter apenas ai_trading_system/ como sistema principal")
    print()
    
    confirm = input("🤔 Confirma a limpeza? (digite 'LIMPAR' para confirmar): ").strip()
    
    if confirm == "LIMPAR":
        main()
    else:
        print("❌ Limpeza cancelada. Nenhum arquivo foi alterado.")
        print("💡 Para executar a limpeza, digite exatamente 'LIMPAR'")
