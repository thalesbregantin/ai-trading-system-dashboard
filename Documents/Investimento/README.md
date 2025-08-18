# 🤖 AI Trading System Dashboard

Sistema completo de trading com IA, incluindo backend, frontend e sistema de IA.

## 📁 Estrutura do Projeto

```
ai-trading-system-dashboard/
├── backend/              # API Flask (Deploy no Railway)
│   ├── app.py           # Servidor Flask
│   ├── requirements.txt # Dependências Python
│   └── Procfile        # Configuração Railway
├── frontend/            # Dashboard HTML/CSS/JS (Deploy no Vercel)
│   ├── index.html      # Dashboard principal
│   ├── trades.html     # Página de trades
│   ├── settings.html   # Configurações
│   ├── ai-models.html  # Modelos de IA
│   └── docs.html       # Documentação
├── ai_trading_system/   # Sistema de IA
└── README.md
```

## 🚀 Deploy

### Backend (Railway)
- **Pasta:** `backend/`
- **URL:** `https://ai-trading-system-dashboard-production.up.railway.app`
- **Comando:** `gunicorn app:app`

### Frontend (Vercel)
- **Pasta:** `frontend/`
- **URL:** Dashboard público
- **Arquivos:** HTML/CSS/JS estáticos

## 🔗 Comunicação

- **Frontend** → **Backend** via API REST
- **Backend** retorna dados reais da Binance
- **Fallback** para dados locais se API não estiver disponível

## 💰 Dados Reais

- **Portfolio Value:** $98.60 (seu saldo real)
- **Today's Profit:** $0.00 (sem trades hoje)
- **Win Rate:** 0.0% (sem trades ainda)
- **Sharpe Ratio:** 0.00 (sem trades ainda)

## 🎯 Próximos Passos

1. ✅ Backend funcionando
2. ✅ Frontend funcionando
3. 🔄 Integrar sistema de IA
4. 🔄 Conectar com Binance real
5. 🔄 Implementar trades automáticos
