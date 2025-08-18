# 🔐 Configuração de Permissões Binance API

## 📋 Permissões Recomendadas para Trading Bot

Baseado na sua tela da Binance, aqui estão as configurações recomendadas:

### ✅ **PERMISSÕES OBRIGATÓRIAS**

1. **Habilitar Leitura** ✅
   - Necessária para ler saldo, histórico, etc.

2. **Ativar Trading Spot e de Margem** ✅  
   - Necessária para executar compras e vendas

3. **Habilitar Saques** ❌
   - **NÃO HABILITAR** por segurança
   - Bot não precisa sacar fundos

4. **Permitir Transferência Universal** ❌
   - **NÃO HABILITAR** por segurança
   - Bot não precisa transferir entre contas

5. **Habilitar Empréstimo, Reembolso e Transferência de Margem** ❌
   - **NÃO HABILITAR** por segurança
   - Trading spot não precisa de margem

6. **Ativar Lista de Permissões do Símbolo** ✅
   - **HABILITAR** e configurar apenas: BTC/USDT, ETH/USDT

### 🔒 **RESTRIÇÕES DE IP**

**IMPORTANTE**: Configure restrição de IP para máxima segurança:
- Adicione apenas o IP do seu computador/servidor
- **Nunca deixe "Irrestrito"** em produção

### ⚙️ **Como Configurar**

1. **Acesse sua API Key na Binance**
2. **Clique em "Editar restrições"**
3. **Configure as permissões conforme listado acima**
4. **Adicione seu IP atual nas restrições**
5. **Salve as alterações**

---

## 🚨 **CONFIGURAÇÃO DE SEGURANÇA CRÍTICA**

### Para o nosso bot, você deve:

✅ **HABILITAR:**
- Habilitar Leitura
- Ativar Trading Spot e de Margem  
- Ativar Lista de Permissões (apenas BTC/USDT, ETH/USDT)

❌ **NÃO HABILITAR:**
- Habilitar Saques
- Permitir Transferência Universal
- Habilitar Empréstimo/Margem

🔒 **RESTRINGIR IP:**
- Adicione apenas seu IP atual
- Nunca deixe irrestrito

---

## 💡 **Verificação das Permissões**

Após configurar, você pode testar com:
```bash
python test_binance_connection.py
```

O teste verificará se todas as permissões necessárias estão ativas e funcionando corretamente.
