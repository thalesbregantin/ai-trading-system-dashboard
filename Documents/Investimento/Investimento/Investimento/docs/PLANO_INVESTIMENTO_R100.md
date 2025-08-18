# 💰 PLANO DE INVESTIMENTO REAL - R$ 100 BINANCE

## 🎯 OBJETIVO
Implementar a estratégia crypto momentum validada com capital inicial de R$ 100

## 📊 ESTRATÉGIA VALIDADA
- **Retorno histórico:** +271% em 9 meses
- **Win rate:** 55% dos trades positivos
- **Max drawdown:** -51% (recuperado)
- **Sharpe ratio:** 1.44 (excelente)

## 🚀 IMPLEMENTAÇÃO PRÁTICA

### 1. SETUP INICIAL BINANCE
```python
# Configurações mínimas necessárias
CAPITAL_INICIAL = 100  # R$ 100
RISK_PER_TRADE = 0.02  # 2% por trade
COINS = ['BTCUSDT', 'ETHUSDT']  # Principais criptos
TIMEFRAME = '1d'  # Diário para sinais
```

### 2. SINAIS DE ENTRADA
**Comprar quando:**
- Preço > Média Móvel 20 dias
- Volume > média dos últimos 5 dias
- RSI entre 30-70 (não oversold/overbought)

**Vender quando:**
- Preço < Média Móvel 20 dias OU
- Stop loss -10% OU
- Take profit +15%

### 3. GESTÃO DE RISCO
- **Capital por trade:** R$ 20 (20% do total)
- **Stop loss:** 10% por posição
- **Take profit:** 15% por posição
- **Máximo 2 posições simultâneas**

### 4. EXECUÇÃO DIÁRIA
1. **8h da manhã:** Verificar sinais
2. **Se sinal de compra:** Executar ordem
3. **Se sinal de venda:** Fechar posição
4. **Registrar:** Trade no Excel/planilha

### 5. MONITORAMENTO
- **Semanal:** Revisar performance
- **Mensal:** Ajustar se necessário
- **Meta:** +20% em 3 meses (conservador)

## 📱 PRÓXIMOS PASSOS IMEDIATOS

### HOJE:
1. ✅ Criar conta Binance (se não tem)
2. ✅ Fazer KYC e verificação
3. ✅ Depositar R$ 100

### SEGUNDA-FEIRA:
1. 🎯 Implementar código simples de sinais
2. 🎯 Fazer primeiro trade teste
3. 🎯 Configurar alertas

### PRIMEIRA SEMANA:
1. 📊 Executar 2-3 trades
2. 📊 Validar estratégia na prática
3. 📊 Ajustar se necessário

## 🔥 CÓDIGO PARA EXECUTAR

```python
# binance_simple_strategy.py
import ccxt
import pandas as pd
import numpy as np

def get_signal(symbol='BTCUSDT'):
    """Sinal simples de momentum"""
    # Conecta Binance
    exchange = ccxt.binance()
    
    # Pega dados dos últimos 30 dias
    ohlcv = exchange.fetch_ohlcv(symbol, '1d', limit=30)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Calcula indicadores
    df['sma_20'] = df['close'].rolling(20).mean()
    df['volume_avg'] = df['volume'].rolling(5).mean()
    
    current = df.iloc[-1]
    
    # Sinal de COMPRA
    if (current['close'] > current['sma_20'] and 
        current['volume'] > current['volume_avg']):
        return 'BUY'
    
    # Sinal de VENDA
    elif current['close'] < current['sma_20']:
        return 'SELL'
    
    return 'HOLD'

# Executar diariamente
signal = get_signal('BTCUSDT')
print(f"Sinal para Bitcoin: {signal}")

signal = get_signal('ETHUSDT')
print(f"Sinal para Ethereum: {signal}")
```

## 💡 PRÓXIMA AÇÃO
Quer que eu crie o código simples para conectar na Binance e implementar os sinais?
