import json
import os

print("🔥 Configurando Firebase para AI Trading System")
print("=" * 50)

# Verificar se arquivo existe
if os.path.exists('firebase-service-account.json'):
    print("✅ Arquivo firebase-service-account.json encontrado!")
    
    # Ler configuração
    with open('firebase-service-account.json', 'r') as f:
        firebase_config = json.load(f)
    
    print("✅ Configuração do Firebase carregada!")
    print(f"📊 Projeto ID: {firebase_config.get('project_id', 'N/A')}")
    
    # Criar firebase_config.py
    config_content = f'''import firebase_admin
from firebase_admin import credentials, firestore, auth
import json
from datetime import datetime
import os

# Configuração do Firebase
FIREBASE_CONFIG = {json.dumps(firebase_config, indent=4)}

class FirebaseManager:
    def __init__(self):
        try:
            cred = credentials.Certificate(FIREBASE_CONFIG)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("✅ Firebase conectado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao conectar Firebase: {{e}}")
            self.db = None
    
    def save_trade(self, trade_data):
        if not self.db:
            return False
        try:
            doc_ref = self.db.collection('trades').document()
            doc_ref.set({{
                'timestamp': datetime.now().isoformat(),
                'symbol': trade_data.get('symbol', ''),
                'side': trade_data.get('side', ''),
                'amount': trade_data.get('amount', 0),
                'price': trade_data.get('price', 0),
                'profit': trade_data.get('profit', 0),
                'status': trade_data.get('status', 'executed')
            }})
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar trade: {{e}}")
            return False
    
    def get_trades(self, limit=100):
        if not self.db:
            return []
        try:
            docs = self.db.collection('trades').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
            trades = []
            for doc in docs:
                trade_data = doc.to_dict()
                trade_data['id'] = doc.id
                trades.append(trade_data)
            return trades
        except Exception as e:
            print(f"❌ Erro ao obter trades: {{e}}")
            return []

firebase_manager = FirebaseManager()
'''
    
    with open('firebase_config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Arquivo firebase_config.py criado!")
    
    # Testar conexão
    print("\n🧪 Testando conexão...")
    try:
        from firebase_config import firebase_manager
        if firebase_manager.db:
            print("✅ Firebase conectado com sucesso!")
            
            # Teste de trade
            test_trade = {
                'symbol': 'BTC/USDT',
                'side': 'BUY',
                'amount': 0.001,
                'price': 42150.50,
                'profit': 25.30,
                'status': 'executed'
            }
            
            if firebase_manager.save_trade(test_trade):
                print("✅ Teste de trade realizado!")
            
            print("\n🎉 Firebase configurado com sucesso!")
        else:
            print("❌ Falha na conexão")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
else:
    print("❌ Arquivo firebase-service-account.json não encontrado!")
