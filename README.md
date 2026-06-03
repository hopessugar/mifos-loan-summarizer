<div align="center">

# 🏦 Mifos Loan Summarizer

### AI-Powered Loan Agreement Analysis

Transform complex loan contracts into clear, borrower-friendly summaries using LLMs and Apache Fineract integration.

[![CI Pipeline](https://github.com/hopessugar/mifos-loan-summarizer/workflows/CI%20Pipeline/badge.svg)](https://github.com/hopessugar/mifos-loan-summarizer/actions)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat&logo=react)](https://reactjs.org/)

[Features](#-features) • [Quick Start](#-quick-start) • [Demo](#-demo) • [Documentation](#-documentation) • [Contributing](#-contributing)

<img src="https://img.shields.io/badge/GSoC-2026-orange?style=for-the-badge" alt="GSoC 2026"/>
<img src="https://img.shields.io/badge/Mifos-Initiative-orange?style=for-the-badge" alt="Mifos Initiative"/>

</div>

---

## 🌟 Overview

Mifos Loan Summarizer is an intelligent system that analyzes loan agreements and contracts using Large Language Models (LLMs), extracting key financial terms, detecting risky clauses, and generating plain-language summaries suitable for borrowers with limited financial literacy.

### Why This Matters

In microfinance and rural banking:
- 📄 **Complex Contracts**: Legal jargon confuses borrowers
- 🌍 **Language Barriers**: English-only documents in multilingual communities
- ⚖️ **Information Asymmetry**: Borrowers don't understand true loan costs
- 📱 **Limited Access**: No internet for online contract analysis

**Our Solution**: Analyze contracts locally or via Mifos X integration, generate summaries in local languages, export to WhatsApp for sharing.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🤖 AI-Powered Analysis
- **20+ Entity Extraction**: Interest rates, EMIs, fees, penalties
- **Hallucination Detection**: Verify extracted values against source
- **Math Validation**: Check calculations for consistency
- **Risk Scoring**: 0-10 scale with detailed factors
- **Multi-Language**: English, Hindi (more coming)

</td>
<td width="50%">

### 🔌 Mifos X Integration
- **Fineract API**: Direct loan product fetching
- **Auto-Conversion**: JSON → Human-readable text
- **Same Pipeline**: No special handling needed
- **Real-time**: Analyze products on-demand

</td>
</tr>
<tr>
<td width="50%">

### 📊 Smart Validation
- **Source Verification**: Shows exact contract clauses
- **Confidence Scoring**: 0-100% for each field
- **Similarity Matching**: Levenshtein + TF-IDF
- **Math Checks**: Total cost validation

</td>
<td width="50%">

### 💬 Borrower-Friendly Output
- **Plain Language**: No financial jargon
- **WhatsApp Export**: <300 chars for sharing
- **Risk Highlights**: Clear warnings
- **Visual Dashboard**: Modern React UI

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

- **Docker** (recommended) or Python 3.11+ & Node 20+
- **API Keys**: Groq, Cerebras, or HuggingFace (free tier works)
- **Optional**: Ollama for local inference

### 🐳 Docker (Fastest)

```bash
# 1. Clone repository
git clone https://github.com/hopessugar/mifos-loan-summarizer.git
cd mifos-loan-summarizer

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start services
docker-compose up -d

# 4. Access application
# Frontend: http://localhost
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 💻 Manual Installation

<details>
<summary>Click to expand manual setup instructions</summary>

#### Backend

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Run
uvicorn main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install

# Configure
echo "VITE_API_URL=http://localhost:8000" > .env
echo "VITE_API_KEY=your-api-key" >> .env

# Run
npm run dev
```

</details>

---

## 🎯 Demo

### Input: Loan Contract

```
LOAN AGREEMENT

Loan Amount: Rs. 1,00,000
Interest Rate: 18% per annum
Loan Tenure: 24 months
Monthly EMI: Rs. 4,992
Processing Fee: Rs. 2,000
Late Payment Penalty: Rs. 500 per month
```

### Output: Analysis

<table>
<tr>
<td width="50%">

**📋 Extracted Entities**
- Loan Amount: ₹100,000 (88% confidence) ✓
- Interest Rate: 18% per annum (100%) ✓
- Duration: 24 months (88%) ✓
- Monthly EMI: ₹4,992 (88%) ✓
- Processing Fee: ₹2,000 (75%) ✓
- Late Fee: ₹500/month (73%) ✓

</td>
<td width="50%">

**⚠️ Risk Analysis**
- Score: **2/10** (Low risk)
- Factor: Moderately high interest rate (18%+)

**💰 Financial Summary**
- Total Repayment: ₹119,808
- Total Interest: ₹19,808
- Effective Rate: 19.81%

</td>
</tr>
</table>

**💬 WhatsApp Export**
```
Loan: Rs.100,000 | Rate: 18.0% | EMI: Rs.4,992 
Total: Rs.119,808 | Risk: 2.0/10
```

**📝 Plain-Language Summary**
> You've borrowed ₹100,000 at 18% annual interest. You'll repay over 24 months with monthly payments of ₹4,992. Total repayment will be ₹119,808, including ₹19,808 in interest. There's a ₹500 late payment fee and ₹2,000 processing fee.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Paste Text  │  │ Mifos Product│  │  Results Display │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend API (FastAPI)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  Auth Layer  │  │  Routers     │  │  Services        │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└───────────┬────────────────────────────────┬────────────────┘
            │                                │
            ▼                                ▼
┌───────────────────────┐      ┌──────────────────────────────┐
│  Fineract API         │      │     LLM Pipeline             │
│  (Mifos X Products)   │      │  ┌────────┐  ┌────────────┐ │
└───────────────────────┘      │  │Segment │→│  Extract   │ │
                               │  └────────┘  └────────────┘ │
                               │  ┌────────┐  ┌────────────┐ │
                               │  │Validate│→│ Summarize  │ │
                               │  └────────┘  └────────────┘ │
                               └──────────────────────────────┘
                                        │
                                        ▼
                               ┌──────────────────┐
                               │  LLM Providers   │
                               │  • Groq          │
                               │  • Cerebras      │
                               │  • HuggingFace   │
                               │  • Ollama        │
                               └──────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, Vite, Tailwind CSS |
| **Backend** | FastAPI, Pydantic v2, Python 3.11+ |
| **AI Pipeline** | LangChain, Instructor, NLTK |
| **LLM Providers** | Groq, Cerebras, HuggingFace, Ollama |
| **Integration** | Apache Fineract REST API |
| **Deployment** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |
| **Testing** | Pytest (95 tests), React Testing Library |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [HOW_TO_TEST.md](HOW_TO_TEST.md) | Step-by-step testing guide |
| [MIFOS_X_INTEGRATION_GUIDE.md](MIFOS_X_INTEGRATION_GUIDE.md) | Complete Fineract integration docs |
| [TESTING_INSTRUCTIONS.md](TESTING_INSTRUCTIONS.md) | Detailed testing procedures |
| [PRODUCTION_AUDIT_REPORT.md](PRODUCTION_AUDIT_REPORT.md) | Security audit and best practices |
| [API Docs](http://localhost:8000/docs) | Interactive Swagger documentation |

---

## 🔒 Security

- 🔐 **API Key Authentication**: Required for all sensitive endpoints
- 🔒 **SSL/TLS**: Certificate verification enforced for Fineract
- 🛡️ **Input Sanitization**: Prevent prompt injection attacks
- 🚫 **No Data Storage**: Contracts never saved to database
- 🔑 **Environment Variables**: All secrets via env vars
- ✅ **Security Scanning**: Automated via GitHub Actions

---

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test suite
pytest tests/test_integration_pipeline.py -v
```

**Test Coverage**: 85%+ | **Tests Passing**: 95/95

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'feat: add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

Please read [DECISIONS.md](DECISIONS.md) for architectural guidelines.

---

## 🐛 Known Issues

| Issue | Status | Workaround |
|-------|--------|------------|
| Mifos demo server (demo.mifos.io) unreachable | External | Use local Fineract or manual paste |
| Ollama integration not tested | Hardware | Requires 16GB RAM for testing |
| WhatsApp export shows full summary | Minor | Prompt tuning needed |

---

## 🗺️ Roadmap

- [ ] PDF contract upload support
- [ ] Batch analysis capability
- [ ] More languages (Tamil, Telugu, Bengali)
- [ ] RAGAS evaluation framework
- [ ] Contract comparison feature
- [ ] Mobile app (React Native)
- [ ] Offline mode with service workers

---

## 📊 Project Stats

<div align="center">

![GitHub code size](https://img.shields.io/github/languages/code-size/hopessugar/mifos-loan-summarizer)
![GitHub last commit](https://img.shields.io/github/last-commit/hopessugar/mifos-loan-summarizer)
![GitHub issues](https://img.shields.io/github/issues/hopessugar/mifos-loan-summarizer)
![GitHub pull requests](https://img.shields.io/github/issues-pr/hopessugar/mifos-loan-summarizer)

</div>

---

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Mifos Initiative** for the opportunity and mentorship
- **Apache Fineract** team for the excellent API
- **LangChain** community for the AI framework
- **GSoC 2026** program

---

## 📞 Contact & Support

- **Author**: Silky Vyas
- **GitHub**: [@hopessugar](https://github.com/hopessugar)
- **Issues**: [GitHub Issues](https://github.com/hopessugar/mifos-loan-summarizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/hopessugar/mifos-loan-summarizer/discussions)

---

<div align="center">

### ⭐ Star this repository if you find it useful!

**Built with ❤️ for GSoC 2026 • Mifos Initiative**

[⬆ Back to Top](#-mifos-loan-summarizer)

</div>
