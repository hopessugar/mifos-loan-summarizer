@echo off
REM =============================================================================
REM Mifos Loan Summarizer - Docker Stop Script for Windows
REM =============================================================================

echo.
echo ========================================
echo Mifos Loan Summarizer - Stopping Services
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo.
    pause
    exit /b 1
)

REM Stop services
echo Stopping services...
docker compose down

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to stop services!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Services Stopped Successfully!
echo ========================================
echo.
pause
