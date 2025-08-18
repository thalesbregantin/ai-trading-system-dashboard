#!/usr/bin/env python3
"""
Worker Manager - Coordena workers para treinamento paralelo
"""

import os
import time
import json
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkerManager:
    """Gerencia workers para treinamento paralelo"""
    
    def __init__(self):
        self.total_workers = int(os.getenv('TOTAL_WORKERS', 4))
        self.results_dir = Path("results")
        self.data_dir = Path("data")
        self.models_dir = Path("models")
        
        # Criar diretórios
        self.results_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
        # Status dos workers
        self.worker_status = {}
        self.training_tasks = []
        
    def prepare_training_data(self):
        """Prepara dados de treinamento divididos entre workers"""
        logger.info("📊 Preparando dados de treinamento...")
        
        # Pares de trading para treinar
        trading_pairs = [
            'BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'XRP-USD',
            'ADA-USD', 'DOGE-USD', 'TRX-USD', 'LINK-USD', 'AVAX-USD',
            'MATIC-USD', 'DOT-USD', 'LTC-USD', 'ATOM-USD', 'UNI-USD'
        ]
        
        # Dividir pares entre workers
        pairs_per_worker = len(trading_pairs) // self.total_workers
        remainder = len(trading_pairs) % self.total_workers
        
        start_idx = 0
        for worker_id in range(1, self.total_workers + 1):
            # Calcular quantos pares este worker vai treinar
            if worker_id <= remainder:
                num_pairs = pairs_per_worker + 1
            else:
                num_pairs = pairs_per_worker
            
            end_idx = start_idx + num_pairs
            worker_pairs = trading_pairs[start_idx:end_idx]
            
            # Criar arquivo de configuração para o worker
            worker_config = {
                'worker_id': worker_id,
                'trading_pairs': worker_pairs,
                'episodes_per_pair': 10,  # Episódios por par
                'training_params': {
                    'learning_rate': 0.001,
                    'gamma': 0.95,
                    'epsilon_start': 1.0,
                    'epsilon_min': 0.01,
                    'epsilon_decay': 0.997,
                    'batch_size': 32,
                    'memory_size': 10000
                }
            }
            
            config_file = self.results_dir / f"worker_{worker_id}_config.json"
            with open(config_file, 'w') as f:
                json.dump(worker_config, f, indent=2)
            
            logger.info(f"✅ Worker {worker_id}: {len(worker_pairs)} pares configurados")
            start_idx = end_idx
    
    def monitor_workers(self):
        """Monitora o progresso dos workers"""
        logger.info("👀 Iniciando monitoramento dos workers...")
        
        while True:
            active_workers = 0
            completed_workers = 0
            
            for worker_id in range(1, self.total_workers + 1):
                status_file = self.results_dir / f"worker_{worker_id}_status.json"
                
                if status_file.exists():
                    try:
                        with open(status_file, 'r') as f:
                            status = json.load(f)
                        
                        if status.get('status') == 'completed':
                            completed_workers += 1
                        elif status.get('status') == 'running':
                            active_workers += 1
                            
                        # Log progresso
                        progress = status.get('progress', 0)
                        current_pair = status.get('current_pair', 'N/A')
                        logger.info(f"Worker {worker_id}: {progress:.1f}% - {current_pair}")
                        
                    except Exception as e:
                        logger.error(f"Erro ao ler status do worker {worker_id}: {e}")
            
            # Verificar se todos completaram
            if completed_workers == self.total_workers:
                logger.info("🎉 Todos os workers completaram o treinamento!")
                self.aggregate_results()
                break
            
            logger.info(f"📊 Progresso: {completed_workers}/{self.total_workers} completos, {active_workers} ativos")
            time.sleep(30)  # Verificar a cada 30 segundos
    
    def aggregate_results(self):
        """Agrega resultados de todos os workers"""
        logger.info("🔄 Agregando resultados dos workers...")
        
        all_results = []
        best_models = []
        
        for worker_id in range(1, self.total_workers + 1):
            results_file = self.results_dir / f"worker_{worker_id}_results.json"
            model_file = self.models_dir / f"worker_{worker_id}_best_model.h5"
            
            if results_file.exists():
                with open(results_file, 'r') as f:
                    worker_results = json.load(f)
                    all_results.extend(worker_results)
            
            if model_file.exists():
                best_models.append(str(model_file))
        
        # Salvar resultados agregados
        aggregated_file = self.results_dir / "aggregated_results.json"
        with open(aggregated_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        # Criar relatório de treinamento
        self.create_training_report(all_results, best_models)
        
        logger.info(f"✅ Agregação concluída: {len(all_results)} resultados, {len(best_models)} modelos")
    
    def create_training_report(self, results, models):
        """Cria relatório de treinamento"""
        report = {
            'training_date': datetime.now().isoformat(),
            'total_workers': self.total_workers,
            'total_results': len(results),
            'best_models': models,
            'summary': {
                'total_episodes': sum(r.get('episodes', 0) for r in results),
                'total_trades': sum(r.get('trades', 0) for r in results),
                'avg_profit': np.mean([r.get('profit', 0) for r in results]),
                'best_profit': max([r.get('profit', 0) for r in results]),
                'worst_profit': min([r.get('profit', 0) for r in results])
            }
        }
        
        report_file = self.results_dir / "training_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("📋 Relatório de treinamento criado")
    
    def run(self):
        """Executa o worker manager"""
        logger.info("🚀 Iniciando Worker Manager...")
        logger.info(f"👥 Total de workers: {self.total_workers}")
        
        # Preparar dados
        self.prepare_training_data()
        
        # Aguardar workers iniciarem
        logger.info("⏳ Aguardando workers iniciarem...")
        time.sleep(10)
        
        # Monitorar progresso
        self.monitor_workers()
        
        logger.info("✅ Worker Manager concluído!")

if __name__ == "__main__":
    manager = WorkerManager()
    manager.run()
