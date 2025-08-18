"""
Guia Rápido de Configuração Binance API
"""

def show_binance_permissions():
    print("🔐 CONFIGURAÇÃO BINANCE API - GUIA RÁPIDO")
    print("=" * 60)
    
    print("""
📋 BASEADO NA SUA TELA DA BINANCE:

✅ HABILITAR ESTAS OPÇÕES:

1️⃣ Habilitar Leitura ✅
   └── Permite ler saldo, preços, histórico

2️⃣ Ativar Trading Spot e de Margem ✅  
   └── Permite comprar e vender criptomoedas

3️⃣ Ativar Lista de Permissões do Símbolo ✅
   └── Configure para: BTC/USDT, ETH/USDT apenas


❌ NÃO HABILITAR (SEGURANÇA):

4️⃣ Habilitar Saques ❌
   └── PERIGOSO - Bot não precisa sacar

5️⃣ Permitir Transferência Universal ❌
   └── PERIGOSO - Bot não precisa transferir

6️⃣ Habilitar Empréstimo, Reembolso e Transferência de Margem ❌
   └── DESNECESSÁRIO - Usamos apenas spot trading


🔒 RESTRIÇÕES DE IP:

7️⃣ ADICIONAR SEU IP ✅
   └── NUNCA deixar "Irrestrito"
   └── Máxima segurança
""")

def show_step_by_step():
    print("""
🔧 PASSO A PASSO:

1. Na tela da Binance que você mostrou:
   ✅ Marque: "Habilitar Leitura"
   ✅ Marque: "Ativar Trading Spot e de Margem"
   ❌ Deixe DESMARCADO: "Habilitar Saques"
   ❌ Deixe DESMARCADO: "Permitir Transferência Universal"
   ❌ Deixe DESMARCADO: "Habilitar Empréstimo..."

2. Na seção "Ativar Lista de Permissões do Símbolo":
   ✅ Marque esta opção
   ✅ Adicione apenas: BTCUSDT, ETHUSDT

3. Na seção "Restrições de acesso por IP":
   ✅ Adicione seu IP atual
   ❌ NUNCA deixe irrestrito

4. Clique em "Salvar"

5. Teste a configuração:
   python test_binance_connection.py
""")

def get_ip_info():
    print("""
🌐 COMO DESCOBRIR SEU IP:

Método 1: Site
   └── Acesse: https://whatismyipaddress.com/

Método 2: Google
   └── Pesquise: "qual meu ip"

Método 3: Terminal
   └── Execute: curl ifconfig.me

⚠️ IMPORTANTE:
   • Use o IP público (não 192.168.x.x)
   • Se usar internet móvel, o IP pode mudar
   • Configure múltiplos IPs se necessário
""")

def security_warnings():
    print("""
🚨 AVISOS DE SEGURANÇA:

🔴 CRÍTICO:
   • NUNCA compartilhe suas API keys
   • SEMPRE use testnet primeiro
   • Configure IP restrito OBRIGATÓRIO
   • Monitore atividade regularmente

⚠️ IMPORTANTE:
   • Comece com valores pequenos
   • Use apenas capital que pode perder
   • Mantenha logs atualizados
   • Revise permissões periodicamente

✅ BOAS PRÁTICAS:
   • API keys separadas para bot e trading manual
   • Backup seguro das configurações
   • Alertas de atividade suspeita
   • Revisão mensal das permissões
""")

if __name__ == "__main__":
    show_binance_permissions()
    show_step_by_step()
    get_ip_info()
    security_warnings()
    
    print("\n" + "=" * 60)
    print("✅ GUIA COMPLETO EXIBIDO!")
    print("🔧 Configure as permissões conforme acima")
    print("🧪 Depois execute: python test_binance_connection.py")
    print("=" * 60)
