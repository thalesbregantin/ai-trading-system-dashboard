# 🚀 Guia de Deploy Cloud - AI Trading System

## 📋 Visão Geral

Este guia vai te ajudar a migrar o sistema de trading local para uma solução completa em cloud com:

- **Backend**: Railway/Render (API Flask)
- **Banco de Dados**: Firebase Firestore
- **Frontend**: Vercel/Netlify (Dashboard HTML)

## 🔥 Passo 1: Configurar Firebase

### 1.1 Criar Projeto Firebase

1. Acesse [Firebase Console](https://console.firebase.google.com/)
2. Clique em "Criar Projeto"
3. Nome: `ai-trading-system`
4. Ative o Google Analytics (opcional)
5. Clique em "Criar Projeto"

### 1.2 Configurar Firestore Database

1. No menu lateral, clique em "Firestore Database"
2. Clique em "Criar banco de dados"
3. Escolha "Iniciar no modo de teste" (para desenvolvimento)
4. Escolha a localização mais próxima (ex: `us-central1`)
5. Clique em "Próximo"

### 1.3 Configurar Service Account

1. No menu lateral, clique em "Configurações do projeto" (ícone de engrenagem)
2. Vá para a aba "Contas de serviço"
3. Clique em "Gerar nova chave privada"
4. Baixe o arquivo JSON
5. Renomeie para `firebase-service-account.json`

### 1.4 Atualizar Configuração

1. Abra o arquivo `firebase_config.py`
2. Substitua o `FIREBASE_CONFIG` com os dados do seu arquivo JSON:

```python
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": "seu-projeto-id",
    "private_key_id": "sua-private-key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-xxxxx@seu-projeto.iam.gserviceaccount.com",
    "client_id": "seu-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

## 🚂 Passo 2: Deploy no Railway

### 2.1 Criar Conta Railway

1. Acesse [Railway](https://railway.app/)
2. Faça login com GitHub
3. Clique em "New Project"

### 2.2 Conectar Repositório

1. Escolha "Deploy from GitHub repo"
2. Selecione seu repositório
3. Escolha a pasta `dashboard`

### 2.3 Configurar Variáveis de Ambiente

No Railway, vá em "Variables" e adicione:

```
BINANCE_API_KEY=sua_binance_api_key
BINANCE_SECRET_KEY=sua_binance_secret_key
FLASK_ENV=production
```

### 2.4 Configurar Deploy

Railway detectará automaticamente que é um projeto Python. Certifique-se de que:

1. **Build Command**: `pip install -r requirements-cloud.txt`
2. **Start Command**: `gunicorn cloud_api_server:app`

### 2.5 Deploy

1. Clique em "Deploy"
2. Aguarde o build completar
3. Anote a URL gerada (ex: `https://ai-trading-api.railway.app`)

## 🌐 Passo 3: Deploy Frontend no Vercel

### 3.1 Preparar Frontend

1. Crie uma pasta `frontend` no seu projeto
2. Copie todos os arquivos HTML para lá
3. Atualize a URL da API nos arquivos HTML:

```javascript
// Substitua em todos os arquivos HTML
const apiBaseUrl = 'https://sua-api-railway.railway.app/api';
```

### 3.2 Deploy no Vercel

1. Acesse [Vercel](https://vercel.com/)
2. Faça login com GitHub
3. Clique em "New Project"
4. Importe seu repositório
5. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: (deixe vazio)
   - **Output Directory**: (deixe vazio)

### 3.3 Deploy

1. Clique em "Deploy"
2. Aguarde o deploy completar
3. Anote a URL gerada (ex: `https://ai-trading-dashboard.vercel.app`)

## 🔧 Passo 4: Configurar CORS

### 4.1 Atualizar CORS no Backend

No arquivo `cloud_api_server.py`, atualize o CORS:

```python
CORS(app, origins=[
    "https://sua-dashboard-vercel.vercel.app",
    "http://localhost:3000",  # Para desenvolvimento local
    "http://localhost:5000"
])
```

### 4.2 Redeploy

1. Faça commit das mudanças
2. Railway fará deploy automático

## 📊 Passo 5: Testar Sistema

### 5.1 Testar API

```bash
curl https://sua-api-railway.railway.app/api/status
```

### 5.2 Testar Dashboard

1. Acesse sua URL do Vercel
2. Verifique se os dados aparecem
3. Teste todas as funcionalidades

## 🔐 Passo 6: Segurança

### 6.1 Configurar Regras do Firestore

No Firebase Console, vá em "Firestore Database" > "Regras":

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Permitir leitura/escrita apenas para usuários autenticados
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### 6.2 Configurar Domínios Permitidos

No Firebase Console, vá em "Authentication" > "Settings" > "Authorized domains" e adicione:
- `sua-dashboard-vercel.vercel.app`

## 📈 Passo 7: Monitoramento

### 7.1 Logs do Railway

1. No Railway, vá em "Deployments"
2. Clique em um deployment
3. Veja os logs em tempo real

### 7.2 Analytics do Firebase

1. No Firebase Console, vá em "Analytics"
2. Veja métricas de uso do dashboard

## 🚀 Benefícios da Migração

### ✅ **Vantagens:**

1. **Sempre Online**: Sem problemas de servidor local
2. **Escalável**: Suporta múltiplos usuários
3. **Seguro**: Dados protegidos em cloud
4. **Acessível**: Dashboard disponível de qualquer lugar
5. **Backup Automático**: Firebase faz backup automático
6. **Logs Persistente**: Histórico completo de trades e treinamentos

### 📊 **Funcionalidades Cloud:**

- **Logs de Treinamento**: Salva todos os treinamentos no Firebase
- **Histórico de Trades**: Trades reais salvos no banco
- **Configurações**: Preferências salvas por usuário
- **Métricas Reais**: Baseadas em dados reais do banco
- **Sincronização**: Dados sincronizados entre dispositivos

## 🔧 Troubleshooting

### Problema: API não responde
**Solução**: Verificar logs do Railway e variáveis de ambiente

### Problema: Firebase não conecta
**Solução**: Verificar configuração do service account

### Problema: CORS error
**Solução**: Atualizar origins no CORS do backend

### Problema: Dashboard não carrega dados
**Solução**: Verificar URL da API no frontend

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs do Railway
2. Teste a API diretamente com curl
3. Verifique as regras do Firestore
4. Confirme as variáveis de ambiente

---

**🎉 Parabéns! Seu sistema de trading agora está 100% em cloud!**
