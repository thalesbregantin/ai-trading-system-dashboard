#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import schedule
from live_ai_trading import LiveAITradingSystem

def run_automated_trading():
    """Executar trading automático"""
    print("🤖 INICIANDO TRADING AUTOMÁTICO")
    print("=" * 50)
    
    # Criar sistema
    trading_system = LiveAITradingSystem()
    
    # Configurar Binance
    if not trading_system.setup_binance():
        print("❌ Falha ao configurar Binance")
        return
    
    # Mostrar resumo inicial
    summary = trading_system.get_account_summary()
    if summary:
        print(f"💰 Saldo inicial: USDT ${summary['usdt_balance']:.2f}, BTC {summary['btc_balance']:.6f}")
    
    print("🔄 Sistema rodando automaticamente...")
    print("⏰ Executando análise a cada 5 minutos")
    print("🛑 Pressione Ctrl+C para parar")
    print("=" * 50)
    
    try:
        while True:
            # Executar ciclo de trading
            success = trading_system.run_trading_cycle()
            
            if success:
                # Mostrar resumo atualizado
                summary = trading_system.get_account_summary()
                if summary:
                    print(f"📊 Status: USDT ${summary['usdt_balance']:.2f}, BTC {summary['btc_balance']:.6f}, Trades: {summary['total_trades']}")
            
            # Aguardar 5 minutos
            print("⏳ Aguardando próxima análise...")
            time.sleep(300)  # 5 minutos
            
    except KeyboardInterrupt:
        print("\n🛑 Trading automático interrompido pelo usuário")
        print("📊 Resumo final:")
        summary = trading_system.get_account_summary()
        if summary:
            print(f"💰 Saldo final: USDT ${summary['usdt_balance']:.2f}, BTC {summary['btc_balance']:.6f}")
            print(f"📈 Total de trades: {summary['total_trades']}")

def main():
    """Função principal"""
    print("🚀 AI TRADING SYSTEM - MODO AUTOMÁTICO")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Este sistema fará trades reais!")
    print("💰 Use apenas com dinheiro que pode perder!")
    print("=" * 60)
    
    response = input("🤔 Quer iniciar o trading automático? (s/n): ")
    
    if response.lower() == 's':
        run_automated_trading()
    else:
        print("👌 Trading automático cancelado")

if __name__ == "__main__":
    main()
