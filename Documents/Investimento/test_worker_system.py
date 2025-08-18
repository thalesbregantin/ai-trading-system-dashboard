#!/usr/bin/env python3
"""
Teste Simplificado do Sistema de Workers
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestWorkerSystem:
    """Sistema de teste para workers"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.data_dir = Path("data")
        self.models_dir = Path("models")
        
        # Criar diretórios
        self.results_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
        # Pares para teste
        self.test_pairs = ['BTC-USD', 'ETH-USD', 'BNB-USD']
        
    def test_data_download(self):
        """Testa download de dados"""
        logger.info("📊 Testando download de dados...")
        
        results = []
        for symbol in self.test_pairs:
            try:
                logger.info(f"Baixando {symbol}...")
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='30d', interval='1h')
                
                if not data.empty:
                    # Salvar dados
                    data_file = self.data_dir / f"{symbol.replace('-', '_')}_test.csv"
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
                        'status': 'no_data'
                    }
                    logger.warning(f"⚠️ {symbol}: Nenhum dado")
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"❌ Erro ao baixar {symbol}: {e}")
                results.append({
                    'symbol': symbol,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def test_worker_config(self):
        """Testa criação de configurações de workers"""
        logger.info("⚙️ Testando configuração de workers...")
        
        # Simular 2 workers
        workers_config = {
            'worker_1': {
                'worker_id': 1,
                'trading_pairs': ['BTC-USD', 'ETH-USD'],
                'episodes_per_pair': 5,
                'status': 'ready'
            },
            'worker_2': {
                'worker_id': 2,
                'trading_pairs': ['BNB-USD'],
                'episodes_per_pair': 5,
                'status': 'ready'
            }
        }
        
        # Salvar configurações
        for worker_name, config in workers_config.items():
            config_file = self.results_dir / f"{worker_name}_config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"✅ {worker_name}: {len(config['trading_pairs'])} pares configurados")
        
        return workers_config
    
    def test_simple_training(self):
        """Testa treinamento simplificado"""
        logger.info("🎓 Testando treinamento simplificado...")
        
        training_results = []
        
        for symbol in self.test_pairs:
            try:
                logger.info(f"Treinando {symbol}...")
                
                # Simular treinamento
                time.sleep(1)  # Simular processamento
                
                # Resultado simulado
                result = {
                    'symbol': symbol,
                    'episodes': 5,
                    'best_profit': np.random.uniform(-100, 200),
                    'avg_profit': np.random.uniform(-50, 150),
                    'total_trades': np.random.randint(10, 50),
                    'win_rate': np.random.uniform(0.4, 0.7),
                    'training_date': datetime.now().isoformat(),
                    'status': 'completed'
                }
                
                training_results.append(result)
                logger.info(f"✅ {symbol}: Profit=${result['best_profit']:.2f}, Win Rate={result['win_rate']:.1%}")
                
            except Exception as e:
                logger.error(f"❌ Erro no treinamento de {symbol}: {e}")
                training_results.append({
                    'symbol': symbol,
                    'status': 'error',
                    'error': str(e)
                })
        
        return training_results
    
    def create_test_report(self, data_results, training_results):
        """Cria relatório de teste"""
        logger.info("📋 Criando relatório de teste...")
        
        report = {
            'test_date': datetime.now().isoformat(),
            'total_pairs': len(self.test_pairs),
            'data_results': data_results,
            'training_results': training_results,
            'summary': {
                'successful_downloads': len([r for r in data_results if r.get('status') == 'success']),
                'successful_trainings': len([r for r in training_results if r.get('status') == 'completed']),
                'avg_profit': np.mean([r.get('best_profit', 0) for r in training_results if r.get('status') == 'completed']),
                'avg_win_rate': np.mean([r.get('win_rate', 0) for r in training_results if r.get('status') == 'completed'])
            }
        }
        
        # Salvar relatório
        report_file = self.results_dir / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("✅ Relatório de teste criado")
        return report
    
    def run_test(self):
        """Executa teste completo"""
        logger.info("🚀 Iniciando teste do sistema de workers...")
        
        # Teste 1: Download de dados
        data_results = self.test_data_download()
        
        # Teste 2: Configuração de workers
        workers_config = self.test_worker_config()
        
        # Teste 3: Treinamento simplificado
        training_results = self.test_simple_training()
        
        # Teste 4: Relatório
        report = self.create_test_report(data_results, training_results)
        
        # Resumo final
        logger.info("🎉 Teste concluído!")
        logger.info(f"📊 Resumo:")
        logger.info(f"   - Downloads bem-sucedidos: {report['summary']['successful_downloads']}/{len(self.test_pairs)}")
        logger.info(f"   - Treinamentos bem-sucedidos: {report['summary']['successful_trainings']}/{len(self.test_pairs)}")
        logger.info(f"   - Lucro médio: ${report['summary']['avg_profit']:.2f}")
        logger.info(f"   - Win rate médio: {report['summary']['avg_win_rate']:.1%}")
        
        return report

if __name__ == "__main__":
    test_system = TestWorkerSystem()
    test_system.run_test()
