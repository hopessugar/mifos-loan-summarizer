# 🐳 Docker Setup Guide

Complete guide for deploying the Mifos Loan Summarizer using Docker and Docker Compose.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Build & Deploy](#build--deploy)
- [Verification](#verification)
- [Using Ollama (Local LLM)](#using-ollama-local-llm)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)
- [Maintenance](#maintenance)

---

## Prerequisites

### Required Software

1. **Docker Desktop** (or Docker Engine + Docker Compose)
   - **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - **Linux**: [Docker Engine](https://docs.docker.com/engine/install/) + [Docker Compose](https://docs.docker.com/compose/install/)
   
   Verify installation:
   ```bash
   docker --version
   docker compose version
   ```

2. **Minimum System Requirements**
   - **RAM**: 4GB minimum, 8GB recommended
   - **Disk Space**: 10GB free space
   - **CPU**: 2 cores minimum, 4 cores recommended

3. **API Keys** (at least one required)
   - **Google Gemini API Key** (recommended): Get from [Google AI Studio](https://aistudio.google.com/apikey)
   - **Groq API Key**: Get from [Groq Console](https://console.groq.com/)
   - **Ollama** (local, no key needed): See [Using Ollama](#using-ollama-local-llm)

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/mifos-loan-summarizer.git
cd mifos-loan-summarizer
```

### 2. Configure Environment

Copy the example environment file:

```bash
# Windows (Command Prompt)
copy .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required: At least one LLM provider
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Primary LLM Provider (choose one)
LLM_PRIMARY=gemini           # or: ollama, groq
LLM_MODEL=gemini-3.5-flash   # or: llama3.2:latest, llama-3.1-8b-instant

# Optional: Fallback provider (for timeout/failures)
LLM_FALLBACK=gemini          # Leave empty to disable fallback
LLM_FALLBACK_MODEL=gemini-3.5-flash

# API Security (generate a random string)
API_KEY=your_secure_api_key_here
```

### 3. Build and Start

```bash
docker compose up -d --build
```

This will:
- Build the backend (FastAPI) image
- Build the frontend (React + Nginx) image
- Start both containers in detached mode

### 4. Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Configuration

### Core Environment Variables

#### LLM Provider Settings

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `LLM_PRIMARY` | Primary AI provider | `gemini` | `gemini`, `ollama`, `groq`, `cerebras`, `huggingface` |
| `LLM_MODEL` | Model name for primary provider | `gemini-3.5-flash` | Provider-specific |
| `LLM_FALLBACK` | Fallback provider (optional) | - | Same as `LLM_PRIMARY` |
| `LLM_FALLBACK_MODEL` | Fallback model name | - | Provider-specific |
| `PRIMARY_PROVIDER_TIMEOUT` | Timeout before fallback (seconds) | `120` | Any positive integer |
| `FALLBACK_ON_TIMEOUT` | Enable timeout-based fallback | `true` | `true`, `false` |

#### Provider-Specific Configuration

```env
# Google Gemini
GEMINI_API_KEY=your_key_here

# Ollama (local)
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2:latest

# Groq
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-8b-instant

# Cerebras
CEREBRAS_API_KEY=your_key_here

# Hugging Face
HF_API_KEY=your_key_here
HF_TOKEN=your_key_here
```

#### Fineract Integration

```env
FINERACT_URL=https://demo.mifos.community/fineract-provider
FINERACT_USER=mifos
FINERACT_PASSWORD=password
FINERACT_TENANT=default
FINERACT_SSL_VERIFY=true
```

#### Pipeline Tuning

```env
# Input limits
MAX_INPUT_CHARS=50000
EXTRACTION_MAX_TOKENS=16384
SUMMARY_MAX_TOKENS=2048

# Semantic chunking
USE_SEMANTIC_CHUNKING=false
MAX_SEGMENT_TOKENS=200

# Validation thresholds
LEVENSHTEIN_THRESHOLD=0.80
COSINE_THRESHOLD=0.80
CONFIDENCE_THRESHOLD=0.50
MATH_TOLERANCE=0.10

# LLM temperature
EXTRACTION_TEMPERATURE=0
```

---

## Build & Deploy

### Standard Deployment

```bash
# Build and start all services
docker compose up -d --build

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f backend
docker compose logs -f frontend
```

### Rebuild from Scratch

```bash
# Stop and remove containers
docker compose down

# Remove all images
docker rmi mifos-loan-summarizer-backend mifos-loan-summarizer-frontend

# Rebuild without cache
docker compose build --no-cache

# Start services
docker compose up -d
```

### Selective Rebuild

```bash
# Rebuild only backend
docker compose up -d --build backend

# Rebuild only frontend
docker compose up -d --build frontend
```

---

## Verification

### 1. Check Container Status

```bash
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE                            STATUS                   PORTS
a7db0b2c4770   mifos-loan-summarizer-frontend   Up 2 minutes (healthy)   0.0.0.0:80->8080/tcp
c0a71851ac1c   mifos-loan-summarizer-backend    Up 2 minutes (healthy)   0.0.0.0:8000->8000/tcp
```

### 2. Test Backend Health

```bash
# Windows (PowerShell)
curl http://localhost:8000/health -UseBasicParsing

# Linux/Mac
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "llm_provider": "gemini",
  "llm_model": "gemini-3.5-flash",
  "provider_configured": true,
  "fineract_reachable": true,
  "fineract_url": "https://demo.mifos.community/fineract-provider"
}
```

### 3. Test Frontend

Open http://localhost in your browser. You should see the Mifos Loan Summarizer interface.

### 4. Test API with Sample Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "contract_text": "Loan amount: $10,000. Interest rate: 5% per annum. Repayment term: 12 months."
  }'
```

---

## Using Ollama (Local LLM)

Ollama allows you to run LLMs locally without API keys or internet dependency.

### Option 1: Ollama on Host Machine (Recommended)

This is the default configuration when using Docker Compose.

#### Step 1: Install Ollama on Your Host

**Windows/Mac**:
- Download from [ollama.com](https://ollama.com/download)
- Run the installer

**Linux**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Step 2: Pull a Model

```bash
# Pull Llama 3.2 (recommended, ~2GB)
ollama pull llama3.2:latest

# Or other models
ollama pull mistral:latest
ollama pull phi3:latest
```

#### Step 3: Configure Environment

Update `.env`:
```env
LLM_PRIMARY=ollama
OLLAMA_MODEL=llama3.2:latest
OLLAMA_BASE_URL=http://host.docker.internal:11434

# Optional: Set Gemini as fallback
LLM_FALLBACK=gemini
LLM_FALLBACK_MODEL=gemini-3.5-flash
GEMINI_API_KEY=your_key_here
```

#### Step 4: Start Docker Services

```bash
docker compose up -d
```

The backend container will connect to Ollama running on your host machine via `host.docker.internal:11434`.

---

### Option 2: Ollama in Docker Container

Run Ollama as a Docker service alongside your application.

#### Step 1: Enable Ollama Service

Edit `docker-compose.yml` and uncomment the Ollama service section:

```yaml
ollama:
  image: ollama/ollama:latest
  container_name: mifos-ollama
  ports:
    - "11434:11434"
  volumes:
    - ollama-data:/root/.ollama
  environment:
    - OLLAMA_HOST=0.0.0.0
  networks:
    - mifos-network
  restart: unless-stopped
  # For NVIDIA GPU support:
  # deploy:
  #   resources:
  #     reservations:
  #       devices:
  #         - driver: nvidia
  #           count: all
  #           capabilities: [gpu]
```

Also uncomment the volumes section:
```yaml
volumes:
  ollama-data:
```

#### Step 2: Update Environment

Update `.env`:
```env
LLM_PRIMARY=ollama
OLLAMA_MODEL=llama3.2:latest
OLLAMA_BASE_URL=http://ollama:11434
```

#### Step 3: Start All Services

```bash
docker compose up -d
```

#### Step 4: Pull Model Inside Container

```bash
# Access Ollama container
docker exec -it mifos-ollama bash

# Pull model
ollama pull llama3.2:latest

# Exit container
exit
```

#### GPU Support

**NVIDIA GPU**:
1. Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
2. Uncomment the `deploy` section in docker-compose.yml

**AMD GPU**:
Replace `nvidia` with `amd` in the deploy section

**CPU Only**:
Remove the `deploy` section (slower but works)

---

## Troubleshooting

### Container Fails to Start

**Check logs**:
```bash
docker compose logs backend
docker compose logs frontend
```

**Common issues**:
- Missing API keys: Verify `.env` file
- Port conflicts: Change ports in `docker-compose.yml`
- Insufficient memory: Increase Docker memory limit

### Backend Health Check Fails

```bash
# Check if backend is responding
docker exec mifos-backend curl http://localhost:8000/health

# Check Python errors
docker compose logs backend | grep ERROR
```

### Cannot Connect to Ollama

**If using host Ollama**:
```bash
# Verify Ollama is running on host
ollama list

# Test connection from backend container
docker exec mifos-backend curl http://host.docker.internal:11434/api/tags
```

**If using Docker Ollama**:
```bash
# Check Ollama container status
docker ps | grep ollama

# Test from backend container
docker exec mifos-backend curl http://ollama:11434/api/tags
```

### Frontend Shows API Error

**Check backend URL**:
- Frontend expects backend at `http://localhost:8000`
- Verify in browser console (F12 → Network tab)

**Rebuild frontend with correct API URL**:
```bash
# Update .env
VITE_API_URL=http://localhost:8000

# Rebuild frontend
docker compose up -d --build frontend
```

### Permission Denied Errors

**Linux/Mac**:
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Or run with sudo
sudo docker compose up -d
```

### Out of Disk Space

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove all unused objects
docker system prune -a --volumes
```

---

## Advanced Configuration

### Custom Network Configuration

```yaml
networks:
  mifos-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Using External Databases

Add a PostgreSQL service for persistence:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    container_name: mifos-postgres
    environment:
      POSTGRES_DB: mifos
      POSTGRES_USER: mifos
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - mifos-network

volumes:
  postgres-data:
```

### SSL/TLS with Nginx Reverse Proxy

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    networks:
      - mifos-network
```

### Resource Limits

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

---

## Maintenance

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100 backend

# Save logs to file
docker compose logs backend > backend-logs.txt
```

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose down
docker compose up -d --build
```

### Backup Configuration

```bash
# Backup environment file
cp .env .env.backup

# Backup Docker volumes (if using Ollama in Docker)
docker run --rm -v ollama-data:/data -v $(pwd):/backup alpine tar czf /backup/ollama-backup.tar.gz /data
```

### Monitor Resource Usage

```bash
# Real-time stats
docker stats

# Container disk usage
docker system df
```

### Restart Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend
docker compose restart frontend
```

### Stop Services

```bash
# Stop all services (preserves containers)
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove containers + volumes
docker compose down -v

# Stop and remove everything including images
docker compose down --rmi all -v
```

---

## Production Deployment Checklist

- [ ] Use strong `API_KEY` value
- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Configure SSL/TLS certificates
- [ ] Set up log aggregation (e.g., ELK stack)
- [ ] Enable container restart policies
- [ ] Configure resource limits
- [ ] Set up monitoring (e.g., Prometheus + Grafana)
- [ ] Implement backup strategy
- [ ] Use Docker secrets for sensitive data
- [ ] Configure firewall rules
- [ ] Set up reverse proxy (Nginx/Traefik)
- [ ] Enable health checks
- [ ] Document disaster recovery procedures

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Ollama Documentation](https://ollama.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Project README](./README.md)
- [Contributing Guidelines](./CONTRIBUTING.md)

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review container logs: `docker compose logs`
3. Search existing [GitHub Issues](https://github.com/your-username/mifos-loan-summarizer/issues)
4. Create a new issue with:
   - Docker version: `docker --version`
   - OS and version
   - Error logs
   - Steps to reproduce

---

**Last Updated**: August 2026  
**Docker Compose Version**: 2.x  
**Tested On**: Windows 11, macOS 14, Ubuntu 22.04
