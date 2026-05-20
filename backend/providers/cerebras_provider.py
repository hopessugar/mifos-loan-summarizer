from backend.providers.base import LLMProvider
from backend.config import settings


class CerebrasProvider(LLMProvider):

    def __init__(self):
        self._model = 'llama-3.1-8b'
        self._client = None

    def get_model_name(self) -> str:
        return self._model

    def health_check(self) -> bool:
        return bool(settings.CEREBRAS_API_KEY)

    @property
    def raw_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=settings.CEREBRAS_API_KEY,
                base_url='https://api.cerebras.ai/v1',
            )
        return self._client