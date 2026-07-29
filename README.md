<div align="center">

# 🏦 Mifos Loan Summarizer

### AI-Powered Loan Contract Analysis for Financial Inclusion

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg?style=for-the-badge)](LICENSE)

[![Tests](https://img.shields.io/badge/Tests-95%2B%20Passing-success?style=for-the-badge&logo=pytest)](https://github.com/hopessugar/mifos-loan-summarizer)
[![Coverage](https://img.shields.io/badge/Coverage-85%25-brightgreen?style=for-the-badge&logo=codecov)](https://github.com/hopessugar/mifos-loan-summarizer)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

<img src="https://img.shields.io/badge/GSoC-2026-orange?style=for-the-badge&logo=google&logoColor=white" alt="GSoC 2026">
<img src="https://img.shields.io/badge/Mifos-Initiative-blue?style=for-the-badge" alt="Mifos Initiative">

---

### 🌟 Transform Complex Loan Agreements into Clear, Borrower-Friendly Summaries

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing) • [Demo](#-demo)

</div>

---

## 📖 Overview

**Mifos Loan Summarizer** is an intelligent system that leverages **Large Language Models** to extract financial terms from loan contracts, validate data accuracy through multi-layer verification, and generate plain-language summaries that empower borrowers to make informed decisions.

### 🎯 The Problem We Solve

- 📄 **Complex Legal Language** confuses borrowers
- 🌍 **Language Barriers** in multilingual communities  
- ⚖️ **Hidden Fees** buried in fine print
- 💸 **Borrowers don't understand** true loan costs
- 🚫 **Financial exclusion** due to lack of transparency

### ✨ Our Solution

- 🤖 **AI-powered extraction** of 20+ financial entities with 88-100% accuracy
- ✓ **Hallucination detection** validates extracted data against source
- ⚠️ **Risk scoring** on a 0-10 scale with clear warnings
- 📝 **Plain-language summaries** in multiple languages
- 💬 **WhatsApp-ready export** for easy sharing
- 🔌 **Mifos X integration** for seamless workflow

---

## 🎨 Features

<table>
<tr>
<td width="50%">

### 🔍 Smart Extraction
- **20+ Financial Entities** (rates, fees, penalties, terms)
- **Multi-Model Support** (Gemini, Ollama, Groq, Cerebras, HF)
- **Timeout-Based Fallback** (primary → fallback in 30s)
- **JSON Mode** for reliable structured output

</td>
<td width="50%">

### ✅ Validation & Verification
- **Levenshtein Distance** matching (80% threshold)
- **TF-IDF Cosine Similarity** for semantic verification
- **Numerical Cross-Check** against source text
- **Math Validation** (EMI, total cost consistency)

</td>
</tr>
<tr>
<td width="50%">

### 📊 Risk Analysis
- **0-10 Risk Score** with explanatory factors
- **Borrower Protection Score** (BPS) calculation
- **Predatory Lending Detection** (usurious rates, unfair clauses)
- **Negotiation Tips** for borrowers

</td>
<td width="50%">

### 🌐 Multi-Channel Output
- **Plain-Language Summary** (English, Hindi)
- **WhatsApp Export** (<300 chars for easy sharing)
- **Detailed Financial Breakdown** with charts
- **Missing Terms Detection** prompts borrowers to ask questions

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| **Git** | Any | Clone repository |
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 18+ (20 recommended) | Frontend runtime |
| **Docker** *(optional)* | 4.x+ | Containerized deployment |

### ⚡ Option 1: Local Development (Recommended)

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/hopessugar/mifos-loan-summarizer.git
cd mifos-loan-summarizer
```

#### 2️⃣ Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

#### 3️⃣ Configure Environment

```bash
# From project root
cp .env.example .env
```

**Edit `.env` and add your API keys:**

```env
# Primary LLM Configuration
LLM_PRIMARY="ollama"              # or "gemini", "groq", "cerebras"
LLM_MODEL="llama3.2:latest"       # Model name
LLM_FALLBACK="gemini"             # Fallback provider
LLM_FALLBACK_MODEL="gemini-3.5-flash"

# Timeout Settings
PRIMARY_PROVIDER_TIMEOUT=120      # Timeout in seconds
FALLBACK_ON_TIMEOUT=true          # Enable automatic fallback

# API Keys (add at least one)
GEMINI_API_KEY="your-gemini-key-here"
GROQ_API_KEY="your-groq-key-here"
OLLAMA_BASE_URL="http://localhost:11434"
```

> 🔑 **Get API Keys:**
> - **Gemini**: https://aistudio.google.com/apikey (Free tier: 1,500 requests/day)
> - **Groq**: https://console.groq.com/keys (Free tier available)
> - **Ollama**: https://ollama.com/download (100% free, runs locally)

#### 4️⃣ Start Backend Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

✅ Backend running at **http://localhost:8000**  
📚 API Docs at **http://localhost:8000/docs**

#### 5️⃣ Frontend Setup (New Terminal)

```bash
cd frontend
npm install

# Create frontend .env
echo VITE_API_URL=http://localhost:8000 > .env

# Start development server
npm run dev
```

✅ Frontend running at **http://localhost:5173**

---

### 🐳 Option 2: Docker Deployment

```bash
# Clone repository
git clone https://github.com/hopessugar/mifos-loan-summarizer.git
cd mifos-loan-summarizer

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Build and start
docker compose up -d --build

# Check status
docker compose ps
```

**Access:**
- Frontend: http://localhost
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Stop:**
```bash
docker compose down
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React 19 + Vite)                 │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ ContractInput│  │  PdfUpload   │  │  AnalysisView   │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI + Python)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  AI Pipeline (Async)                  │  │
│  │  Input → Segment → Extract → Validate → Calculate    │  │
│  │          ↓           ↓          ↓          ↓          │  │
│  │    Sanitizer   LLM Provider  Levenshtein  EMI Check  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────┐  ┌─────────────────────────────────┐  │
│  │   Services     │  │      LLM Provider Registry       │  │
│  │ • ai_service   │  │ • Gemini   • Ollama  • Groq     │  │
│  │ • pdf_service  │  │ • Cerebras • HuggingFace        │  │
│  │ • fineract     │  │   (Timeout-based Fallback)       │  │
│  └────────────────┘  └─────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
              ┌──────────┴─────────┐
              ▼                    ▼
    ┌───────────────────┐  ┌──────────────┐
    │  LLM Provider API  │  │  Mifos X     │
    │  (Cloud/Local)     │  │  Fineract    │
    └───────────────────┘  └──────────────┘
```

---

## 📚 Documentation

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | POST | Analyze contract text |
| `/analyze/pdf` | POST | Upload & analyze PDF/DOCX/TXT |
| `/loanproducts` | GET | Fetch Mifos X loan products |
| `/health` | GET | Health check & LLM status |
| `/providers` | GET | List available LLM providers |

### Configuration

**Environment Variables:**

```env
# LLM Configuration
LLM_PRIMARY                  # Primary provider (gemini/ollama/groq/cerebras/hf_inference)
LLM_MODEL                    # Model name for primary
LLM_FALLBACK                 # Fallback provider
LLM_FALLBACK_MODEL           # Model name for fallback
PRIMARY_PROVIDER_TIMEOUT     # Timeout in seconds (default: 120)
FALLBACK_ON_TIMEOUT          # Enable fallback (true/false)

# API Authentication
API_KEY                      # API key for authentication (optional in dev)

# Validation Thresholds
LEVENSHTEIN_THRESHOLD        # String similarity threshold (0.80)
COSINE_THRESHOLD             # Semantic similarity threshold (0.80)
MATH_TOLERANCE               # EMI calculation tolerance (0.10)
CONFIDENCE_THRESHOLD         # Minimum confidence for extraction (0.50)

# Mifos X Integration
FINERACT_URL                 # Fineract API URL
FINERACT_USER                # Fineract username
FINERACT_PASSWORD            # Fineract password
FINERACT_TENANT              # Tenant identifier (default)
FINERACT_SSL_VERIFY          # Enable SSL verification (true)
```

### Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_validator.py -v           # Unit tests
pytest -m integration -v                    # Integration tests
pytest tests/test_prompt_injection.py -v   # Security tests

# Open coverage report
open htmlcov/index.html
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### 📝 Step 1: Fork & Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/mifos-loan-summarizer.git
cd mifos-loan-summarizer
git remote add upstream https://github.com/hopessugar/mifos-loan-summarizer.git
```

### 🌿 Step 2: Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 💻 Step 3: Make Changes

- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Run tests before committing

### ✅ Step 4: Test Your Changes

```bash
# Backend tests
cd backend
pytest

# Frontend build check
cd frontend
npm run build

# Linting
cd backend
ruff check .
```

### 📦 Step 5: Commit & Push

```bash
git add .
git commit -m "feat: Add new feature description"
git push origin feature/your-feature-name
```

### 🔀 Step 6: Create Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template
5. Submit for review

### 📋 Contribution Guidelines

- **Code Style**: Follow PEP 8 for Python, ESLint rules for JavaScript
- **Commit Messages**: Use [Conventional Commits](https://www.conventionalcommits.org/)
  - `feat:` New feature
  - `fix:` Bug fix
  - `docs:` Documentation changes
  - `test:` Adding tests
  - `refactor:` Code refactoring
- **Tests**: All new features must include tests
- **Documentation**: Update README if adding features

---

## 🐛 Reporting Issues

Found a bug? Have a feature request?

1. Check [existing issues](https://github.com/hopessugar/mifos-loan-summarizer/issues)
2. Create a new issue with:
   - **Clear title** describing the problem
   - **Steps to reproduce** (for bugs)
   - **Expected vs actual behavior**
   - **Screenshots** (if applicable)
   - **Environment details** (OS, Python/Node version)

---

## 🎯 Roadmap

### Phase 1 ✅ (Completed - July 2026)
- [x] PDF/DOCX/TXT upload & text extraction
- [x] Multi-provider LLM support (Gemini, Ollama, Groq, Cerebras, HF)
- [x] Timeout-based fallback system
- [x] Hallucination detection (Levenshtein + TF-IDF)
- [x] Risk scoring & BPS calculation
- [x] Plain-language summarization
- [x] WhatsApp export
- [x] 95+ comprehensive tests

### Phase 2 🚧 (August 2026)
- [ ] Mifos X Fineract full integration
- [ ] Multi-language support (Hindi, Spanish, French)
- [ ] Advanced visualization (charts, graphs)
- [ ] Loan comparison tool
- [ ] Mobile app (React Native)
- [ ] Batch processing for multiple contracts

### Future Enhancements 🔮
- [ ] Voice input/output
- [ ] Blockchain verification
- [ ] Smart contract generation
- [ ] AI-powered negotiation suggestions
- [ ] Integration with credit bureaus

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| **Lines of Code** | 3,500+ (Backend) |
| **Test Coverage** | 85%+ |
| **Test Cases** | 95+ |
| **Supported LLMs** | 5 providers, 10+ models |
| **Languages** | English, Hindi |
| **Document Types** | PDF, DOCX, TXT, Images |
| **Extraction Accuracy** | 88-100% |
| **Average Response Time** | <5s (cloud), <120s (local) |

---

## 🔐 Security

- 🔒 **API Key Authentication** on all endpoints
- 🛡️ **Input Sanitization** & prompt injection detection
- 🚫 **No Data Storage** - contracts processed in-memory only
- ✅ **SSL/TLS Verification** enforced in production
- 🔑 **Environment-based secrets** (never hardcoded)
- ⚡ **Rate Limiting** on API endpoints
- 📏 **Request Size Limits** (max 1MB)

**Security Reporting:** If you discover a security vulnerability, please email security@example.com (do not create a public issue).

---

## 📜 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built for **Google Summer of Code 2026** with the **Mifos Initiative**.

**Special Thanks:**
- [Mifos Initiative](https://mifos.org/) - Financial Inclusion Platform
- [Apache Fineract](https://fineract.apache.org/) - Core Banking Platform
- [Google Gemini](https://ai.google.dev/) - AI Infrastructure
- [Ollama](https://ollama.com/) - Local LLM Runtime
- Open Source Community

---

## 👨‍💻 Author

**Silky Vyas**  
GSoC 2026 Contributor | Mifos Initiative

- GitHub: [@hopessugar](https://github.com/hopessugar)
- Email: silkyvyas@example.com

---

## 📞 Support

Need help? Have questions?

- 📖 Read the [Documentation](https://github.com/hopessugar/mifos-loan-summarizer/wiki)
- 💬 Join our [Discord Community](https://discord.gg/mifos)
- 🐛 Report bugs via [GitHub Issues](https://github.com/hopessugar/mifos-loan-summarizer/issues)
- 📧 Email: support@mifos.org

---

<div align="center">

### ⭐ If you find this project useful, please star the repository!

Made with ❤️ by the Mifos Community

[⬆ Back to Top](#-mifos-loan-summarizer)

</div>
