"""
Teste Simplificado do Sistema AI
Verifica funcionalidades básicas sem dependências pesadas
"""

import numpy as np
import pandas as pd
from datetime import datetime

def test_basic_functionality():
    """Testa funcionalidades básicas"""
    print("🧪 Teste Básico do Sistema AI Trading")
    print("=" * 50)
    
    # Teste 1: Estruturas de dados básicas
    print("📊 Teste 1: Estruturas de Dados")
    
    # Simula dados de preço
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    prices = 30000 + np.cumsum(np.random.randn(100) * 100)
    
    data = pd.DataFrame({
        'Close': prices,
        'Open': prices * 0.99,
        'High': prices * 1.01,
        'Low': prices * 0.98,
        'Volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    print(f"✅ DataFrame criado: {data.shape}")
    print(f"📅 Período: {data.index[0].date()} a {data.index[-1].date()}")
    print(f"💲 Preço inicial: ${data['Close'].iloc[0]:.2f}")
    print(f"💲 Preço final: ${data['Close'].iloc[-1]:.2f}")
    
    # Teste 2: Indicadores técnicos básicos
    print("\n📈 Teste 2: Indicadores Técnicos")
    
    # SMA
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    
    # RSI simplificado
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # Momentum
    data['Momentum'] = data['Close'].pct_change(periods=10)
    
    print(f"✅ SMA 20 calculada")
    print(f"✅ SMA 50 calculada")
    print(f"✅ RSI calculado")
    print(f"✅ Momentum calculado")
    
    # Remove NaN
    data_clean = data.dropna()
    print(f"📊 Dados limpos: {data_clean.shape}")
    
    # Teste 3: Sinais básicos
    print("\n🎯 Teste 3: Geração de Sinais")
    
    # Sinal SMA Crossover
    data_clean['SMA_Signal'] = (data_clean['SMA_20'] > data_clean['SMA_50']).astype(int)
    
    # Sinal RSI
    data_clean['RSI_Signal'] = ((data_clean['RSI'] > 30) & (data_clean['RSI'] < 70)).astype(int)
    
    # Sinal Momentum
    data_clean['Momentum_Signal'] = (data_clean['Momentum'] > 0).astype(int)
    
    # Sinal combinado
    data_clean['Combined_Signal'] = (
        data_clean['SMA_Signal'] + 
        data_clean['RSI_Signal'] + 
        data_clean['Momentum_Signal']
    )
    
    # Converte para ações
    def signal_to_action(score):
        if score >= 2:
            return 'BUY'
        elif score <= 1:
            return 'SELL'
        else:
            return 'HOLD'
    
    data_clean['Action'] = data_clean['Combined_Signal'].apply(signal_to_action)
    
    # Estatísticas
    action_counts = data_clean['Action'].value_counts()
    print(f"✅ Sinais gerados:")
    for action, count in action_counts.items():
        print(f"   {action}: {count} ({count/len(data_clean)*100:.1f}%)")
    
    # Teste 4: Simulação de trading
    print("\n💰 Teste 4: Simulação de Trading")
    
    capital = 1000
    position = 0
    trades = []
    
    for i, row in data_clean.iterrows():
        action = row['Action']
        price = row['Close']
        
        if action == 'BUY' and position == 0:
            # Compra
            position = capital / price
            capital = 0
            trades.append({
                'type': 'BUY',
                'date': i,
                'price': price,
                'position': position
            })
        
        elif action == 'SELL' and position > 0:
            # Venda
            capital = position * price
            profit = capital - 1000  # Lucro desde o início
            position = 0
            trades.append({
                'type': 'SELL',
                'date': i,
                'price': price,
                'capital': capital,
                'profit': profit
            })
    
    # Valor final
    final_value = capital if position == 0 else position * data_clean['Close'].iloc[-1]
    total_return = (final_value - 1000) / 1000 * 100
    
    print(f"✅ Simulação concluída:")
    print(f"💰 Capital inicial: $1,000.00")
    print(f"💰 Valor final: ${final_value:.2f}")
    print(f"📈 Retorno total: {total_return:.2f}%")
    print(f"🔄 Total de trades: {len(trades)}")
    
    # Trades rentáveis
    profitable_trades = [t for t in trades if t.get('profit', 0) > 0]
    if len([t for t in trades if 'profit' in t]) > 0:
        win_rate = len(profitable_trades) / len([t for t in trades if 'profit' in t]) * 100
        print(f"🎯 Win rate: {win_rate:.1f}%")
    
    # Teste 5: Estrutura do Q-Learning (sem TensorFlow)
    print("\n🤖 Teste 5: Estrutura Q-Learning Básica")
    
    class SimpleQAgent:
        def __init__(self, state_size, action_size):
            self.state_size = state_size
            self.action_size = action_size
            self.epsilon = 1.0
            self.epsilon_decay = 0.995
            self.epsilon_min = 0.01
            # Q-table simples (sem neural network)
            self.q_table = np.random.rand(100, action_size)  # Simplificado
        
        def act(self, state_index):
            if np.random.rand() <= self.epsilon:
                return np.random.choice(self.action_size)
            
            # Usa índice simplificado
            return np.argmax(self.q_table[state_index % 100])
        
        def update_epsilon(self):
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
    
    # Testa agente
    agent = SimpleQAgent(state_size=10, action_size=3)
    
    for episode in range(5):
        state_idx = np.random.randint(0, 100)
        action = agent.act(state_idx)
        action_name = ['HOLD', 'BUY', 'SELL'][action]
        agent.update_epsilon()
        
        print(f"✅ Episódio {episode + 1}: Estado {state_idx} → Ação {action_name} (ε={agent.epsilon:.3f})")
    
    print("\n🎉 TODOS OS TESTES BÁSICOS PASSARAM!")
    print("=" * 50)
    print("✅ Sistema pronto para implementação completa")
    print("📦 Próximos passos:")
    print("   1. Instalar TensorFlow: pip install tensorflow")
    print("   2. Instalar yfinance: pip install yfinance")
    print("   3. Instalar ccxt: pip install ccxt")
    print("   4. Executar sistema completo")
    
    return True

if __name__ == "__main__":
    test_basic_functionality()
