#!/usr/bin/env python3
"""
Teste simples do treinamento
"""

import yfinance as yf
import numpy as np
from ai_trading_system.core.ai_trader_dqn import train_ai_trader

def test_training():
    print("🧪 Teste de Treinamento")
    print("=" * 30)
    
    # Baixar dados
    print("📊 Baixando dados...")
    ticker = yf.Ticker('BTC-USD')
    data = ticker.history(period='30d')
    prices = data['Close'].values
    
    print(f"✅ Dados: {len(prices)} pontos")
    print(f"📈 Primeiros 5 preços: {prices[:5]}")
    print(f"📉 Últimos 5 preços: {prices[-5:]}")
    
    # Testar treinamento
    print("\n🎓 Iniciando treinamento...")
    try:
        trader, equities = train_ai_trader(
            prices, 
            episodes=5, 
            window_size=10, 
            initial_capital=1000
        )
        
        if trader is not None:
            print("✅ Treinamento concluído com sucesso!")
            print(f"📊 Episódios treinados: {len(equities)}")
            print(f"💰 Último equity: {equities[-1]:.2f}")
            
            # Salvar modelo
            trader.model.save("test_model.h5")
            print("💾 Modelo salvo: test_model.h5")
        else:
            print("❌ Treinamento falhou - trader é None")
            
    except Exception as e:
        print(f"❌ Erro no treinamento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_training()
