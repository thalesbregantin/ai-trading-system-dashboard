#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ccxt
import time
from datetime import datetime
import json

# Configuração da Binance
BINANCE_API_KEY = 'Gm5VZwg3DzYD7FQXiocUsnhU7CYh5omlb8phvcxuEkec8YgVHHk0AhhyCxMRr80b'
BINANCE_SECRET_KEY = 'VxRa16ZG8FaA854JsviUWBHsg3Sbw46WlIjwUsXlR67DM0wUwQhGLtvtN00U0Vch'

class MarketAnalyzer:
    def __init__(self):
        self.exchange = None
        self.setup_binance()
        
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
            print("✅ Conexão Binance estabelecida!")
            return True
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def get_all_usdt_pairs(self):
        """Obter todos os pares USDT disponíveis"""
        try:
            markets = self.exchange.load_markets()
            usdt_pairs = []
            
            for symbol in markets.keys():
                if symbol.endswith('/USDT') and markets[symbol]['active']:
                    usdt_pairs.append(symbol)
            
            print(f"📊 Total de pares USDT encontrados: {len(usdt_pairs)}")
            return usdt_pairs
        except Exception as e:
            print(f"❌ Erro ao obter pares: {e}")
            return []
    
    def analyze_market_movement(self, symbol, threshold=0.1):
        """Analisar movimento de um par específico"""
        try:
            ohlcv_1m = self.exchange.fetch_ohlcv(symbol, '1m', limit=5)
            ohlcv_5m = self.exchange.fetch_ohlcv(symbol, '5m', limit=5)
            
            if len(ohlcv_1m) < 2 or len(ohlcv_5m) < 2:
                return None
            
            current_price = ohlcv_1m[-1][4]
            price_1m_ago = ohlcv_1m[-2][4]
            price_5m_ago = ohlcv_5m[-2][4]
            
            change_1m = ((current_price - price_1m_ago) / price_1m_ago) * 100
            change_5m = ((current_price - price_5m_ago) / price_5m_ago) * 100
            
            # Qualquer movimento acima do threshold
            if abs(change_1m) > threshold or abs(change_5m) > threshold:
                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'change_1m': change_1m,
                    'change_5m': change_5m,
                    'movement': 'UP' if change_1m > 0 else 'DOWN',
                    'strength': max(abs(change_1m), abs(change_5m))
                }
            
            return None
            
        except Exception as e:
            return None
    
    def scan_all_markets(self, threshold=0.1, max_pairs=50):
        """Escanear todos os mercados"""
        print(f"🔍 ESCANEANDO MERCADOS - Threshold: {threshold}%")
        print("=" * 60)
        
        usdt_pairs = self.get_all_usdt_pairs()
        if not usdt_pairs:
            return
        
        # Limitar para não sobrecarregar
        pairs_to_scan = usdt_pairs[:max_pairs]
        print(f"📊 Escaneando {len(pairs_to_scan)} pares...")
        
        movements = []
        total_scanned = 0
        
        for symbol in pairs_to_scan:
            total_scanned += 1
            if total_scanned % 10 == 0:
                print(f"⏳ Progresso: {total_scanned}/{len(pairs_to_scan)}")
            
            movement = self.analyze_market_movement(symbol, threshold)
            if movement:
                movements.append(movement)
            
            time.sleep(0.1)  # Rate limit
        
        # Ordenar por força do movimento
        movements.sort(key=lambda x: x['strength'], reverse=True)
        
        print(f"\n📊 RESULTADOS DO ESCANEAMENTO:")
        print(f"   🔍 Pares escaneados: {total_scanned}")
        print(f"   🚀 Movimentos detectados: {len(movements)}")
        print(f"   📈 Threshold usado: {threshold}%")
        
        if movements:
            print(f"\n🏆 TOP 10 MOVIMENTOS:")
            for i, movement in enumerate(movements[:10], 1):
                print(f"   {i:2d}. {movement['symbol']:12s} | {movement['movement']:4s} | 1min: {movement['change_1m']:+6.2f}% | 5min: {movement['change_5m']:+6.2f}% | ${movement['current_price']:8.4f}")
        else:
            print(f"\n❌ NENHUM MOVIMENTO DETECTADO!")
            print(f"   💡 Tente reduzir o threshold para {threshold/2}%")
        
        return movements
    
    def test_different_thresholds(self):
        """Testar diferentes thresholds"""
        print("🧪 TESTANDO DIFERENTES THRESHOLDS")
        print("=" * 60)
        
        thresholds = [0.5, 0.3, 0.2, 0.1, 0.05]
        
        for threshold in thresholds:
            print(f"\n🔍 Testando threshold: {threshold}%")
            movements = self.scan_all_markets(threshold, max_pairs=30)
            
            if movements:
                print(f"✅ {len(movements)} movimentos encontrados!")
                break
            else:
                print(f"❌ Nenhum movimento com {threshold}%")
        
        return movements

def main():
    print("🔍 MARKET ANALYZER - BINANCE")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    analyzer = MarketAnalyzer()
    
    if not analyzer.setup_binance():
        return
    
    # Escolher modo
    print("\n🎯 ESCOLHA O MODO:")
    print("1. Escanear com threshold específico")
    print("2. Testar diferentes thresholds")
    
    choice = input("\nEscolha (1/2): ")
    
    if choice == "1":
        threshold = float(input("Threshold (%): ") or "0.1")
        analyzer.scan_all_markets(threshold)
    else:
        analyzer.test_different_thresholds()

if __name__ == "__main__":
    main()
