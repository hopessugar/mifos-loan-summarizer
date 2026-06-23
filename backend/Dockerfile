# ============================================================================
# Multi-stage build for smaller, more secure image
# ============================================================================
FROM python:3.11-slim as builder

WORKDIR /build

# Install system dependencies needed for compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies to user directory
RUN pip install --no-cache-dir --user --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --user -r requirements.txt

# Download NLTK data to a temporary location
RUN python -c "import nltk; nltk.download('punkt', download_dir='/tmp/nltk_data'); nltk.download('punkt_tab', download_dir='/tmp/nltk_data')"

# ============================================================================
# Final stage - minimal runtime image
# ============================================================================
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /usr/local/share/nltk_data && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy NLTK data from builder
COPY --from=builder --chown=appuser:appuser /tmp/nltk_data /usr/local/share/nltk_data

# Copy application code (excluding files in .dockerignore)
COPY --chown=appuser:appuser . .

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8 \
    NLTK_DATA=/usr/local/share/nltk_data \
    PYTHONPATH=/app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Run application with proper reload disabled in production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
