#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import os

class ExtendedTrainingAnalyzer:
    def __init__(self):
        self.metrics_file = "logs/training/training_metrics.csv"
        self.analysis_results = {}
        
    def load_training_metrics(self):
        """Carregar métricas de treinamento"""
        try:
            if os.path.exists(self.metrics_file):
                df = pd.read_csv(self.metrics_file)
                return df
            else:
                print(f"❌ Arquivo de métricas não encontrado: {self.metrics_file}")
                return None
        except Exception as e:
            print(f"❌ Erro ao carregar métricas: {e}")
            return None
    
    def analyze_training_performance(self, df):
        """Analisar performance do treinamento"""
        if df is None or df.empty:
            return None
        
        analysis = {
            'total_episodes': len(df),
            'avg_return': df['total_return_pct'].mean(),
            'max_return': df['total_return_pct'].max(),
            'min_return': df['total_return_pct'].min(),
            'avg_win_rate': df['win_rate'].mean(),
            'avg_sharpe': df['sharpe'].mean(),
            'avg_trades': df['num_trades'].mean(),
            'final_epsilon': df['epsilon'].iloc[-1],
            'improvement_trend': self.calculate_improvement_trend(df),
            'consistency_score': self.calculate_consistency_score(df),
            'risk_adjusted_return': self.calculate_risk_adjusted_return(df)
        }
        
        return analysis
    
    def calculate_improvement_trend(self, df):
        """Calcular tendência de melhoria"""
        if len(df) < 10:
            return 0
        
        # Dividir em períodos
        first_half = df['total_return_pct'].iloc[:len(df)//2].mean()
        second_half = df['total_return_pct'].iloc[len(df)//2:].mean()
        
        improvement = second_half - first_half
        return improvement
    
    def calculate_consistency_score(self, df):
        """Calcular score de consistência"""
        if len(df) < 5:
            return 0
        
        # Calcular desvio padrão dos retornos
        returns_std = df['total_return_pct'].std()
        avg_return = df['total_return_pct'].mean()
        
        # Score baseado na relação retorno/volatilidade
        if returns_std > 0:
            consistency = avg_return / returns_std
        else:
            consistency = avg_return
        
        return consistency
    
    def calculate_risk_adjusted_return(self, df):
        """Calcular retorno ajustado ao risco"""
        if len(df) < 5:
            return 0
        
        avg_return = df['total_return_pct'].mean()
        returns_std = df['total_return_pct'].std()
        
        if returns_std > 0:
            sharpe_ratio = avg_return / returns_std
        else:
            sharpe_ratio = avg_return
        
        return sharpe_ratio
    
    def determine_training_needs(self, analysis):
        """Determinar se mais treinamento é necessário"""
        if not analysis:
            return "INSUFICIENT_DATA"
        
        recommendations = []
        score = 0
        
        # Critérios para mais treinamento
        
        # 1. Retorno médio baixo
        if analysis['avg_return'] < 20:
            recommendations.append("Retorno médio baixo (< 20%)")
            score += 2
        
        # 2. Win rate baixo
        if analysis['avg_win_rate'] < 55:
            recommendations.append("Win rate baixo (< 55%)")
            score += 2
        
        # 3. Sharpe ratio baixo
        if analysis['avg_sharpe'] < 0.5:
            recommendations.append("Sharpe ratio baixo (< 0.5)")
            score += 2
        
        # 4. Tendência de melhoria fraca
        if analysis['improvement_trend'] < 10:
            recommendations.append("Pouca melhoria ao longo do treinamento")
            score += 1
        
        # 5. Consistência baixa
        if analysis['consistency_score'] < 0.5:
            recommendations.append("Baixa consistência nos resultados")
            score += 1
        
        # 6. Epsilon ainda alto (muita exploração)
        if analysis['final_epsilon'] > 0.3:
            recommendations.append("Ainda explorando muito (epsilon alto)")
            score += 1
        
        # Determinar recomendação
        if score >= 4:
            recommendation = "HIGH_TRAINING_NEED"
        elif score >= 2:
            recommendation = "MODERATE_TRAINING_NEED"
        else:
            recommendation = "LOW_TRAINING_NEED"
        
        return {
            'recommendation': recommendation,
            'score': score,
            'reasons': recommendations,
            'analysis': analysis
        }
    
    def suggest_training_parameters(self, analysis):
        """Sugerir parâmetros de treinamento otimizados"""
        if not analysis:
            return None
        
        suggestions = {
            'episodes': 100,  # Base
            'learning_rate': 0.001,
            'batch_size': 32,
            'epsilon_decay': 0.995,
            'target_update_freq': 100,
            'memory_size': 10000
        }
        
        # Ajustar baseado na análise
        if analysis['avg_return'] < 15:
            suggestions['episodes'] = 200
            suggestions['learning_rate'] = 0.0005  # Mais conservador
        
        if analysis['avg_win_rate'] < 50:
            suggestions['episodes'] = 150
            suggestions['batch_size'] = 64  # Mais dados por batch
        
        if analysis['consistency_score'] < 0.3:
            suggestions['epsilon_decay'] = 0.998  # Explorar mais
            suggestions['memory_size'] = 20000  # Mais memória
        
        if analysis['improvement_trend'] < 5:
            suggestions['episodes'] = 250
            suggestions['target_update_freq'] = 50  # Atualizar mais frequentemente
        
        return suggestions
    
    def generate_training_report(self):
        """Gerar relatório completo de treinamento"""
        print("📊 ANÁLISE DE TREINAMENTO ESTENDIDA")
        print("=" * 60)
        
        # Carregar dados
        df = self.load_training_metrics()
        if df is None:
            return
        
        # Analisar performance
        analysis = self.analyze_training_performance(df)
        if not analysis:
            return
        
        # Determinar necessidades
        training_needs = self.determine_training_needs(analysis)
        
        # Sugerir parâmetros
        suggestions = self.suggest_training_parameters(analysis)
        
        # Mostrar resultados
        print(f"\n📈 MÉTRICAS DE PERFORMANCE:")
        print(f"   Episódios totais: {analysis['total_episodes']}")
        print(f"   Retorno médio: {analysis['avg_return']:.2f}%")
        print(f"   Retorno máximo: {analysis['max_return']:.2f}%")
        print(f"   Retorno mínimo: {analysis['min_return']:.2f}%")
        print(f"   Win rate médio: {analysis['avg_win_rate']:.1f}%")
        print(f"   Sharpe ratio médio: {analysis['avg_sharpe']:.3f}")
        print(f"   Trades médios: {analysis['avg_trades']:.1f}")
        print(f"   Epsilon final: {analysis['final_epsilon']:.3f}")
        print(f"   Tendência de melhoria: {analysis['improvement_trend']:.2f}%")
        print(f"   Score de consistência: {analysis['consistency_score']:.3f}")
        print(f"   Retorno ajustado ao risco: {analysis['risk_adjusted_return']:.3f}")
        
        print(f"\n🎯 RECOMENDAÇÃO DE TREINAMENTO:")
        if training_needs['recommendation'] == "HIGH_TRAINING_NEED":
            print("   🔴 NECESSIDADE ALTA de mais treinamento")
        elif training_needs['recommendation'] == "MODERATE_TRAINING_NEED":
            print("   🟡 NECESSIDADE MODERADA de mais treinamento")
        else:
            print("   🟢 NECESSIDADE BAIXA de mais treinamento")
        
        print(f"   Score: {training_needs['score']}/8")
        
        if training_needs['reasons']:
            print(f"   Razões:")
            for reason in training_needs['reasons']:
                print(f"     • {reason}")
        
        if suggestions:
            print(f"\n⚙️ PARÂMETROS SUGERIDOS:")
            print(f"   Episódios: {suggestions['episodes']}")
            print(f"   Learning rate: {suggestions['learning_rate']}")
            print(f"   Batch size: {suggestions['batch_size']}")
            print(f"   Epsilon decay: {suggestions['epsilon_decay']}")
            print(f"   Target update freq: {suggestions['target_update_freq']}")
            print(f"   Memory size: {suggestions['memory_size']}")
        
        # Salvar relatório
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'training_needs': training_needs,
            'suggestions': suggestions
        }
        
        with open('logs/training_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Relatório salvo em: logs/training_analysis_report.json")
        
        return report
    
    def plot_training_progress(self, df):
        """Plotar progresso do treinamento"""
        if df is None or df.empty:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Retorno por episódio
        axes[0, 0].plot(df['episode'], df['total_return_pct'], 'b-', linewidth=2)
        axes[0, 0].set_title('Retorno por Episódio')
        axes[0, 0].set_xlabel('Episódio')
        axes[0, 0].set_ylabel('Retorno (%)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Win rate por episódio
        axes[0, 1].plot(df['episode'], df['win_rate'], 'g-', linewidth=2)
        axes[0, 1].set_title('Win Rate por Episódio')
        axes[0, 1].set_xlabel('Episódio')
        axes[0, 1].set_ylabel('Win Rate (%)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Sharpe ratio por episódio
        axes[1, 0].plot(df['episode'], df['sharpe'], 'r-', linewidth=2)
        axes[1, 0].set_title('Sharpe Ratio por Episódio')
        axes[1, 0].set_xlabel('Episódio')
        axes[1, 0].set_ylabel('Sharpe Ratio')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Epsilon por episódio
        axes[1, 1].plot(df['episode'], df['epsilon'], 'purple', linewidth=2)
        axes[1, 1].set_title('Epsilon por Episódio')
        axes[1, 1].set_xlabel('Episódio')
        axes[1, 1].set_ylabel('Epsilon')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('logs/training_progress.png', dpi=300, bbox_inches='tight')
        print("📊 Gráfico salvo em: logs/training_progress.png")

def main():
    """Função principal"""
    print("🔍 ANALISADOR DE TREINAMENTO ESTENDIDO")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Criar analisador
    analyzer = ExtendedTrainingAnalyzer()
    
    # Gerar relatório
    report = analyzer.generate_training_report()
    
    if report:
        # Plotar gráficos
        df = analyzer.load_training_metrics()
        analyzer.plot_training_progress(df)
        
        print("\n✅ Análise concluída!")
        print("📊 Verifique os gráficos e relatório gerados.")
    else:
        print("\n❌ Falha na análise")

if __name__ == "__main__":
    main()
