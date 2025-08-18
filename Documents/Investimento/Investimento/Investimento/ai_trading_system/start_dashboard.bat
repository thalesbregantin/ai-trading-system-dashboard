@echo off
echo 🚀 Iniciando seu Dashboard IA de Investimentos...
echo.
echo 💰 Monitorando seus $100 em tempo real
echo 🤖 Conectando com a IA...
echo.
cd /d "c:\Users\motol\Downloads\Investimento\Investimento\ai_trading_system"
call .venv\Scripts\activate
streamlit run dashboard\main_dashboard.py --server.port 8501
echo.
echo ✅ Dashboard disponível em: http://localhost:8501
echo 💡 Mantenha esta janela aberta!
pause
