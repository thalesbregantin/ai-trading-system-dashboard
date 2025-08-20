# 🔗 MCP (Model Context Protocol) Module

## 📋 Descrição
Módulo MCP para integração do sistema de IA com ferramentas externas de trading.

## 🎯 Objetivo
Conectar a IA com APIs da Binance para obter dados em tempo real e executar trades automaticamente.

## 📁 Estrutura

```
mcp/
├── __init__.py              # Módulo principal
├── mcp_server_basic.py      # Servidor MCP básico
├── README.md                # Esta documentação
└── tools/                   # Ferramentas MCP (futuro)
```

## 🚀 Funcionalidades Atuais

### BasicMCPServer
- **get_market_data()**: Obter dados de mercado
- **get_balance()**: Obter saldo da conta
- **detect_pump_basic()**: Detectar pumps simples
- **get_trading_pairs()**: Listar pares disponíveis

## 🧪 Como Testar

```bash
# Testar servidor MCP básico
python mcp/mcp_server_basic.py
```

## 📊 Exemplo de Uso

```python
from mcp import BasicMCPServer

# Criar servidor
server = BasicMCPServer()

# Obter dados de mercado
data = server.get_market_data("BTC/USDT")
print(f"Preço BTC: ${data['current_price']}")

# Detectar pump
pump = server.detect_pump_basic("DOGE/USDT")
if pump['should_trade']:
    print(f"Pump detectado: {pump['pump_reason']}")
```

## 🔄 Próximas Etapas

1. **MCP Client**: Cliente para conectar com IA
2. **Tools Avançadas**: Análise técnica, execução de trades
3. **Integração Completa**: Sistema autônomo

## 📈 Benefícios Esperados

- **Automação**: IA toma decisões automaticamente
- **Tempo Real**: Dados instantâneos do mercado
- **Precisão**: Decisões baseadas em dados atuais
- **Escalabilidade**: Sistema modular e expansível
