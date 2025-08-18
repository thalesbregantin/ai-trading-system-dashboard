@echo off
title 🤖 Relatório IA de Investimentos
color 0A
echo.
echo ================================================================
echo 🚀 RELATÓRIO RÁPIDO - SUA IA DE INVESTIMENTOS
echo 💰 Verificando seus $100 na Binance...
echo ================================================================
echo.

cd /d "c:\Users\motol\Downloads\Investimento\Investimento\ai_trading_system"
call .venv\Scripts\activate

echo 🔄 Conectando com sua conta...
echo.

python relatorio_terminal.py

echo.
echo ================================================================
echo 💡 Para configurar dados reais: edite relatorio_terminal.py
echo 🔄 Para atualizar: execute este arquivo novamente
echo 🌐 Para dashboard web: execute start_dashboard.bat
echo ================================================================
pause
