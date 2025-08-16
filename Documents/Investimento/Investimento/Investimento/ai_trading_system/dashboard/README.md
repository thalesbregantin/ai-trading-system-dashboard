# 🚀 Crypto Momentum Strategy Dashboard

Um dashboard interativo e abrangente para análise da estratégia de momentum em criptomoedas, construído com Streamlit e Plotly.

## 📊 Visão Geral

Este dashboard fornece análise em tempo real da performance da estratégia crypto momentum, incluindo:

- **📈 Métricas de Performance**: Retorno total, Sharpe ratio, win rate
- **💹 Análise de Trades**: Histórico detalhado e padrões de trading  
- **⚠️ Análise de Risco**: VaR, drawdowns, volatilidade
- **🔄 Correlação de Mercado**: GPS para switching single/multi-asset
- **📊 Métricas Avançadas**: 25+ indicadores profissionais

## 🚀 Como Executar

### Método 1: Launcher Automático
```bash
python run_dashboard.py
```

### Método 2: Streamlit Direto
```bash
streamlit run dashboard/main_dashboard.py
```

### Método 3: Comando Específico
```bash
streamlit run dashboard/main_dashboard.py --server.port=8501
```

## 📋 Pré-requisitos

### Dependências Python
```
streamlit>=1.48.0
plotly>=6.2.0
pandas>=2.3.1
numpy>=2.3.2
```

### Arquivos de Dados Necessários
O dashboard precisa dos seguintes arquivos na pasta `data/`:

- `equity_momentum_optimized.csv` - Curva de equity
- `trades_momentum_optimized.csv` - Histórico de trades
- `momentum_correlation.csv` - Dados de correlação
- `trades_multi_asset.csv` - Trades multi-ativo
- `advanced_metrics_report.csv` - Métricas avançadas

## 🎯 Funcionalidades

### 🏠 Dashboard Principal (`main_dashboard.py`)

#### 📊 Key Performance Indicators
- Portfolio value atual e delta
- Sharpe ratio com alertas
- Maximum drawdown
- Win rate
- Total de trades

#### 📈 Portfolio Performance
- Curva de equity interativa
- Linha de break-even
- Zoom temporal
- Hover com detalhes

#### 💹 Trades Analysis
- P&L por trade (bar chart)
- Performance por ativo
- Filtros por período/ativo
- Distribuição de resultados

#### 🔄 Market Correlation Analysis
- Correlation GPS temporal
- Zonas de alta/baixa correlação
- Estatísticas de correlation regime
- Indicador de trend atual

#### ⚡ Advanced Metrics
- VaR e CVaR
- Ratios avançados (Calmar, Sortino)
- Métricas de volatilidade
- Information ratio

#### ⚖️ Strategy Comparison
- Single vs Multi-asset
- Métricas comparativas
- Gráfico de performance lado a lado

### 📊 Trade Analytics (`pages/Trade_Analytics.py`)

#### Filtros Avançados
- Por ativo específico
- Por resultado (profitable/losing)
- Por duração (buckets temporais)

#### Análises Detalhadas
- Scatter plot: Return vs Duration
- Distribuição de retornos
- Timeline interativa de trades
- Tabela detalhada com download

#### Métricas Específicas
- Win rate filtrado
- Retorno médio por filtro
- Duração média
- Análise de outliers

### ⚠️ Risk Analysis (`pages/Risk_Analysis.py`)

#### Métricas de Risco
- Value at Risk (95%, 99%)
- Conditional VaR (Expected Shortfall)
- Maximum drawdown e duração
- Volatilidade anualizada
- Sortino ratio
- Beta vs mercado

#### Visualizações de Risco
- Underwater equity curve
- Distribuição de retornos com VaR
- Histograma de drawdowns
- Risk assessment scoring

#### Risk Assessment Engine
- Score de risco 0-8
- Categorização: Low/Medium/High/Very High
- Fatores de risco identificados
- Recomendações automáticas

## 🎨 Customização

### Temas
O dashboard usa tema escuro por padrão. Para alterar:

```toml
# dashboard/.streamlit/config.toml
[theme]
primaryColor = "#00D4AA"  # Cor principal
backgroundColor = "#0E1117"  # Fundo principal
secondaryBackgroundColor = "#262730"  # Fundo sidebar
textColor = "#FAFAFA"  # Cor do texto
```

### Filtros e Configurações
No sidebar é possível configurar:

- **Período de análise**: 30/90/180 dias ou completo
- **Filtros de ativos**: Bitcoin only, Majors only
- **Alertas**: Max drawdown e Sharpe mínimo
- **Thresholds**: Configuração de limites

### Adicionando Novas Páginas
Para adicionar uma nova página:

1. Crie arquivo em `dashboard/pages/`
2. Use estrutura similar às páginas existentes
3. Configure `st.set_page_config()`
4. Implemente função `main()`

Exemplo:
```python
# dashboard/pages/New_Page.py
import streamlit as st

st.set_page_config(
    page_title="New Page - Crypto Momentum",
    page_icon="📈",
    layout="wide"
)

def main():
    st.title("📈 New Analysis Page")
    # Sua análise aqui

if __name__ == "__main__":
    main()
```

## 🔧 Troubleshooting

### Problema: "No module named 'streamlit'"
```bash
pip install streamlit plotly pandas numpy
```

### Problema: "Data files not found"
Execute primeiro a análise da estratégia:
```bash
python src/crypto_momentum_optimized.py
python src/advanced_metrics.py
python src/correlation_analysis.py
python src/multi_asset_portfolio.py
```

### Problema: "Port already in use"
```bash
# Use porta diferente
streamlit run dashboard/main_dashboard.py --server.port=8502
```

### Problema: Dashboard não abre no browser
```bash
# Acesse manualmente
http://localhost:8501
```

### Problema: Gráficos não aparecem
- Verifique se o Plotly está instalado
- Limpe cache do browser
- Recarregue a página (Ctrl+R)

## 📱 Acesso Mobile

O dashboard é responsivo e funciona em dispositivos móveis:

- **Tablet**: Experiência completa
- **Mobile**: Layout adaptado com scroll
- **Desktop**: Experiência otimizada

## 🔒 Segurança

### Uso Local
- Dashboard roda apenas localmente (localhost)
- Dados permanecem na máquina
- Sem conexões externas para dados

### Produção (se necessário)
```toml
# Para ambiente de produção
[server]
enableCORS = true
enableXsrfProtection = true
cookieSecret = "your-secure-secret-key"
```

## 📊 Performance

### Otimizações Implementadas
- **Caching**: `@st.cache_data` para carregamento
- **Chunking**: Dados grandes processados em blocos
- **Lazy loading**: Dados carregados sob demanda
- **Compressão**: Gráficos otimizados

### Monitoramento
- Use `streamlit run --profiler` para análise
- Monitore uso de memória com dados grandes
- Configure `maxUploadSize` se necessário

## 🆕 Próximas Funcionalidades

### Em Desenvolvimento
- [ ] Alerts automáticos por email/Slack
- [ ] Export para PDF dos relatórios
- [ ] Backtesting com parâmetros customizáveis
- [ ] Integration com APIs de exchanges
- [ ] Machine learning predictions

### Roadmap
- [ ] Multi-timeframe analysis
- [ ] Portfolio optimization
- [ ] Real-time data streaming
- [ ] A/B testing de estratégias
- [ ] Social trading integration

## 📞 Suporte

### Logs e Debug
```bash
# Ver logs detalhados
streamlit run dashboard/main_dashboard.py --logger.level=debug

# Limpar cache
streamlit cache clear
```

### Issues Conhecidos
- Primeira carga pode ser lenta (carregamento de dados)
- Gráficos complexos podem consumir memória
- Mobile tem limitações em gráficos 3D

## 🏆 Créditos

Dashboard desenvolvido para análise da estratégia **Crypto Momentum Strategy** com:

- **Frontend**: Streamlit 1.48.0
- **Visualizações**: Plotly 6.2.0  
- **Análise de Dados**: Pandas 2.3.1
- **Computação**: NumPy 2.3.2
- **Tema**: Dark mode customizado

---

**🎯 Happy Trading! 📈**
