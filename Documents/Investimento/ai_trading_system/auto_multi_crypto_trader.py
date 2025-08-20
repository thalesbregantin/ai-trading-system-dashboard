#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import schedule
from multi_crypto_trader import MultiCryptoTrader
import json
from datetime import datetime

class AutoMultiCryptoTrader:
    def __init__(self):
        self.trader = MultiCryptoTrader()
        self.cycle_count = 0
        self.total_trades = 0
        self.performance_log = []
        
    def setup_system(self):
        """Configurar sistema"""
        print("🤖 CONFIGURANDO SISTEMA MULTI-CRYPTO AUTOMÁTICO")
        print("=" * 60)
        
        # Configurar Binance
        if not self.trader.setup_binance():
            print("❌ Falha ao configurar Binance")
            return False
        
        # Mostrar configuração inicial
        print(f"📊 Criptos configuradas: {len(self.trader.crypto_pairs)}")
        for i, symbol in enumerate(self.trader.crypto_pairs, 1):
            print(f"   {i:2d}. {symbol}")
        
        # Mostrar saldo inicial
        summary = self.trader.get_performance_summary()
        if summary:
            print(f"\n💰 Saldo inicial:")
            print(f"   USDT: ${summary['usdt_balance']:.2f}")
            print(f"   Portfolio total: ${summary['total_portfolio']:.2f}")
        
        return True
    
    def run_trading_cycle(self):
        """Executar um ciclo de trading"""
        try:
            self.cycle_count += 1
            print(f"\n🔄 CICLO #{self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 40)
            
            # Executar ciclo
            success = self.trader.run_multi_crypto_cycle()
            
            if success:
                # Obter resumo atualizado
                summary = self.trader.get_performance_summary()
                if summary:
                    # Registrar performance
                    performance_data = {
                        'cycle': self.cycle_count,
                        'timestamp': datetime.now().isoformat(),
                        'usdt_balance': summary['usdt_balance'],
                        'crypto_value': summary['crypto_value'],
                        'total_portfolio': summary['total_portfolio'],
                        'total_trades': summary['total_trades'],
                        'portfolio_change': 0  # Será calculado
                    }
                    
                    # Calcular mudança no portfolio
                    if len(self.performance_log) > 0:
                        prev_portfolio = self.performance_log[-1]['total_portfolio']
                        portfolio_change = ((summary['total_portfolio'] - prev_portfolio) / prev_portfolio) * 100
                        performance_data['portfolio_change'] = portfolio_change
                    
                    self.performance_log.append(performance_data)
                    
                    # Mostrar resumo
                    print(f"📊 Resumo do ciclo #{self.cycle_count}:")
                    print(f"   💰 USDT: ${summary['usdt_balance']:.2f}")
                    print(f"   📈 Criptos: ${summary['crypto_value']:.2f}")
                    print(f"   💼 Total: ${summary['total_portfolio']:.2f}")
                    print(f"   📊 Trades: {summary['total_trades']}")
                    
                    if len(self.performance_log) > 1:
                        change = performance_data['portfolio_change']
                        if change > 0:
                            print(f"   📈 Variação: +{change:.2f}%")
                        else:
                            print(f"   📉 Variação: {change:.2f}%")
                    
                    # Salvar log
                    self.save_performance_log()
            
            return success
            
        except Exception as e:
            print(f"❌ Erro no ciclo #{self.cycle_count}: {e}")
            return False
    
    def save_performance_log(self):
        """Salvar log de performance"""
        try:
            with open('logs/multi_crypto_performance.json', 'w') as f:
                json.dump(self.performance_log, f, indent=2)
        except Exception as e:
            print(f"❌ Erro ao salvar log: {e}")
    
    def show_performance_summary(self):
        """Mostrar resumo de performance"""
        if not self.performance_log:
            print("📊 Nenhum dado de performance disponível")
            return
        
        print("\n📊 RESUMO DE PERFORMANCE")
        print("=" * 40)
        
        latest = self.performance_log[-1]
        initial = self.performance_log[0]
        
        total_change = ((latest['total_portfolio'] - initial['total_portfolio']) / initial['total_portfolio']) * 100
        
        print(f"🔄 Ciclos executados: {self.cycle_count}")
        print(f"📈 Portfolio inicial: ${initial['total_portfolio']:.2f}")
        print(f"📊 Portfolio atual: ${latest['total_portfolio']:.2f}")
        print(f"💰 Variação total: {total_change:+.2f}%")
        print(f"📊 Total de trades: {latest['total_trades']}")
        
        # Calcular métricas
        if len(self.performance_log) > 1:
            changes = [p['portfolio_change'] for p in self.performance_log[1:]]
            avg_change = sum(changes) / len(changes)
            positive_cycles = len([c for c in changes if c > 0])
            win_rate = (positive_cycles / len(changes)) * 100
            
            print(f"📈 Variação média por ciclo: {avg_change:+.2f}%")
            print(f"🎯 Taxa de sucesso: {win_rate:.1f}%")
    
    def run_automated_trading(self, interval_minutes=10):
        """Executar trading automático"""
        print(f"🤖 INICIANDO TRADING AUTOMÁTICO MULTI-CRYPTO")
        print(f"⏰ Intervalo: {interval_minutes} minutos")
        print(f"🛑 Pressione Ctrl+C para parar")
        print("=" * 60)
        
        try:
            while True:
                # Executar ciclo
                success = self.run_trading_cycle()
                
                if success:
                    print(f"✅ Ciclo #{self.cycle_count} concluído")
                else:
                    print(f"❌ Falha no ciclo #{self.cycle_count}")
                
                # Mostrar próximo ciclo
                next_time = datetime.now().timestamp() + (interval_minutes * 60)
                next_time_str = datetime.fromtimestamp(next_time).strftime('%H:%M:%S')
                print(f"⏳ Próximo ciclo: {next_time_str}")
                
                # Aguardar
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Trading automático interrompido pelo usuário")
            self.show_performance_summary()
            
            # Salvar log final
            self.save_performance_log()
            print("💾 Log de performance salvo")

def main():
    """Função principal"""
    print("🚀 AI TRADING SYSTEM - MULTI-CRYPTO AUTOMÁTICO")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Criar trader automático
    auto_trader = AutoMultiCryptoTrader()
    
    # Configurar sistema
    if not auto_trader.setup_system():
        return
    
    print("\n" + "=" * 60)
    
    # Perguntar configurações
    try:
        interval = int(input("⏰ Intervalo entre ciclos (minutos, padrão 10): ") or "10")
    except ValueError:
        interval = 10
    
    print(f"\n⚙️ Configuração:")
    print(f"   Intervalo: {interval} minutos")
    print(f"   Criptos: {len(auto_trader.trader.crypto_pairs)}")
    
    print("\n" + "=" * 60)
    
    # Confirmar início
    response = input("🤔 Quer iniciar o trading automático multi-cripto? (s/n): ")
    
    if response.lower() == 's':
        print("\n🚀 INICIANDO TRADING AUTOMÁTICO...")
        auto_trader.run_automated_trading(interval)
    else:
        print("👌 Trading automático cancelado")

if __name__ == "__main__":
    main()
