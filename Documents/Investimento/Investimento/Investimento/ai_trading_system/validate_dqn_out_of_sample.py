"""Validação Out-of-Sample para DQN
Treina em janela inicial e avalia em janela fora da amostra (sem treino adicional).
Adicionados: logging de ações/Q-values no teste para diagnosticar ausência de trades.
"""

from __future__ import annotations
import argparse
import os
import sys
from typing import List, Dict, Any
import numpy as np
import pandas as pd

from trading_env import TradingEnv, EnvConfig
from agent_dqn import DQNAgent, DQNConfig
from metrics import compute_episode_metrics

try:
    import yfinance as yf  # type: ignore
    HAS_YF = True
except Exception:  # pragma: no cover
    HAS_YF = False


def load_prices(symbol: str, start: str, end: str) -> pd.DataFrame:
    if HAS_YF:
        df = yf.download(symbol, start=start, end=end, progress=False)
        if 'Close' in df.columns:
            out = df[['Close']].rename(columns={'Close': 'close'}).dropna().reset_index(drop=True)
            if len(out) > 50:
                return out
    # fallback sintético
    n = 800
    print("[WARN] Usando dados sintéticos (yfinance indisponível ou série curta)")
    base = np.linspace(100, 130, n) + np.random.randn(n) * 2.0
    return pd.DataFrame({'close': base})


def run_training(prices: pd.DataFrame, episodes: int, seed: int = 42, env_config: EnvConfig | None = None) -> Dict[str, Any]:
    env = TradingEnv(prices, env_config or EnvConfig())
    cfg = DQNConfig(state_size=env.observation_space, action_size=env.action_space)
    agent = DQNAgent(cfg, seed=seed)

    train_history: List[Dict[str, Any]] = []
    for ep in range(1, episodes + 1):
        s = env.reset()
        done = False
        ep_reward = 0.0
        equity_track = [env.equity]
        last_trades_count = 0
        while not done:
            a = agent.select_action(s)
            s2, r, done, info = env.step(a)
            # Loga trade quando número cresce
            if info['trades'] > last_trades_count:
                trade = env.trades[-1]
                print(f"[TRADE] Ep {ep} t={trade['t']} {trade['type']} qty={trade['qty']:.6f} price={trade['price']:.2f}")
                last_trades_count = info['trades']
            agent.remember(s, a, r, s2, done)
            agent.env_steps += 1
            agent.update_epsilon()
            agent.train_step()
            s = s2
            ep_reward += r
            equity_track.append(info['equity'])
        m = compute_episode_metrics(equity_track, env.trades)
        m.update({'episode': ep, 'reward_sum': ep_reward, 'epsilon': agent.epsilon, 'trades_count': len(env.trades)})
        train_history.append(m)
        print(f"[TRAIN] Ep {ep:03d} Reward {ep_reward:8.4f} FinalEq {m['final_equity']:8.2f} Ret% {m['return_pct']:6.2f} Sharpe {m['sharpe']:5.2f} Trades {len(env.trades):3d} Eps {agent.epsilon:5.3f}")
    return {'agent': agent, 'history': train_history, 'env_config': env.config}


def evaluate(agent: DQNAgent, prices: pd.DataFrame, env_config: EnvConfig) -> Dict[str, Any]:
    agent.epsilon = 0.0
    env = TradingEnv(prices, env_config)
    s = env.reset()
    done = False
    equity_track = [env.equity]
    action_counts = np.zeros(env.action_space, dtype=int)
    max_debug_steps = 50  # limitar debug de Q-values
    step_debug = 0
    while not done:
        # Q-values para debug
        q_vals = agent.model.predict(s[None,:], verbose=0)[0]
        # aplica máscara manual só para log (select_action já mascara)
        position_pct = s[-2]
        q_masked = q_vals.copy()
        if position_pct <= 1e-6:
            q_masked[2] = -1e12
        a = agent.select_action(s, greedy=True)
        action_counts[a] += 1
        s2, r, done, info = env.step(a)
        if info['trades'] and len(env.trades) == 1:
            print(f"[TEST-TRADE] Primeiro trade t={env.trades[-1]['t']} {env.trades[-1]['type']} qty={env.trades[-1]['qty']:.6f} price={env.trades[-1]['price']:.2f}")
        if step_debug < max_debug_steps:
            print(f"[TEST-STEP] t={env.t} act={a} q={q_masked} eq={info['equity']:.2f} pos_qty={info['position_qty']:.6f} cooldown={info.get('cooldown')} forced={info.get('forced_hold')}")
            step_debug += 1
        s = s2
        equity_track.append(info['equity'])
    m = compute_episode_metrics(equity_track, env.trades)
    m['steps'] = env.t
    m['action_counts'] = action_counts.tolist()
    m['trades_count'] = len(env.trades)
    return {'metrics': m, 'trades': env.trades, 'equity_series': equity_track, 'action_counts': action_counts}


def split_data(df: pd.DataFrame, train_frac: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    n = len(df)
    cut = max(int(n * train_frac), 50)
    train = df.iloc[:cut].reset_index(drop=True)
    test = df.iloc[cut:].reset_index(drop=True)
    return train, test


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--symbol', default='BTC-USD')
    ap.add_argument('--start', default='2022-01-01')
    ap.add_argument('--end', default='2024-01-01')
    ap.add_argument('--episodes', type=int, default=20)
    ap.add_argument('--train-frac', type=float, default=0.7)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--out-prefix', default='dqn_validation')
    ap.add_argument('--max-trades', type=int, default=150)
    ap.add_argument('--cooldown', type=int, default=3)
    ap.add_argument('--buy-fraction', type=float, default=0.5)
    args = ap.parse_args()

    prices_all = load_prices(args.symbol, args.start, args.end)
    if len(prices_all) < 100:
        print('[ERRO] Série muito curta para validação.')
        sys.exit(1)

    train_prices, test_prices = split_data(prices_all, args.train_frac)
    print(f"Dataset total: {len(prices_all)} | Treino: {len(train_prices)} | Teste: {len(test_prices)}")

    env_cfg = EnvConfig(buy_fraction=args.buy_fraction, max_trades=args.max_trades, trade_cooldown=args.cooldown)
    result_train = run_training(train_prices, args.episodes, seed=args.seed, env_config=env_cfg)
    agent = result_train['agent']

    eval_result = evaluate(agent, test_prices, env_cfg)

    # Salvar artefatos
    train_hist_df = pd.DataFrame(result_train['history'])
    train_hist_path = f"{args.out_prefix}_train_history.csv"
    train_hist_df.to_csv(train_hist_path, index=False)

    test_equity_df = pd.DataFrame({'equity': eval_result['equity_series']})
    test_equity_path = f"{args.out_prefix}_test_equity.csv"
    test_equity_df.to_csv(test_equity_path, index=False)

    trades_df = pd.DataFrame(eval_result['trades'])
    trades_path = f"{args.out_prefix}_test_trades.csv"
    if not trades_df.empty:
        trades_df.to_csv(trades_path, index=False)

    test_metrics = eval_result['metrics']
    print("\n=== RESULTADOS OUT-OF-SAMPLE ===")
    for k, v in test_metrics.items():
        print(f"{k}: {v}")

    print("\nDistribuição de ações no teste:", test_metrics['action_counts'])

    # Resumo adicional
    print("\nArquivos salvos:")
    print(train_hist_path)
    print(test_equity_path)
    if not trades_df.empty:
        print(trades_path)

if __name__ == '__main__':
    main()
