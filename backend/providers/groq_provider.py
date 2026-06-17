from openai import OpenAI
from providers.base import LLMProvider
from config import settings


class GroqProvider(LLMProvider):
    """Groq LLM provider with ultra-fast inference"""

    def __init__(self):
        # Use model from settings instead of hardcoded value
        self._model = settings.LLM_MODEL
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