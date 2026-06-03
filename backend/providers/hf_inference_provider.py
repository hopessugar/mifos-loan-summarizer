from huggingface_hub import InferenceClient
from providers.base import LLMProvider
from config import settings


class HFInferenceProvider(LLMProvider):

    def __init__(self):
        self._model = settings.LLM_MODEL
        self._client = InferenceClient(
            api_key=settings.HF_TOKEN,
        )

    def get_model_name(self) -> str:
        return self._model

    def health_check(self) -> bool:
        try:
            return bool(settings.HF_TOKEN)
        except Exception:
            return False

    @property
    def raw_client(self):
        return self._client