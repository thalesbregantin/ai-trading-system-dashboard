#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ccxt
import time
import json
import os
import threading
from datetime import datetime
from pathlib import Path
import subprocess
import schedule
import numpy as np
import pandas as pd
import math
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Configuração da Binance (do .env)
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

class ParallelTradingSystem:
    def __init__(self):
        # Inicialização básica
        self.exchange = None
        self.initial_balance = 0
        self.current_balance = 0
        self.training_active = False
        self.trading_active = False
        
        # Cache dinâmico para regras da Binance
        self.exchange_rules_cache = {}
        self.cache_last_update = None
        self.cache_update_interval = 3600  # 1 hora
        
        # Configurar pares de trading
        self.trading_pairs = [
            'DOGE/USDT',   # Dogecoin - $0.21
            'ADA/USDT',    # Cardano - $0.87
            'XRP/USDT',    # Ripple - $2.93
            'DOT/USDT',    # Polkadot - $3.79
            'LINK/USDT',   # Chainlink - $24.04
            'UNI/USDT',    # Uniswap - $12.50
            'MATIC/USDT',  # Polygon - $0.85
            'AVAX/USDT',   # Avalanche - $35.00
            'ATOM/USDT',   # Cosmos - $8.50
            'LTC/USDT',    # Litecoin - $114.04
            'BCH/USDT',    # Bitcoin Cash - $450.00
            'ETC/USDT',    # Ethereum Classic - $20.85
            'FIL/USDT',    # Filecoin - $2.38
            'VET/USDT',    # VeChain - $0.03
            'ICP/USDT',    # Internet Computer - $12.00
            'NEAR/USDT',   # NEAR Protocol - $5.50
            'ALGO/USDT',   # Algorand - $0.24
            'THETA/USDT',  # Theta - $1.80
            'TRX/USDT',    # TRON - $0.12
            'XLM/USDT',    # Stellar - $0.15
            'IOTA/USDT',   # IOTA - $0.20
            'NEO/USDT',    # NEO - $5.89
            'QTUM/USDT',   # Qtum - $3.20
        ]
        
        # PARÂMETROS OTIMIZADOS BASEADOS NA DOCUMENTAÇÃO BINANCE
        self.parameters = {
            'min_trade_value_usdt': 15.0,     # Mínimo $15 por trade (BINANCE MIN + MARGEM)
            'max_trade_value_usdt': 30.0,     # Máximo $30 por trade (OTIMIZADO)
            'trade_percentage': 0.30,         # 30% do saldo por trade (MAIS AGRESSIVO)
            'pump_threshold_1min': 0.5,       # Pump >0.5% em 1min
            'pump_threshold_5min': 0.3,       # Pump >0.3% em 5min
            'momentum_threshold': 0.2,        # Momentum 0.2%
            'take_profit_percentage': 2.5,    # Take profit 2.5%
            'stop_loss_percentage': 1.5,      # Stop loss 1.5%
            'max_hold_time_minutes': 8,       # Máximo 8min por trade
            'max_active_trades': 3,           # Máximo 3 trades ativos
            'max_trades_per_cycle': 2,        # Máximo 2 trades por ciclo
            'cycle_interval_minutes': 30,     # Ciclo a cada 30min (como sugerido)
            'sma_short_period': 20,           # SMA 20 períodos
            'sma_long_period': 50,            # SMA 50 períodos
            'rsi_period': 14,                 # RSI 14 períodos
            'rsi_overbought': 70,             # RSI sobrecomprado
            'rsi_oversold': 30                # RSI sobrevendido
        }
        
        # Configurar diretórios
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
        
        # Cache será inicializado após setup_binance()
        
    def setup_firebase(self):
        """Configurar Firebase se disponível"""
        try:
            # Tentar importar do caminho local primeiro
            import sys
            sys.path.append('ai_trading_system')
            
            try:
                from dashboard.firebase_config import firebase_manager
                self.firebase_manager = firebase_manager
                print("✅ Firebase configurado!")
            except ImportError:
                # Se não encontrar, tentar caminho alternativo
                try:
                    from ai_trading_system.dashboard.firebase_config import firebase_manager
                    self.firebase_manager = firebase_manager
                    print("✅ Firebase configurado!")
                except ImportError:
                    print("⚠️ Firebase não disponível - módulo não encontrado")
                    self.firebase_manager = None
        except Exception as e:
            print(f"⚠️ Firebase não disponível: {e}")
            self.firebase_manager = None
            self.firebase_manager = None
    
    def initialize_exchange_rules_cache(self):
        """Inicializar cache de regras da exchange"""
        try:
            print("🔄 Inicializando cache de regras da Binance...")
            self.update_exchange_rules_cache()
            print(f"✅ Cache inicializado com {len(self.exchange_rules_cache)} símbolos")
        except Exception as e:
            print(f"❌ Erro ao inicializar cache: {e}")
    
    def update_exchange_rules_cache(self):
        """Atualizar cache de regras da exchange"""
        try:
            # Verificar se precisa atualizar
            if (self.cache_last_update and 
                time.time() - self.cache_last_update < self.cache_update_interval):
                return
            
            print("🔄 Atualizando cache de regras da Binance...")
            
            # Obter informações de todos os símbolos de interesse
            for symbol in self.trading_pairs:
                try:
                    market = self.exchange.market(symbol)
                    if not market:
                        continue
                    
                    # Extrair filtros específicos
                    filters = {}
                    for filter_obj in market.get('info', {}).get('filters', []):
                        filter_type = filter_obj.get('filterType')
                        if filter_type in ['MIN_NOTIONAL', 'LOT_SIZE', 'PRICE_FILTER']:
                            filters[filter_type] = filter_obj
                    
                    # Armazenar no cache
                    self.exchange_rules_cache[symbol] = {
                        'symbol': symbol,
                        'active': market.get('active', False),
                        'baseAsset': market.get('base'),
                        'quoteAsset': market.get('quote'),
                        'precision': market.get('precision', {}),
                        'limits': market.get('limits', {}),
                        'filters': filters
                    }
                    
                except Exception as e:
                    print(f"⚠️ Erro ao processar {symbol}: {e}")
                    continue
            
            self.cache_last_update = time.time()
            print(f"✅ Cache atualizado: {len(self.exchange_rules_cache)} símbolos")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar cache: {e}")
    
    def get_binance_limits(self, symbol):
        """Obter limites específicos da Binance para um símbolo (COM CACHE)"""
        try:
            # Atualizar cache se necessário
            self.update_exchange_rules_cache()
            
            # Obter do cache
            if symbol not in self.exchange_rules_cache:
                print(f"❌ Símbolo {symbol} não encontrado no cache")
                return None
            
            rules = self.exchange_rules_cache[symbol]
            
            # Extrair filtros específicos
            min_notional = 10.0  # Padrão
            min_qty = 0
            max_qty = float('inf')
            step_size = 0.000001
            tick_size = 0.01
            
            # MIN_NOTIONAL
            if 'MIN_NOTIONAL' in rules['filters']:
                min_notional = float(rules['filters']['MIN_NOTIONAL'].get('minNotional', 10.0))
            
            # LOT_SIZE
            if 'LOT_SIZE' in rules['filters']:
                lot_size = rules['filters']['LOT_SIZE']
                min_qty = float(lot_size.get('minQty', 0))
                max_qty = float(lot_size.get('maxQty', float('inf')))
                step_size = float(lot_size.get('stepSize', 0.000001))
            
            # PRICE_FILTER
            if 'PRICE_FILTER' in rules['filters']:
                price_filter = rules['filters']['PRICE_FILTER']
                tick_size = float(price_filter.get('tickSize', 0.01))
            
            return {
                'symbol': symbol,
                'min_notional': min_notional,
                'min_qty': min_qty,
                'max_qty': max_qty,
                'step_size': step_size,
                'tick_size': tick_size,
                'price_precision': rules['precision'].get('price', 8),
                'amount_precision': rules['precision'].get('amount', 8),
                'active': rules['active']
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter limites para {symbol}: {e}")
            return None
    
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
            
            balance = self.exchange.fetch_balance()
            total_usdt = 0
            
            # USDT direto
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            total_usdt += usdt_balance
            
            # Verificar outras moedas
            for symbol in ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI', 'FET', 'BAND', 'AAVE', 'MKR', 'COMP', 'SNX', 'SUSHI', '1INCH', 'ATOM', 'LTC', 'BCH', 'ETC', 'FIL', 'VET', 'THETA', 'TRX']:
                amount = balance.get(symbol, {}).get('free', 0)
                if amount > 0:
                    try:
                        ticker = self.exchange.fetch_ticker(f'{symbol}/USDT')
                        crypto_value = amount * ticker['last']
                        total_usdt += crypto_value
                        print(f"💰 {symbol}: {amount:.6f} = ${crypto_value:.2f}")
                    except:
                        print(f"💰 {symbol}: {amount:.6f} (valor não calculado)")
            
            self.initial_balance = total_usdt
            self.current_balance = total_usdt
            
            print(f"✅ Conexão estabelecida!")
            print(f"💰 Saldo total: ${self.initial_balance:.2f}")
            
            # Inicializar cache de regras após conexão estabelecida
            self.initialize_exchange_rules_cache()
            
            return True
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def get_balance(self):
        """Obter saldo atual"""
        try:
            balance = self.exchange.fetch_balance()
            total_usdt = 0
            
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            total_usdt += usdt_balance
            
            for symbol in ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI', 'FET', 'BAND', 'AAVE', 'MKR', 'COMP', 'SNX', 'SUSHI', '1INCH', 'ATOM', 'LTC', 'BCH', 'ETC', 'FIL', 'VET', 'THETA', 'TRX']:
                amount = balance.get(symbol, {}).get('free', 0)
                if amount > 0:
                    try:
                        ticker = self.exchange.fetch_ticker(f'{symbol}/USDT')
                        crypto_value = amount * ticker['last']
                        total_usdt += crypto_value
                    except:
                        pass
            
            return total_usdt
        except Exception as e:
            print(f"❌ Erro ao obter saldo: {e}")
            return 0
    
    def calculate_trade_value(self, total_usdt):
        """Calcular valor inteligente do trade"""
        try:
            base_value = total_usdt * self.parameters['trade_percentage']
            trade_value = max(self.parameters['min_trade_value_usdt'], 
                            min(base_value, self.parameters['max_trade_value_usdt']))
            
            if trade_value > total_usdt * 0.7:
                trade_value = total_usdt * 0.7
            
            return trade_value
        except Exception as e:
            print(f"❌ Erro ao calcular valor do trade: {e}")
            return self.parameters['min_trade_value_usdt']
    
    def check_pair_availability(self, symbol):
        """Verificar se o par está realmente disponível baseado na documentação Binance"""
        try:
            # Obter informações detalhadas do mercado
            market = self.exchange.market(symbol)
            if not market:
                return False
            
            # Verificar se o mercado está ativo
            if not market.get('active', False):
                return False
            
            # Obter ticker para preço atual
            ticker = self.exchange.fetch_ticker(symbol)
            if not ticker or ticker.get('last') is None:
                return False
            
            current_price = ticker['last']
            min_trade = self.parameters['min_trade_value_usdt']
            
            # Verificar limites da Binance baseado na documentação
            limits = market.get('limits', {})
            
            # 1. Verificar MIN_NOTIONAL (valor mínimo da ordem)
            min_notional = limits.get('cost', {}).get('min', 10.0)  # Padrão $10
            if min_trade < min_notional:
                print(f"   ⚠️ {symbol}: Trade ${min_trade} < MIN_NOTIONAL ${min_notional}")
                return False
            
            # 2. Verificar LOT_SIZE (quantidade mínima)
            min_qty = limits.get('amount', {}).get('min', 0)
            if min_qty > 0:
                # Calcular se conseguimos comprar quantidade mínima
                possible_qty = min_trade / current_price
                if possible_qty < min_qty:
                    print(f"   ⚠️ {symbol}: Qty {possible_qty:.6f} < MIN_QTY {min_qty}")
                    return False
            
            # 3. Verificar se o preço não é excessivamente alto
            if current_price > min_trade * 50:  # Se preço > $750, pulamos
                print(f"   ⚠️ {symbol}: Preço ${current_price:.2f} muito alto para trade ${min_trade}")
                return False
            
            # 4. Verificar volume 24h (liquidez)
            volume_24h = ticker.get('quoteVolume', 0)
            if volume_24h < 1000000:  # Menos de $1M em volume
                print(f"   ⚠️ {symbol}: Volume baixo ${volume_24h:,.0f}")
                return False
            
            return True
            
        except Exception as e:
            print(f"   ❌ {symbol}: Erro na verificação - {e}")
            return False
    
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
    
    def analyze_market_context(self, symbol):
        """Analisar contexto de mercado (tendência, suporte/resistência)"""
        try:
            # Obter dados históricos
            ohlcv_1h = self.exchange.fetch_ohlcv(symbol, '1h', limit=100)
            ohlcv_15m = self.exchange.fetch_ohlcv(symbol, '15m', limit=50)
            
            if len(ohlcv_1h) < 50 or len(ohlcv_15m) < 20:
                return None
            
            # Extrair preços
            prices_1h = [candle[4] for candle in ohlcv_1h]
            prices_15m = [candle[4] for candle in ohlcv_15m]
            
            # Calcular indicadores
            sma_20 = self.calculate_sma(prices_1h, 20)
            sma_50 = self.calculate_sma(prices_1h, 50)
            rsi = self.calculate_rsi(prices_15m, 14)
            
            current_price = prices_1h[-1]
            
            # Determinar tendência
            if sma_20 and sma_50:
                if sma_20 > sma_50 and current_price > sma_20:
                    trend = "BULLISH"
                elif sma_20 < sma_50 and current_price < sma_20:
                    trend = "BEARISH"
                else:
                    trend = "SIDEWAYS"
            else:
                trend = "UNKNOWN"
            
            # Análise de RSI
            rsi_status = "NEUTRAL"
            if rsi:
                if rsi > self.parameters['rsi_overbought']:
                    rsi_status = "OVERBOUGHT"
                elif rsi < self.parameters['rsi_oversold']:
                    rsi_status = "OVERSOLD"
            
            return {
                'trend': trend,
                'rsi': rsi,
                'rsi_status': rsi_status,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'current_price': current_price
            }
            
        except Exception as e:
            return None
    
    def detect_pump(self, symbol):
        """Detectar pump com análise técnica completa"""
        try:
            # Verificar disponibilidade primeiro
            if not self.check_pair_availability(symbol):
                return None
            
            # Análise de contexto de mercado
            context = self.analyze_market_context(symbol)
            if not context:
                return None
            
            ohlcv_1m = self.exchange.fetch_ohlcv(symbol, '1m', limit=5)
            ohlcv_5m = self.exchange.fetch_ohlcv(symbol, '5m', limit=5)
            
            if len(ohlcv_1m) < 2 or len(ohlcv_5m) < 2:
                return None
            
            current_price = ohlcv_1m[-1][4]
            price_1m_ago = ohlcv_1m[-2][4]
            price_5m_ago = ohlcv_5m[-2][4]
            
            change_1m = ((current_price - price_1m_ago) / price_1m_ago) * 100
            change_5m = ((current_price - price_5m_ago) / price_5m_ago) * 100
            
            # Verificar condições de pump
            pump_detected = False
            pump_reason = ""
            
            if change_1m > self.parameters['pump_threshold_1min']:
                pump_detected = True
                pump_reason = f"PUMP 1min: {change_1m:.1f}%"
            elif change_5m > self.parameters['pump_threshold_5min']:
                pump_detected = True
                pump_reason = f"PUMP 5min: {change_5m:.1f}%"
            elif change_1m > self.parameters['momentum_threshold']:
                pump_detected = True
                pump_reason = f"MOMENTUM: {change_1m:.1f}%"
            
            if pump_detected:
                # REFINAMENTO: Verificar condições adicionais para evitar "comprar o topo"
                should_trade = True
                trade_reason = pump_reason
                
                # Condição 1: Só comprar se a tendência for BULLISH
                if context and context.get('trend') != "BULLISH":
                    should_trade = False
                    trade_reason += " (tendência não bullish)"
                
                # Condição 2: Não comprar se RSI estiver sobrecomprado
                if context and context.get('rsi_status') == "OVERBOUGHT":
                    should_trade = False
                    trade_reason += " (RSI sobrecomprado)"
                
                # Condição 3: Verificar se o pump não é muito agressivo (pode ser topo)
                if change_1m > 5.0:  # Pump muito forte pode ser topo
                    should_trade = False
                    trade_reason += " (pump muito agressivo)"
                
                # Condição 4: Verificar volume (pump sem volume pode ser manipulação)
                if context and context.get('volume_24h', 0) < 1000000:  # Menos de $1M
                    should_trade = False
                    trade_reason += " (volume baixo)"
                
                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'change_1m': change_1m,
                    'change_5m': change_5m,
                    'pump_reason': pump_reason,
                    'should_trade': should_trade,
                    'trade_reason': trade_reason,
                    'market_context': context
                }
            
            return None
            
        except Exception as e:
            return None
    
    def create_conformant_order(self, symbol, desired_notional_value, current_price):
        """Criar ordem conforme com todas as regras da Binance (ALGORITMO UNIFICADO)"""
        try:
            # Obter regras do cache
            limits = self.get_binance_limits(symbol)
            if not limits:
                raise Exception(f"Não foi possível obter limites para {symbol}")
            
            min_notional = limits['min_notional']
            step_size = limits['step_size']
            tick_size = limits['tick_size']
            
            # 1. Verificar se o valor desejado atende ao MIN_NOTIONAL
            if desired_notional_value < min_notional:
                raise Exception(f"Valor desejado ${desired_notional_value:.2f} < MIN_NOTIONAL ${min_notional} para {symbol}")
            
            # 2. Ajustar o preço para conformidade com PRICE_FILTER
            conformant_price = round(current_price / tick_size) * tick_size
            
            # 3. Calcular quantidade inicial
            raw_quantity = desired_notional_value / conformant_price
            
            # 4. Ajustar quantidade para conformidade com LOT_SIZE (floor)
            conformant_quantity = math.floor(raw_quantity / step_size) * step_size
            
            # 5. Verificação final e correção
            final_notional = conformant_quantity * conformant_price
            
            if final_notional < min_notional:
                # O arredondamento para baixo violou o MIN_NOTIONAL
                # Recalcular, forçando arredondamento para cima
                conformant_quantity = math.ceil(raw_quantity / step_size) * step_size
                final_notional = conformant_quantity * conformant_price
                
                print(f"⚠️ Ajuste necessário: quantidade aumentada para atender MIN_NOTIONAL")
            
            # 6. Verificações finais
            if conformant_quantity < limits['min_qty']:
                raise Exception(f"Quantidade {conformant_quantity} < MIN_QTY {limits['min_qty']} para {symbol}")
            
            if conformant_quantity > limits['max_qty']:
                raise Exception(f"Quantidade {conformant_quantity} > MAX_QTY {limits['max_qty']} para {symbol}")
            
            return {
                'symbol': symbol,
                'quantity': conformant_quantity,
                'price': conformant_price,
                'notional_value': final_notional,
                'limits_used': limits
            }
            
        except Exception as e:
            print(f"❌ Erro ao criar ordem conforme para {symbol}: {e}")
            return None
    
    def execute_trade(self, pump_data):
        """Executar trade de compra"""
        try:
            symbol = pump_data['symbol']
            current_price = pump_data['current_price']
            
            print(f"🚀 PARALLEL PUMP: {symbol} - {pump_data['pump_reason']}")
            print(f"💵 Preço atual: ${current_price}")
            
            # VERIFICAR SE O PAR ESTÁ DISPONÍVEL ANTES DE TRADAR
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                if not ticker or ticker.get('last') is None:
                    print(f"⚠️ Par {symbol} não disponível - pulando")
                    return None
            except Exception as e:
                print(f"⚠️ Erro ao verificar {symbol}: {e} - pulando")
                return None
            
            total_usdt = self.get_balance()
            
            if total_usdt < self.parameters['min_trade_value_usdt']:
                print(f"❌ Saldo insuficiente: ${total_usdt:.2f}")
                return None
            
            # Calcular valor do trade
            trade_value = self.calculate_trade_value(total_usdt)
            
            # CRIAR ORDEM CONFORME (ALGORITMO UNIFICADO)
            order_params = self.create_conformant_order(symbol, trade_value, current_price)
            if not order_params:
                return None
            
            print(f"💰 COMPRANDO: ${order_params['notional_value']:.2f} (30% do capital)")
            print(f"📊 Quantidade: {order_params['quantity']} {symbol.split('/')[0]}")
            print(f"💵 Preço ajustado: ${order_params['price']:.6f}")
            
            # Executar ordem LIMITE (contra slippage)
            # Preço limite 0.1% acima do atual para garantir execução rápida
            limit_price = order_params['price'] * 1.001  # 0.1% acima
            order = self.exchange.create_limit_buy_order(
                symbol, 
                order_params['quantity'], 
                limit_price
            )
            
            print(f"🟢 COMPRA EXECUTADA: {symbol}!")
            print(f"📋 Order ID: {order['id']}")
            print(f"💵 Preço de compra: ${current_price:.4f}")
            
            # Salvar trade de compra
            self.save_trade_log({
                 'timestamp': datetime.now().isoformat(),
                 'symbol': symbol,
                 'side': 'BUY',
                 'action': 'COMPRA',
                 'amount': order_params['quantity'],
                 'price': current_price,
                 'value_usdt': trade_value,
                 'order_id': order['id'],
                 'pump_reason': pump_data['pump_reason'],
                 'status': 'executed',
                 'crypto_amount': order_params['quantity']
             })
            
            return order
            
        except Exception as e:
            error_msg = str(e)
            if "Market is closed" in error_msg:
                print(f"⚠️ {symbol} temporariamente indisponível - pulando")
            elif "insufficient balance" in error_msg.lower():
                print(f"❌ Saldo insuficiente para {symbol}")
            elif "notional" in error_msg.lower():
                print(f"❌ Valor mínimo não atingido para {symbol}")
            else:
                print(f"❌ Erro ao executar trade: {e}")
            return None
    
    def check_open_positions(self):
        """Verificar posições abertas e aplicar take profit/stop loss"""
        try:
            print(f"🔍 Verificando posições abertas...")
            
            balance = self.exchange.fetch_balance()
            positions_to_check = []
            
            # Verificar moedas que temos
            for symbol in self.trading_pairs:
                base_currency = symbol.split('/')[0]
                amount = balance.get(base_currency, {}).get('free', 0)
                
                if amount > 0:
                    positions_to_check.append({
                        'symbol': symbol,
                        'amount': amount,
                        'base_currency': base_currency
                    })
            
            if not positions_to_check:
                print(f"   ⚪ Nenhuma posição aberta encontrada")
                return
            
            print(f"   📊 {len(positions_to_check)} posições encontradas")
            
            # Verificar cada posição
            for position in positions_to_check:
                self.check_position_take_profit_stop_loss(position)
                
        except Exception as e:
            print(f"❌ Erro ao verificar posições: {e}")
    
    def check_position_take_profit_stop_loss(self, position):
        """Verificar take profit e stop loss para uma posição (versão atualizada)"""
        try:
            symbol = position['symbol']
            amount = position['amount']
            
            # Obter preço atual
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # Buscar preço e timestamp de compra no log
            buy_price, buy_timestamp = self.get_buy_info_from_log(symbol)
            
            if not buy_price or not buy_timestamp:
                # Se não encontrarmos um log de compra, não podemos gerenciar esta posição.
                # Isso pode acontecer se a moeda foi comprada manualmente.
                # print(f"   ⚠️ {symbol}: Log de compra não encontrado, ignorando gerenciamento.")
                return
            
            # Calcular variação percentual
            price_change = ((current_price - buy_price) / buy_price) * 100
            
            print(f"   📈 {symbol}: Comprado a ${buy_price:.6f} | Atual: ${current_price:.6f} ({price_change:+.2f}%)")
            
            # Verificar take profit
            if price_change >= self.parameters['take_profit_percentage']:
                print(f"   🎯 {symbol}: TAKE PROFIT atingido! ({price_change:.2f}% >= {self.parameters['take_profit_percentage']}%)")
                self.execute_sell_trade(symbol, amount, "Take Profit")
                return
            
            # Verificar stop loss
            if price_change <= -self.parameters['stop_loss_percentage']:
                print(f"   🛑 {symbol}: STOP LOSS atingido! ({price_change:.2f}% <= -{self.parameters['stop_loss_percentage']}%)")
                self.execute_sell_trade(symbol, amount, "Stop Loss")
                return
            
            # Verificar tempo máximo de hold
            hold_time_minutes = (datetime.now() - buy_timestamp).total_seconds() / 60
            if hold_time_minutes >= self.parameters['max_hold_time_minutes']:
                print(f"   ⏰ {symbol}: Tempo máximo de hold atingido! ({hold_time_minutes:.1f}min >= {self.parameters['max_hold_time_minutes']}min)")
                self.execute_sell_trade(symbol, amount, "Max Hold Time")
                return
                
        except Exception as e:
            print(f"❌ Erro ao verificar posição {position['symbol']}: {e}")
    
    def get_buy_info_from_log(self, symbol):
        """
        Lê o arquivo de log de trás para frente para encontrar o preço e o timestamp
        da última ordem de COMPRA para um determinado símbolo.
        """
        try:
            log_file = self.logs_dir / 'parallel_trades.jsonl'
            if not log_file.exists():
                return None, None

            # Lê todas as linhas do arquivo
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Itera de trás para frente para encontrar a compra mais recente
            for line in reversed(lines):
                try:
                    trade = json.loads(line)
                    # Verifica se é a compra do símbolo que estamos procurando
                    if trade.get('symbol') == symbol and trade.get('side') == 'BUY':
                        buy_price = trade.get('price')
                        timestamp_str = trade.get('timestamp')
                        
                        if buy_price and timestamp_str:
                            # Converte o timestamp para um objeto datetime
                            buy_timestamp = datetime.fromisoformat(timestamp_str)
                            return buy_price, buy_timestamp

                except json.JSONDecodeError:
                    continue # Ignora linhas mal formatadas

            return None, None # Nenhuma compra encontrada para este símbolo

        except Exception as e:
            print(f"❌ Erro ao ler log para {symbol}: {e}")
            return None, None
    
    def execute_sell_trade(self, symbol, amount, reason="Take Profit"):
        """Executar trade de venda (COM ORDEM LIMITE)"""
        try:
            print(f"📉 VENDENDO: {symbol} - {reason}")
            print(f"📊 Quantidade: {amount}")
            
            # Obter preço atual
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            print(f"💵 Preço atual: ${current_price:.4f}")
            
            # Executar venda LIMITE (0.1% abaixo do atual)
            limit_price = current_price * 0.999  # 0.1% abaixo
            order = self.exchange.create_limit_sell_order(symbol, amount, limit_price)
            
            # Calcular valor da venda
            sell_value = amount * current_price
            
            print(f"🔴 VENDA EXECUTADA: {symbol}!")
            print(f"📋 Order ID: {order['id']}")
            print(f"💵 Preço de venda: ${current_price:.4f}")
            print(f"💰 Valor recebido: ${sell_value:.2f}")
            
            # Salvar trade de venda
            self.save_trade_log({
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'side': 'SELL',
                'action': 'VENDA',
                'amount': amount,
                'price': current_price,
                'value_usdt': sell_value,
                'order_id': order['id'],
                'sell_reason': reason,
                'status': 'executed',
                'crypto_amount': amount
            })
            
            return order
            
        except Exception as e:
            print(f"❌ Erro ao executar venda: {e}")
            return None
    
    def save_trade_log(self, trade_data):
        """Salvar log do trade (local + Firebase)"""
        try:
            # Salvar localmente
            log_file = self.logs_dir / 'parallel_trades.jsonl'
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(trade_data) + '\n')
            
            # Salvar no Firebase se disponível
            if self.firebase_manager:
                self.firebase_manager.save_trade(trade_data)
            
            print(f"✅ Trade log salvo: {trade_data['symbol']}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar log: {e}")
    
    def save_performance_log(self, performance_data):
        """Salvar log de performance"""
        try:
            log_file = self.logs_dir / 'parallel_performance.json'
            
            # Carregar dados existentes
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {'sessions': []}
            
            # Adicionar nova sessão
            data['sessions'].append(performance_data)
            
            # Salvar
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Performance log salvo")
            
        except Exception as e:
            print(f"❌ Erro ao salvar performance: {e}")
    
    def run_trading_cycle(self):
        """Executar ciclo de trading"""
        try:
            print(f"\n🚀 CICLO PARALLEL - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 50)
            
            total_usdt = self.get_balance()
            self.current_balance = total_usdt
            
            if total_usdt < self.parameters['min_trade_value_usdt']:
                print(f"💰 Saldo insuficiente: ${total_usdt:.2f}")
                return
            
            print(f"💰 Saldo inicial: ${total_usdt:.2f}")
            
            # PRIMEIRO: Verificar posições abertas (take profit/stop loss)
            self.check_open_positions()
            
            # SEGUNDO: Detectar pumps para novas compras
            pumps_detected = []
            pairs_checked = 0
            pairs_available = 0
            pairs_with_pumps = 0
            
            print(f"🔍 Verificando {len(self.trading_pairs)} pares...")
            
            for symbol in self.trading_pairs:
                pairs_checked += 1
                
                # Verificar disponibilidade
                if self.check_pair_availability(symbol):
                    pairs_available += 1
                    pump = self.detect_pump(symbol)
                    if pump and pump.get('should_trade', True):  # Verificar se deve fazer trade
                        pumps_detected.append(pump)
                        pairs_with_pumps += 1
                        print(f"   ✅ {symbol}: {pump['trade_reason']}")
                    elif pump:
                        print(f"   ⚠️ {symbol}: {pump['trade_reason']} (condições não atendidas)")
                    else:
                        print(f"   ⚪ {symbol}: Sem pump detectado")
                else:
                    print(f"   ❌ {symbol}: Indisponível ou preço muito alto")
            
            print(f"\n📊 RESUMO DA VERIFICAÇÃO:")
            print(f"   🔍 Pares verificados: {pairs_checked}")
            print(f"   ✅ Pares disponíveis: {pairs_available}")
            print(f"   🚀 Pumps detectados: {pairs_with_pumps}")
            
            # Executar trades
            trades_executed = 0
            trades_log = []
            trades_failed = 0
            
            print(f"\n🚀 TENTANDO EXECUTAR TRADES:")
            
            for pump in pumps_detected[:2]:
                if trades_executed >= self.parameters['max_trades_per_cycle']:
                    print(f"   ⏹️ Limite de trades por ciclo atingido ({self.parameters['max_trades_per_cycle']})")
                    break
                
                print(f"   🔄 Tentando trade: {pump['symbol']} - {pump['pump_reason']}")
                order = self.execute_trade(pump)
                
                if order:
                    trades_executed += 1
                    trades_log.append({
                        'action': 'BUY',
                        'symbol': pump['symbol'],
                        'price': pump['current_price'],
                        'reason': pump['pump_reason'],
                        'order_id': order['id']
                    })
                    print(f"   ✅ Trade executado com sucesso!")
                    time.sleep(1)
                else:
                    trades_failed += 1
                    print(f"   ❌ Trade falhou")
            
            if trades_executed == 0 and len(pumps_detected) > 0:
                print(f"\n❌ NENHUM TRADE EXECUTADO - POSSÍVEIS MOTIVOS:")
                print(f"   💰 Saldo insuficiente para o valor mínimo (${self.parameters['min_trade_value_usdt']})")
                print(f"   📊 Valor do trade muito baixo para Binance (NOTIONAL error)")
                print(f"   🔒 Par temporariamente indisponível")
                print(f"   ⚠️ Erro de conectividade com Binance")
                print(f"   📈 Contexto de mercado desfavorável")
            
            # Mostrar análise de contexto se houver pumps
            if pumps_detected:
                print(f"\n📊 ANÁLISE DE CONTEXTO DOS PUMPS:")
                for pump in pumps_detected[:3]:
                    context = pump.get('market_context', {})
                    print(f"   {pump['symbol']}: {pump['pump_reason']}")
                    print(f"      📈 Tendência: {context.get('trend', 'N/A')}")
                    print(f"      📊 RSI: {context.get('rsi', 'N/A'):.1f} ({context.get('rsi_status', 'N/A')})")
                    print(f"      📉 SMA20: ${context.get('sma_20', 'N/A'):.4f}")
                    print(f"      📉 SMA50: ${context.get('sma_50', 'N/A'):.4f}")
            
            # Mostrar resumo detalhado
            print(f"\n📊 RESUMO PARALLEL:")
            print(f"   🔍 Pumps detectados: {len(pumps_detected)}")
            print(f"   🚀 Trades executados: {trades_executed}")
            print(f"   ❌ Trades falharam: {trades_failed}")
            print(f"   🎓 Training ativo: {'✅' if self.training_active else '❌'}")
            
            if trades_executed == 0:
                if len(pumps_detected) == 0:
                    print(f"   📝 MOTIVO: Nenhum pump detectado nos pares disponíveis")
                else:
                    print(f"   📝 MOTIVO: Pumps detectados mas trades falharam")
            else:
                print(f"   📝 STATUS: Sistema funcionando normalmente")
            
            # Mostrar trades executados
            if trades_log:
                print(f"\n💼 TRADES EXECUTADOS:")
                for i, trade in enumerate(trades_log, 1):
                    print(f"   {i}. {trade['action']} {trade['symbol']} @ ${trade['price']:.4f}")
                    print(f"      📈 Motivo: {trade['reason']}")
                    print(f"      📋 Order ID: {trade['order_id']}")
            else:
                print(f"\n💼 Nenhum trade executado neste ciclo")
            
            if pumps_detected:
                best_pump = pumps_detected[0]
                print(f"\n🏆 MELHOR OPORTUNIDADE:")
                print(f"   {best_pump['symbol']} - {best_pump['pump_reason']}")
                print(f"   Preço: ${best_pump['current_price']:.4f}")
            
            # Atualizar saldo e mostrar resultado
            new_balance = self.get_balance()
            profit_loss = new_balance - total_usdt
            profit_percentage = (profit_loss / total_usdt) * 100 if total_usdt > 0 else 0
            
            print(f"\n💰 RESULTADO DO CICLO:")
            print(f"   Saldo inicial: ${total_usdt:.2f}")
            print(f"   Saldo final: ${new_balance:.2f}")
            print(f"   P&L: {profit_percentage:+.2f}% (${profit_loss:+.2f})")
            
            # Log detalhado do ciclo
            cycle_log = {
                'timestamp': datetime.now().isoformat(),
                'cycle_number': getattr(self, 'cycle_count', 0) + 1,
                'initial_balance': total_usdt,
                'final_balance': new_balance,
                'profit_loss': profit_loss,
                'profit_percentage': profit_percentage,
                'pumps_detected': len(pumps_detected),
                'trades_executed': trades_executed,
                'trades': trades_log,
                'training_active': self.training_active
            }
            
            self.save_cycle_log(cycle_log)
            self.cycle_count = getattr(self, 'cycle_count', 0) + 1
            
        except Exception as e:
            print(f"❌ Erro no ciclo: {e}")
    
    def save_cycle_log(self, cycle_data):
        """Salvar log detalhado do ciclo"""
        try:
            log_file = self.logs_dir / 'parallel_cycles.jsonl'
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(cycle_data) + '\n')
            
            # Firebase se disponível
            if self.firebase_manager:
                self.firebase_manager.save_trade({
                    'timestamp': cycle_data['timestamp'],
                    'cycle_number': cycle_data['cycle_number'],
                    'profit_loss': cycle_data['profit_loss'],
                    'trades_count': cycle_data['trades_executed'],
                    'status': 'cycle_completed'
                })
            
        except Exception as e:
            print(f"❌ Erro ao salvar cycle log: {e}")
    
    def start_training_background(self):
        """Iniciar treinamento em background"""
        def training_thread():
            try:
                print("🎓 Iniciando treinamento em background...")
                self.training_active = True
                
                # Executar extended_training_with_workers.py
                process = subprocess.Popen([
                    'python', 'extended_training_with_workers.py'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                print(f"✅ Treinamento iniciado (PID: {process.pid})")
                
                # Aguardar conclusão
                stdout, stderr = process.communicate()
                
                print("🎓 Treinamento concluído!")
                self.training_active = False
                
                # Salvar log de treinamento
                training_log = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'background_training',
                    'duration_minutes': 0,  # Calcular se necessário
                    'status': 'completed',
                    'stdout': stdout.decode() if stdout else '',
                    'stderr': stderr.decode() if stderr else ''
                }
                
                self.save_training_log(training_log)
                
            except Exception as e:
                print(f"❌ Erro no treinamento: {e}")
                self.training_active = False
        
        # Iniciar thread
        thread = threading.Thread(target=training_thread, daemon=True)
        thread.start()
    
    def save_training_log(self, training_data):
        """Salvar log de treinamento"""
        try:
            log_file = self.logs_dir / 'parallel_training.jsonl'
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(training_data) + '\n')
            
            # Firebase se disponível
            if self.firebase_manager:
                self.firebase_manager.save_training_log('parallel_system', training_data)
            
            print(f"✅ Training log salvo")
            
        except Exception as e:
            print(f"❌ Erro ao salvar training log: {e}")
    
    def start_parallel_system(self, trading_interval=2, start_training=True):
        """Iniciar sistema paralelo"""
        print(f"🚀 INICIANDO SISTEMA PARALLEL!")
        print(f"⏰ Intervalo trading: {trading_interval} minutos")
        print(f"🎓 Training em background: {'✅' if start_training else '❌'}")
        print(f"💰 Trade mínimo: ${self.parameters['min_trade_value_usdt']}")
        print(f"💰 Trade máximo: ${self.parameters['max_trade_value_usdt']}")
        print(f"📈 Porcentagem por trade: {self.parameters['trade_percentage']:.1%}")
        print(f"🔥 Pump threshold: {self.parameters['pump_threshold_1min']}%")
        print("=" * 50)
        
        # Iniciar treinamento se solicitado
        if start_training:
            self.start_training_background()
        
        # Executar primeiro ciclo
        self.run_trading_cycle()
        
        print(f"✅ Sistema ativo! Próximo ciclo em {self.parameters['cycle_interval_minutes']} minutos...")
        
        try:
            while True:
                time.sleep(self.parameters['cycle_interval_minutes'] * 60)
                self.run_trading_cycle()
        except KeyboardInterrupt:
            print("\n🛑 Sistema interrompido")
            
            # Salvar performance final
            final_balance = self.get_balance()
            performance_data = {
                'timestamp': datetime.now().isoformat(),
                'initial_balance': self.initial_balance,
                'final_balance': final_balance,
                'profit_loss': final_balance - self.initial_balance,
                'profit_percentage': ((final_balance - self.initial_balance) / self.initial_balance) * 100 if self.initial_balance > 0 else 0,
                'training_active': self.training_active,
                'duration_minutes': 0  # Calcular se necessário
            }
            
            self.save_performance_log(performance_data)

def main():
    print("🚀 PARALLEL TRADING SYSTEM")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    system = ParallelTradingSystem()
    
    if not system.setup_binance():
        return
    
    # Configurar intervalo (agora fixo em 30min conforme princípios)
    print("⏰ Intervalo fixo: 30 minutos (conforme princípios de trading)")
    
    # Perguntar sobre treinamento
    training_choice = input("🎓 Iniciar treinamento em background? (s/n, padrão s): ")
    start_training = training_choice.lower() != 'n'
    
    system.start_parallel_system(30, start_training)

if __name__ == "__main__":
    main()
