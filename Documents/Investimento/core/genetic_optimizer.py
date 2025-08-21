#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GENETIC OPTIMIZER v8.0 - PRODUÇÃO
===========================================================
Versão final e robusta com tratamento de casos extremos na função de
fitness, garantindo uma otimização estável e sem warnings.
"""

import os
import json
import time
import logging
import random
import pickle
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from deap import base, creator, tools, algorithms
import xgboost as xgb

# Carregar variáveis do .env
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/genetic_optimizer_v8_production.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class GeneticTradingOptimizer:
    def __init__(self):
        self.results_dir = Path('results')
        self.cache_dir = Path('cache')
        self.results_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.population_size = 30
        self.generations = 20
        self.crossover_prob = 0.7
        self.mutation_prob = 0.3
        
        self.param_ranges = {
            'atr_period': (10, 20),
            'atr_stop_loss_multiplier': (1.0, 2.5),
            'atr_take_profit_multiplier': (1.5, 4.0),
            'hold_period': (6, 24),
            'entry_threshold': (0.60, 0.75),
            'max_bet_size_pct': (0.1, 0.25),
            'n_estimators': (50, 150),
            'max_depth': (3, 5),
            'learning_rate': (0.01, 0.1),
        }
        
        self.trading_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
        self.data_cache = {}
        self.setup_deap()
        
    def setup_deap(self):
        if hasattr(creator, "FitnessMin"): del creator.FitnessMin
        if hasattr(creator, "Individual"): del creator.Individual
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
        self.toolbox = base.Toolbox()

        def generate_gene(param_range):
            return random.randint(*param_range) if isinstance(param_range[0], int) else random.uniform(*param_range)

        def create_individual_genes():
            return tuple(generate_gene(self.param_ranges[key]) for key in self.param_ranges)

        self.toolbox.register("individual_genes", create_individual_genes)
        self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.individual_genes)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.evaluate_individual)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self.mutate_individual)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def engineer_features(self, data):
        df = data.copy()
        df['rsi'] = self.calculate_rsi(df['close'])
        df['sma_short'] = df['close'].rolling(window=20).mean()
        df['sma_long'] = df['close'].rolling(window=50).mean()
        df['atr'] = self.calculate_atr(df['high'], df['low'], df['close'])
        df['macd'], df['macd_signal'], _ = self.calculate_macd(df['close'])
        df['bb_upper'], df['bb_lower'] = self.calculate_bollinger_bands(df['close'])
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['sma_short']
        if 'volume' in df.columns:
            df['obv'] = self.calculate_obv(df['close'], df['volume'])
        df['momentum_24h'] = df['close'].pct_change(24)
        df['volatility_24h'] = df['close'].pct_change(1).rolling(window=24).std()
        df['hour'] = df.index.hour
        return df.dropna()

    def get_triple_barrier_labels(self, data, params_dict):
        df = data.copy()
        outcomes = pd.Series(index=df.index, dtype=int)
        hold_period = int(params_dict['hold_period'])
        for i in range(len(df) - hold_period):
            entry_price = df['close'].iloc[i]
            atr = df['atr'].iloc[i]
            sl_price = entry_price - (atr * params_dict['atr_stop_loss_multiplier'])
            tp_price = entry_price + (atr * params_dict['atr_take_profit_multiplier'])
            path = df['close'].iloc[i+1 : i+1+hold_period]
            hit_tp = path[path >= tp_price].first_valid_index()
            hit_sl = path[path <= sl_price].first_valid_index()
            if hit_tp and (not hit_sl or hit_tp < hit_sl): outcomes.iloc[i] = 1
            elif hit_sl and (not hit_tp or hit_sl < hit_tp): outcomes.iloc[i] = -1
            else: outcomes.iloc[i] = 0
        return outcomes

    def simulate_trading(self, symbol, params, data_override=None):
        default_return = {'profit': 0, 'trades': 0, 'wins': 0, 'returns': [], 'max_drawdown': 1.0}
        try:
            if data_override is None: return default_return
            data = data_override.copy()
            param_names = list(self.param_ranges.keys())
            params_dict = dict(zip(param_names, params))
            df_features = self.engineer_features(data)
            df_features['label'] = self.get_triple_barrier_labels(df_features, params_dict)
            df_features.dropna(inplace=True)
            df_model_data = df_features[df_features['label'] != 0].copy()
            if len(df_model_data) < 50: return default_return
            feature_columns = [c for c in df_features.columns if c not in ['open','high','low','close','volume','label']]
            X = df_model_data[feature_columns].copy()
            y = (df_model_data['label'] > 0).astype(int)
            X.replace([np.inf, -np.inf], np.nan, inplace=True)
            X.fillna(0, inplace=True)
            X = X.astype(np.float32)
            split_point = int(len(X) * 0.7)
            if split_point < 30 or (len(X) - split_point) < 10: return default_return
            X_train, X_test, y_train, _ = X.iloc[:split_point], X.iloc[split_point:], y.iloc[:split_point], y.iloc[split_point:]
            if len(y_train.unique()) < 2: return default_return
            counts = y_train.value_counts()
            scale_pos_weight = counts.get(0, 0) / counts.get(1, 1)
            model = xgb.XGBClassifier(n_estimators=int(params_dict['n_estimators']), max_depth=int(params_dict['max_depth']), learning_rate=params_dict['learning_rate'], scale_pos_weight=scale_pos_weight, eval_metric='logloss', random_state=42, verbosity=0, use_label_encoder=False)
            model.fit(X_train, y_train)
            predictions_proba = model.predict_proba(X_test)[:, 1]
            initial_balance, current_balance, position, trades = 10000, 10000, None, []
            test_data = df_features.loc[X_test.index]
            equity_curve = [initial_balance]
            for i in range(len(test_data)):
                proba = predictions_proba[i]
                row = test_data.iloc[i]
                if position is None and proba > params_dict['entry_threshold']:
                    confidence = (proba - params_dict['entry_threshold']) / (1 - params_dict['entry_threshold'])
                    bet_size_pct = confidence * params_dict['max_bet_size_pct']
                    trade_amount = current_balance * bet_size_pct
                    position = {'entry_price': row.close, 'stop_loss': row.close - (row.atr * params_dict['atr_stop_loss_multiplier']), 'take_profit': row.close + (row.atr * params_dict['atr_take_profit_multiplier']), 'quantity': trade_amount / row.close, 'cost': trade_amount}
                    current_balance -= trade_amount
                elif position is not None and (row.close <= position['stop_loss'] or row.close >= position['take_profit']):
                    profit = (row.close - position['entry_price']) * position['quantity']
                    current_balance += position['cost'] + profit
                    trades.append({'profit': profit})
                    position = None
                equity_curve.append(current_balance + (position['quantity'] * row.close if position else 0))
            return {'profit': current_balance - initial_balance, 'trades': len(trades), 'wins': len([t for t in trades if t['profit'] > 0]), 'returns': [t['profit'] for t in trades], 'max_drawdown': self.calculate_max_drawdown(pd.Series(equity_curve))}
        except Exception as e:
            logging.error(f"Error in ML backtest for {symbol}: {e}")
            return default_return

    def evaluate_individual(self, individual, training_data):
        try:
            params_dict = dict(zip(self.param_ranges.keys(), individual))
            if params_dict['atr_stop_loss_multiplier'] >= params_dict['atr_take_profit_multiplier']: return (1000,)
            
            all_results = [res for res in (self.simulate_trading(s, individual, d) for s, d in training_data.items()) if res and res['trades'] > 0]
            if not all_results: return (1000,)

            # --- MELHORIA v8.0: TRATAMENTO DE CASOS EXTREMOS ---
            sharpe_ratios = [np.mean(r['returns']) / np.std(r['returns']) for r in all_results if len(r['returns']) > 1 and np.std(r['returns']) > 0]
            profit_factors = [self.calculate_profit_factor(r['returns']) for r in all_results]
            
            consistency_score = min(sharpe_ratios) if sharpe_ratios else -10
            
            # Lida com o caso de não haver trades perdedores (profit_factor = inf)
            valid_profit_factors = [pf for pf in profit_factors if pf != float('inf')]
            profitability_score = np.mean(valid_profit_factors) if valid_profit_factors else 3.0 # Recompensa alta se não houver perdas
            
            max_drawdowns = [r['max_drawdown'] for r in all_results]
            risk_score = -max(max_drawdowns) if max_drawdowns else -1.0
            
            fitness = (consistency_score * 0.5) + (profitability_score * 0.3) + (risk_score * 0.2)
            return (-fitness,)
            
        except Exception as e:
            logging.error(f"Error in ML evaluation: {e}")
            return (1000,)

    def run_optimization(self, training_data):
        logging.info(f"🧬 Iniciando otimização v8.0 ML")
        self.toolbox.register("evaluate", self.evaluate_individual, training_data=training_data)
        pop = self.toolbox.population(n=self.population_size)
        hof = tools.HallOfFame(1)
        algorithms.eaSimple(pop, self.toolbox, cxpb=self.crossover_prob, mutpb=self.mutation_prob, ngen=self.generations, halloffame=hof, verbose=False)
        return dict(zip(self.param_ranges.keys(), list(hof[0])))

    # --- MÉTODOS AUXILIARES ---
    def calculate_rsi(self, prices, period=14):
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        return 100 - (100 / (1 + (gain / loss)))
        
    def calculate_macd(self, prices, slow=26, fast=12, signal=9):
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd, signal_line, macd - signal_line

    def calculate_bollinger_bands(self, prices, window=20, num_std_dev=2):
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()
        return rolling_mean + (rolling_std * num_std_dev), rolling_mean - (rolling_std * num_std_dev)

    def calculate_obv(self, close, volume):
        return (np.sign(close.diff()) * volume).fillna(0).cumsum()

    def calculate_atr(self, high, low, close, period=14):
        tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    def mutate_individual(self, individual):
        param_keys = list(self.param_ranges.keys())
        for i, key in enumerate(param_keys):
            if random.random() < self.mutation_prob:
                prange = self.param_ranges[key]
                individual[i] = random.randint(*prange) if isinstance(prange[0], int) else random.uniform(*prange)
        params = dict(zip(param_keys, individual))
        if params['atr_stop_loss_multiplier'] >= params['atr_take_profit_multiplier']:
            new_tp = params['atr_stop_loss_multiplier'] + random.uniform(0.5, 1.5)
            individual[param_keys.index('atr_take_profit_multiplier')] = new_tp
        return individual,

    def calculate_max_drawdown(self, equity_curve):
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return drawdown.min() if not pd.isna(drawdown.min()) else 0

    def calculate_profit_factor(self, returns):
        if not returns: return 0
        gross_profit = sum(r for r in returns if r > 0)
        gross_loss = abs(sum(r for r in returns if r < 0))
        return gross_profit / gross_loss if gross_loss > 0 else float('inf')

def main():
    logging.info("🧬 GENETIC OPTIMIZER v8.0 - PRODUÇÃO")
    optimizer = GeneticTradingOptimizer()
    logging.info("✅ Otimizador v8.0 inicializado com sucesso!")

if __name__ == "__main__":
    main()
