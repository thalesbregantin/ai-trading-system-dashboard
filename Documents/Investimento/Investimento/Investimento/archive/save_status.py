import json
from datetime import datetime
from config import TradingConfig

# Status atual
status = {
    "timestamp": datetime.now().isoformat(),
    "testnet_mode": TradingConfig.TESTNET_MODE,
    "live_trading": TradingConfig.LIVE_TRADING,
    "binance_url": TradingConfig.get_binance_url(),
    "trading_pairs": TradingConfig.TRADING_PAIRS,
    "initial_capital": TradingConfig.INITIAL_CAPITAL,
    "max_position_size": TradingConfig.MAX_POSITION_SIZE,
    "mode": "LIVE" if not TradingConfig.TESTNET_MODE and TradingConfig.LIVE_TRADING else "TESTNET" if TradingConfig.TESTNET_MODE else "DISABLED"
}

# Salva status
with open('trading_status.json', 'w') as f:
    json.dump(status, f, indent=2)

print("✅ Status salvo em trading_status.json")
print(f"🚀 Modo atual: {status['mode']}")
if status['mode'] == 'LIVE':
    print("⚠️ SISTEMA EM MODO LIVE - DINHEIRO REAL!")
