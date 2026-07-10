import httpx
import json
import logging
from openai import OpenAI
from providers.base import LLMProvider
from config import settings

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Ollama LLM provider for local model inference.
    
    This provider connects to a running Ollama instance and supports:
    - OpenAI-compatible API via raw_client (for instructor/langchain)
    - Native Ollama API for text generation (generate_native)
    - Native Ollama JSON mode for structured output (generate_json)
    - Auto-pull of models if not already downloaded
    - Health checks with detailed status info
    
    Setup:
        1. Install Ollama: https://ollama.com/download
        2. Start Ollama: `ollama serve`
        3. Set in .env: LLM_PRIMARY=ollama, OLLAMA_MODEL=llama3.2:latest
    """

    def __init__(self):
        self._model = settings.OLLAMA_MODEL
        self._base_url = settings.OLLAMA_BASE_URL
        
        # OpenAI-compatible client for instructor/langchain compatibility
        self._client = OpenAI(
            api_key='ollama',  # Ollama doesn't need a real API key
            base_url=f'{self._base_url}/v1',
            timeout=120.0,
        )
        
        # Auto-pull model if Ollama is reachable but model isn't downloaded
        self._ensure_model_available()

    def _ensure_model_available(self):
        """Check if the configured model is available, auto-pull if not."""
        try:
            available_models = self._list_model_names()
            
            # Normalize model name for comparison (e.g. "llama3.2:latest" matches "llama3.2")
            model_base = self._model.split(':')[0]
            
            is_available = any(
                model_base in m or self._model in m
                for m in available_models
            )
            
            if is_available:
                logger.info(f"✅ Ollama model '{self._model}' is available")
            else:
                logger.warning(
                    f"⚠️  Ollama model '{self._model}' not found locally. "
                    f"Available models: {available_models or 'none'}. "
                    f"Attempting auto-pull..."
                )
                self._pull_model()
                
        except httpx.ConnectError:
            logger.warning(
                f"⚠️  Cannot connect to Ollama at {self._base_url}. "
                f"Model availability check skipped. "
                f"Make sure Ollama is running: 'ollama serve'"
            )
        except Exception as e:
            logger.warning(f"⚠️  Model availability check failed: {e}")

    def _pull_model(self):
        """Pull/download a model from the Ollama registry."""
        try:
            logger.info(f"📥 Pulling Ollama model '{self._model}'... (this may take several minutes)")
            
            # Use streaming pull to show progress
            with httpx.stream(
                "POST",
                f'{self._base_url}/api/pull',
                json={"model": self._model},
                timeout=600.0,  # 10 min timeout for large models
            ) as response:
                if response.status_code != 200:
                    logger.error(f"Failed to pull model: HTTP {response.status_code}")
                    return
                
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        status = data.get("status", "")
                        if "pulling" in status or "downloading" in status:
                            completed = data.get("completed", 0)
                            total = data.get("total", 0)
                            if total > 0:
                                pct = (completed / total) * 100
                                logger.info(f"  📥 {status}: {pct:.0f}%")
                        elif "success" in status:
                            logger.info(f"✅ Model '{self._model}' pulled successfully!")
                            
        except httpx.TimeoutException:
            logger.error(
                f"❌ Model pull timed out. Please pull manually: ollama pull {self._model}"
            )
        except Exception as e:
            logger.error(f"❌ Model pull failed: {e}. Please pull manually: ollama pull {self._model}")

    def _list_model_names(self) -> list[str]:
        """Get list of model names from Ollama."""
        r = httpx.get(f'{self._base_url}/api/tags', timeout=5.0)
        if r.status_code == 200:
            data = r.json()
            return [m.get('name', '') for m in data.get('models', [])]
        return []

    def get_model_name(self) -> str:
        return self._model

    @property
    def supports_instructor(self) -> bool:
        """Ollama doesn't reliably support instructor — use generate_native/generate_json instead."""
        return False

    def health_check(self) -> bool:
        """Check if Ollama is running and reachable."""
        try:
            r = httpx.get(f'{self._base_url}/api/tags', timeout=5.0)
            return r.status_code == 200
        except Exception:
            return False

    def health_check_detailed(self) -> dict:
        """Return detailed health status for the /health endpoint."""
        result = {
            "running": False,
            "base_url": self._base_url,
            "model": self._model,
            "model_available": False,
            "available_models": [],
        }
        
        try:
            r = httpx.get(f'{self._base_url}/api/tags', timeout=5.0)
            if r.status_code == 200:
                result["running"] = True
                data = r.json()
                models = [m.get('name', '') for m in data.get('models', [])]
                result["available_models"] = models
                
                model_base = self._model.split(':')[0]
                result["model_available"] = any(
                    model_base in m or self._model in m
                    for m in models
                )
        except httpx.ConnectError:
            result["error"] = (
                f"Cannot connect to Ollama at {self._base_url}. "
                "Is Ollama running? Start it with: ollama serve"
            )
        except Exception as e:
            result["error"] = str(e)
        
        return result

    @property
    def raw_client(self):
        """Return OpenAI-compatible client for langchain/instructor."""
        return self._client

    def list_models(self) -> list[dict]:
        """List all models available in this Ollama instance."""
        try:
            r = httpx.get(f'{self._base_url}/api/tags', timeout=5.0)
            if r.status_code == 200:
                return r.json().get('models', [])
            return []
        except Exception:
            return []
    
    def generate_native(self, prompt: str, system: str = "", max_tokens: int = 2000, temperature: float = 0.0) -> str:
        """Generate text using Ollama's native /api/generate endpoint.
        
        Uses streaming to handle long responses. This method is blocking
        and should be called from asyncio.to_thread().
        """
        url = f'{self._base_url}/api/generate'
        
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        payload = {
            "model": self._model,
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        try:
            full_response = ""
            
            with httpx.stream("POST", url, json=payload, timeout=120.0) as response:
                if response.status_code != 200:
                    error_body = ""
                    try:
                        error_body = response.read().decode()
                    except Exception:
                        pass
                    raise Exception(
                        f"Ollama API error (HTTP {response.status_code}): {error_body}. "
                        f"Model: {self._model}, URL: {url}"
                    )
                
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        full_response += chunk
                        
                        if data.get("done", False):
                            break
            
            return full_response
            
        except httpx.ConnectError:
            raise Exception(
                f"Cannot connect to Ollama at {self._base_url}. "
                f"Please ensure Ollama is running:\n"
                f"  1. Install: https://ollama.com/download\n"
                f"  2. Start: ollama serve\n"
                f"  3. Pull model: ollama pull {self._model}"
            )
        except httpx.TimeoutException:
            raise Exception(
                f"Ollama generation timed out after 120s. "
                f"The model '{self._model}' may be too large for your hardware. "
                f"Try a smaller model like 'llama3.2:1b' or 'phi3:mini'."
            )
        except Exception as e:
            if "ConnectError" in str(type(e).__name__):
                raise Exception(
                    f"Cannot connect to Ollama at {self._base_url}. "
                    f"Is Ollama running? Start with: ollama serve"
                )
            raise

    def generate_json(self, prompt: str, system: str = "", max_tokens: int = 2000, temperature: float = 0.0) -> str:
        """Generate structured JSON output using Ollama's native JSON format mode.
        
        Uses the 'format: json' parameter in Ollama's /api/generate endpoint,
        which constrains the model to output valid JSON. This significantly
        reduces JSON parse failures during extraction.
        
        This method is blocking and should be called from asyncio.to_thread().
        """
        url = f'{self._base_url}/api/generate'
        
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        payload = {
            "model": self._model,
            "prompt": full_prompt,
            "format": "json",  # Force JSON output
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        try:
            full_response = ""
            
            with httpx.stream("POST", url, json=payload, timeout=120.0) as response:
                if response.status_code != 200:
                    error_body = ""
                    try:
                        error_body = response.read().decode()
                    except Exception:
                        pass
                    raise Exception(
                        f"Ollama JSON mode error (HTTP {response.status_code}): {error_body}. "
                        f"Model: {self._model}"
                    )
                
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        full_response += chunk
                        
                        if data.get("done", False):
                            break
            
            # Validate that the response is actually valid JSON
            try:
                json.loads(full_response)
            except json.JSONDecodeError:
                logger.warning(
                    f"Ollama JSON mode returned invalid JSON. "
                    f"Falling back to generate_native(). Response preview: {full_response[:200]}"
                )
                return self.generate_native(prompt, system, max_tokens, temperature)
            
            return full_response
            
        except httpx.ConnectError:
            raise Exception(
                f"Cannot connect to Ollama at {self._base_url}. "
                f"Please ensure Ollama is running: ollama serve"
            )
        except httpx.TimeoutException:
            raise Exception(
                f"Ollama JSON generation timed out after 120s. "
                f"Try a smaller model like 'llama3.2:1b' or 'phi3:mini'."
            )
        except Exception as e:
            if "ConnectError" in str(type(e).__name__):
                raise Exception(
                    f"Cannot connect to Ollama at {self._base_url}. "
                    f"Is Ollama running? Start with: ollama serve"
                )
            raise