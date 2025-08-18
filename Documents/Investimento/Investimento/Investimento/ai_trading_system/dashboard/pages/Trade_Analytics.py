import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Adicionar pasta src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# ====================================
# CONFIGURAÇÃO DA PÁGINA
# ====================================

st.set_page_config(
    page_title="Trade Analytics - Crypto Momentum",
    page_icon="📊",
    layout="wide"
)

# ====================================
# CARREGAMENTO DE DADOS
# ====================================

@st.cache_data
def load_trades_data():
    """Carrega dados de trades"""
    try:
        # Caminho correto para data/ a partir de dashboard/pages/
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        trades_file = os.path.join(data_path, 'trades_momentum_optimized.csv')
        
        if not os.path.exists(trades_file):
            st.error(f"Arquivo não encontrado: {trades_file}")
            return None
            
        trades_data = pd.read_csv(trades_file)
        
        # Verifica e corrige colunas de data
        if 'entry_date' in trades_data.columns:
            trades_data['entry_date'] = pd.to_datetime(trades_data['entry_date'])
        elif 'date' in trades_data.columns:
            trades_data['entry_date'] = pd.to_datetime(trades_data['date'])
        else:
            st.warning("Coluna de data não encontrada nos dados de trades")
            
        if 'exit_date' not in trades_data.columns:
            trades_data['exit_date'] = trades_data['entry_date']
        else:
            trades_data['exit_date'] = pd.to_datetime(trades_data['exit_date'])
            
        # Adiciona pnl_pct se não existir
        if 'pnl_pct' not in trades_data.columns:
            if 'value' in trades_data.columns and 'fee' in trades_data.columns:
                # Estimativa simples de PnL
                trades_data['pnl_pct'] = ((trades_data['value'] - trades_data['fee']) / trades_data['value'] * 100).fillna(0)
            else:
                trades_data['pnl_pct'] = 0
        
        # Adiciona P&L absoluto em USD para tamanhos de bolha, se não existir
        if 'abs_pnl_usd' not in trades_data.columns:
            if 'pnl_pct' in trades_data.columns and 'cost' in trades_data.columns:
                trades_data['abs_pnl_usd'] = (trades_data['cost'] * (trades_data['pnl_pct'].abs() / 100.0)).fillna(0)
            else:
                trades_data['abs_pnl_usd'] = 0.0
                
        return trades_data
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

# ====================================
# PÁGINA PRINCIPAL
# ====================================

def main():
    st.title("📊 Trade Analytics")
    st.markdown("*Detailed analysis of individual trades*")
    
    # Carrega dados
    trades_data = load_trades_data()
    
    if trades_data is None:
        st.error("Não foi possível carregar os dados de trades")
        return
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtro por ativo
        symbols = ['All'] + sorted(trades_data['symbol'].unique().tolist())
        selected_symbol = st.selectbox("Select Asset:", symbols)
    
    with col2:
        # Filtro por resultado
        outcome_filter = st.selectbox("Trade Outcome:", ['All', 'Profitable', 'Losing'])
    
    with col3:
        # Filtro por duração
        duration_filter = st.selectbox("Duration:", ['All', '<30 days', '30-60 days', '>60 days'])
    
    # Aplica filtros
    filtered_trades = trades_data.copy()
    
    if selected_symbol != 'All':
        filtered_trades = filtered_trades[filtered_trades['symbol'] == selected_symbol]
    
    if outcome_filter == 'Profitable':
        filtered_trades = filtered_trades[filtered_trades['pnl_pct'] > 0]
    elif outcome_filter == 'Losing':
        filtered_trades = filtered_trades[filtered_trades['pnl_pct'] < 0]
    
    if duration_filter == '<30 days':
        filtered_trades = filtered_trades[filtered_trades['duration_days'] < 30]
    elif duration_filter == '30-60 days':
        filtered_trades = filtered_trades[(filtered_trades['duration_days'] >= 30) & (filtered_trades['duration_days'] <= 60)]
    elif duration_filter == '>60 days':
        filtered_trades = filtered_trades[filtered_trades['duration_days'] > 60]
    
    # Métricas dos trades filtrados
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_trades = len(filtered_trades)
        st.metric("📊 Total Trades", total_trades)
    
    with col2:
        if len(filtered_trades) > 0:
            win_rate = (filtered_trades['pnl_pct'] > 0).mean() * 100
            st.metric("🎯 Win Rate", f"{win_rate:.1f}%")
        else:
            st.metric("🎯 Win Rate", "0%")
    
    with col3:
        if len(filtered_trades) > 0:
            avg_return = filtered_trades['pnl_pct'].mean()
            st.metric("📈 Avg Return", f"{avg_return:.2f}%")
        else:
            st.metric("📈 Avg Return", "0%")
    
    with col4:
        if len(filtered_trades) > 0:
            avg_duration = filtered_trades['duration_days'].mean()
            st.metric("⏱️ Avg Duration", f"{avg_duration:.1f} days")
        else:
            st.metric("⏱️ Avg Duration", "0 days")
    
    if len(filtered_trades) == 0:
        st.warning("No trades match the selected filters.")
        return
    
    # Gráficos
    st.markdown("---")
    
    # Scatter plot: Return vs Duration
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.scatter(
            filtered_trades,
            x='duration_days',
            y='pnl_pct',
            color='pnl_pct',
            size='abs_pnl_usd',
            hover_data=['symbol', 'entry_date'],
            title="📊 Return vs Duration",
            color_continuous_scale='RdYlGn',
            template='plotly_dark'
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="white")
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribuição de retornos
        fig = px.histogram(
            filtered_trades,
            x='pnl_pct',
            nbins=20,
            title="📊 Return Distribution",
            template='plotly_dark'
        )
        
        fig.add_vline(x=0, line_dash="dash", line_color="white")
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Timeline dos trades
    st.markdown("---")
    st.subheader("📅 Trades Timeline")
    
    # Prepara dados para timeline
    timeline_data = []
    for _, trade in filtered_trades.iterrows():
        timeline_data.append({
            'symbol': trade['symbol'],
            'entry_date': trade['entry_date'],
            'exit_date': trade['exit_date'],
            'pnl_pct': trade['pnl_pct'],
            'duration': trade['duration_days']
        })
    
    if timeline_data:
        timeline_df = pd.DataFrame(timeline_data)
        
        fig = go.Figure()
        
        for i, trade in timeline_df.iterrows():
            color = 'green' if trade['pnl_pct'] > 0 else 'red'
            
            fig.add_trace(go.Scatter(
                x=[trade['entry_date'], trade['exit_date']],
                y=[trade['symbol'], trade['symbol']],
                mode='lines+markers',
                line=dict(color=color, width=4),
                marker=dict(size=8, color=color),
                name=f"{trade['symbol']} ({trade['pnl_pct']:.1f}%)",
                hovertemplate=f"<b>{trade['symbol']}</b><br>Entry: {trade['entry_date']:%Y-%m-%d}<br>Exit: {trade['exit_date']:%Y-%m-%d}<br>Return: {trade['pnl_pct']:.2f}%<br>Duration: {trade['duration']:.0f} days<extra></extra>"
            ))
        
        fig.update_layout(
            title="📅 Trades Timeline",
            xaxis_title="Date",
            yaxis_title="Asset",
            template='plotly_dark',
            height=600,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada
    st.markdown("---")
    st.subheader("📋 Detailed Trades Table")
    
    # Configura colunas para exibição
    display_columns = ['symbol', 'entry_date', 'exit_date', 'duration_days', 'pnl_pct', 'abs_pnl_usd']
    
    # Formatação da tabela
    styled_df = filtered_trades[display_columns].copy()
    styled_df['entry_date'] = styled_df['entry_date'].dt.strftime('%Y-%m-%d')
    styled_df['exit_date'] = styled_df['exit_date'].dt.strftime('%Y-%m-%d')
    styled_df['pnl_pct'] = styled_df['pnl_pct'].round(2)
    styled_df['abs_pnl_usd'] = styled_df['abs_pnl_usd'].round(2)
    
    # Renomeia colunas
    styled_df.columns = ['Symbol', 'Entry Date', 'Exit Date', 'Duration (days)', 'Return (%)', 'P&L ($)']
    
    # Exibe tabela com formatação condicional
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv = styled_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Trades Data",
        data=csv,
        file_name=f"trades_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
