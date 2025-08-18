@echo off
echo 🐳 Iniciando AI Trading System com Docker...
echo.

REM Verificar se Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não está instalado!
    echo 📥 Baixe e instale o Docker Desktop: https://www.docker.com/products/docker-desktop/
    echo 🔄 Reinicie o computador após a instalação
    pause
    exit /b 1
)

echo ✅ Docker encontrado
echo.

REM Construir a imagem
echo 🔨 Construindo imagem Docker...
docker-compose build

if errorlevel 1 (
    echo ❌ Erro ao construir imagem
    pause
    exit /b 1
)

echo ✅ Imagem construída com sucesso
echo.

REM Iniciar apenas o dashboard
echo 🚀 Iniciando dashboard...
docker-compose up dashboard

echo.
echo ✅ Dashboard iniciado em: http://localhost:8501
echo.
pause
