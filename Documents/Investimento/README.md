# 🤖 AI Trading System - Sistema de Trading Inteligente

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![CCXT](https://img.shields.io/badge/CCXT-4.5+-green.svg)
![Binance](https://img.shields.io/badge/Binance-API-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Sistema de Trading Automatizado com IA para Criptomoedas**

[🚀 Começar](#-como-usar) • [📊 Funcionalidades](#-funcionalidades-principais) • [🛠️ Configuração](#-configuração) • [📈 Performance](#-performance)

</div>

---

## 📋 Descrição

Sistema avançado de trading automatizado que combina **análise técnica**, **detecção de pumps em tempo real** e **gerenciamento inteligente de risco** para operar criptomoedas na Binance. Desenvolvido com foco em **micro-trading** e **estratégias de baixo risco**.

### 🎯 Características Principais
- **🤖 IA Inteligente**: Sistema de aprendizado contínuo com workers paralelos
- **⚡ Tempo Real**: Detecção de pumps em tempo real com análise de contexto
- **🛡️ Gerenciamento de Risco**: Stop loss e take profit automáticos
- **📊 Análise Técnica**: SMA, RSI, análise de tendência e momentum
- **🔄 Ciclos Otimizados**: Operação em ciclos de 30 minutos
- **💰 Micro-trading**: Operações com valores pequenos ($15-$30)

## 🚀 Funcionalidades Principais

### 📊 Sistema de Trading
- **Detecção de Pumps**: Análise de movimentos rápidos de alta
- **Análise Técnica**: SMA, RSI, análise de tendência
- **Gerenciamento de Risco**: Stop loss e take profit automáticos
- **Micro-trading**: Operações com valores pequenos ($10-$20)
- **Ciclos de 30 minutos**: Conforme princípios de trading

### 🧠 Sistema de IA
- **Treinamento Contínuo**: Workers paralelos para melhorar a IA
- **Análise de Performance**: Métricas detalhadas de lucratividade
- **Auto-correção**: Sistema que aprende com os resultados

## 📁 Estrutura do Projeto

```
├── parallel_trading_system.py      # Sistema principal de trading
├── extended_training_with_workers.py  # Sistema de treinamento IA
├── market_analyzer.py              # Análise de mercado
├── performance_analyzer.py         # Análise de performance
├── singapore_ai_trading_research.md # Pesquisa sobre IA em Singapura
├── verified_trading_pairs.json     # Pares de trading verificados
├── logs/                           # Logs do sistema
├── data/                           # Dados históricos
├── models/                         # Modelos de IA treinados
└── README.md                       # Este arquivo
```

## 🛠️ Configuração e Instalação

### 📋 Pré-requisitos
- Python 3.11 ou superior
- Conta na Binance com API habilitada
- Conhecimento básico de trading de criptomoedas

### 🔧 Instalação

#### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/ai-trading-system.git
cd ai-trading-system
```

#### 2. Configure o Ambiente Virtual
```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente (Windows)
.venv\Scripts\activate

# Ativar ambiente (Linux/Mac)
source .venv/bin/activate
```

#### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

#### 4. Configurar API da Binance
```bash
# Criar arquivo .env
cp env.example .env

# Editar .env com suas chaves da Binance
BINANCE_API_KEY=sua_api_key_aqui
BINANCE_SECRET_KEY=sua_secret_key_aqui
```

#### 5. Configurar Permissões da API
Na Binance, certifique-se de que sua API tem as seguintes permissões:
- ✅ **Spot & Margin Trading** (Obrigatório)
- ✅ **Read Info** (Obrigatório)
- ❌ **Futures** (Não necessário)
- ❌ **Withdraw** (Nunca habilitar)

### 🚀 Como Usar

### 2. Treinamento da IA
```bash
# Terminal 1 - Treinamento contínuo
python extended_training_with_workers.py
```

### 3. Sistema de Trading
```bash
# Terminal 2 - Sistema principal
python parallel_trading_system.py
```

## 🏗️ Arquitetura do Sistema

### 📊 Fluxo de Operação
```
1. 🔍 Análise de Mercado
   ├── Escaneamento de 25 pares USDT
   ├── Detecção de pumps em tempo real
   └── Análise de contexto (tendência, RSI)

2. 🤖 Decisão de Trading
   ├── Filtro de qualidade de sinais
   ├── Verificação de posições abertas
   └── Cálculo de tamanho da posição

3. ⚡ Execução
   ├── Ordem limite (proteção contra slippage)
   ├── Monitoramento de execução
   └── Log detalhado da operação

4. 📈 Gerenciamento
   ├── Take profit automático (2.5%)
   ├── Stop loss automático (1.5%)
   └── Timeout de 8 minutos
```

## 📈 Parâmetros do Sistema

### 💰 Configuração de Trading
| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| **Trade Mínimo** | $15 USDT | Valor mínimo por operação |
| **Trade Máximo** | $30 USDT | Valor máximo por operação |
| **Ciclo de Trading** | 30 min | Intervalo entre análises |
| **Take Profit** | 2.5% | Lucro alvo automático |
| **Stop Loss** | 1.5% | Perda máxima permitida |
| **Timeout** | 8 min | Tempo máximo de hold |
| **Max Trades/Ciclo** | 2 | Máximo de trades por ciclo |
| **Max Trades Ativos** | 3 | Máximo de posições simultâneas |

### 📊 Análise Técnica
| Indicador | Valor | Descrição |
|-----------|-------|-----------|
| **SMA Curta** | 20 períodos | Média móvel de curto prazo |
| **SMA Longa** | 50 períodos | Média móvel de longo prazo |
| **RSI** | 14 períodos | Índice de força relativa |
| **RSI Sobrecomprado** | 70 | Limite superior do RSI |
| **RSI Sobrevendido** | 30 | Limite inferior do RSI |

### ⚡ Detecção de Pumps
| Threshold | Valor | Descrição |
|-----------|-------|-----------|
| **Pump 1min** | 0.5% | Movimento em 1 minuto |
| **Pump 5min** | 0.3% | Movimento em 5 minutos |
| **Momentum** | 0.2% | Momentum em 1 minuto |

## 🔧 Arquivos Principais

### `parallel_trading_system.py`
Sistema principal que:
- Conecta com Binance
- Detecta oportunidades de pump
- Executa trades automaticamente
- Analisa contexto de mercado
- Salva logs detalhados

### `extended_training_with_workers.py`
Sistema de treinamento que:
- Executa workers paralelos
- Treina modelos de IA
- Analisa performance
- Salva resultados

### `market_analyzer.py`
Ferramenta de análise que:
- Escaneia todos os pares USDT
- Testa diferentes thresholds
- Identifica oportunidades

### `performance_analyzer.py`
Análise de performance que:
- Calcula métricas de lucratividade
- Analisa trades executados
- Gera relatórios

## 📊 Monitoramento e Logs

### 📁 Estrutura de Logs
```
logs/
├── parallel_trades.jsonl      # Trades executados (detalhado)
├── parallel_cycles.jsonl      # Ciclos de trading (resumo)
├── parallel_performance.json  # Performance geral (métricas)
└── parallel_training.jsonl    # Logs de treinamento IA
```

### 📈 Métricas Monitoradas
| Métrica | Descrição |
|---------|-----------|
| **Win Rate** | Taxa de trades lucrativos |
| **Profit per Trade** | Lucro médio por operação |
| **Sharpe Ratio** | Retorno ajustado ao risco |
| **Max Drawdown** | Maior perda consecutiva |
| **Total P&L** | Lucro/prejuízo total |
| **Trades Executados** | Número total de trades |
| **Context Analysis** | Análise de contexto de mercado |

### 🔍 Exemplo de Log de Trade
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "symbol": "DOGE/USDT",
  "side": "BUY",
  "action": "COMPRA",
  "amount": 0.123456,
  "price": 0.08765,
  "value_usdt": 15.00,
  "order_id": "123456789",
  "pump_reason": "PUMP_1MIN_0.8%",
  "status": "executed",
  "context": "BULLISH_RSI_45"
}
```

### 📊 Dashboard de Performance
O sistema gera automaticamente:
- **Relatórios diários** de performance
- **Análise de contexto** de mercado
- **Métricas de risco** em tempo real
- **Logs detalhados** para auditoria

## 🎯 Estratégia de Trading

### Princípios Aplicados
1. **Estratégia consistente** - Nunca muda a técnica
2. **Gerenciamento de risco** - Stop loss e take profit
3. **Máximo de entradas** - 2 trades por ciclo
4. **Análise de contexto** - A cada 30 minutos
5. **Micro-trading** - Frações pequenas

### Detecção de Pumps
- Movimento >0.5% em 1 minuto
- Movimento >0.3% em 5 minutos
- Momentum >0.2% em 1 minuto
- Análise de tendência (BULLISH/BEARISH/SIDEWAYS)

## 🔒 Segurança

### API Keys
- Chaves da Binance configuradas
- Permissões limitadas (apenas trading)
- Rate limiting implementado

### Gerenciamento de Risco
- Valor máximo por trade: $20
- Stop loss automático: 1.5%
- Máximo 2 trades por ciclo
- Análise de contexto antes de cada trade

## 📈 Performance

### Métricas Monitoradas
- Win rate (taxa de acerto)
- Profit per trade (lucro por trade)
- Sharpe ratio
- Maximum drawdown
- Total profit/loss

### Otimização
- Sistema auto-corretivo
- Análise de performance contínua
- Ajuste de parâmetros baseado em resultados

## 🛡️ Segurança e Boas Práticas

### 🔐 Segurança da API
- **Chaves da Binance**: Armazenadas em arquivo `.env` (nunca no código)
- **Permissões Limitadas**: Apenas trading spot (sem futures/withdraw)
- **Rate Limiting**: Implementado para evitar bloqueios
- **IP Restriction**: Configure restrição de IP na Binance

### 💡 Boas Práticas
- **Teste em Testnet**: Sempre teste primeiro na Binance Testnet
- **Valores Pequenos**: Comece com valores mínimos ($15)
- **Monitoramento**: Sempre monitore o sistema em execução
- **Backup**: Mantenha backup dos logs e configurações

## 🚨 Troubleshooting

### Problemas Comuns
| Problema | Solução |
|----------|---------|
| **API Key inválida** | Verifique as chaves no arquivo `.env` |
| **Rate limit atingido** | Aguarde alguns minutos e reinicie |
| **Saldo insuficiente** | Verifique se tem USDT suficiente |
| **Par não encontrado** | Verifique se o par está na lista `trading_pairs` |

### Logs de Debug
```bash
# Verificar logs em tempo real
tail -f logs/parallel_trades.jsonl

# Verificar performance
cat logs/parallel_performance.json
```

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### 📋 Checklist para Contribuição
- [ ] Código segue as convenções do projeto
- [ ] Testes passam localmente
- [ ] Documentação atualizada
- [ ] Logs de debug incluídos

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ⚠️ Disclaimer Legal

**⚠️ AVISO IMPORTANTE**

Este software é fornecido "como está", sem garantias de qualquer tipo. Trading de criptomoedas envolve **risco significativo** e pode resultar em **perda total do capital investido**.

### 🚨 Riscos Inerentes
- **Volatilidade extrema** dos mercados de criptomoedas
- **Perda total** do capital investido
- **Falhas técnicas** do sistema ou da exchange
- **Regulamentações** que podem afetar o trading

### 💡 Recomendações
- **Use apenas** dinheiro que pode perder completamente
- **Teste extensivamente** antes de usar com dinheiro real
- **Monitore constantemente** o sistema em execução
- **Mantenha** valores pequenos por operação
- **Consulte** um consultor financeiro se necessário

**O desenvolvedor não se responsabiliza por perdas financeiras resultantes do uso deste software.**

---

<div align="center">

**🤖 Desenvolvido com ❤️ para trading inteligente e responsável**

[⭐ Star no GitHub](https://github.com/seu-usuario/ai-trading-system) • [🐛 Reportar Bug](https://github.com/seu-usuario/ai-trading-system/issues) • [💡 Sugerir Feature](https://github.com/seu-usuario/ai-trading-system/issues)

</div>
