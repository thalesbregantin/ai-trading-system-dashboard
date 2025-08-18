"""
Guia Rápido - Configuração Trading
"""

print("🔐 SUAS API KEYS JÁ ESTÃO CONFIGURADAS!")
print("=" * 50)

print("""
⚠️ PARA PODER COMPRAR/VENDER, VOCÊ PRECISA:

1️⃣ ATIVAR PERMISSÃO DE TRADING:
   🌐 Acesse: https://www.binance.com/en/my/settings/api-management
   ✏️ Clique em "Edit" na sua API Key
   ✅ Ative: "Enable Spot & Margin Trading"
   💾 Salve as alterações

2️⃣ CONFIGURAÇÕES RECOMENDADAS:
   ✅ Enable Reading
   ✅ Enable Spot & Margin Trading ← OBRIGATÓRIO
   ❌ Enable Futures (não necessário)
   ❌ Permit Universal Transfer (não necessário)
   🚫 Enable Withdrawals (NÃO ative para bots)

3️⃣ TESTE NO TESTNET PRIMEIRO:
   🧪 Acesse: https://testnet.binance.vision/
   🎁 Solicite dinheiro virtual no "Faucet"
   💰 Receba $1000+ para testes
   🔄 Use as mesmas API keys

4️⃣ EXECUTE O BOT:
   python main.py --mode live --env test
""")

print("\n💡 RESUMO:")
print("✅ API Keys: Configuradas")
print("⚠️ Trading Permission: PRECISA ATIVAR")
print("🧪 Testnet: Recomendado primeiro")
print("💰 Capital: $0 (testnet) ou $50+ (live)")

print("\n🚀 QUANDO ATIVAR A PERMISSÃO:")
print("Execute: python main.py --mode live --env test")
print("=" * 50)
