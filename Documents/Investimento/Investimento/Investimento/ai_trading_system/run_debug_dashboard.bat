@echo off
echo ===================================
echo 🔍 AI TRADING DASHBOARD - DEBUG
echo ===================================
echo.
echo 🛑 Parando processos antigos...
taskkill /f /im python.exe /t >nul 2>&1

echo 🐍 Ativando ambiente virtual...
cd /d "c:\Users\motol\Downloads\Investimento\Investimento"
call .venv\Scripts\activate.bat

echo 🔍 Iniciando dashboard de debug...
cd ai_trading_system
streamlit run dashboard_debug.py --server.port 8502

echo.
echo ❌ Dashboard de debug encerrado.
pause
