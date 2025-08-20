#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ccxt
import numpy as np
import time
from datetime import datetime
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import threading

# Configuração da Binance
BINANCE_API_KEY = 'Gm5VZwg3DzYD7FQXiocUsnhU7CYh5omlb8phvcxuEkec8YgVHHk0AhhyCxMRr80b'
BINANCE_SECRET_KEY = 'VxRa16ZG8FaA854JsviUWBHsg3Sbw46WlIjwUsXlR67DM0wUwQhGLtvtN00U0Vch'

class MultiCryptoTrader:
    def __init__(self):
        self.exchange = None
        self.trades_log = []
        self.crypto_pairs = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 
            'XRP/USDT', 'SOL/USDT', 'DOT/USDT', 'DOGE/USDT',
            'AVAX/USDT', 'MATIC/USDT', 'LINK/USDT', 'UNI/USDT'
        ]
        self.performance_metrics = {}
        self.lock = threading.Lock()
        
    def setup_binance(self):
        """Configurar conexão com Binance"""
        try:
            self.exchange = ccxt.binance({
                'apiKey': BINANCE_API_KEY,
                'secret': BINANCE_SECRET_KEY,
                'sandbox': False,
                'enableRateLimit': True
            })
            
            # Testar conexão
            balance = self.exchange.fetch_balance()
            print(f"✅ Conexão com Binance estabelecida!")
            print(f"💰 Saldo USDT: {balance.get('USDT', {}).get('free', 0)}")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar com Binance: {e}")
            return False
    
    def calculate_rsi(self, prices, period=14):
        """Calcular RSI"""
        if len(prices) < period + 1:
            return 50
            
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
    
    def calculate_sma(self, prices, period=20):
        """Calcular Média Móvel Simples"""
        if len(prices) < period:
            return prices[-1]
        return np.mean(prices[-period:])
    
    def get_technical_analysis(self, symbol):
        """Análise técnica para uma cripto específica"""
        try:
            # Obter dados OHLCV
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=100)
            
            if len(ohlcv) < 50:
                return None
            
            # Extrair preços de fechamento
            prices = np.array([candle[4] for candle in ohlcv])
            
            # Calcular indicadores
            rsi = self.calculate_rsi(prices)
            sma_20 = self.calculate_sma(prices, 20)
            sma_50 = self.calculate_sma(prices, 50)
            current_price = prices[-1]
            
            # Análise de tendência
            price_change_1h = ((current_price - prices[-2]) / prices[-2]) * 100
            price_change_24h = ((current_price - prices[-24]) / prices[-24]) * 100 if len(prices) >= 24 else 0
            
            # Volume (simulado)
            volume_ratio = 1.0 + (np.random.random() - 0.5) * 0.4
            
            analysis = {
                'symbol': symbol,
                'rsi': rsi,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'current_price': current_price,
                'price_change_1h': price_change_1h,
                'price_change_24h': price_change_24h,
                'volume_ratio': volume_ratio,
                'trend': 'bullish' if sma_20 > sma_50 else 'bearish'
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Erro na análise técnica para {symbol}: {e}")
            return None
    
    def get_ai_signal(self, analysis):
        """Gerar sinal baseado em análise técnica"""
        if not analysis:
            return 'HOLD', 0.5
        
        rsi = analysis['rsi']
        trend = analysis['trend']
        price_change_1h = analysis['price_change_1h']
        volume_ratio = analysis['volume_ratio']
        
        # Lógica de decisão baseada nos resultados de treinamento
        buy_signals = 0
        sell_signals = 0
        
        # RSI (baseado nos resultados: RSI < 30 = compra forte)
        if rsi < 30:
            buy_signals += 2  # Sinal forte
        elif rsi < 40:
            buy_signals += 1
        elif rsi > 70:
            sell_signals += 2  # Sinal forte
        elif rsi > 60:
            sell_signals += 1
        
        # Tendência (baseado nos resultados: tendência é importante)
        if trend == 'bullish':
            buy_signals += 1
        else:
            sell_signals += 1
        
        # Momentum (baseado nos resultados: momentum é crucial)
        if price_change_1h > 2:
            buy_signals += 2
        elif price_change_1h > 1:
            buy_signals += 1
        elif price_change_1h < -2:
            sell_signals += 2
        elif price_change_1h < -1:
            sell_signals += 1
        
        # Volume (confirmação)
        if volume_ratio > 1.2:
            if buy_signals > sell_signals:
                buy_signals += 1
            elif sell_signals > buy_signals:
                sell_signals += 1
        
        # Decisão final (baseada nos resultados de treinamento)
        if buy_signals >= 3:  # Sinal forte de compra
            signal = 'BUY'
            confidence = min(0.95, 0.6 + (buy_signals * 0.1))
        elif sell_signals >= 3:  # Sinal forte de venda
            signal = 'SELL'
            confidence = min(0.95, 0.6 + (sell_signals * 0.1))
        elif buy_signals > sell_signals and buy_signals >= 2:
            signal = 'BUY'
            confidence = 0.7
        elif sell_signals > buy_signals and sell_signals >= 2:
            signal = 'SELL'
            confidence = 0.7
        else:
            signal = 'HOLD'
            confidence = 0.6
        
        return signal, confidence
    
    def calculate_position_size(self, confidence, symbol, balance):
        """Calcular tamanho da posição baseado na confiança e saldo"""
        try:
            # Obter preço atual
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # Calcular valor disponível para trading
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            
            # Distribuir capital entre criptos (máximo 20% por cripto)
            max_per_crypto = usdt_balance * 0.2
            
            # Valor mínimo de $10 por trade (requisito da Binance)
            min_position = 10.0
            
            # Ajustar baseado na confiança
            position_value = max_per_crypto * confidence
            
            # Garantir valor mínimo
            position_value = max(min_position, position_value)
            
            # Calcular quantidade
            amount = position_value / current_price
            
            # Ajustar para precisão da exchange (4 casas decimais para maior flexibilidade)
            if 'BTC' in symbol:
                amount = max(0.00001, round(amount, 4))  # Mínimo 0.00001 BTC
            elif 'ETH' in symbol:
                amount = max(0.001, round(amount, 4))    # Mínimo 0.001 ETH
            elif 'BNB' in symbol:
                amount = max(0.01, round(amount, 4))     # Mínimo 0.01 BNB
            elif 'SOL' in symbol:
                amount = max(0.1, round(amount, 4))      # Mínimo 0.1 SOL
            elif 'XRP' in symbol:
                amount = max(1, round(amount, 4))        # Mínimo 1 XRP
            elif 'ADA' in symbol:
                amount = max(1, round(amount, 4))        # Mínimo 1 ADA
            elif 'DOT' in symbol:
                amount = max(0.1, round(amount, 4))      # Mínimo 0.1 DOT
            elif 'DOGE' in symbol:
                amount = max(1, round(amount, 4))        # Mínimo 1 DOGE
            elif 'AVAX' in symbol:
                amount = max(0.1, round(amount, 4))      # Mínimo 0.1 AVAX
            elif 'MATIC' in symbol:
                amount = max(1, round(amount, 4))        # Mínimo 1 MATIC
            elif 'LINK' in symbol:
                amount = max(0.1, round(amount, 4))      # Mínimo 0.1 LINK
            elif 'UNI' in symbol:
                amount = max(0.1, round(amount, 4))      # Mínimo 0.1 UNI
            else:
                amount = max(0.001, round(amount, 4))    # Padrão
            
            return amount, current_price
            
        except Exception as e:
            print(f"❌ Erro ao calcular posição: {e}")
            return 0, 0
    
    def execute_trade(self, signal, confidence, symbol):
        """Executar trade para uma cripto específica"""
        try:
            if signal == 'HOLD':
                return None
            
            # Obter saldo
            balance = self.exchange.fetch_balance()
            
            # Verificar se podemos fazer o trade
            if signal == 'BUY':
                usdt_balance = balance.get('USDT', {}).get('free', 0)
                if usdt_balance < 10:  # Mínimo $10
                    print(f"❌ Saldo USDT insuficiente para {symbol} (mínimo $10)")
                    return None
            elif signal == 'SELL':
                base_symbol = symbol.split('/')[0]
                base_balance = balance.get(base_symbol, {}).get('free', 0)
                if base_balance <= 0:
                    print(f"❌ Não temos {base_symbol} para vender")
                    return None
                
                # Se temos a cripto, usar todo o saldo disponível
                if base_balance > 0:
                    amount = base_balance  # Vender tudo que temos
                    print(f"📊 Vendendo todo saldo disponível: {amount} {base_symbol}")
            
            # Calcular tamanho da posição
            if signal == 'BUY':
                amount, current_price = self.calculate_position_size(confidence, symbol, balance)
                if amount <= 0:
                    return None
            elif signal == 'SELL':
                # Para venda, usar o preço atual
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                # amount já foi definido acima como base_balance
            
            print(f"🎯 Executando {signal} em {symbol}")
            print(f"📊 Confiança: {confidence:.1%}")
            print(f"💰 Quantidade: {amount}")
            print(f"💵 Preço: ${current_price}")
            print(f"💲 Valor: ${amount * current_price:.2f}")
            
            # Executar ordem
            if signal == 'BUY':
                usdt_balance = balance.get('USDT', {}).get('free', 0)
                usdt_value = amount * current_price
                
                if usdt_balance < usdt_value:
                    print(f"❌ Saldo USDT insuficiente para {symbol}")
                    return None
                
                order = self.exchange.create_market_buy_order(symbol, amount)
                print(f"🟢 COMPRA executada em {symbol}!")
                
            elif signal == 'SELL':
                # Obter símbolo base (ex: BTC de BTC/USDT)
                base_symbol = symbol.split('/')[0]
                base_balance = balance.get(base_symbol, {}).get('free', 0)
                
                if base_balance < amount:
                    print(f"❌ Saldo {base_symbol} insuficiente")
                    return None
                
                order = self.exchange.create_market_sell_order(symbol, amount)
                print(f"🔴 VENDA executada em {symbol}!")
            
            # Registrar trade
            with self.lock:
                trade_info = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'order_id': order['id'],
                    'signal': signal,
                    'confidence': confidence,
                    'price': order['price'],
                    'amount': order['amount'],
                    'status': order['status']
                }
                
                self.trades_log.append(trade_info)
            
            print(f"🎉 Trade executado com sucesso em {symbol}!")
            return order
            
        except Exception as e:
            print(f"❌ Erro ao executar trade em {symbol}: {e}")
            return None
    
    def analyze_crypto(self, symbol):
        """Analisar uma cripto específica"""
        try:
            # Análise técnica
            analysis = self.get_technical_analysis(symbol)
            if not analysis:
                return None
            
            # Gerar sinal
            signal, confidence = self.get_ai_signal(analysis)
            
            # Executar trade se necessário
            if signal != 'HOLD':
                order = self.execute_trade(signal, confidence, symbol)
                if order:
                    return {
                        'symbol': symbol,
                        'signal': signal,
                        'confidence': confidence,
                        'analysis': analysis,
                        'order': order
                    }
            
            return {
                'symbol': symbol,
                'signal': signal,
                'confidence': confidence,
                'analysis': analysis,
                'order': None
            }
            
        except Exception as e:
            print(f"❌ Erro ao analisar {symbol}: {e}")
            return None
    
    def run_multi_crypto_cycle(self):
        """Executar ciclo de trading para todas as criptos"""
        try:
            print("🔄 Iniciando ciclo de trading multi-cripto...")
            
            # Analisar todas as criptos em paralelo
            results = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.analyze_crypto, symbol) for symbol in self.crypto_pairs]
                
                for future in futures:
                    result = future.result()
                    if result:
                        results.append(result)
            
            # Mostrar resumo
            print(f"\n📊 Resumo do ciclo multi-cripto:")
            print(f"🔍 Criptos analisadas: {len(results)}")
            
            buy_signals = [r for r in results if r['signal'] == 'BUY']
            sell_signals = [r for r in results if r['signal'] == 'SELL']
            hold_signals = [r for r in results if r['signal'] == 'HOLD']
            
            print(f"🟢 Sinais de COMPRA: {len(buy_signals)}")
            print(f"🔴 Sinais de VENDA: {len(sell_signals)}")
            print(f"⏸️ Sinais de HOLD: {len(hold_signals)}")
            
            # Mostrar melhores oportunidades
            if buy_signals:
                best_buy = max(buy_signals, key=lambda x: x['confidence'])
                print(f"🎯 Melhor oportunidade de COMPRA: {best_buy['symbol']} (Confiança: {best_buy['confidence']:.1%})")
            
            if sell_signals:
                best_sell = max(sell_signals, key=lambda x: x['confidence'])
                print(f"🎯 Melhor oportunidade de VENDA: {best_sell['symbol']} (Confiança: {best_sell['confidence']:.1%})")
            
            # Mostrar saldo atualizado
            balance = self.exchange.fetch_balance()
            print(f"\n💰 Saldo atualizado:")
            print(f"   USDT: ${balance.get('USDT', {}).get('free', 0):.2f}")
            
            # Mostrar posições em criptos
            crypto_balances = []
            for symbol in self.crypto_pairs:
                base_symbol = symbol.split('/')[0]
                amount = balance.get(base_symbol, {}).get('free', 0)
                if amount > 0:
                    crypto_balances.append(f"{base_symbol}: {amount:.6f}")
            
            if crypto_balances:
                print(f"   Criptos: {', '.join(crypto_balances)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no ciclo multi-cripto: {e}")
            return False
    
    def get_performance_summary(self):
        """Obter resumo de performance"""
        try:
            balance = self.exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            
            # Calcular valor total em criptos
            total_crypto_value = 0
            for symbol in self.crypto_pairs:
                base_symbol = symbol.split('/')[0]
                amount = balance.get(base_symbol, {}).get('free', 0)
                if amount > 0:
                    ticker = self.exchange.fetch_ticker(symbol)
                    crypto_value = amount * ticker['last']
                    total_crypto_value += crypto_value
            
            total_portfolio = usdt_balance + total_crypto_value
            
            return {
                'usdt_balance': usdt_balance,
                'crypto_value': total_crypto_value,
                'total_portfolio': total_portfolio,
                'total_trades': len(self.trades_log),
                'recent_trades': self.trades_log[-5:] if self.trades_log else []
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter resumo: {e}")
            return None

def main():
    """Função principal"""
    print("🚀 AI TRADING SYSTEM - MULTI-CRYPTO")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Criar trader multi-cripto
    trader = MultiCryptoTrader()
    
    # Configurar Binance
    print("\n1️⃣ Configurando Binance...")
    if not trader.setup_binance():
        return
    
    # Mostrar criptos que serão analisadas
    print(f"\n2️⃣ Criptos configuradas ({len(trader.crypto_pairs)}):")
    for i, symbol in enumerate(trader.crypto_pairs, 1):
        print(f"   {i:2d}. {symbol}")
    
    # Mostrar resumo inicial
    print("\n3️⃣ Resumo inicial:")
    summary = trader.get_performance_summary()
    if summary:
        print(f"💰 USDT: ${summary['usdt_balance']:.2f}")
        print(f"📊 Total de trades: {summary['total_trades']}")
    
    print("\n" + "=" * 60)
    
    # Perguntar se quer executar
    response = input("🤔 Quer executar um ciclo de trading multi-cripto? (s/n): ")
    
    if response.lower() == 's':
        print("\n4️⃣ Executando ciclo multi-cripto...")
        success = trader.run_multi_crypto_cycle()
        
        if success:
            print("\n✅ CICLO MULTI-CRYPTO CONCLUÍDO!")
            print("🎯 Sistema multi-cripto funcionando!")
            print("🚀 Pronto para operar automaticamente!")
            
            # Mostrar resumo final
            final_summary = trader.get_performance_summary()
            if final_summary:
                print(f"\n📊 Resumo final:")
                print(f"💰 USDT: ${final_summary['usdt_balance']:.2f}")
                print(f"📈 Valor em criptos: ${final_summary['crypto_value']:.2f}")
                print(f"💼 Portfolio total: ${final_summary['total_portfolio']:.2f}")
                print(f"📊 Total de trades: {final_summary['total_trades']}")
        else:
            print("\n❌ Falha no ciclo multi-cripto")
    else:
        print("👌 Operação cancelada")

if __name__ == "__main__":
    main()
