from config import TradingConfig

print("🔥 CONFIGURAÇÃO ATUAL:")
print(f"LIVE_TRADING: {TradingConfig.LIVE_TRADING}")
print(f"TESTNET_MODE: {TradingConfig.TESTNET_MODE}")
print(f"API Key configurada: {len(TradingConfig.BINANCE_API_KEY) > 10}")

if TradingConfig.LIVE_TRADING:
    print("✅ Trading ao vivo HABILITADO!")
    print("Próximo passo: python main.py --mode live --env test")
else:
    print("❌ Trading ao vivo DESABILITADO")
