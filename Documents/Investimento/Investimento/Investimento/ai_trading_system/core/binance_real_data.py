#!/usr/bin/env python3
"""
Binance Real Data Connector
Conecta com API da Binance para obter dados reais da conta
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import ccxt
import warnings
warnings.filterwarnings('ignore')

from .config import TradingConfig

class BinanceRealData:
    """Conecta com dados reais da Binance"""
    
    def __init__(self):
        """Inicializa conexão com Binance"""
        self.config = TradingConfig()
        self.exchange = None
        self.account_info = None
        self.trades_cache = None
        self.setup_exchange()
    
    def setup_exchange(self):
        """Configura conexão com Binance"""
        try:
            # Inicializa exchange (spot por padrão)
            self.exchange = ccxt.binance({
                'apiKey': self.config.BINANCE_API_KEY,
                'secret': self.config.BINANCE_API_SECRET,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })

            # Ativa testnet se configurado
            try:
                self.exchange.set_sandbox_mode(self.config.TESTNET_MODE)
            except Exception:
                pass
            
            # Testa conexão
            self.exchange.load_markets()
            print(f"✅ Conectado à Binance {'(Testnet)' if self.config.TESTNET_MODE else '(Live)'}")
            
        except Exception as e:
            print(f"❌ Erro na conexão Binance: {e}")
            # Mensagem amigável para API inválida
            try:
                if isinstance(e, ccxt.BaseError) and 'Invalid Api-Key ID' in str(e):
                    print("⚠️ Verifique suas credenciais BINANCE_API_KEY/BINANCE_API_SECRET no .env")
            except Exception:
                pass
            self.exchange = None
    
    def get_account_balance(self) -> Dict:
        """Obtém saldo real da conta"""
        try:
            if not self.exchange:
                return self._get_demo_balance()
            
            balance = self.exchange.fetch_balance()
            
            totals = balance.get('total', {}) or {}
            relevant_balances = {}
            for currency, total in totals.items():
                if total and currency in ['USDT', 'BTC', 'ETH', 'BNB']:
                    relevant_balances[currency] = {
                        'total': total,
                        'free': balance.get('free', {}).get(currency, 0),
                        'used': balance.get('used', {}).get(currency, 0)
                    }
            
            # Calcula valor total em USDT
            total_usdt = 0
            for currency, amounts in relevant_balances.items():
                if currency == 'USDT':
                    total_usdt += amounts['total']
                else:
                    try:
                        ticker = self.exchange.fetch_ticker(f"{currency}/USDT")
                        total_usdt += amounts['total'] * ticker['last']
                    except Exception:
                        pass
            
            return {
                'balances': relevant_balances,
                'total_usdt': total_usdt,
                'free_usdt': balance.get('free', {}).get('USDT', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter saldo: {e}")
            return self._get_demo_balance()
    
    def get_trading_history(self, days: int = 30) -> pd.DataFrame:
        """Obtém histórico real de trades"""
        try:
            if not self.exchange:
                return self._get_demo_trades()
            
            trades_list = []
            symbols = ['BTC/USDT', 'ETH/USDT']
            
            for symbol in symbols:
                try:
                    # Busca trades dos últimos 30 dias
                    since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
                    trades = self.exchange.fetch_my_trades(symbol, since=since)
                    
                    for trade in trades:
                        trades_list.append({
                            'symbol': trade['symbol'],
                            'side': trade['side'].upper(),
                            'amount': trade['amount'],
                            'price': trade['price'],
                            'cost': trade['cost'],
                            'fee': trade['fee']['cost'] if trade['fee'] else 0,
                            'timestamp': pd.to_datetime(trade['timestamp'], unit='ms'),
                            'id': trade['id']
                        })
                        
                except Exception as e:
                    print(f"⚠️ Erro ao buscar trades de {symbol}: {e}")
                    continue
            
            if not trades_list:
                return self._get_demo_trades()
            
            df = pd.DataFrame(trades_list)
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Adiciona colunas calculadas
            df['entry_date'] = df['timestamp']
            df['exit_date'] = df['timestamp'] + timedelta(hours=1)  # Estimativa
            
            # Calcula PnL estimado (pareando BUY/SELL)
            df['pnl_pct'] = 0.0
            for symbol in df['symbol'].unique():
                symbol_trades = df[df['symbol'] == symbol].copy()
                
                buys = symbol_trades[symbol_trades['side'] == 'BUY']
                sells = symbol_trades[symbol_trades['side'] == 'SELL']
                
                if len(buys) > 0 and len(sells) > 0:
                    avg_buy_price = buys['price'].mean()
                    avg_sell_price = sells['price'].mean()
                    pnl = ((avg_sell_price / avg_buy_price) - 1) * 100
                    
                    df.loc[df['symbol'] == symbol, 'pnl_pct'] = pnl
            
            # Duração dos trades
            df['duration_days'] = (df['exit_date'] - df['entry_date']).dt.total_seconds() / 86400
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao obter histórico: {e}")
            return self._get_demo_trades()
    
    def get_current_positions(self) -> List[Dict]:
        """Obtém posições atuais (derivado de balance.total)"""
        try:
            if not self.exchange:
                return []
            
            balance = self.exchange.fetch_balance()
            totals = balance.get('total', {}) or {}
            positions = []
            
            for currency, total in totals.items():
                if not total or currency in ['USDT', 'USD']:
                    continue
                try:
                    ticker = self.exchange.fetch_ticker(f"{currency}/USDT")
                    price = ticker['last']
                    value_usdt = total * price
                    
                    positions.append({
                        'symbol': f"{currency}/USDT",
                        'amount': total,
                        'price': price,
                        'current_price': price,
                        'value_usdt': value_usdt,
                        'market_value': value_usdt,
                        'avg_cost': None,
                        'pnl_pct': 0.0
                    })
                except Exception:
                    continue
            
            return positions
            
        except Exception as e:
            print(f"❌ Erro ao obter posições: {e}")
            return []
    
    def get_market_data(self, symbol: str = 'BTC/USDT', timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
        """Obtém dados de mercado em tempo real"""
        try:
            if not self.exchange:
                return self._get_demo_market_data()
            
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['date'] = df['timestamp']
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao obter dados de mercado: {e}")
            return self._get_demo_market_data()
    
    def _get_demo_balance(self) -> Dict:
        """Dados de saldo simulados para demo"""
        return {
            'balances': {
                'USDT': {'total': 85.50, 'free': 50.0, 'used': 35.50},
                'BTC': {'total': 0.0015, 'free': 0.0015, 'used': 0.0},
                'ETH': {'total': 0.025, 'free': 0.025, 'used': 0.0}
            },
            'total_usdt': 150.75,
            'free_usdt': 50.0,
            'timestamp': datetime.now()
        }
    
    def _get_demo_trades(self) -> pd.DataFrame:
        """Dados de trades simulados para demo"""
        np.random.seed(42)
        
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='6H')
        
        trades = []
        for i, date in enumerate(dates):
            if np.random.random() > 0.7:  # 30% chance de trade
                symbol = np.random.choice(['BTC/USDT', 'ETH/USDT'])
                side = np.random.choice(['BUY', 'SELL'])
                
                trades.append({
                    'symbol': symbol,
                    'side': side,
                    'amount': np.random.uniform(0.001, 0.01),
                    'price': np.random.uniform(25000, 75000) if 'BTC' in symbol else np.random.uniform(1500, 4000),
                    'cost': np.random.uniform(50, 500),
                    'fee': np.random.uniform(0.1, 2.0),
                    'timestamp': date,
                    'entry_date': date,
                    'exit_date': date + timedelta(hours=np.random.randint(1, 24)),
                    'pnl_pct': np.random.normal(0.5, 3.0),
                    'duration_days': np.random.uniform(0.5, 5.0),
                    'id': f"demo_{i}"
                })
        
        return pd.DataFrame(trades)
    
    def _get_demo_market_data(self) -> pd.DataFrame:
        """Dados de mercado simulados para demo"""
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='1H')
        
        # Simula movimento de preço do BTC
        np.random.seed(42)
        base_price = 45000
        prices = [base_price]
        
        for _ in range(len(dates) - 1):
            change = np.random.normal(0, 0.02)  # 2% volatilidade
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        df = pd.DataFrame({
            'timestamp': dates,
            'date': dates,
            'open': prices,
            'high': [p * (1 + np.random.uniform(0, 0.03)) for p in prices],
            'low': [p * (1 - np.random.uniform(0, 0.03)) for p in prices],
            'close': prices,
            'volume': np.random.uniform(100, 1000, len(dates))
        })
        
        return df

# Instância global
binance_data = BinanceRealData()
