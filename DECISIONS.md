# Design Decisions

Every non-obvious architectural choice is documented here with rationale.

## 1. React + Vite instead of Streamlit
Frontend is React 18 + Vite + Tailwind CSS. Streamlit is a prototyping tool and cannot
support the component architecture needed for production use by loan officers.

## 2. LangChain + Instructor instead of raw API calls
LangChain gives provider portability. Instructor gives schema enforcement + self-healing
retries. Together they eliminate malformed JSON output and provider-specific logic
scattered through business code.

## 3. Ollama as default (local-first architecture)
Loan agreements contain sensitive borrower PII. India's DPDP Act (2023) requires
appropriate safeguards. Local-first means no data leaves the institution's hardware.
Ollama will be set up once RAM is upgraded to 16GB. HuggingFace Inference API is
used as default during development.

## 4. RunnableParallel for validation chain
All 4 validation checks are independent so they run concurrently, bringing total
validation time down to the slowest single check instead of the sum of all four.

## 5. Levenshtein for short values, TF-IDF cosine for long clauses
Levenshtein works well for short values with minor formatting differences.
TF-IDF cosine captures semantic similarity for longer clause-level text.

## 6. HuggingFace Inference API as development default
Free tier, no credit card, OpenAI-compatible. Replaced by Ollama local inference
once hardware supports it (16GB RAM).

## 7. Open source providers only
Per Mifos mentor guidance, only open source LLM providers are used:
HuggingFace Inference API (Qwen, Llama — Apache 2.0), Ollama (local),
Groq free tier (Llama), Cerebras free tier (Llama). No OpenAI, Gemini,
Mistral, or other proprietary APIs.
