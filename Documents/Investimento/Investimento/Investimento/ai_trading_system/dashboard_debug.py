#!/usr/bin/env python3
"""
Dashboard Simplificado para Debug
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

def main():
    """Dashboard principal simplificado"""
    st.set_page_config(
        page_title="🤖 AI Trading Dashboard - Debug",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 AI Trading System - Debug Version")
    st.markdown("---")
    
    try:
        # Teste 1: Dados básicos
        st.header("📊 Teste 1: Dados Básicos")
        
        # Cria dados simulados simples
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        correlations = 0.5 + 0.3 * np.sin(np.arange(len(dates)) * 2 * np.pi / 30) + 0.1 * np.random.randn(len(dates))
        correlations = np.clip(correlations, 0, 1)
        
        correlation_data = pd.DataFrame({
            'date': dates,
            'correlation': correlations
        })
        
        st.success("✅ Dados de correlação criados com sucesso")
        st.write(f"📊 Dados: {len(correlation_data)} registros")
        
        # Teste 2: Gráfico básico
        st.header("📈 Teste 2: Gráfico de Correlação")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=correlation_data['date'],
            y=correlation_data['correlation'],
            mode='lines',
            name='Market Correlation',
            line=dict(color='#FF6B6B', width=2)
        ))
        
        fig.update_layout(
            title="Market Correlation Test",
            xaxis_title="Date",
            yaxis_title="Correlation",
            template='plotly_dark',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.success("✅ Gráfico criado com sucesso")
        
        # Teste 3: Métricas
        st.header("📋 Teste 3: Métricas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Portfolio Value", "$1,000.00", "0%")
        
        with col2:
            st.metric("📈 Daily Return", "+0.5%", "0.1%")
        
        with col3:
            st.metric("🎯 Win Rate", "65%", "5%")
        
        with col4:
            st.metric("📊 Total Trades", "12", "2")
        
        st.success("✅ Métricas exibidas com sucesso")
        
        # Teste 4: Dados de trading simulados
        st.header("🔄 Teste 4: Dados de Trading")
        
        # Criar dados de trades simulados
        trade_data = pd.DataFrame({
            'symbol': ['BTCUSDT', 'ETHUSDT', 'BTCUSDT', 'ETHUSDT'] * 3,
            'side': ['BUY', 'SELL', 'BUY', 'SELL'] * 3,
            'quantity': np.random.uniform(0.01, 0.1, 12),
            'price': np.random.uniform(25000, 75000, 12),
            'value': np.random.uniform(100, 1000, 12),
            'fee': np.random.uniform(0.1, 2.0, 12),
            'entry_date': pd.date_range('2024-01-01', periods=12, freq='D'),
            'exit_date': pd.date_range('2024-01-02', periods=12, freq='D'),
        })
        
        # Adicionar colunas calculadas
        trade_data['pnl_pct'] = np.random.normal(0.5, 2.0, 12)
        trade_data['duration_days'] = (trade_data['exit_date'] - trade_data['entry_date']).dt.days
        
        st.dataframe(trade_data.head())
        st.success("✅ Dados de trading criados com sucesso")
        
        # Teste 5: Estratégia de comparação
        st.header("⚖️ Teste 5: Comparação de Estratégias")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🎯 Single-Asset Strategy**")
            total_return = trade_data['pnl_pct'].sum()
            win_rate = (trade_data['pnl_pct'] > 0).mean() * 100
            avg_duration = trade_data['duration_days'].mean()
            
            st.metric("Total Return", f"{total_return:.1f}%")
            st.metric("Win Rate", f"{win_rate:.1f}%")
            st.metric("Avg Duration", f"{avg_duration:.1f} days")
            st.metric("Total Trades", len(trade_data))
        
        with col2:
            st.write("**🔄 Multi-Asset Strategy**")
            # Simular estratégia multi-asset
            multi_return = total_return * 1.2
            multi_win_rate = win_rate * 1.1
            multi_duration = avg_duration * 0.9
            
            st.metric("Total Return", f"{multi_return:.1f}%")
            st.metric("Win Rate", f"{multi_win_rate:.1f}%")
            st.metric("Avg Duration", f"{multi_duration:.1f} days")
            st.metric("Total Trades", len(trade_data))
        
        st.success("✅ Comparação de estratégias criada com sucesso")
        
        # Status final
        st.markdown("---")
        st.success("🎉 Todos os testes passaram! Dashboard funcionando corretamente.")
        
    except Exception as e:
        st.error(f"❌ Erro detectado: {e}")
        st.write("📋 Detalhes do erro:")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
