#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Otimização Genética para Trading Algorítmico
Implementa algoritmos genéticos para otimizar parâmetros de trading automaticamente
"""

import random
import numpy as np
import pandas as pd
import json
import logging
from datetime import datetime
from pathlib import Path
from deap import base, creator, tools, algorithms
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeneticTradingOptimizer:
    """Otimizador genético para parâmetros de trading"""
    
    def __init__(self, data_dir="data", results_dir="results", training_data=None):
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        # Dados de treinamento (pode ser fornecido externamente)
        self.training_data = training_data
        
        # Configuração do algoritmo genético - VERSÃO ELITE
        self.population_size = 100  # População maior para mais diversidade
        self.generations = 50       # Mais gerações para convergência
        self.mutation_rate = 0.15   # Taxa de mutação ligeiramente maior
        self.crossover_rate = 0.8   # Taxa de crossover maior
        
        # Definir espaço de busca dos parâmetros
        self.param_ranges = {
            'rsi_oversold': (20, 40),      # RSI para compra
            'rsi_overbought': (60, 80),    # RSI para venda
            'sma_short': (10, 30),         # SMA curta
            'sma_long': (40, 100),         # SMA longa
            'stop_loss_pct': (0.01, 0.05), # Stop loss (1-5%)
            'take_profit_pct': (0.02, 0.08), # Take profit (2-8%)
            'max_hold_time': (12, 48),     # Tempo máximo (horas)
            'trade_amount_pct': (0.05, 0.20), # % do capital por trade
            'transaction_fee': (0.0005, 0.002) # Taxa de transação
        }
        
        # Pares para otimização
        self.trading_pairs = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT'
        ]
        
        # Configurar DEAP
        self.setup_genetic_algorithm()
    
    def setup_genetic_algorithm(self):
        """Configurar algoritmo genético com DEAP"""
        # Criar tipos para indivíduos e população
        if 'FitnessMax' not in creator.__dict__:
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        if 'Individual' not in creator.__dict__:
            creator.create("Individual", list, fitness=creator.FitnessMax)
        
        # Toolbox
        self.toolbox = base.Toolbox()
        
        # Gerador de genes (parâmetros)
        def generate_gene(param_name, param_range):
            if isinstance(param_range[0], int):
                return random.randint(param_range[0], param_range[1])
            else:
                return random.uniform(param_range[0], param_range[1])
        
        # Gerador de indivíduos
        def create_individual():
            individual = []
            for param_name, param_range in self.param_ranges.items():
                individual.append(generate_gene(param_name, param_range))
            return individual
        
        # Registrar operadores genéticos
        self.toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.evaluate_individual)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self.mutate_individual)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
    
    def mutate_individual(self, individual):
        """Mutação personalizada para parâmetros de trading - VERSÃO ELITE"""
        # Fazer uma cópia para não modificar o original
        mutated = individual[:]
        
        for i, (param_name, param_range) in enumerate(self.param_ranges.items()):
            if random.random() < self.mutation_rate:
                if isinstance(param_range[0], int):
                    mutated[i] = random.randint(param_range[0], param_range[1])
                else:
                    mutated[i] = random.uniform(param_range[0], param_range[1])
        
        # ---> VALIDAÇÃO PÓS-MUTAÇÃO <---
        # Se a mutação criou parâmetros inválidos, tentar corrigir
        params = self.individual_to_params(mutated)
        
        # Corrigir SMA se necessário
        if params['sma_short'] >= params['sma_long']:
            # Garantir que SMA curta seja menor que longa
            if params['sma_short'] >= params['sma_long']:
                params['sma_short'] = max(10, params['sma_long'] - 10)
        
        # Corrigir RSI se necessário
        if params['rsi_oversold'] >= params['rsi_overbought']:
            # Garantir que oversold seja menor que overbought
            params['rsi_oversold'] = min(35, params['rsi_overbought'] - 10)
        
        # Corrigir stop loss vs take profit
        if params['stop_loss_pct'] >= params['take_profit_pct']:
            # Garantir que take profit seja maior que stop loss
            params['take_profit_pct'] = params['stop_loss_pct'] * 1.5
        
        # Converter de volta para indivíduo
        for i, (param_name, _) in enumerate(self.param_ranges.items()):
            mutated[i] = params[param_name]
        
        return (mutated,)
    
    def individual_to_params(self, individual):
        """Converter indivíduo para dicionário de parâmetros"""
        params = {}
        for i, (param_name, _) in enumerate(self.param_ranges.items()):
            params[param_name] = individual[i]
        return params
    
    def evaluate_individual(self, individual):
        """Avaliar fitness de um indivíduo (estratégia) - VERSÃO ELITE"""
        try:
            params = self.individual_to_params(individual)
            
            # ---> VALIDAÇÃO LÓGICA DOS PARÂMETROS <---
            if params['sma_short'] >= params['sma_long']:
                return (-1000.0,)  # Penalização imediata por lógica inválida
            
            if params['rsi_oversold'] >= params['rsi_overbought']:
                return (-1000.0,)  # Penalização imediata por lógica inválida
            
            if params['stop_loss_pct'] >= params['take_profit_pct']:
                return (-1000.0,)  # Stop loss maior que take profit é inválido
            # ---> FIM DA VALIDAÇÃO LÓGICA <---
            
            # Simular backtesting com os parâmetros
            pair_results = []
            all_returns = []
            
            # Testar em múltiplos pares
            for symbol in self.trading_pairs[:3]:  # Usar apenas 3 pares para velocidade
                result = self.simulate_trading(symbol, params)
                if result and result['trades'] > 0:
                    pair_results.append(result)
                    all_returns.extend(result.get('returns', []))
            
            if not pair_results:
                return (-1000.0,)  # Penalizar estratégias sem trades
            
            # ---> OTIMIZAÇÃO PARA CONSISTÊNCIA (ELITE) <---
            # Calcular métricas individuais por par
            pair_metrics = []
            for result in pair_results:
                win_rate = result['wins'] / result['trades'] if result['trades'] > 0 else 0
                avg_profit = result['profit'] / result['trades'] if result['trades'] > 0 else 0
                
                # Sharpe Ratio individual
                returns = result.get('returns', [])
                sharpe_ratio = 0
                if returns:
                    returns_std = np.std(returns)
                    if returns_std > 0:
                        sharpe_ratio = np.mean(returns) / returns_std
                
                pair_metrics.append({
                    'win_rate': win_rate,
                    'avg_profit': avg_profit,
                    'sharpe_ratio': sharpe_ratio,
                    'trades': result['trades']
                })
            
            # Métrica de consistência: pior Sharpe Ratio entre todos os pares
            worst_sharpe = min(metric['sharpe_ratio'] for metric in pair_metrics)
            worst_win_rate = min(metric['win_rate'] for metric in pair_metrics)
            
            # Fitness baseado no pior cenário (ELITE)
            consistency_fitness = (worst_sharpe * 0.5 + worst_win_rate * 0.3 + 
                                 np.mean([m['avg_profit'] for m in pair_metrics]) * 0.2)
            
            return (consistency_fitness,)
            
        except Exception as e:
            logger.error(f"Erro na avaliação: {e}")
            return (-1000.0,)
    
    def simulate_trading(self, symbol, params):
        """Simular trading com parâmetros específicos"""
        try:
            # Usar dados fornecidos ou carregar do arquivo
            if self.training_data and symbol in self.training_data:
                data = self.training_data[symbol].copy()
            else:
                # Carregar dados do arquivo
                data_file = self.data_dir / f"{symbol.replace('/', '_')}_extended.csv"
                if not data_file.exists():
                    return None
                
                data = pd.read_csv(data_file, index_col=0, parse_dates=True)
            
            # Normalizar colunas
            if 'close' in data.columns:
                data['Close'] = data['close']
            
            # Parâmetros da simulação
            rsi_oversold = params['rsi_oversold']
            rsi_overbought = params['rsi_overbought']
            sma_short = int(params['sma_short'])
            sma_long = int(params['sma_long'])
            stop_loss_pct = params['stop_loss_pct']
            take_profit_pct = params['take_profit_pct']
            max_hold_time = int(params['max_hold_time'])
            trade_amount_pct = params['trade_amount_pct']
            transaction_fee = params['transaction_fee']
            
            # Simulação
            initial_balance = 1000
            current_balance = initial_balance
            trades = 0
            wins = 0
            returns = []
            
            position = {'type': None, 'entry_price': 0, 'entry_time': 0, 'amount': 0}
            
            for i in range(sma_long, len(data) - 1):
                current_price = data['Close'].iloc[i]
                
                # Calcular indicadores
                close_prices = data['Close'].iloc[i-sma_long:i+1]
                rsi = self.calculate_rsi(close_prices)
                sma_short_val = close_prices.rolling(window=sma_short).mean().iloc[-1]
                sma_long_val = close_prices.rolling(window=sma_long).mean().iloc[-1]
                
                # Verificar posição aberta
                if position['type'] is not None:
                    # Condições de saída
                    exit_trade = False
                    exit_price = current_price
                    
                    if position['type'] == 'long':
                        if (current_price <= position['entry_price'] * (1 - stop_loss_pct) or
                            current_price >= position['entry_price'] * (1 + take_profit_pct) or
                            i - position['entry_time'] >= max_hold_time or
                            rsi > rsi_overbought):
                            exit_trade = True
                    
                    elif position['type'] == 'short':
                        if (current_price >= position['entry_price'] * (1 + stop_loss_pct) or
                            current_price <= position['entry_price'] * (1 - take_profit_pct) or
                            i - position['entry_time'] >= max_hold_time or
                            rsi < rsi_oversold):
                            exit_trade = True
                    
                    if exit_trade:
                        # Calcular lucro/prejuízo
                        if position['type'] == 'long':
                            price_change = (exit_price - position['entry_price']) / position['entry_price']
                        else:
                            price_change = (position['entry_price'] - exit_price) / position['entry_price']
                        
                        net_change = price_change - (2 * transaction_fee)
                        profit = position['amount'] * net_change
                        
                        current_balance += profit
                        trades += 1
                        returns.append(profit)
                        
                        if profit > 0:
                            wins += 1
                        
                        position = {'type': None, 'entry_price': 0, 'entry_time': 0, 'amount': 0}
                
                # Verificar entrada
                if position['type'] is None:
                    trend_bullish = sma_short_val > sma_long_val
                    trend_bearish = sma_short_val < sma_long_val
                    
                    # Long
                    if rsi < rsi_oversold and trend_bullish:
                        trade_amount = current_balance * trade_amount_pct
                        position = {
                            'type': 'long',
                            'entry_price': current_price,
                            'entry_time': i,
                            'amount': trade_amount
                        }
                        current_balance -= trade_amount
                    
                    # Short
                    elif rsi > rsi_overbought and trend_bearish:
                        trade_amount = current_balance * trade_amount_pct
                        position = {
                            'type': 'short',
                            'entry_price': current_price,
                            'entry_time': i,
                            'amount': trade_amount
                        }
                        current_balance -= trade_amount
            
            return {
                'profit': current_balance - initial_balance,
                'trades': trades,
                'wins': wins,
                'returns': returns
            }
            
        except Exception as e:
            logger.error(f"Erro na simulação {symbol}: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Calcular RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else 50
    
    def run_optimization(self, training_data=None):
        """Executar otimização genética"""
        # Atualizar dados de treinamento se fornecidos
        if training_data:
            self.training_data = training_data
        logger.info("🧬 INICIANDO OTIMIZAÇÃO GENÉTICA")
        logger.info("=" * 50)
        
        # Criar população inicial
        pop = self.toolbox.population(n=self.population_size)
        
        # Estatísticas
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)
        
        # Hall of Fame (melhores indivíduos)
        hof = tools.HallOfFame(5)
        
        # Executar algoritmo genético
        start_time = time.time()
        
        pop, logbook = algorithms.eaSimple(
            pop, 
            self.toolbox, 
            cxpb=self.crossover_rate, 
            mutpb=self.mutation_rate, 
            ngen=self.generations,
            stats=stats,
            halloffame=hof,
            verbose=True
        )
        
        optimization_time = time.time() - start_time
        
        # Resultados
        logger.info("🎯 OTIMIZAÇÃO CONCLUÍDA!")
        logger.info(f"⏱️ Tempo: {optimization_time:.1f} segundos")
        
        # Salvar melhores parâmetros
        best_params = self.individual_to_params(hof[0])
        best_fitness = hof[0].fitness.values[0]
        
        results = {
            'optimization_date': datetime.now().isoformat(),
            'best_fitness': best_fitness,
            'best_params': best_params,
            'generations': self.generations,
            'population_size': self.population_size,
            'optimization_time': optimization_time,
            'hall_of_fame': [
                {
                    'fitness': ind.fitness.values[0],
                    'params': self.individual_to_params(ind)
                }
                for ind in hof
            ]
        }
        
        # Salvar resultados
        results_file = self.results_dir / "genetic_optimization_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Log dos melhores parâmetros
        logger.info("🏆 MELHORES PARÂMETROS ENCONTRADOS:")
        logger.info(f"   - Fitness: {best_fitness:.4f}")
        logger.info("   📊 Parâmetros Otimizados:")
        for param, value in best_params.items():
            logger.info(f"      - {param}: {value}")
        
        # Log do Hall of Fame
        logger.info("🥇 HALL OF FAME (Top 5 Estratégias):")
        for i, ind in enumerate(hof):
            fitness = ind.fitness.values[0]
            params = self.individual_to_params(ind)
            logger.info(f"   #{i+1} - Fitness: {fitness:.4f}")
            logger.info(f"      RSI: {params['rsi_oversold']:.1f}-{params['rsi_overbought']:.1f}")
            logger.info(f"      SMA: {params['sma_short']}-{params['sma_long']}")
            logger.info(f"      SL/TP: {params['stop_loss_pct']:.3f}/{params['take_profit_pct']:.3f}")
        
        return best_params

if __name__ == "__main__":
    optimizer = GeneticTradingOptimizer()
    best_params = optimizer.run_optimization()
