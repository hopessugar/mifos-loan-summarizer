from backend.providers.base import LLMProvider
from backend.config import settings


class GroqProvider(LLMProvider):

    def __init__(self):
        self._model = 'llama-3.1-8b-instant'
        self._client = None

    def get_model_name(self) -> str:
        return self._model

    def health_check(self) -> bool:
        return bool(settings.GROQ_API_KEY)

    @property
    def raw_client(self):
        if self._client is None:
            from langchain_groq import ChatGroq
            self._client = ChatGroq(
                model=self._model,
                api_key=settings.GROQ_API_KEY,
            )
        return self._client