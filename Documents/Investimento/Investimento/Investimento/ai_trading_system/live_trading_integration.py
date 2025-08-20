#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integração do Sistema de IA com Trade Real
Conecta o sistema de IA treinado com a API da Binance
"""

import sys
import os
import ccxt
import logging
from datetime import datetime
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

from core.config import get_config
from core.hybrid_trading_system import HybridTradingSystem

# Configuração da Binance
BINANCE_API_KEY = 'Gm5VZwg3DzYD7FQXiocUsnhU7CYh5omlb8phvcxuEkec8YgVHHk0AhhyCxMRr80b'
BINANCE_SECRET_KEY = 'VxRa16ZG8FaA854JsviUWBHsg3Sbw46WlIjwUsXlR67DM0wUwQhGLtvtN00U0Vch'

class LiveTradingIntegration:
    def __init__(self):
        self.config = get_config('prod')
        self.exchange = None
        self.hybrid_system = None
        self.setup_logging()
        
    def setup_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/live_integration.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
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
            self.logger.info("Conexao com Binance estabelecida!")
            self.logger.info(f"Saldo USDT: {balance.get('USDT', {}).get('free', 0)}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao conectar com Binance: {e}")
            return False
    
    def setup_ai_system(self):
        """Configurar sistema de IA"""
        try:
            self.hybrid_system = HybridTradingSystem(self.config)
            self.logger.info("Sistema de IA configurado!")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao configurar IA: {e}")
            return False
    
    def get_market_data(self, symbol='BTC/USDT', limit=100):
        """Obter dados de mercado da Binance"""
        try:
            # Obter dados OHLCV
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=limit)
            
            # Converter para formato esperado pelo sistema
            prices = [candle[4] for candle in ohlcv]  # Preços de fechamento
            
            self.logger.info(f"Dados obtidos: {len(prices)} pontos")
            return prices
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados: {e}")
            return None
    
    def get_ai_signal(self, symbol='BTC/USDT'):
        """Obter sinal da IA usando dados reais"""
        try:
            # Obter dados de mercado
            prices = self.get_market_data(symbol)
            if not prices:
                return None
            
            # Usar sistema híbrido para gerar sinal
            signal = self.hybrid_system.generate_signal(prices, len(prices) - 1)
            
            self.logger.info(f"Sinal da IA: {signal}")
            return signal
            
        except Exception as e:
            self.logger.error(f"Erro ao obter sinal da IA: {e}")
            return None
    
    def execute_trade(self, signal, symbol='BTC/USDT', amount=0.0001):
        """Executar trade baseado no sinal da IA"""
        try:
            if signal == 'HOLD':
                self.logger.info("Sinal HOLD - Nenhum trade executado")
                return None
            
            # Obter preço atual
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            self.logger.info(f"Executando trade: {signal}")
            self.logger.info(f"Preco atual: ${current_price}")
            self.logger.info(f"Quantidade: {amount} BTC")
            
            # Verificar saldo
            balance = self.exchange.fetch_balance()
            
            if signal == 'BUY':
                usdt_balance = balance.get('USDT', {}).get('free', 0)
                usdt_value = amount * current_price
                
                if usdt_balance < usdt_value:
                    self.logger.error(f"Saldo USDT insuficiente: ${usdt_balance}")
                    return False
                
                order = self.exchange.create_market_buy_order(symbol, amount)
                self.logger.info("COMPRA executada!")
                
            elif signal == 'SELL':
                btc_balance = balance.get('BTC', {}).get('free', 0)
                
                if btc_balance < amount:
                    self.logger.error(f"Saldo BTC insuficiente: {btc_balance}")
                    return False
                
                order = self.exchange.create_market_sell_order(symbol, amount)
                self.logger.info("VENDA executada!")
            
            self.logger.info(f"Trade executado com sucesso!")
            self.logger.info(f"Order ID: {order['id']}")
            self.logger.info(f"Preco: ${order['price']}")
            self.logger.info(f"Status: {order['status']}")
            
            return order
            
        except Exception as e:
            self.logger.error(f"Erro ao executar trade: {e}")
            return False
    
    def run_live_trading_cycle(self):
        """Executar um ciclo completo de trading com IA real"""
        try:
            self.logger.info("Iniciando ciclo de trading...")
            
            # 1. Obter sinal da IA
            signal = self.get_ai_signal()
            if not signal:
                return False
            
            # 2. Executar trade se necessário
            if signal != 'HOLD':
                order = self.execute_trade(signal)
                if order:
                    # 3. Mostrar resumo
                    balance = self.exchange.fetch_balance()
                    usdt_balance = balance.get('USDT', {}).get('free', 0)
                    btc_balance = balance.get('BTC', {}).get('free', 0)
                    
                    self.logger.info(f"Resumo: USDT ${usdt_balance:.2f}, BTC {btc_balance:.6f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no ciclo de trading: {e}")
            return False

def main():
    """Função principal"""
    print("🚀 AI TRADING SYSTEM - INTEGRAÇÃO COMPLETA")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Criar integração
    integration = LiveTradingIntegration()
    
    # Configurar Binance
    print("\n1️⃣ Configurando Binance...")
    if not integration.setup_binance():
        return
    
    # Configurar IA
    print("\n2️⃣ Configurando sistema de IA...")
    if not integration.setup_ai_system():
        return
    
    # Mostrar resumo inicial
    print("\n3️⃣ Resumo da conta:")
    balance = integration.exchange.fetch_balance()
    print(f"💰 USDT: ${balance.get('USDT', {}).get('free', 0):.2f}")
    print(f"₿ BTC: {balance.get('BTC', {}).get('free', 0):.6f}")
    
    print("\n" + "=" * 60)
    
    # Perguntar se quer executar
    response = input("🤔 Quer executar um ciclo de trading com IA real? (s/n): ")
    
    if response.lower() == 's':
        print("\n4️⃣ Executando ciclo de trading...")
        success = integration.run_live_trading_cycle()
        
        if success:
            print("\n✅ CICLO DE TRADING CONCLUÍDO!")
            print("🎯 Sistema de IA integrado funcionando!")
            print("🚀 Pronto para operar automaticamente!")
        else:
            print("\n❌ Falha no ciclo de trading")
    else:
        print("👌 Operação cancelada")

if __name__ == "__main__":
    main()
