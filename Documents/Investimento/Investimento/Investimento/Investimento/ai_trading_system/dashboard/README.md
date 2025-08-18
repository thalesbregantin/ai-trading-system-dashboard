# 🚀 AI Trading System - Dashboard

## 📋 **Descrição**

Sistema de trading automatizado com dashboard web, integração Binance e Firebase para armazenamento de dados.

## 🔐 **Configuração Segura**

### **1. Configurar Chaves (OBRIGATÓRIO)**

**⚠️ IMPORTANTE: NUNCA commite suas chaves no GitHub!**

1. **Binance API:**
   - Acesse: https://www.binance.com/en/my/settings/api-management
   - Crie uma nova API Key
   - Configure as permissões necessárias

2. **Firebase:**
   - Baixe o arquivo `firebase-service-account.json`
   - Coloque na pasta `dashboard/`
   - Este arquivo está no `.gitignore` (não será enviado ao GitHub)

3. **Configurar Variáveis de Ambiente:**
   ```bash
   # Local (arquivo .env)
   BINANCE_API_KEY=sua_chave_aqui
   BINANCE_SECRET_KEY=sua_chave_secreta_aqui
   
   # Cloud (Railway/Render)
   # Configure nas variáveis de ambiente da plataforma
   ```

### **2. Instalar Dependências**

```bash
pip install -r requirements-cloud.txt
```

### **3. Testar Configuração**

```bash
# Testar Firebase
python -c "from firebase_config import test_firebase; test_firebase()"

# Testar servidor local
python cloud_api_server.py
```

## 🚀 **Deploy**

### **Backend (Railway)**
1. Acesse: https://railway.app/
2. Conecte seu repositório GitHub
3. Configure variáveis de ambiente
4. Deploy automático

### **Frontend (Vercel)**
1. Acesse: https://vercel.com/
2. Importe repositório
3. Configure pasta `frontend`
4. Deploy instantâneo

## 📁 **Estrutura do Projeto**

```
dashboard/
├── 🔐 firebase-service-account.json  # (NÃO COMMITAR)
├── 🚀 cloud_api_server.py           # Servidor API
├── 🔥 firebase_config.py            # Configuração Firebase
├── 📊 index.html                    # Dashboard principal
├── 📈 trades.html                   # Página de trades
├── ⚙️ settings.html                 # Configurações
├── 🤖 ai-models.html                # Modelos AI
├── 📖 docs.html                     # Documentação
├── 📋 requirements-cloud.txt        # Dependências
├── 🔒 .gitignore                    # Proteção de chaves
├── 📝 README.md                     # Este arquivo
└── 🎯 DEPLOY_GUIDE.md              # Guia de deploy
```

## 🔒 **Segurança**

✅ **Arquivos Protegidos:**
- `firebase-service-account.json` - Credenciais Firebase
- `.env` - Variáveis de ambiente
- `*.key`, `*.pem` - Chaves privadas
- `__pycache__/` - Cache Python
- `.venv/` - Ambiente virtual

✅ **Boas Práticas:**
- Use variáveis de ambiente em produção
- Nunca commite chaves no GitHub
- Mantenha o `.gitignore` atualizado
- Use HTTPS em produção

## 🎯 **Funcionalidades**

- 📊 Dashboard em tempo real
- 🔥 Integração Firebase
- 💰 Dados reais da Binance
- 📈 Gráficos interativos
- 🤖 Modelos de IA
- 📝 Logs de treinamento
- ⚙️ Configurações salvas

## 🆘 **Suporte**

Se encontrar problemas:

1. Verifique se as chaves estão configuradas
2. Teste a conexão com Firebase
3. Verifique as variáveis de ambiente
4. Consulte o `DEPLOY_GUIDE.md`

---

**🎉 Sistema pronto para deploy!**
