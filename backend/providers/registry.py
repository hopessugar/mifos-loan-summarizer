from providers.base import LLMProvider
from config import settings


_PROVIDERS = {
    'hf_inference': lambda: _import_hf(),
    'ollama': lambda: _import_ollama(),
    'groq': lambda: _import_groq(),
    'cerebras': lambda: _import_cerebras(),
    'gemini': lambda: _import_gemini(),
}


def _import_hf():
    from providers.hf_inference_provider import HFInferenceProvider
    return HFInferenceProvider()


def _import_ollama():
    from providers.ollama_provider import OllamaProvider
    return OllamaProvider()


def _import_groq():
    from providers.groq_provider import GroqProvider
    return GroqProvider()


def _import_cerebras():
    from providers.cerebras_provider import CerebrasProvider
    return CerebrasProvider()


def _import_gemini():
    from providers.gemini_provider import GeminiProvider
    return GeminiProvider()


class ProviderRegistry:

    @staticmethod
    def get(override: str | None = None) -> LLMProvider:
        name = override or settings.LLM_PRIMARY
        if name not in _PROVIDERS:
            raise ValueError(f'Unknown provider: {name}. Choose from: {list(_PROVIDERS.keys())}')
        return _PROVIDERS[name]()

    @staticmethod
    def list_all() -> list[dict]:
        return [
            {
                'name': name,
                'active': name == settings.LLM_PRIMARY,
            }
            for name in _PROVIDERS
        ]