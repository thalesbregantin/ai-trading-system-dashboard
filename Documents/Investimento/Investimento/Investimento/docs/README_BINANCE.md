# 🚀 Binance Testnet Executor — Execução Simulada

Este script executa a **estratégia de momentum otimizada** na Binance Testnet, permitindo simular trades reais sem risco.

## 📊 **Parâmetros Otimizados**

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
TOP_N = 30            # top 30 pares por volume
```

## 🔧 **Setup Binance Testnet**

### 1. Criar conta na Binance Testnet
- Acesse: https://testnet.binance.vision/
- Faça login com sua conta Binance
- Gere API Key e Secret

### 2. Configurar variáveis de ambiente
```bash
# Windows PowerShell
$env:BINANCE_API_KEY="sua_api_key_aqui"
$env:BINANCE_API_SECRET="sua_api_secret_aqui"

# Windows CMD
set BINANCE_API_KEY=sua_api_key_aqui
set BINANCE_API_SECRET=sua_api_secret_aqui

# Linux/Mac
export BINANCE_API_KEY="sua_api_key_aqui"
export BINANCE_API_SECRET="sua_api_secret_aqui"
```

### 3. Instalar dependências
```bash
pip install -r requirements-crypto.txt
```

## 🎯 **Como usar**

### Executar backtest com custos (CoinGecko)
```bash
python crypto_momentum_optimized.py
```

### Executar na Binance Testnet
```bash
python binance_testnet_executor.py
```

## 📈 **O que o script faz**

1. **Conecta ao Binance Testnet**
2. **Busca top 30 pares USDT** por volume
3. **Baixa dados históricos** (365 dias)
4. **Aplica ranking momentum** (w7/w14/wv)
5. **Executa rebalanceamento** a cada 14 dias
6. **Aplica gestão de risco** (stop/trailing)
7. **Gera logs** de execução

## 📊 **Arquivos gerados**

- `binance_equity.csv` — curva de capital
- `binance_trades.csv` — histórico de trades
- Logs no console — execução em tempo real

## ⚠️ **Observações importantes**

- **Testnet apenas** — não usa dinheiro real
- **Dados reais** — usa dados históricos da Binance
- **Simulação** — execução simula ordens reais
- **Rate limits** — respeita limites da API

## 🔄 **Próximos passos**

1. **Testar na testnet** — validar execução
2. **Ajustar parâmetros** — se necessário
3. **Migrar para produção** — trocar sandbox=False
4. **Monitorar performance** — logs e métricas

## 🎯 **Resultado esperado**

Baseado na otimização anterior:
- **+368%** de retorno (com custos)
- **Sharpe 1.92**
- **Max DD -52%**
- **21 trades** no período

---

**Pronto para testar na Binance Testnet!** 🚀
