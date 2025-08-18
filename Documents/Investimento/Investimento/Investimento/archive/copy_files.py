import shutil
import os
from pathlib import Path

# Arquivos para copiar
files_to_copy = [
    ("ai_trader_dqn.py", "ai_trading_system/core/"),
    ("hybrid_trading_system.py", "ai_trading_system/core/"),
    ("binance_ai_bot.py", "ai_trading_system/core/"),
    (".env", "ai_trading_system/"),
]

print("📋 Copiando arquivos essenciais...")

for source, dest_dir in files_to_copy:
    try:
        if os.path.exists(source):
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, os.path.basename(source))
            shutil.copy2(source, dest_path)
            print(f"✅ {source} -> {dest_path}")
        else:
            print(f"⚠️ Arquivo não encontrado: {source}")
    except Exception as e:
        print(f"❌ Erro copiando {source}: {e}")

# Copiar dashboard
if os.path.exists("dashboard"):
    try:
        if os.path.exists("ai_trading_system/dashboard"):
            shutil.rmtree("ai_trading_system/dashboard")
        shutil.copytree("dashboard", "ai_trading_system/dashboard")
        print("✅ dashboard/ -> ai_trading_system/dashboard/")
    except Exception as e:
        print(f"❌ Erro copiando dashboard: {e}")

print("\n✅ Cópia concluída!")
