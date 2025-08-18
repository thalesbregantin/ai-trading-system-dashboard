# 🚀 Guia de Instalação e Execução

## 📁 **Configuração do Ambiente**

### 1. **Detectar Diretório Automaticamente:**
```bash
python setup_environment.py
```
Este script:
- ✅ Detecta automaticamente o diretório do projeto
- ✅ Verifica se todos os arquivos estão presentes  
- ✅ Testa dependências instaladas
- ✅ Configura o ambiente de trabalho

### 2. **Instalar Dependências:**
```bash
pip install -r requirements-crypto.txt
```

### 3. **Executar Análise Completa:**
```bash
python run_complete_analysis.py
```

---

## 🔧 **Resolução de Problemas**

### **Problema: "Diretório não encontrado"**
**Solução:**
```bash
# 1. Vá para o diretório correto
cd "C:\Users\motol\Downloads\Investimento\Investimento"

# 2. Ou execute o configurador
python setup_environment.py
```

### **Problema: "Módulo não encontrado"**
**Solução:**
```bash
# Instalar dependências
pip install pandas numpy requests tqdm scikit-learn matplotlib seaborn

# Ou usar o arquivo requirements
pip install -r requirements-crypto.txt
```

### **Problema: "Arquivo não encontrado"**
**Solução:**
```bash
# Verificar se está no diretório correto
python setup_environment.py

# Listar arquivos do diretório
dir  # Windows
ls   # Linux/Mac
```

---

## 📋 **Ordem de Execução Recomendada**

### **Opção 1 - Automática (Recomendada):**
```bash
# 1. Configurar ambiente
python setup_environment.py

# 2. Executar tudo
python run_complete_analysis.py
```

### **Opção 2 - Manual:**
```bash
# 1. Estratégia base
python crypto_momentum_optimized.py

# 2. Métricas avançadas  
python advanced_metrics.py

# 3. Análise de correlação
python correlation_analysis.py

# 4. Portfolio multi-asset
python multi_asset_portfolio.py

# 5. Walk-forward analysis
python walk_forward_analysis.py

# 6. Análise de regimes
python regime_analysis.py
```

---

## 📊 **Arquivos Esperados**

### **Arquivos de entrada (obrigatórios):**
- ✅ `crypto_momentum_optimized.py`
- ✅ `requirements-crypto.txt`

### **Arquivos de melhorias (criados):**
- ✅ `walk_forward_analysis.py`
- ✅ `correlation_analysis.py`  
- ✅ `advanced_metrics.py`
- ✅ `multi_asset_portfolio.py`
- ✅ `regime_analysis.py`
- ✅ `run_complete_analysis.py`
- ✅ `setup_environment.py`

### **Arquivos de saída (gerados):**
- 📊 `equity_momentum_optimized.csv`
- 📊 `trades_momentum_optimized.csv`
- 📊 `advanced_metrics_report.csv`
- 📊 `correlation_analysis.csv`
- 📊 `walk_forward_results.csv`
- 📊 `regime_analysis.csv`
- 🖼️ `correlation_heatmap.png`

---

## 🌐 **Dependências de Internet**

⚠️ **Atenção:** Os scripts precisam de conexão com internet para:
- 📡 **CoinGecko API** - Dados de preços e volume
- 🔄 **Rate limiting** - Scripts têm delays para respeitar limites

**Se houver problemas de conexão:**
- Verifique firewall/proxy
- Aguarde alguns minutos (rate limit)
- Execute scripts individuais

---

## 💡 **Dicas Importantes**

### **Performance:**
- ⏱️ Análise completa: ~10-20 minutos
- 💾 Espaço necessário: ~50MB para dados
- 🌐 Conexão estável recomendada

### **Primeira execução:**
```bash
# 1. Configure uma vez
python setup_environment.py

# 2. Execute quando quiser
python run_complete_analysis.py
```

### **Execuções subsequentes:**
```bash
# Apenas execute
python run_complete_analysis.py
```

---

## 📞 **Suporte**

Se ainda tiver problemas:

1. **Execute o diagnóstico:**
   ```bash
   python setup_environment.py
   ```

2. **Verifique o diretório:**
   ```bash
   pwd  # Linux/Mac
   cd   # Windows
   ```

3. **Liste arquivos:**
   ```bash
   ls -la  # Linux/Mac  
   dir     # Windows
   ```

4. **Teste dependências:**
   ```bash
   python -c "import pandas, numpy, requests, sklearn; print('OK')"
   ```

---

**🎯 Agora o projeto funciona em qualquer diretório!** 🚀
