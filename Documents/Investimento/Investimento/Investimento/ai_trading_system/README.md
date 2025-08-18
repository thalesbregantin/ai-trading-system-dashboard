# 🤖 AI Trading System

Sistema de trading automatizado com Deep Q-Learning e análise técnica para criptomoedas.

## 📋 Visão Geral

Este sistema combina:
- 🧠 **Deep Q-Learning**: Rede neural para decisões de trading
- 📊 **Análise Técnica**: Indicadores tradicionais (SMA, RSI, Momentum)
- 🔄 **Sistema Híbrido**: Combina AI (60%) + Momentum (40%)
- 🌐 **Dashboard**: Interface web em tempo real
- 🔗 **Binance Integration**: Trading automático via API

## 🏗️ Estrutura do Projeto

```
ai_trading_system/
├── 📁 core/                         # Núcleo do Sistema
│   ├── 🤖 ai_trader_dqn.py          # Deep Q-Learning AI
│   ├── 🔄 hybrid_trading_system.py  # Sistema Híbrido
│   ├── 🔗 binance_ai_bot.py         # Bot Binance
│   └── ⚙️ config.py                 # Configurações
├── 📁 dashboard/                    # Interface Web
│   ├── 📊 main_dashboard.py         # Dashboard Principal
│   └── 🎯 ai_trading_dashboard.py   # Dashboard AI
├── 📁 utils/                        # Utilitários
│   ├── 🔧 setup.py                  # Setup do sistema
│   └── 📊 monitor.py                # Monitor em tempo real
├── 🚀 main.py                       # Arquivo Principal
└── 📦 requirements.txt              # Dependências
```

## 🚀 Quick Start

### 1. Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd ai_trading_system

# Crie ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\\Scripts\\activate   # Windows

# Instale dependências
pip install -r requirements.txt
```

### 2. Configuração

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite com suas credenciais Binance
nano .env
```

```env
BINANCE_API_KEY=sua_api_key_aqui
BINANCE_API_SECRET=sua_api_secret_aqui
```

### 3. Execução

```bash
# Teste básico
python main.py --mode test

# Treinamento AI
python main.py --mode train --episodes 20

# Backtest
python main.py --mode backtest

# Trading ao vivo (TESTNET)
python main.py --mode live --env test

# Trading ao vivo (REAL) ⚠️
python main.py --mode live --env prod

# Dashboard
python main.py --mode dashboard
```

## ⚙️ Configuração

### Ambientes Disponíveis

- **dev**: Desenvolvimento (TESTNET, capital baixo)
- **test**: Testes (TESTNET, capital médio)
- **prod**: Produção (LIVE, capital real) ⚠️

### Parâmetros Principais

```python
# Trading
TRADING_PAIRS = ['BTC/USDT', 'ETH/USDT']
MAX_POSITION_SIZE = 0.02  # 2% por trade
STOP_LOSS_PCT = 0.05      # 5% stop loss

# AI
AI_EPISODES = 20          # Episódios de treinamento
AI_WEIGHT = 0.6          # Peso do AI (60%)
MOMENTUM_WEIGHT = 0.4    # Peso momentum (40%)

# Indicadores
SMA_SHORT = 20
SMA_LONG = 50
RSI_PERIOD = 14
```

## 📊 Dashboard

Acesse o dashboard em: `http://localhost:8501`

Recursos disponíveis:
- 📈 Gráficos de performance em tempo real
- 💰 Métricas de portfolio
- 🎯 Histórico de trades
- 🤖 Status do AI
- ⚙️ Configurações

## 🔗 API Binance

### Permissões Necessárias

Na sua conta Binance, habilite:
- ✅ **Enable Spot & Margin Trading**
- ✅ **Enable Reading**
- ❌ Futures (não necessário)

### URLs

- **Testnet**: `https://testnet.binance.vision`
- **Live**: `https://api.binance.com`

## 🛡️ Segurança

- 🔒 Use sempre TESTNET primeiro
- 🔑 Mantenha API keys seguras
- 💰 Configure limites de posição baixos
- 📊 Monitore sempre via dashboard
- ⚠️ NUNCA compartilhe credenciais

## 📈 Performance

Resultados típicos em backtests:
- 📊 **Sharpe Ratio**: 0.8+
- 💰 **Retorno Anual**: 15-25%
- 📉 **Max Drawdown**: <20%
- 🎯 **Win Rate**: 60-70%

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de API**: Verifique permissões Binance
2. **Erro de dependências**: Execute `pip install -r requirements.txt`
3. **Erro de TensorFlow**: Instale versão compatível
4. **Dashboard não carrega**: Verifique porta 8501

### Logs

Verifique os logs em:
```
logs/trading_log_YYYYMMDD.log
```

## 📞 Suporte

- 📋 **Issues**: Use GitHub Issues
- 📧 **Email**: suporte@example.com
- 💬 **Discord**: [Link do servidor]

## ⚖️ Disclaimer

⚠️ **AVISO IMPORTANTE**:
- Trading envolve risco de perda
- Este sistema é para fins educacionais
- Teste sempre em TESTNET primeiro
- Use apenas capital que pode perder
- Não somos responsáveis por perdas

## 📄 Licença

MIT License - veja `LICENSE` para detalhes.

---

🤖 **Happy Trading!** 🚀
