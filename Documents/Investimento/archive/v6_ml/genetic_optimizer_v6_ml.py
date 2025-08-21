#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GENETIC OPTIMIZER v6.0 - MACHINE LEARNING & FEATURE ENGINEERING
===============================================================
Versão de vanguarda que substitui regras fixas por um modelo de ML (XGBoost)
para prever a direção do mercado. Otimiza os hiperparâmetros do modelo
e a estratégia de execução.
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
        logging.FileHandler('logs/genetic_optimizer_v6_ml.log', encoding='utf-8'),
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
        self.generations = 20 # Reduzido, pois o treino de ML é mais intensivo
        self.crossover_prob = 0.7
        self.mutation_prob = 0.3
        
        # --- ALTERADO v6.0: Otimiza hiperparâmetros de ML e da estratégia ---
        self.param_ranges = {
            'atr_period': (10, 30),
            'atr_stop_loss_multiplier': (1.0, 3.0),
            'atr_take_profit_multiplier': (2.0, 6.0),
            'hold_period': (12, 48), # Período para a "Triple Barrier"
            'entry_threshold': (0.6, 0.85), # Probabilidade mínima para entrar no trade
            'trade_amount_pct': (0.05, 0.20), # Percentual do capital por trade
            # Hiperparâmetros do XGBoost
            'n_estimators': (50, 200),
            'max_depth': (3, 7),
            'learning_rate': (0.01, 0.2),
        }
        
        self.trading_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'] # Reduzido para velocidade
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
        
        # --- ALTERADO v6.0: Geradores de genes para ML e estratégia ---
        self.toolbox.register("atr_period", random.randint, 10, 30)
        self.toolbox.register("atr_stop_loss_multiplier", random.uniform, 1.0, 3.0)
        self.toolbox.register("atr_take_profit_multiplier", random.uniform, 2.0, 6.0)
        self.toolbox.register("hold_period", random.randint, 12, 48)
        self.toolbox.register("entry_threshold", random.uniform, 0.6, 0.85)
        self.toolbox.register("trade_amount_pct", random.uniform, 0.05, 0.20)
        self.toolbox.register("n_estimators", random.randint, 50, 200)
        self.toolbox.register("max_depth", random.randint, 3, 7)
        self.toolbox.register("learning_rate", random.uniform, 0.01, 0.2)
        
        genes = (self.toolbox.atr_period, self.toolbox.atr_stop_loss_multiplier,
                 self.toolbox.atr_take_profit_multiplier, self.toolbox.hold_period,
                 self.toolbox.entry_threshold, self.toolbox.trade_amount_pct,
                 self.toolbox.n_estimators, self.toolbox.max_depth,
                 self.toolbox.learning_rate)

        self.toolbox.register("individual", tools.initCycle, creator.Individual, genes, n=1)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.evaluate_individual)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self.mutate_individual)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    # --- NOVO v6.0: Funções de Feature Engineering e Labeling ---
    def engineer_features(self, data):
        """Cria um conjunto rico de features para o modelo de ML."""
        df = data.copy()
        
        # Indicadores técnicos
        df['rsi'] = self.calculate_rsi(df['close'])
        df['sma_short'] = df['close'].rolling(window=20).mean()
        df['sma_long'] = df['close'].rolling(window=50).mean()
        df['atr'] = self.calculate_atr(df['high'], df['low'], df['close'])
        
        # Features baseadas em preço
        df['return_1h'] = df['close'].pct_change(1)
        df['return_24h'] = df['close'].pct_change(24)
        df['volatility_24h'] = df['return_1h'].rolling(window=24).std()
        
        # Features de momentum
        df['momentum_1h'] = df['close'] / df['close'].shift(1) - 1
        df['momentum_6h'] = df['close'] / df['close'].shift(6) - 1
        df['momentum_24h'] = df['close'] / df['close'].shift(24) - 1
        
        # Features de volume (se disponível)
        if 'volume' in df.columns:
            df['volume_ma'] = df['volume'].rolling(window=24).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma']
        else:
            df['volume_ratio'] = 1.0  # Valor padrão se não houver volume
        
        # Features de volatilidade
        df['high_low_ratio'] = (df['high'] - df['low']) / df['close']
        df['price_range'] = (df['high'] - df['low']) / df['close']
        
        # Features de tendência
        df['trend_short'] = (df['close'] - df['close'].shift(6)) / df['close'].shift(6)
        df['trend_long'] = (df['close'] - df['close'].shift(24)) / df['close'].shift(24)
        
        return df.dropna()

    def calculate_atr(self, high, low, close, period=14):
        """Calcula o Average True Range (ATR)."""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

    def get_triple_barrier_labels(self, data, params_dict):
        """Cria os labels (alvos) para o modelo de ML usando Triple Barrier Method."""
        df = data.copy()
        outcomes = pd.Series(index=df.index, dtype=int)
        
        sl_mult = params_dict['atr_stop_loss_multiplier']
        tp_mult = params_dict['atr_take_profit_multiplier']
        hold_period = params_dict['hold_period']

        for i in range(len(df) - hold_period):
            entry_price = df['close'].iloc[i]
            atr_at_entry = df['atr'].iloc[i]
            
            stop_loss_price = entry_price - (atr_at_entry * sl_mult)
            take_profit_price = entry_price + (atr_at_entry * tp_mult)
            
            path = df['close'].iloc[i+1 : i+1+hold_period]
            
            # Verifica se o take profit foi atingido primeiro
            hit_tp = path[path >= take_profit_price].first_valid_index()
            # Verifica se o stop loss foi atingido primeiro
            hit_sl = path[path <= stop_loss_price].first_valid_index()
            
            if hit_tp is not None and (hit_sl is None or hit_tp < hit_sl):
                outcomes.iloc[i] = 1 # Vitória
            elif hit_sl is not None and (hit_tp is None or hit_sl < hit_tp):
                outcomes.iloc[i] = -1 # Derrota
            else:
                outcomes.iloc[i] = 0 # Neutro (timeout)
                
        return outcomes

    def simulate_trading(self, symbol, params, data_override=None):
        """Simula o trading usando Machine Learning para prever direção do mercado."""
        try:
            if data_override is None: 
                return None
                
            data = data_override.copy()
            
            param_names = list(self.param_ranges.keys())
            params_dict = dict(zip(param_names, params))

            # 1. Feature Engineering
            df_features = self.engineer_features(data)
            
            # 2. Labeling com Triple Barrier Method
            labels = self.get_triple_barrier_labels(df_features, params_dict)
            df_features['label'] = labels.reindex(df_features.index)
            df_features = df_features.dropna()
            
            # Filtrar apenas por trades de compra (label=1) ou venda (label=-1)
            df_model_data = df_features[df_features['label'] != 0].copy()
            
            if len(df_model_data) < 100: # Dados insuficientes para treinar
                return {'profit': 0, 'trades': 0, 'wins': 0, 'returns': []}

            # 3. Preparar dados para ML
            feature_columns = ['rsi', 'sma_short', 'sma_long', 'atr', 'return_1h', 'return_24h', 
                             'volatility_24h', 'momentum_1h', 'momentum_6h', 'momentum_24h',
                             'volume_ratio', 'high_low_ratio', 'price_range', 'trend_short', 'trend_long']
            
            X = df_model_data[feature_columns]
            y = (df_model_data['label'] > 0).astype(int) # 1 para long, 0 para short

            # Dividir dados em treino e teste (simulando o tempo)
            split_point = int(len(X) * 0.7)
            X_train, X_test = X.iloc[:split_point], X.iloc[split_point:]
            y_train, y_test = y.iloc[:split_point], y.iloc[split_point:]

            # 4. Treinamento do Modelo XGBoost
            model = xgb.XGBClassifier(
                n_estimators=int(params_dict['n_estimators']),
                max_depth=int(params_dict['max_depth']),
                learning_rate=params_dict['learning_rate'],
                use_label_encoder=False,
                eval_metric='logloss',
                random_state=42
            )
            model.fit(X_train, y_train)
            
            # 5. Simulação de Backtest com o Modelo Treinado
            predictions_proba = model.predict_proba(X_test)[:, 1]
            
            initial_balance = 10000
            current_balance = initial_balance
            position = None
            trades = []
            
            test_data = df_features.loc[X_test.index]

            for i in range(len(test_data)):
                if position is None and predictions_proba[i] > params_dict['entry_threshold']:
                    row = test_data.iloc[i]
                    trade_amount = current_balance * params_dict['trade_amount_pct']
                    position = {
                        'entry_price': row.close,
                        'stop_loss': row.close - (row.atr * params_dict['atr_stop_loss_multiplier']),
                        'take_profit': row.close + (row.atr * params_dict['atr_take_profit_multiplier']),
                        'quantity': trade_amount / row.close,
                        'cost': trade_amount
                    }
                    current_balance -= trade_amount
                elif position is not None:
                    row = test_data.iloc[i]
                    if row.close <= position['stop_loss'] or row.close >= position['take_profit']:
                        profit = (row.close - position['entry_price']) * position['quantity']
                        current_balance += position['cost'] + profit
                        trades.append({'profit': profit})
                        position = None
            
            return {
                'profit': current_balance - initial_balance,
                'trades': len(trades),
                'wins': len([t for t in trades if t['profit'] > 0]),
                'returns': [t['profit'] for t in trades]
            }

        except Exception as e:
            logging.error(f"Erro no backtest ML para {symbol}: {e}")
            return None

    def evaluate_individual(self, individual, training_data):
        """Avalia um indivíduo usando Machine Learning."""
        try:
            params_dict = dict(zip(self.param_ranges.keys(), individual))
            
            # Validação lógica
            if params_dict['atr_stop_loss_multiplier'] >= params_dict['atr_take_profit_multiplier']:
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
            logging.error(f"Erro na avaliação ML: {e}")
            return (1000,)

    def run_optimization(self, training_data):
        """Executa a otimização genética com Machine Learning."""
        logging.info(f"🧬 Iniciando otimização v6.0 ML com {len(training_data)} pares")
        logging.info("🤖 Sistema: Machine Learning (XGBoost) + Feature Engineering")
        logging.info("🎯 Método: Triple Barrier Labeling")
        
        self.toolbox.register("evaluate", self.evaluate_individual, training_data=training_data)
        
        pop = self.toolbox.population(n=self.population_size)
        hof = tools.HallOfFame(1)
        
        algorithms.eaSimple(pop, self.toolbox, cxpb=self.crossover_prob, mutpb=self.mutation_prob,
                              ngen=self.generations, halloffame=hof, verbose=False)
        
        best_params_list = list(hof[0])
        best_params = dict(zip(self.param_ranges.keys(), best_params_list))
        
        logging.info(f"✅ Melhores parâmetros ML encontrados: {best_params}")
        return best_params

    # --- MÉTODOS AUXILIARES ---
    def calculate_rsi(self, prices, period=14):
        """Calcula RSI para uma série completa."""
        prices = pd.Series(prices)
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def mutate_individual(self, individual):
        """Mutação inteligente para parâmetros de ML."""
        individual = list(individual)
        
        # Mutação padrão
        for i in range(len(individual)):
            if random.random() < 0.1:  # 10% chance de mutação
                if i == 0:  # atr_period
                    individual[i] = random.randint(10, 30)
                elif i == 1:  # atr_stop_loss_multiplier
                    individual[i] = random.uniform(1.0, 3.0)
                elif i == 2:  # atr_take_profit_multiplier
                    individual[i] = random.uniform(2.0, 6.0)
                elif i == 3:  # hold_period
                    individual[i] = random.randint(12, 48)
                elif i == 4:  # entry_threshold
                    individual[i] = random.uniform(0.6, 0.85)
                elif i == 5:  # trade_amount_pct
                    individual[i] = random.uniform(0.05, 0.20)
                elif i == 6:  # n_estimators
                    individual[i] = random.randint(50, 200)
                elif i == 7:  # max_depth
                    individual[i] = random.randint(3, 7)
                elif i == 8:  # learning_rate
                    individual[i] = random.uniform(0.01, 0.2)
        
        # Correção de lógica inválida
        if individual[1] >= individual[2]:  # atr_stop >= atr_take
            individual[2] = individual[1] + random.uniform(0.5, 2.0)
        
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
    logging.info("🧬 GENETIC OPTIMIZER v6.0 - MACHINE LEARNING & FEATURE ENGINEERING")
    logging.info("=" * 70)
    logging.info("🤖 NOVA FUNCIONALIDADE: XGBoost para prever direção do mercado")
    logging.info("🎯 MÉTODO: Triple Barrier Labeling para targets de ML")
    logging.info("🔧 FEATURES: 15 indicadores técnicos e de preço")
    logging.info("🚀 SISTEMA: Transcende regras humanas - APRENDE PADRÕES!")
    
    optimizer = GeneticTradingOptimizer()
    
    # Teste básico
    logging.info("✅ Otimizador v6.0 ML inicializado com sucesso!")
    logging.info("🔧 Pronto para integração com Walk-Forward Optimization")
    logging.info("🤖 Sistema de Machine Learning ativo!")
    logging.info("🎯 QUINTA ESSÊNCIA: Trading quantitativo de vanguarda!")

if __name__ == "__main__":
    main()
