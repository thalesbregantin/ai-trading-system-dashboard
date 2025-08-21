#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GENETIC OPTIMIZER v3.0 - OTIMIZADO
===================================

Versão otimizada com:
1. Cache de dados históricos
2. Validação cruzada simplificada
3. Processamento em lotes
4. Melhor performance
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
        logging.FileHandler('logs/genetic_optimizer_v3.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class GeneticOptimizerV3:
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
        
        # Pares para otimização (reduzidos)
        self.trading_pairs = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT'
        ]
        
        # Períodos de dados (reduzidos)
        self.data_periods = [
            ('2024-01-01', '2024-06-30'),  # Primeiro semestre 2024
            ('2024-07-01', '2024-12-31'),  # Segundo semestre 2024
        ]
        
        # Cache de dados
        self.data_cache = {}
        
        # Configurar DEAP
        self.setup_deap()
        
    def setup_deap(self):
        """Configurar DEAP para otimização genética"""
        # Limpar registros anteriores
        if hasattr(creator, "FitnessMin"):
            del creator.FitnessMin
        if hasattr(creator, "Individual"):
            del creator.Individual
        
        # Criar tipos
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
        
        # Configurar toolbox
        self.toolbox = base.Toolbox()
        
        # Genes (parâmetros)
        self.toolbox.register("rsi_oversold", random.randint, 20, 50)
        self.toolbox.register("rsi_overbought", random.randint, 50, 80)
        self.toolbox.register("sma_short", random.randint, 10, 50)
        self.toolbox.register("sma_long", random.randint, 30, 100)
        self.toolbox.register("stop_loss_pct", random.uniform, 0.005, 0.03)
        self.toolbox.register("take_profit_pct", random.uniform, 0.01, 0.08)
        self.toolbox.register("max_hold_time", random.randint, 6, 48)
        self.toolbox.register("trade_amount_pct", random.uniform, 0.02, 0.10)
        self.toolbox.register("transaction_fee", random.uniform, 0.0005, 0.002)
        
        # Estrutura do indivíduo
        self.toolbox.register("individual", tools.initCycle, creator.Individual,
                             (self.toolbox.rsi_oversold, self.toolbox.rsi_overbought,
                              self.toolbox.sma_short, self.toolbox.sma_long,
                              self.toolbox.stop_loss_pct, self.toolbox.take_profit_pct,
                              self.toolbox.max_hold_time, self.toolbox.trade_amount_pct,
                              self.toolbox.transaction_fee), n=1)
        
        # População
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        # Operadores genéticos
        self.toolbox.register("evaluate", self.evaluate_individual)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self.mutate_individual)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        
    def setup_binance(self):
        """Configurar conexão com Binance"""
        try:
            self.exchange = ccxt.binance({
                'apiKey': BINANCE_API_KEY,
                'secret': BINANCE_SECRET_KEY,
                'sandbox': False,
                'enableRateLimit': True,
                'options': {
                    'adjustForTimeDifference': True,
                    'recvWindow': 60000
                }
            })
            logging.info("Conexao Binance estabelecida")
            return True
        except Exception as e:
            logging.error(f"Erro ao conectar com Binance: {e}")
            return False
    
    def get_cached_data(self, symbol, start_date, end_date):
        """Obter dados do cache ou baixar se necessário"""
        cache_key = f"{symbol}_{start_date}_{end_date}"
        
        if cache_key in self.data_cache:
            logging.info(f"Dados em cache: {symbol}")
            return self.data_cache[cache_key]
        
        # Verificar se existe arquivo de cache
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                self.data_cache[cache_key] = data
                logging.info(f"Dados carregados do cache: {symbol}")
                return data
            except Exception as e:
                logging.warning(f"Erro ao carregar cache: {e}")
        
        # Baixar dados
        data = self.get_historical_data(symbol, start_date, end_date)
        if data is not None:
            # Salvar no cache
            self.data_cache[cache_key] = data
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
            except Exception as e:
                logging.warning(f"Erro ao salvar cache: {e}")
        
        return data
    
    def get_historical_data(self, symbol, start_date, end_date, timeframe='1h'):
        """Obter dados históricos"""
        try:
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
            
            logging.info(f"Baixando dados: {symbol} ({start_date} a {end_date})")
            
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=start_ts, limit=1000)
            
            if not ohlcv:
                return None
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            
            logging.info(f"Dados baixados: {symbol} - {len(df)} candles")
            return df
            
        except Exception as e:
            logging.error(f"Erro ao obter dados para {symbol}: {e}")
            return None
    
    def calculate_sma(self, prices, period):
        """Calcular Média Móvel Simples"""
        if len(prices) < period:
            return None
        return np.mean(prices[-period:])
    
    def calculate_rsi(self, prices, period=14):
        """Calcular RSI"""
        if len(prices) < period + 1:
            return None
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def backtest_strategy_cv(self, df, params, fold_name):
        """Backtest da estratégia para validação cruzada"""
        try:
            initial_balance = 10000
            current_balance = initial_balance
            position = None
            trades = []
            
            # Extrair parâmetros
            rsi_oversold, rsi_overbought, sma_short, sma_long, stop_loss_pct, take_profit_pct, max_hold_time, trade_amount_pct, transaction_fee = params
            
            # Processar cada candle
            for i in range(max(sma_long, 50), len(df)):
                current_price = df['close'].iloc[i]
                current_time = df.index[i]
                
                # Calcular indicadores
                prices = df['close'].iloc[:i+1].values
                sma_short_val = self.calculate_sma(prices, sma_short)
                sma_long_val = self.calculate_sma(prices, sma_long)
                rsi = self.calculate_rsi(prices, 14)
                
                # Verificar posição aberta
                if position:
                    entry_price = position['entry_price']
                    price_change = (current_price - entry_price) / entry_price
                    hold_time_hours = (current_time - position['entry_time']).total_seconds() / 3600
                    
                    # Verificar condições de saída
                    should_exit = False
                    exit_reason = ""
                    
                    if price_change >= take_profit_pct:
                        should_exit = True
                        exit_reason = "Take Profit"
                    elif price_change <= -stop_loss_pct:
                        should_exit = True
                        exit_reason = "Stop Loss"
                    elif hold_time_hours >= max_hold_time:
                        should_exit = True
                        exit_reason = "Max Hold Time"
                    
                    if should_exit:
                        sell_value = position['quantity'] * current_price * (1 - transaction_fee)
                        profit = sell_value - position['cost']
                        profit_pct = (profit / position['cost']) * 100
                        
                        current_balance += sell_value
                        
                        trade = {
                            'entry_time': position['entry_time'],
                            'exit_time': current_time,
                            'entry_price': position['entry_price'],
                            'exit_price': current_price,
                            'quantity': position['quantity'],
                            'profit': profit,
                            'profit_pct': profit_pct,
                            'exit_reason': exit_reason,
                            'hold_time_hours': hold_time_hours
                        }
                        trades.append(trade)
                        
                        position = None
                
                # Verificar condições de entrada
                if not position and sma_short_val and sma_long_val and rsi:
                    bullish_trend = sma_short_val > sma_long_val
                    rsi_oversold_condition = rsi < rsi_oversold
                    
                    if bullish_trend and rsi_oversold_condition:
                        trade_amount = current_balance * trade_amount_pct
                        quantity = trade_amount / current_price
                        cost = quantity * current_price * (1 + transaction_fee)
                        
                        if cost <= current_balance:
                            position = {
                                'entry_time': current_time,
                                'entry_price': current_price,
                                'quantity': quantity,
                                'cost': cost
                            }
                            current_balance -= cost
            
            # Fechar posição final se houver
            if position:
                final_price = df['close'].iloc[-1]
                sell_value = position['quantity'] * final_price * (1 - transaction_fee)
                profit = sell_value - position['cost']
                profit_pct = (profit / position['cost']) * 100
                
                current_balance += sell_value
                
                trade = {
                    'entry_time': position['entry_time'],
                    'exit_time': df.index[-1],
                    'entry_price': position['entry_price'],
                    'exit_price': final_price,
                    'quantity': position['quantity'],
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'exit_reason': 'End of Period',
                    'hold_time_hours': (df.index[-1] - position['entry_time']).total_seconds() / 3600
                }
                trades.append(trade)
            
            # Calcular métricas
            total_return = ((current_balance - initial_balance) / initial_balance) * 100
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t['profit'] > 0])
            losing_trades = len([t for t in trades if t['profit'] < 0])
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            avg_profit = np.mean([t['profit_pct'] for t in trades]) if trades else 0
            avg_win = np.mean([t['profit_pct'] for t in trades if t['profit'] > 0]) if winning_trades > 0 else 0
            avg_loss = np.mean([t['profit_pct'] for t in trades if t['profit'] < 0]) if losing_trades > 0 else 0
            
            # Calcular Sharpe Ratio
            returns = [t['profit_pct'] for t in trades]
            sharpe_ratio = np.mean(returns) / np.std(returns) if len(returns) > 1 and np.std(returns) > 0 else 0
            
            # Calcular máximo drawdown
            max_drawdown = self.calculate_max_drawdown(trades, initial_balance)
            
            # Penalização por overfitting
            overfitting_penalty = 0
            if total_trades < 5:  # Poucos trades
                overfitting_penalty += 3
            if win_rate < 30:  # Win rate muito baixo
                overfitting_penalty += 2
            if sharpe_ratio < -1:  # Sharpe muito negativo
                overfitting_penalty += 1
            
            # Fitness score (menor é melhor)
            fitness = -total_return + overfitting_penalty
            
            # Penalização adicional para resultados muito ruins
            if total_return < -10:
                fitness += 5
            
            return {
                'fold': fold_name,
                'total_return': total_return,
                'win_rate': win_rate,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'total_trades': total_trades,
                'avg_profit': avg_profit,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'overfitting_penalty': overfitting_penalty,
                'fitness': fitness,
                'trades': trades
            }
            
        except Exception as e:
            logging.error(f"Erro no backtest CV: {e}")
            return None
    
    def calculate_max_drawdown(self, trades, initial_balance):
        """Calcular máximo drawdown"""
        try:
            if not trades:
                return 0
            
            balance = initial_balance
            peak_balance = initial_balance
            max_drawdown = 0
            
            for trade in trades:
                balance += trade['profit']
                
                if balance > peak_balance:
                    peak_balance = balance
                
                drawdown = (peak_balance - balance) / peak_balance * 100
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            return max_drawdown
            
        except Exception as e:
            logging.error(f"Erro ao calcular max drawdown: {e}")
            return 0
    
    def evaluate_individual(self, individual):
        """Avaliar indivíduo com validação cruzada simplificada"""
        try:
            # Dividir dados em k-folds
            all_results = []
            
            for period_start, period_end in self.data_periods:
                # Dividir período em k-folds
                start_date = datetime.strptime(period_start, '%Y-%m-%d')
                end_date = datetime.strptime(period_end, '%Y-%m-%d')
                total_days = (end_date - start_date).days
                fold_days = total_days // self.k_folds
                
                fold_results = []
                
                for k in range(self.k_folds):
                    # Calcular datas do fold
                    fold_start = start_date + timedelta(days=k * fold_days)
                    fold_end = fold_start + timedelta(days=fold_days)
                    
                    if k == self.k_folds - 1:  # Último fold pega o resto
                        fold_end = end_date
                    
                    fold_start_str = fold_start.strftime('%Y-%m-%d')
                    fold_end_str = fold_end.strftime('%Y-%m-%d')
                    fold_name = f"{period_start}_{period_end}_fold_{k+1}"
                    
                    # Testar em todos os pares
                    pair_results = []
                    for symbol in self.trading_pairs:
                        df = self.get_cached_data(symbol, fold_start_str, fold_end_str)
                        if df is not None and len(df) > 100:
                            result = self.backtest_strategy_cv(df, individual, fold_name)
                            if result:
                                pair_results.append(result)
                    
                    # Média dos resultados do fold
                    if pair_results:
                        avg_fitness = np.mean([r['fitness'] for r in pair_results])
                        fold_results.append(avg_fitness)
                
                # Média dos folds do período
                if fold_results:
                    period_avg = np.mean(fold_results)
                    all_results.append(period_avg)
            
            # Fitness final é a média de todos os períodos
            if all_results:
                final_fitness = np.mean(all_results)
            else:
                final_fitness = 1000  # Penalização alta se não conseguir resultados
            
            return (final_fitness,)
            
        except Exception as e:
            logging.error(f"Erro na avaliação: {e}")
            return (1000,)  # Penalização alta
    
    def mutate_individual(self, individual):
        """Mutação personalizada"""
        try:
            # Mutação para cada gene
            if random.random() < 0.1:
                individual[0] = random.randint(20, 50)  # rsi_oversold
            if random.random() < 0.1:
                individual[1] = random.randint(50, 80)  # rsi_overbought
            if random.random() < 0.1:
                individual[2] = random.randint(10, 50)  # sma_short
            if random.random() < 0.1:
                individual[3] = random.randint(30, 100)  # sma_long
            if random.random() < 0.1:
                individual[4] = random.uniform(0.005, 0.03)  # stop_loss_pct
            if random.random() < 0.1:
                individual[5] = random.uniform(0.01, 0.08)  # take_profit_pct
            if random.random() < 0.1:
                individual[6] = random.randint(6, 48)  # max_hold_time
            if random.random() < 0.1:
                individual[7] = random.uniform(0.02, 0.10)  # trade_amount_pct
            if random.random() < 0.1:
                individual[8] = random.uniform(0.0005, 0.002)  # transaction_fee
            
            return (individual,)
            
        except Exception as e:
            logging.error(f"Erro na mutação: {e}")
            return (individual,)
    
    def run_optimization(self):
        """Executar otimização genética otimizada"""
        try:
            logging.info("INICIANDO OTIMIZACAO GENETICA v3.0 OTIMIZADA")
            logging.info("=" * 60)
            
            if not self.setup_binance():
                return
            
            start_time = time.time()
            
            # Criar população inicial
            pop = self.toolbox.population(n=self.population_size)
            
            # Estatísticas
            stats = tools.Statistics(lambda ind: ind.fitness.values)
            stats.register("avg", np.mean)
            stats.register("std", np.std)
            stats.register("min", np.min)
            stats.register("max", np.max)
            
            # Hall of Fame
            hof = tools.HallOfFame(5)
            
            # Executar algoritmo genético
            pop, logbook = algorithms.eaSimple(
                pop, self.toolbox,
                cxpb=self.crossover_prob,
                mutpb=self.mutation_prob,
                ngen=self.generations,
                stats=stats,
                halloffame=hof,
                verbose=True
            )
            
            end_time = time.time()
            optimization_time = end_time - start_time
            
            # Resultados
            best_individual = hof[0]
            best_fitness = best_individual.fitness.values[0]
            
            # Converter para parâmetros
            best_params = {
                'rsi_oversold': int(best_individual[0]),
                'rsi_overbought': int(best_individual[1]),
                'sma_short': int(best_individual[2]),
                'sma_long': int(best_individual[3]),
                'stop_loss_pct': float(best_individual[4]),
                'take_profit_pct': float(best_individual[5]),
                'max_hold_time': int(best_individual[6]),
                'trade_amount_pct': float(best_individual[7]),
                'transaction_fee': float(best_individual[8])
            }
            
            # Salvar resultados
            results = {
                'optimization_date': datetime.now().isoformat(),
                'best_fitness': best_fitness,
                'best_params': best_params,
                'generations': self.generations,
                'population_size': self.population_size,
                'k_folds': self.k_folds,
                'optimization_time': optimization_time,
                'hall_of_fame': []
            }
            
            # Adicionar Hall of Fame
            for i, individual in enumerate(hof):
                params = {
                    'rsi_oversold': int(individual[0]),
                    'rsi_overbought': int(individual[1]),
                    'sma_short': int(individual[2]),
                    'sma_long': int(individual[3]),
                    'stop_loss_pct': float(individual[4]),
                    'take_profit_pct': float(individual[5]),
                    'max_hold_time': int(individual[6]),
                    'trade_amount_pct': float(individual[7]),
                    'transaction_fee': float(individual[8])
                }
                
                results['hall_of_fame'].append({
                    'fitness': individual.fitness.values[0],
                    'params': params
                })
            
            # Salvar arquivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"genetic_optimization_v3_results_{timestamp}.json"
            filepath = self.results_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Log final
            logging.info("OTIMIZACAO CONCLUIDA!")
            logging.info(f"Tempo: {optimization_time:.1f} segundos")
            logging.info(f"MELHORES PARAMETROS ENCONTRADOS:")
            logging.info(f"   - Fitness: {best_fitness:.4f}")
            for key, value in best_params.items():
                logging.info(f"   - {key}: {value}")
            logging.info(f"Resultados salvos em: {filepath}")
            
            return results
            
        except Exception as e:
            logging.error(f"Erro na otimização: {e}")
            return None

def main():
    print("GENETIC OPTIMIZER v3.0 - OTIMIZADO")
    print("=" * 50)
    print("Otimização com cache e validação simplificada")
    print("=" * 50)
    
    optimizer = GeneticOptimizerV3()
    optimizer.run_optimization()

if __name__ == "__main__":
    main()

