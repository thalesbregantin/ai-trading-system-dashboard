#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Walk-Forward Optimization System v3.0 - CORRIGIDO
=================================================
Versão corrigida que usa o genetic_optimizer_v3_fixed para dados externos.
Combate overfitting através de validação out-of-sample sequencial.
"""

import logging
import json
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from genetic_optimizer_v3_fixed import GeneticTradingOptimizer

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/walk_forward_v3_fixed.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WalkForwardOptimizerV3:
    """
    Sistema de Walk-Forward Optimization v3.0 - CORRIGIDO
    """
    
    def __init__(self):
        self.data_dir = Path("data")
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Parâmetros Walk-Forward
        self.training_window_pct = 0.6  # 60% para treino
        self.testing_window_pct = 0.2   # 20% para teste
        self.step_size_pct = 0.2        # Avançar a janela pelo tamanho do teste
        
        # Pares de trading
        self.trading_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT']
        
        # Instanciar o motor de simulação e otimização CORRIGIDO
        self.optimizer_engine = GeneticTradingOptimizer()
        
        logger.info("🚀 WALK-FORWARD OPTIMIZER v3.0 - CORRIGIDO")
        logger.info(f"📊 Pares: {self.trading_pairs}")
        logger.info(f"🎯 Treino: {self.training_window_pct*100}%, Teste: {self.testing_window_pct*100}%, Step: {self.step_size_pct*100}%")

    def load_all_data(self):
        """Carrega todos os dados para os pares de trading."""
        logger.info("📥 Carregando dados para Walk-Forward...")
        full_data = {}
        for symbol in self.trading_pairs:
            data_file = self.data_dir / f"{symbol.replace('/', '_')}_extended.csv"
            if data_file.exists():
                data = pd.read_csv(data_file, index_col=0, parse_dates=True)
                # Garantir que as colunas estão no formato correto
                if 'Close' in data.columns:
                    data['close'] = data['Close']
                full_data[symbol] = data
                logger.info(f"✅ {symbol}: {len(data)} pontos de dados")
            else:
                logger.warning(f"⚠️ Arquivo não encontrado: {data_file}")
        return full_data

    def create_data_windows(self, full_data):
        """Cria janelas de dados sequenciais para o Walk-Forward."""
        logger.info("🔄 Criando janelas de dados...")
        reference_data = next(iter(full_data.values()))
        total_points = len(reference_data)
        
        training_size = int(total_points * self.training_window_pct)
        testing_size = int(total_points * self.testing_window_pct)
        step_size = int(total_points * self.step_size_pct)
        
        windows = []
        start_index = 0
        
        while start_index + training_size + testing_size <= total_points:
            end_training = start_index + training_size
            end_testing = end_training + testing_size
            
            training_data = {s: d.iloc[start_index:end_training] for s, d in full_data.items()}
            testing_data = {s: d.iloc[end_training:end_testing] for s, d in full_data.items()}
            
            windows.append({
                'id': len(windows) + 1,
                'training_data': training_data,
                'testing_data': testing_data,
                'training_dates': (training_data[self.trading_pairs[0]].index[0], training_data[self.trading_pairs[0]].index[-1]),
                'testing_dates': (testing_data[self.trading_pairs[0]].index[0], testing_data[self.trading_pairs[0]].index[-1])
            })
            start_index += step_size
            
        logger.info(f"✅ Criadas {len(windows)} janelas de Walk-Forward")
        return windows

    def run_optimization_on_window(self, training_data):
        """Executa otimização genética na janela de treino."""
        logger.info(f"🧬 Otimizando na janela de treino...")
        try:
            # Usar o método corrigido que aceita dados externos
            best_params = self.optimizer_engine.run_optimization(training_data)
            logger.info(f"✅ Otimização concluída: {best_params}")
            return best_params
        except Exception as e:
            logger.error(f"❌ Erro na otimização: {e}")
            return None

    def run_backtest_on_window(self, testing_data, best_params):
        """Executa backtest na janela de teste com os melhores parâmetros."""
        logger.info(f"📊 Testando na janela out-of-sample...")
        try:
            all_results = []
            total_profit = 0
            total_trades = 0
            total_wins = 0
            
            for symbol, data in testing_data.items():
                # Usar o método corrigido que aceita dados externos
                result = self.optimizer_engine.simulate_trading(symbol, list(best_params.values()), data_override=data)
                if result:
                    all_results.append(result)
                    total_profit += result['profit']
                    total_trades += result['trades']
                    total_wins += result['wins']
            
            return {
                'total_profit': total_profit,
                'total_trades': total_trades,
                'total_wins': total_wins,
                'win_rate': (total_wins / total_trades * 100) if total_trades > 0 else 0,
                'params_used': best_params,
                'individual_results': all_results
            }
        except Exception as e:
            logger.error(f"❌ Erro no backtest: {e}")
            return None

    def process_windows(self, windows):
        """Processa todas as janelas de Walk-Forward."""
        logger.info("🔄 Processando janelas de Walk-Forward...")
        out_of_sample_results = []
        
        for i, window in enumerate(windows):
            logger.info(f"\n📊 JANELA {window['id']}/{len(windows)}")
            logger.info(f"   🎓 Treino: {window['training_dates'][0]} a {window['training_dates'][1]}")
            logger.info(f"   🧪 Teste: {window['testing_dates'][0]} a {window['testing_dates'][1]}")
            
            # 1. Otimizar na janela de treino
            best_params = self.run_optimization_on_window(window['training_data'])
            if not best_params:
                logger.warning(f"⚠️ Falha na otimização da janela {window['id']}")
                continue
            
            # 2. Testar na janela de teste (out-of-sample)
            test_result = self.run_backtest_on_window(window['testing_data'], best_params)
            if not test_result:
                logger.warning(f"⚠️ Falha no backtest da janela {window['id']}")
                continue
            
            # 3. Armazenar resultado
            test_result['window_id'] = window['id']
            test_result['training_dates'] = window['training_dates']
            test_result['testing_dates'] = window['testing_dates']
            out_of_sample_results.append(test_result)
            
            logger.info(f"   💰 Resultado: ${test_result['total_profit']:.2f} ({test_result['total_trades']} trades, {test_result['win_rate']:.1f}% win rate)")
        
        logger.info(f"\n✅ Processamento concluído: {len(out_of_sample_results)}/{len(windows)} janelas")
        return out_of_sample_results

    def analyze_final_results(self, out_of_sample_results):
        """Analisa os resultados finais do Walk-Forward."""
        logger.info("📊 Analisando resultados finais...")
        
        if not out_of_sample_results:
            logger.error("❌ Nenhum resultado para analisar")
            return None
        
        # Métricas de performance
        total_profit = sum(r['total_profit'] for r in out_of_sample_results)
        total_trades = sum(r['total_trades'] for r in out_of_sample_results)
        total_wins = sum(r['total_wins'] for r in out_of_sample_results)
        
        # Sharpe Ratio (simplificado)
        profits = [r['total_profit'] for r in out_of_sample_results]
        sharpe_ratio = np.mean(profits) / np.std(profits) if np.std(profits) > 0 else 0
        
        # Max Drawdown (simplificado)
        cumulative_profits = np.cumsum(profits)
        max_drawdown = 0
        if len(cumulative_profits) > 1:
            peak = np.maximum.accumulate(cumulative_profits)
            drawdown = (cumulative_profits - peak) / peak
            max_drawdown = np.min(drawdown)
        
        # Profit Factor
        positive_profits = [p for p in profits if p > 0]
        negative_profits = [p for p in profits if p < 0]
        profit_factor = sum(positive_profits) / abs(sum(negative_profits)) if negative_profits else float('inf')

        # Análise de Estabilidade de Parâmetros
        params_df = pd.DataFrame([r['params_used'] for r in out_of_sample_results])
        params_stability = {
            'mean': params_df.mean().to_dict(),
            'std_dev': params_df.std().to_dict(),
            'coefficient_of_variation': (params_df.std() / params_df.mean()).to_dict()
        }

        # Calcular estabilidade geral
        stability_score = 0
        if len(params_df) > 1:
            cv_values = [v for v in params_stability['coefficient_of_variation'].values() if not np.isnan(v)]
            if cv_values:
                avg_cv = np.mean(cv_values)
                stability_score = max(0, 100 - (avg_cv * 100))

        final_report = {
            'run_date': datetime.now().isoformat(),
            'performance_summary': {
                'total_profit': total_profit,
                'total_trades': total_trades,
                'win_rate': (total_wins / total_trades * 100) if total_trades > 0 else 0,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'profit_factor': profit_factor,
                'consistency_rate': (sum(1 for r in out_of_sample_results if r['total_profit'] > 0) / len(out_of_sample_results)) * 100
            },
            'parameter_stability': {
                'stability_score': stability_score,
                'mean_parameters': params_stability['mean'],
                'std_dev_parameters': params_stability['std_dev'],
                'coefficient_of_variation': params_stability['coefficient_of_variation']
            },
            'window_details': out_of_sample_results
        }
        
        report_file = self.results_dir / "walk_forward_results_v3_fixed.json"
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=4, default=str)
            
        # Log dos resultados
        logger.info("🏆 RESULTADOS WALK-FORWARD v3.0 - CORRIGIDO:")
        logger.info(f"   📊 Janelas processadas: {len(out_of_sample_results)}")
        logger.info(f"   💰 Lucro total: ${total_profit:.2f}")
        logger.info(f"   📈 Total de trades: {total_trades}")
        logger.info(f"   🎯 Win rate: {(total_wins / total_trades * 100) if total_trades > 0 else 0:.1f}%")
        logger.info(f"   📊 Sharpe Ratio: {sharpe_ratio:.3f}")
        logger.info(f"   📉 Max Drawdown: {max_drawdown:.2%}")
        logger.info(f"   📈 Profit Factor: {profit_factor:.2f}")
        logger.info(f"   🔄 Taxa de consistência: {(sum(1 for r in out_of_sample_results if r['total_profit'] > 0) / len(out_of_sample_results)) * 100:.1f}%")
        logger.info(f"   🎯 Score de estabilidade: {stability_score:.1f}/100")
        
        # Recomendações baseadas na estabilidade
        logger.info("\n🎯 RECOMENDAÇÕES:")
        if stability_score >= 80:
            logger.info("   ✅ Parâmetros MUITO ESTÁVEIS - Alta confiança na estratégia")
        elif stability_score >= 60:
            logger.info("   ⚠️ Parâmetros MODERADAMENTE ESTÁVEIS - Estratégia aceitável")
        else:
            logger.info("   ❌ Parâmetros INSTÁVEIS - Revisar abordagem fundamental")
            
        logger.info(f"\n💾 Relatório final salvo em: {report_file}")
        return final_report

    def run(self):
        """Orquestra o processo completo de Walk-Forward Optimization."""
        logger.info("🚀 INICIANDO WALK-FORWARD OPTIMIZATION v3.0 - CORRIGIDO")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # 1. Carregar dados
        full_data = self.load_all_data()
        if not full_data:
            logger.error("❌ Nenhum dado encontrado")
            return None
            
        # 2. Criar janelas
        windows = self.create_data_windows(full_data)
        if not windows:
            logger.error("❌ Não foi possível criar janelas")
            return None
            
        # 3. Processar janelas
        out_of_sample_results = self.process_windows(windows)
        if not out_of_sample_results:
            logger.error("❌ Nenhum resultado obtido")
            return None
            
        # 4. Analisar resultados
        final_report = self.analyze_final_results(out_of_sample_results)
        
        elapsed_time = time.time() - start_time
        logger.info(f"\n⏱️ Tempo total: {elapsed_time:.1f} segundos")
        logger.info("🎉 WALK-FORWARD OPTIMIZATION CONCLUÍDO!")
        
        return final_report

def main():
    """Função principal."""
    optimizer = WalkForwardOptimizerV3()
    results = optimizer.run()
    
    if results:
        print("\n🎯 RESUMO FINAL:")
        print(f"💰 Lucro Total: ${results['performance_summary']['total_profit']:.2f}")
        print(f"📊 Sharpe Ratio: {results['performance_summary']['sharpe_ratio']:.3f}")
        print(f"🎯 Estabilidade: {results['parameter_stability']['stability_score']:.1f}/100")
    else:
        print("❌ Falha na execução do Walk-Forward Optimization")

if __name__ == "__main__":
    main()
