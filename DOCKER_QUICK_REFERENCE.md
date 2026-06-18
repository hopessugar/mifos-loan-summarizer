# 🐳 Docker Quick Reference

Quick command reference for Mifos Loan Summarizer Docker operations.

---

## 🚀 Quick Start

```bash
# 1. Start Docker
# 2. Copy .env.example to .env and add API keys
# 3. Run:

docker compose up -d
```

---

## 📦 Building

```bash
# Build all services
docker compose build

# Build specific service
docker compose build backend
docker compose build frontend

# Rebuild without cache
docker compose build --no-cache

# Using helper scripts
./build.sh          # Linux/Mac
.\build.bat         # Windows
```

---

## ▶️ Starting

```bash
# Start all services (detached)
docker compose up -d

# Start with logs visible
docker compose up

# Start specific service
docker compose up -d backend

# Using helper scripts
./start.sh          # Linux/Mac
.\start.bat         # Windows
```

---

## ⏸️ Stopping

```bash
# Stop all services
docker compose down

# Stop but keep containers
docker compose stop

# Stop and remove volumes
docker compose down -v

# Using helper scripts
./stop.sh           # Linux/Mac
.\stop.bat          # Windows
```

---

## 🔄 Restarting

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend

# Rebuild and restart
docker compose up -d --build
```

---

## 📊 Monitoring

```bash
# View running containers
docker compose ps

# View logs (all services)
docker compose logs

# Follow logs in real-time
docker compose logs -f

# Logs for specific service
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100 backend

# Resource usage
docker stats
```

---

## 🔍 Health Checks

```bash
# Check service status
docker compose ps

# Test backend health
curl http://localhost:8000/health

# Test frontend health
curl http://localhost/health

# View health status
docker inspect mifos-backend --format='{{json .State.Health}}'
```

---

## 🐛 Debugging

```bash
# Enter backend container
docker exec -it mifos-backend /bin/bash

# Enter frontend container
docker exec -it mifos-frontend /bin/sh

# Check environment variables
docker exec -it mifos-backend env | grep LLM

# Test Python imports
docker exec -it mifos-backend python -c "import fastapi; print('OK')"

# View container details
docker inspect mifos-backend
```

---

## 🔧 Maintenance

```bash
# View disk usage
docker system df

# Clean unused images
docker image prune

# Clean unused volumes
docker volume prune

# Full cleanup (WARNING: removes everything)
docker system prune -a --volumes

# Update base images
docker compose pull
```

---

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost | Web UI |
| Backend | http://localhost:8000 | API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health | http://localhost:8000/health | Health check |

---

## 📝 Configuration

```bash
# View current .env
cat .env

# Edit .env
nano .env          # Linux/Mac
notepad .env       # Windows

# Validate configuration
docker compose config

# Apply .env changes (restart required)
docker compose down
docker compose up -d
```

---

## 🔐 Security

```bash
# View exposed ports
docker compose ps

# Check for vulnerabilities (if Docker Scout enabled)
docker scout cves mifos-backend

# View container users
docker exec -it mifos-backend whoami

# Verify non-root
docker exec -it mifos-backend id
```

---

## 📊 Performance

```bash
# View resource usage
docker stats

# Limit resources (add to docker-compose.yml)
# deploy:
#   resources:
#     limits:
#       cpus: '1.0'
#       memory: 1G

# View network
docker network inspect mifos-network
```

---

## 🧪 Testing

```bash
# Run backend tests in container
docker exec -it mifos-backend pytest tests/ -v

# Test API endpoint
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"contract_text": "Test loan", "provider": "gemini"}'

# Check provider availability
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/providers
```

---

## 📦 Backup & Restore

```bash
# Save images
docker save mifos-loan-summarizer-backend:latest | gzip > backend.tar.gz
docker save mifos-loan-summarizer-frontend:latest | gzip > frontend.tar.gz

# Load images
docker load < backend.tar.gz
docker load < frontend.tar.gz

# Backup configuration
tar -czf backup-$(date +%Y%m%d).tar.gz .env docker-compose.yml

# Export logs
docker compose logs > logs-$(date +%Y%m%d-%H%M%S).txt
```

---

## 🚨 Emergency

```bash
# Force remove container
docker rm -f mifos-backend

# Force rebuild everything
docker compose down -v
docker compose build --no-cache
docker compose up -d

# View all containers (including stopped)
docker ps -a

# Start stopped container
docker start mifos-backend

# Check Docker daemon
docker info
```

---

## 💡 Tips

- Use `docker compose` (v2) not `docker-compose` (v1)
- Always check logs when something fails: `docker compose logs -f`
- Rebuild after changing Dockerfile: `docker compose build`
- Restart after changing .env: `docker compose restart`
- Use `--no-cache` if dependencies changed
- Health checks take 60s to stabilize for backend

---

## 📚 More Help

- Full guide: [DOCKER_SETUP.md](DOCKER_SETUP.md)
- Troubleshooting: [DOCKER_SETUP.md#troubleshooting](DOCKER_SETUP.md#troubleshooting)
- Main README: [README.md](README.md)
- Report issues: [GitHub Issues](https://github.com/hopessugar/mifos-loan-summarizer/issues)

---

**TIP:** Bookmark this page for quick reference! 🔖
