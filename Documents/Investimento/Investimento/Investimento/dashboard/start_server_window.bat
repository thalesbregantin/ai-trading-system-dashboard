@echo off
echo 🚀 Iniciando AI Trading API Server em janela separada...
echo 📍 Diretório: %~dp0
echo 🌐 URL: http://localhost:5000
echo.
echo ✅ O servidor está rodando em uma janela separada
echo 💡 Você pode fechar esta janela
echo.

cd /d "%~dp0"
start "AI Trading API Server" powershell -NoExit -Command "python simple_api_server.py"

echo.
echo 🎉 Servidor iniciado! Pode continuar usando o chat normalmente.
pause
