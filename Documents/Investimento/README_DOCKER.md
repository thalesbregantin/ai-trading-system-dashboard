# 🐳 AI Trading System - Docker

## 📋 **Resumo**
Este projeto usa Docker para resolver problemas de dependências (especialmente TensorFlow) e fornecer um ambiente isolado e reproduzível.

## 🚀 **Início Rápido**

### **1. Instalar Docker Desktop**
- Baixe: https://www.docker.com/products/docker-desktop/
- Instale e reinicie o computador
- Inicie o Docker Desktop

### **2. Testar Docker**
```bash
test_docker.bat
```

### **3. Iniciar o Sistema**
```bash
start_docker.bat
```

### **4. Acessar Dashboard**
- Abra: http://localhost:8501

## 🔧 **Comandos Docker**

### **Construir imagem:**
```bash
docker-compose build
```

### **Iniciar apenas dashboard:**
```bash
docker-compose up dashboard
```

### **Iniciar tudo:**
```bash
docker-compose up
```

### **Parar tudo:**
```bash
docker-compose down
```

### **Ver logs:**
```bash
docker-compose logs dashboard
```

## 📁 **Estrutura Docker**

### **Serviços Disponíveis:**
- **dashboard**: Interface web (porta 8501)
- **ai-trader**: Sistema de trading AI
- **paper-trading**: Trading simulado
- **worker_0/1**: Workers para otimização

### **Volumes:**
- `./logs` → `/app/logs` (logs do sistema)
- `./data` → `/app/data` (dados históricos)
- `./models` → `/app/models` (modelos AI)

## 🎯 **Vantagens do Docker**

✅ **Resolve problema do TensorFlow** (Long Path)  
✅ **Ambiente isolado** (não afeta sua máquina)  
✅ **Todas as dependências incluídas**  
✅ **Fácil reprodução**  
✅ **Sem conflitos de versão**  

## 🔍 **Troubleshooting**

### **Docker não encontrado:**
- Instale Docker Desktop
- Reinicie o computador

### **Erro de construção:**
- Execute `docker-compose build --no-cache`

### **Porta ocupada:**
- Mude a porta no `docker-compose.yml`

### **Problemas de permissão:**
- Execute como administrador

## 📊 **Monitoramento**

### **Ver containers ativos:**
```bash
docker ps
```

### **Ver uso de recursos:**
```bash
docker stats
```

### **Acessar container:**
```bash
docker exec -it ai-trading-dashboard bash
```

## 🎉 **Pronto!**
Agora você tem um ambiente completo e isolado para o AI Trading System!
