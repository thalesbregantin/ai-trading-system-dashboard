#!/usr/bin/env python3
"""
Conversor BRL para USDT na Binance
Ajuda a converter seus R$ 100 para USDT para começar o trading
"""

import ccxt
from datetime import datetime

# Credenciais
API_KEY = "Jsga4pAg9nndc0JmoWVt9w8rd9xQHxNFK7oxn11lKWtwS86MpruPbEdGXnkdkOzM"
API_SECRET = "7q8w7cWMkUvytSG1bFzYOosRzLrl4AOWk6v3Q1EMYOQcDer0R88EL5b7TP5opU2M"

def converter_brl_para_usdt():
    """Converte BRL para USDT para começar o trading"""
    print("💱 CONVERSOR BRL → USDT")
    print("=" * 40)
    
    try:
        # Conecta à Binance
        exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        # Verifica saldo atual
        balance = exchange.fetch_balance()
        saldo_brl = balance.get('BRL', {}).get('free', 0)
        saldo_usdt = balance.get('USDT', {}).get('free', 0)
        
        print(f"💰 Saldo atual:")
        print(f"   BRL: R$ {saldo_brl:.2f}")
        print(f"   USDT: $ {saldo_usdt:.2f}")
        
        if saldo_brl <= 0:
            print("❌ Você não tem BRL suficiente para converter")
            return
        
        # Verifica se existe o par BRL/USDT
        try:
            ticker_brl_usdt = exchange.fetch_ticker('BRL/USDT')
            preco_brl_usdt = ticker_brl_usdt['last']
            print(f"📊 Taxa de câmbio BRL/USDT: {preco_brl_usdt:.4f}")
            
            # Calcula quanto USDT você pode comprar
            usdt_disponivel = saldo_brl * preco_brl_usdt
            print(f"💵 Com R$ {saldo_brl:.2f} você pode comprar: $ {usdt_disponivel:.2f} USDT")
            
        except Exception as e:
            print(f"⚠️ Par BRL/USDT não disponível: {e}")
            
            # Tenta via BTC
            try:
                print("\n🔄 Tentando conversão via BTC...")
                ticker_brl_btc = exchange.fetch_ticker('BRL/BTC')
                ticker_btc_usdt = exchange.fetch_ticker('BTC/USDT')
                
                preco_brl_btc = ticker_brl_btc['last']
                preco_btc_usdt = ticker_btc_usdt['last']
                
                print(f"📊 BRL/BTC: {preco_brl_btc:.8f}")
                print(f"📊 BTC/USDT: $ {preco_btc_usdt:.2f}")
                
                # Calcula conversão indireta
                btc_disponivel = saldo_brl * preco_brl_btc
                usdt_disponivel = btc_disponivel * preco_btc_usdt
                
                print(f"💵 Conversão indireta BRL → BTC → USDT:")
                print(f"   R$ {saldo_brl:.2f} → {btc_disponivel:.8f} BTC → $ {usdt_disponivel:.2f} USDT")
                
            except Exception as e2:
                print(f"❌ Erro na conversão via BTC: {e2}")
                return
        
        # Pergunta se quer fazer a conversão
        print(f"\n🤔 IMPORTANTE:")
        print(f"   Para usar o sistema de trading AI, você precisa de USDT")
        print(f"   Seus R$ {saldo_brl:.2f} podem virar aproximadamente $ {usdt_disponivel:.2f} USDT")
        
        print(f"\n⚠️ ATENÇÃO:")
        print(f"   Esta conversão usa dinheiro REAL!")
        print(f"   O trading também usa dinheiro REAL!")
        print(f"   Pode haver perdas!")
        
        confirmacao = input("\n❓ Quer fazer a conversão BRL → USDT? (digite 'CONFIRMO'): ")
        
        if confirmacao != 'CONFIRMO':
            print("❌ Conversão cancelada")
            print("💡 Você pode fazer isso manualmente no app da Binance também")
            return
        
        # Executa a conversão (CUIDADO - DINHEIRO REAL!)
        print("\n🔄 Executando conversão...")
        
        try:
            # Tenta ordem direta BRL/USDT
            try:
                amount_to_convert = saldo_brl * 0.99  # Deixa um pouco de margem
                order = exchange.create_market_sell_order('BRL/USDT', amount_to_convert)
                print(f"✅ Conversão BRL → USDT executada!")
                print(f"📋 ID da ordem: {order['id']}")
                
            except:
                # Fallback: BRL → BTC → USDT
                print("🔄 Tentando conversão via BTC...")
                
                # Primeiro: BRL → BTC
                amount_brl = saldo_brl * 0.99
                order1 = exchange.create_market_sell_order('BRL/BTC', amount_brl)
                print(f"✅ Primeira etapa: BRL → BTC (ID: {order1['id']})")
                
                # Aguarda um pouco
                import time
                time.sleep(2)
                
                # Segundo: BTC → USDT
                balance_novo = exchange.fetch_balance()
                saldo_btc = balance_novo.get('BTC', {}).get('free', 0)
                
                if saldo_btc > 0:
                    order2 = exchange.create_market_sell_order('BTC/USDT', saldo_btc)
                    print(f"✅ Segunda etapa: BTC → USDT (ID: {order2['id']})")
                
            # Verifica resultado final
            time.sleep(3)
            balance_final = exchange.fetch_balance()
            saldo_usdt_final = balance_final.get('USDT', {}).get('free', 0)
            
            print(f"\n🎉 CONVERSÃO CONCLUÍDA!")
            print(f"💰 Novo saldo USDT: $ {saldo_usdt_final:.2f}")
            print(f"💡 Agora você pode usar o sistema de trading AI!")
            
        except Exception as e:
            print(f"❌ Erro na conversão: {e}")
            print("💡 Tente fazer a conversão manualmente no app da Binance")
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")

def verificar_status_pos_conversao():
    """Verifica o status após conversão"""
    print("\n🔍 VERIFICANDO STATUS APÓS CONVERSÃO...")
    
    try:
        exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
        })
        
        balance = exchange.fetch_balance()
        
        print(f"💰 Status atual:")
        print(f"   BRL: R$ {balance.get('BRL', {}).get('free', 0):.2f}")
        print(f"   USDT: $ {balance.get('USDT', {}).get('free', 0):.2f}")
        print(f"   BTC: {balance.get('BTC', {}).get('free', 0):.8f}")
        print(f"   ETH: {balance.get('ETH', {}).get('free', 0):.6f}")
        
        saldo_usdt = balance.get('USDT', {}).get('free', 0)
        
        if saldo_usdt >= 10:
            print(f"\n✅ PRONTO PARA TRADING!")
            print(f"💡 Você tem $ {saldo_usdt:.2f} USDT para começar!")
            print(f"🤖 Pode rodar: python main.py --mode live")
        else:
            print(f"\n⚠️ Saldo USDT baixo: $ {saldo_usdt:.2f}")
            print(f"💡 Mínimo recomendado: $ 10.00 USDT")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    converter_brl_para_usdt()
    verificar_status_pos_conversao()
