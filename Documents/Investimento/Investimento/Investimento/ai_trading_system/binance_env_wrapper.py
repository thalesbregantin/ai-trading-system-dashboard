"""Wrapper de ambiente para usar dados da Binance (histórico curto -> feed incremental) com TradingEnv.
+ Hard stop / Trailing stop / Limite diário de perda / Kill-switch
"""
from __future__ import annotations
import time
import json
import logging
import datetime as dt
import pandas as pd
from typing import Optional, Dict, Any
from trading_env import TradingEnv, EnvConfig
from core.binance_real_data import binance_data

class LiveTradingWrapper:
    def __init__(self, symbol: str = 'BTC/USDT', timeframe: str = '1h', lookback: int = 200, refresh_sec: int = 5,
                 env_config: Optional[EnvConfig] = None, hard_stop_pct: float = 0.15, daily_loss_limit_pct: float = 0.1,
                 trail_atr_window: int = 14, trail_k: float = 2.0, kill_switch_file: str = 'STOP',
                 logger: Optional[logging.Logger] = None):
        self.symbol = symbol
        self.timeframe = timeframe
        self.lookback = lookback
        self.refresh_sec = refresh_sec
        self.env_config = env_config or EnvConfig()
        self.hard_stop_pct = hard_stop_pct
        self.daily_loss_limit_pct = daily_loss_limit_pct
        self.trail_atr_window = trail_atr_window
        self.trail_k = trail_k
        self.kill_switch_file = kill_switch_file
        self.logger = logger or self._create_logger()
        self._last_timestamp = None
        self.env: Optional[TradingEnv] = None
        self.data: Optional[pd.DataFrame] = None
        self.start_of_day_equity = None
        self.hard_stop_equity = None
        self._init_env()

    def _create_logger(self) -> logging.Logger:
        log = logging.getLogger('live_wrapper')
        if not log.handlers:
            h = logging.StreamHandler()
            fmt = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
            h.setFormatter(fmt)
            log.addHandler(h)
            log.setLevel(logging.INFO)
        return log

    def _init_env(self):
        raw = binance_data.get_market_data(self.symbol, self.timeframe, self.lookback)
        if raw is None or raw.empty:
            raise RuntimeError('Falha ao obter dados de mercado iniciais')
        self.data = raw[['close','high','low']].copy().reset_index(drop=True)
        self.env = TradingEnv(self.data[['close']].copy(), self.env_config)
        self._last_timestamp = raw['timestamp'].iloc[-1]
        self.start_of_day_equity = self.env.equity
        self.hard_stop_equity = self.env.equity * (1 - self.hard_stop_pct)
        self.logger.info(f"Init wrapper | Equity={self.env.equity:.2f} HardStop={self.hard_stop_equity:.2f}")

    def _refresh(self) -> bool:
        raw = binance_data.get_market_data(self.symbol, self.timeframe, self.lookback)
        if raw is None or raw.empty:
            return False
        latest_ts = raw['timestamp'].iloc[-1]
        if latest_ts == self._last_timestamp:
            return False
        self._last_timestamp = latest_ts
        self.data = raw[['close','high','low']].copy().reset_index(drop=True)
        # atualiza série de preços mantendo estado financeiro
        self.env.prices_raw = self.data[['close']].copy()
        self.env._prepare_features()
        # reset diário se mudança de dia UTC
        if dt.datetime.utcnow().date() != getattr(self, '_current_day', dt.datetime.utcnow().date()):
            self._current_day = dt.datetime.utcnow().date()
            self.start_of_day_equity = self.env.equity
        return True

    def _atr(self) -> float:
        if self.data is None or len(self.data) < self.trail_atr_window + 1:
            return 0.0
        d = self.data.tail(self.trail_atr_window+1).reset_index(drop=True)
        high = d['high']; low = d['low']; close = d['close']
        prev_close = close.shift(1)
        tr = pd.concat([
            (high - low),
            (high - prev_close).abs(),
            (low - prev_close).abs()
        ], axis=1).max(axis=1)
        atr = tr.rolling(self.trail_atr_window).mean().iloc[-1]
        return float(atr) if not pd.isna(atr) else 0.0

    def current_observation(self):
        return self.env._get_observation()

    def _check_kill_switch(self) -> bool:
        return self.kill_switch_file and os.path.isfile(self.kill_switch_file)

    def risk_controls_triggered(self) -> Optional[str]:
        equity = self.env.equity
        # Hard stop global
        if equity <= self.hard_stop_equity:
            return f"Hard stop equity {equity:.2f} <= {self.hard_stop_equity:.2f}"
        # Daily loss limit
        if self.start_of_day_equity and equity <= self.start_of_day_equity * (1 - self.daily_loss_limit_pct):
            return f"Daily loss limit atingido {equity:.2f} <= {(self.start_of_day_equity * (1 - self.daily_loss_limit_pct)):.2f}"
        # Kill switch manual
        if self._check_kill_switch():
            return "Kill switch file detectado"
        return None

    def compute_trailing_stop(self) -> Optional[float]:
        if self.env.position_qty <= 0:
            return None
        atr = self._atr()
        if atr <= 0:
            return None
        price = float(self.data['close'].iloc[-1])
        trail = price - self.trail_k * atr
        return trail

    def enforce_trailing_stop(self) -> bool:
        trail = self.compute_trailing_stop()
        if trail is None:
            return False
        price = float(self.data['close'].iloc[-1])
        if price <= trail:
            # força venda (ação 2)
            _, _, _, info = self.env.step(2)
            self.logger.warning(f"Trailing stop executado | Price={price:.2f} Trail={trail:.2f} Equity={info['equity']:.2f}")
            return True
        return False

    def step_live(self, action: int):
        # Atualiza dados
        self._refresh()
        # Checa risco antes de executar
        risk_msg = self.risk_controls_triggered()
        if risk_msg:
            self.logger.error(f"Risco acionado: {risk_msg}. Forçando hold.")
            action = 0
        # Executa ação
        obs, reward, done, info = self.env.step(action)
        # Trailing stop após ação (para não interferir em execução original)
        if self.enforce_trailing_stop():
            done = False  # episódio continua
        # Reinício se done
        if done:
            final_equity = info['equity']
            cfg = self.env.config
            cfg.initial_balance = final_equity
            self.env = TradingEnv(self.data[['close']].copy(), cfg)
            obs = self.env.reset()
        # Log JSON compacto
        log_obj = {
            'ts': time.time(), 'eq': info['equity'], 'bal': info['balance'], 'pos_qty': info['position_qty'],
            'r': reward, 'act': action, 'eps_done': done
        }
        self.logger.info(json.dumps(log_obj))
        return obs, reward, done, info

if __name__ == '__main__':
    import os
    w = LiveTradingWrapper()
    obs = w.current_observation()
    for i in range(3):
        o, r, d, info = w.step_live(0)
        time.sleep(1)
