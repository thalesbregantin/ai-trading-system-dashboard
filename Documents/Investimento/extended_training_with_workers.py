#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExtendedWorkerTraining:
    """Sistema de treinamento estendido com workers otimizados"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.data_dir = Path("data")
        self.models_dir = Path("models")
        self.logs_dir = Path("logs")
        
        # Criar diretórios
        for dir_path in [self.results_dir, self.data_dir, self.models_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Configuração otimizada baseada na análise
        self.optimized_params = {
            'learning_rate': 0.0005,  # Reduzido para estabilidade
            'gamma': 0.98,            # Aumentado para foco no longo prazo
            'epsilon_start': 1.0,
            'epsilon_min': 0.05,      # Reduzido para menos exploração
            'epsilon_decay': 0.9995,  # Decaimento mais lento
            'batch_size': 64,         # Aumentado para melhor estabilidade
            'memory_size': 20000,     # Aumentado para mais experiências
            'episodes_per_pair': 50,  # Aumentado significativamente
            'lookback_window': 60     # Janela maior para análise
        }
        
        # Pares de trading expandidos
        self.trading_pairs = [
            'BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'XRP-USD',
            'ADA-USD', 'DOGE-USD', 'TRX-USD', 'LINK-USD', 'AVAX-USD',
            'MATIC-USD', 'DOT-USD', 'LTC-USD', 'ATOM-USD', 'UNI-USD',
            'NEAR-USD', 'FTM-USD', 'ALGO-USD', 'VET-USD', 'ICP-USD'
        ]
        
        self.total_workers = 4
        self.worker_results = {}
        self.global_metrics = []
        
    def prepare_training_data(self):
        """Prepara dados de treinamento para todos os pares"""
        logger.info("📊 Preparando dados de treinamento estendido...")
        
        results = []
        for symbol in self.trading_pairs:
            try:
                logger.info(f"Baixando {symbol}...")
                ticker = yf.Ticker(symbol)
                # Dados de 1 ano com intervalo de 1 hora
                data = ticker.history(period='1y', interval='1h')
                
                if not data.empty and len(data) > 100:
                    # Salvar dados
                    data_file = self.data_dir / f"{symbol.replace('-', '_')}_extended.csv"
                    data.to_csv(data_file)
                    
                    result = {
                        'symbol': symbol,
                        'data_points': len(data),
                        'last_price': data['Close'].iloc[-1],
                        'file': str(data_file),
                        'status': 'success'
                    }
                    logger.info(f"✅ {symbol}: {len(data)} pontos, ${data['Close'].iloc[-1]:.2f}")
                else:
                    result = {
                        'symbol': symbol,
                        'status': 'insufficient_data'
                    }
                    logger.warning(f"⚠️ {symbol}: Dados insuficientes")
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"❌ Erro ao baixar {symbol}: {e}")
                results.append({
                    'symbol': symbol,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def create_worker_configs(self):
        """Cria configurações para workers"""
        logger.info("⚙️ Criando configurações de workers...")
        
        # Dividir pares entre workers
        pairs_per_worker = len(self.trading_pairs) // self.total_workers
        remainder = len(self.trading_pairs) % self.total_workers
        
        start_idx = 0
        for worker_id in range(1, self.total_workers + 1):
            # Calcular quantos pares este worker vai treinar
            if worker_id <= remainder:
                num_pairs = pairs_per_worker + 1
            else:
                num_pairs = pairs_per_worker
            
            end_idx = start_idx + num_pairs
            worker_pairs = self.trading_pairs[start_idx:end_idx]
            
            # Criar configuração otimizada para o worker
            worker_config = {
                'worker_id': worker_id,
                'trading_pairs': worker_pairs,
                'episodes_per_pair': self.optimized_params['episodes_per_pair'],
                'training_params': self.optimized_params.copy(),
                'status': 'ready',
                'created_at': datetime.now().isoformat()
            }
            
            config_file = self.results_dir / f"worker_{worker_id}_extended_config.json"
            with open(config_file, 'w') as f:
                json.dump(worker_config, f, indent=2)
            
            logger.info(f"✅ Worker {worker_id}: {len(worker_pairs)} pares configurados")
            start_idx = end_idx
    
    def train_worker(self, worker_id):
        """Executa treinamento para um worker específico"""
        logger.info(f"🎓 Iniciando treinamento do Worker {worker_id}...")
        
        config_file = self.results_dir / f"worker_{worker_id}_extended_config.json"
        if not config_file.exists():
            logger.error(f"❌ Configuração não encontrada para Worker {worker_id}")
            return None
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        worker_results = {
            'worker_id': worker_id,
            'pairs_trained': [],
            'total_profit': 0,
            'total_trades': 0,
            'win_rate': 0,
            'start_time': datetime.now().isoformat(),
            'status': 'training'
        }
        
        # Atualizar status
        status_file = self.results_dir / f"worker_{worker_id}_extended_status.json"
        with open(status_file, 'w') as f:
            json.dump(worker_results, f, indent=2)
        
        total_pairs = len(config['trading_pairs'])
        for idx, symbol in enumerate(config['trading_pairs'], 1):
            try:
                logger.info(f"Worker {worker_id} ({idx}/{total_pairs}): Treinando {symbol}...")
                
                # Simular treinamento otimizado
                pair_result = self.simulate_optimized_training(symbol, config['training_params'])
                
                worker_results['pairs_trained'].append(pair_result)
                worker_results['total_profit'] += pair_result['profit']
                worker_results['total_trades'] += pair_result['trades']
                
                # Atualizar status
                worker_results['status'] = f'training ({idx}/{total_pairs})'
                with open(status_file, 'w') as f:
                    json.dump(worker_results, f, indent=2)
                
                logger.info(f"✅ Worker {worker_id} - {symbol}: Profit=${pair_result['profit']:.2f}, Win Rate={pair_result['win_rate']:.1f}%")
                
            except Exception as e:
                logger.error(f"❌ Erro no Worker {worker_id} - {symbol}: {e}")
                worker_results['pairs_trained'].append({
                    'symbol': symbol,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Calcular métricas finais
        successful_trades = [r for r in worker_results['pairs_trained'] if r.get('status') != 'error']
        if successful_trades:
            total_wins = sum(r.get('wins', 0) for r in successful_trades)
            total_trades = sum(r.get('trades', 0) for r in successful_trades)
            worker_results['win_rate'] = (total_wins / total_trades * 100) if total_trades > 0 else 0
        
        worker_results['status'] = 'completed'
        worker_results['end_time'] = datetime.now().isoformat()
        
        # Salvar resultados finais
        with open(status_file, 'w') as f:
            json.dump(worker_results, f, indent=2)
        
        logger.info(f"🎉 Worker {worker_id} concluído! Profit=${worker_results['total_profit']:.2f}, Win Rate={worker_results['win_rate']:.1f}%")
        return worker_results
    
    def simulate_optimized_training(self, symbol, params):
        """Simula treinamento otimizado para um par"""
        # Carregar dados
        data_file = self.data_dir / f"{symbol.replace('-', '_')}_extended.csv"
        if not data_file.exists():
            return {'symbol': symbol, 'status': 'no_data'}
        
        data = pd.read_csv(data_file, index_col=0, parse_dates=True)
        
        # Simular treinamento com parâmetros otimizados
        episodes = params['episodes_per_pair']
        total_profit = 0
        total_trades = 0
        total_wins = 0
        
        for episode in range(episodes):
            # Simular trading com parâmetros otimizados
            initial_balance = 1000
            current_balance = initial_balance
            trades_this_episode = 0
            wins_this_episode = 0
            
            # Simular trades baseado nos dados históricos
            for i in range(100, len(data) - 1):
                # Análise técnica simplificada
                close_prices = data['Close'].iloc[i-params['lookback_window']:i+1]
                rsi = self.calculate_rsi(close_prices)
                
                # Decisão baseada em RSI e tendência
                if rsi < 30:  # Sobrevendido
                    if np.random.random() > params['epsilon_min']:
                        # Compra
                        trade_amount = current_balance * 0.1
                        price_change = (data['Close'].iloc[i+1] - data['Close'].iloc[i]) / data['Close'].iloc[i]
                        profit = trade_amount * price_change
                        current_balance += profit
                        trades_this_episode += 1
                        if profit > 0:
                            wins_this_episode += 1
                
                elif rsi > 70:  # Sobrecomprado
                    if np.random.random() > params['epsilon_min']:
                        # Venda
                        trade_amount = current_balance * 0.1
                        price_change = (data['Close'].iloc[i] - data['Close'].iloc[i+1]) / data['Close'].iloc[i]
                        profit = trade_amount * price_change
                        current_balance += profit
                        trades_this_episode += 1
                        if profit > 0:
                            wins_this_episode += 1
            
            episode_profit = current_balance - initial_balance
            total_profit += episode_profit
            total_trades += trades_this_episode
            total_wins += wins_this_episode
        
        return {
            'symbol': symbol,
            'profit': total_profit,
            'trades': total_trades,
            'wins': total_wins,
            'win_rate': (total_wins / total_trades * 100) if total_trades > 0 else 0,
            'episodes': episodes,
            'status': 'success'
        }
    
    def calculate_rsi(self, prices, period=14):
        """Calcula RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else 50
    
    def run_extended_training(self):
        """Executa treinamento estendido com workers"""
        logger.info("🚀 INICIANDO TREINAMENTO ESTENDIDO COM WORKERS")
        logger.info("=" * 60)
        
        # Preparar dados
        data_results = self.prepare_training_data()
        successful_downloads = len([r for r in data_results if r['status'] == 'success'])
        logger.info(f"📊 Downloads bem-sucedidos: {successful_downloads}/{len(self.trading_pairs)}")
        
        if successful_downloads < len(self.trading_pairs) * 0.8:
            logger.warning("⚠️ Muitos downloads falharam. Continuando com os dados disponíveis...")
        
        # Criar configurações de workers
        self.create_worker_configs()
        
        # Executar workers em paralelo
        logger.info("🎓 Iniciando workers em paralelo...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.total_workers) as executor:
            # Submeter jobs para workers
            future_to_worker = {
                executor.submit(self.train_worker, worker_id): worker_id 
                for worker_id in range(1, self.total_workers + 1)
            }
            
            # Coletar resultados
            for future in as_completed(future_to_worker):
                worker_id = future_to_worker[future]
                try:
                    result = future.result()
                    if result:
                        self.worker_results[worker_id] = result
                except Exception as e:
                    logger.error(f"❌ Worker {worker_id} falhou: {e}")
        
        # Análise final
        self.analyze_final_results()
        
        training_time = time.time() - start_time
        logger.info(f"🎉 Treinamento estendido concluído em {training_time/60:.1f} minutos!")
    
    def analyze_final_results(self):
        """Analisa resultados finais do treinamento"""
        logger.info("📊 Analisando resultados finais...")
        
        if not self.worker_results:
            logger.warning("⚠️ Nenhum resultado de worker encontrado")
            return
        
        # Agregar métricas
        total_profit = sum(w['total_profit'] for w in self.worker_results.values())
        total_trades = sum(w['total_trades'] for w in self.worker_results.values())
        total_wins = sum(sum(p.get('wins', 0) for p in w['pairs_trained']) for w in self.worker_results.values())
        
        overall_win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
        
        # Análise por worker
        worker_analysis = []
        for worker_id, result in self.worker_results.items():
            worker_analysis.append({
                'worker_id': worker_id,
                'total_profit': result['total_profit'],
                'total_trades': result['total_trades'],
                'win_rate': result['win_rate'],
                'pairs_trained': len(result['pairs_trained'])
            })
        
        # Criar relatório final
        final_report = {
            'training_date': datetime.now().isoformat(),
            'total_workers': len(self.worker_results),
            'total_pairs_trained': sum(len(w['pairs_trained']) for w in self.worker_results.values()),
            'overall_metrics': {
                'total_profit': total_profit,
                'total_trades': total_trades,
                'total_wins': total_wins,
                'overall_win_rate': overall_win_rate,
                'average_profit_per_trade': total_profit / total_trades if total_trades > 0 else 0
            },
            'worker_analysis': worker_analysis,
            'optimization_params': self.optimized_params,
            'recommendations': self.generate_recommendations(total_profit, overall_win_rate)
        }
        
        # Salvar relatório
        report_file = self.results_dir / "extended_training_report.json"
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=2)
        
        # Log resumo
        logger.info("📋 RESUMO FINAL:")
        logger.info(f"   - Workers ativos: {len(self.worker_results)}")
        logger.info(f"   - Pares treinados: {final_report['total_pairs_trained']}")
        logger.info(f"   - Lucro total: ${total_profit:.2f}")
        logger.info(f"   - Total de trades: {total_trades}")
        logger.info(f"   - Win rate geral: {overall_win_rate:.1f}%")
        logger.info(f"   - Lucro médio por trade: ${final_report['overall_metrics']['average_profit_per_trade']:.2f}")
        
        # Recomendações
        logger.info("🎯 RECOMENDAÇÕES:")
        for rec in final_report['recommendations']:
            logger.info(f"   - {rec}")
    
    def generate_recommendations(self, total_profit, win_rate):
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        if total_profit > 1000:
            recommendations.append("✅ Sistema muito lucrativo - Considere aumentar capital")
        elif total_profit > 500:
            recommendations.append("✅ Sistema lucrativo - Continue monitorando")
        elif total_profit > 0:
            recommendations.append("⚠️ Sistema marginalmente lucrativo - Otimize parâmetros")
        else:
            recommendations.append("❌ Sistema não lucrativo - Revisar estratégia")
        
        if win_rate > 70:
            recommendations.append("✅ Win rate excelente - Sistema muito confiável")
        elif win_rate > 60:
            recommendations.append("✅ Win rate bom - Sistema confiável")
        elif win_rate > 50:
            recommendations.append("⚠️ Win rate aceitável - Melhorar precisão")
        else:
            recommendations.append("❌ Win rate baixo - Revisar estratégia")
        
        if total_profit > 0 and win_rate > 60:
            recommendations.append("🚀 Sistema pronto para trading real")
        else:
            recommendations.append("🔧 Sistema precisa de mais otimização")
        
        return recommendations

if __name__ == "__main__":
    # Executar treinamento estendido
    trainer = ExtendedWorkerTraining()
    trainer.run_extended_training()
