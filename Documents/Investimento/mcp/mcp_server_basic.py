#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import asyncio
import ccxt
from typing import Any, Dict, List
from datetime import datetime

# Configuração da Binance
BINANCE_API_KEY = 'Gm5VZwg3DzYD7FQXiocUsnhU7CYh5omlb8phvcxuEkec8YgVHHk0AhhyCxMRr80b'
BINANCE_SECRET_KEY = 'VxRa16ZG8FaA854JsviUWBHsg3Sbw46WlIjwUsXlR67DM0wUwQhGLtvtN00U0Vch'

class BasicMCPServer:
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
            print("✅ MCP Server: Conexão Binance estabelecida!")
        except Exception as e:
            print(f"❌ MCP Server: Erro na conexão: {e}")
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Obter dados básicos de mercado"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            ohlcv_1m = self.exchange.fetch_ohlcv(symbol, '1m', limit=5)
            
            if not ticker or not ohlcv_1m:
                return {"error": f"Dados não disponíveis para {symbol}"}
            
            current_price = ticker['last']
            price_1m_ago = ohlcv_1m[-2][4] if len(ohlcv_1m) > 1 else current_price
            
            change_1m = ((current_price - price_1m_ago) / price_1m_ago) * 100
            
            return {
                "symbol": symbol,
                "current_price": current_price,
                "change_1m": change_1m,
                "volume_24h": ticker.get('quoteVolume', 0),
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        except Exception as e:
            return {"error": f"Erro ao obter dados: {e}"}
    
    def get_balance(self) -> Dict[str, Any]:
        """Obter saldo da conta"""
        try:
            balance = self.exchange.fetch_balance()
            total_usdt = 0
            
            # USDT direto
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            total_usdt += usdt_balance
            
            # Verificar outras moedas principais
            for symbol in ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE']:
                amount = balance.get(symbol, {}).get('free', 0)
                if amount > 0:
                    try:
                        ticker = self.exchange.fetch_ticker(f'{symbol}/USDT')
                        crypto_value = amount * ticker['last']
                        total_usdt += crypto_value
                    except:
                        pass
            
            return {
                "total_balance_usdt": total_usdt,
                "usdt_balance": usdt_balance,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        except Exception as e:
            return {"error": f"Erro ao obter saldo: {e}"}
    
    def detect_pump_basic(self, symbol: str) -> Dict[str, Any]:
        """Detectar pump básico"""
        try:
            market_data = self.get_market_data(symbol)
            if "error" in market_data:
                return market_data
            
            change_1m = market_data["change_1m"]
            
            # Detecção simples de pump
            if change_1m > 0.5:
                pump_status = "PUMP_DETECTED"
                pump_reason = f"Movimento de {change_1m:.1f}% em 1min"
            elif change_1m > 0.2:
                pump_status = "MOMENTUM"
                pump_reason = f"Momentum de {change_1m:.1f}% em 1min"
            else:
                pump_status = "NO_PUMP"
                pump_reason = f"Movimento de {change_1m:.1f}% (insignificante)"
            
            return {
                **market_data,
                "pump_status": pump_status,
                "pump_reason": pump_reason,
                "should_trade": pump_status in ["PUMP_DETECTED", "MOMENTUM"]
            }
        except Exception as e:
            return {"error": f"Erro na detecção de pump: {e}"}
    
    def get_trading_pairs(self) -> List[str]:
        """Obter lista de pares de trading"""
        try:
            markets = self.exchange.load_markets()
            usdt_pairs = []
            
            for symbol in markets.keys():
                if symbol.endswith('/USDT') and markets[symbol]['active']:
                    usdt_pairs.append(symbol)
            
            return usdt_pairs[:20]  # Limitar a 20 pares para teste
        except Exception as e:
            print(f"❌ Erro ao obter pares: {e}")
            return []

# Função para testar o servidor MCP
def test_mcp_server():
    """Testar funcionalidades básicas do MCP Server"""
    print("🧪 TESTANDO MCP SERVER BÁSICO")
    print("=" * 50)
    
    server = BasicMCPServer()
    
    # Teste 1: Obter saldo
    print("\n1️⃣ Testando obtenção de saldo...")
    balance = server.get_balance()
    print(f"💰 Saldo: ${balance.get('total_balance_usdt', 0):.2f}")
    
    # Teste 2: Obter pares de trading
    print("\n2️⃣ Testando obtenção de pares...")
    pairs = server.get_trading_pairs()
    print(f"📊 Pares encontrados: {len(pairs)}")
    print(f"   Primeiros 5: {pairs[:5]}")
    
    # Teste 3: Detectar pump em DOGE
    print("\n3️⃣ Testando detecção de pump em DOGE/USDT...")
    pump_data = server.detect_pump_basic("DOGE/USDT")
    print(f"📈 Resultado: {pump_data}")
    
    # Teste 4: Dados de mercado
    print("\n4️⃣ Testando dados de mercado BTC/USDT...")
    market_data = server.get_market_data("BTC/USDT")
    print(f"📊 Dados: {market_data}")
    
    print("\n✅ Testes MCP Server concluídos!")

if __name__ == "__main__":
    test_mcp_server()
