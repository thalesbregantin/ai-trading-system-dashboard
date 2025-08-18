"""Trading Environment (Passo 2/4)
Ações discretas: 0=Hold, 1=Buy (move posição alvo), 2=Sell (full position)
Observação: [price_rel, ret_1, ret_5, vol_5, position_pct, unrealized_pnl_pct]
Recompensa padrão: delta_equity (normalizado por saldo_inicial) + shaping
Anti-overtrading adicionados:
 - buy_fraction agora representa alvo máximo de posição (% do equity)
 - Cooldown após trade para impedir sequências rápidas
 - Penalidade fixa por trade (trade_penalty)
 - Limite opcional de trades por episódio (max_trades)
 - holding_penalty penaliza manter posição aberta continuamente
 - Liquidação forçada no final do episódio para consolidar PnL
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

@dataclass
class EnvConfig:
    initial_balance: float = 1000.0
    fee_pct: float = 0.001          # 0.1%
    slippage_pct: float = 0.0005    # 0.05%
    buy_fraction: float = 0.5       # alvo máximo de posição (50% do equity)
    reward_normalize: bool = True
    max_steps: Optional[int] = None
    min_candles: int = 20           # mínimo para calcular features estáveis
    reward_unrealized_weight: float = 0.01  # incentivo a manter posição lucrativa
    inactivity_penalty: float = 0.0001      # leve penalidade para inação prolongada
    trade_penalty: float = 0.0002           # penalidade por trade (normalizada se reward_normalize)
    trade_cooldown: int = 3                 # passos obrigatórios de hold após qualquer trade
    max_trades: Optional[int] = None        # limite hard; None = ilimitado
    holding_penalty: float = 0.00005          # penalidade * position_pct por step

class TradingEnv:
    def __init__(self, prices: pd.DataFrame, config: EnvConfig = EnvConfig(), seed: Optional[int] = None):
        if 'close' not in prices.columns:
            raise ValueError("DataFrame deve conter coluna 'close'")
        self.prices_raw = prices.reset_index(drop=True).copy()
        self.config = config
        self.rng = np.random.default_rng(seed)
        self._prepare_features()
        self.action_space = 3
        self.observation_space = 6
        self.reset()

    def _prepare_features(self):
        df = self.prices_raw
        df['ret_1'] = df['close'].pct_change()
        df['ret_5'] = df['close'].pct_change(5)
        df['vol_5'] = df['ret_1'].rolling(5).std()
        df[['ret_1','ret_5','vol_5']] = df[['ret_1','ret_5','vol_5']].fillna(0)
        self.data = df

    def reset(self) -> np.ndarray:
        self.balance = self.config.initial_balance
        self.position_qty = 0.0
        self.position_avg_price = 0.0
        self.equity = self.balance
        self.equity_prev = self.equity
        self.t = max(self.config.min_candles, 1)
        self.ref_price = float(self.data.loc[0,'close'])
        self.done = False
        self.trades: list[Dict[str, Any]] = []
        self.steps_since_trade = 0
        self.cooldown = 0
        return self._get_observation()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        if self.done:
            raise RuntimeError("Chamou step após done=True. Use reset().")
        if action not in (0,1,2):
            raise ValueError("Ação inválida. Use 0=Hold,1=Buy,2=Sell")
        forced_hold = False
        # Aplica cooldown e limite de trades
        if (self.cooldown > 0) or (self.config.max_trades is not None and len(self.trades) >= self.config.max_trades):
            action = 0
            forced_hold = True
        price = float(self.data.loc[self.t,'close'])
        executed_trade = None
        if action == 1:
            # Recalcula equity mark-to-market antes para definir alvo
            mark_value_pre = self.position_qty * price
            current_equity_pre = self.balance + mark_value_pre
            target_position_value = current_equity_pre * self.config.buy_fraction
            current_position_value = mark_value_pre
            # Se já próximo do alvo, não faz nada
            if current_position_value < target_position_value * 0.98:  # margem 2%
                needed_value = target_position_value - current_position_value
                available_cash = self.balance  # pode usar todo saldo livre, limite imposto pelo needed
                order_value = min(needed_value, available_cash)
                if order_value > 0:
                    exec_price = price * (1 + self.config.slippage_pct)
                    qty = order_value / (exec_price * (1 + self.config.fee_pct))
                    if qty > 0:
                        gross = qty * exec_price
                        fee = gross * self.config.fee_pct
                        total_cost = gross + fee
                        if total_cost <= self.balance + 1e-9:
                            new_total_qty = self.position_qty + qty
                            if new_total_qty > 0:
                                self.position_avg_price = (self.position_avg_price * self.position_qty + exec_price * qty) / new_total_qty
                            self.position_qty = new_total_qty
                            self.balance -= total_cost
                            executed_trade = {"type":"BUY","qty":float(qty),"price":float(exec_price),"fee":float(fee)}
        elif action == 2 and self.position_qty > 0:
            exec_price = price * (1 - self.config.slippage_pct)
            gross = exec_price * self.position_qty
            fee = gross * self.config.fee_pct
            proceeds = gross - fee
            pnl = (exec_price - self.position_avg_price) * self.position_qty
            self.balance += proceeds
            executed_trade = {"type":"SELL","qty":float(self.position_qty),"price":float(exec_price),"fee":float(fee),"pnl":float(pnl)}
            self.position_qty = 0.0
            self.position_avg_price = 0.0

        if executed_trade:
            self.trades.append({"t": self.t, **executed_trade})
            self.steps_since_trade = 0
            self.cooldown = self.config.trade_cooldown
        else:
            self.steps_since_trade += 1
            if self.cooldown > 0:
                self.cooldown -= 1

        # Atualiza equity
        mark_value = self.position_qty * price if self.position_qty > 0 else 0.0
        self.equity_prev = self.equity
        self.equity = self.balance + mark_value

        reward = self._compute_reward(executed_trade is not None)

        # Penalidade por trade (após reward base)
        if executed_trade and self.config.trade_penalty > 0:
            penalty = self.config.trade_penalty if self.config.reward_normalize else self.config.trade_penalty * self.config.initial_balance
            reward -= penalty

        self.t += 1
        if self.t >= len(self.data) - 1:
            self.done = True
        if self.config.max_steps is not None and (self.t >= self.config.max_steps):
            self.done = True

        # Liquidação forçada se episódio terminou e ainda há posição
        forced_liq = False
        if self.done and self.position_qty > 0:
            price_liq = float(self.data.loc[self.t,'close'])
            exec_price = price_liq * (1 - self.config.slippage_pct)
            gross = exec_price * self.position_qty
            fee = gross * self.config.fee_pct
            proceeds = gross - fee
            pnl = (exec_price - self.position_avg_price) * self.position_qty
            self.balance += proceeds
            self.trades.append({"t": self.t, "type": "SELL", "qty": float(self.position_qty), "price": float(exec_price), "fee": float(fee), "pnl": float(pnl), "forced": True})
            self.position_qty = 0.0
            self.position_avg_price = 0.0
            # atualiza equity pós-forced sell
            self.equity = self.balance
            forced_liq = True

        obs = self._get_observation()
        info = {
            "equity": self.equity,
            "balance": self.balance,
            "position_qty": self.position_qty,
            "position_avg_price": self.position_avg_price,
            "reward_raw": self.equity - self.equity_prev,
            "trades": len(self.trades),
            "cooldown": self.cooldown,
            "forced_hold": forced_hold,
            "forced_liq": forced_liq
        }
        return obs, reward, self.done, info

    def _compute_reward(self, traded: bool) -> float:
        delta = self.equity - self.equity_prev
        reward = delta / self.config.initial_balance if self.config.reward_normalize else delta
        if self.config.reward_unrealized_weight > 0 and self.position_qty > 0 and self.position_avg_price > 0:
            unrealized = (self._last_price() - self.position_avg_price) / self.position_avg_price
            reward += self.config.reward_unrealized_weight * unrealized
        if self.config.inactivity_penalty > 0 and not traded and self.position_qty == 0:
            reward -= self.config.inactivity_penalty
        # Penalidade por manter posição (risk control / incentivo a fechar)
        if self.config.holding_penalty > 0 and self.position_qty > 0 and self.equity > 0:
            position_pct = (self.position_qty * self._last_price()) / self.equity
            reward -= self.config.holding_penalty * position_pct
        return reward

    def _last_price(self) -> float:
        return float(self.data.loc[self.t,'close'])

    def _get_observation(self) -> np.ndarray:
        price = float(self.data.loc[self.t,'close'])
        ret_1 = float(self.data.loc[self.t,'ret_1'])
        ret_5 = float(self.data.loc[self.t,'ret_5'])
        vol_5 = float(self.data.loc[self.t,'vol_5'])
        price_rel = price / self.ref_price - 1.0
        position_value = self.position_qty * price
        position_pct = position_value / self.equity if self.equity > 0 else 0.0
        unrealized_pnl_pct = 0.0
        if self.position_qty > 0 and self.position_avg_price > 0:
            unrealized_pnl_pct = (price - self.position_avg_price) / self.position_avg_price
        obs = np.array([price_rel, ret_1, ret_5, vol_5, position_pct, unrealized_pnl_pct], dtype=np.float32)
        return obs

    # Helpers
    def get_equity_curve(self) -> np.ndarray:
        return np.array([t['equity'] for t in self.iter_equity()])

    def iter_equity(self):
        balance = self.config.initial_balance
        qty = 0.0
        avg = 0.0
        for record in self.trades:
            price = record['price']
            if record['type'] == 'BUY':
                cost = price * record['qty'] + record['fee']
                new_qty = qty + record['qty']
                if new_qty > 0:
                    avg = (avg * qty + price * record['qty']) / new_qty
                qty = new_qty
                balance -= cost
            else:  # SELL
                gross = price * record['qty']
                fee = record['fee']
                balance += gross - fee
                qty = 0.0
                avg = 0.0
            mark_price = price
            equity = balance + qty * mark_price
            yield {"t": record['t'], "equity": equity}

    def sample_random_action(self) -> int:
        return int(self.rng.integers(0, self.action_space))

if __name__ == "__main__":
    # Exemplo rápido
    n = 200
    prices = pd.DataFrame({"close": np.linspace(100, 120, n) + np.random.randn(n)})
    env = TradingEnv(prices)
    obs = env.reset()
    done = False
    total_reward = 0.0
    while not done:
        a = env.sample_random_action()
        obs, r, done, info = env.step(a)
        total_reward += r
    print("Episódio finalizado. Equity=", info['equity'], "Reward acumulado=", total_reward)
