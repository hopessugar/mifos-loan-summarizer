# 🐳 Docker Setup Guide

Complete guide to build and run the Mifos Loan Summarizer using Docker.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Building Images](#building-images)
- [Running the Application](#running-the-application)
- [Accessing Services](#accessing-services)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)
- [Development Mode](#development-mode)

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10 or higher)
  - [Install Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
  - [Install Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
  - [Install Docker Engine for Linux](https://docs.docker.com/engine/install/)

- **Docker Compose** (version 2.0 or higher)
  - Usually included with Docker Desktop
  - Verify: `docker-compose --version`

---

## Quick Start

Get up and running in 3 steps:

### 1. Clone and Navigate

```bash
git clone https://github.com/hopessugar/mifos-loan-summarizer.git
cd mifos-loan-summarizer
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
# Required: At least one LLM provider API key (GROQ_API_KEY, GEMINI_API_KEY, etc.)
```

**Minimum configuration in `.env`:**

```env
# Choose your primary LLM provider
LLM_PRIMARY=gemini
LLM_MODEL=gemini-1.5-flash

# Add your API key(s)
GEMINI_API_KEY=your_actual_api_key_here
API_KEY=your-secure-api-key-min-32-chars

# Fineract (optional - uses demo by default)
FINERACT_URL=https://demo.mifos.io/fineract-provider
FINERACT_USER=mifos
FINERACT_PASSWORD=password
```

### 3. Start Services

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

That's it! The application is now running.

---

## Configuration

### Environment Variables

The application reads configuration from the `.env` file in the root directory.

#### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_PRIMARY` | Primary LLM provider | `gemini`, `groq`, `cerebras`, `ollama` |
| `LLM_MODEL` | Model name | `gemini-1.5-flash`, `llama-3.1-8b-instant` |
| `API_KEY` | API authentication key | `your-secure-key-here` |

#### LLM Provider API Keys (at least one required)

| Variable | Provider | Get Key |
|----------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `GROQ_API_KEY` | Groq | [Groq Console](https://console.groq.com/keys) |
| `CEREBRAS_API_KEY` | Cerebras | [Cerebras Cloud](https://cloud.cerebras.ai/) |
| `HF_TOKEN` | HuggingFace | [HF Settings](https://huggingface.co/settings/tokens) |
| `OLLAMA_BASE_URL` | Ollama (local) | `http://host.docker.internal:11434` |

#### Fineract Integration (optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `FINERACT_URL` | Fineract API endpoint | `https://demo.mifos.io/fineract-provider` |
| `FINERACT_USER` | Username | `mifos` |
| `FINERACT_PASSWORD` | Password | `password` |
| `FINERACT_TENANT` | Tenant ID | `default` |

#### Pipeline Configuration (optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `LEVENSHTEIN_THRESHOLD` | Text similarity threshold | `0.80` |
| `COSINE_THRESHOLD` | Semantic similarity threshold | `0.80` |
| `CONFIDENCE_THRESHOLD` | Minimum confidence score | `0.50` |
| `MAX_INPUT_CHARS` | Max contract length | `2500` |
| `EXTRACTION_TEMPERATURE` | LLM temperature | `0.1` |

---

## Building Images

### Build All Services

```bash
# Build both frontend and backend
docker-compose build

# Build with no cache (fresh build)
docker-compose build --no-cache
```

### Build Individual Services

```bash
# Build only backend
docker-compose build backend

# Build only frontend
docker-compose build frontend
```

### View Built Images

```bash
docker images | grep mifos
```

Expected output:
```
mifos-loan-summarizer-backend    latest    abc123def456    2 minutes ago    450MB
mifos-loan-summarizer-frontend   latest    def456abc123    1 minute ago     45MB
```

---

## Running the Application

### Start Services

```bash
# Start in detached mode (background)
docker-compose up -d

# Start with logs visible
docker-compose up

# Start specific service
docker-compose up -d backend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop but keep containers
docker-compose stop
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### View Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Check Service Status

```bash
# View running containers
docker-compose ps

# View detailed stats
docker stats
```

Expected output:
```
NAME              STATUS                    PORTS
mifos-backend     Up 2 minutes (healthy)    0.0.0.0:8000->8000/tcp
mifos-frontend    Up 2 minutes (healthy)    0.0.0.0:80->8080/tcp
```

---

## Accessing Services

Once the services are running, access them at:

### Frontend (Web UI)
- **URL**: http://localhost
- **Port**: 80 (default HTTP port)

### Backend API
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Testing the API

```bash
# Health check
curl http://localhost:8000/health

# List available providers
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/providers

# Analyze a loan contract (example)
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "contract_text": "Loan Amount: Rs. 100,000\nInterest Rate: 18% per annum\nTenure: 24 months",
    "provider": "gemini"
  }'
```

---

## Troubleshooting

### Common Issues

#### 1. Container fails to start

**Check logs:**
```bash
docker-compose logs backend
```

**Common causes:**
- Missing or invalid API keys in `.env`
- Port 8000 or 80 already in use
- Insufficient memory allocated to Docker

**Solution:**
```bash
# Stop conflicting services
docker-compose down

# Check if ports are in use
netstat -ano | findstr :8000
netstat -ano | findstr :80

# Restart with fresh build
docker-compose up -d --build
```

#### 2. Health check failing

**Symptoms:**
```
mifos-backend    Up 2 minutes (unhealthy)
```

**Check:**
```bash
# View health check logs
docker inspect mifos-backend --format='{{json .State.Health}}'

# Check backend logs
docker-compose logs backend | tail -50
```

**Common causes:**
- Application crashed during startup
- NLTK data download failed
- Database/API connection issues

#### 3. Frontend can't connect to backend

**Check:**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check frontend logs
docker-compose logs frontend

# Verify network connectivity
docker network inspect mifos-network
```

**Solution:**
- Ensure `VITE_API_URL` in `.env` is set correctly
- Rebuild frontend: `docker-compose build --no-cache frontend`

#### 4. NLTK data download issues

**Symptoms:**
```
nltk.downloader: Error downloading 'punkt'
```

**Solution:**
```bash
# Rebuild backend with no cache
docker-compose build --no-cache backend
docker-compose up -d backend
```

#### 5. Permission denied errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution (Linux/Mac):**
```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Or run with sudo (not recommended)
sudo docker-compose up -d
```

#### 6. Out of disk space

**Check disk usage:**
```bash
docker system df
```

**Clean up:**
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Full cleanup (WARNING: removes everything not in use)
docker system prune -a --volumes
```

### Debugging Tips

#### Enter a running container

```bash
# Backend
docker exec -it mifos-backend /bin/bash

# Frontend (if running)
docker exec -it mifos-frontend /bin/sh
```

#### Test Python dependencies

```bash
docker exec -it mifos-backend python -c "import fastapi; import langchain; print('OK')"
```

#### Check environment variables

```bash
docker exec -it mifos-backend env | grep LLM
```

#### Verify NLTK data

```bash
docker exec -it mifos-backend python -c "import nltk; print(nltk.data.path)"
```

---

## Production Deployment

### Security Checklist

Before deploying to production:

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Generate a strong `API_KEY` (min 32 characters)
- [ ] Use `FINERACT_SSL_VERIFY=true`
- [ ] Never commit `.env` to version control
- [ ] Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
- [ ] Enable HTTPS with reverse proxy (nginx, Caddy, Traefik)
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Regular security updates

### Production docker-compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: mifos-backend-prod
    restart: always
    env_file:
      - .env.production
    environment:
      - ENVIRONMENT=production
    networks:
      - mifos-network
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - VITE_API_URL=https://api.yourdomain.com
    container_name: mifos-frontend-prod
    restart: always
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - mifos-network

  # Reverse proxy (optional but recommended)
  nginx:
    image: nginx:alpine
    container_name: mifos-nginx
    restart: always
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    networks:
      - mifos-network

networks:
  mifos-network:
    driver: bridge
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Development Mode

For active development with hot-reload:

### Backend Development

```bash
# Run backend locally (not in Docker)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend Development

```bash
# Run frontend locally with hot-reload
cd frontend
npm install
npm run dev
# Access at http://localhost:5173
```

### Using Docker for Backend + Local Frontend

```bash
# Start only backend in Docker
docker-compose up -d backend

# Run frontend locally
cd frontend
npm run dev
```

Update `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

---

## Additional Commands

### View Container Resource Usage

```bash
docker stats mifos-backend mifos-frontend
```

### Export Logs

```bash
# Export all logs to file
docker-compose logs > logs.txt

# Export with timestamp
docker-compose logs -t > logs-$(date +%Y%m%d-%H%M%S).txt
```

### Update Images

```bash
# Pull latest base images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build
```

### Backup Configuration

```bash
# Backup .env file
cp .env .env.backup-$(date +%Y%m%d)

# Create archive
tar -czf mifos-backup-$(date +%Y%m%d).tar.gz .env docker-compose.yml
```

---

## Need Help?

- **GitHub Issues**: [Report a bug](https://github.com/hopessugar/mifos-loan-summarizer/issues)
- **Documentation**: Check the main [README.md](./README.md)
- **API Docs**: Visit http://localhost:8000/docs when running

---

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details
