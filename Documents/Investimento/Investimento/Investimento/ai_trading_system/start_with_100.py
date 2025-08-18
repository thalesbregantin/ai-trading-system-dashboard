#!/usr/bin/env python3
"""
Guia passo a passo para começar com $100
"""

print("💰 VOCÊ TEM $100 NA BINANCE - VAMOS COMEÇAR!")
print("=" * 60)

print("🎯 PLANO RECOMENDADO:")
print()
print("PASSO 1: 🎓 Treinar AI (10 min)")
print("  python main.py --mode train --episodes 15")
print("  → AI aprende padrões do mercado")
print()
print("PASSO 2: 📊 Abrir Dashboard")  
print("  python main.py --mode dashboard")
print("  → Ver como sistema funciona")
print()
print("PASSO 3: 🚀 Iniciar Trading")
print("  python main.py --mode live --env prod")
print("  → Trading com dinheiro real!")
print()
print("⚙️ CONFIGURAÇÃO ATUAL:")
print("  • Capital: $100")
print("  • Max por trade: $2 (2%)")
print("  • Stop-loss: 5%")
print("  • Pares: BTC/USDT, ETH/USDT")
print()
print("🛡️ PROTEÇÕES ATIVAS:")
print("  • Máximo 10 trades/dia")
print("  • Stop-loss automático")
print("  • Logs detalhados")
print()
print("📊 MONITORAMENTO:")
print("  • Dashboard: http://localhost:8501")
print("  • Logs: logs/trading_log_*.log")
print()
print("🚀 PRONTO PARA COMEÇAR!")

choice = input("\nQue passo quer executar? (1/2/3): ").strip()

if choice == "1":
    print("🎓 Iniciando treinamento da AI...")
    import subprocess
    subprocess.run(["python", "main.py", "--mode", "train", "--episodes", "15"])
elif choice == "2":
    print("📊 Abrindo dashboard...")
    import subprocess
    subprocess.run(["python", "main.py", "--mode", "dashboard"])
elif choice == "3":
    print("⚠️ ATENÇÃO: Trading com seus $100 reais!")
    confirm = input("Digite 'CONFIRMO' para prosseguir: ")
    if confirm == "CONFIRMO":
        print("🚀 Iniciando trading ao vivo...")
        import subprocess
        subprocess.run(["python", "main.py", "--mode", "live", "--env", "prod"])
    else:
        print("❌ Trading cancelado")
else:
    print("❌ Opção inválida!")
