"""
Binance AI Trading Bot
Integra AI Trader com execução real na Binance
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from .hybrid_trading_system import HybridTradingSystem, train_hybrid_system, AITrader
from .config import TradingConfig
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_trading_bot.log', encoding='utf-8')
    ]
)

class BinanceAIBot:
    """
    Bot de trading AI para Binance
    Combina Deep Q-Learning com execução real
    """
    
    def __init__(self, api_key, api_secret, testnet=True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # Inicializa exchange
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'sandbox': testnet,
            'rateLimit': 1200,
            'enableRateLimit': True,
        })
        
        # Configurações (agora vindas de TradingConfig)
        self.trading_pairs = TradingConfig.TRADING_PAIRS
        self.min_trade_amount = TradingConfig.MIN_TRADE_AMOUNT
        self.max_position_size = TradingConfig.MAX_POSITION_SIZE
        self.signal_interval = TradingConfig.SIGNAL_INTERVAL
        
        # Sistema AI
        self.ai_systems = {}
        self.positions = {}
        self.trade_history = []
        
        # Estado
        self.running = False
        self.last_signals = {}
        
        logging.info(f"Binance AI Bot inicializado {'(TESTNET)' if testnet else '(LIVE)'}")

    def run_trading_cycle(self):
        """Executa um ciclo único de trading: processa sinais e mostra status."""
        # Inicializa AI na primeira execução
        if not self.ai_systems:
            self.initialize_ai_systems()
        self.process_signals()
        self.show_status()
    
    def calculate_total_value(self, balance):
        """Calcula valor total usando mapas free/used"""
        try:
            free_map = balance.get('free', {}) if isinstance(balance.get('free'), dict) else {}
            used_map = balance.get('used', {}) if isinstance(balance.get('used'), dict) else {}
            total = 0.0
            for asset, free_amt in free_map.items():
                amt = (free_amt or 0) + (used_map.get(asset, 0) or 0)
                if amt <= 0:
                    continue
                if asset == 'USDT':
                    total += amt
                else:
                    pair = f"{asset}/USDT"
                    try:
                        ticker = self.exchange.fetch_ticker(pair)
                        total += amt * ticker['last']
                    except Exception:
                        continue
            return total
        except Exception as e:
            logging.error(f"❌ Erro ao calcular valor total (fallback 0): {e}")
            return 0.0

    def initialize_ai_systems(self):
        """Inicializa sistemas AI para cada par com fallback de dados da exchange"""
        logging.info("🧠 Inicializando sistemas AI...")
        # Snapshot de saldo para definir capital inicial
        try:
            self.balance_snapshot = self.get_account_balance()
        except Exception:
            self.balance_snapshot = {'USDT_free': 0}
        for pair in self.trading_pairs:
            try:
                yf_symbol = TradingConfig.get_yfinance_symbol(pair)
                hybrid = HybridTradingSystem(yf_symbol)
                # Tenta yfinance
                try:
                    data = hybrid.download_data(period='6mo')
                except Exception:
                    # Fallback: usar dados ccxt
                    logging.warning(f"⚠️ Fallback para dados da exchange em {pair}")
                    ohlcv = self.exchange.fetch_ohlcv(pair, timeframe='1h', limit=500)
                    df_fb = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
                    df_fb['Date'] = pd.to_datetime(df_fb['timestamp'], unit='ms')
                    df_fb.set_index('Date', inplace=True)
                    df_fb.rename(columns={'close':'Close','open':'Open','high':'High','low':'Low','volume':'Volume'}, inplace=True)
                    # Garante colunas necessárias
                    for col in ['Open','High','Low','Volume']:
                        if col not in df_fb.columns:
                            df_fb[col] = df_fb['Close']
                    data = df_fb[['Open','High','Low','Close','Volume']].copy()
                # Verifica mínimo de pontos
                if len(data) < 50:
                    logging.warning(f"⚠️ Dados insuficientes para {pair} ({len(data)}) - pulando")
                    continue
                free_usdt = self.balance_snapshot.get('USDT_free', 0)
                pct = getattr(TradingConfig, 'TRAIN_CAPITAL_PERCENT', 0.8)
                initial_capital = max(free_usdt * pct, 10)
                hybrid.train_hybrid_system(data, episodes=3, initial_capital=initial_capital)
                self.ai_systems[pair] = hybrid
                logging.info(f"✅ Sistema AI treinado para {pair} | capital={initial_capital:.2f}")
            except Exception as e:
                logging.error(f"❌ Erro ao treinar AI para {pair}: {e}")

    def get_account_balance(self):
        """Obtém saldo da conta"""
        try:
            balance = self.exchange.fetch_balance()
            
            # USDT disponível para trading
            usdt_free = balance['USDT']['free'] if 'USDT' in balance else 0
            
            return {
                'USDT_free': usdt_free,
                'total_value': self.calculate_total_value(balance)
            }
        
        except Exception as e:
            logging.error(f"❌ Erro ao obter saldo: {e}")
            return {'USDT_free': 0, 'total_value': 0}
    
    def get_market_data(self, pair, timeframe='1h', limit=100):
        """Obtém dados de mercado"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(pair, timeframe, limit=limit)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
        
        except Exception as e:
            logging.error(f"❌ Erro ao obter dados de {pair}: {e}")
            return None
    
    def generate_ai_signal(self, pair):
        """Gera sinal AI para um par incluindo contexto de estratégia"""
        try:
            if pair not in self.ai_systems:
                logging.warning(f"⚠️ Sistema AI não encontrado para {pair}")
                return None
            market_data = self.get_market_data(pair, limit=250)
            if market_data is None or market_data.empty:
                return None
            # Cálculo de MMs (rápida 20, lenta 50) se possível
            fast_ma = market_data['close'].rolling(20).mean().iloc[-1] if len(market_data) >= 20 else None
            slow_ma = market_data['close'].rolling(50).mean().iloc[-1] if len(market_data) >= 50 else None
            ai_system = self.ai_systems[pair]
            data_for_ai = pd.DataFrame({'Close': market_data['close']})
            signal = ai_system.generate_signal(data_for_ai, len(data_for_ai) - 1)
            current_price = market_data['close'].iloc[-1]
            logging.info(f"SINAL {pair} | close={current_price:.4f} | ai_signal={signal}")
            # Indicadores extras (RSI / Momentum simples)
            closes = market_data['close']
            rsi_period = getattr(TradingConfig, 'RSI_PERIOD', 14)
            delta = closes.diff()
            gain = delta.clip(lower=0).rolling(rsi_period).mean()
            loss = (-delta.clip(upper=0)).rolling(rsi_period).mean()
            rs = gain / (loss.replace(0, np.nan))
            rsi_val = (100 - (100 / (1 + rs))).iloc[-1] if len(closes) > rsi_period else None
            mom_period = getattr(TradingConfig, 'MOMENTUM_PERIOD', 10)
            momentum_val = closes.pct_change(mom_period).iloc[-1] if len(closes) > mom_period else None
            signal_info = {
                'pair': pair,
                'signal': signal,
                'price': current_price,
                'timestamp': datetime.now(),
                'confidence': 0.8,
                'fast_ma': fast_ma,
                'slow_ma': slow_ma,
                'rsi': rsi_val,
                'momentum': momentum_val
            }
            return signal_info
        except Exception as e:
            logging.error(f"❌ Erro ao gerar sinal para {pair}: {e}")
            return None

    def _log_structured_execution(self, action, pair, quantity, price, strategy_info=None, pnl=None, pnl_pct=None):
        """Log estruturado em português para execução de ordens."""
        base = pair.split('/')[0]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        barra = "-" * 45
        action_label = 'COMPRADO' if action == 'BUY' else 'SEM POSIÇÃO'
        header_icon = '🟢' if action == 'BUY' else '🔴'
        logging.info(barra)
        logging.info(f"{header_icon} EXECUTADO ({timestamp})")
        logging.info(f"Par: {pair}")
        logging.info(f"Posição atual: {action_label}")
        if action == 'BUY':
            logging.info(f"Balanço atual: {quantity:.6f} ({base})")
        if action == 'SELL' and pnl is not None:
            logging.info(f"Resultado Trade: PnL ${pnl:.2f} ({pnl_pct:.2f}%)")
        logging.info(barra)
        logging.info("Estratégia executada:")
        if strategy_info:
            fast_ma = strategy_info.get('fast_ma')
            slow_ma = strategy_info.get('slow_ma')
            rsi_v = strategy_info.get('rsi')
            mom_v = strategy_info.get('momentum')
            if fast_ma is not None:
                logging.info(f" - Média Rápida (20): {fast_ma:.4f}")
            if slow_ma is not None:
                logging.info(f" - Média Lenta (50): {slow_ma:.4f}")
            sig_txt = ['HOLD','COMPRAR','VENDER'][strategy_info.get('signal',0)]
            logging.info(f" - Decisão de posição: {sig_txt}")
            if rsi_v is not None:
                logging.info(f" - RSI: {rsi_v:.2f}")
            if mom_v is not None:
                logging.info(f" - Momentum: {mom_v:.4f}")
            if strategy_info.get('fast_ma') and strategy_info.get('slow_ma'):
                spread = (strategy_info['fast_ma'] - strategy_info['slow_ma']) / strategy_info['slow_ma'] * 100 if strategy_info['slow_ma'] else 0
                logging.info(f" - Spread MAs: {spread:.3f}%")
        logging.info(f" - Preço Execução: {price:.4f}")
        logging.info(barra)

    def execute_buy_order(self, pair, quantity, price, strategy_info=None):
        """Executa ordem de compra"""
        try:
            order = self.exchange.create_market_buy_order(pair, quantity)
            self.positions[pair] = {
                'side': 'long',
                'quantity': quantity,
                'entry_price': price,
                'timestamp': datetime.now()
            }
            self._log_structured_execution('BUY', pair, quantity, price, strategy_info)
            return order
        except Exception as e:
            logging.error(f"❌ Erro na compra de {pair}: {e}")
            return None

    def execute_sell_order(self, pair, strategy_info=None):
        """Executa ordem de venda"""
        try:
            if pair not in self.positions:
                logging.warning(f"⚠️ Nenhuma posição para vender em {pair}")
                return None
            position = self.positions[pair]
            quantity = position['quantity']
            order = self.exchange.create_market_sell_order(pair, quantity)
            current_price = self.exchange.fetch_ticker(pair)['last']
            pnl = (current_price - position['entry_price']) * quantity
            pnl_pct = (current_price / position['entry_price'] - 1) * 100
            del self.positions[pair]
            self.trade_history.append({
                'pair': pair,
                'entry_price': position['entry_price'],
                'exit_price': current_price,
                'quantity': quantity,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'timestamp': datetime.now()
            })
            self._log_structured_execution('SELL', pair, quantity, current_price, strategy_info, pnl, pnl_pct)
            return order
        except Exception as e:
            logging.error(f"❌ Erro na venda de {pair}: {e}")
            return None

    def process_signals(self):
        """Processa sinais para todos os pares"""
        logging.info("🔄 Processando sinais...")
        for pair in self.trading_pairs:
            try:
                signal_info = self.generate_ai_signal(pair)
                if signal_info is None:
                    continue
                signal = signal_info['signal']
                price = signal_info['price']
                self.last_signals[pair] = signal_info
                if signal == 1 and pair not in self.positions:
                    quantity, trade_value = self.calculate_position_size(pair, price)
                    if quantity == 0:
                        logging.info(f"⏸️ Skip {pair}: trade_value={trade_value:.2f} < min notional")
                        continue
                    self.execute_buy_order(pair, quantity, price, signal_info)
                elif signal == 2 and pair in self.positions:
                    self.execute_sell_order(pair, signal_info)
                elif signal == 0:
                    logging.info(f"HOLD para {pair} - Preço: ${price:.2f}")
            except Exception as e:
                logging.error(f"❌ Erro ao processar {pair}: {e}")

    def run_trading_session(self, duration_hours=24):
        """Executa sessão de trading"""
        logging.info(f"🚀 Iniciando sessão de trading por {duration_hours}h")
        
        # Inicializa sistemas AI
        self.initialize_ai_systems()
        
        # Mostra saldo inicial
        initial_balance = self.get_account_balance()
        logging.info(f"💰 Saldo inicial: ${initial_balance['total_value']:.2f}")
        
        self.running = True
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        signal_interval = self.signal_interval  # usar do config
        
        try:
            while self.running and datetime.now() < end_time:
                # Processa sinais
                self.process_signals()
                
                # Mostra status
                self.show_status()
                
                # Aguarda próximo ciclo
                time.sleep(signal_interval)
        
        except KeyboardInterrupt:
            logging.info("⏹️ Sessão interrompida pelo usuário")
        
        finally:
            self.running = False
            
            # Fecha todas as posições
            self.close_all_positions()
            
            # Relatório final
            self.generate_final_report(initial_balance)
    
    def close_all_positions(self):
        """Fecha todas as posições abertas"""
        logging.info("🔒 Fechando todas as posições...")
        
        for pair in list(self.positions.keys()):
            self.execute_sell_order(pair)
    
    def show_status(self):
        """Mostra status atual"""
        balance = self.get_account_balance()
        
        logging.info("=" * 50)
        logging.info(f"💰 Saldo: ${balance['total_value']:.2f}")
        logging.info(f"🏦 USDT Livre: ${balance['USDT_free']:.2f}")
        logging.info(f"📊 Posições Abertas: {len(self.positions)}")
        
        for pair, position in self.positions.items():
            current_price = self.exchange.fetch_ticker(pair)['last']
            pnl = (current_price - position['entry_price']) * position['quantity']
            pnl_pct = (current_price / position['entry_price'] - 1) * 100
            
            logging.info(f"   📈 {pair}: ${pnl:.2f} ({pnl_pct:.2f}%)")
        
        # Últimos sinais
        for pair, signal_info in self.last_signals.items():
            signal_name = ['HOLD', 'BUY', 'SELL'][signal_info['signal']]
            logging.info(f"🎯 {pair}: {signal_name} @ ${signal_info['price']:.2f}")
    
    def generate_final_report(self, initial_balance):
        """Gera relatório final"""
        final_balance = self.get_account_balance()
        
        total_return = ((final_balance['total_value'] - initial_balance['total_value']) / 
                       initial_balance['total_value'] * 100)
        
        logging.info("=" * 60)
        logging.info("📊 RELATÓRIO FINAL")
        logging.info("=" * 60)
        logging.info(f"💰 Saldo Inicial: ${initial_balance['total_value']:.2f}")
        logging.info(f"💰 Saldo Final: ${final_balance['total_value']:.2f}")
        logging.info(f"📈 Retorno Total: {total_return:.2f}%")
        logging.info(f"🔄 Total de Trades: {len(self.trade_history)}")
        
        if self.trade_history:
            profitable_trades = [t for t in self.trade_history if t['pnl'] > 0]
            win_rate = len(profitable_trades) / len(self.trade_history) * 100
            avg_pnl = sum(t['pnl'] for t in self.trade_history) / len(self.trade_history)
            
            logging.info(f"🎯 Win Rate: {win_rate:.1f}%")
            logging.info(f"📊 P&L Médio: ${avg_pnl:.2f}")
    
    def save_config(self, filename):
        """Salva configuração"""
        config = {
            'trading_pairs': self.trading_pairs,
            'min_trade_amount': self.min_trade_amount,
            'max_position_size': self.max_position_size,
            'testnet': self.testnet
        }
        
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        
        logging.info(f"💾 Configuração salva: {filename}")

def main():
    """Função principal para teste"""
    
    # IMPORTANTE: Use suas próprias chaves API
    API_KEY = "your_api_key_here"
    API_SECRET = "your_api_secret_here"
    
    if API_KEY == "your_api_key_here":
        print("❌ CONFIGURE SUAS CHAVES API ANTES DE USAR!")
        print("📝 Edite as variáveis API_KEY e API_SECRET")
        return
    
    # Cria bot (TESTNET por segurança)
    bot = BinanceAIBot(
        api_key=API_KEY,
        api_secret=API_SECRET,
        testnet=True  # SEMPRE True para testes!
    )
    
    try:
        # Executa por 1 hora para teste
        bot.run_trading_session(duration_hours=1)
        
    except Exception as e:
        logging.error(f"❌ Erro geral: {e}")
    
    finally:
        logging.info("🏁 Bot finalizado")

if __name__ == "__main__":
    main()
