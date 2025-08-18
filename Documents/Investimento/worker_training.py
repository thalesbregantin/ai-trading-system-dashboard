#!/usr/bin/env python3
"""
Worker de Treinamento - Executa treinamento em paralelo
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf

# Adicionar diretório do projeto ao path
sys.path.append(str(Path(__file__).parent / "ai_trading_system"))

from core.config import get_config
from core.ai_trader_dqn import AITrader

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Worker %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TrainingWorker:
    """Worker para treinamento paralelo"""
    
    def __init__(self):
        self.worker_id = int(os.getenv('WORKER_ID', 1))
        self.total_workers = int(os.getenv('TOTAL_WORKERS', 4))
        self.results_dir = Path("results")
        self.data_dir = Path("data")
        self.models_dir = Path("models")
        
        # Configuração do sistema
        self.config = get_config('test')
        
        # Status do worker
        self.status = {
            'worker_id': self.worker_id,
            'status': 'initializing',
            'progress': 0.0,
            'current_pair': 'N/A',
            'start_time': datetime.now().isoformat()
        }
        
        logger.info(f"🤖 Worker {self.worker_id} inicializado")
    
    def load_config(self):
        """Carrega configuração específica do worker"""
        config_file = self.results_dir / f"worker_{self.worker_id}_config.json"
        
        if not config_file.exists():
            logger.error(f"❌ Arquivo de configuração não encontrado: {config_file}")
            return False
        
        with open(config_file, 'r') as f:
            self.worker_config = json.load(f)
        
        logger.info(f"✅ Configuração carregada: {len(self.worker_config['trading_pairs'])} pares")
        return True
    
    def download_data(self, symbol):
        """Baixa dados históricos para um símbolo"""
        try:
            logger.info(f"📊 Baixando dados para {symbol}...")
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1y', interval='1h')
            
            if data.empty:
                logger.warning(f"⚠️ Nenhum dado encontrado para {symbol}")
                return None
            
            # Salvar dados
            data_file = self.data_dir / f"{symbol.replace('-', '_')}_data.csv"
            data.to_csv(data_file)
            
            logger.info(f"✅ Dados baixados: {len(data)} pontos para {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Erro ao baixar dados para {symbol}: {e}")
            return None
    
    def train_pair(self, symbol, episodes=10):
        """Treina modelo para um par específico"""
        try:
            logger.info(f"🎓 Treinando {symbol} (Worker {self.worker_id})...")
            
            # Baixar dados
            data = self.download_data(symbol)
            if data is None:
                return None
            
            # Criar AI Trader
            ai_trader = AITrader(self.config)
            
            # Configurar dados de treinamento
            training_data = data.copy()
            
            # Treinar modelo
            results = []
            best_profit = -float('inf')
            best_model = None
            
            for episode in range(episodes):
                logger.info(f"📈 Episódio {episode + 1}/{episodes} - {symbol}")
                
                # Treinar episódio
                episode_result = ai_trader.train_episode(training_data)
                
                if episode_result:
                    results.append(episode_result)
                    
                    # Verificar se é o melhor modelo
                    if episode_result.get('total_profit', 0) > best_profit:
                        best_profit = episode_result.get('total_profit', 0)
                        best_model = ai_trader.model
                
                # Atualizar status
                progress = ((episode + 1) / episodes) * 100
                self.update_status(progress, symbol)
            
            # Salvar melhor modelo
            if best_model:
                model_file = self.models_dir / f"worker_{self.worker_id}_{symbol.replace('-', '_')}_model.h5"
                best_model.save(model_file)
                logger.info(f"💾 Melhor modelo salvo: {model_file}")
            
            # Resultado do treinamento
            training_result = {
                'symbol': symbol,
                'worker_id': self.worker_id,
                'episodes': episodes,
                'best_profit': best_profit,
                'avg_profit': np.mean([r.get('total_profit', 0) for r in results]),
                'total_trades': sum([r.get('total_trades', 0) for r in results]),
                'win_rate': np.mean([r.get('win_rate', 0) for r in results]),
                'model_file': str(model_file) if best_model else None,
                'training_date': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Treinamento concluído para {symbol}: Profit=${best_profit:.2f}")
            return training_result
            
        except Exception as e:
            logger.error(f"❌ Erro no treinamento de {symbol}: {e}")
            return None
    
    def update_status(self, progress, current_pair):
        """Atualiza status do worker"""
        self.status.update({
            'status': 'running',
            'progress': progress,
            'current_pair': current_pair,
            'last_update': datetime.now().isoformat()
        })
        
        status_file = self.results_dir / f"worker_{self.worker_id}_status.json"
        with open(status_file, 'w') as f:
            json.dump(self.status, f, indent=2)
    
    def run(self):
        """Executa o worker de treinamento"""
        logger.info(f"🚀 Worker {self.worker_id} iniciando treinamento...")
        
        # Carregar configuração
        if not self.load_config():
            return
        
        # Atualizar status
        self.status['status'] = 'running'
        self.update_status(0, 'Iniciando...')
        
        # Treinar cada par
        results = []
        total_pairs = len(self.worker_config['trading_pairs'])
        
        for i, symbol in enumerate(self.worker_config['trading_pairs']):
            # Calcular progresso geral
            overall_progress = (i / total_pairs) * 100
            self.update_status(overall_progress, symbol)
            
            # Treinar par
            result = self.train_pair(symbol, self.worker_config['episodes_per_pair'])
            if result:
                results.append(result)
            
            # Pequena pausa entre pares
            time.sleep(2)
        
        # Salvar resultados
        results_file = self.results_dir / f"worker_{self.worker_id}_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Atualizar status final
        self.status.update({
            'status': 'completed',
            'progress': 100.0,
            'current_pair': 'Concluído',
            'end_time': datetime.now().isoformat(),
            'total_results': len(results)
        })
        self.update_status(100, 'Concluído')
        
        logger.info(f"✅ Worker {self.worker_id} concluído: {len(results)} resultados")

if __name__ == "__main__":
    worker = TrainingWorker()
    worker.run()
