#!/usr/bin/env python3
"""
Teste rápido do dashboard para verificar se os dados carregam corretamente
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Adiciona o diretório atual ao path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def test_data_loading():
    """Testa o carregamento dos dados"""
    print("🧪 Testing Data Loading...")
    print(f"📁 Current directory: {os.getcwd()}")
    
    # Verifica se estamos no diretório correto
    data_dir = current_dir / "data"
    print(f"📂 Data directory: {data_dir}")
    print(f"📂 Data directory exists: {data_dir.exists()}")
    
    if data_dir.exists():
        files = list(data_dir.glob("*.csv"))
        print(f"📄 Found {len(files)} CSV files:")
        for file in files:
            print(f"   • {file.name}")
    
    # Tenta carregar os dados principais
    files_to_load = {
        'equity': 'equity_momentum_optimized.csv',
        'trades': 'trades_momentum_optimized.csv',
        'correlation': 'momentum_correlation.csv',
        'multi_asset': 'trades_multi_asset.csv',
        'metrics': 'advanced_metrics_report.csv'
    }
    
    loaded_data = {}
    
    for key, filename in files_to_load.items():
        filepath = data_dir / filename
        print(f"\n📊 Loading {key} from {filename}...")
        
        if not filepath.exists():
            print(f"   ❌ File not found: {filepath}")
            continue
            
        try:
            df = pd.read_csv(filepath)
            print(f"   ✅ Loaded successfully: {len(df)} rows, {len(df.columns)} columns")
            print(f"   📋 Columns: {list(df.columns)}")
            
            # Verifica primeiras linhas
            if len(df) > 0:
                print(f"   📝 First row sample: {dict(df.iloc[0])}")
            
            loaded_data[key] = df
            
        except Exception as e:
            print(f"   ❌ Error loading {filename}: {e}")
    
    return loaded_data

def test_dashboard_functions():
    """Testa as funções do dashboard"""
    print("\n🔧 Testing Dashboard Functions...")
    
    try:
        # Importa as funções do dashboard
        from dashboard.main_dashboard import load_data, calculate_portfolio_metrics
        
        print("✅ Dashboard imports successful")
        
        # Testa carregamento de dados
        print("\n📡 Testing load_data function...")
        data = load_data()
        
        if data is None:
            print("❌ load_data returned None")
        else:
            print(f"✅ load_data successful: {list(data.keys())}")
            
            # Testa cálculo de métricas
            if 'equity' in data and not data['equity'].empty:
                print("\n📊 Testing calculate_portfolio_metrics...")
                metrics = calculate_portfolio_metrics(data['equity'])
                print(f"✅ Metrics calculated: {metrics}")
            else:
                print("⚠️ No equity data for metrics calculation")
                
    except Exception as e:
        print(f"❌ Error testing dashboard functions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Dashboard Data Loading Test")
    print("=" * 50)
    
    # Teste 1: Carregamento direto dos dados
    data = test_data_loading()
    
    # Teste 2: Funções do dashboard
    test_dashboard_functions()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
