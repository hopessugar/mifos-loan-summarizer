@echo off
REM =============================================================================
REM Mifos Loan Summarizer - Docker Start Script for Windows
REM =============================================================================

echo.
echo ========================================
echo Mifos Loan Summarizer - Starting Services
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo.
    echo Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo.
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo Please edit .env file with your API keys and run this script again.
    echo.
    pause
    exit /b 1
)

echo [OK] .env file found
echo.

REM Start services
echo Starting services...
docker compose up -d

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start services!
    echo.
    echo Check logs with: docker compose logs
    pause
    exit /b 1
)

echo.
echo ========================================
echo Services Started Successfully!
echo ========================================
echo.
echo Frontend: http://localhost
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo View logs:   docker compose logs -f
echo Stop:        docker compose down
echo Restart:     docker compose restart
echo.

REM Wait a bit for services to start
timeout /t 5 /nobreak >nul

REM Check service health
echo Checking service health...
echo.

docker compose ps

echo.
pause
