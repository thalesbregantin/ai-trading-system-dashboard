# 🐳 AI Trading System - Workers de Treinamento

## 📋 **Resumo**
Sistema de treinamento paralelo usando Docker workers para acelerar o treinamento do AI Trading System.

## 🚀 **Início Rápido**

### **1. Iniciar Treinamento:**
```bash
start_training.bat
```

### **2. Monitorar Progresso:**
- Dashboard: http://localhost:8502
- Logs: `docker-compose -f docker-compose-workers.yml logs -f`

### **3. Parar Workers:**
```bash
docker-compose -f docker-compose-workers.yml down
```

## 🏗️ **Arquitetura**

### **Componentes:**
- **Worker Manager**: Coordena e monitora workers
- **Workers (4x)**: Executam treinamento em paralelo
- **Training Dashboard**: Monitora progresso em tempo real

### **Fluxo de Trabalho:**
1. **Worker Manager** divide pares entre workers
2. **Workers** treinam modelos em paralelo
3. **Resultados** são agregados automaticamente
4. **Melhores modelos** são salvos

## 📊 **Distribuição de Trabalho**

### **15 Pares de Trading:**
- **Worker 1**: BTC-USD, ETH-USD, BNB-USD, SOL-USD
- **Worker 2**: XRP-USD, ADA-USD, DOGE-USD, TRX-USD
- **Worker 3**: LINK-USD, AVAX-USD, MATIC-USD, DOT-USD
- **Worker 4**: LTC-USD, ATOM-USD, UNI-USD

### **Configuração por Worker:**
- **Episódios por par**: 10
- **Dados históricos**: 1 ano (1h interval)
- **Parâmetros**: Learning rate, gamma, epsilon, etc.

## 🎯 **Vantagens dos Workers**

✅ **Treinamento 4x mais rápido** (paralelo)  
✅ **Melhor utilização de recursos** (CPU/GPU)  
✅ **Falha isolada** (um worker falha, outros continuam)  
✅ **Monitoramento em tempo real**  
✅ **Resultados agregados automaticamente**  

## 📁 **Estrutura de Arquivos**

```
results/
├── worker_1_config.json      # Configuração Worker 1
├── worker_2_config.json      # Configuração Worker 2
├── worker_3_config.json      # Configuração Worker 3
├── worker_4_config.json      # Configuração Worker 4
├── worker_1_status.json      # Status Worker 1
├── worker_2_status.json      # Status Worker 2
├── worker_3_status.json      # Status Worker 3
├── worker_4_status.json      # Status Worker 4
├── worker_1_results.json     # Resultados Worker 1
├── worker_2_results.json     # Resultados Worker 2
├── worker_3_results.json     # Resultados Worker 3
├── worker_4_results.json     # Resultados Worker 4
├── aggregated_results.json   # Resultados agregados
└── training_report.json      # Relatório final

models/
├── worker_1_BTC_USD_model.h5
├── worker_1_ETH_USD_model.h5
├── worker_2_XRP_USD_model.h5
└── ... (melhores modelos de cada worker)

data/
├── BTC_USD_data.csv
├── ETH_USD_data.csv
└── ... (dados históricos)
```

## 🔧 **Comandos Úteis**

### **Ver logs de um worker específico:**
```bash
docker-compose -f docker-compose-workers.yml logs worker-1
```

### **Ver status de todos os workers:**
```bash
docker-compose -f docker-compose-workers.yml ps
```

### **Reiniciar um worker:**
```bash
docker-compose -f docker-compose-workers.yml restart worker-1
```

### **Ver uso de recursos:**
```bash
docker stats
```

## 📈 **Monitoramento**

### **Dashboard de Treinamento:**
- Progresso em tempo real
- Status de cada worker
- Resultados parciais
- Gráficos de performance

### **Logs Detalhados:**
- Progresso por episódio
- Erros e warnings
- Métricas de treinamento
- Tempo de execução

## 🎉 **Resultados Esperados**

### **Após Treinamento:**
- **60 modelos treinados** (15 pares × 4 workers)
- **Relatório agregado** com métricas
- **Melhores modelos** salvos
- **Dados históricos** organizados

### **Métricas de Performance:**
- Profit/Loss por par
- Win rate por modelo
- Sharpe ratio
- Drawdown máximo

## 🚨 **Troubleshooting**

### **Worker não inicia:**
- Verificar logs: `docker-compose -f docker-compose-workers.yml logs worker-1`
- Verificar configuração: `results/worker_1_config.json`

### **Erro de dados:**
- Verificar conexão com Yahoo Finance
- Verificar símbolos válidos

### **Erro de memória:**
- Reduzir batch_size nos parâmetros
- Reduzir número de workers

## 🎯 **Próximos Passos**

1. **Treinar modelos** com workers
2. **Validar resultados** em dados out-of-sample
3. **Selecionar melhores modelos** para live trading
4. **Implementar ensemble** dos melhores modelos
5. **Testar em paper trading** antes do live

---

**🎉 Sistema pronto para treinamento em larga escala!**
