#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Walk-Forward Optimization System v2.0
Combate overfitting através de validação out-of-sample sequencial
e análise de estabilidade de parâmetros.
"""

import logging
import json
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from genetic_optimizer import GeneticTradingOptimizer

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('walk_forward_optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WalkForwardOptimizer:
    """
    Sistema de Walk-Forward Optimization para combater overfitting.
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
        
        # Instanciar o motor de simulação e otimização
        self.optimizer_engine = GeneticTradingOptimizer()
        
        logger.info("🚀 WALK-FORWARD OPTIMIZER v2.0 INICIADO")
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

    def run_backtest_on_window(self, params, testing_data):
        """Executa um backtest único com parâmetros fixos em um conjunto de dados."""
        total_profit = 0
        total_trades = 0
        total_wins = 0
        all_returns = []
        
        for symbol, data in testing_data.items():
            # Usar o motor de simulação do otimizador
            result = self.optimizer_engine.simulate_trading(symbol, params)
            if result and result['trades'] > 0:
                total_profit += result['profit']
                total_trades += result['trades']
                total_wins += result['wins']
                all_returns.extend(result.get('returns', []))
        
        win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_profit': total_profit,
            'total_trades': total_trades,
            'total_wins': total_wins,
            'win_rate': win_rate,
            'returns': all_returns,
            'params_used': params
        }

    def analyze_final_results(self, out_of_sample_results):
        """Analisa os resultados agregados de todos os testes Out-of-Sample."""
        logger.info("📊 ANALISANDO RESULTADOS FINAIS DO WALK-FORWARD")
        
        if not out_of_sample_results:
            logger.error("❌ Nenhum resultado out-of-sample para analisar.")
            return None

        # --- Análise de Performance Agregada ---
        all_returns = [r for res in out_of_sample_results for r in res['returns']]
        total_profit = sum(all_returns)
        total_trades = sum(res['total_trades'] for res in out_of_sample_results)
        total_wins = sum(res['total_wins'] for res in out_of_sample_results)
        
        equity_curve = pd.Series([1000] + np.cumsum(all_returns).tolist())
        returns_series = equity_curve.pct_change().dropna()
        
        # Calcular métricas de risco
        sharpe_ratio = 0
        if len(returns_series) > 0:
            returns_std = returns_series.std()
            if returns_std > 0:
                sharpe_ratio = returns_series.mean() / returns_std
        
        # Max Drawdown
        max_drawdown = 0
        if len(equity_curve) > 1:
            peak = equity_curve.expanding().max()
            drawdown = (equity_curve - peak) / peak
            max_drawdown = drawdown.min()
        
        # Profit Factor
        profit_factor = float('inf')
        if all_returns:
            gross_profit = sum(r for r in all_returns if r > 0)
            gross_loss = abs(sum(r for r in all_returns if r < 0))
            if gross_loss > 0:
                profit_factor = gross_profit / gross_loss

        # --- Análise de Estabilidade de Parâmetros ---
        params_df = pd.DataFrame([res['params_used'] for res in out_of_sample_results])
        params_stability = {
            'mean': params_df.mean().to_dict(),
            'std_dev': params_df.std().to_dict(),
            'coefficient_of_variation': (params_df.std() / params_df.mean()).to_dict()
        }

        # Calcular estabilidade geral
        stability_score = 0
        if len(params_df) > 1:
            # Média dos coeficientes de variação (menor = mais estável)
            cv_values = [v for v in params_stability['coefficient_of_variation'].values() if not np.isnan(v)]
            if cv_values:
                avg_cv = np.mean(cv_values)
                stability_score = max(0, 100 - (avg_cv * 100))  # Score de 0-100

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
        
        report_file = self.results_dir / "walk_forward_results_v2.json"
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=4, default=str)
            
        # Log dos resultados
        logger.info("🏆 RESULTADOS WALK-FORWARD v2.0:")
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
        logger.info("🚀 INICIANDO WALK-FORWARD OPTIMIZATION v2.0")
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
            
        # 3. Executar Walk-Forward
        out_of_sample_results = []
        
        for window in windows:
            logger.info(f"\n🔄 PROCESSANDO JANELA {window['id']}/{len(windows)}")
            logger.info(f"   📅 Treino: {window['training_dates'][0]} a {window['training_dates'][1]}")
            logger.info(f"   📅 Teste: {window['testing_dates'][0]} a {window['testing_dates'][1]}")
            
            # Otimizar na janela de treino (In-Sample)
            logger.info(f"   🧬 Otimizando janela {window['id']}...")
            best_params = self.optimizer_engine.run_optimization(training_data=window['training_data'])
            
            # Testar na janela de teste (Out-of-Sample)
            logger.info(f"   📊 Testando janela {window['id']} (Out-of-Sample)...")
            test_result = self.run_backtest_on_window(best_params, window['testing_data'])
            test_result['window_id'] = window['id']
            out_of_sample_results.append(test_result)
            
            logger.info(f"   ✅ Janela {window['id']}: Profit=${test_result['total_profit']:.2f}, Win Rate={test_result['win_rate']:.1f}%")
        
        # 4. Analisar resultados
        total_time = time.time() - start_time
        logger.info(f"\n⏱️ Walk-Forward concluído em {total_time/60:.1f} minutos")
        
        final_results = self.analyze_final_results(out_of_sample_results)
        
        return final_results

if __name__ == "__main__":
    wf_optimizer = WalkForwardOptimizer()
    results = wf_optimizer.run()
    
    if results:
        print("\n🎉 WALK-FORWARD OPTIMIZATION v2.0 CONCLUÍDA COM SUCESSO!")
        print("📊 Verifique os resultados em: results/walk_forward_results_v2.json")
    else:
        print("\n❌ Erro na Walk-Forward Optimization v2.0")
