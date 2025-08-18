#!/usr/bin/env python3
"""
🔍 VERIFICAR CONTA - Status antes de operar
Verifica se está tudo pronto para trading real
"""

import os
import sys
from datetime import datetime

# Adicionar paths
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, 'core'))

def verificar_conta_completa():
    """Verificação completa da conta"""
    print("🔍 VERIFICAÇÃO COMPLETA DA SUA CONTA")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    print()
    
    try:
        # Tenta conectar com dados reais
        from binance_real_data import binance_data
        
        print("🔄 Conectando com sua conta Binance...")
        
        # Verifica saldo
        balance = binance_data.get_account_balance()
        positions = binance_data.get_current_positions()
        trades = binance_data.get_trading_history(days=1)
        
        print("✅ Conexão estabelecida!")
        print()
        
        # SEÇÃO 1: SALDOS
        print("💰 SEUS SALDOS:")
        print("-" * 30)
        print(f"Total em USDT: ${balance['total_usdt']:.2f}")
        print(f"Disponível: ${balance['free_usdt']:.2f}")
        print(f"Em ordens: ${balance['total_usdt'] - balance['free_usdt']:.2f}")
        
        # Status do saldo
        if balance['total_usdt'] >= 50:
            print("✅ Saldo EXCELENTE para trading")
        elif balance['total_usdt'] >= 20:
            print("✅ Saldo BOM para trading")
        elif balance['total_usdt'] >= 10:
            print("⚠️ Saldo MÍNIMO para trading")
        else:
            print("❌ Saldo INSUFICIENTE (mínimo $10)")
        
        print()
        
        # SEÇÃO 2: POSIÇÕES ATUAIS
        print("📊 SUAS POSIÇÕES ATUAIS:")
        print("-" * 30)
        
        if positions and len(positions) > 0:
            total_positions_value = 0
            for pos in positions:
                if pos.get('amount', 0) > 0:
                    symbol = pos.get('symbol', 'Unknown').replace('/USDT', '')
                    amount = pos.get('amount', 0)
                    value = pos.get('market_value', 0)
                    total_positions_value += value
                    
                    print(f"🪙 {symbol}: {amount:.6f} = ${value:.2f}")
            
            if total_positions_value > 0:
                allocation_pct = (total_positions_value / balance['total_usdt']) * 100
                print(f"📈 Total investido: ${total_positions_value:.2f} ({allocation_pct:.1f}%)")
            else:
                print("💵 100% em dinheiro (USDT)")
        else:
            print("💵 100% em dinheiro (USDT) - Pronto para investir!")
        
        print()
        
        # SEÇÃO 3: ATIVIDADE RECENTE
        print("💹 ATIVIDADE RECENTE (24h):")
        print("-" * 30)
        
        if not trades.empty:
            print(f"📊 Trades hoje: {len(trades)}")
            
            # Última operação
            last_trade = trades.tail(1).iloc[0]
            symbol = last_trade.get('symbol', 'N/A').replace('/USDT', '')
            side = 'COMPRA' if last_trade.get('side', '').lower() == 'buy' else 'VENDA'
            value = last_trade.get('cost', 0)
            timestamp = last_trade.get('timestamp', datetime.now())
            
            print(f"⚡ Última: {side} {symbol} - ${value:.2f}")
            print(f"🕐 Quando: {timestamp.strftime('%H:%M')}")
            
            # Performance do dia
            if 'pnl_pct' in trades.columns:
                daily_pnl = trades['pnl_pct'].sum()
                if daily_pnl > 0:
                    print(f"📈 P&L hoje: +{daily_pnl:.2f}%")
                else:
                    print(f"📉 P&L hoje: {daily_pnl:.2f}%")
        else:
            print("😴 Nenhuma operação hoje")
            print("🤖 IA analisando oportunidades...")
        
        print()
        
        # SEÇÃO 4: STATUS PARA TRADING
        print("🎯 STATUS PARA TRADING:")
        print("-" * 30)
        
        # Verificações de segurança
        checks = []
        
        if balance['total_usdt'] >= 10:
            checks.append("✅ Saldo suficiente")
        else:
            checks.append("❌ Saldo insuficiente")
        
        if balance['free_usdt'] >= 5:
            checks.append("✅ Dinheiro livre disponível")
        else:
            checks.append("⚠️ Pouco dinheiro livre")
        
        # Diversificação
        active_positions = len([p for p in positions if p.get('amount', 0) > 0])
        if active_positions <= 3:
            checks.append("✅ Diversificação adequada")
        else:
            checks.append("⚠️ Muitas posições abertas")
        
        for check in checks:
            print(check)
        
        # Recomendação final
        ready_count = len([c for c in checks if c.startswith("✅")])
        total_checks = len(checks)
        
        print()
        if ready_count == total_checks:
            print("🚀 PRONTO PARA TRADING AUTOMÁTICO!")
            print("💡 Execute TRADING_REAL.bat para começar")
        elif ready_count >= total_checks - 1:
            print("⚠️ QUASE PRONTO - Verifique avisos acima")
            print("💡 Pode operar mas com cuidado")
        else:
            print("🔴 NÃO RECOMENDADO OPERAR AGORA")
            print("💡 Resolva os problemas primeiro")
        
    except Exception as e:
        print(f"❌ Erro ao verificar conta: {e}")
        print("💡 Possíveis causas:")
        print("   - Sem internet")
        print("   - API keys incorretas")
        print("   - Problema temporário da Binance")

def main():
    verificar_conta_completa()
    print()
    print("=" * 50)
    print("🔄 Para verificar novamente: execute este script")
    print("🚀 Para iniciar trading: execute TRADING_REAL.bat")
    print("📊 Para dashboard: execute start_dashboard.bat")
    print("=" * 50)

if __name__ == "__main__":
    main()
    input("\n⏸️ Pressione Enter para sair...")
