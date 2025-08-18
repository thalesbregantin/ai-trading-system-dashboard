"""Funções de métricas para avaliação do agente.
"""
from __future__ import annotations
import numpy as np
from typing import List, Dict, Any

# =============================
# Métricas de série de equity
# =============================

def max_drawdown(equity: np.ndarray) -> float:
    if len(equity) == 0:
        return 0.0
    peaks = np.maximum.accumulate(equity)
    dd = (equity - peaks) / peaks
    return float(dd.min())  # valor negativo

def sharpe_ratio(returns: np.ndarray, risk_free: float = 0.0, eps: float = 1e-9) -> float:
    if returns.size < 2:
        return 0.0
    excess = returns - risk_free
    std = excess.std()
    if std < eps:
        return 0.0
    return float(excess.mean() / std * np.sqrt(252))  # assume diário

def sortino_ratio(returns: np.ndarray, risk_free: float = 0.0, eps: float = 1e-9) -> float:
    if returns.size < 2:
        return 0.0
    excess = returns - risk_free
    downside = excess[excess < 0]
    if downside.size == 0:
        return 0.0
    denom = downside.std()
    if denom < eps:
        return 0.0
    return float(excess.mean() / denom * np.sqrt(252))

# =============================
# Métricas de trades
# =============================

def trade_metrics(trades: List[Dict[str, Any]]) -> Dict[str, float]:
    sells = [t for t in trades if t.get('type') == 'SELL']
    if not sells:
        return {"trades": 0, "win_rate": 0.0, "avg_win": 0.0, "avg_loss": 0.0, "profit_factor": 0.0}
    pnls = [t.get('pnl', 0.0) for t in sells]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    win_rate = len(wins) / len(sells) if sells else 0.0
    avg_win = np.mean(wins) if wins else 0.0
    avg_loss = np.mean(losses) if losses else 0.0
    total_win = sum(wins) if wins else 0.0
    total_loss = abs(sum(losses)) if losses else 0.0
    profit_factor = (total_win / total_loss) if total_loss > 0 else (total_win if total_win > 0 else 0.0)
    return {
        "trades": len(sells),
        "win_rate": float(win_rate),
        "avg_win": float(avg_win),
        "avg_loss": float(avg_loss),
        "profit_factor": float(profit_factor)
    }

# =============================
# Função principal de agregação
# =============================

def compute_episode_metrics(equity_series: List[float], trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    eq = np.array(equity_series, dtype=np.float32)
    if eq.size < 2:
        returns = np.array([], dtype=np.float32)
    else:
        returns = np.diff(eq) / eq[:-1]
    mdd = max_drawdown(eq)
    sr = sharpe_ratio(returns)
    sor = sortino_ratio(returns)
    tmet = trade_metrics(trades)
    result = {
        "final_equity": float(eq[-1]) if eq.size else 0.0,
        "return_pct": float((eq[-1] / eq[0] - 1.0) * 100) if eq.size else 0.0,
        "max_drawdown_pct": float(mdd * 100),
        "sharpe": sr,
        "sortino": sor,
    }
    result.update(tmet)
    return result

if __name__ == "__main__":
    # Teste rápido
    eq = [1000, 1010, 1005, 1020, 990, 995, 1030]
    trades = [
        {"type":"BUY", "pnl":0},
        {"type":"SELL", "pnl":10},
        {"type":"BUY", "pnl":0},
        {"type":"SELL", "pnl":-5},
    ]
    print(compute_episode_metrics(eq, trades))
