"""
EXECUTOR DE ORDENS BINANCE - TRADING REAL
==========================================

ATENÇÃO: Este código executa ordens REAIS na Binance!
- Use apenas com dinheiro que pode perder
- Comece com valores pequenos
- Configure suas chaves API com cuidado

Estratégia: Momentum otimizada com R$ 100
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
from typing import Dict, Optional, Tuple

class BinanceExecutor:
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = True):
        """
        Inicializa o executor da Binance
        
        Args:
            api_key: Chave API da Binance
            api_secret: Secret da API da Binance  
            testnet: Se True, usa testnet. Se False, usa produção REAL
        """
        self.testnet = testnet
        
        # Configuração da exchange
        if testnet:
            self.exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'sandbox': True,  # Testnet
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                }
            })
        else:
            # PRODUÇÃO REAL - CUIDADO!
            self.exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'sandbox': False,  # PRODUÇÃO REAL
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                }
            })
        
        # Configurações de trading
        self.symbols = ['BTC/USDT', 'ETH/USDT']
        self.capital_per_trade = 50  # R$ 50 por trade (total R$ 100)
        self.stop_loss_pct = 0.10    # 10% stop loss
        self.take_profit_pct = 0.15  # 15% take profit
        
        # Histórico de ordens
        self.orders_history = []
        self.positions = {}
        
        print(f"🔧 Binance Executor inicializado")
        print(f"📊 Modo: {'TESTNET' if testnet else '🚨 PRODUÇÃO REAL 🚨'}")
        print(f"💰 Capital por trade: ${self.capital_per_trade}")

    def get_balance(self) -> Dict:
        """Obtém saldo da conta"""
        try:
            balance = self.exchange.fetch_balance()
            return {
                'USDT': balance.get('USDT', {}).get('free', 0),
                'BTC': balance.get('BTC', {}).get('free', 0),
                'ETH': balance.get('ETH', {}).get('free', 0)
            }
        except Exception as e:
            print(f"❌ Erro ao obter saldo: {e}")
            return {}

    def get_market_data(self, symbol: str, timeframe: str = '1d', limit: int = 50) -> pd.DataFrame:
        """Obtém dados de mercado"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"❌ Erro ao obter dados de {symbol}: {e}")
            return pd.DataFrame()

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores técnicos"""
        if df.empty or len(df) < 21:
            return df
            
        # SMA
        df['sma_9'] = df['close'].rolling(window=9).mean()
        df['sma_21'] = df['close'].rolling(window=21).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Volume médio
        df['volume_sma'] = df['volume'].rolling(window=10).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        return df

    def get_signal(self, symbol: str) -> str:
        """Gera sinal de trading para um símbolo"""
        try:
            df = self.get_market_data(symbol)
            if df.empty:
                return "HOLD"
                
            df = self.calculate_indicators(df)
            latest = df.iloc[-1]
            
            # Condições de compra (mesmo algoritmo otimizado)
            buy_conditions = [
                latest['close'] > latest['sma_9'],           # Preço acima SMA 9
                latest['sma_9'] > latest['sma_21'],          # SMA 9 acima SMA 21
                latest['rsi'] > 30 and latest['rsi'] < 70,   # RSI em zona neutra
                latest['volume_ratio'] > 1.2                 # Volume acima da média
            ]
            
            # Condições de venda
            sell_conditions = [
                latest['close'] < latest['sma_9'],           # Preço abaixo SMA 9
                latest['rsi'] > 70                           # RSI sobrecomprado
            ]
            
            if all(buy_conditions):
                return "BUY"
            elif any(sell_conditions):
                return "SELL"
            else:
                return "HOLD"
                
        except Exception as e:
            print(f"❌ Erro ao calcular sinal para {symbol}: {e}")
            return "HOLD"

    def execute_buy_order(self, symbol: str, amount_usdt: float) -> Optional[Dict]:
        """Executa ordem de compra"""
        try:
            # Obtém preço atual
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            
            # Calcula quantidade
            quantity = amount_usdt / price
            
            # Arredonda para precisão mínima
            market = self.exchange.market(symbol)
            quantity = self.exchange.amount_to_precision(symbol, quantity)
            
            print(f"🛒 Executando COMPRA:")
            print(f"   Symbol: {symbol}")
            print(f"   Quantidade: {quantity}")
            print(f"   Preço: ${price:.2f}")
            print(f"   Total: ${float(quantity) * price:.2f}")
            
            if not self.testnet:
                # Confirmação extra para produção
                confirm = input("⚠️  ORDEM REAL! Confirma? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("❌ Ordem cancelada pelo usuário")
                    return None
            
            # Executa ordem
            order = self.exchange.create_market_buy_order(symbol, quantity)
            
            # Registra ordem
            order_record = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'side': 'buy',
                'amount': quantity,
                'price': price,
                'cost': float(quantity) * price,
                'order_id': order['id'],
                'status': order['status']
            }
            
            self.orders_history.append(order_record)
            self.positions[symbol] = {
                'amount': float(quantity),
                'entry_price': price,
                'entry_time': datetime.now()
            }
            
            print(f"✅ Ordem de compra executada!")
            print(f"   ID: {order['id']}")
            
            return order_record
            
        except Exception as e:
            print(f"❌ Erro ao executar compra de {symbol}: {e}")
            return None

    def execute_sell_order(self, symbol: str) -> Optional[Dict]:
        """Executa ordem de venda"""
        try:
            if symbol not in self.positions:
                print(f"⚠️ Não há posição em {symbol} para vender")
                return None
                
            position = self.positions[symbol]
            quantity = position['amount']
            
            # Obtém preço atual
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            
            print(f"💰 Executando VENDA:")
            print(f"   Symbol: {symbol}")
            print(f"   Quantidade: {quantity}")
            print(f"   Preço: ${price:.2f}")
            print(f"   Total: ${quantity * price:.2f}")
            
            # Calcula P&L
            entry_price = position['entry_price']
            pnl_pct = ((price - entry_price) / entry_price) * 100
            pnl_usd = (price - entry_price) * quantity
            
            print(f"   📊 P&L: {pnl_pct:+.2f}% (${pnl_usd:+.2f})")
            
            if not self.testnet:
                # Confirmação extra para produção
                confirm = input("⚠️  VENDA REAL! Confirma? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("❌ Ordem cancelada pelo usuário")
                    return None
            
            # Executa ordem
            order = self.exchange.create_market_sell_order(symbol, quantity)
            
            # Registra ordem
            order_record = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'side': 'sell',
                'amount': quantity,
                'price': price,
                'cost': quantity * price,
                'order_id': order['id'],
                'status': order['status'],
                'pnl_pct': pnl_pct,
                'pnl_usd': pnl_usd
            }
            
            self.orders_history.append(order_record)
            del self.positions[symbol]  # Remove posição
            
            print(f"✅ Ordem de venda executada!")
            print(f"   ID: {order['id']}")
            
            return order_record
            
        except Exception as e:
            print(f"❌ Erro ao executar venda de {symbol}: {e}")
            return None

    def check_stop_loss_take_profit(self):
        """Verifica stop loss e take profit das posições abertas"""
        for symbol, position in list(self.positions.items()):
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                entry_price = position['entry_price']
                
                # Calcula variação percentual
                pct_change = ((current_price - entry_price) / entry_price) * 100
                
                # Verifica stop loss
                if pct_change <= -self.stop_loss_pct * 100:
                    print(f"🛑 STOP LOSS ativado para {symbol} ({pct_change:.2f}%)")
                    self.execute_sell_order(symbol)
                
                # Verifica take profit
                elif pct_change >= self.take_profit_pct * 100:
                    print(f"🎯 TAKE PROFIT ativado para {symbol} ({pct_change:.2f}%)")
                    self.execute_sell_order(symbol)
                
            except Exception as e:
                print(f"❌ Erro ao verificar {symbol}: {e}")

    def run_daily_analysis(self):
        """Executa análise diária e trading"""
        print(f"\n🔍 ANÁLISE DIÁRIA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Verifica saldo
        balance = self.get_balance()
        print(f"💰 Saldo: ${balance.get('USDT', 0):.2f} USDT")
        
        # Verifica posições atuais
        if self.positions:
            print("\n📊 Posições abertas:")
            for symbol, pos in self.positions.items():
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                pnl_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
                print(f"   • {symbol}: {pos['amount']:.6f} @ ${pos['entry_price']:.2f} (P&L: {pnl_pct:+.2f}%)")
        
        # Verifica stop loss / take profit
        self.check_stop_loss_take_profit()
        
        # Analisa novos sinais
        print(f"\n📈 Análise de sinais:")
        for symbol in self.symbols:
            signal = self.get_signal(symbol)
            print(f"   • {symbol}: {signal}")
            
            if signal == "BUY" and symbol not in self.positions:
                if balance.get('USDT', 0) >= self.capital_per_trade:
                    print(f"🚀 Executando compra de {symbol}")
                    self.execute_buy_order(symbol, self.capital_per_trade)
                else:
                    print(f"⚠️ Saldo insuficiente para comprar {symbol}")
                    
            elif signal == "SELL" and symbol in self.positions:
                print(f"📉 Executando venda de {symbol}")
                self.execute_sell_order(symbol)

    def show_performance(self):
        """Mostra performance das operações"""
        if not self.orders_history:
            print("📊 Nenhuma operação executada ainda")
            return
            
        print("\n📊 PERFORMANCE")
        print("=" * 40)
        
        trades = [o for o in self.orders_history if 'pnl_usd' in o]
        
        if trades:
            total_pnl = sum(t['pnl_usd'] for t in trades)
            avg_pnl = np.mean([t['pnl_pct'] for t in trades])
            win_rate = len([t for t in trades if t['pnl_usd'] > 0]) / len(trades) * 100
            
            print(f"💰 P&L Total: ${total_pnl:+.2f}")
            print(f"📈 P&L Médio: {avg_pnl:+.2f}%")
            print(f"🎯 Taxa de Acerto: {win_rate:.1f}%")
            print(f"🔢 Total de Trades: {len(trades)}")

def main():
    """Função principal"""
    print("🚀 BINANCE EXECUTOR - TRADING COM R$ 100")
    print("=" * 50)
    
    # CONFIGURAÇÃO IMPORTANTE
    print("⚠️  IMPORTANTE: Configure suas chaves API")
    print("📝 Edite as variáveis abaixo com suas chaves:")
    
    # SUAS CHAVES API AQUI
    API_KEY = "sua_api_key_aqui"
    API_SECRET = "sua_api_secret_aqui"
    
    # MODO: True = Testnet, False = PRODUÇÃO REAL
    TESTNET = True
    
    if API_KEY == "sua_api_key_aqui":
        print("❌ Configure suas chaves API antes de usar!")
        print("📖 Veja o arquivo PLANO_INVESTIMENTO_R100.md para instruções")
        return
    
    # Inicializa executor
    executor = BinanceExecutor(
        api_key=API_KEY,
        api_secret=API_SECRET,
        testnet=TESTNET
    )
    
    try:
        # Executa análise diária
        executor.run_daily_analysis()
        
        # Mostra performance
        executor.show_performance()
        
    except KeyboardInterrupt:
        print("\n👋 Execução interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()
