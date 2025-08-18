# 🔐 CONFIGURAÇÃO DE EXEMPLO
# Copie este arquivo para config.py e preencha com suas chaves

# Binance API Keys
BINANCE_API_KEY = "sua_binance_api_key_aqui"
BINANCE_SECRET_KEY = "sua_binance_secret_key_aqui"

# Firebase Configuration
# O arquivo firebase-service-account.json deve estar na mesma pasta
# e será carregado automaticamente pelo firebase_config.py

# Configurações do Sistema
DEBUG = False
PORT = 5000
HOST = "0.0.0.0"

# Configurações de Trading
DEFAULT_SYMBOL = "BTC/USDT"
DEFAULT_TIMEFRAME = "1h"
MAX_TRADES_PER_DAY = 10

# Configurações de Segurança
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5000",
    "https://seu-dashboard.vercel.app"
]

# ⚠️ IMPORTANTE:
# 1. NUNCA commite suas chaves reais no GitHub
# 2. Use variáveis de ambiente em produção
# 3. Mantenha o firebase-service-account.json seguro
