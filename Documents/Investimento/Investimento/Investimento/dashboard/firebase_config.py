import firebase_admin
from firebase_admin import credentials, firestore, auth
import json
from datetime import datetime
import os

# Configuração do Firebase
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": "ai-trading-system",
    "private_key_id": "your_private_key_id",
    "private_key": "your_private_key",
    "client_email": "your_client_email",
    "client_id": "your_client_id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "your_cert_url"
}

class FirebaseManager:
    def __init__(self):
        try:
            # Inicializar Firebase Admin SDK
            cred = credentials.Certificate(FIREBASE_CONFIG)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("✅ Firebase conectado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao conectar Firebase: {e}")
            self.db = None
    
    def save_training_log(self, model_name, training_data):
        """Salvar log de treinamento"""
        if not self.db:
            return False
        
        try:
            doc_ref = self.db.collection('training_logs').document()
            doc_ref.set({
                'model_name': model_name,
                'timestamp': datetime.now().isoformat(),
                'episodes': training_data.get('episodes', 0),
                'learning_rate': training_data.get('learning_rate', 0),
                'batch_size': training_data.get('batch_size', 0),
                'accuracy': training_data.get('accuracy', 0),
                'profit': training_data.get('profit', 0),
                'status': training_data.get('status', 'completed'),
                'duration_minutes': training_data.get('duration_minutes', 0)
            })
            print(f"✅ Log de treinamento salvo: {model_name}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar log: {e}")
            return False
    
    def save_trade(self, trade_data):
        """Salvar trade executado"""
        if not self.db:
            return False
        
        try:
            doc_ref = self.db.collection('trades').document()
            doc_ref.set({
                'timestamp': datetime.now().isoformat(),
                'symbol': trade_data.get('symbol', ''),
                'side': trade_data.get('side', ''),
                'amount': trade_data.get('amount', 0),
                'price': trade_data.get('price', 0),
                'profit': trade_data.get('profit', 0),
                'status': trade_data.get('status', 'executed'),
                'ai_confidence': trade_data.get('ai_confidence', 0),
                'model_used': trade_data.get('model_used', '')
            })
            print(f"✅ Trade salvo: {trade_data.get('symbol')}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar trade: {e}")
            return False
    
    def get_training_logs(self, model_name=None, limit=50):
        """Obter logs de treinamento"""
        if not self.db:
            return []
        
        try:
            query = self.db.collection('training_logs')
            if model_name:
                query = query.where('model_name', '==', model_name)
            
            docs = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
            
            logs = []
            for doc in docs:
                log_data = doc.to_dict()
                log_data['id'] = doc.id
                logs.append(log_data)
            
            return logs
        except Exception as e:
            print(f"❌ Erro ao obter logs: {e}")
            return []
    
    def get_trades(self, symbol=None, limit=100):
        """Obter histórico de trades"""
        if not self.db:
            return []
        
        try:
            query = self.db.collection('trades')
            if symbol:
                query = query.where('symbol', '==', symbol)
            
            docs = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
            
            trades = []
            for doc in docs:
                trade_data = doc.to_dict()
                trade_data['id'] = doc.id
                trades.append(trade_data)
            
            return trades
        except Exception as e:
            print(f"❌ Erro ao obter trades: {e}")
            return []
    
    def save_user_settings(self, user_id, settings):
        """Salvar configurações do usuário"""
        if not self.db:
            return False
        
        try:
            doc_ref = self.db.collection('user_settings').document(user_id)
            doc_ref.set({
                'updated_at': datetime.now().isoformat(),
                'api_keys': settings.get('api_keys', {}),
                'trading_config': settings.get('trading_config', {}),
                'appearance': settings.get('appearance', {})
            })
            print(f"✅ Configurações salvas para usuário: {user_id}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar configurações: {e}")
            return False
    
    def get_user_settings(self, user_id):
        """Obter configurações do usuário"""
        if not self.db:
            return None
        
        try:
            doc_ref = self.db.collection('user_settings').document(user_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                return None
        except Exception as e:
            print(f"❌ Erro ao obter configurações: {e}")
            return None

# Instância global
firebase_manager = FirebaseManager()
