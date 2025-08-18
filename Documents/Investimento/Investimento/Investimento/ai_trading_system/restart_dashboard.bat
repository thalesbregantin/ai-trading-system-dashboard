@echo off
echo ========================================
echo 🚀 AI TRADING DASHBOARD - DADOS REAIS
echo ========================================
echo.
echo 🔄 Parando processos antigos...
taskkill /f /im python.exe /t >nul 2>&1

echo 🐍 Ativando ambiente virtual...
cd /d "c:\Users\motol\Downloads\Investimento\Investimento"
call .venv\Scripts\activate.bat

echo 📦 Instalando dependências necessárias...
cd ai_trading_system
pip install ccxt python-dotenv

echo 🔍 Testando conexão com Binance...
python test_simple_connection.py

echo.
echo 📊 Iniciando dashboard com dados reais...
python main.py --mode dashboard

echo.
echo ❌ Dashboard encerrado. Pressione qualquer tecla para sair.
pause >nul
