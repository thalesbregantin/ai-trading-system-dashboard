"""Execução Live / Paper do DQN usando dados da Binance.
Requer: binance_env_wrapper (candles via ccxt) + modelo DQN treinado (opcional).

Uso exemplo:
  python run_live_dqn.py --symbol BTC/USDT --timeframe 1h --model dqn_weights.h5 --poll 60

Fluxo:
 1. Inicializa wrapper live (carrega últimos candles)
 2. Cria agente DQN e carrega pesos se existir
 3. Loop: aguarda novo candle (polling), gera ação, executa step_live
 4. Registra métricas e salva snapshot periódico

Obs: Este script NÃO envia ordens reais; apenas simula dentro do wrapper.
Integração com execução real exigiria módulo de execução separado.
"""
from __future__ import annotations
import argparse
import os
import time
import json
import signal
import logging
from pathlib import Path
from typing import Optional
import numpy as np

from agent_dqn import DQNAgent, DQNConfig
from trading_env import EnvConfig
from binance_env_wrapper import LiveTradingWrapper
from metrics import compute_episode_metrics

STOP = False

def handle_sig(signum, frame):  # noqa
    global STOP
    STOP = True
    print("\n[Signal] Encerrando loop...")

for sig in (signal.SIGINT, signal.SIGTERM):
    try:
        signal.signal(sig, handle_sig)
    except Exception:
        pass


def create_logger(log_path: str, verbose: bool = True) -> logging.Logger:
    logger = logging.getLogger("live_dqn")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        fmt = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        logger.addHandler(sh)
        fh = logging.FileHandler(log_path)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger


def wait_new_candle(wrapper: LiveTradingWrapper, poll_sec: int, logger: logging.Logger) -> bool:
    """Espera até um novo candle aparecer. Retorna True se novo candle, False se stop."""
    start_ts = wrapper._last_timestamp
    while not STOP:
        updated = wrapper._refresh()
        if updated and wrapper._last_timestamp != start_ts:
            return True
        time.sleep(poll_sec)
    return False


def run_live(args):
    os.makedirs('logs', exist_ok=True)
    logger = create_logger('logs/live_dqn.log', verbose=not args.quiet)
    logger.info(f"Iniciando Live DQN | Symbol={args.symbol} TF={args.timeframe}")

    env_cfg = EnvConfig(initial_balance=args.initial_balance,
                        fee_pct=args.fee_pct,
                        slippage_pct=args.slippage_pct,
                        buy_fraction=args.buy_fraction,
                        reward_normalize=True)

    wrapper = LiveTradingWrapper(symbol=args.symbol, timeframe=args.timeframe, lookback=args.lookback,
                                 refresh_sec=args.poll, env_config=env_cfg)

    state_size = wrapper.env.observation_space
    action_size = wrapper.env.action_space

    cfg = DQNConfig(state_size=state_size,
                    action_size=action_size,
                    epsilon_start=args.epsilon,
                    epsilon_end=args.epsilon_min,
                    epsilon_decay_steps=10_000,
                    batch_size=args.batch_size,
                    buffer_size=args.buffer_size,
                    min_buffer_size=args.min_buffer,
                    target_sync_interval=args.target_sync,
                    train_interval=args.train_every,
                    lr=args.lr,
                    save_path=args.model)
    agent = DQNAgent(cfg, seed=args.seed)

    # Carrega pesos se existir
    if args.model and Path(args.model).is_file():
        try:
            agent.load(args.model)
            logger.info(f"Pesos carregados de {args.model}")
        except Exception as e:
            logger.warning(f"Falha ao carregar pesos: {e}; iniciando do zero.")

    equity_track = [wrapper.env.equity]
    last_save = time.time()
    start_equity = wrapper.env.equity
    min_equity_allowed = start_equity * (1 - args.max_loss_pct)

    logger.info(f"Equity inicial: {start_equity:.2f} | Max perda permitida: {args.max_loss_pct*100:.2f}%")

    steps = 0
    episodes = 0

    # Loop principal: espera novo candle, decide ação com estado anterior
    obs = wrapper.current_observation()

    while not STOP:
        # Espera novo candle fechado
        if not wait_new_candle(wrapper, args.poll, logger):
            break
        # Seleciona ação
        action = agent.select_action(obs)
        next_obs, reward, done, info = wrapper.step_live(action)
        agent.remember(obs, action, reward, next_obs, done)
        agent.env_steps += 1
        agent.update_epsilon()
        loss = agent.train_step()
        obs = next_obs
        equity_track.append(info['equity'])
        steps += 1

        if loss is not None and steps % 10 == 0:
            logger.info(f"Step {steps} Eq {info['equity']:.2f} R {reward:.4f} Eps {agent.epsilon:.3f} Loss {loss:.5f} Trades {info['trades']}")
        elif loss is None and steps % 10 == 0:
            logger.info(f"Step {steps} Eq {info['equity']:.2f} R {reward:.4f} Eps {agent.epsilon:.3f} (warming buffer) Trades {info['trades']}")

        # Risk cut
        if info['equity'] < min_equity_allowed:
            logger.error(f"Stop de perda atingido. Equity {info['equity']:.2f} < {min_equity_allowed:.2f}")
            break

        if done:
            # Episódio completo (fim da série / reinício por wrapper)
            episodes += 1
            metrics = compute_episode_metrics(equity_track, wrapper.env.trades)
            logger.info(f"[EP {episodes}] Ret% {metrics['return_pct']:.2f} MDD% {metrics['max_drawdown_pct']:.2f} Sharpe {metrics['sharpe']:.2f} Trades {metrics['trades']}")
            equity_track = [wrapper.env.equity]

        # Salva periódico
        if args.model and (time.time() - last_save) > args.save_interval:
            try:
                agent.save(args.model)
                last_save = time.time()
                logger.info("Pesos salvos.")
            except Exception as e:
                logger.warning(f"Falha ao salvar pesos: {e}")

    # Encerramento
    if args.model:
        try:
            agent.save(args.model)
        except Exception:
            pass

    # Dump final de métricas
    metrics = compute_episode_metrics(equity_track, wrapper.env.trades)
    summary_path = 'live_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    logger.info(f"Resumo salvo em {summary_path}")
    logger.info("Encerrado.")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--symbol', default='BTC/USDT')
    p.add_argument('--timeframe', default='1h')
    p.add_argument('--lookback', type=int, default=300)
    p.add_argument('--poll', type=int, default=30, help='Segundos entre verificações de novo candle')
    p.add_argument('--initial-balance', type=float, default=1000.0)
    p.add_argument('--fee-pct', type=float, default=0.001)
    p.add_argument('--slippage-pct', type=float, default=0.0005)
    p.add_argument('--buy-fraction', type=float, default=1.0)
    p.add_argument('--epsilon', type=float, default=0.1)
    p.add_argument('--epsilon-min', type=float, default=0.01)
    p.add_argument('--batch-size', type=int, default=64)
    p.add_argument('--buffer-size', type=int, default=50000)
    p.add_argument('--min-buffer', type=int, default=1000)
    p.add_argument('--target-sync', type=int, default=1000)
    p.add_argument('--train-every', type=int, default=4)
    p.add_argument('--lr', type=float, default=1e-3)
    p.add_argument('--model', default='dqn_live.h5')
    p.add_argument('--save-interval', type=int, default=900, help='Segundos entre salvamentos de pesos')
    p.add_argument('--max-loss-pct', type=float, default=0.2, help='Perda máxima percentual do equity inicial para parar')
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--quiet', action='store_true')
    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()
    run_live(args)
