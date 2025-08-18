"""Script de treino integrando TradingEnv + DQNAgent + métricas.
Uso:
  python train_dqn.py --episodes 20
"""
from __future__ import annotations
import argparse
import numpy as np
import pandas as pd
from typing import List, Dict, Any

from trading_env import TradingEnv, EnvConfig
from agent_dqn import DQNAgent, DQNConfig
from metrics import compute_episode_metrics


def generate_synthetic_data(n: int = 1500) -> pd.DataFrame:
    trend = np.linspace(100, 130, n)
    noise = np.random.randn(n) * 1.5
    return pd.DataFrame({'close': trend + noise})


def train(episodes: int, save: bool = True):
    prices = generate_synthetic_data()
    env = TradingEnv(prices, EnvConfig())
    cfg = DQNConfig(state_size=env.observation_space, action_size=env.action_space)
    agent = DQNAgent(cfg, seed=42)

    history: List[Dict[str, Any]] = []
    for ep in range(1, episodes + 1):
        s = env.reset()
        done = False
        ep_reward = 0.0
        equity_track = [env.equity]
        while not done:
            a = agent.select_action(s)
            s2, r, done, info = env.step(a)
            agent.remember(s, a, r, s2, done)
            agent.env_steps += 1
            agent.update_epsilon()
            agent.train_step()
            s = s2
            ep_reward += r
            equity_track.append(info['equity'])
        metrics = compute_episode_metrics(equity_track, env.trades)
        metrics.update({
            'episode': ep,
            'reward_sum': ep_reward,
            'epsilon': agent.epsilon,
            'steps': env.t,
        })
        history.append(metrics)
        print(f"Ep {ep:03d} | Reward {ep_reward:8.4f} | Equity {metrics['final_equity']:8.2f} | Ret% {metrics['return_pct']:6.2f} | MDD% {metrics['max_drawdown_pct']:6.2f} | Sharpe {metrics['sharpe']:5.2f} | Eps {agent.epsilon:5.3f} | Trades {metrics['trades']}")

    if save:
        agent.save()
    return history


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--episodes', type=int, default=10)
    p.add_argument('--no-save', action='store_true')
    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()
    train(episodes=args.episodes, save=not args.no_save)
