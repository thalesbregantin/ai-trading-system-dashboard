@echo off
title 📊 Exportar para Excel/JSON
color 0B
echo.
echo ================================================================
echo 📊 EXPORTADOR DE DADOS - IA DE INVESTIMENTOS
echo 📄 Criando arquivo JSON para Excel/Google Sheets...
echo ================================================================
echo.

cd /d "c:\Users\motol\Downloads\Investimento\Investimento\ai_trading_system"
call .venv\Scripts\activate

echo 🔄 Coletando dados da sua conta...
echo.

python exportar_dados.py

echo.
echo ================================================================
echo 📄 Arquivo 'portfolio_data.json' criado!
echo 💡 Você pode:
echo    - Abrir no Excel (Dados ^> Obter Dados ^> De Arquivo ^> JSON)
echo    - Usar no Google Sheets 
echo    - Analisar em qualquer programa
echo ================================================================
pause
