import httpx
import json
from openai import OpenAI
from providers.base import LLMProvider
from config import settings


class OllamaProvider(LLMProvider):

    def __init__(self):
        self._model = settings.OLLAMA_MODEL
        self._base_url = settings.OLLAMA_BASE_URL
        
        self._client = OpenAI(
            api_key='ollama',
            base_url=f'{self._base_url}/v1',
            timeout=120.0,
        )

    def get_model_name(self) -> str:
        return self._model

    def health_check(self) -> bool:
        try:
            r = httpx.get(f'{self._base_url}/api/tags', timeout=3.0)
            return r.status_code == 200
        except Exception:
            return False

    @property
    def raw_client(self):
        return self._client
    
    def generate_native(self, prompt: str, system: str = "", max_tokens: int = 2000, temperature: float = 0.1) -> str:
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
                    raise Exception(f"Ollama API error: {response.status_code}")
                
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        full_response += chunk
                        
                        if data.get("done", False):
                            break
            
            return full_response
            
        except httpx.TimeoutException:
            raise Exception("Ollama generation timed out after 120 seconds")
        except Exception as e:
            raise Exception(f"Ollama native API error: {e}")