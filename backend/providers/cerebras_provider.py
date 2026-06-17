import httpx
from openai import OpenAI
from providers.base import LLMProvider
from config import settings
import os


class CerebrasProvider(LLMProvider):
    """Cerebras LLM provider with fast inference"""

    def __init__(self):
        # Use fallback model from settings
        self._model = settings.LLM_FALLBACK_MODEL or 'llama3.1-8b'
        
        # ⚠️ SECURITY: Only disable SSL in development
        environment = os.getenv('ENVIRONMENT', 'development').lower()
        verify_ssl = environment != 'development'
        
        if not verify_ssl:
            print('⚠️  WARNING: SSL verification disabled for Cerebras (development only)')
        
        self._client = OpenAI(
            api_key=settings.CEREBRAS_API_KEY,
            base_url='https://api.cerebras.ai/v1',
            http_client=httpx.Client(verify=verify_ssl) if not verify_ssl else None,
        )

    def get_model_name(self) -> str:
        return self._model

    def health_check(self) -> bool:
        return bool(settings.CEREBRAS_API_KEY)

    @property
    def raw_client(self):
        return self._client