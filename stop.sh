#!/bin/bash
# =============================================================================
# Mifos Loan Summarizer - Docker Stop Script
# =============================================================================

set -e

echo ""
echo "========================================"
echo "Mifos Loan Summarizer - Stopping Services"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "[ERROR] Docker is not running!"
    echo ""
    exit 1
fi

# Stop services
echo "Stopping services..."
docker compose down

echo ""
echo "========================================"
echo "Services Stopped Successfully!"
echo "========================================"
echo ""
