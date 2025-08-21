#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf
import ccxt
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
        
        # Configuração otimizada baseada na análise - MAIS AGRESSIVA
        self.optimized_params = {
            'learning_rate': 0.001,   # Aumentado para aprendizado mais rápido
            'gamma': 0.95,            # Reduzido para foco no curto prazo
            'epsilon_start': 1.0,
            'epsilon_min': 0.01,      # Muito reduzido para mais execução
            'epsilon_decay': 0.999,   # Decaimento mais rápido
            'batch_size': 32,         # Reduzido para mais agilidade
            'memory_size': 10000,     # Reduzido para foco
            'episodes_per_pair': 100, # Muito aumentado para mais oportunidades
            'lookback_window': 60     # Janela maior para análise (CORRETO)
        }
        
        # Pares de trading expandidos (formato Binance)
        self.trading_pairs = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
            'ADA/USDT', 'DOGE/USDT', 'TRX/USDT', 'LINK/USDT', 'AVAX/USDT',
            'MATIC/USDT', 'DOT/USDT', 'LTC/USDT', 'ATOM/USDT', 'UNI/USDT',
            'NEAR/USDT', 'FTM/USDT', 'ALGO/USDT', 'VET/USDT', 'ICP/USDT'
        ]
        
        # Mapeamento para Yahoo Finance (fallback)
        self.yf_pairs = [
            'BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'XRP-USD',
            'ADA-USD', 'DOGE-USD', 'TRX-USD', 'LINK-USD', 'AVAX-USD',
            'MATIC-USD', 'DOT-USD', 'LTC-USD', 'ATOM-USD', 'UNI-USD',
            'NEAR-USD', 'FTM-USD', 'ALGO-USD', 'VET-USD', 'ICP-USD'
        ]
        
        self.total_workers = 4
        self.worker_results = {}
        self.global_metrics = []
        
    def get_binance_data(self, symbol, timeframe='1h', limit=1000):
        """Obtém dados da Binance via CCXT"""
        try:
            exchange = ccxt.binance({
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'
                }
            })
            
            # Converter símbolo para formato Binance
            binance_symbol = symbol.replace('-', '/')
            
            # Obter dados OHLCV
            ohlcv = exchange.fetch_ohlcv(binance_symbol, timeframe, limit=limit)
            
            if ohlcv:
                # Converter para DataFrame
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                return df
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter dados da Binance para {symbol}: {e}")
            return None
    
    def prepare_training_data(self):
        """Prepara dados de treinamento para todos os pares"""
        logger.info("📊 Preparando dados de treinamento estendido...")
        
        results = []
        for i, symbol in enumerate(self.trading_pairs):
            try:
                logger.info(f"Baixando {symbol}...")
                
                # Tentar Binance primeiro
                data = self.get_binance_data(symbol)
                
                # Fallback para Yahoo Finance se Binance falhar
                if data is None or len(data) < 100:
                    logger.info(f"Fallback para Yahoo Finance: {self.yf_pairs[i]}")
                    ticker = yf.Ticker(self.yf_pairs[i])
                    data = ticker.history(period='1y', interval='1h')
                
                if not data.empty and len(data) > 100:
                    # Salvar dados
                    symbol_clean = symbol.replace('/', '_').replace('-', '_')
                    data_file = self.data_dir / f"{symbol_clean}_extended.csv"
                    data.to_csv(data_file)
                    
                    result = {
                        'symbol': symbol,
                        'data_points': len(data),
                        'last_price': data['close'].iloc[-1] if 'close' in data.columns else data['Close'].iloc[-1],
                        'file': str(data_file),
                        'status': 'success'
                    }
                    logger.info(f"✅ {symbol}: {len(data)} pontos, ${result['last_price']:.2f}")
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
                
                # Verificar se o resultado tem as chaves necessárias
                if 'profit' in pair_result and 'trades' in pair_result:
                    worker_results['total_profit'] += pair_result['profit']
                    worker_results['total_trades'] += pair_result['trades']
                else:
                    logger.warning(f"⚠️ Resultado incompleto para {symbol}: {pair_result}")
                
                # Atualizar status
                worker_results['status'] = f'training ({idx}/{total_pairs})'
                with open(status_file, 'w') as f:
                    json.dump(worker_results, f, indent=2)
                
                if 'profit' in pair_result and 'win_rate' in pair_result:
                    logger.info(f"✅ Worker {worker_id} - {symbol}: Profit=${pair_result['profit']:.2f}, Win Rate={pair_result['win_rate']:.1f}%")
                else:
                    logger.info(f"⚠️ Worker {worker_id} - {symbol}: {pair_result.get('status', 'unknown')}")
                
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
        """Simula backtesting realista sem lookahead bias"""
        # Carregar dados
        data_file = self.data_dir / f"{symbol.replace('-', '_')}_extended.csv"
        if not data_file.exists():
            return {
                'symbol': symbol, 
                'status': 'no_data',
                'profit': 0,
                'trades': 0,
                'wins': 0,
                'win_rate': 0,
                'episodes': 0,
                'avg_profit_per_trade': 0,
                'transaction_fees': 0,
                'stop_loss_pct': 0,
                'take_profit_pct': 0
            }
        
        data = pd.read_csv(data_file, index_col=0, parse_dates=True)
        
        # Normalizar nomes de colunas
        if 'close' in data.columns:
            data['Close'] = data['close']
        if 'high' in data.columns:
            data['High'] = data['high']
        if 'low' in data.columns:
            data['Low'] = data['low']
        if 'volume' in data.columns:
            data['Volume'] = data['volume']
        
        # Parâmetros de trading realistas
        transaction_fee = 0.001  # 0.1% por operação (Binance)
        stop_loss_pct = 0.02     # 2% stop loss
        take_profit_pct = 0.03   # 3% take profit
        max_hold_time = 24       # Máximo 24 horas por trade
        
        # Simular backtesting com parâmetros otimizados
        episodes = params['episodes_per_pair']
        total_profit = 0
        total_trades = 0
        total_wins = 0
        returns_list = []  # Lista para armazenar retornos reais
        
        for episode in range(episodes):
            # Simular trading com parâmetros otimizados
            initial_balance = 1000
            current_balance = initial_balance
            trades_this_episode = 0
            wins_this_episode = 0
            
            # Estado da posição atual
            position = {
                'type': None,        # 'long' ou 'short'
                'entry_price': 0,    # Preço de entrada
                'entry_time': 0,     # Índice de entrada
                'amount': 0,         # Quantidade
                'stop_loss': 0,      # Preço do stop loss
                'take_profit': 0     # Preço do take profit
            }
            
            # Simular trades baseado nos dados históricos
            for i in range(100, len(data) - 1):
                current_price = data['Close'].iloc[i]
                current_time = i
                
                # Análise técnica (apenas dados disponíveis até o momento i)
                close_prices = data['Close'].iloc[i-params['lookback_window']:i+1]
                rsi = self.calculate_rsi(close_prices)
                
                # Calcular médias móveis
                sma_20 = close_prices.rolling(window=20).mean().iloc[-1]
                sma_50 = close_prices.rolling(window=50).mean().iloc[-1]
                
                # Verificar se há posição aberta
                if position['type'] is not None:
                    # Verificar condições de saída
                    exit_trade = False
                    exit_price = current_price
                    exit_reason = ""
                    
                    # Stop loss
                    if position['type'] == 'long' and current_price <= position['stop_loss']:
                        exit_trade = True
                        exit_reason = "stop_loss"
                    elif position['type'] == 'short' and current_price >= position['stop_loss']:
                        exit_trade = True
                        exit_reason = "stop_loss"
                    
                    # Take profit
                    elif position['type'] == 'long' and current_price >= position['take_profit']:
                        exit_trade = True
                        exit_reason = "take_profit"
                    elif position['type'] == 'short' and current_price <= position['take_profit']:
                        exit_trade = True
                        exit_reason = "take_profit"
                    
                    # Timeout
                    elif current_time - position['entry_time'] >= max_hold_time:
                        exit_trade = True
                        exit_reason = "timeout"
                    
                    # Condição de RSI oposta (MAIS FLEXÍVEL)
                    elif (position['type'] == 'long' and rsi > 75) or (position['type'] == 'short' and rsi < 25):
                        exit_trade = True
                        exit_reason = "rsi_signal"
                    
                    if exit_trade:
                        # Calcular lucro/prejuízo realista
                        if position['type'] == 'long':
                            price_change = (exit_price - position['entry_price']) / position['entry_price']
                        else:  # short
                            price_change = (position['entry_price'] - exit_price) / position['entry_price']
                        
                        # Aplicar taxas de transação (entrada + saída)
                        net_change = price_change - (2 * transaction_fee)
                        profit = position['amount'] * net_change
                        
                        current_balance += profit
                        trades_this_episode += 1
                        returns_list.append(profit)  # Adicionar retorno real
                        if profit > 0:
                            wins_this_episode += 1
                        
                        logger.debug(f"Trade fechado: {position['type']} {symbol} - {exit_reason} - Profit: ${profit:.2f}")
                        
                        # Resetar posição
                        position = {'type': None, 'entry_price': 0, 'entry_time': 0, 'amount': 0, 'stop_loss': 0, 'take_profit': 0}
                
                # Verificar condições de entrada (apenas se não há posição aberta)
                if position['type'] is None:
                    # Condições de entrada mais robustas
                    trend_bullish = sma_20 > sma_50
                    trend_bearish = sma_20 < sma_50
                    
                    # DEBUG: Logar condições a cada 100 candles
                    if i % 100 == 0:
                        logger.debug(f"DEBUG {symbol} - RSI: {rsi:.1f}, SMA20: {sma_20:.4f}, SMA50: {sma_50:.4f}, Trend: {'BULL' if trend_bullish else 'BEAR'}")
                    
                    # ESTRATÉGIA SIMPLIFICADA COM RSI + TENDÊNCIA
                    # Long: RSI baixo + tendência de alta
                    if rsi < 35 and trend_bullish and np.random.random() > 0.1:  # 90% de chance
                        trade_amount = current_balance * 0.1
                        position = {
                            'type': 'long',
                            'entry_price': current_price,
                            'entry_time': current_time,
                            'amount': trade_amount,
                            'stop_loss': current_price * (1 - stop_loss_pct),
                            'take_profit': current_price * (1 + take_profit_pct)
                        }
                        current_balance -= trade_amount
                        logger.info(f"🚀 LONG ENTRY: {symbol} @ ${current_price:.4f} (RSI: {rsi:.1f})")
                    
                    # Short: RSI alto + tendência de baixa
                    elif rsi > 65 and trend_bearish and np.random.random() > 0.1:  # 90% de chance
                        trade_amount = current_balance * 0.1
                        position = {
                            'type': 'short',
                            'entry_price': current_price,
                            'entry_time': current_time,
                            'amount': trade_amount,
                            'stop_loss': current_price * (1 + stop_loss_pct),
                            'take_profit': current_price * (1 - take_profit_pct)
                        }
                        current_balance -= trade_amount
                        logger.info(f"🔻 SHORT ENTRY: {symbol} @ ${current_price:.4f} (RSI: {rsi:.1f})")
                    
                    # CONDIÇÕES ALTERNATIVAS (independente da tendência)
                    # Long: RSI muito baixo
                    elif rsi < 25 and np.random.random() > 0.2:  # 80% de chance
                        trade_amount = current_balance * 0.05  # Trade menor
                        position = {
                            'type': 'long',
                            'entry_price': current_price,
                            'entry_time': current_time,
                            'amount': trade_amount,
                            'stop_loss': current_price * (1 - stop_loss_pct),
                            'take_profit': current_price * (1 + take_profit_pct)
                        }
                        current_balance -= trade_amount
                        logger.info(f"🚀 LONG ENTRY (RSI baixo): {symbol} @ ${current_price:.4f} (RSI: {rsi:.1f})")
                    
                    # Short: RSI muito alto
                    elif rsi > 75 and np.random.random() > 0.2:  # 80% de chance
                        trade_amount = current_balance * 0.05  # Trade menor
                        position = {
                            'type': 'short',
                            'entry_price': current_price,
                            'entry_time': current_time,
                            'amount': trade_amount,
                            'stop_loss': current_price * (1 + stop_loss_pct),
                            'take_profit': current_price * (1 - take_profit_pct)
                        }
                        current_balance -= trade_amount
                        logger.info(f"🔻 SHORT ENTRY (RSI alto): {symbol} @ ${current_price:.4f} (RSI: {rsi:.1f})")
            
            # Fechar posição final se ainda estiver aberta
            if position['type'] is not None:
                final_price = data['Close'].iloc[-1]
                if position['type'] == 'long':
                    price_change = (final_price - position['entry_price']) / position['entry_price']
                else:
                    price_change = (position['entry_price'] - final_price) / position['entry_price']
                
                net_change = price_change - (2 * transaction_fee)
                profit = position['amount'] * net_change
                current_balance += profit + position['amount']  # Retornar capital reservado
                trades_this_episode += 1
                returns_list.append(profit)  # Adicionar retorno real
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
            'avg_profit_per_trade': total_profit / total_trades if total_trades > 0 else 0,
            'transaction_fees': transaction_fee,
            'stop_loss_pct': stop_loss_pct,
            'take_profit_pct': take_profit_pct,
            'returns': returns_list,  # Retornos reais para métricas precisas
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
    
    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.02):
        """Calcula Sharpe Ratio"""
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - risk_free_rate/252  # Assumindo 252 dias úteis
        if excess_returns.std() == 0:
            return 0
        
        return excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    
    def calculate_max_drawdown(self, equity_curve):
        """Calcula Maximum Drawdown"""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return drawdown.min()
    
    def calculate_profit_factor(self, returns):
        """Calcula Profit Factor baseado em retornos reais"""
        if not returns:
            return float('inf')
        
        gross_profit = sum(r for r in returns if r > 0)
        gross_loss = abs(sum(r for r in returns if r < 0))
        
        return gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
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
        
        # Calcular métricas avançadas
        avg_profit_per_trade = total_profit / total_trades if total_trades > 0 else 0
        
        # Coletar todos os retornos reais para análise
        all_returns = []
        equity_curve = [1000]  # Começa com capital inicial de $1000
        
        for worker_result in self.worker_results.values():
            for pair_result in worker_result['pairs_trained']:
                if pair_result.get('status') == 'success' and 'returns' in pair_result:
                    all_returns.extend(pair_result['returns'])
                    # Construir curva de capital
                    for pnl in pair_result['returns']:
                        equity_curve.append(equity_curve[-1] + pnl)
        
        # Calcular métricas com dados reais
        if all_returns:
            equity_series = pd.Series(equity_curve)
            returns_series = equity_series.pct_change().dropna()  # Retornos percentuais reais
            sharpe_ratio = self.calculate_sharpe_ratio(returns_series)
            max_drawdown = self.calculate_max_drawdown(equity_series)
        else:
            sharpe_ratio = 0
            max_drawdown = 0
        
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
                'average_profit_per_trade': avg_profit_per_trade,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'profit_factor': self.calculate_profit_factor(all_returns) if all_returns else float('inf')
            },
            'worker_analysis': worker_analysis,
            'optimization_params': self.optimized_params,
            'backtesting_params': {
                'transaction_fee': 0.001,
                'stop_loss_pct': 0.02,
                'take_profit_pct': 0.03,
                'max_hold_time': 24
            },
            'recommendations': self.generate_recommendations(total_profit, overall_win_rate, sharpe_ratio)
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
        logger.info(f"   - Lucro médio por trade: ${avg_profit_per_trade:.2f}")
        logger.info(f"   - Sharpe Ratio: {sharpe_ratio:.2f}")
        logger.info(f"   - Max Drawdown: {max_drawdown:.2%}")
        logger.info(f"   - Profit Factor: {final_report['overall_metrics']['profit_factor']:.2f}")
        
        # Recomendações
        logger.info("🎯 RECOMENDAÇÕES:")
        for rec in final_report['recommendations']:
            logger.info(f"   - {rec}")
    
    def generate_recommendations(self, total_profit, win_rate, sharpe_ratio):
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Análise de lucratividade
        if total_profit > 1000:
            recommendations.append("✅ Sistema muito lucrativo - Considere aumentar capital")
        elif total_profit > 500:
            recommendations.append("✅ Sistema lucrativo - Continue monitorando")
        elif total_profit > 0:
            recommendations.append("⚠️ Sistema marginalmente lucrativo - Otimize parâmetros")
        else:
            recommendations.append("❌ Sistema não lucrativo - Revisar estratégia")
        
        # Análise de win rate
        if win_rate > 70:
            recommendations.append("✅ Win rate excelente - Sistema muito confiável")
        elif win_rate > 60:
            recommendations.append("✅ Win rate bom - Sistema confiável")
        elif win_rate > 50:
            recommendations.append("⚠️ Win rate aceitável - Melhorar precisão")
        else:
            recommendations.append("❌ Win rate baixo - Revisar estratégia")
        
        # Análise de Sharpe Ratio
        if sharpe_ratio > 2.0:
            recommendations.append("✅ Sharpe Ratio excelente - Retorno ajustado ao risco muito bom")
        elif sharpe_ratio > 1.5:
            recommendations.append("✅ Sharpe Ratio bom - Retorno ajustado ao risco adequado")
        elif sharpe_ratio > 1.0:
            recommendations.append("⚠️ Sharpe Ratio aceitável - Melhorar eficiência de risco")
        else:
            recommendations.append("❌ Sharpe Ratio baixo - Revisar gerenciamento de risco")
        
        # Recomendação geral
        if total_profit > 0 and win_rate > 60 and sharpe_ratio > 1.5:
            recommendations.append("🚀 Sistema pronto para trading real - Todas as métricas são favoráveis")
        elif total_profit > 0 and win_rate > 50:
            recommendations.append("🔧 Sistema promissor - Otimizar parâmetros de risco")
        else:
            recommendations.append("🔧 Sistema precisa de mais otimização - Focar em estratégia e gerenciamento de risco")
        
        return recommendations

if __name__ == "__main__":
    # Executar treinamento estendido
    trainer = ExtendedWorkerTraining()
    trainer.run_extended_training()
