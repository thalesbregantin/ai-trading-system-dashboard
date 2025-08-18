@echo off
echo 🐳 Testando Docker para AI Trading System...
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

REM Testar se Docker está rodando
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não está rodando!
    echo 🚀 Inicie o Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker está rodando
echo.

REM Testar construção da imagem
echo 🔨 Testando construção da imagem...
docker-compose build --no-cache

if errorlevel 1 (
    echo ❌ Erro ao construir imagem
    pause
    exit /b 1
)

echo ✅ Imagem construída com sucesso!
echo 🎉 Docker está funcionando perfeitamente!
echo.
echo 📋 Próximos passos:
echo 1. Execute: start_docker.bat
echo 2. Acesse: http://localhost:8501
echo.
pause
