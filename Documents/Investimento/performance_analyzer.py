#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import os

class PerformanceAnalyzer:
    def __init__(self):
        self.trades_log = []
        self.performance_history = []
        self.analysis_results = {}
        
    def load_data(self):
        """Carregar dados de performance e trades"""
        try:
            # Carregar trades
            if os.path.exists('logs/trades_log.json'):
                with open('logs/trades_log.json', 'r', encoding='utf-8') as f:
                    self.trades_log = json.load(f)
                print(f"📊 {len(self.trades_log)} trades carregados")
            
            # Carregar performance
            if os.path.exists('logs/performance_history.json'):
                with open('logs/performance_history.json', 'r', encoding='utf-8') as f:
                    self.performance_history = json.load(f)
                print(f"📈 {len(self.performance_history)} registros de performance carregados")
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
    
    def analyze_trading_performance(self):
        """Analisar performance dos trades"""
        if not self.trades_log:
            print("❌ Nenhum trade encontrado para análise")
            return
        
        print("\n🔍 ANÁLISE DE PERFORMANCE DOS TRADES")
        print("=" * 60)
        
        # Estatísticas básicas
        total_trades = len(self.trades_log)
        buy_trades = len([t for t in self.trades_log if t['signal'] == 'BUY'])
        sell_trades = len([t for t in self.trades_log if t['signal'] == 'SELL'])
        
        print(f"📊 Total de trades: {total_trades}")
        print(f"🟢 Compras: {buy_trades}")
        print(f"🔴 Vendas: {sell_trades}")
        
        # Análise de confiança
        confidences = [t['confidence'] for t in self.trades_log]
        avg_confidence = np.mean(confidences)
        print(f"🎯 Confiança média: {avg_confidence:.1%}")
        
        # Análise temporal
        if len(self.trades_log) > 1:
            first_trade = datetime.fromisoformat(self.trades_log[0]['timestamp'])
            last_trade = datetime.fromisoformat(self.trades_log[-1]['timestamp'])
            trading_duration = last_trade - first_trade
            trades_per_hour = total_trades / (trading_duration.total_seconds() / 3600)
            
            print(f"⏰ Duração do trading: {trading_duration}")
            print(f"📈 Trades por hora: {trades_per_hour:.2f}")
        
        # Análise de símbolos
        symbols = [t['symbol'] for t in self.trades_log]
        symbol_counts = pd.Series(symbols).value_counts()
        print(f"\n🎯 Símbolos mais negociados:")
        for symbol, count in symbol_counts.head(5).items():
            print(f"   {symbol}: {count} trades")
        
        return {
            'total_trades': total_trades,
            'buy_trades': buy_trades,
            'sell_trades': sell_trades,
            'avg_confidence': avg_confidence,
            'trades_per_hour': trades_per_hour if len(self.trades_log) > 1 else 0
        }
    
    def analyze_profitability(self):
        """Analisar lucratividade"""
        if not self.performance_history:
            print("❌ Nenhum dado de performance encontrado")
            return
        
        print("\n💰 ANÁLISE DE LUCRATIVIDADE")
        print("=" * 60)
        
        # Converter para DataFrame
        df = pd.DataFrame(self.performance_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Análise de retorno
        initial_balance = df['initial_balance'].iloc[0]
        final_balance = df['current_balance'].iloc[-1]
        total_return = final_balance - initial_balance
        total_return_pct = (total_return / initial_balance) * 100 if initial_balance > 0 else 0
        
        print(f"💰 Saldo inicial: ${initial_balance:.2f}")
        print(f"💰 Saldo final: ${final_balance:.2f}")
        print(f"📈 Retorno total: ${total_return:.2f} ({total_return_pct:+.2f}%)")
        
        # Análise de volatilidade
        if len(df) > 1:
            returns = df['profit_percentage'].diff().dropna()
            volatility = returns.std()
            sharpe_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0
            
            print(f"📊 Volatilidade: {volatility:.2f}%")
            print(f"📈 Sharpe Ratio: {sharpe_ratio:.2f}")
        
        # Análise de drawdown
        if len(df) > 1:
            cumulative_returns = (1 + df['profit_percentage'] / 100).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max * 100
            max_drawdown = drawdown.min()
            
            print(f"📉 Máximo drawdown: {max_drawdown:.2f}%")
        
        return {
            'initial_balance': initial_balance,
            'final_balance': final_balance,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'volatility': volatility if len(df) > 1 else 0,
            'sharpe_ratio': sharpe_ratio if len(df) > 1 else 0,
            'max_drawdown': max_drawdown if len(df) > 1 else 0
        }
    
    def compare_with_benchmarks(self):
        """Comparar com benchmarks de mercado"""
        print("\n🏆 COMPARAÇÃO COM BENCHMARKS")
        print("=" * 60)
        
        # Benchmarks típicos
        benchmarks = {
            'Bitcoin (BTC)': 15.0,  # Retorno anual médio
            'S&P 500': 10.0,        # Retorno anual médio
            'Trading Manual': 5.0,   # Retorno médio de traders manuais
            'HODL Strategy': 12.0,   # Estratégia buy and hold
        }
        
        # Calcular retorno anualizado do nosso sistema
        if self.performance_history:
            df = pd.DataFrame(self.performance_history)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            if len(df) > 1:
                total_days = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).days
                total_return_pct = df['profit_percentage'].iloc[-1]
                
                if total_days > 0:
                    annualized_return = (1 + total_return_pct / 100) ** (365 / total_days) - 1
                    annualized_return_pct = annualized_return * 100
                    
                    print(f"📊 Retorno anualizado do sistema: {annualized_return_pct:+.2f}%")
                    print(f"⏰ Período analisado: {total_days} dias")
                    
                    print(f"\n🏆 Comparação com benchmarks:")
                    for benchmark, return_pct in benchmarks.items():
                        comparison = annualized_return_pct - return_pct
                        status = "✅ SUPERIOR" if comparison > 0 else "❌ INFERIOR"
                        print(f"   {benchmark}: {return_pct:.1f}% | {status} ({comparison:+.1f}%)")
                    
                    return annualized_return_pct
                else:
                    print("❌ Período insuficiente para análise anualizada")
            else:
                print("❌ Dados insuficientes para análise")
        
        return None
    
    def assess_training_needs(self):
        """Avaliar se o sistema precisa de mais treinamento"""
        print("\n🎓 AVALIAÇÃO DE NECESSIDADE DE TREINAMENTO")
        print("=" * 60)
        
        training_score = 0
        recommendations = []
        
        # Critérios de avaliação
        if self.trades_log:
            # 1. Volume de trades
            total_trades = len(self.trades_log)
            if total_trades < 10:
                training_score += 30
                recommendations.append("📈 Volume baixo de trades - precisa de mais dados")
            elif total_trades < 50:
                training_score += 15
                recommendations.append("📈 Volume moderado - pode precisar de mais dados")
            else:
                training_score += 0
                recommendations.append("✅ Volume adequado de trades")
            
            # 2. Confiança média
            confidences = [t['confidence'] for t in self.trades_log]
            avg_confidence = np.mean(confidences)
            if avg_confidence < 0.6:
                training_score += 25
                recommendations.append("🎯 Confiança baixa - sistema incerto")
            elif avg_confidence < 0.75:
                training_score += 15
                recommendations.append("🎯 Confiança moderada - pode melhorar")
            else:
                training_score += 0
                recommendations.append("✅ Confiança alta - sistema confiável")
        
        if self.performance_history:
            # 3. Retorno vs benchmarks
            df = pd.DataFrame(self.performance_history)
            total_return_pct = df['profit_percentage'].iloc[-1]
            
            if total_return_pct < 0:
                training_score += 30
                recommendations.append("📉 Retorno negativo - precisa de ajustes")
            elif total_return_pct < 5:
                training_score += 20
                recommendations.append("📈 Retorno baixo - pode melhorar")
            elif total_return_pct < 15:
                training_score += 10
                recommendations.append("📈 Retorno moderado - aceitável")
            else:
                training_score += 0
                recommendations.append("✅ Retorno excelente - sistema funcionando bem")
            
            # 4. Volatilidade
            if len(df) > 1:
                returns = df['profit_percentage'].diff().dropna()
                volatility = returns.std()
                
                if volatility > 10:
                    training_score += 20
                    recommendations.append("📊 Alta volatilidade - muito arriscado")
                elif volatility > 5:
                    training_score += 10
                    recommendations.append("📊 Volatilidade moderada - aceitável")
                else:
                    training_score += 0
                    recommendations.append("✅ Baixa volatilidade - estável")
        
        # 5. Frequência de trades
        if self.trades_log and len(self.trades_log) > 1:
            first_trade = datetime.fromisoformat(self.trades_log[0]['timestamp'])
            last_trade = datetime.fromisoformat(self.trades_log[-1]['timestamp'])
            trading_duration = last_trade - first_trade
            trades_per_hour = len(self.trades_log) / (trading_duration.total_seconds() / 3600)
            
            if trades_per_hour < 0.1:
                training_score += 15
                recommendations.append("⏰ Frequência baixa - pode estar perdendo oportunidades")
            elif trades_per_hour > 2:
                training_score += 10
                recommendations.append("⏰ Frequência alta - pode estar overtrading")
            else:
                training_score += 0
                recommendations.append("✅ Frequência adequada de trades")
        
        # Resultado final
        print(f"🎯 Score de necessidade de treinamento: {training_score}/100")
        
        if training_score >= 80:
            print("🔴 NECESSIDADE ALTA de treinamento")
            print("   - Sistema precisa de ajustes significativos")
            print("   - Recomenda-se mais dados e otimização")
        elif training_score >= 50:
            print("🟡 NECESSIDADE MODERADA de treinamento")
            print("   - Sistema pode melhorar com ajustes")
            print("   - Algumas otimizações recomendadas")
        else:
            print("🟢 NECESSIDADE BAIXA de treinamento")
            print("   - Sistema funcionando bem")
            print("   - Manutenção regular suficiente")
        
        print(f"\n📋 Recomendações:")
        for rec in recommendations:
            print(f"   {rec}")
        
        return training_score, recommendations
    
    def generate_report(self):
        """Gerar relatório completo"""
        print("📊 RELATÓRIO DE PERFORMANCE DO SISTEMA")
        print("=" * 80)
        print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Carregar dados
        self.load_data()
        
        # Análises
        trading_metrics = self.analyze_trading_performance()
        profitability_metrics = self.analyze_profitability()
        benchmark_comparison = self.compare_with_benchmarks()
        training_needs = self.assess_training_needs()
        
        # Resumo executivo
        print("\n📋 RESUMO EXECUTIVO")
        print("=" * 60)
        
        if trading_metrics:
            print(f"🎯 Total de trades: {trading_metrics['total_trades']}")
            print(f"📈 Trades por hora: {trading_metrics['trades_per_hour']:.2f}")
            print(f"🎯 Confiança média: {trading_metrics['avg_confidence']:.1%}")
        
        if profitability_metrics:
            print(f"💰 Retorno total: {profitability_metrics['total_return_pct']:+.2f}%")
            if profitability_metrics['sharpe_ratio'] > 0:
                print(f"📊 Sharpe Ratio: {profitability_metrics['sharpe_ratio']:.2f}")
            print(f"📉 Máximo drawdown: {profitability_metrics['max_drawdown']:.2f}%")
        
        if benchmark_comparison:
            print(f"🏆 Retorno anualizado: {benchmark_comparison:+.2f}%")
        
        if training_needs:
            score, recommendations = training_needs
            print(f"🎓 Score de treinamento: {score}/100")
        
        # Salvar relatório
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'trading_metrics': trading_metrics,
            'profitability_metrics': profitability_metrics,
            'benchmark_comparison': benchmark_comparison,
            'training_needs': training_needs
        }
        
        with open('logs/performance_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo em: logs/performance_report.json")

def main():
    """Função principal"""
    print("📊 ANALISADOR DE PERFORMANCE")
    print("=" * 60)
    
    analyzer = PerformanceAnalyzer()
    analyzer.generate_report()

if __name__ == "__main__":
    main()
