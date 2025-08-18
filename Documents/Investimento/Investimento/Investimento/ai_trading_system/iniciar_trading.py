#!/usr/bin/env python3
"""
🤖 INICIAR TRADING REAL - SUA IA OPERANDO!
Script para começar as operações reais na Binance
"""

import os
import sys
import time
from datetime import datetime

# Adicionar paths
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, 'core'))

def print_banner():
    """Banner de início"""
    print("=" * 60)
    print("🤖 INICIANDO TRADING REAL COM IA")
    print("💰 Seus $100 serão operados automaticamente")
    print("🚀 Sistema híbrido: IA + Momentum")
    print("📅", datetime.now().strftime("%d/%m/%Y às %H:%M:%S"))
    print("=" * 60)

def verificar_configuracao():
    """Verifica se está tudo pronto"""
    print("\n🔍 VERIFICANDO CONFIGURAÇÃO...")
    print("-" * 40)
    
    try:
        from config import TradingConfig
        
        # Verifica modo live
        if TradingConfig.TESTNET_MODE:
            print("⚠️ ATENÇÃO: Modo TESTNET ativo")
            print("💡 Para trading real, configure TESTNET_MODE = False")
            return False
        else:
            print("✅ Modo LIVE ativo - Trading real!")
        
        # Verifica API keys
        if TradingConfig.BINANCE_API_KEY and TradingConfig.BINANCE_API_SECRET:
            print("✅ API Keys configuradas")
        else:
            print("❌ API Keys não configuradas")
            return False
        
        # Verifica live trading
        if TradingConfig.LIVE_TRADING:
            print("✅ Live Trading habilitado")
        else:
            print("❌ Live Trading desabilitado")
            return False
        
        print("✅ Configuração válida para trading real!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return False

def verificar_conta():
    """Verifica conta na Binance"""
    print("\n💰 VERIFICANDO SUA CONTA BINANCE...")
    print("-" * 40)
    
    try:
        from binance_real_data import binance_data
        
        # Pega saldo atual
        balance = binance_data.get_account_balance()
        
        print(f"💵 Saldo Total: ${balance['total_usdt']:.2f}")
        print(f"💸 Disponível: ${balance['free_usdt']:.2f}")
        
        if balance['total_usdt'] < 10:
            print("⚠️ Saldo muito baixo para trading")
            print("💡 Recomendado: pelo menos $10 USDT")
            return False
        
        print("✅ Saldo suficiente para começar!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar conta: {e}")
        return False

def mostrar_estrategia():
    """Mostra a estratégia que será usada"""
    print("\n🧠 ESTRATÉGIA DA IA:")
    print("-" * 40)
    print("🤖 60% - Sinais da Inteligência Artificial")
    print("📈 40% - Análise de Momentum (SMA, RSI)")
    print("🎯 Pares: BTC/USDT, ETH/USDT")
    print("🛡️ Stop-loss: 5% automático")
    print("💰 Máximo por trade: 2% do saldo")
    print("⏰ Análise a cada 5 minutos")

def confirmar_inicio():
    """Confirma se quer começar"""
    print("\n⚠️ CONFIRMAÇÃO FINAL:")
    print("-" * 40)
    print("🔴 VOCÊ ESTÁ PRESTES A INICIAR TRADING REAL")
    print("💰 A IA vai operar com SEU DINHEIRO REAL")
    print("📊 Operações serão executadas automaticamente")
    print("🛑 Você pode parar a qualquer momento (Ctrl+C)")
    
    while True:
        resposta = input("\n🤔 Tem certeza que quer começar? (SIM/não): ").strip().upper()
        
        if resposta in ['SIM', 'S', 'YES', 'Y']:
            return True
        elif resposta in ['NÃO', 'NAO', 'N', 'NO']:
            return False
        else:
            print("❓ Por favor, digite SIM ou NÃO")

def iniciar_bot():
    """Inicia o bot de trading"""
    print("\n🚀 INICIANDO BOT DE TRADING...")
    print("-" * 40)
    
    try:
        from config import TradingConfig
        from binance_ai_bot import BinanceAIBot
        
        # Cria o bot
        bot = BinanceAIBot(
            api_key=TradingConfig.BINANCE_API_KEY,
            api_secret=TradingConfig.BINANCE_API_SECRET,
            testnet=TradingConfig.TESTNET_MODE
        )
        
        print("✅ Bot criado com sucesso!")
        print("🔄 Iniciando loop de trading...")
        print("💡 Pressione Ctrl+C para parar")
        
        # Loop principal de trading
        while True:
            try:
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Analisando mercado...")
                
                # Executa ciclo de trading
                bot.run_trading_cycle()
                
                # Aguarda próximo ciclo (5 minutos)
                print("⏳ Aguardando próximo ciclo (5 min)...")
                time.sleep(300)  # 5 minutos
                
            except KeyboardInterrupt:
                print("\n\n🛑 TRADING INTERROMPIDO PELO USUÁRIO")
                print("✅ Bot parado com segurança")
                break
            except Exception as e:
                print(f"❌ Erro no ciclo de trading: {e}")
                print("🔄 Continuando em 1 minuto...")
                time.sleep(60)
        
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")
        print("💡 Verifique suas configurações")

def main():
    """Função principal"""
    print_banner()
    
    # Verificações de segurança
    if not verificar_configuracao():
        print("\n❌ Configuração inválida. Corrija antes de continuar.")
        input("⏸️ Pressione Enter para sair...")
        return
    
    if not verificar_conta():
        print("\n❌ Problema com conta Binance. Verifique antes de continuar.")
        input("⏸️ Pressione Enter para sair...")
        return
    
    # Mostra estratégia
    mostrar_estrategia()
    
    # Confirmação final
    if not confirmar_inicio():
        print("\n👋 Trading cancelado pelo usuário")
        input("⏸️ Pressione Enter para sair...")
        return
    
    # Inicia bot
    iniciar_bot()
    
    print("\n" + "=" * 60)
    print("👋 Obrigado por usar o AI Trading System!")
    print("💰 Seus investimentos continuam seguros")
    print("=" * 60)

if __name__ == "__main__":
    main()
