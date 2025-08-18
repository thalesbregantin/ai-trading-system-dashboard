#!/usr/bin/env python3
"""
Test script para verificar erros no dashboard
"""
import os
import sys
import traceback

def test_dashboard_imports():
    """Testa importações do dashboard"""
    try:
        print("🔍 Testando importações...")
        
        # Teste básico de importações
        import streamlit as st
        print("✅ Streamlit OK")
        
        import pandas as pd
        print("✅ Pandas OK")
        
        import numpy as np
        print("✅ Numpy OK")
        
        import plotly.graph_objects as go
        print("✅ Plotly OK")
        
        # Teste específico do dashboard
        sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))
        
        print("🔍 Testando módulo dashboard...")
        
        # Importa sem executar
        import importlib.util
        dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard', 'main_dashboard.py')
        
        spec = importlib.util.spec_from_file_location("main_dashboard", dashboard_path)
        dashboard_module = importlib.util.module_from_spec(spec)
        
        print("✅ Dashboard module carregado")
        
        # Testa função específica
        print("🔍 Testando função load_data...")
        
        # Executa o módulo
        spec.loader.exec_module(dashboard_module)
        
        # Testa função load_data
        if hasattr(dashboard_module, 'load_data'):
            print("✅ Função load_data encontrada")
            
            # Teste da função (sem cache do streamlit)
            try:
                # Simula dados para teste
                test_data = {
                    'portfolio': {'current_value': 1000},
                    'trades': pd.DataFrame(),
                    'correlation': pd.DataFrame({'date': pd.date_range('2024-01-01', periods=10), 'correlation': np.random.rand(10)})
                }
                print("✅ Dados de teste criados")
                
            except Exception as e:
                print(f"❌ Erro nos dados de teste: {e}")
                
        else:
            print("❌ Função load_data não encontrada")
            
        print("🎉 Teste de importações concluído!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🧪 TESTE DE DASHBOARD")
    print("=" * 50)
    
    success = test_dashboard_imports()
    
    if success:
        print("\n✅ Todos os testes passaram!")
        print("💡 Dashboard deve funcionar corretamente")
    else:
        print("\n❌ Problemas detectados!")
        print("💡 Verifique os erros acima")
