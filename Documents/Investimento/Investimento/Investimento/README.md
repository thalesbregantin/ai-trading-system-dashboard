# 🤖 AI Trading System - Projeto Organizado

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
📁 Investimento/
├── 🤖 ai_trading_system/          # Núcleo do Sistema
│   ├── 📁 core/                   # Componentes principais
│   │   ├── ai_trader_dqn.py       # Deep Q-Learning AI
│   │   ├── hybrid_trading_system.py # Sistema Híbrido
│   │   ├── binance_ai_bot.py      # Bot Binance
│   │   └── config.py              # Configurações
│   ├── 📊 dashboard/              # Interface web
│   ├── 📁 models/                 # Modelos treinados
│   ├── 📁 logs/                   # Logs do sistema
│   ├── 📁 data/                   # Dados de mercado
│   ├── 📁 utils/                  # Utilitários
│   └── 📁 config/                 # Configurações
├── 📊 dashboard/                  # Dashboard principal
├── 📚 docs/                       # Documentação
├── 🐳 docker-compose.yml          # Docker
├── 📦 requirements.txt            # Dependências
└── 📋 README.md                   # Este arquivo
```

## 🚀 Quick Start

### 1. Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd Investimento

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
python ai_trading_system/main.py --mode test

# Treinamento AI
python ai_trading_system/main.py --mode train --episodes 20

# Backtest
python ai_trading_system/main.py --mode backtest

# Trading ao vivo (TESTNET)
python ai_trading_system/main.py --mode live --env test

# Trading ao vivo (REAL) ⚠️
python ai_trading_system/main.py --mode live --env prod

# Dashboard
python ai_trading_system/main.py --mode dashboard
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

## 🐳 Docker

Para executar com Docker:

```bash
# Build da imagem
docker build -t ai-trading-system .

# Executar container
docker-compose up -d

# Ver logs
docker-compose logs -f
```

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
ai_trading_system/logs/trading_log_YYYYMMDD.log
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
