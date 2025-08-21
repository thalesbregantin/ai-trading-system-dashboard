@echo off
echo ========================================
echo    AI TRADING SYSTEM - OPTIMIZATION
echo ========================================
echo.

cd /d "%~dp0.."
echo [INFO] Diretório: %CD%
echo [INFO] Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo [INFO] Iniciando Walk-Forward Optimization v8.0...
echo [INFO] Log: logs/genetic_optimizer_v8_production.log
echo.

python -c "from core.walk_forward_optimizer import WalkForwardOptimizerV7; print('🚀 INICIANDO WALK-FORWARD v8.0 PRODUÇÃO...'); optimizer = WalkForwardOptimizerV7(); results = optimizer.run(); print('🎉 WALK-FORWARD v8.0 CONCLUÍDO!')"

echo.
echo [INFO] Otimização concluída!
echo [INFO] Verifique os resultados em: results/
echo [INFO] Logs em: logs/
echo.
pause
