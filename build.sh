#!/bin/bash
# =============================================================================
# Mifos Loan Summarizer - Docker Build Script
# =============================================================================

set -e

echo ""
echo "========================================"
echo "Mifos Loan Summarizer - Docker Build"
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

# Build backend
echo "========================================"
echo "Building Backend..."
echo "========================================"
docker compose build backend

echo ""
echo "[OK] Backend built successfully"
echo ""

# Build frontend
echo "========================================"
echo "Building Frontend..."
echo "========================================"
docker compose build frontend

echo ""
echo "[OK] Frontend built successfully"
echo ""

echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "To start the services, run:"
echo "  docker compose up -d"
echo ""
echo "Or use: ./start.sh"
echo ""
