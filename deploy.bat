@echo off
REM =============================================================================
REM Mifos Loan Summarizer - Complete Deployment Script
REM =============================================================================

echo.
echo ========================================
echo Mifos Loan Summarizer - Deployment
echo ========================================
echo.

REM Check if Docker Desktop is running
echo Checking Docker status...
docker info >nul 2>&1
if errorlevel 1 (
    echo [INFO] Docker is not running. Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    
    echo.
    echo Waiting for Docker to start (this may take 30-60 seconds)...
    echo.
    
    REM Wait for Docker to be ready (max 2 minutes)
    set /a counter=0
    :WAIT_LOOP
    timeout /t 5 /nobreak >nul
    docker info >nul 2>&1
    if errorlevel 1 (
        set /a counter+=1
        if %counter% lss 24 (
            echo Still waiting... (%counter%/24)
            goto WAIT_LOOP
        ) else (
            echo.
            echo [ERROR] Docker failed to start after 2 minutes.
            echo Please ensure Docker Desktop is installed and try starting it manually.
            pause
            exit /b 1
        )
    )
    echo.
    echo [OK] Docker is now running!
) else (
    echo [OK] Docker is already running
)

echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo.
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo [IMPORTANT] Please edit .env file with your API keys!
    echo.
    echo Opening .env file for editing...
    notepad .env
    echo.
    echo After saving your API keys, press any key to continue...
    pause >nul
)

echo [OK] .env file found
echo.

REM Display configuration summary
echo ========================================
echo Configuration Summary
echo ========================================
findstr /B "LLM_PRIMARY= LLM_MODEL= GEMINI_API_KEY= GROQ_API_KEY=" .env
echo.

REM Stop any existing containers
echo ========================================
echo Cleaning up old containers...
echo ========================================
docker compose down 2>nul
echo.

REM Build images
echo ========================================
echo Building Docker Images...
echo ========================================
echo.
echo This will take 3-5 minutes on first run...
echo.

docker compose build
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo.
    echo Check the error messages above.
    echo Common issues:
    echo   - Invalid Dockerfile syntax
    echo   - Network connection issues
    echo   - Insufficient disk space
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Build completed successfully!
echo.

REM Start services
echo ========================================
echo Starting Services...
echo ========================================
echo.

docker compose up -d
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start services!
    echo.
    echo View logs with: docker compose logs
    pause
    exit /b 1
)

echo.
echo [OK] Services started!
echo.

REM Wait for services to initialize
echo Waiting for services to initialize (60 seconds)...
timeout /t 60 /nobreak >nul

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.

REM Show service status
echo Service Status:
docker compose ps
echo.

echo ========================================
echo Access Points:
echo ========================================
echo.
echo   Frontend:  http://localhost
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo   Health:    http://localhost:8000/health
echo.

REM Test health endpoint
echo ========================================
echo Testing Backend Health...
echo ========================================
echo.
curl -s http://localhost:8000/health
if errorlevel 1 (
    echo [WARNING] Health check failed - services may still be starting
    echo.
    echo Check logs with: docker compose logs -f
) else (
    echo.
    echo [OK] Backend is healthy!
)

echo.
echo ========================================
echo Quick Commands:
echo ========================================
echo   View logs:      docker compose logs -f
echo   Restart:        docker compose restart
echo   Stop:           docker compose down
echo   Rebuild:        docker compose build --no-cache
echo.
echo Opening frontend in browser...
timeout /t 3 /nobreak >nul
start http://localhost

echo.
echo Press any key to exit...
pause >nul
