# 🤖 AI Trading System - Sistema de Trading Inteligente

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **Sistema de Trading Quantitativo Avançado** com Machine Learning, Otimização Genética e Walk-Forward Analysis para criptomoedas.

## 🚀 Visão Geral

Este é um sistema de trading quantitativo de **vanguarda** que combina:

- **🤖 Machine Learning (XGBoost)** para previsão de direção do mercado
- **🧬 Algoritmos Genéticos (DEAP)** para otimização de parâmetros
- **📊 Walk-Forward Analysis** para validação robusta
- **💰 Dimensionamento Inteligente** de posições baseado na confiança do modelo
- **🎯 Triple Barrier Labeling** para targets de ML

### ✨ Características Principais

- **🔄 Otimização Automática**: Parâmetros otimizados via algoritmo genético
- **📈 Feature Engineering Avançado**: 15+ indicadores técnicos
- **🛡️ Validação Robusta**: Walk-Forward para evitar overfitting
- **⚡ Performance**: Otimizado para execução rápida
- **📊 Análise Completa**: Métricas de risco e retorno detalhadas

## 📁 Estrutura do Projeto

```
Investimento/
├── 📁 core/                    # Sistema principal (v8.0)
│   ├── genetic_optimizer.py    # Otimizador genético final
│   └── walk_forward_optimizer.py # Walk-Forward principal
├── 📁 archive/                 # Versões antigas (backup)
├── 📁 scripts/                 # Scripts de execução
│   └── run_optimization.bat    # Executar otimização
├── 📁 logs/                    # Logs de execução
├── 📁 data/                    # Dados de mercado
├── 📁 results/                 # Resultados da otimização
├── 📁 cache/                   # Cache de dados
└── 📁 docs/                    # Documentação
```

## 🛠️ Instalação

### Pré-requisitos

- Python 3.8+
- pip
- Git

### Setup Rápido

```bash
# 1. Clonar o repositório
git clone https://github.com/thalesbregantin/ai-trading-system-dashboard.git
cd ai-trading-system-dashboard

# 2. Criar ambiente virtual
python -m venv .venv

# 3. Ativar ambiente virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Configurar variáveis de ambiente
cp env.example .env
# Editar .env com suas configurações
```

## 🚀 Como Usar

### Execução Rápida (Recomendado)

```bash
# Usar o script batch (Windows)
scripts/run_optimization.bat

# Ou via terminal
python -c "from core.walk_forward_optimizer import WalkForwardOptimizerV7; optimizer = WalkForwardOptimizerV7(); results = optimizer.run()"
```

### Execução Manual

```bash
# 1. Ativar ambiente virtual
.venv\Scripts\activate

# 2. Executar otimização
python -c "from core.walk_forward_optimizer import WalkForwardOptimizerV7; optimizer = WalkForwardOptimizerV7(); results = optimizer.run()"

# 3. Verificar resultados
# - Logs: logs/genetic_optimizer_v8_production.log
# - Resultados: results/walk_forward_results_v7_intelligent_sizing.json
```

## 📊 Funcionalidades

### 🧬 Otimização Genética
- **População**: 30 indivíduos
- **Gerações**: 20
- **Fitness Multi-objetivo**: Consistência, Lucratividade, Risco
- **Parâmetros Otimizados**: 9 parâmetros de trading

### 🤖 Machine Learning
- **Modelo**: XGBoost Classifier
- **Features**: 15+ indicadores técnicos
- **Target**: Triple Barrier Labeling
- **Validação**: Out-of-sample testing

### 📈 Indicadores Técnicos
- RSI, SMA, ATR
- MACD, Bollinger Bands
- OBV, Momentum
- Volatilidade, Features temporais

### 🎯 Walk-Forward Analysis
- **Treino**: 60% dos dados
- **Teste**: 20% dos dados
- **Step**: 20% (janela deslizante)
- **Validação**: Sequencial out-of-sample

## 📊 Métricas de Performance

O sistema calcula e reporta:

- **💰 Lucro Total**: Retorno absoluto
- **📊 Sharpe Ratio**: Retorno ajustado ao risco
- **📉 Max Drawdown**: Máxima perda consecutiva
- **🎯 Win Rate**: Taxa de acerto
- **📈 Profit Factor**: Lucro bruto / Perda bruta
- **🔄 Taxa de Consistência**: % de janelas lucrativas
- **🎯 Score de Estabilidade**: Estabilidade dos parâmetros

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```env
# Binance API (opcional para dados em tempo real)
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key

# Configurações do Sistema
LOG_LEVEL=INFO
DATA_DIR=data
RESULTS_DIR=results
```

### Parâmetros Otimizáveis

```python
param_ranges = {
    'atr_period': (10, 20),
    'atr_stop_loss_multiplier': (1.0, 2.5),
    'atr_take_profit_multiplier': (1.5, 4.0),
    'hold_period': (6, 24),
    'entry_threshold': (0.60, 0.75),
    'max_bet_size_pct': (0.1, 0.25),
    'n_estimators': (50, 150),
    'max_depth': (3, 5),
    'learning_rate': (0.01, 0.1),
}
```

## 📈 Resultados Esperados

### Exemplo de Output

```
🎯 RESUMO FINAL v8.0 - PRODUÇÃO:
💰 Lucro Total: $1,234.56
📊 Sharpe Ratio: 1.85
🎯 Estabilidade: 87.3/100
🤖 Confiança média: 0.78
💰 Tamanho médio da aposta: 0.15%
📈 Total de trades: 156
🎯 Win rate: 68.5%
```

## 🔍 Monitoramento

### Logs
- **Arquivo**: `logs/genetic_optimizer_v8_production.log`
- **Nível**: INFO, WARNING, ERROR
- **Formato**: Timestamp + Mensagem detalhada

### Resultados
- **JSON**: `results/walk_forward_results_v7_intelligent_sizing.json`
- **Métricas**: Performance completa
- **Parâmetros**: Melhores parâmetros encontrados

## 🚀 Próximos Passos

1. **✅ Sistema Base**: Implementado e testado
2. **🔄 Suporte Parquet**: Para dados mais eficientes
3. **📊 Dashboard Web**: Interface visual
4. **🤖 Trading Live**: Execução automática
5. **📈 Backtesting Avançado**: Mais métricas

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Thales Bregantin**
- GitHub: [@thalesbregantin](https://github.com/thalesbregantin)
- LinkedIn: [Thales Bregantin](https://www.linkedin.com/in/thalesbregantin/)

## ⚠️ Disclaimer

Este software é fornecido "como está", sem garantias. Trading envolve riscos significativos. Use por sua conta e risco.

---

**⭐ Se este projeto te ajudou, considere dar uma estrela no GitHub!**
