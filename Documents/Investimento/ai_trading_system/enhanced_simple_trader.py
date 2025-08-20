#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ccxt
import numpy as np
import time
from datetime import datetime
import json

# Configuração da Binance
BINANCE_API_KEY = 'Gm5VZwg3DzYD7FQXiocUsnhU7CYh5omlb8phvcxuEkec8YgVHHk0AhhyCxMRr80b'
BINANCE_SECRET_KEY = 'VxRa16ZG8FaA854JsviUWBHsg3Sbw46WlIjwUsXlR67DM0wUwQhGLtvtN00U0Vch'

class EnhancedSimpleTrader:
    def __init__(self):
        self.exchange = None
        self.trades_log = []
        
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
            return 50  # Valor neutro se não há dados suficientes
            
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
            return prices[-1]  # Retorna último preço se não há dados suficientes
        return np.mean(prices[-period:])
    
    def get_technical_analysis(self, symbol='BTC/USDT'):
        """Análise técnica real"""
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
            
            # Volume (simulado para simplificar)
            volume_ratio = 1.0 + (np.random.random() - 0.5) * 0.4  # ±20%
            
            analysis = {
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
            print(f"❌ Erro na análise técnica: {e}")
            return None
    
    def get_ai_signal(self, analysis):
        """Gerar sinal baseado em análise técnica"""
        if not analysis:
            return 'HOLD', 0.5
        
        rsi = analysis['rsi']
        trend = analysis['trend']
        price_change_1h = analysis['price_change_1h']
        volume_ratio = analysis['volume_ratio']
        
        # Lógica de decisão
        buy_signals = 0
        sell_signals = 0
        
        # RSI
        if rsi < 30:
            buy_signals += 1
        elif rsi > 70:
            sell_signals += 1
        
        # Tendência
        if trend == 'bullish':
            buy_signals += 1
        else:
            sell_signals += 1
        
        # Momentum
        if price_change_1h > 1:
            buy_signals += 1
        elif price_change_1h < -1:
            sell_signals += 1
        
        # Volume
        if volume_ratio > 1.1:
            if buy_signals > sell_signals:
                buy_signals += 1
            elif sell_signals > buy_signals:
                sell_signals += 1
        
        # Decisão final
        if buy_signals > sell_signals and buy_signals >= 2:
            signal = 'BUY'
            confidence = min(0.9, 0.5 + (buy_signals * 0.1))
        elif sell_signals > buy_signals and sell_signals >= 2:
            signal = 'SELL'
            confidence = min(0.9, 0.5 + (sell_signals * 0.1))
        else:
            signal = 'HOLD'
            confidence = 0.6
        
        return signal, confidence
    
    def execute_trade(self, signal, confidence, symbol='BTC/USDT'):
        """Executar trade baseado no sinal"""
        try:
            if signal == 'HOLD':
                print(f"⏸️ Sinal HOLD - Nenhum trade executado")
                return None
            
            # Calcular tamanho da posição baseado na confiança
            base_amount = 0.0001  # Quantidade base
            position_multiplier = confidence  # Usar confiança como multiplicador
            amount = base_amount * position_multiplier
            
            # Obter preço atual
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            print(f"🎯 Executando trade: {signal}")
            print(f"📊 Confiança: {confidence:.1%}")
            print(f"💰 Quantidade: {amount:.6f} BTC")
            print(f"💵 Preço atual: ${current_price}")
            
            # Verificar saldo
            balance = self.exchange.fetch_balance()
            
            if signal == 'BUY':
                usdt_balance = balance.get('USDT', {}).get('free', 0)
                usdt_value = amount * current_price
                
                if usdt_balance < usdt_value:
                    print(f"❌ Saldo USDT insuficiente: ${usdt_balance}")
                    return False
                
                order = self.exchange.create_market_buy_order(symbol, amount)
                print(f"🟢 COMPRA executada!")
                
            elif signal == 'SELL':
                btc_balance = balance.get('BTC', {}).get('free', 0)
                
                if btc_balance < amount:
                    print(f"❌ Saldo BTC insuficiente: {btc_balance}")
                    return False
                
                order = self.exchange.create_market_sell_order(symbol, amount)
                print(f"🔴 VENDA executada!")
            
            # Registrar trade
            trade_info = {
                'timestamp': datetime.now().isoformat(),
                'order_id': order['id'],
                'signal': signal,
                'confidence': confidence,
                'price': order['price'],
                'amount': order['amount'],
                'status': order['status']
            }
            
            self.trades_log.append(trade_info)
            
            print(f"🎉 Trade executado com sucesso!")
            print(f"📋 Order ID: {order['id']}")
            print(f"💰 Preço: ${order['price']}")
            print(f"📊 Status: {order['status']}")
            
            return order
            
        except Exception as e:
            print(f"❌ Erro ao executar trade: {e}")
            return False
    
    def run_trading_cycle(self):
        """Executar um ciclo completo de trading"""
        try:
            print("🔄 Iniciando ciclo de trading...")
            
            # 1. Análise técnica
            analysis = self.get_technical_analysis()
            if not analysis:
                return False
            
            print(f"📊 Análise Técnica:")
            print(f"   RSI: {analysis['rsi']:.1f}")
            print(f"   SMA 20: ${analysis['sma_20']:.2f}")
            print(f"   SMA 50: ${analysis['sma_50']:.2f}")
            print(f"   Tendência: {analysis['trend']}")
            print(f"   Variação 1h: {analysis['price_change_1h']:.2f}%")
            
            # 2. Gerar sinal
            signal, confidence = self.get_ai_signal(analysis)
            print(f"🧠 Sinal da IA: {signal} (Confiança: {confidence:.1%})")
            
            # 3. Executar trade se necessário
            if signal != 'HOLD':
                order = self.execute_trade(signal, confidence)
                if order:
                    # 4. Mostrar resumo
                    balance = self.exchange.fetch_balance()
                    usdt_balance = balance.get('USDT', {}).get('free', 0)
                    btc_balance = balance.get('BTC', {}).get('free', 0)
                    
                    print(f"📊 Resumo: USDT ${usdt_balance:.2f}, BTC {btc_balance:.6f}")
                    print(f"📈 Total de trades: {len(self.trades_log)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no ciclo de trading: {e}")
            return False

def main():
    """Função principal"""
    print("🚀 AI TRADING SYSTEM - VERSÃO MELHORADA")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Criar trader
    trader = EnhancedSimpleTrader()
    
    # Configurar Binance
    print("\n1️⃣ Configurando Binance...")
    if not trader.setup_binance():
        return
    
    # Mostrar resumo inicial
    print("\n2️⃣ Resumo da conta:")
    balance = trader.exchange.fetch_balance()
    print(f"💰 USDT: ${balance.get('USDT', {}).get('free', 0):.2f}")
    print(f"₿ BTC: {balance.get('BTC', {}).get('free', 0):.6f}")
    
    print("\n" + "=" * 60)
    
    # Perguntar se quer executar
    response = input("🤔 Quer executar um ciclo de trading com análise técnica? (s/n): ")
    
    if response.lower() == 's':
        print("\n3️⃣ Executando ciclo de trading...")
        success = trader.run_trading_cycle()
        
        if success:
            print("\n✅ CICLO DE TRADING CONCLUÍDO!")
            print("🎯 Sistema com análise técnica funcionando!")
            print("🚀 Pronto para operar automaticamente!")
        else:
            print("\n❌ Falha no ciclo de trading")
    else:
        print("👌 Operação cancelada")

if __name__ == "__main__":
    main()
