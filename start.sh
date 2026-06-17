#!/bin/bash
# =============================================================================
# Mifos Loan Summarizer - Docker Start Script
# =============================================================================

set -e

echo ""
echo "========================================"
echo "Mifos Loan Summarizer - Starting Services"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "[ERROR] Docker is not running!"
    echo ""
    echo "Please start Docker and try again."
    echo ""
    exit 1
fi

echo "[OK] Docker is running"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found!"
    echo ""
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "Please edit .env file with your API keys and run this script again."
    echo ""
    exit 1
fi

echo "[OK] .env file found"
echo ""

# Start services
echo "Starting services..."
docker compose up -d

echo ""
echo "========================================"
echo "Services Started Successfully!"
echo "========================================"
echo ""
echo "Frontend: http://localhost"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "View logs:   docker compose logs -f"
echo "Stop:        docker compose down"
echo "Restart:     docker compose restart"
echo ""

# Wait a bit for services to start
sleep 5

# Check service health
echo "Checking service health..."
echo ""

docker compose ps

echo ""
