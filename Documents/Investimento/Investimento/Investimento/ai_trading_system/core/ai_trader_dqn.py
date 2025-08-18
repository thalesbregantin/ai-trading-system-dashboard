"""
AI Trading Robot com Deep Q-Learning
Adaptado do repositório oGabrielFreitas/Trading-Robot-Deep-Q-Learning
Integrado com nosso sistema de momentum e indicadores técnicos
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from collections import deque
import random
import warnings
from pathlib import Path
import csv, datetime
import json
from .config import TradingConfig
warnings.filterwarnings('ignore')

class AITrader:
    """
    Trader AI usando Deep Q-Learning
    """
    
    def __init__(self, state_size, is_eval=False, model_name=""):
        self.state_size = state_size
        self.action_size = 3  # 0: Hold, 1: Buy, 2: Sell
        self.memory = deque(maxlen=2000)
        self.inventory = []
        self.model_name = model_name
        self.is_eval = is_eval
        
        # Parâmetros Q-Learning
        self.gamma = 0.95    # discount factor
        self.epsilon = 1.0   # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = getattr(TradingConfig, 'AI_EPSILON_DECAY', 0.995)
        self.learning_rate = 0.001
        
        # Build neural network
        self.model = self._model()
        
        if is_eval and model_name:
            self.model.load_weights(model_name)
    
    def _model(self):
        """Cria a rede neural Q-Network"""
        model = Sequential()
        model.add(Dense(64, input_dim=self.state_size, activation="relu"))
        model.add(Dropout(0.2))
        model.add(Dense(32, activation="relu"))
        model.add(Dropout(0.2))
        model.add(Dense(16, activation="relu"))
        model.add(Dense(self.action_size, activation="linear"))
        
        model.compile(loss="mse", optimizer=Adam(learning_rate=self.learning_rate))
        return model
    
    def act(self, state):
        """Escolhe uma ação baseada no estado atual"""
        if not self.is_eval and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        
        q_values = self.model.predict(state, verbose=0)
        return np.argmax(q_values[0])
    
    def remember(self, state, action, reward, next_state, done):
        """Armazena experiência na memória"""
        self.memory.append((state, action, reward, next_state, done))
    
    def replay(self, batch_size):
        """Treina o modelo usando experiências passadas"""
        if len(self.memory) < batch_size:
            return
            
        batch = random.sample(self.memory, batch_size)
        
        for state, action, reward, next_state, done in batch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(next_state, verbose=0)[0])
            
            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target
            
            self.model.fit(state, target_f, epochs=1, verbose=0)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

def create_state(data, timestep, window_size):
    """
    Cria estado normalizado baseado nos preços
    Combina com indicadores técnicos do nosso sistema
    """
    starting_id = timestep - window_size + 1
    
    if starting_id >= 0:
        windowed_data = data[starting_id:timestep + 1]
    else:
        windowed_data = np.concatenate([np.array([data[0]] * (-starting_id)), data[0:timestep + 1]])
    
    # Normaliza os dados
    state = []
    for i in range(window_size - 1):
        state.append(sigmoid(windowed_data[i + 1] - windowed_data[i]))
    
    return np.array([state])

def sigmoid(x):
    """Função sigmoid para normalização"""
    return 1 / (1 + np.exp(-x))

def format_price(price):
    """Formata preço para exibição"""
    return f"${price:.2f}"

class TradingEnvironment:
    """
    Ambiente de trading que integra com nosso sistema existente
    """
    
    def __init__(self, data, window_size=10):
        self.data = data
        self.window_size = window_size
        self.reset()
    
    def reset(self):
        """Reset do ambiente"""
        self.current_step = self.window_size
        self.total_profit = 0
        self.trades = []
        return create_state(self.data, self.current_step, self.window_size)
    
    def step(self, action, trader):
        """
        Executa uma ação no ambiente
        """
        current_price = self.data[self.current_step]
        reward = 0
        done = False
        
        # Ação 1: Buy
        if action == 1:
            trader.inventory.append(current_price)
            self.trades.append({
                'type': 'BUY',
                'price': current_price,
                'timestamp': self.current_step,
                'inventory_size': len(trader.inventory)
            })
            
        # Ação 2: Sell
        elif action == 2 and len(trader.inventory) > 0:
            buy_price = trader.inventory.pop(0)
            profit = current_price - buy_price
            reward = max(profit, 0)  # Reward apenas para lucros
            self.total_profit += profit
            
            self.trades.append({
                'type': 'SELL',
                'buy_price': buy_price,
                'sell_price': current_price,
                'profit': profit,
                'timestamp': self.current_step,
                'inventory_size': len(trader.inventory)
            })
        
        # Próximo estado
        self.current_step += 1
        if self.current_step >= len(self.data) - 1:
            done = True
            next_state = None
        else:
            next_state = create_state(self.data, self.current_step, self.window_size)
        
        return next_state, reward, done
    
    def get_performance_metrics(self):
        """Calcula métricas de performance"""
        if not self.trades:
            return {}
        
        profits = [trade['profit'] for trade in self.trades if trade['type'] == 'SELL']
        
        if not profits:
            return {}
        
        win_rate = len([p for p in profits if p > 0]) / len(profits) * 100
        avg_profit = np.mean(profits)
        max_profit = max(profits)
        min_profit = min(profits)
        
        return {
            'total_profit': self.total_profit,
            'num_trades': len([t for t in self.trades if t['type'] == 'SELL']),
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'max_profit': max_profit,
            'min_profit': min_profit,
            'sharpe_ratio': np.mean(profits) / np.std(profits) if np.std(profits) > 0 else 0
        }

class CapitalTradingEnvironment:
    """Ambiente com capital realista e posição única."""
    def __init__(self, data, window_size=10, initial_capital=100.0, prices=None):
        self.data = data
        self.window_size = window_size
        self.initial_capital = initial_capital
        self.prices = prices if prices is not None else data
        self.reset()
    def reset(self):
        self.current_step = self.window_size
        self.capital = float(self.initial_capital)
        self.position_qty = 0.0
        self.entry_price = 0.0
        self.equity = self.capital
        self.prev_equity = self.equity
        self.trades = []
        return create_state(self.data, self.current_step, self.window_size)
    def step(self, action, trader):
        price = self.data[self.current_step]
        done = False
        reward = 0.0
        # BUY
        if action == 1 and self.position_qty == 0 and self.capital > 0:
            self.position_qty = self.capital / price
            self.entry_price = price
            self.capital = 0.0
            self.trades.append({'type':'BUY','price':price,'step':self.current_step,'qty':self.position_qty})
        # SELL
        elif action == 2 and self.position_qty > 0:
            sell_value = self.position_qty * price
            profit = sell_value - (self.position_qty * self.entry_price)
            self.capital = sell_value
            self.trades.append({'type':'SELL','price':price,'step':self.current_step,'qty':self.position_qty,'profit':profit})
            self.position_qty = 0.0
            self.entry_price = 0.0
        # Atualiza equity
        position_value = self.position_qty * price
        self.prev_equity = self.equity
        self.equity = self.capital + position_value
        # Reward = retorno percentual incremental
        if self.prev_equity > 0:
            reward = (self.equity - self.prev_equity) / self.prev_equity
        # Avança
        self.current_step += 1
        if self.current_step >= len(self.data) - 1:
            done = True
            next_state = None
        else:
            next_state = create_state(self.data, self.current_step, self.window_size)
        return next_state, reward, done
    def get_metrics(self):
        returns = []
        if len(self.trades) == 0:
            return {}
        realized = [t for t in self.trades if t['type']=='SELL']
        profits = [t.get('profit',0) for t in realized]
        win_rate = (len([p for p in profits if p>0]) / len(profits) * 100) if profits else 0
        total_profit = (self.equity - self.initial_capital)
        total_return_pct = (self.equity / self.initial_capital - 1)*100 if self.initial_capital>0 else 0
        # Simplistic sharpe: usar equity diffs
        if len(profits)>1 and np.std(profits)!=0:
            sharpe = np.mean(profits)/np.std(profits)
        else:
            sharpe = 0
        return {
            'equity': self.equity,
            'total_profit': total_profit,
            'total_return_pct': total_return_pct,
            'num_trades': len(realized),
            'win_rate': win_rate,
            'sharpe': sharpe
        }

def compute_indicators(series, rsi_period=14, momentum_period=10):
    prices = pd.Series(series)
    delta = prices.diff()
    gain = delta.clip(lower=0).rolling(rsi_period).mean()
    loss = (-delta.clip(upper=0)).rolling(rsi_period).mean()
    rs = gain / (loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    momentum = prices.pct_change(momentum_period)
    return rsi.fillna(50), momentum.fillna(0)

def create_state_with_indicators(data, timestep, window_size, rsi_series, mom_series):
    base = create_state(data, timestep, window_size)[0]
    rsi_val = rsi_series.iloc[timestep] if timestep < len(rsi_series) else 50
    mom_val = mom_series.iloc[timestep] if timestep < len(mom_series) else 0
    enhanced = np.concatenate([base, [rsi_val/100.0, mom_val]])
    return np.array([enhanced])

def train_ai_trader(data, episodes=50, window_size=10, batch_size=32, initial_capital=None, log_dir="logs/training", checkpoint_prefix="checkpoint_ep", use_indicators=True, save_checkpoints=True, jsonl_steps=True):
    """Treina AI Trader com opção de ambiente de capital."""
    print("🤖 Iniciando Treinamento do AI Trader...")
    print(f"📊 Dados: {len(data)} pontos")
    print(f"🎯 Episódios: {episodes}")
    print(f"🪟 Window Size: {window_size}")
    state_size = window_size - 1 + (2 if use_indicators else 0)
    trader = AITrader(state_size)
    step_sample = getattr(TradingConfig, 'STEP_LOG_SAMPLE', 3)
    jsonl_max = getattr(TradingConfig, 'JSONL_MAX_LINES', 50000)
    ckpt_freq = getattr(TradingConfig, 'CHECKPOINT_FREQUENCY', 5)
    save_best = getattr(TradingConfig, 'SAVE_BEST_CHECKPOINT', True)
    early_stop = getattr(TradingConfig, 'EARLY_STOP_ENABLED', False)
    early_patience = getattr(TradingConfig, 'EARLY_STOP_PATIENCE', 10)
    early_metric = getattr(TradingConfig, 'EARLY_STOP_METRIC', 'sharpe')
    momentum_clip = getattr(TradingConfig, 'MOMENTUM_CLIP', 0.2)
    # Ajuste momentum (clip)
    # Pré-computa indicadores
    if use_indicators:
        rsi_series, mom_series = compute_indicators(data)
        mom_series = mom_series.clip(-momentum_clip, momentum_clip)
    else:
        rsi_series, mom_series = None, None
    use_capital_env = initial_capital is not None
    if use_capital_env:
        env = CapitalTradingEnvironment(data, window_size, initial_capital=initial_capital)
    else:
        env = TradingEnvironment(data, window_size)
    # Logging dirs
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    metrics_csv = log_path / "training_metrics.csv"
    steps_jsonl = log_path / "training_steps.jsonl"
    write_header = not metrics_csv.exists()
    if write_header:
        with metrics_csv.open('w', newline='', encoding='utf-8') as f:
            cw = csv.writer(f)
            cw.writerow(["timestamp","episode","use_capital_env","equity","total_profit","total_return_pct","num_trades","win_rate","sharpe","epsilon"])    
    episode_equities = []
    jsonl_line_count = 0
    best_metric = -1e9
    best_ckpt_path = None
    no_improve = 0
    for ep in range(episodes):
        print(f"\n📈 Episódio {ep+1}/{episodes}")
        state = (create_state_with_indicators(data, env.current_step, window_size, rsi_series, mom_series) if use_indicators else env.reset())
        if not use_indicators:
            state = env.reset()
        else:
            env.reset()
            state = create_state_with_indicators(data, env.current_step, window_size, rsi_series, mom_series)
        trader.inventory = []
        done = False
        step_count = 0
        while not done:
            action = trader.act(state)
            next_state_raw, reward, done = env.step(action, trader)
            if next_state_raw is not None:
                next_state = (create_state_with_indicators(data, env.current_step, window_size, rsi_series, mom_series) if use_indicators else next_state_raw)
            else:
                next_state = None
            if next_state is not None:
                trader.remember(state, action, reward, next_state, done)
            # JSONL step logging com sampling
            if jsonl_steps and (step_count % step_sample == 0):
                rec = {
                    'episode': int(ep+1),
                    'step': int(step_count),
                    'action': int(action),
                    'reward': float(reward),
                    'equity': float(getattr(env, 'equity', 0)),
                    'capital': float(getattr(env, 'capital', 0)),
                    'position_qty': float(getattr(env, 'position_qty', 0)),
                    'price': float(data[env.current_step-1]) if env.current_step-1 < len(data) else None,
                    'epsilon': float(trader.epsilon)
                }
                with steps_jsonl.open('a', encoding='utf-8') as jf:
                    jf.write(json.dumps(rec) + "\n")
                jsonl_line_count += 1
                if jsonl_line_count >= jsonl_max:
                    # Rotaciona
                    rotated = log_path / f"training_steps_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jsonl"
                    steps_jsonl.rename(rotated)
                    jsonl_line_count = 0
            state = next_state
            if action == 1 and use_capital_env:
                print(f"   🟢 BUY  @ {data[env.current_step-1]:.2f} Equity={getattr(env,'equity',0):.2f}")
            elif action == 2 and use_capital_env:
                print(f"   🔴 SELL @ {data[env.current_step-1]:.2f} Equity={getattr(env,'equity',0):.2f}")
            step_count += 1
        if len(trader.memory) > batch_size:
            trader.replay(batch_size)
        metrics = env.get_metrics() if use_capital_env else env.get_performance_metrics()
        equity = metrics.get('equity', metrics.get('total_profit',0)) if metrics else 0
        episode_equities.append(equity)
        if use_capital_env:
            print(f"💰 Equity Final: {equity:.2f} (Retorno {metrics.get('total_return_pct',0):.2f}%)")
        else:
            print(f"💰 Lucro Total: {metrics.get('total_profit',0):.2f}")
        if metrics:
            print(f"📊 Trades: {metrics.get('num_trades',0)} | WinRate: {metrics.get('win_rate',0):.1f}% | Sharpe: {metrics.get('sharpe',0):.3f}")
        print(f"🎯 Epsilon: {trader.epsilon:.3f}")
        with metrics_csv.open('a', newline='', encoding='utf-8') as f:
            cw = csv.writer(f)
            cw.writerow([
                datetime.datetime.utcnow().isoformat(), ep+1, int(use_capital_env),
                metrics.get('equity',0) if metrics else 0,
                metrics.get('total_profit',0) if metrics else 0,
                metrics.get('total_return_pct',0) if metrics else 0,
                metrics.get('num_trades',0) if metrics else 0,
                metrics.get('win_rate',0) if metrics else 0,
                metrics.get('sharpe',0) if metrics else 0,
                trader.epsilon
            ])
        # Early stopping & best checkpoint
        current_metric = 0
        if metrics:
            if early_metric == 'sharpe':
                current_metric = metrics.get('sharpe', 0)
            elif early_metric == 'equity_return':
                current_metric = metrics.get('total_return_pct', 0)
        if save_best and metrics:
            if current_metric > best_metric:
                best_metric = current_metric
                best_ckpt_path = log_path / "best_model.weights.h5"
                trader.model.save_weights(str(best_ckpt_path))
                print(f"🌟 Novo melhor modelo ({early_metric}={current_metric:.4f}) salvo")
                no_improve = 0
            else:
                no_improve += 1
        # Checkpoint periódico
        if save_checkpoints and ((ep+1) % ckpt_freq == 0):
            ckpt_path = log_path / f"{checkpoint_prefix}_{ep+1:03d}.weights.h5"
            trader.model.save_weights(str(ckpt_path))
        # Early stop
        if early_stop and no_improve >= early_patience:
            print(f"⏹️ Early stopping após {ep+1} episódios (sem melhora {early_metric} por {no_improve} eps)")
            break
    return trader, episode_equities

def integrate_with_momentum_strategy(price_data, sma_short=20, sma_long=50):
    """
    Integra AI Trader com nossa estratégia de momentum
    """
    print("🔄 Integrando AI Trader com Estratégia de Momentum...")
    
    # Calcula indicadores técnicos
    df = pd.DataFrame({'close': price_data})
    df['sma_short'] = df['close'].rolling(window=sma_short).mean()
    df['sma_long'] = df['close'].rolling(window=sma_long).mean()
    df['momentum'] = df['close'].pct_change(periods=10)
    
    # Remove NaN
    df = df.dropna()
    
    # Treina AI com dados + indicadores
    enhanced_data = df['close'].values
    
    # Adiciona features técnicas ao estado
    def create_enhanced_state(data_idx):
        """Estado expandido com indicadores técnicos"""
        if data_idx < 10:
            return None
            
        base_state = create_state(enhanced_data, data_idx, 10)
        
        # Adiciona features técnicas
        sma_signal = 1 if df.iloc[data_idx]['sma_short'] > df.iloc[data_idx]['sma_long'] else 0
        momentum_signal = 1 if df.iloc[data_idx]['momentum'] > 0 else 0
        
        # Combina estados
        technical_features = np.array([[sma_signal, momentum_signal]])
        enhanced_state = np.concatenate([base_state, technical_features], axis=1)
        
        return enhanced_state
    
    return enhanced_data, create_enhanced_state

def backtest_ai_trader(trader, data, window_size=10):
    """
    Backtesting do AI trader treinado
    """
    print("🧪 Executando Backtest do AI Trader...")
    
    env = TradingEnvironment(data, window_size)
    state = env.reset()
    trader.inventory = []
    trader.is_eval = True  # Modo avaliação (sem exploração)
    
    results = []
    
    for t in range(window_size, len(data) - 1):
        action = trader.act(state)
        
        action_name = ['HOLD', 'BUY', 'SELL'][action]
        
        next_state, reward, done = env.step(action, trader)
        
        results.append({
            'timestamp': t,
            'price': data[t],
            'action': action_name,
            'reward': reward,
            'inventory_size': len(trader.inventory)
        })
        
        state = next_state
        
        if done:
            break
    
    metrics = env.get_performance_metrics()
    
    print("📊 Resultados do Backtest:")
    print(f"💰 Lucro Total: {format_price(metrics.get('total_profit', 0))}")
    print(f"📈 Trades: {metrics.get('num_trades', 0)}")
    print(f"🎯 Win Rate: {metrics.get('win_rate', 0):.1f}%")
    print(f"📊 Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}")
    
    return results, metrics

def save_ai_model(trader, filename):
    """Salva o modelo treinado"""
    trader.model.save_weights(filename)
    print(f"💾 Modelo salvo: {filename}")

def load_ai_model(state_size, filename):
    """Carrega modelo treinado"""
    trader = AITrader(state_size, is_eval=True, model_name=filename)
    print(f"📂 Modelo carregado: {filename}")
    return trader

if __name__ == "__main__":
    # Exemplo de uso
    print("🤖 AI Trading Robot - Deep Q-Learning")
    print("=" * 50)
    
    # Simula dados de preço
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(500) * 0.1)
    
    # Treina o trader
    trader, profits = train_ai_trader(prices, episodes=10)
    
    # Salva modelo
    save_ai_model(trader, "ai_trader_model.h5")
    
    # Testa o modelo
    results, metrics = backtest_ai_trader(trader, prices)
    
    print("\n✅ Treinamento e teste concluídos!")
