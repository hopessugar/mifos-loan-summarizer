@echo off
REM =============================================================================
REM Mifos Loan Summarizer - Docker Build Script for Windows
REM =============================================================================

echo.
echo ========================================
echo Mifos Loan Summarizer - Docker Build
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

REM Build backend
echo ========================================
echo Building Backend...
echo ========================================
docker compose build backend
if errorlevel 1 (
    echo.
    echo [ERROR] Backend build failed!
    pause
    exit /b 1
)

echo.
echo [OK] Backend built successfully
echo.

REM Build frontend
echo ========================================
echo Building Frontend...
echo ========================================
docker compose build frontend
if errorlevel 1 (
    echo.
    echo [ERROR] Frontend build failed!
    pause
    exit /b 1
)

echo.
echo [OK] Frontend built successfully
echo.

echo ========================================
echo Build Complete!
echo ========================================
echo.
echo To start the services, run:
echo   docker compose up -d
echo.
echo Or use start.bat script
echo.
pause
