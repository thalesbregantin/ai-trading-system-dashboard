#!/usr/bin/env python3
"""
Script para configurar Firebase automaticamente
"""

import json
import os
import sys

def create_firebase_config():
    """Criar arquivo de configuração do Firebase"""
    
    print("🔥 Configurando Firebase para AI Trading System")
    print("=" * 50)
    
    # Verificar se arquivo já existe
    if os.path.exists('firebase-service-account.json'):
        print("✅ Arquivo firebase-service-account.json já existe!")
        print("📝 Atualizando configuração...")
    else:
        print("❌ Arquivo firebase-service-account.json não encontrado!")
        print("\n📋 Para obter o arquivo:")
        print("1. Acesse: https://console.firebase.google.com/")
        print("2. Crie um projeto chamado 'ai-trading-system'")
        print("3. Vá em Configurações do Projeto > Contas de Serviço")
        print("4. Clique em 'Gerar nova chave privada'")
        print("5. Baixe o arquivo JSON")
        print("6. Renomeie para 'firebase-service-account.json'")
        print("7. Coloque na pasta dashboard/")
        
        response = input("\n🤔 Você já tem o arquivo? (s/n): ")
        if response.lower() != 's':
            print("❌ Por favor, obtenha o arquivo primeiro!")
            return False
    
    # Ler arquivo de configuração
    try:
        with open('firebase-service-account.json', 'r') as f:
            firebase_config = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo firebase-service-account.json não encontrado!")
        return False
    except json.JSONDecodeError:
        print("❌ Arquivo JSON inválido!")
        return False
    
    # Atualizar firebase_config.py
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
            # Inicializar Firebase Admin SDK
            cred = credentials.Certificate(FIREBASE_CONFIG)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("✅ Firebase conectado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao conectar Firebase: {{e}}")
            self.db = None
    
    def save_training_log(self, model_name, training_data):
        """Salvar log de treinamento"""
        if not self.db:
            return False
        
        try:
            doc_ref = self.db.collection('training_logs').document()
            doc_ref.set({{
                'model_name': model_name,
                'timestamp': datetime.now().isoformat(),
                'episodes': training_data.get('episodes', 0),
                'learning_rate': training_data.get('learning_rate', 0),
                'batch_size': training_data.get('batch_size', 0),
                'accuracy': training_data.get('accuracy', 0),
                'profit': training_data.get('profit', 0),
                'status': training_data.get('status', 'completed'),
                'duration_minutes': training_data.get('duration_minutes', 0)
            }})
            print(f"✅ Log de treinamento salvo: {{model_name}}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar log: {{e}}")
            return False
    
    def save_trade(self, trade_data):
        """Salvar trade executado"""
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
                'status': trade_data.get('status', 'executed'),
                'ai_confidence': trade_data.get('ai_confidence', 0),
                'model_used': trade_data.get('model_used', '')
            }})
            print(f"✅ Trade salvo: {{trade_data.get('symbol')}}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar trade: {{e}}")
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
            print(f"❌ Erro ao obter logs: {{e}}")
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
            print(f"❌ Erro ao obter trades: {{e}}")
            return []
    
    def save_user_settings(self, user_id, settings):
        """Salvar configurações do usuário"""
        if not self.db:
            return False
        
        try:
            doc_ref = self.db.collection('user_settings').document(user_id)
            doc_ref.set({{
                'updated_at': datetime.now().isoformat(),
                'api_keys': settings.get('api_keys', {{}}),
                'trading_config': settings.get('trading_config', {{}}),
                'appearance': settings.get('appearance', {{}})
            }})
            print(f"✅ Configurações salvas para usuário: {{user_id}}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar configurações: {{e}}")
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
            print(f"❌ Erro ao obter configurações: {{e}}")
            return None

# Instância global
firebase_manager = FirebaseManager()
'''
    
    # Salvar arquivo
    with open('firebase_config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Arquivo firebase_config.py criado/atualizado!")
    
    # Testar conexão
    print("\n🧪 Testando conexão com Firebase...")
    try:
        from firebase_config import firebase_manager
        if firebase_manager.db:
            print("✅ Conexão com Firebase estabelecida!")
            
            # Criar coleções de teste
            print("📝 Criando coleções de teste...")
            
            # Teste de trade
            test_trade = {
                'symbol': 'BTC/USDT',
                'side': 'BUY',
                'amount': 0.001,
                'price': 42150.50,
                'profit': 25.30,
                'status': 'executed',
                'ai_confidence': 85,
                'model_used': 'BTC_Model_v1'
            }
            
            if firebase_manager.save_trade(test_trade):
                print("✅ Teste de trade realizado!")
            
            # Teste de log de treinamento
            test_training = {
                'episodes': 1000,
                'learning_rate': 0.001,
                'batch_size': 64,
                'accuracy': 78.5,
                'profit': 1234.56,
                'status': 'completed',
                'duration_minutes': 45
            }
            
            if firebase_manager.save_training_log('BTC_Model_v1', test_training):
                print("✅ Teste de log de treinamento realizado!")
            
            print("\n🎉 Firebase configurado com sucesso!")
            print("📊 Dados de teste salvos no banco")
            
        else:
            print("❌ Falha na conexão com Firebase")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Firebase: {{e}}")
        return False
    
    return True

def main():
    """Função principal"""
    print("🚀 Setup Firebase - AI Trading System")
    print("=" * 40)
    
    if create_firebase_config():
        print("\n✅ Setup concluído com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Deploy no Railway/Render")
        print("2. Deploy do frontend no Vercel")
        print("3. Configurar CORS")
        print("4. Testar sistema completo")
        print("\n📖 Consulte o arquivo CLOUD_DEPLOY_GUIDE.md para detalhes")
    else:
        print("\n❌ Setup falhou!")
        print("🔧 Verifique os erros acima e tente novamente")

if __name__ == "__main__":
    main()
