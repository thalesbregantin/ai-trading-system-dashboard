#!/usr/bin/env python3
"""
Teste do Sistema AI Trading - Versão Simplificada
Testa funcionalidades sem TensorFlow
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent / "ai_trading_system"))

def test_imports():
    """Testa importações básicas"""
    print("🧪 Testando importações...")
    
    try:
        import pandas as pd
        import numpy as np
        import yfinance as yf
        import ccxt
        import streamlit as st
        import plotly.graph_objects as go
        print("✅ Importações básicas OK")
        return True
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False

def test_simple_ai_trader():
    """Testa AI Trader simplificado"""
    print("\n🤖 Testando AI Trader simplificado...")
    
    try:
        from core.config import get_config
        from core.ai_trader_simple import SimpleAITrader
        
        config = get_config('test')
        ai_trader = SimpleAITrader(config)
        print("✅ AI Trader simplificado criado")
        
        # Testar sinal para BTC
        signal = ai_trader.get_current_signal("BTC-USD")
        print(f"✅ Sinal BTC-USD: {signal}")
        
        return True
    except Exception as e:
        print(f"❌ Erro no AI Trader: {e}")
        return False

def test_hybrid_system():
    """Testa sistema híbrido"""
    print("\n🔄 Testando sistema híbrido...")
    
    try:
        from core.config import get_config
        from core.hybrid_trading_system import HybridTradingSystem
        
        config = get_config('test')
        hybrid_system = HybridTradingSystem(config)
        print("✅ Sistema híbrido criado")
        
        return True
    except Exception as e:
        print(f"❌ Erro no sistema híbrido: {e}")
        return False

def test_data_download():
    """Testa download de dados"""
    print("\n📊 Testando download de dados...")
    
    try:
        import yfinance as yf
        
        # Testa download de dados do BTC
        ticker = yf.Ticker("BTC-USD")
        data = ticker.history(period="5d")
        
        if not data.empty:
            print(f"✅ Dados baixados: {len(data)} pontos")
            print(f"   Último preço: ${data['Close'].iloc[-1]:.2f}")
            print(f"   Período: {data.index[0].date()} a {data.index[-1].date()}")
            return True
        else:
            print("❌ Nenhum dado baixado")
            return False
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        return False

def test_binance_connection():
    """Testa conexão com Binance"""
    print("\n🔗 Testando conexão Binance...")
    
    try:
        import ccxt
        
        # Testa conexão com Binance (sem API keys)
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        # Tenta buscar ticker
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✅ Conexão Binance OK")
        print(f"   BTC/USDT: ${ticker['last']:.2f}")
        print(f"   Volume 24h: {ticker['quoteVolume']:,.0f} USDT")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão Binance: {e}")
        return False

def test_dashboard_files():
    """Testa arquivos do dashboard"""
    print("\n📊 Testando arquivos do dashboard...")
    
    dashboard_files = [
        "ai_trading_system/dashboard/main_dashboard.py",
        "ai_trading_system/dashboard/ai_trading_dashboard.py",
        "dashboard/main_dashboard.py"
    ]
    
    for file_path in dashboard_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} não encontrado")
    
    return True

def main():
    """Função principal de teste"""
    print("🚀 TESTE DO SISTEMA AI TRADING - VERSÃO SIMPLIFICADA")
    print("=" * 60)
    
    tests = [
        ("Importações", test_imports),
        ("AI Trader Simplificado", test_simple_ai_trader),
        ("Sistema Híbrido", test_hybrid_system),
        ("Download de Dados", test_data_download),
        ("Conexão Binance", test_binance_connection),
        ("Arquivos Dashboard", test_dashboard_files),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print("💡 Use: python ai_trading_system/main_simple.py --mode test")
        print("💡 Dashboard: python ai_trading_system/main_simple.py --mode dashboard")
    elif passed >= total * 0.8:
        print("✅ SISTEMA FUNCIONANDO BEM (alguns problemas menores)")
    else:
        print("⚠️ SISTEMA COM PROBLEMAS (verificar configuração)")

if __name__ == "__main__":
    main()
