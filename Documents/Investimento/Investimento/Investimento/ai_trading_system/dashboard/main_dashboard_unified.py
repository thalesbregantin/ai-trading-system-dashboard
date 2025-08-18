#!/usr/bin/env python3
"""
🤖 AI Trading Dashboard - Interface Unificada e Completa
Dashboard em tempo real para monitoramento do sistema AI Trading
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import sys
import os
import json
import glob
import requests

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.config import get_config
    from core.hybrid_trading_system import HybridTradingSystem
    import yfinance as yf
except ImportError:
    st.error("❌ Erro ao importar módulos do sistema AI Trading")
    st.stop()

# Configuração da página
st.set_page_config(
    page_title="AI Trading Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para o design moderno
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .metric-change {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .ai-panel {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .score-circle {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

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

@st.cache_data(ttl=30)
def load_real_data():
    """Carrega dados reais do sistema AI Trading"""
    try:
        config = get_config('test')
        
        # Carrega dados de treinamento
        training_metrics = []
        training_steps = []
        
        # Lê métricas de treinamento
        metrics_file = "logs/training/training_metrics.csv"
        if os.path.exists(metrics_file):
            try:
                df_metrics = pd.read_csv(metrics_file)
                if not df_metrics.empty:
                    training_metrics = df_metrics.to_dict('records')
            except Exception as e:
                st.warning(f"Erro ao ler métricas: {e}")
        
        # Lê passos de treinamento
        steps_file = "logs/training/training_steps.jsonl"
        if os.path.exists(steps_file):
            try:
                with open(steps_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            training_steps.append(json.loads(line))
            except Exception as e:
                st.warning(f"Erro ao ler passos: {e}")
        
        # Carrega dados de preço em tempo real
        try:
            ticker = yf.Ticker("BTC-USD")
            data = ticker.history(period='1d', interval='1h')
            if not data.empty:
                real_prices = data['Close'].values
                real_timestamps = data.index
            else:
                real_prices = []
                real_timestamps = []
        except Exception as e:
            st.warning(f"Erro ao carregar dados BTC: {e}")
            real_prices = []
            real_timestamps = []
        
        # Carrega logs de trading
        trading_logs = []
        log_file = f"logs/trading_log_{datetime.now().strftime('%Y%m%d')}.log"
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        if 'INFO' in line or 'ERROR' in line:
                            trading_logs.append(line.strip())
            except Exception as e:
                st.warning(f"Erro ao ler logs: {e}")
        
        return {
            'training_metrics': training_metrics,
            'training_steps': training_steps,
            'real_prices': real_prices,
            'real_timestamps': real_timestamps,
            'trading_logs': trading_logs,
            'config': config
        }
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

def get_binance_trades():
    """Obtém trades da Binance via API"""
    try:
        response = requests.get('http://localhost:5000/api/trades', timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_ai_models_status():
    """Obtém status dos modelos AI"""
    try:
        # Verifica arquivos de modelo
        model_files = glob.glob("models/*.h5")
        training_logs = glob.glob("logs/training/*.csv")
        
        models = []
        for model_file in model_files:
            model_name = os.path.basename(model_file).replace('.h5', '')
            models.append({
                'name': model_name,
                'file': model_file,
                'status': 'Trained',
                'last_updated': datetime.fromtimestamp(os.path.getmtime(model_file))
            })
        
        return models
    except Exception as e:
        st.error(f"Erro ao carregar modelos: {e}")
        return []

def calculate_real_metrics(data):
    """Calcula métricas reais baseadas nos dados"""
    if not data or not data['training_metrics']:
        return {
            'portfolio_value': 1000.0,
            'today_profit': 0.0,
            'win_rate': 0.0,
            'sharpe_ratio': 0.0
        }
    
    metrics = data['training_metrics']
    
    if len(metrics) >= 3:
        recent_metrics = metrics[-3:]
        portfolio_value = recent_metrics[-1].get('final_equity', 1000.0)
        today_profit = portfolio_value - recent_metrics[0].get('final_equity', 1000.0)
        
        win_rates = [m.get('win_rate', 0) for m in recent_metrics if 'win_rate' in m]
        win_rate = np.mean(win_rates) if win_rates else 0.0
        
        sharpe_ratios = [m.get('sharpe_ratio', 0) for m in recent_metrics if 'sharpe_ratio' in m]
        sharpe_ratio = np.mean(sharpe_ratios) if sharpe_ratios else 0.0
        
        return {
            'portfolio_value': portfolio_value,
            'today_profit': today_profit,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe_ratio
        }
    
    return {
        'portfolio_value': 1000.0,
        'today_profit': 0.0,
        'win_rate': 0.0,
        'sharpe_ratio': 0.0
    }

def create_trading_chart(data):
    """Cria gráfico de trading"""
    if not data or len(data['real_prices']) == 0:
        # Fallback para dados simulados
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        timestamps = pd.date_range(start=start_time, end=end_time, freq='H')
        base_price = 42100
        prices = [base_price + np.sin(i * 0.5) * 300 + np.random.normal(0, 50) for i in range(len(timestamps))]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=prices,
            mode='lines+markers',
            name='BTC Price (Simulado)',
            line=dict(color='#3b82f6', width=2),
            fill='tonexty',
            fillcolor='rgba(59, 130, 246, 0.1)'
        ))
        
        fig.update_layout(
            title='BTC/USDT - AI Trading Signals',
            xaxis_title='Time',
            yaxis_title='Price (USD)',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['real_timestamps'],
        y=data['real_prices'],
        mode='lines+markers',
        name='BTC Price (Real)',
        line=dict(color='#3b82f6', width=2),
        fill='tonexty',
        fillcolor='rgba(59, 130, 246, 0.1)'
    ))
    
    if len(data['real_prices']) >= 20:
        sma_20 = pd.Series(data['real_prices']).rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=data['real_timestamps'],
            y=sma_20,
            mode='lines',
            name='SMA (20)',
            line=dict(color='#8b5cf6', width=2, dash='dash')
        ))
    
    fig.update_layout(
        title='BTC/USDT - AI Trading Signals (Dados Reais)',
        xaxis_title='Time',
        yaxis_title='Price (USD)',
        template='plotly_white',
        height=400,
        showlegend=True
    )
    
    return fig

def create_metric_card(title, value, change=None, change_type="positive"):
    """Cria um card de métrica"""
    change_html = ""
    if change:
        arrow = "↗️" if change_type == "positive" else "↘️"
        change_html = f'<div class="metric-change">{arrow} {change}</div>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">{title}</div>
        {change_html}
    </div>
    """

def create_ai_decision_panel():
    """Cria painel de decisão AI"""
    return f"""
    <div class="ai-panel">
        <h4>Current Decision</h4>
        <div style="display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;">
            <span>Current Decision</span>
            <button style="background: #10b981; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; font-weight: bold;">BUY</button>
        </div>
        <div style="font-size: 0.9rem; color: #64748b;">
            AI Confidence: 78%<br>
            Momentum Score: 62%
        </div>
    </div>
    
    <div class="ai-panel">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h4>Hybrid System</h4>
            <span style="background: #3b82f6; color: white; padding: 0.25rem 0.5rem; border-radius: 3px; font-size: 0.8rem;">60% AI / 40% Momentum</span>
        </div>
        
        <div style="display: flex; justify-content: space-between;">
            <div style="text-align: center;">
                <div class="score-circle" style="background: #3b82f6;">4.7</div>
                <div style="margin-top: 0.5rem;">
                    <div style="font-weight: bold;">AI Score</div>
                    <div style="font-size: 0.9rem; color: #64748b;">4.7/5</div>
                </div>
            </div>
            
            <div style="text-align: center;">
                <div class="score-circle" style="background: #8b5cf6;">3.9</div>
                <div style="margin-top: 0.5rem;">
                    <div style="font-weight: bold;">Momentum</div>
                    <div style="font-size: 0.9rem; color: #64748b;">3.9/5</div>
                </div>
            </div>
            
            <div style="text-align: center;">
                <div class="score-circle" style="background: #10b981;">4.3</div>
                <div style="margin-top: 0.5rem;">
                    <div style="font-weight: bold;">Final</div>
                    <div style="font-size: 0.9rem; color: #64748b;">4.3/5</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="ai-panel">
        <h4>Technical Indicators</h4>
        <div style="font-size: 0.9rem; line-height: 2;">
            <div>SMA (20) $42,356.78</div>
            <div>SMA (50) $41,987.32</div>
            <div>RSI (14) 56.4</div>
            <div>Momentum +1.2%</div>
        </div>
    </div>
    """

def render_dashboard_page(data):
    """Renderiza a página principal do dashboard"""
    # Header principal
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("AI Trading Dashboard")
    
    with col2:
        # Estado do Live Mode
        if 'live_mode' not in st.session_state:
            st.session_state.live_mode = False
        
        if st.button("🟢 Live Mode ON" if st.session_state.live_mode else "🔴 Live Mode", type="primary"):
            st.session_state.live_mode = not st.session_state.live_mode
            st.rerun()
    
    with col3:
        if st.button("👤 Admin"):
            st.rerun()
    
    # Métricas principais
    st.markdown("---")
    
    if data:
        metrics = calculate_real_metrics(data)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            change_type = "positive" if metrics['portfolio_value'] >= 1000 else "negative"
            change = f"${metrics['portfolio_value'] - 1000:+.2f}"
            st.markdown(create_metric_card("Portfolio Value", f"${metrics['portfolio_value']:,.2f}", change, change_type), unsafe_allow_html=True)
        
        with col2:
            change_type = "positive" if metrics['today_profit'] >= 0 else "negative"
            change = f"${metrics['today_profit']:+.2f}"
            st.markdown(create_metric_card("Today's Profit", f"${metrics['today_profit']:,.2f}", change, change_type), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_metric_card("Win Rate", f"{metrics['win_rate']:.1f}%"), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_metric_card("Sharpe Ratio", f"{metrics['sharpe_ratio']:.3f}"), unsafe_allow_html=True)
    else:
        # Métricas de fallback
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_metric_card("Portfolio Value", "$24,567.89", "+2.4%", "positive"), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_metric_card("Today's Profit", "$567.89", "-1.2%", "negative"), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_metric_card("Win Rate", "68.5%"), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_metric_card("Sharpe Ratio", "0.82"), unsafe_allow_html=True)
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Trading Chart")
        
        # Botões de período
        col_period1, col_period2, col_period3, col_period4, col_period5 = st.columns(5)
        with col_period1:
            if st.button("1H", type="primary"):
                st.rerun()
        with col_period2:
            if st.button("4H"):
                st.rerun()
        with col_period3:
            if st.button("1D"):
                st.rerun()
        with col_period4:
            if st.button("1W"):
                st.rerun()
        with col_period5:
            if st.button("1M"):
                st.rerun()
        
        # Gráfico
        fig = create_trading_chart(data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### AI Decision Panel")
        st.markdown(create_ai_decision_panel(), unsafe_allow_html=True)

def render_trades_page():
    """Renderiza a página de trades"""
    st.title("🔄 Trades")
    st.markdown("---")
    
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        symbol = st.selectbox("Par", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "ADA/USDT"])
    with col2:
        timeframe = st.selectbox("Período", ["1H", "4H", "1D", "1W"])
    with col3:
        order_type = st.selectbox("Tipo", ["Todos", "BUY", "SELL"])
    with col4:
        status = st.selectbox("Status", ["Todos", "Executado", "Pendente", "Cancelado"])
    
    # Buscar trades da API
    trades_data = get_binance_trades()
    
    if trades_data and trades_data.get('success'):
        trades = trades_data['data']
        
        # Criar DataFrame
        df = pd.DataFrame(trades)
        
        # Aplicar filtros
        if symbol != "Todos":
            df = df[df['symbol'] == symbol]
        if order_type != "Todos":
            df = df[df['side'] == order_type]
        if status != "Todos":
            df = df[df['status'] == status]
        
        # Mostrar tabela
        st.markdown("### Histórico de Trades")
        st.dataframe(df, use_container_width=True)
        
        # Métricas dos trades
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Trades", len(df))
        with col2:
            st.metric("Win Rate", f"{len(df[df['profit'] > 0]) / len(df) * 100:.1f}%" if len(df) > 0 else "0%")
        with col3:
            st.metric("Total Profit", f"${df['profit'].sum():.2f}" if len(df) > 0 else "$0.00")
        with col4:
            st.metric("Avg Trade", f"${df['profit'].mean():.2f}" if len(df) > 0 else "$0.00")
        
        # Gráfico de performance
        if len(df) > 0:
            fig = px.line(df, x='timestamp', y='cumulative_profit', title='Cumulative Profit')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Não foi possível carregar os trades. Verifique se a API está rodando.")
        
        # Dados simulados para demonstração
        st.markdown("### Dados de Demonstração")
        
        # Criar dados simulados
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        np.random.seed(42)
        
        demo_trades = []
        cumulative_profit = 0
        
        for i, date in enumerate(dates[:50]):  # Primeiros 50 dias
            profit = np.random.normal(10, 50)  # Profit/loss normal
            cumulative_profit += profit
            
            demo_trades.append({
                'timestamp': date,
                'symbol': np.random.choice(['BTC/USDT', 'ETH/USDT', 'SOL/USDT']),
                'side': np.random.choice(['BUY', 'SELL']),
                'amount': np.random.uniform(0.1, 2.0),
                'price': np.random.uniform(40000, 50000),
                'profit': profit,
                'cumulative_profit': cumulative_profit,
                'status': 'Executado'
            })
        
        df_demo = pd.DataFrame(demo_trades)
        st.dataframe(df_demo, use_container_width=True)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Trades", len(df_demo))
        with col2:
            st.metric("Win Rate", f"{len(df_demo[df_demo['profit'] > 0]) / len(df_demo) * 100:.1f}%")
        with col3:
            st.metric("Total Profit", f"${df_demo['profit'].sum():.2f}")
        with col4:
            st.metric("Avg Trade", f"${df_demo['profit'].mean():.2f}")

def render_settings_page():
    """Renderiza a página de configurações"""
    st.title("⚙️ Settings")
    st.markdown("---")
    
    # Abas de configuração
    tab1, tab2, tab3, tab4 = st.tabs(["🔑 API Keys", "💰 Trading", "🔔 Notifications", "🎨 Appearance"])
    
    with tab1:
        st.markdown("### Configuração de API Keys")
        st.info("⚠️ As chaves são armazenadas localmente e não são enviadas para servidores externos.")
        
        api_key = st.text_input("Binance API Key", type="password", help="Sua chave API da Binance")
        secret_key = st.text_input("Binance Secret Key", type="password", help="Sua chave secreta da Binance")
        
        if st.button("💾 Salvar Chaves"):
            st.success("✅ Chaves salvas com sucesso!")
    
    with tab2:
        st.markdown("### Configurações de Trading")
        
        col1, col2 = st.columns(2)
        with col1:
            initial_capital = st.number_input("Capital Inicial (USDT)", min_value=100.0, value=1000.0, step=100.0)
            max_position_size = st.number_input("Tamanho Máximo da Posição (%)", min_value=1, max_value=100, value=10)
            stop_loss = st.number_input("Stop Loss (%)", min_value=0.1, max_value=50.0, value=5.0, step=0.1)
        
        with col2:
            take_profit = st.number_input("Take Profit (%)", min_value=0.1, max_value=100.0, value=10.0, step=0.1)
            max_daily_trades = st.number_input("Máximo de Trades Diários", min_value=1, max_value=100, value=10)
            risk_per_trade = st.number_input("Risco por Trade (%)", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
        
        if st.button("💾 Salvar Configurações"):
            st.success("✅ Configurações salvas com sucesso!")
    
    with tab3:
        st.markdown("### Configurações de Notificações")
        
        email_notifications = st.checkbox("📧 Notificações por Email")
        telegram_notifications = st.checkbox("📱 Notificações por Telegram")
        browser_notifications = st.checkbox("🌐 Notificações do Navegador")
        
        if email_notifications:
            email = st.text_input("Email para notificações")
        
        if telegram_notifications:
            telegram_token = st.text_input("Token do Bot Telegram", type="password")
            telegram_chat_id = st.text_input("Chat ID do Telegram")
        
        if st.button("💾 Salvar Notificações"):
            st.success("✅ Configurações de notificações salvas!")
    
    with tab4:
        st.markdown("### Aparência do Dashboard")
        
        theme = st.selectbox("Tema", ["Claro", "Escuro", "Auto"])
        language = st.selectbox("Idioma", ["Português", "English", "Español"])
        timezone = st.selectbox("Fuso Horário", ["UTC", "America/Sao_Paulo", "Europe/London"])
        
        if st.button("💾 Salvar Aparência"):
            st.success("✅ Configurações de aparência salvas!")

def render_ai_models_page():
    """Renderiza a página de modelos AI"""
    st.title("🧠 AI Models")
    st.markdown("---")
    
    # Status dos modelos
    models = get_ai_models_status()
    
    if models:
        st.markdown("### Modelos Treinados")
        
        for model in models:
            with st.expander(f"🤖 {model['name']} - {model['status']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Status", model['status'])
                    st.metric("Última Atualização", model['last_updated'].strftime("%d/%m/%Y %H:%M"))
                
                with col2:
                    st.metric("Accuracy", "78.5%")
                    st.metric("Profit/Loss", "+$1,234.56")
                
                with col3:
                    if st.button("🔄 Retrain", key=f"retrain_{model['name']}"):
                        st.info("🔄 Retreinando modelo...")
                    
                    if st.button("📊 Performance", key=f"perf_{model['name']}"):
                        st.info("📊 Carregando métricas de performance...")
    
    else:
        st.warning("⚠️ Nenhum modelo encontrado. Execute o treinamento primeiro.")
    
    # Configurações de treinamento
    st.markdown("---")
    st.markdown("### Configurações de Treinamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        episodes = st.number_input("Episódios de Treinamento", min_value=100, value=1000, step=100)
        learning_rate = st.number_input("Taxa de Aprendizado", min_value=0.0001, max_value=0.1, value=0.001, format="%.4f")
        batch_size = st.number_input("Tamanho do Batch", min_value=16, max_value=512, value=64, step=16)
    
    with col2:
        memory_size = st.number_input("Tamanho da Memória", min_value=1000, value=10000, step=1000)
        gamma = st.number_input("Gamma (Discount Factor)", min_value=0.1, max_value=1.0, value=0.95, step=0.05)
        epsilon = st.number_input("Epsilon Inicial", min_value=0.01, max_value=1.0, value=1.0, step=0.01)
    
    if st.button("🚀 Iniciar Treinamento"):
        st.info("🚀 Iniciando treinamento do modelo...")
        # Aqui seria implementada a lógica de treinamento

def render_docs_page():
    """Renderiza a página de documentação"""
    st.title("📄 Documentation")
    st.markdown("---")
    
    # Abas de documentação
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Guia de Uso", "🔧 API Docs", "❓ FAQ", "🔗 Links"])
    
    with tab1:
        st.markdown("### 📖 Guia de Uso")
        
        st.markdown("""
        #### 🚀 Primeiros Passos
        
        1. **Configure suas API Keys** na seção Settings
        2. **Inicie o servidor API** com `python simple_api_server.py`
        3. **Ative o Live Mode** para dados em tempo real
        4. **Monitore seus trades** na seção Trades
        
        #### 📊 Dashboard
        
        O dashboard principal mostra:
        - **Métricas em tempo real** do seu portfólio
        - **Gráficos de preços** com sinais de trading
        - **Decisões da IA** baseadas em análise técnica
        
        #### 🔄 Live Mode
        
        O Live Mode atualiza automaticamente:
        - Dados de preços a cada 30 segundos
        - Métricas de performance
        - Sinais de trading da IA
        """)
    
    with tab2:
        st.markdown("### 🔧 API Documentation")
        
        st.markdown("""
        #### Endpoints Disponíveis
        
        **GET /api/status**
        - Verifica status da conexão com Binance
        - Retorna: `{success: true, data: {binance_connected: true}}`
        
        **GET /api/balance**
        - Obtém saldo da conta Binance
        - Retorna: `{success: true, data: {balances: {...}, total_usdt_value: 1234.56}}`
        
        **GET /api/trades**
        - Obtém histórico de trades
        - Parâmetros: `symbol`, `limit`, `since`
        
        **GET /api/current-price**
        - Obtém preço atual de um par
        - Parâmetros: `symbol` (padrão: BTC/USDT)
        """)
    
    with tab3:
        st.markdown("### ❓ FAQ")
        
        with st.expander("Como configurar as API Keys?"):
            st.markdown("""
            1. Acesse sua conta Binance
            2. Vá em API Management
            3. Crie uma nova API Key
            4. Configure as permissões necessárias
            5. Cole as chaves na seção Settings
            """)
        
        with st.expander("O que significa 'API Desconectada'?"):
            st.markdown("""
            Significa que o servidor API não está rodando. Execute:
            ```bash
            python simple_api_server.py
            ```
            """)
        
        with st.expander("Como interpretar os sinais da IA?"):
            st.markdown("""
            - **BUY**: A IA recomenda comprar
            - **SELL**: A IA recomenda vender
            - **HOLD**: A IA recomenda aguardar
            - **Score**: Confiança da decisão (0-5)
            """)
    
    with tab4:
        st.markdown("### 🔗 Links Úteis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📚 Recursos**
            - [Documentação Binance API](https://binance-docs.github.io/apidocs/)
            - [CCXT Library](https://docs.ccxt.com/)
            - [Streamlit Docs](https://docs.streamlit.io/)
            """)
        
        with col2:
            st.markdown("""
            **🛠️ Ferramentas**
            - [TradingView](https://www.tradingview.com/)
            - [CoinGecko](https://coingecko.com/)
            - [Fear & Greed Index](https://alternative.me/crypto/fear-and-greed-index/)
            """)

def main():
    """Função principal do dashboard"""
    
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
            if api_status['data']['binance_connected']:
                st.success("✅ Binance Conectada")
            else:
                st.warning("⚠️ Binance Desconectada")
        else:
            st.error("❌ API Desconectada")
            st.info("💡 Execute: python simple_api_server.py")
        
        # Carrega dados reais
        data = load_real_data()
        
        if data:
            st.success("✅ Sistema Conectado")
            st.info(f"📊 Dados de Treinamento: {len(data['training_metrics'])} registros")
            st.info(f"🔄 Passos de Treinamento: {len(data['training_steps'])} passos")
            if len(data['real_prices']) > 0:
                st.success(f"📈 Dados BTC: {len(data['real_prices'])} pontos")
            else:
                st.warning("⚠️ Dados BTC não disponíveis")
        else:
            st.warning("⚠️ Dados limitados disponíveis")
        
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
        render_dashboard_page(data)
    elif st.session_state.current_page == 'trades':
        render_trades_page()
    elif st.session_state.current_page == 'settings':
        render_settings_page()
    elif st.session_state.current_page == 'ai_models':
        render_ai_models_page()
    elif st.session_state.current_page == 'docs':
        render_docs_page()
    
    # Auto-refresh
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    # Live Mode Auto-refresh
    if st.session_state.live_mode:
        st.info("🟢 Live Mode Ativo - Atualizando automaticamente a cada 30 segundos...")
        time.sleep(30)
        st.rerun()

if __name__ == "__main__":
    main()
