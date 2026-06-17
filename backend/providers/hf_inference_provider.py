from openai import OpenAI
from providers.base import LLMProvider
from config import settings


class HFInferenceProvider(LLMProvider):
    """HuggingFace Inference provider using OpenAI-compatible API"""

    def __init__(self):
        self._model = settings.LLM_FALLBACK_MODEL or "meta-llama/Llama-3.2-3B-Instruct"
        # Use OpenAI-compatible client for HF Inference
        self._client = OpenAI(
            base_url="https://api-inference.huggingface.co/v1/",
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