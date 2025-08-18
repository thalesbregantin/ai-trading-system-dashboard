# Crypto Momentum Selector — Backtest Semanal (CoinGecko)

Este projeto seleciona automaticamente as **moedas mais fortes** (momentum + volume) e faz um **backtest semanal**,  
rebalanceando para a #1 do ranking. Útil para estudar se a estratégia poderia acelerar o crescimento de um capital pequeno.

> **⚠️ Aviso:** uso educacional. Não é recomendação de investimento.  
> Criptomoedas são extremamente voláteis. Custos, impostos e riscos devem ser considerados.

---

## 📌 O que o script faz
- Coleta as **top N moedas por volume** no CoinGecko (exclui stablecoins)
- Baixa histórico de preços/volumes (diário)
- Calcula **retorno 7d**, **retorno 14d**, **volume médio 14d**
- Cria **ranking** combinando momentum e volume
- Backtest com **rebalanceamento semanal** na #1 do ranking
- Exporta:
  - `trades_momentum.csv` — histórico de operações simuladas
  - `equity_curve_momentum.csv` — evolução do capital
- Imprime métricas no console (retorno total, CAGR, drawdown, Sharpe)

---

## ⚙️ Requisitos
Instalar dependências com:
```bash
pip install -r requirements-momentum.txt
