import httpx
from openai import OpenAI
from providers.base import LLMProvider
from config import settings


class CerebrasProvider(LLMProvider):

    def __init__(self):
        self._model = 'gpt-oss-120b'
        self._client = OpenAI(
            api_key=settings.CEREBRAS_API_KEY,
            base_url='https://api.cerebras.ai/v1',
            http_client=httpx.Client(verify=False),
        )

    def get_model_name(self) -> str:
        return self._model

    def health_check(self) -> bool:
        return bool(settings.CEREBRAS_API_KEY)

    @property
    def raw_client(self):
        return self._client