from pydantic_settings import BaseSettings
import yaml
import os


def _load_yaml() -> dict:
    path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    if os.path.exists(path):
        with open(path) as f:
            return yaml.safe_load(f) or {}
    return {}


_yaml = _load_yaml()


class Settings(BaseSettings):
    # LLM
    LLM_PRIMARY: str = _yaml.get('llm', {}).get('primary', 'hf_inference')
    LLM_MODEL: str = _yaml.get('llm', {}).get('model', 'Qwen/Qwen2.5-72B-Instruct')
    LLM_FALLBACK: str = _yaml.get('llm', {}).get('fallback', 'hf_inference')
    LLM_FALLBACK_MODEL: str = _yaml.get('llm', {}).get('fallback_model', 'meta-llama/Llama-3.1-8B-Instruct')

    # HuggingFace
    HF_TOKEN: str = _yaml.get('hf_token', '')

    # Ollama
    OLLAMA_BASE_URL: str = _yaml.get('ollama_base_url', 'http://localhost:11434')
    OLLAMA_MODEL: str = _yaml.get('ollama_model', 'qwen2.5:7b')

    # Fineract
    FINERACT_URL: str = _yaml.get('fineract_url', '')
    FINERACT_USER: str = _yaml.get('fineract_user', 'mifos')
    FINERACT_PASSWORD: str = _yaml.get('fineract_password', 'password')
    FINERACT_TENANT: str = _yaml.get('fineract_tenant', 'default')

    # Cloud free-tier providers
    GROQ_API_KEY: str = _yaml.get('groq_api_key', '')
    CEREBRAS_API_KEY: str = _yaml.get('cerebras_api_key', '')

    # Validation thresholds
    LEVENSHTEIN_THRESHOLD: float = _yaml.get('levenshtein_threshold', 0.80)
    COSINE_THRESHOLD: float = _yaml.get('cosine_threshold', 0.80)
    MATH_TOLERANCE: float = _yaml.get('math_tolerance', 0.10)
    CONFIDENCE_THRESHOLD: float = _yaml.get('confidence_threshold', 0.50)

    # Pipeline
    USE_SEMANTIC_CHUNKING: bool = _yaml.get('use_semantic_chunking', False)
    MAX_SEGMENT_TOKENS: int = _yaml.get('max_segment_tokens', 200)
    EXTRACTION_MAX_TOKENS: int = _yaml.get('extraction_max_tokens', 2000)
    SUMMARY_MAX_TOKENS: int = _yaml.get('summary_max_tokens', 500)
    EXTRACTION_TEMPERATURE: float = _yaml.get('extraction_temperature', 0.1)

    class Config:
        extra = 'ignore'


settings = Settings()
