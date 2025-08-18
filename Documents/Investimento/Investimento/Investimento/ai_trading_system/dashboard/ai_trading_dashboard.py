"""
Dashboard para AI Trading System
Visualização avançada do sistema híbrido
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os

# Garante import do núcleo correto (evita importar arquivo vazio homônimo nesta pasta)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from hybrid_trading_system import HybridTradingSystem, run_hybrid_analysis
import yfinance as yf
from datetime import datetime, timedelta

def main():
    st.set_page_config(
        page_title="🤖 AI Trading Dashboard",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI Trading System Dashboard")
    st.markdown("**Deep Q-Learning + Momentum Strategy**")
    
    # Sidebar
    st.sidebar.header("⚙️ Configurações")
    
    # Seleção de ativo
    symbol = st.sidebar.selectbox(
        "📈 Selecione o Ativo",
        ['BTC-USD', 'ETH-USD', 'AAPL', 'GOOGL', 'TSLA', 'MSFT'],
        index=0
    )
    
    # Parâmetros do sistema
    st.sidebar.subheader("🎛️ Parâmetros AI")
    ai_weight = st.sidebar.slider("Peso AI Trader", 0.0, 1.0, 0.6, 0.1)
    momentum_weight = 1.0 - ai_weight
    
    episodes = st.sidebar.slider("Episódios de Treinamento", 5, 50, 15, 5)
    
    # Período de dados
    period = st.sidebar.selectbox(
        "📅 Período de Dados",
        ['3mo', '6mo', '1y', '2y'],
        index=2
    )
    
    # Botões principais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        train_button = st.button("🧠 Treinar AI", type="primary")
    
    with col2:
        backtest_button = st.button("📊 Backtest")
    
    with col3:
        signal_button = st.button("🔮 Sinal Atual")
    
    # Estado da sessão
    if 'hybrid_system' not in st.session_state:
        st.session_state.hybrid_system = None
    
    if 'training_data' not in st.session_state:
        st.session_state.training_data = None
    
    # Treinamento
    if train_button:
        with st.spinner(f"🤖 Treinando AI Trader para {symbol}..."):
            try:
                # Inicializa sistema
                hybrid = HybridTradingSystem(symbol, ai_weight, momentum_weight)
                
                # Baixa dados
                data = hybrid.download_data(period=period)
                
                # Treina
                profits = hybrid.train_hybrid_system(data, episodes=episodes)
                
                # Salva no estado
                st.session_state.hybrid_system = hybrid
                st.session_state.training_data = data
                st.session_state.training_profits = profits
                
                st.success("✅ AI Trader treinado com sucesso!")
                
                # Mostra gráfico de treinamento
                show_training_results(profits)
                
            except Exception as e:
                st.error(f"❌ Erro no treinamento: {e}")
    
    # Backtest
    if backtest_button and st.session_state.hybrid_system:
        with st.spinner("📊 Executando backtest..."):
            try:
                hybrid = st.session_state.hybrid_system
                data = st.session_state.training_data
                
                # Executa backtest
                trades, metrics, equity = hybrid.backtest_hybrid(data)
                
                # Mostra resultados
                show_backtest_results(trades, metrics, equity, data, symbol)
                
            except Exception as e:
                st.error(f"❌ Erro no backtest: {e}")
    
    # Sinal atual
    if signal_button and st.session_state.hybrid_system:
        with st.spinner("🔮 Gerando sinal atual..."):
            try:
                hybrid = st.session_state.hybrid_system
                signal = hybrid.real_time_signal(symbol)
                
                show_current_signal(signal)
                
            except Exception as e:
                st.error(f"❌ Erro ao gerar sinal: {e}")
    
    # Informações iniciais
    if not st.session_state.hybrid_system:
        st.info("👆 Clique em 'Treinar AI' para começar!")
        
        # Mostra exemplo de dados
        show_sample_data(symbol, period)

def show_training_results(profits):
    """Mostra resultados do treinamento"""
    st.subheader("📈 Resultados do Treinamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de lucros por episódio
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, len(profits) + 1)),
            y=profits,
            mode='lines+markers',
            name='Lucro por Episódio',
            line=dict(color='#00D4AA', width=3)
        ))
        
        fig.update_layout(
            title="💰 Evolução do Lucro Durante Treinamento",
            xaxis_title="Episódio",
            yaxis_title="Lucro ($)",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Métricas de treinamento
        st.metric("💰 Lucro Final", f"${profits[-1]:.2f}")
        st.metric("📈 Melhor Episódio", f"${max(profits):.2f}")
        st.metric("📉 Pior Episódio", f"${min(profits):.2f}")
        st.metric("📊 Média", f"${np.mean(profits):.2f}")
        
        # Progresso do treinamento
        improvement = profits[-1] - profits[0] if len(profits) > 1 else 0
        st.metric("🚀 Melhoria Total", f"${improvement:.2f}")

def show_backtest_results(trades, metrics, equity, data, symbol):
    """Mostra resultados do backtest"""
    st.subheader("📊 Resultados do Backtest")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Retorno Total",
            f"{metrics['total_return']:.2f}%",
            delta=f"{metrics['total_return']:.2f}%"
        )
    
    with col2:
        st.metric("📈 Trades", metrics['num_trades'])
    
    with col3:
        st.metric(
            "🎯 Win Rate",
            f"{metrics['win_rate']:.1f}%",
            delta=f"{metrics['win_rate']:.1f}%"
        )
    
    with col4:
        st.metric(
            "📊 Sharpe Ratio",
            f"{metrics['sharpe_ratio']:.3f}",
            delta=f"{metrics['sharpe_ratio']:.3f}"
        )
    
    # Gráfico principal
    show_backtest_chart(data, trades, equity, symbol)
    
    # Tabela de trades
    if trades:
        st.subheader("📋 Histórico de Trades")
        
        trades_df = pd.DataFrame(trades)
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
        trades_df = trades_df.sort_values('timestamp')
        
        # Formata para exibição
        display_df = trades_df.copy()
        if 'profit' in display_df.columns:
            display_df['profit'] = display_df['profit'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "")
        
        st.dataframe(display_df, use_container_width=True)

def show_backtest_chart(data, trades, equity, symbol):
    """Gráfico detalhado do backtest"""
    
    # Prepara dados
    df = data.copy()
    df['sma_20'] = df['Close'].rolling(window=20).mean()
    df['sma_50'] = df['Close'].rolling(window=50).mean()
    
    # Cria subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(f'{symbol} - Preço e Sinais', 'Curva de Equity'),
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3]
    )
    
    # Preço
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Preço',
            line=dict(color='white', width=1)
        ),
        row=1, col=1
    )
    
    # SMAs
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['sma_20'],
            mode='lines',
            name='SMA 20',
            line=dict(color='orange', width=1),
            opacity=0.7
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['sma_50'],
            mode='lines',
            name='SMA 50',
            line=dict(color='red', width=1),
            opacity=0.7
        ),
        row=1, col=1
    )
    
    # Sinais de compra e venda
    if trades:
        trades_df = pd.DataFrame(trades)
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
        
        buy_trades = trades_df[trades_df['action'] == 'BUY']
        sell_trades = trades_df[trades_df['action'] == 'SELL']
        
        if not buy_trades.empty:
            fig.add_trace(
                go.Scatter(
                    x=buy_trades['timestamp'],
                    y=buy_trades['price'],
                    mode='markers',
                    name='Compra',
                    marker=dict(
                        symbol='triangle-up',
                        size=10,
                        color='lime'
                    )
                ),
                row=1, col=1
            )
        
        if not sell_trades.empty:
            fig.add_trace(
                go.Scatter(
                    x=sell_trades['timestamp'],
                    y=sell_trades['price'],
                    mode='markers',
                    name='Venda',
                    marker=dict(
                        symbol='triangle-down',
                        size=10,
                        color='red'
                    )
                ),
                row=1, col=1
            )
    
    # Curva de equity
    if equity:
        equity_series = pd.Series(equity, index=df.index[:len(equity)])
        
        fig.add_trace(
            go.Scatter(
                x=equity_series.index,
                y=equity_series.values,
                mode='lines',
                name='Equity',
                line=dict(color='#00D4AA', width=2)
            ),
            row=2, col=1
        )
    
    fig.update_layout(
        height=800,
        title=f"📊 Análise Completa - {symbol}",
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_current_signal(signal):
    """Mostra sinal atual"""
    st.subheader("🔮 Sinal de Trading Atual")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏷️ Símbolo", signal['symbol'])
    
    with col2:
        st.metric("💲 Preço Atual", f"${signal['price']:.2f}")
    
    with col3:
        # Cor baseada no sinal
        if signal['signal'] == 'BUY':
            delta_color = "normal"
            emoji = "🟢"
        elif signal['signal'] == 'SELL':
            delta_color = "inverse"
            emoji = "🔴"
        else:
            delta_color = "off"
            emoji = "🟡"
        
        st.metric(
            "🎯 Sinal",
            f"{emoji} {signal['signal']}",
            delta=f"{signal['confidence']:.1%} confiança"
        )
    
    with col4:
        st.metric(
            "📅 Timestamp",
            signal['timestamp'].strftime('%H:%M')
        )
    
    # Alerta visual
    if signal['signal'] == 'BUY':
        st.success(f"🟢 **COMPRA RECOMENDADA** - Confiança: {signal['confidence']:.1%}")
    elif signal['signal'] == 'SELL':
        st.error(f"🔴 **VENDA RECOMENDADA** - Confiança: {signal['confidence']:.1%}")
    else:
        st.warning(f"🟡 **MANTER POSIÇÃO** - Aguardar melhor oportunidade")

def show_sample_data(symbol, period):
    """Mostra dados de exemplo"""
    st.subheader(f"📊 Dados de {symbol}")
    
    try:
        # Baixa dados de exemplo
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if not data.empty:
            # Gráfico simples
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name=f'{symbol} Close',
                line=dict(color='#00D4AA', width=2)
            ))
            
            fig.update_layout(
                title=f"💹 {symbol} - Últimos {period}",
                xaxis_title="Data",
                yaxis_title="Preço ($)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Info básica
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Pontos de Dados", len(data))
            with col2:
                st.metric("💲 Preço Atual", f"${data['Close'].iloc[-1]:.2f}")
            with col3:
                change = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0] * 100
                st.metric("📈 Mudança Total", f"{change:.2f}%")
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")

if __name__ == "__main__":
    main()
