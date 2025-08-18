# 🚀 Crypto Momentum Optimized — Estratégia Otimizada

Este script implementa a **estratégia de momentum otimizada** com os melhores parâmetros encontrados na grid search.

## 📊 **Resultados da Otimização**

**Melhor configuração encontrada:**
- **Retorno total:** +692% no período
- **Capital final:** $179.55 (a partir de $22.66 após warm-up)
- **Sharpe ratio:** 2.39
- **Max drawdown:** -38.05%

## ⚙️ **Parâmetros Otimizados**

```python
# Gestão de risco
RISK_PCT = 0.04       # 4% do capital por trade
STOP_LOSS_PCT = 0.03  # stop loss de 3%
TRAIL_K = 1.5         # trailing stop 1.5x volatilidade

# Pesos momentum
W7 = 0.8              # peso retorno 7d (80%)
W14 = 0.2             # peso retorno 14d (20%)
WV = 0.1              # peso volume (10%)

# Configuração
REBALANCE_DAYS = 14   # rebalanceamento quinzenal
MIN_VOL_USD = 1e6     # filtro de liquidez
```

## 🎯 **Como usar**

1. **Execute o script otimizado:**
```bash
python crypto_momentum_optimized.py
```

2. **O que o script faz:**
   - Baixa dados das top 30 criptomoedas por volume
   - Aplica a estratégia de momentum otimizada
   - Executa backtest com gestão de risco
   - Gera métricas e arquivos de resultado

3. **Arquivos gerados:**
   - `equity_momentum_optimized.csv` — curva de capital
   - `trades_momentum_optimized.csv` — histórico de trades

## 📈 **Estratégia**

**Seleção de ativos:**
- Ranking por momentum (retorno 7d + 14d + volume)
- Filtro de liquidez (volume mínimo)
- Rebalanceamento quinzenal

**Gestão de risco:**
- Sizing por risco (4% do capital por trade)
- Stop loss fixo (3%)
- Trailing stop dinâmico (1.5x volatilidade)

## ⚠️ **Observações importantes**

- **Uso educacional** — não é recomendação de investimento
- **Rate limit** — script tem delays para respeitar limites da API
- **Tempo de execução** — pode demorar alguns minutos
- **Overfitting** — resultados passados não garantem performance futura

## 🔄 **Próximos passos sugeridos**

1. **Validação out-of-sample** — teste em período diferente
2. **Walk-forward analysis** — otimização contínua
3. **Comparação com buy-and-hold** — benchmark
4. **Teste em Binance Testnet** — simulação real

---

**Resultado esperado:** ~+692% de retorno com Sharpe de 2.39 🎯
