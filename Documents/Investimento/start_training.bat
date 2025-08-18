@echo off
echo 🚀 Iniciando Treinamento AI Trading com Workers...
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

REM Verificar se Docker está rodando
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não está rodando!
    echo 🚀 Inicie o Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker está rodando
echo.

REM Construir imagem
echo 🔨 Construindo imagem Docker...
docker-compose -f docker-compose-workers.yml build

if errorlevel 1 (
    echo ❌ Erro ao construir imagem
    pause
    exit /b 1
)

echo ✅ Imagem construída com sucesso
echo.

REM Iniciar workers
echo 🚀 Iniciando workers de treinamento...
docker-compose -f docker-compose-workers.yml up -d

if errorlevel 1 (
    echo ❌ Erro ao iniciar workers
    pause
    exit /b 1
)

echo ✅ Workers iniciados com sucesso!
echo.
echo 📊 Dashboard de treinamento: http://localhost:8502
echo 📋 Para ver logs: docker-compose -f docker-compose-workers.yml logs -f
echo 🛑 Para parar: docker-compose -f docker-compose-workers.yml down
echo.
pause
