import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime
import sys
import os

# ====================================
# CONFIGURAÇÃO DA PÁGINA
# ====================================

st.set_page_config(
    page_title="Risk Analysis - Crypto Momentum",
    page_icon="⚠️",
    layout="wide"
)

# ====================================
# CARREGAMENTO DE DADOS
# ====================================

@st.cache_data
def load_risk_data():
    """Carrega dados para análise de risco"""
    try:
        # Caminho correto para data/ a partir de dashboard/pages/
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        
        equity_file = os.path.join(data_path, 'equity_momentum_optimized.csv')
        trades_file = os.path.join(data_path, 'trades_momentum_optimized.csv')
        
        if not os.path.exists(equity_file):
            st.error(f"Arquivo de equity não encontrado: {equity_file}")
            return None, None
            
        if not os.path.exists(trades_file):
            st.error(f"Arquivo de trades não encontrado: {trades_file}")
            return None, None
        
        equity_data = pd.read_csv(equity_file)
        trades_data = pd.read_csv(trades_file)
        
        equity_data['date'] = pd.to_datetime(equity_data['date'])
        
        # Corrige colunas de data nos trades
        if 'entry_date' in trades_data.columns:
            trades_data['entry_date'] = pd.to_datetime(trades_data['entry_date'])
        elif 'date' in trades_data.columns:
            trades_data['entry_date'] = pd.to_datetime(trades_data['date'])
            
        if 'exit_date' not in trades_data.columns:
            trades_data['exit_date'] = trades_data['entry_date']
        else:
            trades_data['exit_date'] = pd.to_datetime(trades_data['exit_date'])
        
        return equity_data, trades_data
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None, None

def calculate_risk_metrics(equity_data):
    """Calcula métricas de risco detalhadas"""
    if equity_data is None or len(equity_data) == 0:
        return {}
    
    # Usa 'equity' se existir, senão 'portfolio_value'
    value_col = 'equity' if 'equity' in equity_data.columns else 'portfolio_value'
    
    if value_col not in equity_data.columns:
        st.error(f"Coluna de valor não encontrada. Colunas disponíveis: {list(equity_data.columns)}")
        return {}
    
    equity_values = equity_data[value_col].values
    returns = np.diff(equity_values) / equity_values[:-1]
    
    if len(returns) == 0:
        return {}
    
    # Value at Risk (VaR)
    var_95 = np.percentile(returns, 5) * 100 if len(returns) > 0 else 0
    var_99 = np.percentile(returns, 1) * 100 if len(returns) > 0 else 0
    
    # Conditional VaR (Expected Shortfall)
    returns_5pct = returns[returns <= np.percentile(returns, 5)]
    returns_1pct = returns[returns <= np.percentile(returns, 1)]
    
    cvar_95 = returns_5pct.mean() * 100 if len(returns_5pct) > 0 else 0
    cvar_99 = returns_1pct.mean() * 100 if len(returns_1pct) > 0 else 0
    
    # Maximum Drawdown
    cumulative = equity_values / np.maximum.accumulate(equity_values)
    drawdowns = 1 - cumulative
    max_drawdown = np.max(drawdowns) * 100 if len(drawdowns) > 0 else 0
    
    # Drawdown duration
    drawdown_periods = []
    in_drawdown = False
    start_dd = 0
    
    for i, dd in enumerate(drawdowns):
        if dd > 0 and not in_drawdown:
            in_drawdown = True
            start_dd = i
        elif dd == 0 and in_drawdown:
            in_drawdown = False
            drawdown_periods.append(i - start_dd)
    
    avg_drawdown_duration = np.mean(drawdown_periods) if drawdown_periods else 0
    max_drawdown_duration = np.max(drawdown_periods) if drawdown_periods else 0
    
    # Volatility metrics
    volatility_daily = np.std(returns) * 100
    volatility_annual = volatility_daily * np.sqrt(252)
    
    # Downside deviation
    negative_returns = returns[returns < 0]
    downside_deviation = np.std(negative_returns) * np.sqrt(252) * 100 if len(negative_returns) > 0 else 0
    
    # Sortino Ratio
    mean_return = np.mean(returns) * 252
    sortino_ratio = mean_return / (downside_deviation / 100) if downside_deviation > 0 else 0
    
    # Beta vs Bitcoin (proxy for market)
    # Assumindo que o primeiro ativo é sempre Bitcoin ou um proxy de mercado
    market_beta = 1.0  # Simplificado para este exemplo
    
    return {
        'var_95': var_95,
        'var_99': var_99,
        'cvar_95': cvar_95,
        'cvar_99': cvar_99,
        'max_drawdown': max_drawdown,
        'avg_drawdown_duration': avg_drawdown_duration,
        'max_drawdown_duration': max_drawdown_duration,
        'volatility_daily': volatility_daily,
        'volatility_annual': volatility_annual,
        'downside_deviation': downside_deviation,
        'sortino_ratio': sortino_ratio,
        'market_beta': market_beta,
        'returns': returns,
        'drawdowns': drawdowns
    }

# ====================================
# PÁGINA PRINCIPAL
# ====================================

def main():
    st.title("⚠️ Risk Analysis")
    st.markdown("*Comprehensive risk assessment of the crypto momentum strategy*")
    
    # Carrega dados
    equity_data, trades_data = load_risk_data()
    
    if equity_data is None or trades_data is None:
        st.error("Não foi possível carregar os dados")
        return
    
    # Calcula métricas de risco
    risk_metrics = calculate_risk_metrics(equity_data)
    
    # Métricas principais de risco
    st.markdown("---")
    st.subheader("🎯 Key Risk Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📉 Max Drawdown",
            f"{risk_metrics['max_drawdown']:.2f}%",
            help="Maximum peak-to-trough decline"
        )
    
    with col2:
        st.metric(
            "📊 VaR (95%)",
            f"{risk_metrics['var_95']:.2f}%",
            help="Value at Risk - 95% confidence level"
        )
    
    with col3:
        st.metric(
            "📈 Annual Volatility",
            f"{risk_metrics['volatility_annual']:.2f}%",
            help="Annualized standard deviation of returns"
        )
    
    with col4:
        st.metric(
            "⬇️ Sortino Ratio",
            f"{risk_metrics['sortino_ratio']:.2f}",
            help="Risk-adjusted return using downside deviation"
        )
    
    # Gráficos de risco
    st.markdown("---")
    
    # Drawdown Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📉 Drawdown Analysis")
        
        fig = go.Figure()
        
        # Drawdown underwater chart
        fig.add_trace(go.Scatter(
            x=equity_data['date'],
            y=-risk_metrics['drawdowns'] * 100,
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.3)',
            line=dict(color='red'),
            name='Drawdown',
            hovertemplate='<b>Date:</b> %{x}<br><b>Drawdown:</b> %{y:.2f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title="Underwater Equity Curve",
            xaxis_title="Date",
            yaxis_title="Drawdown (%)",
            template='plotly_dark',
            height=400
        )
        
        fig.update_yaxis(range=[-risk_metrics['max_drawdown'] * 1.1, 5])
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Return Distribution")
        
        returns_pct = risk_metrics['returns'] * 100
        
        fig = go.Figure()
        
        # Histogram of returns
        fig.add_trace(go.Histogram(
            x=returns_pct,
            nbinsx=30,
            name='Daily Returns',
            marker_color='lightblue',
            opacity=0.7
        ))
        
        # VaR lines
        fig.add_vline(x=risk_metrics['var_95'], line_dash="dash", line_color="red", 
                     annotation_text="VaR 95%")
        fig.add_vline(x=risk_metrics['var_99'], line_dash="dash", line_color="darkred", 
                     annotation_text="VaR 99%")
        
        fig.update_layout(
            title="Daily Returns Distribution",
            xaxis_title="Return (%)",
            yaxis_title="Frequency",
            template='plotly_dark',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de métricas detalhadas
    st.markdown("---")
    st.subheader("📋 Detailed Risk Metrics")
    
    # Cria tabela de métricas
    metrics_data = {
        'Metric': [
            'Value at Risk (95%)',
            'Value at Risk (99%)',
            'Conditional VaR (95%)',
            'Conditional VaR (99%)',
            'Maximum Drawdown',
            'Avg Drawdown Duration',
            'Max Drawdown Duration',
            'Daily Volatility',
            'Annual Volatility',
            'Downside Deviation',
            'Sortino Ratio',
            'Market Beta'
        ],
        'Value': [
            f"{risk_metrics['var_95']:.2f}%",
            f"{risk_metrics['var_99']:.2f}%",
            f"{risk_metrics['cvar_95']:.2f}%",
            f"{risk_metrics['cvar_99']:.2f}%",
            f"{risk_metrics['max_drawdown']:.2f}%",
            f"{risk_metrics['avg_drawdown_duration']:.1f} days",
            f"{risk_metrics['max_drawdown_duration']:.0f} days",
            f"{risk_metrics['volatility_daily']:.2f}%",
            f"{risk_metrics['volatility_annual']:.2f}%",
            f"{risk_metrics['downside_deviation']:.2f}%",
            f"{risk_metrics['sortino_ratio']:.2f}",
            f"{risk_metrics['market_beta']:.2f}"
        ],
        'Interpretation': [
            "Daily loss not exceeded 95% of the time",
            "Daily loss not exceeded 99% of the time",
            "Average loss when VaR 95% is exceeded",
            "Average loss when VaR 99% is exceeded",
            "Largest peak-to-trough decline",
            "Average time to recover from drawdowns",
            "Longest drawdown period",
            "Standard deviation of daily returns",
            "Annualized volatility measure",
            "Volatility of negative returns only",
            "Risk-adjusted return (downside focus)",
            "Correlation with market movements"
        ]
    }
    
    metrics_df = pd.DataFrame(metrics_data)
    
    st.dataframe(
        metrics_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Risk Assessment
    st.markdown("---")
    st.subheader("🎯 Risk Assessment")
    
    # Risk scoring
    risk_score = 0
    risk_factors = []
    
    # Avalia fatores de risco
    if risk_metrics['max_drawdown'] > 50:
        risk_score += 3
        risk_factors.append("⚠️ High maximum drawdown (>50%)")
    elif risk_metrics['max_drawdown'] > 30:
        risk_score += 2
        risk_factors.append("⚠️ Moderate maximum drawdown (30-50%)")
    elif risk_metrics['max_drawdown'] > 20:
        risk_score += 1
        risk_factors.append("⚠️ Elevated maximum drawdown (20-30%)")
    
    if risk_metrics['volatility_annual'] > 100:
        risk_score += 2
        risk_factors.append("⚠️ Very high volatility (>100%)")
    elif risk_metrics['volatility_annual'] > 50:
        risk_score += 1
        risk_factors.append("⚠️ High volatility (50-100%)")
    
    if risk_metrics['sortino_ratio'] < 1:
        risk_score += 1
        risk_factors.append("⚠️ Low risk-adjusted returns (Sortino < 1)")
    
    if abs(risk_metrics['var_95']) > 10:
        risk_score += 1
        risk_factors.append("⚠️ High daily VaR (>10%)")
    
    # Determina nível de risco
    if risk_score <= 2:
        risk_level = "🟢 LOW RISK"
        risk_color = "green"
    elif risk_score <= 4:
        risk_level = "🟡 MEDIUM RISK"
        risk_color = "orange"
    elif risk_score <= 6:
        risk_level = "🔴 HIGH RISK"
        risk_color = "red"
    else:
        risk_level = "🔴 VERY HIGH RISK"
        risk_color = "darkred"
    
    # Exibe assessment
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; border: 2px solid {risk_color}; border-radius: 10px; background-color: rgba(0,0,0,0.1)'>
            <h3 style='color: {risk_color}'>{risk_level}</h3>
            <p>Risk Score: {risk_score}/8</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.write("**Risk Factors Identified:**")
        if risk_factors:
            for factor in risk_factors:
                st.write(f"• {factor}")
        else:
            st.write("• ✅ No significant risk factors identified")
        
        st.write("**Recommendations:**")
        if risk_score <= 2:
            st.write("• ✅ Strategy shows acceptable risk levels")
            st.write("• ✅ Continue monitoring with current parameters")
        elif risk_score <= 4:
            st.write("• ⚠️ Consider position size reduction")
            st.write("• ⚠️ Implement stricter stop losses")
        else:
            st.write("• 🔴 Review strategy parameters")
            st.write("• 🔴 Consider significant position size reduction")
            st.write("• 🔴 Implement additional risk controls")

if __name__ == "__main__":
    main()
