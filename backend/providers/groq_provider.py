from openai import OpenAI
from backend.providers.base import LLMProvider
from backend.config import settings


class GroqProvider(LLMProvider):

    def __init__(self):
        self._model = 'llama-3.1-8b-instant'
        self._client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url='https://api.groq.com/openai/v1',
        )

    def get_model_name(self) -> str:
        return self._model

    def health_check(self) -> bool:
        return bool(settings.GROQ_API_KEY)

    @property
    def raw_client(self):
        return self._client