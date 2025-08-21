#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Walk-Forward Optimization System
Combate overfitting através de validação out-of-sample sequencial
"""

import logging
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
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
    Sistema de Walk-Forward Optimization para combater overfitting
    """
    
    def __init__(self):
        self.data_dir = Path("data")
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Parâmetros Walk-Forward
        self.training_window_pct = 0.7  # 70% para treino
        self.testing_window_pct = 0.2   # 20% para teste
        self.step_size_pct = 0.1        # 10% para avançar janela
        
        # Pares de trading (usar apenas 3 para velocidade)
        self.trading_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
        
        logger.info("🚀 WALK-FORWARD OPTIMIZER INICIADO")
        logger.info(f"📊 Pares: {self.trading_pairs}")
        logger.info(f"🎯 Treino: {self.training_window_pct*100}%, Teste: {self.testing_window_pct*100}%, Step: {self.step_size_pct*100}%")
    
    def load_all_data_for_all_pairs(self):
        """Carrega todos os dados para todos os pares"""
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
        """Cria janelas de dados para Walk-Forward"""
        logger.info("🔄 Criando janelas de dados...")
        
        # Usar BTC/USDT como referência para tamanho
        reference_data = full_data['BTC/USDT']
        total_points = len(reference_data)
        
        training_size = int(total_points * self.training_window_pct)
        testing_size = int(total_points * self.testing_window_pct)
        step_size = int(total_points * self.step_size_pct)
        
        windows = []
        start_index = 0
        
        while start_index + training_size + testing_size <= total_points:
            end_training = start_index + training_size
            end_testing = end_training + testing_size
            
            # Criar janelas para todos os pares
            training_data = {}
            testing_data = {}
            
            for symbol, data in full_data.items():
                training_data[symbol] = data.iloc[start_index:end_training].copy()
                testing_data[symbol] = data.iloc[end_training:end_testing].copy()
            
            window_info = {
                'window_id': len(windows) + 1,
                'start_index': start_index,
                'end_training': end_training,
                'end_testing': end_testing,
                'training_dates': {
                    'start': training_data['BTC/USDT'].index[0],
                    'end': training_data['BTC/USDT'].index[-1]
                },
                'testing_dates': {
                    'start': testing_data['BTC/USDT'].index[0],
                    'end': testing_data['BTC/USDT'].index[-1]
                },
                'training_data': training_data,
                'testing_data': testing_data
            }
            
            windows.append(window_info)
            start_index += step_size
        
        logger.info(f"✅ Criadas {len(windows)} janelas de Walk-Forward")
        return windows
    
    def run_optimization_on_window(self, training_data, window_id):
        """Executa otimização genética em uma janela específica"""
        logger.info(f"🧬 Otimizando janela {window_id}...")
        
        # Criar otimizador genético temporário
        optimizer = GeneticTradingOptimizer()
        
        # Executar otimização com dados da janela
        start_time = time.time()
        best_params = optimizer.run_optimization(training_data=training_data)
        optimization_time = time.time() - start_time
        
        logger.info(f"✅ Janela {window_id} otimizada em {optimization_time:.1f}s")
        
        return best_params, optimization_time
    
    def run_backtest_with_params(self, params, testing_data, window_id):
        """Executa backtest com parâmetros otimizados nos dados de teste"""
        logger.info(f"📊 Testando janela {window_id} (Out-of-Sample)...")
        
        total_profit = 0
        total_trades = 0
        total_wins = 0
        all_returns = []
        
        # Testar em todos os pares
        for symbol, data in testing_data.items():
            result = self.simulate_trading_with_params(symbol, data, params)
            if result and result['trades'] > 0:
                total_profit += result['profit']
                total_trades += result['trades']
                total_wins += result['wins']
                all_returns.extend(result.get('returns', []))
        
        # Calcular métricas
        win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
        avg_profit = total_profit / total_trades if total_trades > 0 else 0
        
        # Sharpe Ratio
        sharpe_ratio = 0
        if all_returns:
            returns_std = np.std(all_returns)
            if returns_std > 0:
                sharpe_ratio = np.mean(all_returns) / returns_std
        
        test_result = {
            'window_id': window_id,
            'total_profit': total_profit,
            'total_trades': total_trades,
            'total_wins': total_wins,
            'win_rate': win_rate,
            'avg_profit_per_trade': avg_profit,
            'sharpe_ratio': sharpe_ratio,
            'returns': all_returns,
            'params_used': params
        }
        
        logger.info(f"✅ Janela {window_id}: Profit=${total_profit:.2f}, Win Rate={win_rate:.1f}%, Sharpe={sharpe_ratio:.3f}")
        
        return test_result
    
    def simulate_trading_with_params(self, symbol, data, params):
        """Simula trading com parâmetros específicos"""
        try:
            # Calcular indicadores
            data = data.copy()
            data['rsi'] = self.calculate_rsi(data['Close'], params['rsi_period'])
            data['sma_short'] = data['Close'].rolling(window=params['sma_short']).mean()
            data['sma_long'] = data['Close'].rolling(window=params['sma_long']).mean()
            
            # Remover NaN
            data = data.dropna()
            
            if len(data) < 100:  # Mínimo de dados
                return None
            
            # Parâmetros de trading
            initial_balance = 1000
            current_balance = initial_balance
            position = None
            trades = 0
            wins = 0
            returns_list = []
            
            # Simular trading
            for i in range(len(data)):
                current_price = data['Close'].iloc[i]
                current_time = data.index[i]
                
                # Verificar condições de entrada
                rsi = data['rsi'].iloc[i]
                sma_short = data['sma_short'].iloc[i]
                sma_long = data['sma_long'].iloc[i]
                
                trend_bullish = sma_short > sma_long
                trend_bearish = sma_short < sma_long
                
                # Estratégia baseada nos parâmetros otimizados
                if position is None:  # Sem posição aberta
                    # Long: RSI baixo + tendência de alta
                    if rsi < params['rsi_oversold'] and trend_bullish:
                        trade_amount = current_balance * params['trade_amount_pct']
                        position = {
                            'type': 'long',
                            'entry_price': current_price,
                            'entry_time': current_time,
                            'amount': trade_amount,
                            'stop_loss': current_price * (1 - params['stop_loss_pct']),
                            'take_profit': current_price * (1 + params['take_profit_pct'])
                        }
                        current_balance -= trade_amount
                
                # Verificar saída da posição
                elif position is not None:
                    exit_trade = False
                    profit = 0
                    
                    # Stop Loss ou Take Profit
                    if position['type'] == 'long':
                        if current_price <= position['stop_loss'] or current_price >= position['take_profit']:
                            exit_trade = True
                            profit = position['amount'] * ((current_price - position['entry_price']) / position['entry_price'])
                    
                    # Tempo máximo de hold
                    hold_time = current_time - position['entry_time']
                    if hold_time.total_seconds() > params['max_hold_time'] * 3600:  # Converter para segundos
                        exit_trade = True
                        profit = position['amount'] * ((current_price - position['entry_price']) / position['entry_price'])
                    
                    if exit_trade:
                        # Aplicar taxa de transação
                        profit -= position['amount'] * params['transaction_fee']
                        
                        current_balance += position['amount'] + profit
                        trades += 1
                        returns_list.append(profit)
                        
                        if profit > 0:
                            wins += 1
                        
                        position = None
            
            # Fechar posição final se ainda estiver aberta
            if position is not None:
                current_price = data['Close'].iloc[-1]
                profit = position['amount'] * ((current_price - position['entry_price']) / position['entry_price'])
                profit -= position['amount'] * params['transaction_fee']
                
                current_balance += position['amount'] + profit
                trades += 1
                returns_list.append(profit)
                
                if profit > 0:
                    wins += 1
            
            return {
                'profit': current_balance - initial_balance,
                'trades': trades,
                'wins': wins,
                'returns': returns_list
            }
            
        except Exception as e:
            logger.error(f"Erro na simulação de {symbol}: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Calcula RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def analyze_walk_forward_results(self, out_of_sample_results):
        """Analisa resultados do Walk-Forward"""
        logger.info("📊 ANALISANDO RESULTADOS WALK-FORWARD")
        logger.info("=" * 60)
        
        if not out_of_sample_results:
            logger.error("❌ Nenhum resultado para analisar")
            return
        
        # Métricas agregadas
        total_profit = sum(r['total_profit'] for r in out_of_sample_results)
        total_trades = sum(r['total_trades'] for r in out_of_sample_results)
        total_wins = sum(r['total_wins'] for r in out_of_sample_results)
        
        # Win rate geral
        overall_win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
        
        # Lucro médio por trade
        avg_profit_per_trade = total_profit / total_trades if total_trades > 0 else 0
        
        # Coletar todos os retornos para Sharpe Ratio
        all_returns = []
        for result in out_of_sample_results:
            all_returns.extend(result['returns'])
        
        # Sharpe Ratio
        sharpe_ratio = 0
        if all_returns:
            returns_std = np.std(all_returns)
            if returns_std > 0:
                sharpe_ratio = np.mean(all_returns) / returns_std
        
        # Consistência entre janelas
        profitable_windows = sum(1 for r in out_of_sample_results if r['total_profit'] > 0)
        consistency_rate = (profitable_windows / len(out_of_sample_results)) * 100
        
        # Análise por janela
        window_analysis = []
        for result in out_of_sample_results:
            window_analysis.append({
                'window_id': result['window_id'],
                'profit': result['total_profit'],
                'trades': result['total_trades'],
                'win_rate': result['win_rate'],
                'sharpe_ratio': result['sharpe_ratio'],
                'profitable': result['total_profit'] > 0
            })
        
        # Resultados finais
        final_results = {
            'walk_forward_analysis': {
                'total_windows': len(out_of_sample_results),
                'profitable_windows': profitable_windows,
                'consistency_rate': consistency_rate,
                'total_profit': total_profit,
                'total_trades': total_trades,
                'total_wins': total_wins,
                'overall_win_rate': overall_win_rate,
                'avg_profit_per_trade': avg_profit_per_trade,
                'sharpe_ratio': sharpe_ratio,
                'all_returns': all_returns
            },
            'window_analysis': window_analysis,
            'detailed_results': out_of_sample_results
        }
        
        # Salvar resultados
        results_file = self.results_dir / "walk_forward_results.json"
        with open(results_file, 'w') as f:
            json.dump(final_results, f, indent=2, default=str)
        
        # Log dos resultados
        logger.info("🏆 RESULTADOS WALK-FORWARD:")
        logger.info(f"   📊 Janelas totais: {len(out_of_sample_results)}")
        logger.info(f"   ✅ Janelas lucrativas: {profitable_windows} ({consistency_rate:.1f}%)")
        logger.info(f"   💰 Lucro total: ${total_profit:.2f}")
        logger.info(f"   📈 Total de trades: {total_trades}")
        logger.info(f"   🎯 Win rate geral: {overall_win_rate:.1f}%")
        logger.info(f"   📊 Lucro médio por trade: ${avg_profit_per_trade:.2f}")
        logger.info(f"   📈 Sharpe Ratio: {sharpe_ratio:.3f}")
        
        # Recomendações
        logger.info("\n🎯 RECOMENDAÇÕES:")
        if consistency_rate >= 70:
            logger.info("   ✅ Estratégia CONSISTENTE - Alta confiança")
        elif consistency_rate >= 50:
            logger.info("   ⚠️ Estratégia MODERADA - Revisar parâmetros")
        else:
            logger.info("   ❌ Estratégia INCONSISTENTE - Revisar abordagem")
        
        if sharpe_ratio > 1.0:
            logger.info("   ✅ Sharpe Ratio EXCELENTE - Baixo risco")
        elif sharpe_ratio > 0.5:
            logger.info("   ⚠️ Sharpe Ratio MODERADO - Risco aceitável")
        else:
            logger.info("   ❌ Sharpe Ratio BAIXO - Alto risco")
        
        logger.info(f"\n💾 Resultados salvos em: {results_file}")
        
        return final_results
    
    def run_walk_forward_optimization(self):
        """Executa Walk-Forward Optimization completa"""
        logger.info("🚀 INICIANDO WALK-FORWARD OPTIMIZATION")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # 1. Carregar todos os dados
        full_data = self.load_all_data_for_all_pairs()
        if not full_data:
            logger.error("❌ Nenhum dado encontrado")
            return None
        
        # 2. Criar janelas de dados
        windows = self.create_data_windows(full_data)
        if not windows:
            logger.error("❌ Não foi possível criar janelas")
            return None
        
        # 3. Executar Walk-Forward
        out_of_sample_results = []
        
        for window in windows:
            logger.info(f"\n🔄 PROCESSANDO JANELA {window['window_id']}/{len(windows)}")
            logger.info(f"   📅 Treino: {window['training_dates']['start']} a {window['training_dates']['end']}")
            logger.info(f"   📅 Teste: {window['testing_dates']['start']} a {window['testing_dates']['end']}")
            
            # Otimizar na janela de treino
            best_params, opt_time = self.run_optimization_on_window(
                window['training_data'], 
                window['window_id']
            )
            
            # Testar na janela de teste (Out-of-Sample)
            test_result = self.run_backtest_with_params(
                best_params, 
                window['testing_data'], 
                window['window_id']
            )
            
            out_of_sample_results.append(test_result)
        
        # 4. Analisar resultados
        total_time = time.time() - start_time
        logger.info(f"\n⏱️ Walk-Forward concluído em {total_time/60:.1f} minutos")
        
        final_results = self.analyze_walk_forward_results(out_of_sample_results)
        
        return final_results

if __name__ == "__main__":
    optimizer = WalkForwardOptimizer()
    results = optimizer.run_walk_forward_optimization()
    
    if results:
        print("\n🎉 WALK-FORWARD OPTIMIZATION CONCLUÍDA COM SUCESSO!")
        print("📊 Verifique os resultados em: results/walk_forward_results.json")
    else:
        print("\n❌ Erro na Walk-Forward Optimization")
