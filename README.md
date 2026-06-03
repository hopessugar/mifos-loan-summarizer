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
  <img src="https://img.shields.io/badge/React-18+-61DAFB?style=flat&logo=react" alt="React">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/Tests-95%20Passing-success?style=flat" alt="Tests">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green?style=flat" alt="License">
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#usage">Usage</a> •
  <a href="#tech-stack">Tech Stack</a>
</p>

<br>

---

<br>

## Overview

An intelligent system that uses **Large Language Models** to extract financial terms from loan contracts, validate data accuracy, and generate plain-language summaries for borrowers.

Built for **GSoC 2026** with the **Mifos Initiative**.

<br>

### The Problem

- 📄 Complex legal language confuses borrowers
- 🌍 Language barriers in multilingual communities  
- ⚖️ Hidden fees buried in fine print
- 💸 Borrowers don't understand true loan costs

### The Solution

- 🤖 AI extracts 20+ financial entities with 88-100% accuracy
- ✓ Validates data against source contract
- ⚠️ Calculates risk scores (0-10 scale)
- 📝 Generates plain-language summaries
- 💬 Exports to WhatsApp for easy sharing
- 🔌 Integrates with Mifos X / Apache Fineract

<br>

---

<br>

## Features

- **Smart Extraction** — 20+ entities including rates, fees, penalties, terms
- **Hallucination Detection** — Levenshtein + TF-IDF similarity matching
- **Risk Analysis** — Multi-factor scoring with clear warnings
- **Math Validation** — Checks calculations for consistency  
- **Mifos Integration** — Direct Fineract API integration
- **Multi-Language** — English, Hindi (more coming)
- **WhatsApp Export** — <300 character shareable summaries
- **No Storage** — Contracts never saved, processed in-memory only

<br>

---

<br>

## Quick Start

### Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/hopessugar/mifos-loan-summarizer.git
cd mifos-loan-summarizer

# Configure environment
cp .env.example .env
# Edit .env with your API keys (Groq, Cerebras, or HuggingFace)

# Start services
docker-compose up -d

# Access
# Frontend: http://localhost
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Installation

<details>
<summary>Click to expand</summary>

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

</details>

<br>

---

<br>

## Usage

### 1. Paste Contract

```text
LOAN AGREEMENT

Loan Amount: Rs. 1,00,000
Interest Rate: 18% per annum  
Loan Tenure: 24 months
Monthly EMI: Rs. 4,992
Processing Fee: Rs. 2,000
Late Payment: Rs. 500/month
```

### 2. Get Analysis

```json
{
  "loan_amount": "₹100,000",
  "interest_rate": "18%",
  "risk_score": "2/10 (Low)",
  "total_cost": "₹119,808",
  "summary": "You'll repay ₹119,808 over 24 months..."
}
```

### 3. Export to WhatsApp

```
Loan: Rs.100,000 | Rate: 18.0% | EMI: Rs.4,992 
Total: Rs.119,808 | Risk: 2.0/10
```

<br>

---

<br>

## Tech Stack

**Frontend**  
React • Vite • Tailwind CSS

**Backend**  
FastAPI • Pydantic • Python 3.11+

**AI Pipeline**  
LangChain • Instructor • NLTK

**LLM Providers**  
Groq • Cerebras • HuggingFace • Ollama

**Integration**  
Apache Fineract REST API

**DevOps**  
Docker • Docker Compose • GitHub Actions

<br>

---

<br>

## Architecture

```
┌─────────────┐
│   Frontend  │  React UI for contract input
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Backend   │  FastAPI REST API
└──────┬──────┘
       │
       ├──────────────┐
       ▼              ▼
┌──────────┐   ┌──────────────┐
│ Fineract │   │  LLM Pipeline│
│   API    │   │  (LangChain) │
└──────────┘   └──────┬───────┘
                      │
                      ▼
               ┌──────────────┐
               │ LLM Provider │
               │ (Groq/etc)   │
               └──────────────┘
```

<br>

---

<br>

## Testing

```bash
# Run all tests
cd backend && pytest tests/ -v

# With coverage
pytest --cov=. --cov-report=html

# Test results: 95 tests passing, 85%+ coverage
```

<br>

---

<br>

## Security

- 🔐 API key authentication on all endpoints
- 🔒 SSL/TLS verification for all external connections
- 🛡️ Input sanitization and validation
- 🚫 No data storage - contracts processed in-memory only
- 🔑 Environment variables for all secrets
- ✅ Automated security scanning in CI/CD

<br>

---

<br>

## Contributing

Contributions welcome! Please read our [contributing guidelines](CONTRIBUTING.md) first.

```bash
git checkout -b feature/your-feature
git commit -m 'Add some feature'
git push origin feature/your-feature
```

<br>

---

<br>

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details

<br>

---

<br>

## Acknowledgments

Built for **GSoC 2026** with the **Mifos Initiative**

Special thanks to:
- Apache Fineract team
- LangChain community
- Groq for fast inference
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
