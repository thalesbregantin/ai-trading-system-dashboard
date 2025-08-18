"""
Integrador AI Trading com Sistema Existente
Combina Deep Q-Learning com estratégias de momentum
"""

import pandas as pd
import numpy as np
from .ai_trader_dqn import AITrader, train_ai_trader, backtest_ai_trader, integrate_with_momentum_strategy
import yfinance as yf
from datetime import datetime, timedelta

class HybridTradingSystem:
    """
    Sistema híbrido que combina:
    1. AI Trader (Deep Q-Learning)
    2. Estratégia de Momentum
    3. Indicadores Técnicos
    """
    
    def __init__(self, symbol='BTC-USD', ai_weight=0.6, momentum_weight=0.4):
        self.symbol = symbol
        self.ai_weight = ai_weight
        self.momentum_weight = momentum_weight
        self.ai_trader = None
        self.trained = False
        
    def download_data(self, period='1y'):
        """Download dados históricos com fallback simples"""
        print(f"📊 Baixando dados para {self.symbol}...")
        
        ticker = yf.Ticker(self.symbol)
        data = ticker.history(period=period)
        
        if data.empty and self.symbol.endswith('-USDT'):
            alt = self.symbol.replace('-USDT', '-USD')
            ticker = yf.Ticker(alt)
            data = ticker.history(period=period)
        
        if data.empty:
            raise ValueError(f"Não foi possível baixar dados para {self.symbol}")
        
        print(f"✅ {len(data)} pontos de dados baixados")
        return data
    
    def prepare_features(self, data):
        """Prepara features técnicas"""
        df = data.copy()
        
        # Indicadores básicos
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        df['sma_50'] = df['Close'].rolling(window=50).mean()
        df['rsi'] = self.calculate_rsi(df['Close'])
        df['momentum'] = df['Close'].pct_change(periods=10)
        df['volatility'] = df['Close'].rolling(window=20).std()
        
        # Sinais
        df['sma_signal'] = (df['sma_20'] > df['sma_50']).astype(int)
        df['momentum_signal'] = (df['momentum'] > 0).astype(int)
        df['rsi_signal'] = ((df['rsi'] > 30) & (df['rsi'] < 70)).astype(int)
        
        return df.dropna()
    
    def calculate_rsi(self, prices, period=14):
        """Calcula RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def train_hybrid_system(self, data, episodes=20, initial_capital=1000):
        """Treina o sistema híbrido"""
        print("🧠 Treinando Sistema Híbrido...")
        
        # Prepara dados
        df = self.prepare_features(data)
        prices = df['Close'].values
        
        # Treina AI Trader
        print("🤖 Treinando AI Trader...")
        self.ai_trader, profits = train_ai_trader(prices, episodes=episodes, initial_capital=initial_capital)
        
        self.trained = True
        print("✅ Sistema híbrido treinado!")
        
        return profits
    
    def generate_signal(self, data, current_idx):
        """
        Gera sinal combinado:
        - AI Trader: 60% peso
        - Momentum: 40% peso
        """
        if not self.trained:
            raise ValueError("Sistema precisa ser treinado primeiro!")
        
        df = self.prepare_features(data)
        
        if current_idx >= len(df):
            return 0  # Hold
        
        # Sinal AI
        from .ai_trader_dqn import create_state_with_indicators, compute_indicators
        prices = df['Close'].values
        rsi_series, mom_series = compute_indicators(prices)
        state = create_state_with_indicators(prices, current_idx, 10, rsi_series, mom_series)
        ai_action = self.ai_trader.act(state)
        
        # Sinal Momentum
        row = df.iloc[current_idx]
        momentum_score = 0
        
        # SMA Crossover
        if row['sma_signal']:
            momentum_score += 1
        
        # Momentum
        if row['momentum_signal']:
            momentum_score += 1
        
        # RSI
        if row['rsi_signal']:
            momentum_score += 1
        
        # Converte momentum score para ação (ajustado para reduzir SELL excessivo)
        # momentum_score pode ir de 0 a 3 (sma, momentum, rsi)
        if momentum_score >= 2:
            momentum_action = 1  # BUY forte
        elif momentum_score == 0:
            momentum_action = 2  # SELL somente se zero sinais positivos
        else:
            momentum_action = 0  # HOLD quando neutro
        
        # Combina sinais
        ai_vote = ai_action
        momentum_vote = momentum_action
        
        # Voto ponderado
        if ai_vote == momentum_vote:
            return ai_vote  # Consenso
        
        # Conflito - usa pesos
        if ai_vote == 1 and self.ai_weight > 0.5:
            return 1  # AI quer comprar e tem peso maior
        elif momentum_vote == 1 and self.momentum_weight > 0.5:
            return 1  # Momentum quer comprar e tem peso maior
        elif ai_vote == 2 and self.ai_weight > 0.5:
            return 2  # AI quer vender e tem peso maior
        elif momentum_vote == 2 and self.momentum_weight > 0.5:
            return 2  # Momentum quer vender e tem peso maior
        else:
            return 0  # Hold em caso de empate
    
    def backtest_hybrid(self, data, initial_capital=1000):
        """Backtest do sistema híbrido"""
        print("📈 Executando Backtest Híbrido...")
        
        df = self.prepare_features(data)
        capital = initial_capital
        position = 0
        trades = []
        equity_curve = [capital]
        
        for i in range(50, len(df) - 1):  # Deixa margem para indicadores
            signal = self.generate_signal(data, i)
            current_price = df.iloc[i]['Close']
            
            action_taken = None
            
            # Buy Signal
            if signal == 1 and position == 0:
                position = capital / current_price
                capital = 0
                action_taken = 'BUY'
                
                trades.append({
                    'timestamp': df.index[i],
                    'action': 'BUY',
                    'price': current_price,
                    'position': position
                })
            
            # Sell Signal
            elif signal == 2 and position > 0:
                capital = position * current_price
                profit = capital - initial_capital
                position = 0
                action_taken = 'SELL'
                
                trades.append({
                    'timestamp': df.index[i],
                    'action': 'SELL',
                    'price': current_price,
                    'capital': capital,
                    'profit': profit
                })
            
            # Atualiza equity
            if position > 0:
                current_value = position * current_price
            else:
                current_value = capital
            
            equity_curve.append(current_value)
            
            if action_taken:
                print(f"📅 {df.index[i].strftime('%Y-%m-%d')} | {action_taken} | ${current_price:.2f}")
        
        # Métricas finais
        final_value = equity_curve[-1]
        total_return = (final_value - initial_capital) / initial_capital * 100
        
        equity_series = pd.Series(equity_curve, index=df.index[:len(equity_curve)])
        returns = equity_series.pct_change().dropna()
        
        metrics = {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'num_trades': len(trades),
            'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
            'max_drawdown': self.calculate_max_drawdown(equity_series),
            'win_rate': self.calculate_win_rate(trades)
        }
        
        return trades, metrics, equity_curve
    
    def calculate_max_drawdown(self, equity_series):
        """Calcula máximo drawdown"""
        rolling_max = equity_series.expanding().max()
        drawdown = (equity_series - rolling_max) / rolling_max
        return drawdown.min() * 100
    
    def calculate_win_rate(self, trades):
        """Calcula win rate"""
        profitable_trades = [t for t in trades if t.get('profit', 0) > 0]
        total_trades = len([t for t in trades if 'profit' in t])
        
        if total_trades == 0:
            return 0
        
        return len(profitable_trades) / total_trades * 100
    
    def real_time_signal(self, symbol=None):
        """Gera sinal em tempo real"""
        if symbol:
            self.symbol = symbol
        
        # Baixa dados recentes
        data = self.download_data(period='3mo')
        
        # Gera sinal para o último ponto
        signal = self.generate_signal(data, len(data) - 1)
        
        current_price = data['Close'].iloc[-1]
        timestamp = data.index[-1]
        
        signal_name = ['HOLD', 'BUY', 'SELL'][signal]
        
        result = {
            'timestamp': timestamp,
            'symbol': self.symbol,
            'price': current_price,
            'signal': signal_name,
            'confidence': self.ai_weight if signal in [1, 2] else 0.5
        }
        
        return result
    
    def save_model(self, filename):
        """Salva modelo treinado"""
        if self.ai_trader:
            self.ai_trader.model.save_weights(f"{filename}_ai_model.h5")
            print(f"💾 Modelo híbrido salvo: {filename}")
    
    def load_model(self, filename):
        """Carrega modelo treinado"""
        from .ai_trader_dqn import load_ai_model
        self.ai_trader = load_ai_model(9, f"{filename}_ai_model.h5")  # state_size = 9
        self.trained = True
        print(f"📂 Modelo híbrido carregado: {filename}")

def run_hybrid_analysis(symbol='BTC-USD'):
    """
    Executa análise completa do sistema híbrido
    """
    print(f"🚀 Análise Híbrida: {symbol}")
    print("=" * 50)
    
    # Inicializa sistema
    hybrid = HybridTradingSystem(symbol)
    
    # Baixa dados
    data = hybrid.download_data(period='2y')
    
    # Treina sistema
    profits = hybrid.train_hybrid_system(data, episodes=15)
    
    # Backtest
    trades, metrics, equity = hybrid.backtest_hybrid(data)
    
    # Resultados
    print("\n📊 RESULTADOS FINAIS:")
    print("=" * 30)
    print(f"💰 Retorno Total: {metrics['total_return']:.2f}%")
    print(f"📈 Trades: {metrics['num_trades']}")
    print(f"🎯 Win Rate: {metrics['win_rate']:.1f}%")
    print(f"📊 Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
    print(f"📉 Max Drawdown: {metrics['max_drawdown']:.2f}%")
    
    # Sinal atual
    current_signal = hybrid.real_time_signal()
    print(f"\n🔮 Sinal Atual:")
    print(f"📅 {current_signal['timestamp'].strftime('%Y-%m-%d %H:%M')}")
    print(f"💲 Preço: ${current_signal['price']:.2f}")
    print(f"🎯 Sinal: {current_signal['signal']}")
    print(f"🔮 Confiança: {current_signal['confidence']:.1%}")
    
    # Salva modelo
    hybrid.save_model(f"hybrid_model_{symbol.replace('-', '_')}")
    
    return hybrid, trades, metrics

def train_hybrid_system(data, episodes=10, window_size=10, initial_capital=None):
    """Função externa simplificada para treinar AI com suporte a capital."""
    try:
        # Garantir que data é um array numpy
        if isinstance(data, pd.DataFrame):
            if 'close' in data.columns:
                closing = data['close'].values
            elif 'Close' in data.columns:
                closing = data['Close'].values
            else:
                raise ValueError('DataFrame sem coluna close/Close')
        elif isinstance(data, np.ndarray):
            closing = data
        else:
            # Tentar converter para numpy array
            closing = np.array(data, dtype=float)
        
        # Verificar se os dados são válidos
        if len(closing) == 0:
            raise ValueError('Dados vazios')
        
        print(f"📊 Dados para treinamento: {len(closing)} pontos, tipo: {type(closing)}")
        print(f"📈 Primeiros 3 valores: {closing[:3]}")
        
        trader, equities = train_ai_trader(closing, episodes=episodes, window_size=window_size, initial_capital=initial_capital)
        return trader, equities
    except Exception as e:
        print(f"Erro em train_hybrid_system: {e}")
        import traceback
        traceback.print_exc()
        return None, []

if __name__ == "__main__":
    # Testa com diferentes símbolos
    symbols = ['BTC-USD', 'ETH-USD', 'AAPL']
    
    for symbol in symbols[:1]:  # Testa apenas BTC primeiro
        try:
            hybrid, trades, metrics = run_hybrid_analysis(symbol)
            print(f"\n✅ Análise {symbol} concluída!")
        except Exception as e:
            print(f"❌ Erro em {symbol}: {e}")
        print("\n" + "="*70 + "\n")
