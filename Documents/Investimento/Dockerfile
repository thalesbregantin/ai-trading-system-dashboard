# Dockerfile para AI Trading System
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (para cache)
COPY requirements.txt .
COPY requirements-crypto.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-crypto.txt && \
    pip install --no-cache-dir streamlit plotly && \
    pip install --no-cache-dir tensorflow-cpu==2.15.0

# Copiar código do projeto
COPY . .

# Expor porta do Streamlit
EXPOSE 8501

# Comando padrão
CMD ["streamlit", "run", "dashboard/main_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
