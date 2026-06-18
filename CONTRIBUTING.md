# Contributing to Mifos Loan Summarizer

Thank you for considering contributing to the Mifos Loan Summarizer! This document outlines how to set up the project, run tests, and submit contributions.

## Prerequisites

- **Docker Desktop** (recommended) — for containerized development
- **Python 3.11+** — for local backend development
- **Node.js 18+** — for local frontend development
- **Git**

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/your-org/mifos-loan-summarizer.git
cd mifos-loan-summarizer
cp .env.example .env
# Edit .env with your Gemini API key
```

### 2. Run with Docker (recommended)

```bash
docker compose up -d
```

- **Frontend**: http://localhost:80
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 3. Run tests

```bash
docker exec mifos-backend python -m pytest tests/ -v --tb=short
```

## Project Structure

```
mifos-loan-summarizer/
├── backend/
│   ├── main.py              # FastAPI application entry
│   ├── auth.py              # API key authentication
│   ├── config.py            # Settings (env vars + YAML)
│   ├── exceptions.py        # Custom exception hierarchy
│   ├── pipeline/
│   │   ├── segmenter.py     # Contract text segmentation
│   │   ├── extractor.py     # LLM extraction chain
│   │   ├── validator.py     # Hallucination detection + risk scoring
│   │   ├── summariser.py    # Natural language summary
│   │   ├── financial_calculator.py  # EMI/interest calculations
│   │   ├── input_sanitizer.py       # Prompt injection defense
│   │   └── prompts.py       # LLM prompt templates
│   ├── providers/
│   │   ├── base.py           # LLM provider interface
│   │   ├── registry.py       # Provider registry (singleton cache)
│   │   ├── gemini_provider.py
│   │   └── ...               # Other providers
│   ├── schemas/
│   │   ├── loan_schema.py    # Pydantic extraction schema
│   │   ├── request.py        # API request models
│   │   └── response.py       # API response models
│   ├── services/
│   │   ├── ai_service.py     # Main analysis orchestrator
│   │   ├── fineract_service.py # Apache Fineract integration
│   │   └── audit_service.py  # JSONL audit trail
│   ├── routers/
│   │   ├── analysis.py       # /analyze endpoint
│   │   └── health.py         # /health endpoint
│   └── tests/                # Pytest test suite
├── frontend/
│   ├── src/
│   │   ├── components/       # React-style Vanilla JS components
│   │   ├── services/api.js   # API client
│   │   └── App.jsx           # Main application
│   └── Dockerfile
├── docker-compose.yml
├── .env.example              # Environment variable template
└── CONTRIBUTING.md           # This file
```

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8. Use type hints. Use `logging` (never `print()`).
- **JavaScript**: Use ES6+ syntax. Use `const`/`let` (never `var`).
- **Imports**: Use relative imports within packages (`from pipeline.validator import ...`).
- **Error handling**: Use custom exceptions from `exceptions.py` — never raise bare `Exception`.

### Testing

Tests live in `backend/tests/`. We use **pytest** with these conventions:

| Convention | Example |
|---|---|
| File naming | `test_<module>.py` |
| Test classes | `class TestFeatureName:` |
| Test functions | `def test_specific_behavior():` |
| Fixtures | Put in `conftest.py` |

**Run specific test file:**
```bash
docker exec mifos-backend python -m pytest tests/test_financial_calculator.py -v
```

**Critical tests** (must pass before merging):
- `test_financial_calculator.py` — EMI calculations (fintech correctness)
- `test_input_sanitizer.py` — Prompt injection defense
- `test_loan_schema.py` — Data model integrity

### Security Checklist

Before submitting a PR, verify:

- [ ] No API keys or secrets in code or frontend bundle
- [ ] All user input is sanitized before LLM calls
- [ ] New endpoints have authentication (`Depends(verify_api_key)`)
- [ ] Provider inputs are validated against allowlist
- [ ] No `print()` statements (use `logger`)
- [ ] Financial calculations use `Decimal` (never `float`)

### Adding a New LLM Provider

1. Create `backend/providers/<name>_provider.py`
2. Extend `BaseLLMProvider` from `providers/base.py`
3. Implement `generate_native()`, `health_check()`, `get_model_name()`
4. Register in `providers/registry.py`
5. Add provider name to `Literal` allowlist in `schemas/request.py`
6. Add tests in `tests/test_<name>_provider.py`

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add Hindi language support
fix: handle null interest rate in validator
security: add request body size limit
perf: cache provider instances as singletons
test: add EMI consistency edge cases
docs: update API documentation
```

## License

By contributing, you agree that your contributions will be licensed under the project's Apache 2.0 License.
