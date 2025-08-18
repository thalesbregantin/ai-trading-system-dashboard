@echo off
echo 🚀 Iniciando AI Trading API Server...
echo 📍 Diretório: C:\Users\tbregantin\Documents\Investimento\Investimento\Investimento\dashboard
echo 🌐 URL: http://localhost:5000
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

cd /d "C:\Users\tbregantin\Documents\Investimento\Investimento\Investimento\dashboard"
"C:\temp\tf_env\Scripts\python.exe" "C:\Users\tbregantin\Documents\Investimento\Investimento\Investimento\dashboard\simple_api_server.py"

pause
