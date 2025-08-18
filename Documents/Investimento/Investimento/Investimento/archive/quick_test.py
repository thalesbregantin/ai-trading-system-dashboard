import sys
import os
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

print("🧪 Quick Dashboard Test")
print("=" * 40)

# Teste 1: Importação do dashboard
try:
    from dashboard.main_dashboard import load_data, calculate_portfolio_metrics
    print("✅ Dashboard imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    exit(1)

# Teste 2: Carregamento dos dados
try:
    print("\n📊 Testing data loading...")
    
    # Simula o contexto do Streamlit
    class MockStreamlit:
        def write(self, text): print(f"   {text}")
        def success(self, text): print(f"   ✅ {text}")
        def warning(self, text): print(f"   ⚠️ {text}")
        def error(self, text): print(f"   ❌ {text}")
    
    # Mock temporário do streamlit
    import dashboard.main_dashboard as dash
    dash.st = MockStreamlit()
    
    # Carrega dados
    data = load_data()
    
    if data is None:
        print("❌ Data loading failed")
    else:
        print(f"✅ Data loading successful: {list(data.keys())}")
        
        # Teste 3: Cálculo de métricas
        if 'equity' in data and not data['equity'].empty:
            print("\n📈 Testing metrics calculation...")
            metrics = calculate_portfolio_metrics(data['equity'])
            
            print(f"✅ Metrics calculated:")
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"   • {key}: {value:.2f}")
                else:
                    print(f"   • {key}: {value}")
                    
        # Informações dos dados
        for key, df in data.items():
            if hasattr(df, 'shape'):
                print(f"   📋 {key}: {df.shape[0]} rows, {df.shape[1]} columns")
                if not df.empty:
                    print(f"      Columns: {list(df.columns)}")

except Exception as e:
    print(f"❌ Test error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 40)
print("✅ Test completed!")
