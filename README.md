<div align="center">
  
# Mifos X — Smart Contract & Loan Agreement Summarization with LLMs

<div align="center">

### AI-powered financial contract intelligence for Mifos X

Extract structured financial entities, detect risky clauses, validate hallucinations,
and generate borrower-friendly summaries using LLMs + Fineract APIs.

<br>

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge\&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge\&logo=fastapi)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge\&logo=react)
![LangChain](https://img.shields.io/badge/LangChain-AI%20Pipeline-black?style=for-the-badge)
![Mifos](https://img.shields.io/badge/Mifos-Fineract-orange?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge\&logo=docker)
![CI/CD](https://img.shields.io/badge/CI/CD-GitHub%20Actions-2088FF?style=for-the-badge\&logo=github-actions)

<br>

**GSoC 2026 • Mifos Initiative**
Built with ❤️ by **Silky Vyas**

</div>

---

# 🌟 Overview

This project builds an **LLM-powered contract analysis pipeline** for Mifos X loan agreements.

The system can:

* 📄 Parse loan agreements and smart contracts
* 🧠 Extract 20+ structured financial entities
* ⚠️ Detect risky or borrower-unfriendly clauses
* ✅ Validate outputs using hallucination detection
* 📊 Perform math consistency checks
* 💬 Generate simplified borrower summaries
* 🔌 Integrate directly with Mifos X via the Fineract REST API

---

# 🧩 Features

<table>
<tr>
<td width="50%">

### 🤖 AI Extraction

* Interest rate extraction
* EMI detection
* Penalty clause identification
* Loan tenure parsing
* Collateral extraction
* Grace period analysis

</td>

<td width="50%">

### 🛡️ Validation Layer

* Hallucination detection
* Numerical consistency checks
* Confidence scoring
* Output verification pipeline

</td>
</tr>

<tr>
<td width="50%">

### 📘 Borrower Summaries

* Plain-language explanations
* Risk highlights
* Simplified repayment details
* Easy-to-read outputs

</td>

<td width="50%">

### 🔗 Mifos Integration

* Live Fineract API integration
* Loan product ingestion
* Dynamic product analysis
* Provider health monitoring

</td>
</tr>
</table>

---

# 🏗️ Tech Stack

| Layer                 | Technology                     |
| --------------------- | ------------------------------ |
| **Frontend**          | React 18 + Vite + Tailwind CSS |
| **Backend**           | FastAPI + Pydantic v2          |
| **AI Pipeline**       | LangChain + Instructor         |
| **Default LLM**       | HuggingFace Inference API      |
| **Local LLM Support** | Ollama                         |
| **Evaluation**        | RAGAS                          |
| **Mifos Integration** | Apache Fineract REST API       |

---

# ⚡ Quick Setup

## 1️⃣ Clone Repository

```bash
git clone https://github.com/hopessugar/mifos-loan-summarizer.git

cd mifos-loan-summarizer
```

---

## 2️⃣ Backend Setup

```bash
cd backend

python -m venv venv
```

### Activate virtual environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment

```bash
cp config.example.yaml config.yaml
```

**IMPORTANT: Secrets Management**

⚠️ **DO NOT put real secrets in config.yaml!** Use environment variables instead.

**Option 1: Environment Variables (Recommended for Production)**
```bash
# Windows
set HF_TOKEN=your_huggingface_token
set FINERACT_PASSWORD=your_fineract_password
set API_KEY=your_api_key

# Linux / macOS
export HF_TOKEN=your_huggingface_token
export FINERACT_PASSWORD=your_fineract_password
export API_KEY=your_api_key
```

**Option 2: .env File (Recommended for Development)**
```bash
# Create .env file in backend/ directory
cd backend
cp .env.example .env

# Edit .env with your secrets
# .env is already in .gitignore and will never be committed
```

**Why Environment Variables?**
- ✅ Secrets never committed to Git
- ✅ Different secrets per environment (dev/staging/prod)
- ✅ Easy rotation without code changes
- ✅ Industry standard (12-factor app)

See [Secrets Management](#-secrets-management) section below for detailed instructions.

### Set up authentication (REQUIRED for production)

Generate a strong API key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Set via environment variable (Recommended)**
```bash
# Windows
set API_KEY=your-generated-api-key-here

# Linux / macOS
export API_KEY=your-generated-api-key-here
```

**Note**: In production environments (`ENVIRONMENT=production`), the API key is required. The application will refuse to start without it.

---

## 3️⃣ Run Backend

```bash
cd ..

uvicorn backend.main:app --reload --port 8000
```

### Backend URLs

| Service      | URL                           |
| ------------ | ----------------------------- |
| API          | `http://localhost:8000`       |
| Swagger Docs | `http://localhost:8000/docs`  |
| ReDoc        | `http://localhost:8000/redoc` |

---

## 4️⃣ Frontend Setup

```bash
cd frontend

npm install
```

### Configure frontend API key

Edit `frontend/.env`:
```bash
VITE_API_URL="http://localhost:8000"
VITE_API_KEY="your-api-key-here"  # Same key as backend
```

### Run frontend

```bash
npm run dev
```

---

# 📂 Project Structure

```bash
mifos-loan-summarizer/
│
├── README.md
├── DECISIONS.md
├── config.example.yaml
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   │
│   ├── routers/
│   │   ├── analysis.py
│   │   ├── loanproducts.py
│   │   ├── health.py
│   │   └── providers.py
│   │
│   ├── services/
│   ├── pipeline/
│   ├── providers/
│   ├── schemas/
│   └── tests/
│
├── frontend/
│
└── evaluation/
```

---

# 🔌 API Endpoints

## Authentication

All API endpoints (except `/health` and `/`) require authentication via API key.

**Include the API key in request headers:**
```bash
X-API-Key: your-api-key-here
```

**Example with curl:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your contract text here..."}'
```

## Endpoints

| Method | Endpoint             | Auth Required | Description                      |
| ------ | -------------------- | ------------- | -------------------------------- |
| `POST` | `/analyze`           | ✅ Yes         | Full AI pipeline analysis        |
| `GET`  | `/loanproducts`      | ✅ Yes         | Fetch all Fineract loan products |
| `GET`  | `/loanproducts/{id}` | ✅ Yes         | Fetch single loan product        |
| `GET`  | `/providers`         | ✅ Yes         | List configured LLM providers    |
| `GET`  | `/health`            | ❌ No          | Provider + API health status     |
| `GET`  | `/`                  | ❌ No          | API information                  |

---

# 🧠 Multi-Provider LLM Architecture

Switch providers instantly from `config.yaml`.

```yaml
llm:
  primary: hf_inference
```

### Supported Providers

* HuggingFace Inference API
* Ollama
* Groq
* Cerebras

No backend refactoring required.

---

# 🔒 Privacy & Security

* 🔐 **API Key Authentication** - All endpoints protected with API key authentication
* 🔐 **Fineract credentials** remain server-side only
* 🚫 **No data storage** - Contract data never stored in databases
* 🧠 **Open-source models** supported by default
* 💻 **Ollama local inference** supported for offline deployments
* 🛡️ **Frontend security** - API secrets never exposed to frontend
* ✅ **SSL/TLS enforcement** - Certificate verification enforced for all Fineract connections
* 🚨 **Production safety** - Security checks prevent misconfiguration in production
* 🔑 **Secrets management** - Environment variables for all sensitive data

---

# 🔑 Secrets Management

## Overview

This application follows security best practices for managing sensitive credentials:

- ✅ **Environment variables** for all secrets (recommended)
- ✅ **`.env` files** for local development (gitignored)
- ❌ **Never commit secrets** to version control
- ⚠️ **Runtime warnings** if secrets detected in config files

## Quick Start

### 🐳 Docker (Recommended)

The fastest way to get started:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/mifos-loan-summarizer.git
cd mifos-loan-summarizer

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Start with Docker Compose
docker-compose up --build

# 4. Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

That's it! The application is now running in containers. 🎉

### 📦 Manual Installation

If you prefer to run without Docker:

### 1. Generate Secrets

```bash
# Generate strong API key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Set Environment Variables

**Production (Linux/macOS)**:
```bash
export HF_TOKEN=your_huggingface_token_here
export FINERACT_PASSWORD=your_secure_password
export API_KEY=your_generated_api_key
export GROQ_API_KEY=your_groq_key  # Optional
export CEREBRAS_API_KEY=your_cerebras_key  # Optional
```

**Production (Windows)**:
```cmd
set HF_TOKEN=your_huggingface_token_here
set FINERACT_PASSWORD=your_secure_password
set API_KEY=your_generated_api_key
```

**Development (.env file)**:
```bash
# backend/.env
HF_TOKEN=your_huggingface_token_here
FINERACT_URL=http://localhost:8443/fineract-provider
FINERACT_USER=mifos
FINERACT_PASSWORD=your_secure_password
FINERACT_TENANT=default
API_KEY=dev-key-for-testing
GROQ_API_KEY=your_groq_key
CEREBRAS_API_KEY=your_cerebras_key
```

### 3. Verify Setup

Start the application and check for warnings:

```bash
uvicorn backend.main:app --reload
```

✅ **Good**: No security warnings  
⚠️ **Warning**: "SECURITY WARNING: Secrets detected in config.yaml!"

If you see warnings, move secrets from `config.yaml` to environment variables.

## Configuration Priority

The application loads secrets in this order (highest priority first):

1. **Environment Variables** (highest priority)
2. **`.env` file** (development only)
3. **`config.yaml`** (discouraged for secrets)

Example:
```bash
# If both are set, environment variable wins:
export API_KEY=env-key-123
# config.yaml: api_key: yaml-key-456
# Result: Uses "env-key-123"
```

## Security Best Practices

### ✅ DO

- ✅ Use environment variables for all secrets
- ✅ Use `.env` file for local development
- ✅ Add `config.yaml` to `.gitignore` (already done)
- ✅ Rotate secrets regularly
- ✅ Use strong, randomly generated keys
- ✅ Different secrets per environment (dev/staging/prod)
- ✅ Review `.gitignore` before committing

### ❌ DON'T

- ❌ Put secrets in `config.yaml`
- ❌ Commit `.env` files to Git
- ❌ Share secrets via email or chat
- ❌ Use weak passwords like "password" or "123456"
- ❌ Reuse secrets across environments
- ❌ Commit `config.yaml` with real secrets

## Required Secrets

| Secret | Required | Purpose | How to Get |
|--------|----------|---------|------------|
| `API_KEY` | ✅ Production | API authentication | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `HF_TOKEN` | ⚠️ If using HF | HuggingFace API access | Get from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| `FINERACT_PASSWORD` | ⚠️ If using Fineract | Fineract database access | Your Fineract admin password |
| `GROQ_API_KEY` | ❌ Optional | Groq LLM provider | Get from [console.groq.com](https://console.groq.com) |
| `CEREBRAS_API_KEY` | ❌ Optional | Cerebras LLM provider | Get from Cerebras |

## Troubleshooting

### "SECURITY WARNING: Secrets detected in config.yaml!"

**Problem**: You have real secrets in `config.yaml`

**Solution**:
1. Copy secrets to environment variables or `.env` file
2. Remove secrets from `config.yaml` (replace with empty strings)
3. Restart application

### "CRITICAL SECURITY ERROR: API_KEY must be set in production"

**Problem**: Running in production without API key

**Solution**:
```bash
export ENVIRONMENT=production
export API_KEY=your-strong-api-key-here
```

### Secrets not loading

**Check priority order**:
1. Verify environment variable is set: `echo $API_KEY` (Linux/macOS) or `echo %API_KEY%` (Windows)
2. Check `.env` file exists and has correct format
3. Check `config.yaml` (last resort, not recommended)

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
env:
  API_KEY: ${{ secrets.API_KEY }}
  HF_TOKEN: ${{ secrets.HF_TOKEN }}
  FINERACT_PASSWORD: ${{ secrets.FINERACT_PASSWORD }}
```

### Docker

```dockerfile
# Pass secrets as environment variables
docker run -e API_KEY=$API_KEY -e HF_TOKEN=$HF_TOKEN myapp
```

### Kubernetes

```yaml
# Use Kubernetes secrets
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  api-key: <base64-encoded-key>
  hf-token: <base64-encoded-token>
```

---
* 🛡️ **Frontend security** - API secrets never exposed to frontend
* ✅ **SSL/TLS enforcement** - Certificate verification enforced for all Fineract connections
* 🚨 **Production safety** - Security checks prevent misconfiguration in production

## API Authentication

The API uses API key authentication to protect all sensitive endpoints.

### Setup

1. **Generate a strong API key:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Configure backend** (choose one method):
   
   **Environment variable (Recommended):**
   ```bash
   export API_KEY=your-generated-key
   ```
   
   **Configuration file:**
   ```yaml
   # config.yaml
   api_key: your-generated-key
   ```

3. **Configure frontend:**
   ```bash
   # frontend/.env
   VITE_API_KEY=your-generated-key
   ```

### Usage

Include the API key in all requests to protected endpoints:

```bash
# Example: Analyze contract
curl -X POST http://localhost:8000/analyze \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"text": "Contract text..."}'
```

### Production Requirements

- ✅ API key is **REQUIRED** in production (`ENVIRONMENT=production`)
- ✅ Application refuses to start without API key in production
- ✅ Use strong, randomly generated keys (minimum 32 characters)
- ✅ Rotate keys regularly
- ✅ Never commit API keys to version control

## Fineract SSL Configuration

By default, all connections to Fineract use SSL/TLS certificate verification for security.

### Production (Recommended)
```yaml
# config.yaml
fineract_ssl_verify: true  # Default - always verify certificates
```

### Development with Self-Signed Certificates
If your development Fineract instance uses self-signed certificates:

```yaml
# config.yaml
fineract_ssl_verify: true
fineract_ca_bundle: /path/to/your/ca-certificate.pem
```

**Note**: SSL verification cannot be disabled in production environments. The application will refuse to start if `ENVIRONMENT=production` and `fineract_ssl_verify: false`.

---

# 📈 Development Progress

| Status | Milestone                       |
| ------ | ------------------------------- |
| ✅      | LMS-1: Repository scaffold      |
| ✅      | LMS-2: FastAPI backend skeleton |
| 🚧     | LMS-3: React frontend skeleton  |
| ⏳      | LMS-4: Clause segmenter         |
| ⏳      | LMS-5: LLM provider registry    |
| ⏳      | LMS-6: Extraction chain         |
| ⏳      | LMS-7: Validation chain         |
| ⏳      | LMS-8: Summary chain            |
| ⏳      | LMS-9: React results UI         |
| ⏳      | LMS-10: Testing & deployment    |

---

# 🎯 Vision

The goal of this project is to make financial contracts:

* More transparent
* Easier to understand
* Safer for borrowers
* Faster for financial institutions to analyze

By combining **LLMs + validation pipelines + Mifos infrastructure**, this system aims to bring practical AI assistance into microfinance and fintech workflows.

---

# 🤝 Contributing

Before contributing, please read:

```bash
DECISIONS.md
```

This document explains:

* architectural choices
* provider abstractions
* validation strategy
* pipeline design rationale

---

# 🐳 Docker Deployment

## Quick Start with Docker

The easiest way to run the application:

```bash
# 1. Clone and navigate
git clone https://github.com/yourusername/mifos-loan-summarizer.git
cd mifos-loan-summarizer

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys and configuration

# 3. Start services
docker-compose up --build

# 4. Access application
# Frontend: http://localhost
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Docker Architecture

The application uses multi-stage Docker builds for optimal image sizes:

- **Backend**: Python 3.11-slim → ~200MB
- **Frontend**: Node 20 (build) + Nginx Alpine (serve) → ~25MB

### Services

| Service | Port | Description |
|---------|------|-------------|
| Backend | 8000 | FastAPI application |
| Frontend | 80 | React app served by Nginx |

### Features

✅ Multi-stage builds for smaller images  
✅ Non-root users for security  
✅ Health checks for reliability  
✅ Automatic restarts  
✅ Network isolation  
✅ Volume mounts for development  

## Docker Commands

```bash
# Start services (detached)
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

# Production mode
ENVIRONMENT=production docker-compose up -d
```

## Environment Configuration

All configuration is done via environment variables in `.env`:

```bash
# Application
ENVIRONMENT=development
API_KEY=your-api-key

# LLM Providers
GROQ_API_KEY=your-groq-key
HF_API_KEY=your-hf-key
OLLAMA_BASE_URL=http://host.docker.internal:11434

# Fineract
FINERACT_URL=https://your-fineract.com
FINERACT_USER=mifos
FINERACT_PASSWORD=your-password
FINERACT_SSL_VERIFY=true
```

---

# 🔄 CI/CD Pipeline

## GitHub Actions Workflows

The project includes comprehensive CI/CD automation:

### 1. Continuous Integration (`ci.yml`)

**Triggers:** Push to main/develop, Pull Requests

**Jobs:**
- ✅ Backend tests with coverage (95 tests)
- ✅ Integration tests
- ✅ Frontend linting and build
- ✅ Docker image build verification
- ✅ Security scanning

**Status:** ![CI](https://github.com/yourusername/mifos-loan-summarizer/workflows/CI%20Pipeline/badge.svg)

### 2. Continuous Deployment (`cd.yml`)

**Triggers:** Manual workflow dispatch

**Features:**
- 🐳 Build and push Docker images
- 🏷️ Version tagging
- 🌍 Environment selection (staging/production)
- ✅ Health checks
- 🔄 Rollback capability

### 3. Security Scanning (`security.yml`)

**Triggers:** Weekly schedule, Manual, Dependency changes

**Scans:**
- 🔒 Python dependency vulnerabilities (safety)
- 🔒 Code security issues (Bandit)
- 🔒 Node.js vulnerabilities (npm audit)
- 🔒 Docker image CVEs (Trivy)

## Running CI Locally

```bash
# Run tests like CI does
cd backend
pytest tests/ -v --cov=. --cov-report=html

# Run linting
ruff check .

# Build Docker images
docker-compose build
```

## Required GitHub Secrets

To enable full CI/CD functionality:

```
DOCKER_USERNAME       - Docker Hub username
DOCKER_PASSWORD       - Docker Hub token
CODECOV_TOKEN        - Codecov API token (optional)
```

---

# 📜 License

MIT License

---

<div align="center">

### ⭐ If you like this project, consider starring the repository!

Built during **Google Summer of Code 2026** with the ❤️ of open source.

</div>
