# Local Model Setup Guide — Mifos Loan Summarizer

> **Complete step-by-step guide to run LLMs locally on your own machine and connect them to the Mifos Loan Summarizer app.**
> 
> No API keys needed. No cloud. No cost. Full data privacy.

---

## Table of Contents

1. [Why Run Local Models?](#why-run-local-models)
2. [Prerequisites & Hardware Requirements](#prerequisites--hardware-requirements)
3. [Step 1 — Install Ollama](#step-1--install-ollama)
4. [Step 2 — Download a Model](#step-2--download-a-model)
5. [Step 3 — Configure the App](#step-3--configure-the-app)
6. [Step 4 — Verify the Connection](#step-4--verify-the-connection)
7. [Step 5 — Run the App](#step-5--run-the-app)
8. [Model Selection Guide](#model-selection-guide)
9. [Docker Setup (Ollama in Container)](#docker-setup-ollama-in-container)
10. [GPU Acceleration Setup](#gpu-acceleration-setup)
11. [Performance Tuning](#performance-tuning)
12. [Advanced Configuration](#advanced-configuration)
13. [Troubleshooting](#troubleshooting)
14. [FAQ](#faq)

---

## Why Run Local Models?

| Benefit | Explanation |
|---------|-------------|
| 🔒 **Complete Data Privacy** | Loan contracts contain sensitive financial and personal data (SSN, Aadhaar, PAN, income, etc.). With local models, **zero data leaves your machine**. |
| 💰 **Zero Cost** | No API fees, no usage billing, no monthly subscriptions. Free forever. |
| 🌐 **Offline Capable** | Works without internet after initial model download. Perfect for rural MFI deployments. |
| ⚡ **No Rate Limits** | Process unlimited contracts — no 15 RPM cap like Gemini's free tier. |
| 🏛️ **Regulatory Compliance** | Meets data localization requirements (RBI data localization norms for India, GDPR for EU). |

---

## Prerequisites & Hardware Requirements

### Minimum Requirements

| Component | Minimum | Recommended | Best |
|-----------|---------|-------------|------|
| **OS** | Windows 10/11, macOS 12+, Linux (Ubuntu 20.04+) | Same | Same |
| **RAM** | 8 GB | 16 GB | 32 GB+ |
| **Disk Space** | 10 GB free | 20 GB free | 50 GB+ |
| **CPU** | Any modern x86_64 or ARM64 | 8+ cores | 12+ cores |
| **GPU (Optional)** | Not required | NVIDIA 6GB+ VRAM | NVIDIA 12GB+ VRAM |

### RAM Requirements Per Model

| Model Size | RAM Needed (CPU) | VRAM Needed (GPU) |
|------------|-----------------|-------------------|
| 1B params | ~2 GB | ~1 GB |
| 3B params | ~4 GB | ~3 GB |
| 7B params | ~8 GB | ~5 GB |
| 8B params | ~10 GB | ~6 GB |
| 13B params | ~16 GB | ~10 GB |
| 70B params | ~48 GB | ~40 GB |

> **Rule of thumb:** You need roughly **1.2× the model file size** in available RAM/VRAM.

### Software Prerequisites

- **Python 3.10+** — for the backend
- **Node.js 18+** — for the frontend
- **Git** — to clone the repo
- **(Optional) Docker** — for containerized deployment
- **(Optional) NVIDIA CUDA Toolkit** — for GPU acceleration

---

## Step 1 — Install Ollama

### Windows

1. **Download** the installer from [ollama.com/download](https://ollama.com/download)
2. **Run** `OllamaSetup.exe` — follow the prompts
3. Ollama installs as a **background service** and starts automatically
4. Verify installation — open PowerShell:

```powershell
ollama --version
# Expected output: ollama version 0.x.x
```

> **Note:** On Windows, Ollama runs as a system service. It starts automatically with Windows and listens on `http://localhost:11434`.

### macOS

```bash
# Option A: Download from ollama.com/download (recommended)
# Option B: Homebrew
brew install ollama

# Start Ollama
ollama serve
```

### Linux (Ubuntu/Debian)

```bash
# One-line install (official script)
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama as a service
sudo systemctl enable ollama
sudo systemctl start ollama

# Verify
ollama --version
systemctl status ollama
```

### Verify Ollama is Running

Open your browser or use curl:

```bash
curl http://localhost:11434
# Expected: "Ollama is running"
```

Or in PowerShell:
```powershell
Invoke-RestMethod http://localhost:11434
# Expected: "Ollama is running"
```

---

## Step 2 — Download a Model

### Quick Start (Recommended Model)

```bash
# Best balance of speed and quality for loan extraction
ollama pull qwen2.5:7b
```

This downloads ~4.7 GB. Takes 2-10 minutes depending on your internet speed.

### Other Recommended Models

```bash
# Fastest (for testing, low RAM machines)
ollama pull llama3.2:1b          # 1.3 GB download

# Good balance (default in this app)
ollama pull llama3.2:latest      # 2.0 GB download (3B params)

# Best quality (needs 16GB+ RAM)
ollama pull llama3.1:8b          # 4.7 GB download

# Excellent JSON output (great for extraction)
ollama pull qwen2.5:7b           # 4.7 GB download

# Google's open model (good reasoning)
ollama pull gemma2:9b            # 5.4 GB download

# Microsoft's model (good for structured tasks)
ollama pull phi3:mini             # 2.3 GB download
```

### Verify Model is Downloaded

```bash
ollama list
# Expected output:
# NAME              ID            SIZE    MODIFIED
# qwen2.5:7b        845dbda0ea48  4.7 GB  2 minutes ago
```

### Quick Test — Generate Text

```bash
ollama run qwen2.5:7b "Extract the loan amount from: The borrower receives $50,000"
```

If you get a sensible response mentioning $50,000, everything is working!

---

## Step 3 — Configure the App

### Option A: Edit `.env` File (Recommended)

Open the `.env` file in the project root (`c:\Users\vyass\Documents\mifos-loan-summarizer\.env`) and set these values:

```env
# ─── PRIMARY PROVIDER: Set to Ollama ───
LLM_PRIMARY=ollama

# ─── MODEL: Match what you downloaded in Step 2 ───
OLLAMA_MODEL=qwen2.5:7b

# ─── OLLAMA CONNECTION ───
# Default: http://localhost:11434 (no change needed if running locally)
OLLAMA_BASE_URL=http://localhost:11434

# ─── OPTIONAL: Cloud Fallback ───
# If Ollama is slow or fails, automatically switch to a cloud provider
LLM_FALLBACK=gemini
LLM_FALLBACK_MODEL=gemini-2.0-flash
GEMINI_API_KEY=your-gemini-api-key-here    # Only needed if using fallback

# ─── TIMEOUT: How long to wait before switching to fallback ───
PRIMARY_PROVIDER_TIMEOUT=120    # 120 seconds for local models (they're slower)
FALLBACK_ON_TIMEOUT=true
```

### Option B: No Fallback (Pure Offline)

If you want **zero cloud dependency** (fully offline):

```env
LLM_PRIMARY=ollama
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434

# No fallback — keep these empty
LLM_FALLBACK=
LLM_FALLBACK_MODEL=
GEMINI_API_KEY=
GROQ_API_KEY=
CEREBRAS_API_KEY=
HF_TOKEN=

PRIMARY_PROVIDER_TIMEOUT=180    # Give local model more time
FALLBACK_ON_TIMEOUT=false
```

### Important: Model Name Must Match Exactly

The `OLLAMA_MODEL` value must **exactly match** what `ollama list` shows:

```bash
ollama list
# NAME              ID            SIZE
# qwen2.5:7b        845dbda0ea48  4.7 GB    ← Use this exact name
```

```env
# ✅ Correct
OLLAMA_MODEL=qwen2.5:7b

# ❌ Wrong (will fail to find model)
OLLAMA_MODEL=qwen2.5
OLLAMA_MODEL=Qwen2.5:7B
OLLAMA_MODEL=qwen-2.5-7b
```

---

## Step 4 — Verify the Connection

### Test 1: Check Ollama is Running

```bash
curl http://localhost:11434/api/tags
```

Expected: JSON response listing your downloaded models.

### Test 2: Start the Backend & Check Health

```powershell
cd c:\Users\vyass\Documents\mifos-loan-summarizer\backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start the backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open your browser:
```
http://localhost:8000/health
```

You should see:
```json
{
  "status": "ok",
  "llm_provider": "ollama",
  "llm_model": "qwen2.5:7b",
  "provider_configured": true,
  "ollama_status": {
    "running": true,
    "base_url": "http://localhost:11434",
    "model": "qwen2.5:7b",
    "model_available": true,
    "available_models": ["qwen2.5:7b"]
  }
}
```

**What to check:**
- `"provider_configured": true` — app knows about Ollama
- `"ollama_status.running": true` — Ollama server is reachable
- `"ollama_status.model_available": true` — your model is downloaded

### Test 3: Check Providers List

```
http://localhost:8000/providers
```

Expected:
```json
[
  {"name": "hf_inference", "active": false},
  {"name": "ollama", "active": true},      ← Should be active
  {"name": "groq", "active": false},
  {"name": "cerebras", "active": false},
  {"name": "gemini", "active": false}
]
```

### Test 4: Quick Extraction Test

Use the Swagger docs at `http://localhost:8000/docs` or curl:

```bash
curl -X POST http://localhost:8000/analyse \
  -H "Content-Type: application/json" \
  -d '{
    "text": "LOAN AGREEMENT. Loan Amount: $50,000. Interest Rate: 8.5% per annum. Tenure: 36 months. Monthly EMI: $1,579. Late fee: $50 per instance.",
    "language": "en"
  }'
```

If you get a response with extracted entities and a summary, **everything is working!**

> **Note:** First request may take 30-60 seconds as Ollama loads the model into memory. Subsequent requests will be much faster (model stays in RAM).

---

## Step 5 — Run the App

### Option A: Run Locally (Development)

**Terminal 1 — Backend:**
```powershell
cd c:\Users\vyass\Documents\mifos-loan-summarizer\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```powershell
cd c:\Users\vyass\Documents\mifos-loan-summarizer\frontend
npm run dev
```

**Terminal 3 — (No action needed)**
Ollama runs as a background service on Windows. If it's not running:
```powershell
ollama serve
```

Open the app: **http://localhost:5173**

### Option B: Run with Docker

See the [Docker Setup section](#docker-setup-ollama-in-container) below.

---

## Model Selection Guide

### Which Model Should I Use?

```
                  ┌─────────────────────────────────┐
                  │   What's your hardware?         │
                  └──────────┬──────────────────────┘
                             │
              ┌──────────────┼──────────────────┐
              ▼              ▼                  ▼
        ≤ 8GB RAM      8-16GB RAM          16GB+ RAM
              │              │                  │
              ▼              ▼                  ▼
        llama3.2:1b    llama3.2:latest     qwen2.5:7b
        (1B params)    (3B params)         (7B params)
        ~60 tok/s      ~30 tok/s           ~15 tok/s
        ⭐⭐ Quality    ⭐⭐⭐ Quality       ⭐⭐⭐⭐ Quality
```

### Model Comparison for Loan Extraction

| Model | Download | RAM | Speed (CPU) | Extraction Quality | JSON Reliability | Hindi Support | Best For |
|-------|----------|-----|-------------|--------------------|--------------------|---------------|----------|
| `llama3.2:1b` | 1.3 GB | ~2 GB | ⚡⚡⚡⚡⚡ ~60 tok/s | ⭐⭐ Poor — misses many fields | ⭐⭐ Frequent parse errors | ⭐ Minimal | Quick smoke testing |
| `llama3.2:latest` | 2.0 GB | ~4 GB | ⚡⚡⚡⚡ ~30 tok/s | ⭐⭐⭐ Decent — gets core terms | ⭐⭐⭐ OK with JSON mode | ⭐⭐ Basic | Development, low-RAM |
| `phi3:mini` | 2.3 GB | ~4 GB | ⚡⚡⚡⚡ ~25 tok/s | ⭐⭐⭐ Decent — good reasoning | ⭐⭐⭐ OK | ⭐ English only | Structured tasks |
| `mistral:latest` | 4.1 GB | ~6 GB | ⚡⚡⚡ ~15 tok/s | ⭐⭐⭐ OK — misses nuance | ⭐⭐⭐ OK | ⭐⭐ Basic | General purpose |
| **`qwen2.5:7b`** | **4.7 GB** | **~8 GB** | **⚡⚡⚡ ~15 tok/s** | **⭐⭐⭐⭐ Good** | **⭐⭐⭐⭐⭐ Excellent** | **⭐⭐⭐ Good** | **🥇 Recommended** |
| `llama3.1:8b` | 4.7 GB | ~10 GB | ⚡⚡ ~12 tok/s | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐ Good | ⭐⭐⭐ Good | Production (CPU) |
| `gemma2:9b` | 5.4 GB | ~12 GB | ⚡⚡ ~10 tok/s | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐ Good | ⭐⭐ OK | Production (GPU) |
| `llama3.1:70b` | 40 GB | ~48 GB | ⚡ ~2 tok/s (CPU) | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very good | GPU only, best quality |

### Why `qwen2.5:7b` is Recommended

1. **Best JSON output** — Qwen 2.5 has excellent instruction following and produces clean, parseable JSON consistently. The app uses Ollama's `format: json` mode which pairs perfectly with Qwen's strengths.
2. **Balanced size** — 7B parameters is the sweet spot: enough intelligence for financial extraction, small enough for CPU inference.
3. **Multilingual** — Handles both English and Hindi well (important for Indian loan contracts).
4. **Fits in 8GB RAM** — Works on most modern laptops without a GPU.

---

## Docker Setup (Ollama in Container)

If you prefer running everything in Docker (no local Ollama install needed):

### Step 1: Uncomment Ollama in `docker-compose.yml`

Open `docker-compose.yml` and uncomment the Ollama service block:

```yaml
  ollama:
    image: ollama/ollama:latest
    container_name: mifos-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama    # Persist models across restarts
    environment:
      - OLLAMA_HOST=0.0.0.0          # Allow container connections
    networks:
      - mifos-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 30s
```

Also uncomment the volume at the bottom:
```yaml
volumes:
  ollama-data:
```

### Step 2: Update `.env` for Docker

```env
LLM_PRIMARY=ollama
OLLAMA_MODEL=qwen2.5:7b

# IMPORTANT: When backend runs in Docker, use Docker's internal DNS
# "host.docker.internal" lets the backend container reach Ollama on your host
# If Ollama is also in Docker, use the service name "ollama" instead
OLLAMA_BASE_URL=http://ollama:11434
```

> **Key networking detail:**
> - If Ollama runs **on your host** (installed directly): use `http://host.docker.internal:11434`
> - If Ollama runs **in Docker** (the service above): use `http://ollama:11434`

### Step 3: Start Everything

```bash
docker compose up -d
```

### Step 4: Pull the Model Inside the Container

```bash
# Pull model into the Ollama container
docker exec -it mifos-ollama ollama pull qwen2.5:7b

# Verify
docker exec -it mifos-ollama ollama list
```

### Step 5: Verify

```bash
# Check all services are running
docker compose ps

# Check health
curl http://localhost:8000/health
```

### Docker with GPU (NVIDIA)

Add GPU support to the Ollama service:

```yaml
  ollama:
    image: ollama/ollama:latest
    container_name: mifos-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    networks:
      - mifos-network
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

**Prerequisites:** Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

---

## GPU Acceleration Setup

GPU dramatically speeds up local inference (3-10× faster than CPU).

### NVIDIA GPU (CUDA)

#### Windows
1. Install latest NVIDIA GPU drivers from [nvidia.com/drivers](https://www.nvidia.com/Download/index.aspx)
2. Ollama automatically detects and uses NVIDIA GPUs on Windows — **no extra setup needed**
3. Verify GPU is being used:
```powershell
ollama run qwen2.5:7b "Hello"
# Check VRAM usage while it runs:
nvidia-smi
```

You should see `ollama_llama_server` in the GPU processes list.

#### Linux
1. Install NVIDIA drivers:
```bash
sudo apt install nvidia-driver-535    # or latest version
```

2. Install CUDA Toolkit:
```bash
sudo apt install nvidia-cuda-toolkit
```

3. Restart Ollama:
```bash
sudo systemctl restart ollama
```

4. Verify:
```bash
nvidia-smi
ollama run qwen2.5:7b "Hello"
```

### AMD GPU (ROCm) — Linux Only

```bash
# Install ROCm
sudo apt install rocm-hip-sdk

# Pull the ROCm-specific Ollama image (Docker)
docker run -d --device /dev/kfd --device /dev/dri \
  -v ollama-data:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama:rocm
```

### Apple Silicon (M1/M2/M3/M4) — macOS

Ollama automatically uses Apple's Metal GPU acceleration on Apple Silicon. **No extra setup needed.**

```bash
# Just install and run
ollama serve
ollama pull qwen2.5:7b
# Metal GPU is used automatically
```

### Verify GPU is Being Used

```bash
# While a model is running:

# NVIDIA:
nvidia-smi
# Look for ollama processes using GPU memory

# macOS (Apple Silicon):
# Activity Monitor → GPU History tab — look for spike when running queries

# Check Ollama logs:
# Windows: Check %LOCALAPPDATA%\Ollama\logs\server.log
# Linux: journalctl -u ollama
# Look for: "using CUDA" or "using Metal"
```

---

## Performance Tuning

### Tune Ollama for This App

#### 1. Increase Context Window

By default, Ollama uses a 2048-token context. Our loan contracts can be much larger. Increase it:

```bash
# Create a Modelfile with larger context
cat > Modelfile << 'EOF'
FROM qwen2.5:7b
PARAMETER num_ctx 8192
EOF

# Create a custom model
ollama create qwen2.5-loan:7b -f Modelfile

# Use this model in .env
# OLLAMA_MODEL=qwen2.5-loan:7b
```

Or on Windows (PowerShell):
```powershell
@"
FROM qwen2.5:7b
PARAMETER num_ctx 8192
"@ | Set-Content Modelfile

ollama create qwen2.5-loan:7b -f Modelfile
```

#### 2. Keep Model Loaded in Memory

Ollama unloads models after 5 minutes of inactivity by default. Keep it loaded:

```bash
# Set environment variable before starting Ollama
# Linux/macOS:
export OLLAMA_KEEP_ALIVE=-1    # Never unload

# Windows (PowerShell):
$env:OLLAMA_KEEP_ALIVE="-1"

# Or set as system environment variable
[System.Environment]::SetEnvironmentVariable('OLLAMA_KEEP_ALIVE', '-1', 'User')
```

Then restart Ollama.

#### 3. Optimize App Timeout Settings

In `.env`, tune the timeouts for local model speed:

```env
# For 7B models on CPU — give them plenty of time
PRIMARY_PROVIDER_TIMEOUT=180    # 3 minutes
MAX_INPUT_CHARS=50000           # Don't truncate contracts
EXTRACTION_MAX_TOKENS=16384     # Allow detailed extraction
SUMMARY_MAX_TOKENS=2048         # Allow detailed summaries
EXTRACTION_TEMPERATURE=0        # Deterministic output (most accurate)
```

#### 4. Concurrent Processing

Ollama can handle multiple parallel requests, but each one uses more RAM:

```bash
# Linux/macOS:
export OLLAMA_NUM_PARALLEL=2    # Allow 2 concurrent inferences

# Windows:
$env:OLLAMA_NUM_PARALLEL="2"
```

> **Warning:** Each parallel request loads a separate model instance. With a 7B model, 2 parallel = ~16GB RAM needed.

---

## Advanced Configuration

### Custom Model with System Prompt

Create a fine-tuned model specifically optimized for loan extraction:

```bash
cat > LoanModelfile << 'EOF'
FROM qwen2.5:7b

# Optimized parameters for financial document extraction
PARAMETER temperature 0
PARAMETER num_ctx 8192
PARAMETER num_predict 2048
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1

SYSTEM """You are a financial document extraction assistant. Your job is to 
extract structured data from loan agreements and contracts. Always output 
valid JSON. Never hallucinate or infer values not present in the document. 
Use null for missing fields. Extract exact amounts without currency symbols."""
EOF

ollama create loan-extractor:7b -f LoanModelfile
```

Then in `.env`:
```env
OLLAMA_MODEL=loan-extractor:7b
```

### Remote Ollama Server

Run Ollama on a more powerful machine and connect to it remotely:

**On the server (powerful machine):**
```bash
# Allow external connections
OLLAMA_HOST=0.0.0.0 ollama serve

# Or for systemd (Linux):
sudo systemctl edit ollama
# Add:
# [Service]
# Environment="OLLAMA_HOST=0.0.0.0"
sudo systemctl restart ollama
```

**On the client (app machine), in `.env`:**
```env
LLM_PRIMARY=ollama
OLLAMA_BASE_URL=http://192.168.1.100:11434    # Server's IP
OLLAMA_MODEL=qwen2.5:7b
```

> **Security:** If exposing Ollama over a network, use a reverse proxy (nginx) with authentication, or restrict access via firewall rules. Ollama has **no built-in authentication**.

### Multiple Models (A/B Testing)

You can test different models by switching `OLLAMA_MODEL` without restarting the app:

```bash
# Download multiple models
ollama pull llama3.2:latest
ollama pull qwen2.5:7b
ollama pull llama3.1:8b

# The app reads OLLAMA_MODEL on each request via the config,
# but the provider is cached. To switch models, restart the backend:

# In .env:
OLLAMA_MODEL=qwen2.5:7b    # Change this

# Restart backend:
# Ctrl+C the uvicorn process, then start it again
```

---

## Troubleshooting

### ❌ "Cannot connect to Ollama at http://localhost:11434"

**Cause:** Ollama server is not running.

**Fix (Windows):**
```powershell
# Check if Ollama service is running
Get-Service OllamaService

# If stopped, start it
Start-Service OllamaService

# Or start manually
ollama serve
```

**Fix (Linux):**
```bash
sudo systemctl status ollama
sudo systemctl start ollama
```

**Fix (macOS):**
```bash
ollama serve    # Start in terminal
```

---

### ❌ "Model 'xyz' not found locally"

**Cause:** The model specified in `OLLAMA_MODEL` hasn't been downloaded.

**Fix:**
```bash
# Check what's downloaded
ollama list

# Pull the missing model
ollama pull qwen2.5:7b

# Make sure .env matches exactly
# OLLAMA_MODEL=qwen2.5:7b  (match the name from 'ollama list')
```

**Note:** The app has **auto-pull logic** in `ollama_provider.py` — it will try to download the model automatically on startup. Check the backend logs for download progress.

---

### ❌ "Ollama generation timed out after 120s"

**Cause:** Model is too large for your hardware, or the contract is too long.

**Fix:**
```env
# Option 1: Increase timeout
PRIMARY_PROVIDER_TIMEOUT=300    # 5 minutes

# Option 2: Reduce contract size
MAX_INPUT_CHARS=8000            # Truncate large contracts

# Option 3: Use a smaller model
OLLAMA_MODEL=llama3.2:latest    # 3B instead of 7B

# Option 4: Use a cloud fallback for large contracts
LLM_FALLBACK=gemini
LLM_FALLBACK_MODEL=gemini-2.0-flash
GEMINI_API_KEY=your-key
FALLBACK_ON_TIMEOUT=true
```

---

### ❌ "Out of memory" / System becomes unresponsive

**Cause:** Model is too large for available RAM.

**Fix:**
```bash
# Check current memory usage
# Windows:
tasklist /FI "IMAGENAME eq ollama*" /FO TABLE

# Kill the Ollama process if system is unresponsive
# Windows:
taskkill /IM ollama.exe /F

# Switch to a smaller model:
ollama pull llama3.2:1b    # Only 1.3 GB
```

In `.env`:
```env
OLLAMA_MODEL=llama3.2:1b
```

---

### ❌ "Ollama JSON mode returned invalid JSON"

**Cause:** The model struggled to produce valid JSON despite the `format: json` setting.

This is handled automatically — the provider falls back to `generate_native()` and then `parse_llm_response()` tries to extract JSON from the raw text.

**To reduce occurrences:**
- Use `qwen2.5:7b` — best JSON output of any local model
- Reduce `EXTRACTION_TEMPERATURE` to 0
- Ensure `MAX_INPUT_CHARS` isn't truncating important contract sections

---

### ❌ Docker: Backend can't reach Ollama

**Cause:** Wrong URL in Docker networking.

**Fix:**

If Ollama runs **on your host** (installed directly, not in Docker):
```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

If Ollama runs **in Docker** (using the docker-compose service):
```env
OLLAMA_BASE_URL=http://ollama:11434
```

> `host.docker.internal` is a special DNS name that Docker Desktop resolves to your host machine's IP. On Linux without Docker Desktop, you may need `--add-host=host.docker.internal:host-gateway` or use the host's actual IP.

---

### ❌ GPU not being used (inference is slow)

**Check 1:** Is the GPU detected?
```bash
# NVIDIA
nvidia-smi
# Should show your GPU with driver version

# In Ollama logs (Windows):
# Check: %LOCALAPPDATA%\Ollama\logs\server.log
# Look for: "CUDA" or "GPU layers"
```

**Check 2:** Is the model using GPU layers?
```bash
ollama show qwen2.5:7b --modelfile
# Check num_gpu parameter
```

**Fix:** Force GPU usage:
```bash
cat > Modelfile << 'EOF'
FROM qwen2.5:7b
PARAMETER num_gpu 999    # Use all GPU layers
EOF
ollama create qwen2.5-gpu:7b -f Modelfile
```

---

## FAQ

### Q: Can I use Ollama and a cloud provider simultaneously?

**Yes!** That's exactly what the fallback system is designed for. Set Ollama as primary and Gemini/Groq as fallback:

```env
LLM_PRIMARY=ollama
OLLAMA_MODEL=qwen2.5:7b
LLM_FALLBACK=gemini
LLM_FALLBACK_MODEL=gemini-2.0-flash
GEMINI_API_KEY=your-key
PRIMARY_PROVIDER_TIMEOUT=120
FALLBACK_ON_TIMEOUT=true
```

The app tries Ollama first. If it times out after 120 seconds, it automatically switches to Gemini for that request.

---

### Q: How much disk space do I need?

Ollama base install: ~500 MB. Then each model adds to disk usage. Models are stored at:
- **Windows:** `C:\Users\<username>\.ollama\models\`
- **macOS:** `~/.ollama/models/`
- **Linux:** `/usr/share/ollama/.ollama/models/`

Common setups:
- 1 model (7B): ~5 GB total
- 3 models (1B + 3B + 7B): ~8 GB total
- 5 models (including 13B): ~25 GB total

---

### Q: Can I use a quantized model for faster inference?

**Yes!** Ollama models are already quantized (typically Q4_K_M — 4-bit quantization). You can request specific quantization levels:

```bash
# Default (Q4_K_M — best balance)
ollama pull qwen2.5:7b

# Smaller/faster (Q4_0 — slightly lower quality)
ollama pull qwen2.5:7b-q4_0

# Higher quality (Q8_0 — nearly full precision, needs more RAM)
ollama pull qwen2.5:7b-q8_0
```

---

### Q: Can I fine-tune a model specifically for loan extraction?

Ollama doesn't support fine-tuning directly. However, you can:

1. **Use a system prompt** (see [Custom Model with System Prompt](#custom-model-with-system-prompt) above)
2. **Use GGUF models from HuggingFace** — if someone fine-tunes a model for financial extraction and publishes a GGUF:

```bash
# Download a custom GGUF model
cat > Modelfile << 'EOF'
FROM ./path-to-custom-model.gguf
EOF
ollama create custom-loan-model -f Modelfile
```

---

### Q: Does Ollama work on a Raspberry Pi or ARM device?

**Yes!** Ollama supports ARM64. The 1B model (llama3.2:1b) runs on a Raspberry Pi 5 with 8GB RAM, though it will be slow (~5-10 tok/s). This could work for very simple microfinance contracts in remote deployments.

---

### Q: How do I update Ollama and models?

```bash
# Update Ollama itself
# Windows: Download latest installer from ollama.com/download
# Linux:
curl -fsSL https://ollama.com/install.sh | sh

# Update a model to the latest version
ollama pull qwen2.5:7b    # Re-pulling always gets the latest

# Remove old/unused models to free disk space
ollama rm mistral:latest
ollama rm llama3.2:1b
```

---

### Q: What's the difference between `LLM_MODEL` and `OLLAMA_MODEL`?

- `LLM_MODEL` — Used by cloud providers (Groq, Cerebras, HF). Example: `llama-3.1-8b-instant`
- `OLLAMA_MODEL` — Used exclusively by the Ollama provider. Example: `qwen2.5:7b`

When `LLM_PRIMARY=ollama`, the app reads from `OLLAMA_MODEL`, ignoring `LLM_MODEL`.

---

> **Need help?** Open an issue on the GitHub repository or check the [Ollama documentation](https://github.com/ollama/ollama/blob/main/docs/README.md).
