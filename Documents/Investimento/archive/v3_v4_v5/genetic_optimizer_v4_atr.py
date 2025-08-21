#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GENETIC OPTIMIZER v4.0 - RISCO DINÂMICO COM ATR
=================================================
Versão de elite com:
1. Risco dinâmico (Stop Loss/Take Profit) baseado na volatilidade (ATR).
2. Capacidade de aceitar dados externos para Walk-Forward.
3. Otimização para consistência (pior cenário).
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
        logging.FileHandler('logs/genetic_optimizer_v4_atr.log', encoding='utf-8'),
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
        
        # --- ALTERADO: Espaço de busca com parâmetros de risco dinâmico ---
        self.param_ranges = {
            'rsi_oversold': (20, 40),
            'rsi_overbought': (60, 80),
            'sma_short': (10, 50),
            'sma_long': (50, 100),
            'atr_period': (10, 30),                 # Período para cálculo do ATR
            'atr_stop_loss_multiplier': (1.0, 3.0), # Multiplicador de ATR para Stop Loss
            'atr_take_profit_multiplier': (2.0, 6.0),# Multiplicador de ATR para Take Profit
            'max_hold_time': (12, 48),
            'trade_amount_pct': (0.05, 0.20),
        }
        
        self.trading_pairs = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT'
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
        
        # --- ALTERADO: Geradores de genes para os novos parâmetros ---
        self.toolbox.register("rsi_oversold", random.randint, 20, 40)
        self.toolbox.register("rsi_overbought", random.randint, 60, 80)
        self.toolbox.register("sma_short", random.randint, 10, 50)
        self.toolbox.register("sma_long", random.randint, 50, 100)
        self.toolbox.register("atr_period", random.randint, 10, 30)
        self.toolbox.register("atr_stop_loss_multiplier", random.uniform, 1.0, 3.0)
        self.toolbox.register("atr_take_profit_multiplier", random.uniform, 2.0, 6.0)
        self.toolbox.register("max_hold_time", random.randint, 12, 48)
        self.toolbox.register("trade_amount_pct", random.uniform, 0.05, 0.20)
        
        self.toolbox.register("individual", tools.initCycle, creator.Individual,
                              (self.toolbox.rsi_oversold, self.toolbox.rsi_overbought,
                               self.toolbox.sma_short, self.toolbox.sma_long,
                               self.toolbox.atr_period, self.toolbox.atr_stop_loss_multiplier,
                               self.toolbox.atr_take_profit_multiplier, self.toolbox.max_hold_time,
                               self.toolbox.trade_amount_pct), n=1)
        
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.evaluate_individual)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self.mutate_individual)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    # --- NOVO: Função para calcular o ATR ---
    def calculate_atr(self, high, low, close, period=14):
        """Calcula o Average True Range (ATR)."""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

    def simulate_trading(self, symbol, params, data_override=None):
        """Simula o trading com parâmetros específicos, agora com risco dinâmico."""
        try:
            if data_override is not None:
                data = data_override.copy()
            else:
                return None

            # --- ALTERADO: Mapeamento de parâmetros para o indivíduo ---
            param_names = list(self.param_ranges.keys())
            params_dict = dict(zip(param_names, params))

            # Verificar se temos dados suficientes
            if len(data) < 100:
                logging.warning(f"Dados insuficientes para {symbol}: {len(data)} pontos")
                return None

            # Garantir que temos as colunas necessárias
            if 'high' not in data.columns or 'low' not in data.columns:
                logging.warning(f"Dados OHLC incompletos para {symbol}")
                return None

            # Pré-calcular indicadores para performance
            data['sma_short'] = data['close'].rolling(window=int(params_dict['sma_short'])).mean()
            data['sma_long'] = data['close'].rolling(window=int(params_dict['sma_long'])).mean()
            data['rsi'] = self.calculate_rsi_series(data['close'], 14)
            data['atr'] = self.calculate_atr(data['high'], data['low'], data['close'], period=int(params_dict['atr_period']))
            data.dropna(inplace=True)

            if len(data) < 50:  # Verificar se ainda temos dados suficientes após dropna
                return None

            initial_balance = 10000
            current_balance = initial_balance
            position = None
            trades = []
            
            for i in range(len(data)):
                row = data.iloc[i]
                
                if position:
                    exit_trade = False
                    if row.close <= position['stop_loss'] or row.close >= position['take_profit']:
                        exit_trade = True
                    elif (row.name - position['entry_time']).total_seconds() / 3600 >= params_dict['max_hold_time']:
                        exit_trade = True
                    
                    if exit_trade:
                        profit = (row.close - position['entry_price']) * position['quantity']
                        current_balance += position['cost'] + profit
                        trades.append({'profit': profit})
                        position = None
                
                if not position:
                    if row.sma_short > row.sma_long and row.rsi < params_dict['rsi_oversold']:
                        trade_amount = current_balance * params_dict['trade_amount_pct']
                        quantity = trade_amount / row.close
                        
                        position = {
                            'entry_time': row.name,
                            'entry_price': row.close,
                            'quantity': quantity,
                            'cost': trade_amount,
                            # --- LÓGICA DE RISCO DINÂMICO ---
                            'stop_loss': row.close - (row.atr * params_dict['atr_stop_loss_multiplier']),
                            'take_profit': row.close + (row.atr * params_dict['atr_take_profit_multiplier'])
                        }
                        current_balance -= trade_amount
            
            return {
                'profit': current_balance - initial_balance,
                'trades': len(trades),
                'wins': len([t for t in trades if t['profit'] > 0]),
                'returns': [t['profit'] for t in trades]
            }

        except Exception as e:
            logging.error(f"Erro no backtest: {e}")
            return None

    def evaluate_individual(self, individual, training_data):
        """Avalia um indivíduo usando os dados de treino fornecidos."""
        try:
            params_dict = dict(zip(self.param_ranges.keys(), individual))
            # Validação lógica
            if params_dict['sma_short'] >= params_dict['sma_long'] or \
               params_dict['rsi_oversold'] >= params_dict['rsi_overbought'] or \
               params_dict['atr_stop_loss_multiplier'] >= params_dict['atr_take_profit_multiplier']:
                return (1000,)

            all_results = []
            for symbol, data in training_data.items():
                result = self.simulate_trading(symbol, individual, data_override=data)
                if result:
                    all_results.append(result)
            
            if not all_results:
                return (1000,)
            
            sharpe_ratios = []
            for res in all_results:
                if res['trades'] > 1 and np.std(res['returns']) > 0:
                    sharpe = np.mean(res['returns']) / np.std(res['returns'])
                    sharpe_ratios.append(sharpe)
            
            worst_sharpe = min(sharpe_ratios) if sharpe_ratios else -10
            fitness = -worst_sharpe
            return (fitness,)

        except Exception as e:
            logging.error(f"Erro na avaliação: {e}")
            return (1000,)

    def run_optimization(self, training_data):
        """Executa a otimização genética nos dados de treino fornecidos."""
        logging.info(f"🧬 Iniciando otimização v4.0 com {len(training_data)} pares")
        logging.info("🎯 Parâmetros de risco dinâmico: ATR-based")
        
        self.toolbox.register("evaluate", self.evaluate_individual, training_data=training_data)
        
        pop = self.toolbox.population(n=self.population_size)
        hof = tools.HallOfFame(1)
        
        algorithms.eaSimple(pop, self.toolbox, cxpb=self.crossover_prob, mutpb=self.mutation_prob,
                              ngen=self.generations, halloffame=hof, verbose=False)
        
        best_params_list = list(hof[0])
        best_params = dict(zip(self.param_ranges.keys(), best_params_list))
        
        logging.info(f"✅ Melhores parâmetros encontrados: {best_params}")
        return best_params

    # --- MÉTODOS AUXILIARES ---
    def calculate_sma(self, prices, period):
        if len(prices) < period: return None
        return pd.Series(prices).rolling(window=period).mean().iloc[-1]
    
    def calculate_rsi_series(self, prices, period=14):
        """Calcula RSI para uma série completa."""
        prices = pd.Series(prices)
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_rsi(self, prices, period=14):
        """Calcula RSI para um valor único."""
        rsi_series = self.calculate_rsi_series(prices, period)
        return rsi_series.iloc[-1] if not rsi_series.empty else 50

    def mutate_individual(self, individual):
        """Mutação inteligente que tenta corrigir genes inválidos."""
        individual = list(individual)
        
        # Mutação padrão
        for i in range(len(individual)):
            if random.random() < 0.1:  # 10% chance de mutação
                if i == 0:  # rsi_oversold
                    individual[i] = random.randint(20, 40)
                elif i == 1:  # rsi_overbought
                    individual[i] = random.randint(60, 80)
                elif i == 2:  # sma_short
                    individual[i] = random.randint(10, 50)
                elif i == 3:  # sma_long
                    individual[i] = random.randint(50, 100)
                elif i == 4:  # atr_period
                    individual[i] = random.randint(10, 30)
                elif i == 5:  # atr_stop_loss_multiplier
                    individual[i] = random.uniform(1.0, 3.0)
                elif i == 6:  # atr_take_profit_multiplier
                    individual[i] = random.uniform(2.0, 6.0)
                elif i == 7:  # max_hold_time
                    individual[i] = random.randint(12, 48)
                elif i == 8:  # trade_amount_pct
                    individual[i] = random.uniform(0.05, 0.20)
        
        # Correção de lógica inválida
        if individual[2] >= individual[3]:  # sma_short >= sma_long
            individual[3] = individual[2] + random.randint(10, 30)
        
        if individual[0] >= individual[1]:  # rsi_oversold >= rsi_overbought
            individual[1] = individual[0] + random.randint(10, 20)
        
        if individual[5] >= individual[6]:  # atr_stop >= atr_take
            individual[6] = individual[5] + random.uniform(0.5, 2.0)
        
        return individual,

    def calculate_sharpe_ratio(self, returns_series):
        if not returns_series.empty and returns_series.std() > 0:
            return (returns_series.mean() / returns_series.std()) * np.sqrt(252)
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
    logging.info("🧬 GENETIC OPTIMIZER v4.0 - RISCO DINÂMICO COM ATR")
    logging.info("=" * 60)
    logging.info("🎯 NOVA FUNCIONALIDADE: Stop Loss/Take Profit baseado em volatilidade")
    logging.info("📊 ATR: Average True Range para risco adaptativo")
    logging.info("🔄 Sistema se adapta automaticamente à volatilidade do mercado")
    
    optimizer = GeneticTradingOptimizer()
    
    # Teste básico
    logging.info("✅ Otimizador v4.0 inicializado com sucesso!")
    logging.info("🔧 Pronto para integração com Walk-Forward Optimization")
    logging.info("🚀 Sistema de risco dinâmico ativo!")

if __name__ == "__main__":
    main()
