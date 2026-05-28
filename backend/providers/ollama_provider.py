from openai import OpenAI
from backend.providers.base import LLMProvider
from backend.config import settings


class OllamaProvider(LLMProvider):

    def __init__(self):
        self._model = settings.OLLAMA_MODEL
        self._client = OpenAI(
            api_key='ollama',
            base_url=f'{settings.OLLAMA_BASE_URL}/v1',
        )

    def get_model_name(self) -> str:
        return self._model

    def health_check(self) -> bool:
        try:
            import httpx
            r = httpx.get(f'{settings.OLLAMA_BASE_URL}/api/tags', timeout=3.0)
            return r.status_code == 200
        except Exception:
            return False

    @property
    def raw_client(self):
        return self._client