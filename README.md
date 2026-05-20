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

Add your HuggingFace token inside `config.yaml`.

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

| Method | Endpoint             | Description                      |
| ------ | -------------------- | -------------------------------- |
| `POST` | `/analyze`           | Full AI pipeline analysis        |
| `GET`  | `/loanproducts`      | Fetch all Fineract loan products |
| `GET`  | `/loanproducts/{id}` | Fetch single loan product        |
| `GET`  | `/health`            | Provider + API health status     |
| `GET`  | `/providers`         | List configured LLM providers    |

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

* 🔐 Fineract credentials remain server-side only
* 🚫 No contract data stored in databases
* 🧠 Open-source models supported by default
* 💻 Ollama local inference supported for offline deployments
* 🛡️ Frontend never receives API secrets

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

# 📜 License

MIT License

---

<div align="center">

### ⭐ If you like this project, consider starring the repository!

Built during **Google Summer of Code 2026** with the ❤️ of open source.

</div>
