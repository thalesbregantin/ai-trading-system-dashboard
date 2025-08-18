#!/usr/bin/env python3
"""
Teste Simples de Multi-Pair Training
Treina múltiplos pares sequencialmente para verificar funcionamento
"""

import sys
import os
sys.path.append('ai_trading_system')

from ai_trading_system.core.config import get_config
from ai_trading_system.core.hybrid_trading_system import train_hybrid_system
import yfinance as yf

def test_multi_pairs():
    """Testa treinamento de múltiplos pares"""
    print("🚀 TESTE MULTI-PAIR TRAINING")
    print("=" * 50)
    
    # Configuração
    config = get_config('test')
    
    # Pares para testar (poucos para teste rápido)
    test_pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    
    results = {}
    
    for i, pair in enumerate(test_pairs, 1):
        print(f"\n📊 TREINANDO PAR {i}/{len(test_pairs)}: {pair}")
        print("-" * 30)
        
        try:
            # Converte símbolo
            yf_symbol = config.YFINANCE_SYMBOLS.get(pair, pair)
            print(f"📈 Símbolo Yahoo Finance: {yf_symbol}")
            
            # Baixa dados
            ticker = yf.Ticker(yf_symbol)
            data = ticker.history(period='6mo')  # 6 meses para teste rápido
            
            if data.empty:
                print(f"❌ Falha ao baixar dados para {pair}")
                continue
                
            prices = data['Close'].values
            print(f"✅ {len(prices)} pontos de dados baixados")
            
            # Treina (poucos episódios para teste)
            trader, equities = train_hybrid_system(
                prices,
                episodes=5,  # Poucos episódios para teste rápido
                window_size=config.AI_WINDOW_SIZE,
                initial_capital=config.INITIAL_CAPITAL
            )
            
            if trader and equities:
                final_equity = equities[-1] if equities else config.INITIAL_CAPITAL
                return_pct = ((final_equity - config.INITIAL_CAPITAL) / config.INITIAL_CAPITAL) * 100
                
                results[pair] = {
                    'final_equity': final_equity,
                    'return_pct': return_pct,
                    'episodes': len(equities)
                }
                
                print(f"✅ {pair}: ${final_equity:.2f} ({return_pct:+.2f}%)")
                
                # Salva modelo
                model_path = f"models/ai_model_{pair.replace('/', '_')}.h5"
                os.makedirs('models', exist_ok=True)
                trader.model.save(model_path)
                print(f"💾 Modelo salvo: {model_path}")
                
            else:
                print(f"❌ Falha no treinamento de {pair}")
                
        except Exception as e:
            print(f"❌ Erro em {pair}: {e}")
            continue
    
    # Resumo final
    print(f"\n🎯 RESUMO DO MULTI-PAIR TRAINING")
    print("=" * 50)
    print(f"📊 Pares testados: {len(results)}/{len(test_pairs)}")
    
    if results:
        total_return = sum(r['return_pct'] for r in results.values())
        avg_return = total_return / len(results)
        best_pair = max(results.items(), key=lambda x: x[1]['return_pct'])
        worst_pair = min(results.items(), key=lambda x: x[1]['return_pct'])
        
        print(f"💰 Retorno Total: {total_return:+.2f}%")
        print(f"📈 Retorno Médio: {avg_return:+.2f}%")
        print(f"🏆 Melhor: {best_pair[0]} ({best_pair[1]['return_pct']:+.2f}%)")
        print(f"📉 Pior: {worst_pair[0]} ({worst_pair[1]['return_pct']:+.2f}%)")
        print("✅ Multi-pair training funcionando!")
    else:
        print("❌ Nenhum par treinado com sucesso")
    
    return results

if __name__ == "__main__":
    test_multi_pairs()
