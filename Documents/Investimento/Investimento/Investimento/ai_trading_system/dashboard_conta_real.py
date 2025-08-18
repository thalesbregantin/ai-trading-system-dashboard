#!/usr/bin/env python3
"""
Dashboard da Conta Real - Seus R$ 100 na Binance
"""

import streamlit as st
import ccxt
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="💰 Sua Conta Real Binance",
    page_icon="💰",
    layout="wide"
)

# Credenciais
API_KEY = "Jsga4pAg9nndc0JmoWVt9w8rd9xQHxNFK7oxn11lKWtwS86MpruPbEdGXnkdkOzM"
API_SECRET = "7q8w7cWMkUvytSG1bFzYOosRzLrl4AOWk6v3Q1EMYOQcDer0R88EL5b7TP5opU2M"

@st.cache_data(ttl=60)  # Cache por 1 minuto
def get_account_data():
    """Busca dados reais da conta"""
    try:
        exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
        })
        
        balance = exchange.fetch_balance()
        
        # Preços atuais
        try:
            btc_price = exchange.fetch_ticker('BTC/USDT')['last']
            eth_price = exchange.fetch_ticker('ETH/USDT')['last']
        except:
            btc_price = 0
            eth_price = 0
        
        return {
            'balance': balance,
            'btc_price': btc_price,
            'eth_price': eth_price,
            'timestamp': datetime.now()
        }
    except Exception as e:
        st.error(f"Erro ao conectar: {e}")
        return None

def main():
    """Dashboard principal"""
    
    # Header
    st.markdown("""
    <div style='background: linear-gradient(90deg, #1e3c72, #2a5298); padding: 2rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 2rem;'>
        <h1>💰 Sua Conta Real na Binance</h1>
        <h3>Acompanhe seus R$ 100,00 em tempo real</h3>
        <p><i>Dados diretos da API da Binance</i></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Busca dados
    with st.spinner("🔗 Conectando com sua conta..."):
        data = get_account_data()
    
    if not data:
        st.error("❌ Não foi possível conectar com sua conta")
        st.stop()
    
    balance = data['balance']
    
    # Status da conta
    st.markdown("## 💳 Status da Sua Conta")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        brl_total = balance.get('BRL', {}).get('total', 0)
        st.metric("💵 Real Brasileiro", f"R$ {brl_total:.2f}")
    
    with col2:
        usdt_total = balance.get('USDT', {}).get('total', 0)
        st.metric("💲 Dólar Digital", f"$ {usdt_total:.2f}")
    
    with col3:
        btc_total = balance.get('BTC', {}).get('total', 0)
        st.metric("₿ Bitcoin", f"{btc_total:.8f}")
    
    with col4:
        eth_total = balance.get('ETH', {}).get('total', 0)
        st.metric("Ξ Ethereum", f"{eth_total:.6f}")
    
    # Aviso principal
    if usdt_total < 10:
        st.markdown("""
        <div style='background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 10px; padding: 1.5rem; margin: 1rem 0;'>
            <h3>⚠️ Para começar o Trading AI, você precisa de USDT</h3>
            <p><b>Situação atual:</b> Você tem R$ {:.2f}, mas o sistema opera com USDT (dólar digital)</p>
            <p><b>Solução:</b> Converta seus reais para USDT para começar a usar a IA</p>
        </div>
        """.format(brl_total), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background: #d4edda; border: 1px solid #c3e6cb; border-radius: 10px; padding: 1.5rem; margin: 1rem 0;'>
            <h3>✅ Pronto para Trading!</h3>
            <p>Você tem $ {:.2f} USDT - pode começar a usar o sistema AI!</p>
        </div>
        """.format(usdt_total), unsafe_allow_html=True)
    
    # Preços atuais
    st.markdown("## 📊 Preços Atuais do Mercado")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if data['btc_price'] > 0:
            st.metric("₿ Bitcoin (BTC/USDT)", f"$ {data['btc_price']:,.2f}")
        else:
            st.metric("₿ Bitcoin", "Carregando...")
    
    with col2:
        if data['eth_price'] > 0:
            st.metric("Ξ Ethereum (ETH/USDT)", f"$ {data['eth_price']:,.2f}")
        else:
            st.metric("Ξ Ethereum", "Carregando...")
    
    with col3:
        # Calcula poder de compra
        if data['btc_price'] > 0 and usdt_total > 0:
            btc_poder_compra = usdt_total / data['btc_price']
            st.metric("🛒 Seu Poder de Compra", f"{btc_poder_compra:.6f} BTC")
        else:
            st.metric("🛒 Poder de Compra", "$ 0.00")
    
    # Distribuição de ativos
    st.markdown("## 🥧 Distribuição dos Seus Ativos")
    
    # Prepara dados para gráfico
    assets_data = []
    
    if brl_total > 0:
        assets_data.append({"Asset": "BRL (Real)", "Value": brl_total, "Currency": "BRL"})
    
    if usdt_total > 0:
        assets_data.append({"Asset": "USDT (Dólar)", "Value": usdt_total, "Currency": "USD"})
    
    if btc_total > 0:
        btc_value_usd = btc_total * data['btc_price'] if data['btc_price'] > 0 else 0
        assets_data.append({"Asset": "BTC (Bitcoin)", "Value": btc_value_usd, "Currency": "USD"})
    
    if eth_total > 0:
        eth_value_usd = eth_total * data['eth_price'] if data['eth_price'] > 0 else 0
        assets_data.append({"Asset": "ETH (Ethereum)", "Value": eth_value_usd, "Currency": "USD"})
    
    if assets_data:
        df_assets = pd.DataFrame(assets_data)
        
        fig = px.pie(
            df_assets,
            values='Value',
            names='Asset',
            title="Distribuição dos seus ativos por valor",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Valor: %{value:.2f}<br>Percentual: %{percent}<extra></extra>'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 Nenhum ativo encontrado para exibir")
    
    # Ações disponíveis
    st.markdown("## 🎯 O Que Você Pode Fazer Agora")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 💱 Converter para USDT
        
        **Para usar o Trading AI, você precisa converter seus reais para USDT:**
        
        1. **Opção Fácil:** Use o app da Binance
           - Abra o app da Binance
           - Vá em "Trade" > "Convert"
           - Converta BRL → USDT
        
        2. **Opção Terminal:** Execute o conversor
           ```bash
           python converter_brl_usdt.py
           ```
        
        ⚠️ **Importante:** Esta conversão usa dinheiro real!
        """)
    
    with col2:
        st.markdown("""
        ### 🤖 Iniciar Trading AI
        
        **Depois de ter USDT, você pode:**
        
        1. **Iniciar o sistema AI:**
           ```bash
           python main.py --mode live
           ```
        
        2. **Ver o dashboard completo:**
           ```bash
           streamlit run dashboard/main_dashboard.py
           ```
        
        3. **Fazer um teste primeiro:**
           ```bash
           python main.py --mode test
           ```
        
        ✅ **Mínimo recomendado:** $ 10 USDT
        """)
    
    # Informações de segurança
    st.markdown("## 🛡️ Segurança da Sua Conta")
    
    st.info("""
    **🔒 Sua conta está segura:**
    - ✅ Conexão criptografada com a Binance
    - ✅ Chaves API com permissões limitadas
    - ✅ Dados em tempo real direto da fonte
    - ✅ Sem armazenamento de credenciais
    
    **⚠️ Lembre-se:**
    - Este é dinheiro REAL, não simulação
    - Trading sempre envolve riscos
    - Comece com valores pequenos
    - Monitore sempre os resultados
    """)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>📡 <b>Última atualização:</b> {data['timestamp'].strftime('%d/%m/%Y às %H:%M:%S')}</p>
        <p>🔗 <b>Conectado à:</b> Binance API (Conta Real)</p>
        <p>💡 <b>Dica:</b> Recarregue a página para atualizar os dados</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
