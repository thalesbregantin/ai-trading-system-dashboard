#!/usr/bin/env python3
"""
AI Trader Simplificado - Versão sem TensorFlow
Usa estratégias baseadas em regras e indicadores técnicos
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging

class SimpleAITrader:
    """Trading AI simplificado usando indicadores técnicos"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def calculate_technical_indicators(self, data):
        """Calcula indicadores técnicos"""
        df = data.copy()
        
        # Médias móveis
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # Momentum
        df['Momentum'] = df['Close'] - df['Close'].shift(10)
        
        return df
    
    def generate_signals(self, data):
        """Gera sinais de trading baseados em indicadores"""
        df = self.calculate_technical_indicators(data)
        
        signals = pd.DataFrame(index=df.index)
        signals['signal'] = 0  # 0: hold, 1: buy, -1: sell
        
        # Sinais baseados em múltiplos indicadores
        for i in range(20, len(df)):
            buy_signals = 0
            sell_signals = 0
            
            # SMA crossover
            if df['SMA_20'].iloc[i] > df['SMA_50'].iloc[i] and df['SMA_20'].iloc[i-1] <= df['SMA_50'].iloc[i-1]:
                buy_signals += 1
            elif df['SMA_20'].iloc[i] < df['SMA_50'].iloc[i] and df['SMA_20'].iloc[i-1] >= df['SMA_50'].iloc[i-1]:
                sell_signals += 1
            
            # RSI
            if df['RSI'].iloc[i] < 30:
                buy_signals += 1
            elif df['RSI'].iloc[i] > 70:
                sell_signals += 1
            
            # MACD
            if df['MACD'].iloc[i] > df['MACD_Signal'].iloc[i] and df['MACD'].iloc[i-1] <= df['MACD_Signal'].iloc[i-1]:
                buy_signals += 1
            elif df['MACD'].iloc[i] < df['MACD_Signal'].iloc[i] and df['MACD'].iloc[i-1] >= df['MACD_Signal'].iloc[i-1]:
                sell_signals += 1
            
            # Bollinger Bands
            if df['Close'].iloc[i] < df['BB_Lower'].iloc[i]:
                buy_signals += 1
            elif df['Close'].iloc[i] > df['BB_Upper'].iloc[i]:
                sell_signals += 1
            
            # Momentum
            if df['Momentum'].iloc[i] > 0 and df['Momentum'].iloc[i-1] <= 0:
                buy_signals += 1
            elif df['Momentum'].iloc[i] < 0 and df['Momentum'].iloc[i-1] >= 0:
                sell_signals += 1
            
            # Decisão final
            if buy_signals >= 2:
                signals['signal'].iloc[i] = 1
            elif sell_signals >= 2:
                signals['signal'].iloc[i] = -1
        
        return signals
    
    def get_current_signal(self, symbol):
        """Obtém sinal atual para um símbolo"""
        try:
            # Baixar dados recentes
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="100d")
            
            if data.empty:
                return 0
            
            signals = self.generate_signals(data)
            current_signal = signals['signal'].iloc[-1]
            
            self.logger.info(f"Sinal atual para {symbol}: {current_signal}")
            return current_signal
            
        except Exception as e:
            self.logger.error(f"Erro ao obter sinal para {symbol}: {e}")
            return 0
    
    def get_portfolio_signals(self):
        """Obtém sinais para todos os pares do portfólio"""
        signals = {}
        
        for symbol in self.config.TRADING_PAIRS:
            signal = self.get_current_signal(symbol)
            signals[symbol] = signal
            
        return signals

# Função de compatibilidade
def create_ai_trader(config):
    """Cria uma instância do AI Trader simplificado"""
    return SimpleAITrader(config)
