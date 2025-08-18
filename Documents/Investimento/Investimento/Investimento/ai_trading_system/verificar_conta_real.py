#!/usr/bin/env python3
"""
Verificação Detalhada da Conta Binance Real
"""

import ccxt
import os
from datetime import datetime

# Credenciais
API_KEY = "Jsga4pAg9nndc0JmoWVt9w8rd9xQHxNFK7oxn11lKWtwS86MpruPbEdGXnkdkOzM"
API_SECRET = "7q8w7cWMkUvytSG1bFzYOosRzLrl4AOWk6v3Q1EMYOQcDer0R88EL5b7TP5opU2M"

def verificar_conta_completa():
    """Verificação completa da conta"""
    print("🔍 VERIFICAÇÃO DETALHADA DA CONTA BINANCE")
    print("=" * 60)
    
    try:
        # Conecta à Binance REAL (não testnet)
        exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}  # Modo spot
        })
        
        # NÃO usar sandbox (conta real)
        # exchange.set_sandbox_mode(False)  # Já é False por padrão
        
        print("🔗 Conectando à Binance REAL...")
        
        # Teste 1: Informações da conta
        print("\n📊 Teste 1: Informações da Conta")
        try:
            account = exchange.fetch_account()
            print(f"✅ Conta carregada: {account['id'] if 'id' in account else 'N/A'}")
            print(f"✅ Tipo de conta: {account.get('accountType', 'SPOT')}")
            print(f"✅ Permissões: {account.get('permissions', [])}")
        except Exception as e:
            print(f"❌ Erro nas informações da conta: {e}")
        
        # Teste 2: Saldo detalhado
        print("\n💰 Teste 2: Saldo Detalhado")
        try:
            balance = exchange.fetch_balance()
            print(f"✅ Saldo carregado com {len(balance)} moedas")
            
            # Mostra todas as moedas com saldo > 0
            moedas_com_saldo = []
            for currency, amounts in balance.items():
                if isinstance(amounts, dict) and amounts.get('total', 0) > 0:
                    moedas_com_saldo.append((currency, amounts))
            
            if moedas_com_saldo:
                print(f"💰 Encontradas {len(moedas_com_saldo)} moedas com saldo:")
                for currency, amounts in moedas_com_saldo:
                    print(f"   {currency}: Total={amounts['total']:.8f} | Livre={amounts['free']:.8f} | Usado={amounts['used']:.8f}")
            else:
                print("⚠️ Nenhuma moeda com saldo > 0 encontrada")
                
            # Mostra info de USDT especificamente
            usdt_info = balance.get('USDT', {})
            print(f"\n💵 USDT específico:")
            print(f"   Total: {usdt_info.get('total', 0):.8f}")
            print(f"   Livre: {usdt_info.get('free', 0):.8f}")
            print(f"   Usado: {usdt_info.get('used', 0):.8f}")
            
        except Exception as e:
            print(f"❌ Erro no saldo: {e}")
        
        # Teste 3: Status da API
        print("\n🔑 Teste 3: Status da API")
        try:
            status = exchange.fetch_status()
            print(f"✅ Status da exchange: {status}")
        except Exception as e:
            print(f"❌ Erro no status: {e}")
        
        # Teste 4: Preços de mercado (para verificar conectividade)
        print("\n📈 Teste 4: Preços de Mercado")
        try:
            ticker_btc = exchange.fetch_ticker('BTC/USDT')
            ticker_eth = exchange.fetch_ticker('ETH/USDT')
            print(f"✅ BTC/USDT: ${ticker_btc['last']:,.2f}")
            print(f"✅ ETH/USDT: ${ticker_eth['last']:,.2f}")
        except Exception as e:
            print(f"❌ Erro nos preços: {e}")
        
        # Teste 5: Histórico de ordens (se existir)
        print("\n📋 Teste 5: Histórico de Ordens")
        try:
            orders = exchange.fetch_orders('BTC/USDT', limit=5)
            print(f"✅ Ordens BTC/USDT: {len(orders)} encontradas")
            
            if orders:
                for order in orders[:3]:  # Mostra apenas 3
                    print(f"   {order['datetime']} | {order['side']} | {order['amount']} | Status: {order['status']}")
            else:
                print("   Nenhuma ordem encontrada")
                
        except Exception as e:
            print(f"❌ Erro nas ordens: {e}")
        
        # Teste 6: Trades executados
        print("\n🔄 Teste 6: Histórico de Trades")
        try:
            trades = exchange.fetch_my_trades('BTC/USDT', limit=5)
            print(f"✅ Trades BTC/USDT: {len(trades)} encontrados")
            
            if trades:
                for trade in trades[:3]:
                    print(f"   {trade['datetime']} | {trade['side']} | ${trade['cost']:.2f}")
            else:
                print("   Nenhum trade encontrado")
                
        except Exception as e:
            print(f"❌ Erro nos trades: {e}")
        
        print(f"\n🎉 VERIFICAÇÃO CONCLUÍDA às {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        print("\n💡 Possíveis soluções:")
        print("1. Verifique se as chaves API estão corretas")
        print("2. Verifique se as permissões incluem 'Spot & Margin Trading'")
        print("3. Verifique se não há restrições de IP")
        print("4. Verifique se a conta não está restrita")

if __name__ == "__main__":
    verificar_conta_completa()
