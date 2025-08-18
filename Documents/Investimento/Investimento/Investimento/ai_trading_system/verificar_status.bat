@echo off
title 🔍 Verificar Conta Binance
color 0B
echo.
echo ================================================================
echo 🔍 VERIFICAÇÃO DA SUA CONTA BINANCE
echo 💰 Checando se está tudo pronto para trading
echo ================================================================
echo.

cd /d "c:\Users\motol\Downloads\Investimento\Investimento\ai_trading_system"
call .venv\Scripts\activate

echo 🔄 Conectando com sua conta...
echo.

python verificar_conta.py

echo.
echo ================================================================
echo 💡 Próximos passos:
echo    - Se tudo OK: execute TRADING_REAL.bat
echo    - Para dashboard: execute start_dashboard.bat
echo ================================================================
pause
