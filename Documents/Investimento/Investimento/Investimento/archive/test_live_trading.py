#!/usr/bin/env python3
"""
Teste de Configuração de Trading ao Vivo
Verifica se o sistema está pronto para operar em modo LIVE
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório do projeto
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

from config import TradingConfig

def test_live_configuration():
    """Testa configuração para trading ao vivo"""
    
    print("🔥 TESTE DE CONFIGURAÇÃO TRADING AO VIVO")
    print("=" * 60)
    
    # 1. Verificar se LIVE_TRADING está habilitado
    print(f"1️⃣ LIVE_TRADING: {'✅ HABILITADO' if TradingConfig.LIVE_TRADING else '❌ DESABILITADO'}")
    
    # 2. Verificar modo testnet
    print(f"2️⃣ TESTNET_MODE: {'🧪 TESTNET' if TradingConfig.TESTNET_MODE else '🚀 LIVE'}")
    
    # 3. Verificar API Keys
    api_key_ok = TradingConfig.BINANCE_API_KEY != 'your_api_key_here' and len(TradingConfig.BINANCE_API_KEY) > 10
    api_secret_ok = TradingConfig.BINANCE_API_SECRET != 'your_api_secret_here' and len(TradingConfig.BINANCE_API_SECRET) > 10
    
    print(f"3️⃣ API Key: {'✅ CONFIGURADA' if api_key_ok else '❌ NÃO CONFIGURADA'}")
    print(f"4️⃣ API Secret: {'✅ CONFIGURADA' if api_secret_ok else '❌ NÃO CONFIGURADA'}")
    
    if api_key_ok:
        print(f"   🔑 API Key: {TradingConfig.BINANCE_API_KEY[:15]}...")
    
    # 4. Verificar URL da Binance
    binance_url = TradingConfig.get_binance_url()
    print(f"5️⃣ Binance URL: {binance_url}")
    
    # 5. Verificar parâmetros de trading
    print(f"6️⃣ Pares de Trading: {', '.join(TradingConfig.TRADING_PAIRS)}")
    print(f"7️⃣ Capital Inicial: ${TradingConfig.INITIAL_CAPITAL:,.2f}")
    print(f"8️⃣ Max Position Size: {TradingConfig.MAX_POSITION_SIZE:.1%}")
    print(f"9️⃣ Min Trade Amount: ${TradingConfig.MIN_TRADE_AMOUNT}")
    
    # 6. Verificar configurações de risco
    print(f"🔟 Stop Loss: {TradingConfig.STOP_LOSS_PCT:.1%}")
    print(f"1️⃣1️⃣ Take Profit: {TradingConfig.TAKE_PROFIT_PCT:.1%}")
    
    # 7. Validar configuração geral
    print("\n🔍 VALIDAÇÃO GERAL:")
    errors = TradingConfig.validate_config()
    
    if errors:
        print("❌ ERROS ENCONTRADOS:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print("✅ Configuração válida!")
    
    # 8. Status final
    print("\n🎯 STATUS DO SISTEMA:")
    
    if not TradingConfig.LIVE_TRADING:
        print("❌ LIVE_TRADING está DESABILITADO")
        print("   💡 Para habilitar trading ao vivo, configure LIVE_TRADING = True")
        return False
    
    if not api_key_ok or not api_secret_ok:
        print("❌ API Keys da Binance não configuradas corretamente")
        return False
    
    print("✅ Sistema PRONTO para trading ao vivo!")
    
    if TradingConfig.TESTNET_MODE:
        print("🧪 Modo TESTNET - Trading simulado")
        print("   💡 Para trading real, configure TESTNET_MODE = False")
    else:
        print("🚀 Modo LIVE - Trading com dinheiro real!")
        print("   ⚠️ CUIDADO: Operações com capital real!")
    
    return True

def show_next_steps():
    """Mostra próximos passos para começar o trading"""
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("=" * 60)
    
    if TradingConfig.LIVE_TRADING:
        print("1️⃣ Verificar permissões da API na Binance:")
        print("   🔗 https://www.binance.com/en/my/settings/api-management")
        print("   ✅ Habilitar 'Enable Spot & Margin Trading'")
        print()
        
        if TradingConfig.TESTNET_MODE:
            print("2️⃣ Executar teste no TESTNET:")
            print("   📟 python main.py --mode live --env test")
            print()
            print("3️⃣ Se teste OK, mudar para LIVE:")
            print("   ⚙️ Configurar TESTNET_MODE = False")
            print("   📟 python main.py --mode live --env prod")
        else:
            print("2️⃣ EXECUTAR TRADING AO VIVO:")
            print("   📟 python main.py --mode live --env prod")
            print("   ⚠️ ATENÇÃO: Trading com dinheiro real!")
        
        print()
        print("4️⃣ Monitorar via Dashboard:")
        print("   📊 streamlit run dashboard/main_dashboard.py")
        print("   🌐 http://localhost:8501")
        
    else:
        print("❌ LIVE_TRADING está desabilitado")
        print("   💡 Para habilitar: Configure LIVE_TRADING = True no config.py")

if __name__ == "__main__":
    # Executa teste
    success = test_live_configuration()
    
    # Mostra próximos passos
    show_next_steps()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SISTEMA CONFIGURADO PARA TRADING AO VIVO!")
    else:
        print("🔧 CONFIGURAÇÃO PRECISA SER AJUSTADA")
    print("=" * 60)
