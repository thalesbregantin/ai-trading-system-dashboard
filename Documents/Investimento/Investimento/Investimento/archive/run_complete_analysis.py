#!/usr/bin/env python3
"""
🚀 Suite Completa de Análises - Crypto Momentum
Executa todas as melhorias implementadas em sequência
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def print_header(title: str):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*70)
    print(f"🚀 {title}")
    print("="*70)

def run_script(script_name: str, description: str) -> bool:
    """Executa um script Python e retorna True se bem-sucedido"""
    print_header(description)
    
    try:
        print(f"▶️ Executando: {script_name}")
        start_time = time.time()
        
        # Executa o script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=600)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️ Tempo de execução: {duration:.1f}s")
        
        if result.returncode == 0:
            print("✅ Execução bem-sucedida!")
            if result.stdout:
                print("\n📊 Saída:")
                print(result.stdout[-1000:])  # Últimas 1000 chars
            return True
        else:
            print("❌ Erro na execução!")
            if result.stderr:
                print(f"\n🚨 Erro: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - Script demorou mais de 10 minutos")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print_header("VERIFICAÇÃO DE DEPENDÊNCIAS")
    
    required_packages = [
        'pandas', 'numpy', 'requests', 'tqdm', 
        'sklearn', 'matplotlib', 'seaborn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - FALTANDO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🚨 Pacotes faltando: {', '.join(missing_packages)}")
        print("📥 Para instalar:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("\n✅ Todas as dependências estão instaladas!")
    return True

def check_base_files():
    """Verifica se os arquivos base existem"""
    print_header("VERIFICAÇÃO DE ARQUIVOS BASE")
    
    required_files = [
        'crypto_momentum_optimized.py',
        'requirements-crypto.txt'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - FALTANDO")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n🚨 Arquivos base faltando: {', '.join(missing_files)}")
        return False
    
    print("\n✅ Todos os arquivos base encontrados!")
    return True

def generate_summary_report():
    """Gera relatório resumido de todos os resultados"""
    print_header("RELATÓRIO RESUMIDO")
    
    # Lista todos os arquivos CSV gerados
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    print("📁 Arquivos gerados:")
    for file in sorted(csv_files):
        if os.path.getsize(file) > 0:
            print(f"  ✅ {file} ({os.path.getsize(file)} bytes)")
        else:
            print(f"  ⚠️ {file} (vazio)")
    
    # Lista arquivos de imagem
    img_files = [f for f in os.listdir('.') if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    if img_files:
        print("\n🖼️ Gráficos gerados:")
        for file in sorted(img_files):
            print(f"  ✅ {file}")
    
    print(f"\n📊 Total de arquivos: {len(csv_files) + len(img_files)}")

def main():
    """Função principal - executa toda a suite de análises"""
    
    print("🚀 SUITE COMPLETA DE ANÁLISES - CRYPTO MOMENTUM")
    print(f"📅 Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Diretório atual: {os.getcwd()}")
    
    # 1. Verificações iniciais
    if not check_dependencies():
        print("\n❌ Instale as dependências faltando antes de continuar.")
        print("💡 Execute: pip install -r requirements-crypto.txt")
        return
    
    if not check_base_files():
        print("\n❌ Arquivos base faltando. Verifique a instalação do projeto.")
        print("💡 Execute: python setup_environment.py")
        return
    
    # 2. Scripts para executar (em ordem)
    scripts = [
        ("crypto_momentum_optimized.py", "ESTRATÉGIA BASE - Momentum Otimizado"),
        ("advanced_metrics.py", "MÉTRICAS AVANÇADAS"),
        ("correlation_analysis.py", "ANÁLISE DE CORRELAÇÃO"),
        ("multi_asset_portfolio.py", "PORTFOLIO MULTI-ASSET"),
        ("walk_forward_analysis.py", "WALK-FORWARD ANALYSIS"),
        ("regime_analysis.py", "ANÁLISE DE REGIMES")
    ]
    
    # 3. Executa cada script
    results = {}
    total_start_time = time.time()
    
    for script, description in scripts:
        if os.path.exists(script):
            success = run_script(script, description)
            results[script] = success
            
            if not success:
                print(f"\n⚠️ {script} falhou. Continuando com próximo...")
            
            # Pausa entre execuções
            time.sleep(2)
        else:
            print(f"\n⚠️ {script} não encontrado. Pulando...")
            results[script] = False
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # 4. Relatório final
    print_header("RELATÓRIO FINAL DE EXECUÇÃO")
    
    print(f"⏱️ Tempo total: {total_duration/60:.1f} minutos")
    print(f"📅 Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📊 Resultados por script:")
    successful = 0
    for script, success in results.items():
        status = "✅ Sucesso" if success else "❌ Falha"
        print(f"  {script:<30} {status}")
        if success:
            successful += 1
    
    print(f"\n📈 Taxa de sucesso: {successful}/{len(scripts)} ({successful/len(scripts)*100:.1f}%)")
    
    # 5. Relatório de arquivos gerados
    generate_summary_report()
    
    # 6. Recomendações finais
    print_header("PRÓXIMOS PASSOS")
    
    if successful >= len(scripts) * 0.8:  # 80% de sucesso
        print("🎉 Análise completa executada com sucesso!")
        print("\n📋 Próximos passos recomendados:")
        print("  1. Revisar relatórios CSV gerados")
        print("  2. Analisar gráficos de correlação")
        print("  3. Comparar estratégias (single vs multi-asset)")
        print("  4. Avaliar robustez temporal (walk-forward)")
        print("  5. Adaptar parâmetros por regime")
        print("\n📖 Consulte README_MELHORIAS.md para detalhes")
    else:
        print("⚠️ Algumas análises falharam.")
        print("\n🔧 Sugestões:")
        print("  1. Verificar conexão com internet (APIs)")
        print("  2. Verificar espaço em disco")
        print("  3. Executar scripts individualmente")
        print("  4. Verificar logs de erro acima")
    
    print(f"\n💾 Todos os arquivos salvos no diretório atual:")
    print(f"  {os.path.abspath('.')}")

if __name__ == "__main__":
    main()
