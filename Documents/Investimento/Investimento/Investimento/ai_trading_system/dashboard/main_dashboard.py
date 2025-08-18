#!/usr/bin/env python3
"""
🤖 AI Trading Dashboard - Interface Unificada
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import requests

# Configuração da página
st.set_page_config(
    page_title="AI Trading Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar estado da sessão
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

def check_api_connection():
    """Verifica conexão com a API"""
    try:
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def render_dashboard():
    """Página principal do dashboard"""
    st.title("📊 Dashboard")
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Portfolio Value", "$24,567.89", "+2.4%")
    with col2:
        st.metric("Today's Profit", "$567.89", "-1.2%")
    with col3:
        st.metric("Win Rate", "68.5%")
    with col4:
        st.metric("Sharpe Ratio", "0.82")
    
    # Gráfico
    st.markdown("### Trading Chart")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pd.date_range(start='2024-01-01', periods=100, freq='D'),
        y=np.random.randn(100).cumsum(),
        mode='lines',
        name='Portfolio Value'
    ))
    st.plotly_chart(fig, use_container_width=True)
    
def render_trades():
    """Página de trades"""
    st.title("🔄 Trades")
    
    # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
        symbol = st.selectbox("Par", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
            with col2:
        timeframe = st.selectbox("Período", ["1H", "4H", "1D", "1W"])
            with col3:
        status = st.selectbox("Status", ["Todos", "Executado", "Pendente"])
    
    # Dados simulados
    trades_data = {
        'timestamp': pd.date_range(start='2024-01-01', periods=20, freq='D'),
        'symbol': ['BTC/USDT'] * 20,
        'side': ['BUY', 'SELL'] * 10,
        'amount': np.random.uniform(0.1, 2.0, 20),
        'price': np.random.uniform(40000, 50000, 20),
        'profit': np.random.uniform(-100, 200, 20)
    }
    
    df = pd.DataFrame(trades_data)
    st.dataframe(df, use_container_width=True)

def render_settings():
    """Página de configurações"""
    st.title("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["🔑 API Keys", "💰 Trading", "🎨 Appearance"])
    
    with tab1:
        st.markdown("### Configuração de API Keys")
        api_key = st.text_input("Binance API Key", type="password")
        secret_key = st.text_input("Binance Secret Key", type="password")
        if st.button("💾 Salvar"):
            st.success("✅ Chaves salvas!")
    
    with tab2:
        st.markdown("### Configurações de Trading")
        initial_capital = st.number_input("Capital Inicial (USDT)", value=1000.0)
        stop_loss = st.number_input("Stop Loss (%)", value=5.0)
        take_profit = st.number_input("Take Profit (%)", value=10.0)
        if st.button("💾 Salvar"):
            st.success("✅ Configurações salvas!")
    
    with tab3:
        st.markdown("### Aparência")
        theme = st.selectbox("Tema", ["Claro", "Escuro", "Auto"])
        language = st.selectbox("Idioma", ["Português", "English"])
        if st.button("💾 Salvar"):
            st.success("✅ Configurações salvas!")

def render_ai_models():
    """Página de modelos AI"""
    st.title("🧠 AI Models")
    
    # Modelos simulados
    models = [
        {"name": "BTC_Model_v1", "status": "Trained", "accuracy": "78.5%", "profit": "+$1,234.56"},
        {"name": "ETH_Model_v1", "status": "Training", "accuracy": "75.2%", "profit": "+$567.89"},
        {"name": "SOL_Model_v1", "status": "Ready", "accuracy": "82.1%", "profit": "+$2,345.67"}
    ]
    
    for model in models:
        with st.expander(f"🤖 {model['name']} - {model['status']}"):
        col1, col2, col3 = st.columns(3)
        with col1:
                st.metric("Status", model['status'])
        with col2:
                st.metric("Accuracy", model['accuracy'])
        with col3:
                st.metric("Profit/Loss", model['profit'])
            
            if st.button("🔄 Retrain", key=f"retrain_{model['name']}"):
                st.info("🔄 Retreinando modelo...")

def render_docs():
    """Página de documentação"""
    st.title("📄 Documentation")
    
    tab1, tab2, tab3 = st.tabs(["📖 Guia", "🔧 API", "❓ FAQ"])
    
    with tab1:
                st.markdown("""
        ### 📖 Guia de Uso
        
        1. **Configure suas API Keys** na seção Settings
        2. **Inicie o servidor API** com `python simple_api_server.py`
        3. **Ative o Live Mode** para dados em tempo real
        4. **Monitore seus trades** na seção Trades
        """)
    
    with tab2:
            st.markdown("""
        ### 🔧 API Documentation
        
        **GET /api/status** - Verifica status da conexão
        **GET /api/balance** - Obtém saldo da conta
        **GET /api/trades** - Obtém histórico de trades
        """)
    
    with tab3:
    st.markdown("""
        ### ❓ FAQ
        
        **Como configurar as API Keys?**
        1. Acesse sua conta Binance
        2. Vá em API Management
        3. Crie uma nova API Key
        4. Configure as permissões necessárias
        """)

def main():
    # Sidebar
    with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2 style="color: white; margin: 0;">🤖 AI Trader</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
        st.markdown("### 🔧 System Status")
        
        # Verifica conexão com API
        api_status = check_api_connection()
        if api_status and api_status.get('success'):
            st.success("✅ API Conectada")
        else:
            st.error("❌ API Desconectada")
    
    st.markdown("---")
        st.markdown("### 📱 Navegação")
        
        # Menu de navegação
        pages = {
            'dashboard': '📊 Dashboard',
            'trades': '🔄 Trades',
            'settings': '⚙️ Settings',
            'ai_models': '🧠 AI Models',
            'docs': '📄 Docs'
        }
        
        for page_id, page_name in pages.items():
            if st.button(page_name, key=f"nav_{page_id}"):
                st.session_state.current_page = page_id
                st.rerun()
    
    # Renderizar página atual
    if st.session_state.current_page == 'dashboard':
        render_dashboard()
    elif st.session_state.current_page == 'trades':
        render_trades()
    elif st.session_state.current_page == 'settings':
        render_settings()
    elif st.session_state.current_page == 'ai_models':
        render_ai_models()
    elif st.session_state.current_page == 'docs':
        render_docs()

if __name__ == "__main__":
    main()
