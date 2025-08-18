from config import TradingConfig

print("🚀 CONFIGURAÇÃO MODO LIVE")
print("=" * 40)
print(f"TESTNET_MODE: {TradingConfig.TESTNET_MODE}")
print(f"LIVE_TRADING: {TradingConfig.LIVE_TRADING}")
print(f"URL Binance: {TradingConfig.get_binance_url()}")

if not TradingConfig.TESTNET_MODE and TradingConfig.LIVE_TRADING:
    print("🔥 SISTEMA EM MODO LIVE!")
    print("⚠️ TRADING COM DINHEIRO REAL!")
else:
    print("🧪 Sistema ainda em teste")

print(f"Pares: {', '.join(TradingConfig.TRADING_PAIRS)}")
print(f"Capital: ${TradingConfig.INITIAL_CAPITAL}")
print(f"Max Position: {TradingConfig.MAX_POSITION_SIZE:.1%}")
