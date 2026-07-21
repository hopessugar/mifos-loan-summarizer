<h1 align="center">
  <br>
  🏦
  <br>
  Mifos Loan Summarizer
  <br>
  <sub>AI-Powered Loan Contract Analysis</sub>
  <br>
  <br>
</h1>

<p align="center">
  <b>Transform complex loan agreements into clear, borrower-friendly summaries</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/Tests-95%20Passing-success?style=flat" alt="Tests">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green?style=flat" alt="License">
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-prerequisites">Prerequisites</a> •
  <a href="#-quick-start-docker">Quick Start</a> •
  <a href="#-manual-installation">Manual Setup</a> •
  <a href="#-llm-provider-setup">LLM Providers</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-testing">Testing</a> •
  <a href="#-troubleshooting">Troubleshooting</a>
</p>

<br>

---

<br>

## 📖 Overview

An intelligent system that uses **Large Language Models** to extract financial terms from loan contracts, validate data accuracy, and generate plain-language summaries for borrowers.

Built for **GSoC 2026** with the **Mifos Initiative**.

### The Problem

- 📄 Complex legal language confuses borrowers
- 🌍 Language barriers in multilingual communities
- ⚖️ Hidden fees buried in fine print
- 💸 Borrowers don't understand true loan costs

### The Solution

- 🤖 AI extracts 20+ financial entities with 88–100% accuracy
- ✓ Validates extracted data against the source contract (hallucination detection)
- ⚠️ Calculates risk scores on a 0–10 scale
- 📝 Generates plain-language summaries
- 💬 Exports to WhatsApp for easy sharing
- 🔌 Integrates with Mifos X / Apache Fineract

<br>

---

<br>

## ✨ Features

| Feature | Description |
|---|---|
| **Smart Extraction** | 20+ entities including rates, fees, penalties, terms |
| **Hallucination Detection** | Levenshtein + TF-IDF similarity matching against source text |
| **Risk Analysis** | Multi-factor scoring with clear warnings |
| **Math Validation** | Cross-checks calculations (EMI, total cost) for consistency |
| **PDF/DOCX/Image Upload** | Upload contracts as PDF, DOCX, TXT, or images (with OCR) |
| **Mifos Integration** | Direct Fineract API integration for loan product lookup |
| **Multi-Language** | English, Hindi (more coming) |
| **WhatsApp Export** | <300 character shareable summaries |
| **No Storage** | Contracts never saved — processed in-memory only |
| **Multi-Provider LLM** | Gemini, Groq, Cerebras, HuggingFace, Ollama (local) |

<br>

---

<br>

## 📋 Prerequisites

Before you begin, make sure you have the following installed on your machine:

### For Docker Setup (Recommended)

| Tool | Version | Install |
|---|---|---|
| **Git** | Any | [git-scm.com](https://git-scm.com/downloads) |
| **Docker Desktop** | 4.x+ | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) |

> **Windows Users:** Docker Desktop requires WSL 2. If prompted, follow the [WSL 2 installation guide](https://learn.microsoft.com/en-us/windows/wsl/install).

### For Manual Setup

| Tool | Version | Install |
|---|---|---|
| **Git** | Any | [git-scm.com](https://git-scm.com/downloads) |
| **Python** | 3.11+ | [python.org/downloads](https://www.python.org/downloads/) |
| **Node.js** | 18+ (20 recommended) | [nodejs.org](https://nodejs.org/) |
| **npm** | 9+ (comes with Node.js) | Bundled with Node.js |
| **Tesseract OCR** | *(Optional — for scanned PDFs/images)* | See [OCR Setup](#-optional-tesseract-ocr-for-scanned-pdfs) |

### LLM API Key (Required)

You need **at least one** LLM provider API key. See the [LLM Provider Setup](#-llm-provider-setup) section for details. The quickest free options:

| Provider | Free Tier | Get API Key |
|---|---|---|
| **Google Gemini** | ✅ Generous free tier | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| **Groq** | ✅ Free tier available | [console.groq.com/keys](https://console.groq.com/keys) |
| **Ollama** | ✅ Fully free (runs locally) | [ollama.com/download](https://ollama.com/download) |

<br>

---

<br>

## 🐳 Quick Start (Docker)

This is the **recommended** way to run the project. It sets up both the backend and frontend in isolated containers with a single command.

### Step 1 — Clone the Repository

```bash
git clone https://github.com/hopessugar/mifos-loan-summarizer.git
cd mifos-loan-summarizer
```

### Step 2 — Create the Environment File

```bash
# Copy the example environment file
cp .env.example .env
```

> **Windows (Command Prompt):**
> ```cmd
> copy .env.example .env
> ```

### Step 3 — Add Your API Key

Open the `.env` file in any text editor and set **at least one** LLM provider key:

```dotenv
# Pick your LLM provider (gemini, groq, cerebras, ollama, hf_inference)
LLM_PRIMARY=gemini
LLM_MODEL=gemini-2.5-flash-lite

# Set the API key for your chosen provider
GEMINI_API_KEY=your-gemini-api-key-here
```

> **Tip:** For local/offline usage, set `LLM_PRIMARY=ollama` — no API key needed! See [Ollama Setup](#option-e-ollama-free-local-models).

### Step 4 — Build & Start

```bash
docker compose up -d --build
```

Or use the convenience scripts:

```bash
# Linux / macOS
./build.sh && ./start.sh

# Windows
build.bat
start.bat
```

### Step 5 — Open the App

Wait ~30 seconds for the services to initialize, then open:

| Service | URL |
|---|---|
| **Frontend (Web UI)** | [http://localhost](http://localhost) |
| **Backend API** | [http://localhost:8000](http://localhost:8000) |
| **API Documentation (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) |

### Stopping the Services

```bash
docker compose down

# Or on Windows:
stop.bat
```

<br>

---

<br>

## 🔧 Manual Installation

If you prefer to run the backend and frontend directly on your machine without Docker.

### Step 1 — Clone the Repository

```bash
git clone https://github.com/hopessugar/mifos-loan-summarizer.git
cd mifos-loan-summarizer
```

### Step 2 — Backend Setup

#### 2a. Create a Python virtual environment

```bash
cd backend
```

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> If you get an execution policy error, run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

</details>

<details>
<summary><b>Windows (Command Prompt)</b></summary>

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

</details>

<details>
<summary><b>macOS / Linux</b></summary>

```bash
python3 -m venv venv
source venv/bin/activate
```

</details>

#### 2b. Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note:** This may take 2–5 minutes. Some packages (`scikit-learn`, `python-Levenshtein`) require C compilation. On Linux, you may need: `sudo apt install build-essential python3-dev`

#### 2c. Download NLTK data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

#### 2d. Create the environment file

```bash
# From the project root (go back one level)
cd ..
cp .env.example .env
```

> **Windows:** `copy .env.example .env`

Edit `.env` and set your API key (see [Step 3 of Docker setup](#step-3--add-your-api-key) above).

#### 2e. Start the backend server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

You should see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

✅ **Verify:** Open [http://localhost:8000/docs](http://localhost:8000/docs) — you should see the Swagger API documentation.

### Step 3 — Frontend Setup

Open a **new terminal window** (keep the backend running).

```bash
cd frontend
npm install
```

> **Note:** First run downloads ~100MB of dependencies. Subsequent runs will be fast.

Create the frontend env file:

```bash
# From the frontend/ directory
echo VITE_API_URL=http://localhost:8000 > .env
```

Start the development server:

```bash
npm run dev
```

You should see:

```
  VITE v8.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

✅ **Verify:** Open [http://localhost:5173](http://localhost:5173) — you should see the Mifos Loan Summarizer UI.

### Summary of Running Services (Manual)

| Service | URL | Terminal |
|---|---|---|
| Backend API | [http://localhost:8000](http://localhost:8000) | Terminal 1 |
| Frontend UI | [http://localhost:5173](http://localhost:5173) | Terminal 2 |
| API Docs | [http://localhost:8000/docs](http://localhost:8000/docs) | — |

<br>

---

<br>

## 🤖 LLM Provider Setup

The application needs at least one LLM provider to work. You configure this in the `.env` file at the project root.

### Option A: Google Gemini ⭐ (Recommended)

1. Go to [Google AI Studio](https://aistudio.google.com/apikey) and create an API key
2. Set in `.env`:

```dotenv
LLM_PRIMARY=gemini
LLM_MODEL=gemini-2.5-flash-lite
GEMINI_API_KEY=your-api-key-here
```

### Option B: Groq (Free Tier)

1. Sign up at [console.groq.com](https://console.groq.com)
2. Generate an API key at [console.groq.com/keys](https://console.groq.com/keys)
3. Set in `.env`:

```dotenv
LLM_PRIMARY=groq
LLM_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=your-api-key-here
```

### Option C: Cerebras (Free Tier)

1. Sign up at [cloud.cerebras.ai](https://cloud.cerebras.ai)
2. Get an API key from your dashboard
3. Set in `.env`:

```dotenv
LLM_PRIMARY=cerebras
LLM_MODEL=llama3.1-8b
CEREBRAS_API_KEY=your-api-key-here
```

### Option D: HuggingFace Inference API

1. Sign up at [huggingface.co](https://huggingface.co)
2. Create a token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) (read access is enough)
3. Set in `.env`:

```dotenv
LLM_PRIMARY=hf_inference
LLM_MODEL=Qwen/Qwen2.5-72B-Instruct
HF_TOKEN=hf_your-token-here
```

### Option E: Ollama (Free, Local Models)

Ollama lets you run LLMs **entirely on your own machine** — no API key, no internet required.

#### 1. Install Ollama

| OS | Install Command |
|---|---|
| **Windows** | Download from [ollama.com/download](https://ollama.com/download) |
| **macOS** | `brew install ollama` or download from [ollama.com](https://ollama.com/download) |
| **Linux** | `curl -fsSL https://ollama.com/install.sh \| sh` |

#### 2. Start the Ollama server

```bash
ollama serve
```

> Ollama runs in the background on port `11434`. Leave this terminal open.

#### 3. Pull a model (optional — it auto-pulls on first use)

```bash
ollama pull llama3.2:latest
```

**Recommended models by hardware:**

| Model | Size | RAM Needed | Best For |
|---|---|---|---|
| `llama3.2:1b` | 1.3 GB | 4 GB | Testing, low-end hardware |
| `llama3.2:latest` | 2.0 GB | 6 GB | Balanced speed/quality |
| `phi3:mini` | 2.3 GB | 6 GB | Good reasoning |
| `mistral:latest` | 4.1 GB | 8 GB | Strong general-purpose |
| `qwen2.5:7b` | 4.7 GB | 8 GB | Excellent JSON output ⭐ |

#### 4. Set in `.env`

```dotenv
LLM_PRIMARY=ollama
LLM_MODEL=llama3.2:latest
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
```

> **Docker + Ollama:** If running Ollama on your host and the app in Docker, set `OLLAMA_BASE_URL=http://host.docker.internal:11434` in `.env`.

<br>

---

<br>

## 📸 (Optional) Tesseract OCR for Scanned PDFs

Tesseract is only needed if you want to process **scanned PDFs or image files**. Text-based PDFs, DOCX, and TXT files work without it.

| OS | Install Command |
|---|---|
| **Windows** | `winget install UB-Mannheim.TesseractOCR` |
| **macOS** | `brew install tesseract` |
| **Ubuntu/Debian** | `sudo apt install tesseract-ocr` |

**Windows users:** After installation, add the Tesseract path to your `.env`:

```dotenv
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

> **Docker users:** Tesseract is already included in the Docker image — no extra setup needed.

<br>

---

<br>

## 🚀 Usage

### Using the Web UI

1. **Open the app** in your browser ([http://localhost:5173](http://localhost:5173) for manual setup, or [http://localhost](http://localhost) for Docker)
2. **Paste a loan contract** in the text area, **or upload a file** (PDF, DOCX, TXT, or image)
3. Click **Analyze** to extract financial terms
4. Review the results:
   - **Extracted Terms** — all financial entities found in the contract
   - **Risk Score** — overall risk assessment (0–10 scale)
   - **Plain-Language Summary** — borrower-friendly explanation
   - **Validation Report** — hallucination detection results
5. **Export to WhatsApp** — generates a compact summary you can share

### Sample Contract (for testing)

You can try with this sample text:

```text
LOAN AGREEMENT

Loan Amount: Rs. 1,00,000
Interest Rate: 18% per annum
Loan Tenure: 24 months
Monthly EMI: Rs. 4,992
Processing Fee: Rs. 2,000
Late Payment Penalty: Rs. 500/month
Prepayment Penalty: 2% of outstanding
```

Or use one of the pre-built sample contracts in the [`sample_contracts/`](sample_contracts/) directory.

### Using the REST API

You can also interact directly with the backend API:

```bash
# Analyze a loan contract (text input)
curl -X POST http://localhost:8000/api/v1/analysis/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"contract_text": "Loan Amount: Rs. 1,00,000\nInterest Rate: 18%\nTenure: 24 months"}'
```

```bash
# Upload a PDF file
curl -X POST http://localhost:8000/api/v1/analysis/upload \
  -H "X-API-Key: your-api-key" \
  -F "file=@/path/to/contract.pdf"
```

```bash
# Check API health
curl http://localhost:8000/health
```

> **Full API documentation** is available at [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI).

<br>

---

<br>

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                │
│  Components: ContractInput, PdfUpload, AnalysisView,     │
│              ExportButton, MifosProductPicker             │
└────────────────────────┬─────────────────────────────────┘
                         │  HTTP (REST API)
                         ▼
┌──────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                       │
│  Routers: /analysis  /loanproducts  /health  /simulator  │
├────────────┬───────────────────────┬─────────────────────┤
│  Services  │     AI Pipeline       │   LLM Providers     │
│            │                       │                     │
│ ai_service │  input_sanitizer      │  gemini_provider    │
│ pdf_service│  segmenter            │  groq_provider      │
│ fineract   │  extractor            │  cerebras_provider  │
│ audit      │  validator            │  hf_inference       │
│            │  financial_calculator │  ollama_provider     │
│            │  summariser           │                     │
└────────────┴───────────────────────┴─────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
     ┌──────────────┐     ┌──────────────────┐
     │ LLM Provider │     │ Apache Fineract  │
     │ (Gemini/Groq │     │   (Mifos X)      │
     │  /Ollama/..) │     │   REST API       │
     └──────────────┘     └──────────────────┘
```

### How the Pipeline Works

1. **Input Sanitization** — Cleans and validates the contract text, detects prompt injection
2. **Segmentation** — Splits long contracts into manageable chunks
3. **Extraction** — LLM extracts 20+ financial entities into structured JSON
4. **Validation** — Checks extracted data against source text (Levenshtein + cosine similarity)
5. **Financial Calculation** — Validates EMI, total cost, and other math
6. **Summarization** — Generates a plain-language summary with risk score

<br>

---

<br>

## 🧪 Testing

The project has **95+ tests** covering unit, integration, and security scenarios.

### Run All Tests

```bash
cd backend
pytest
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in your browser to view the report
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/test_validator.py tests/test_extractor.py tests/test_loan_schema.py -v

# Security tests
pytest tests/test_auth.py tests/test_prompt_injection.py tests/test_secrets_management.py -v

# Integration tests (require external services/API keys)
pytest -m integration -v

# Skip slow tests
pytest -m "not slow" -v
```

<br>

---

<br>

## 📁 Project Structure

```
mifos-loan-summarizer/
├── backend/                    # FastAPI backend
│   ├── main.py                 # Application entrypoint
│   ├── config.py               # Settings (env + YAML)
│   ├── auth.py                 # API key authentication
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Backend Docker image
│   ├── routers/                # API route handlers
│   │   ├── analysis.py         #   /api/v1/analysis/*
│   │   ├── loanproducts.py     #   /api/v1/loanproducts/*
│   │   ├── health.py           #   /health
│   │   ├── providers.py        #   /api/v1/providers/*
│   │   └── simulator.py        #   /api/v1/simulator/*
│   ├── pipeline/               # AI processing pipeline
│   │   ├── input_sanitizer.py  #   Input cleaning + injection detection
│   │   ├── segmenter.py        #   Contract text chunking
│   │   ├── extractor.py        #   LLM-based entity extraction
│   │   ├── validator.py        #   Hallucination detection
│   │   ├── financial_calculator.py  # Math validation
│   │   ├── summariser.py       #   Summary generation
│   │   └── prompts.py          #   LLM prompt templates
│   ├── providers/              # LLM provider integrations
│   │   ├── gemini_provider.py
│   │   ├── groq_provider.py
│   │   ├── cerebras_provider.py
│   │   ├── hf_inference_provider.py
│   │   ├── ollama_provider.py
│   │   └── registry.py         #   Provider factory
│   ├── services/               # Business logic services
│   │   ├── ai_service.py       #   Orchestrates the pipeline
│   │   ├── pdf_service.py      #   PDF/DOCX/image text extraction
│   │   ├── fineract_service.py #   Mifos X API integration
│   │   └── audit_service.py    #   Analysis audit logging
│   └── tests/                  # 95+ test files
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx             # Main application component
│   │   ├── components/         # UI components
│   │   │   ├── ContractInput/  #   Text input area
│   │   │   ├── PdfUpload/      #   File upload widget
│   │   │   ├── AnalysisView/   #   Results display
│   │   │   ├── ExportButton/   #   WhatsApp export
│   │   │   └── MifosProductPicker/  # Fineract product selector
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API client
│   │   ├── context/            # React context providers
│   │   └── i18n/               # Internationalization
│   ├── package.json
│   ├── Dockerfile              # Frontend Docker image (Nginx)
│   └── nginx.conf              # Production Nginx config
├── sample_contracts/           # 29 sample loan contracts for testing
├── .env.example                # Environment variable template
├── config.example.yaml         # YAML configuration template
├── docker-compose.yml          # Docker services definition
├── build.bat / build.sh        # Build scripts (Windows/Linux)
├── start.bat / start.sh        # Start scripts
├── stop.bat / stop.sh          # Stop scripts
├── CONTRIBUTING.md             # Contribution guidelines
└── .github/workflows/          # CI/CD pipelines
    ├── ci.yml                  #   Tests + linting
    ├── cd.yml                  #   Deployment
    └── security.yml            #   Security scanning
```

<br>

---

<br>

## 🔐 Security

- 🔐 **API key authentication** on all endpoints (configurable via `API_KEY` env var)
- 🔒 **SSL/TLS verification** enforced for all external connections (mandatory in production)
- 🛡️ **Input sanitization** and prompt injection detection
- 🚫 **No data storage** — contracts are processed in-memory only
- 🔑 **Environment variables** for all secrets (never hardcoded)
- ⚡ **Rate limiting** on API endpoints via SlowAPI
- 📏 **Request size limits** — max 1MB request body
- ✅ **Automated security scanning** in CI/CD

<br>

---

<br>

## ❓ Troubleshooting

<details>
<summary><b>Docker: "port 80 is already in use"</b></summary>

Another service (like IIS or Apache) is using port 80. Either stop that service or change the frontend port in `docker-compose.yml`:

```yaml
frontend:
  ports:
    - "3000:8080"   # Change 80 to 3000 (or any free port)
```

Then access the frontend at `http://localhost:3000`.
</details>

<details>
<summary><b>Docker: "Cannot connect to the Docker daemon"</b></summary>

Docker Desktop is not running. Start Docker Desktop and try again.

- **Windows:** Launch Docker Desktop from the Start menu
- **macOS:** Launch Docker Desktop from Applications
- **Linux:** Run `sudo systemctl start docker`
</details>

<details>
<summary><b>Backend: "ModuleNotFoundError: No module named 'xyz'"</b></summary>

Your virtual environment is not activated or dependencies aren't installed:

```bash
# Activate the venv first
# Windows: .\venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate

pip install -r requirements.txt
```
</details>

<details>
<summary><b>Backend: "No .env file found"</b></summary>

Copy the example env file:

```bash
# From the project root
cp .env.example .env
# Then edit .env with your API keys
```
</details>

<details>
<summary><b>Frontend: "VITE_API_URL not set" or API calls failing</b></summary>

Make sure the frontend `.env` file exists:

```bash
cd frontend
echo VITE_API_URL=http://localhost:8000 > .env
```

Restart the Vite dev server after creating/editing `.env`.
</details>

<details>
<summary><b>LLM: "API key not valid" or "authentication failed"</b></summary>

1. Check your `.env` file has the correct API key for your chosen provider
2. Make sure `LLM_PRIMARY` matches the provider whose key you set
3. Verify the key hasn't expired at your provider's dashboard
</details>

<details>
<summary><b>Ollama: "connection refused" on localhost:11434</b></summary>

Ollama server isn't running. Start it:

```bash
ollama serve
```

If using Docker, make sure `OLLAMA_BASE_URL=http://host.docker.internal:11434` in your `.env`.
</details>

<details>
<summary><b>OCR: "TesseractNotFoundError"</b></summary>

Tesseract is not installed or not on your PATH. Install it (see [OCR Setup](#-optional-tesseract-ocr-for-scanned-pdfs)), then set the path in `.env`:

```dotenv
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```
</details>

<details>
<summary><b>Windows PowerShell: "execution of scripts is disabled"</b></summary>

Run this command in an **elevated PowerShell** (Run as Administrator):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
</details>

<details>
<summary><b>npm install: "ERESOLVE unable to resolve dependency tree"</b></summary>

Try installing with the legacy peer deps flag:

```bash
npm install --legacy-peer-deps
```
</details>

<br>

---

<br>

## ⚙️ Configuration Reference

The app can be configured via **environment variables** (`.env` file) or a **YAML config** (`config.yaml`). Environment variables take priority over YAML.

| Variable | Default | Description |
|---|---|---|
| `LLM_PRIMARY` | `gemini` | LLM provider: `gemini`, `groq`, `cerebras`, `ollama`, `hf_inference` |
| `LLM_MODEL` | `gemini-2.5-flash-lite` | Model name for the primary provider |
| `LLM_FALLBACK` | *(empty)* | Optional fallback provider for multi-model consensus |
| `GEMINI_API_KEY` | *(empty)* | Google Gemini API key |
| `GROQ_API_KEY` | *(empty)* | Groq API key |
| `CEREBRAS_API_KEY` | *(empty)* | Cerebras API key |
| `HF_TOKEN` | *(empty)* | HuggingFace API token |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2:latest` | Ollama model name |
| `API_KEY` | *(empty)* | API authentication key (required in production) |
| `ENVIRONMENT` | `development` | Set to `production` to enforce security checks |
| `FINERACT_URL` | `https://demo.mifos.community/fineract-provider` | Mifos X Fineract API URL |
| `FINERACT_USER` | `mifos` | Fineract username |
| `FINERACT_PASSWORD` | `password` | Fineract password |
| `VITE_API_URL` | `http://localhost:8000` | Backend URL for the frontend |
| `MAX_INPUT_CHARS` | `2500` | Max characters for contract input |
| `EXTRACTION_MAX_TOKENS` | `1500` | Max tokens for LLM extraction |
| `LEVENSHTEIN_THRESHOLD` | `0.80` | Similarity threshold for validation |
| `TESSERACT_CMD` | *(auto-detect)* | Path to Tesseract executable |

<br>

---

<br>

## 🤝 Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) first.

```bash
# Create a feature branch
git checkout -b feature/your-feature

# Make your changes, then commit
git commit -m 'Add some feature'

# Push and create a pull request
git push origin feature/your-feature
```

<br>

---

<br>

## 📄 License

Apache License 2.0 — see [LICENSE](LICENSE) file for details.

<br>

---

<br>

## 🙏 Acknowledgments

Built for **GSoC 2026** with the **Mifos Initiative**

Special thanks to:
- Apache Fineract team
- LangChain community
- Groq for fast inference
- Google for Gemini API
- Open source contributors

<br>

---

<br>

<p align="center">
  <b>Made with ❤️ by Silky Vyas</b>
  <br>
  <sub>Star ⭐ this repo if you find it useful!</sub>
</p>

<p align="center">
  <a href="https://github.com/hopessugar/mifos-loan-summarizer/issues">Report Bug</a> •
  <a href="https://github.com/hopessugar/mifos-loan-summarizer/issues">Request Feature</a>
</p>

<br>
