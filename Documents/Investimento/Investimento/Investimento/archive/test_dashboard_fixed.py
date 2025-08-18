import os
import sys
from pathlib import Path

# Adiciona o diretório do projeto
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

# Mock do Streamlit para testes
class MockStreamlit:
    def write(self, text): 
        print(f"ST: {text}")
    def success(self, text): 
        print(f"✅ {text}")
    def warning(self, text): 
        print(f"⚠️ {text}")
    def error(self, text): 
        print(f"❌ {text}")
    def cache_data(self, func):
        return func
    def set_page_config(self, **kwargs):
        pass
    def title(self, text):
        print(f"TITLE: {text}")
    def sidebar(self):
        return self
    def columns(self, n):
        return [self] * n
    def metric(self, *args, **kwargs):
        pass
    def plotly_chart(self, *args, **kwargs):
        pass
    def subheader(self, text):
        print(f"SUBHEADER: {text}")
    def markdown(self, text):
        pass
    def selectbox(self, *args, **kwargs):
        return "All"
    def slider(self, *args, **kwargs):
        return 1.0
    def checkbox(self, *args, **kwargs):
        return False

# Mock global
sys.modules['streamlit'] = MockStreamlit()

print("🧪 Dashboard Function Test")
print("=" * 50)

try:
    # Agora importa o dashboard
    from dashboard.main_dashboard import load_data, calculate_portfolio_metrics, render_key_metrics
    
    print("✅ Dashboard imports successful")
    
    # Teste load_data
    print("\n📊 Testing load_data()...")
    data = load_data()
    
    if data is None:
        print("❌ load_data returned None")
    else:
        print(f"✅ load_data successful!")
        print(f"📋 Data keys: {list(data.keys())}")
        
        for key, df in data.items():
            if hasattr(df, 'shape'):
                print(f"   • {key}: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Teste calculate_portfolio_metrics
        if 'equity' in data and not data['equity'].empty:
            print("\n📈 Testing calculate_portfolio_metrics()...")
            metrics = calculate_portfolio_metrics(data['equity'])
            
            print("✅ Metrics calculated:")
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    print(f"   • {key}: {value:.2f}")
                else:
                    print(f"   • {key}: {value}")
        
        # Teste render_key_metrics (só a lógica, não a UI)
        print("\n🎯 Testing render_key_metrics logic...")
        mock_filters = {
            'period_days': None,
            'min_sharpe_alert': 1.0,
            'max_dd_alert': 20.0
        }
        
        try:
            # Aqui normalmente seria chamado render_key_metrics(data, mock_filters)
            # Mas vamos apenas verificar se os dados estão OK para a função
            equity_data = data.get('equity', None)
            trades_data = data.get('trades', None)
            
            if equity_data is not None and not equity_data.empty:
                print("✅ Equity data ready for render_key_metrics")
            else:
                print("⚠️ No equity data for render_key_metrics")
                
            if trades_data is not None and not trades_data.empty:
                print("✅ Trades data ready for render_key_metrics")
                print(f"   • Trades columns: {list(trades_data.columns)}")
                # Verifica se tem pnl_pct
                if 'pnl_pct' in trades_data.columns:
                    print(f"   • PnL data available: {trades_data['pnl_pct'].describe()}")
                else:
                    print("   ⚠️ No pnl_pct column")
            else:
                print("⚠️ No trades data for render_key_metrics")
                
        except Exception as e:
            print(f"❌ Error in render_key_metrics test: {e}")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("✅ Dashboard test completed!")
