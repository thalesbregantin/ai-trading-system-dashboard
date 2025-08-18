# 🤖 AI Trading Dashboard

Dashboard moderno para monitorar seu sistema de trading AI com dados reais da Binance.

## 🚀 **ETAPA 1: CONEXÃO COM BINANCE**

### **1. Configurar Chaves da Binance**

1. **Crie uma conta na Binance** (se ainda não tiver)
2. **Gere suas chaves API:**
   - Acesse: https://www.binance.com/pt-BR/my/settings/api-management
   - Clique em "Criar API"
   - **IMPORTANTE:** Marque apenas "Leitura" (não precisa de permissão de trading)
   - Copie a **API Key** e **Secret Key**

### **2. Configurar Arquivo .env**

Edite o arquivo `.env` na raiz do projeto:

```env
# Binance API Configuration
BINANCE_API_KEY=sua_api_key_aqui
BINANCE_SECRET_KEY=sua_secret_key_aqui

# Trading Configuration
INITIAL_CAPITAL=10000
RISK_PERCENTAGE=2
MAX_POSITION_SIZE=10

# AI Model Configuration
MODEL_PATH=models/
LOG_PATH=logs/
```

## 🛠️ **ETAPA 2: INSTALAÇÃO E EXECUÇÃO**

### **Opção 1: Setup Automático (Recomendado)**

```bash
# Navegue até a pasta do dashboard
cd dashboard

# Execute o script de setup
python start_dashboard.py
```

### **Opção 2: Setup Manual**

```bash
# 1. Instalar dependências
pip install -r requirements-api.txt

# 2. Iniciar servidor API
python api_server.py

# 3. Em outro terminal, abrir o dashboard
# Use VS Code + Live Server no arquivo index.html
```

## 🌐 **ETAPA 3: ACESSAR O DASHBOARD**

### **1. Abrir o Dashboard**

1. **Abra o VS Code** na pasta do projeto
2. **Navegue até:** `dashboard/index.html`
3. **Clique com botão direito** → "Open with Live Server"
4. **O dashboard abrirá em:** `http://localhost:5500/dashboard/index.html`

### **2. Verificar Conexão**

- ✅ **Status Verde:** Conectado com Binance
- ❌ **Status Vermelho:** Erro na conexão (verifique as chaves API)

## 📊 **FUNCIONALIDADES IMPLEMENTADAS**

### **✅ ETAPA 1 - DADOS REAIS:**
- **Portfolio Real:** Saldo atual da sua conta Binance
- **Trades Reais:** Histórico de suas operações
- **Preços em Tempo Real:** Dados atuais do mercado
- **Gráficos Interativos:** Preços com indicadores técnicos
- **Métricas Calculadas:** Win rate, Sharpe ratio, etc.

### **🔄 ETAPA 2 - FUNCIONALIDADES BÁSICAS:**
- **Live Mode:** Atualizações automáticas a cada 5 segundos
- **Timeframes:** 1H, 4H, 1D, 1W
- **Responsivo:** Funciona em desktop e mobile
- **Status do Sistema:** Monitoramento de conexões

### **🧠 ETAPA 3 - FUNCIONALIDADES AVANÇADAS:**
- **Integração com AI:** Sinais de trading em tempo real
- **Configurações:** Personalização de parâmetros
- **Alertas:** Notificações de oportunidades
- **Backtesting:** Teste de estratégias

## 🔧 **ESTRUTURA DO PROJETO**

```
dashboard/
├── index.html              # Dashboard principal
├── api_server.py           # Servidor API Flask
├── requirements-api.txt    # Dependências Python
├── start_dashboard.py      # Script de setup
└── README.md              # Este arquivo
```

## 📡 **ENDPOINTS DA API**

- `GET /api/portfolio` - Dados do portfolio
- `GET /api/trades` - Trades recentes
- `GET /api/chart-data` - Dados para gráficos
- `GET /api/metrics` - Métricas de performance
- `GET /api/current-price` - Preço atual
- `GET /api/status` - Status da conexão

## ⚠️ **IMPORTANTE**

### **🔒 Segurança:**
- **NUNCA** compartilhe suas chaves API
- Use apenas permissão de **leitura** na Binance
- Mantenha o arquivo `.env` seguro

### **🚨 Limitações:**
- API da Binance tem limite de requisições
- Dados históricos limitados
- Algumas funcionalidades precisam de permissões especiais

### **🛠️ Troubleshooting:**

**Erro de Conexão:**
```bash
# Verificar se o servidor está rodando
curl http://localhost:5000/api/status
```

**Erro de Chaves API:**
```bash
# Verificar arquivo .env
cat .env
```

**Erro de Dependências:**
```bash
# Reinstalar dependências
pip install -r requirements-api.txt --force-reinstall
```

## 🎯 **PRÓXIMOS PASSOS**

1. **Configure suas chaves da Binance**
2. **Execute o setup automático**
3. **Abra o dashboard com Live Server**
4. **Verifique a conexão com Binance**
5. **Explore as funcionalidades**

## 📞 **SUPORTE**

Se encontrar problemas:

1. **Verifique o console do navegador** (F12)
2. **Verifique os logs do servidor API**
3. **Confirme se as chaves API estão corretas**
4. **Teste a conexão com a Binance**

---

**🎉 Agora você tem um dashboard profissional com dados reais da sua conta Binance!**
