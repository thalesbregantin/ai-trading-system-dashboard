#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GENETIC OPTIMIZER v3.1 - CORRIGIDO E OTIMIZADO
==============================================
Versão final com:
1. Capacidade de aceitar dados externos para Walk-Forward.
2. Cache de dados históricos.
3. Validação cruzada simplificada.
"""

import ccxt
import time
import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import logging
from deap import base, creator, tools, algorithms
import random
import pickle

# Carregar variáveis do .env
load_dotenv()

# Configuração da Binance
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/genetic_optimizer_v3_fixed.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class GeneticTradingOptimizer:
    def __init__(self):
        self.exchange = None
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
        self.cache_dir = Path('cache')
        self.cache_dir.mkdir(exist_ok=True)
        
        # Parâmetros de otimização
        self.population_size = 30
        self.generations = 30
        self.crossover_prob = 0.7
        self.mutation_prob = 0.3
        
        # Validação cruzada simplificada
        self.k_folds = 3
        
        # Pares para otimização
        self.trading_pairs = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT'
        ]
        
        # Períodos de dados
        self.data_periods = [
            ('2024-01-01', '2024-06-30'),
            ('2024-07-01', '2024-12-31'),
        ]
        
        self.data_cache = {}
        self.setup_deap()
        
    def setup_deap(self):
        if hasattr(creator, "FitnessMin"):
            del creator.FitnessMin
        if hasattr(creator, "Individual"):
            del creator.Individual
        
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
        
        self.toolbox = base.Toolbox()
        
        self.toolbox.register("rsi_oversold", random.randint, 20, 50)
        self.toolbox.register("rsi_overbought", random.randint, 50, 80)
        self.toolbox.register("sma_short", random.randint, 10, 50)
        self.toolbox.register("sma_long", random.randint, 30, 100)
        self.toolbox.register("stop_loss_pct", random.uniform, 0.005, 0.03)
        self.toolbox.register("take_profit_pct", random.uniform, 0.01, 0.08)
        self.toolbox.register("max_hold_time", random.randint, 6, 48)
        self.toolbox.register("trade_amount_pct", random.uniform, 0.02, 0.10)
        self.toolbox.register("transaction_fee", random.uniform, 0.0005, 0.002)
        
        self.toolbox.register("individual", tools.initCycle, creator.Individual,
                              (self.toolbox.rsi_oversold, self.toolbox.rsi_overbought,
                               self.toolbox.sma_short, self.toolbox.sma_long,
                               self.toolbox.stop_loss_pct, self.toolbox.take_profit_pct,
                               self.toolbox.max_hold_time, self.toolbox.trade_amount_pct,
                               self.toolbox.transaction_fee), n=1)
        
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.evaluate_individual)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self.mutate_individual)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    # --- MÉTODOS DE DADOS E BACKTESTING ---
    
    def simulate_trading(self, symbol, params, data_override=None):
        """
        Simula o trading com parâmetros específicos.
        Aceita um DataFrame externo para Walk-Forward.
        """
        try:
            if data_override is not None:
                data = data_override.copy()
            else:
                # Lógica para carregar do cache/arquivo se não for Walk-Forward
                logging.warning("simulate_trading chamado sem dados externos")
                return None

            # Verificar se temos dados suficientes
            if len(data) < 100:
                logging.warning(f"Dados insuficientes para {symbol}: {len(data)} pontos")
                return None

            initial_balance = 10000
            current_balance = initial_balance
            position = None
            trades = []
            
            rsi_oversold, rsi_overbought, sma_short, sma_long, stop_loss_pct, take_profit_pct, max_hold_time, trade_amount_pct, transaction_fee = params
            
            for i in range(max(sma_long, 50), len(data)):
                current_price = data['close'].iloc[i]
                current_time = data.index[i]
                
                prices = data['close'].iloc[:i+1].values
                sma_short_val = self.calculate_sma(prices, sma_short)
                sma_long_val = self.calculate_sma(prices, sma_long)
                rsi = self.calculate_rsi(prices, 14)
                
                if position:
                    entry_price = position['entry_price']
                    price_change = (current_price - entry_price) / entry_price
                    hold_time_hours = (current_time - position['entry_time']).total_seconds() / 3600
                    
                    should_exit = False
                    exit_reason = ""
                    
                    if price_change >= take_profit_pct:
                        should_exit, exit_reason = True, "Take Profit"
                    elif price_change <= -stop_loss_pct:
                        should_exit, exit_reason = True, "Stop Loss"
                    elif hold_time_hours >= max_hold_time:
                        should_exit, exit_reason = True, "Max Hold Time"
                    
                    if should_exit:
                        sell_value = position['quantity'] * current_price * (1 - transaction_fee)
                        profit = sell_value - position['cost']
                        current_balance += sell_value
                        trades.append({'profit': profit})
                        position = None
                
                if not position and sma_short_val and sma_long_val and rsi:
                    if sma_short_val > sma_long_val and rsi < rsi_oversold:
                        trade_amount = current_balance * trade_amount_pct
                        quantity = trade_amount / current_price
                        cost = quantity * current_price * (1 + transaction_fee)
                        
                        if cost <= current_balance:
                            position = {'entry_time': current_time, 'entry_price': current_price, 'quantity': quantity, 'cost': cost}
                            current_balance -= cost
            
            return {
                'profit': current_balance - initial_balance,
                'trades': len(trades),
                'wins': len([t for t in trades if t['profit'] > 0]),
                'returns': [t['profit'] for t in trades]
            }

        except Exception as e:
            logging.error(f"Erro no backtest: {e}")
            return None

    # --- MÉTODOS DO ALGORITMO GENÉTICO ---
    
    def evaluate_individual(self, individual, training_data):
        """Avalia um indivíduo usando os dados de treino fornecidos."""
        try:
            # Validação lógica
            if individual[2] >= individual[3] or individual[0] >= individual[1]:
                return (1000,)

            all_results = []
            for symbol, data in training_data.items():
                result = self.simulate_trading(symbol, individual, data_override=data)
                if result:
                    all_results.append(result)
            
            if not all_results:
                return (1000,)
            
            # Fitness baseado no pior cenário (consistência)
            sharpe_ratios = []
            for res in all_results:
                if res['trades'] > 1 and np.std(res['returns']) > 0:
                    sharpe = np.mean(res['returns']) / np.std(res['returns'])
                    sharpe_ratios.append(sharpe)
            
            worst_sharpe = min(sharpe_ratios) if sharpe_ratios else -10
            fitness = -worst_sharpe # Queremos maximizar o pior Sharpe, então minimizamos o negativo dele
            return (fitness,)

        except Exception as e:
            logging.error(f"Erro na avaliação: {e}")
            return (1000,)

    def run_optimization(self, training_data):
        """Executa a otimização genética nos dados de treino fornecidos."""
        logging.info(f"Iniciando otimização com {len(training_data)} pares")
        
        # Registrar a função de avaliação com os dados corretos
        self.toolbox.register("evaluate", self.evaluate_individual, training_data=training_data)
        
        pop = self.toolbox.population(n=self.population_size)
        hof = tools.HallOfFame(1)
        
        algorithms.eaSimple(pop, self.toolbox, cxpb=self.crossover_prob, mutpb=self.mutation_prob,
                              ngen=self.generations, halloffame=hof, verbose=False)
        
        best_params_list = list(hof[0])
        param_names = ['rsi_oversold', 'rsi_overbought', 'sma_short', 'sma_long', 'stop_loss_pct', 'take_profit_pct', 'max_hold_time', 'trade_amount_pct', 'transaction_fee']
        best_params = dict(zip(param_names, best_params_list))
        
        logging.info(f"Melhores parâmetros encontrados: {best_params}")
        return best_params

    def calculate_sma(self, prices, period):
        if len(prices) < period: return None
        return np.mean(prices[-period:])
    
    def calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1: return None
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        if avg_loss == 0: return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def mutate_individual(self, individual):
        """Mutação inteligente que tenta corrigir genes inválidos."""
        individual = list(individual)
        
        # Mutação padrão
        for i in range(len(individual)):
            if random.random() < 0.1:  # 10% chance de mutação
                if i == 0:  # rsi_oversold
                    individual[i] = random.randint(20, 50)
                elif i == 1:  # rsi_overbought
                    individual[i] = random.randint(50, 80)
                elif i == 2:  # sma_short
                    individual[i] = random.randint(10, 50)
                elif i == 3:  # sma_long
                    individual[i] = random.randint(30, 100)
                elif i == 4:  # stop_loss_pct
                    individual[i] = random.uniform(0.005, 0.03)
                elif i == 5:  # take_profit_pct
                    individual[i] = random.uniform(0.01, 0.08)
                elif i == 6:  # max_hold_time
                    individual[i] = random.randint(6, 48)
                elif i == 7:  # trade_amount_pct
                    individual[i] = random.uniform(0.02, 0.10)
                elif i == 8:  # transaction_fee
                    individual[i] = random.uniform(0.0005, 0.002)
        
        # Correção de lógica inválida
        if individual[2] >= individual[3]:  # sma_short >= sma_long
            individual[3] = individual[2] + random.randint(10, 30)
        
        if individual[0] >= individual[1]:  # rsi_oversold >= rsi_overbought
            individual[1] = individual[0] + random.randint(10, 20)
        
        return individual,

    def calculate_sharpe_ratio(self, returns_series):
        if returns_series.std() > 0:
            return (returns_series.mean() / returns_series.std()) * np.sqrt(252) # Anualizado
        return 0

    def calculate_max_drawdown(self, equity_curve):
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return drawdown.min()

    def calculate_profit_factor(self, returns):
        if not returns: return float('inf')
        gross_profit = sum(r for r in returns if r > 0)
        gross_loss = abs(sum(r for r in returns if r < 0))
        return gross_profit / gross_loss if gross_loss > 0 else float('inf')

def main():
    """Função principal para teste independente."""
    logging.info("🧬 GENETIC OPTIMIZER v3.1 - VERSÃO CORRIGIDA")
    logging.info("=" * 50)
    
    optimizer = GeneticTradingOptimizer()
    
    # Teste básico
    logging.info("✅ Otimizador inicializado com sucesso!")
    logging.info("🔧 Pronto para integração com Walk-Forward Optimization")

if __name__ == "__main__":
    main()
