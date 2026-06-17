"""
Google Gemini provider for loan agreement extraction.
Uses the new Google GenAI SDK (google-genai).
"""
import time
import re
import logging

from providers.base import BaseLLMProvider
from config import settings
from exceptions import RateLimitError

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Provider for Google Gemini models using the new google-genai SDK."""

    def __init__(self):
        from google import genai

        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set. Please set it in .env or environment variables.")

        self._client = genai.Client(api_key=api_key)

        model_name = settings.LLM_MODEL if 'gemini' in settings.LLM_MODEL.lower() else 'gemini-2.0-flash'
        self._model_name = model_name
        self._is_gemini = True  # Flag to skip instructor

    def get_model_name(self) -> str:
        return self._model_name

    @property
    def raw_client(self):
        """Return the genai Client for direct usage."""
        return self._client

    @property
    def supports_instructor(self) -> bool:
        return False

    def health_check(self) -> bool:
        """Check if the Gemini API key is configured (no API call to save quota)."""
        return bool(settings.GEMINI_API_KEY)

    def generate_native(self, prompt: str, system: str = None, max_tokens: int = 1000, temperature: float = 0.1) -> str:
        """Generate text using Gemini's native API with automatic retry on rate limits.
        
        THREADING NOTE: This method uses time.sleep() for retry backoff.
        It MUST be called from asyncio.to_thread() or a background thread
        to avoid blocking the uvicorn event loop.
        """
        full_prompt = f"{system}\n\n{prompt}" if system else prompt

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self._client.models.generate_content(
                    model=self._model_name,
                    contents=full_prompt,
                    config={
                        "max_output_tokens": max_tokens,
                        "temperature": temperature,
                    }
                )
                return response.text

            except Exception as e:
                error_str = str(e)
                if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                    delay_match = re.search(r'retry in (\d+)', error_str, re.IGNORECASE)
                    wait_time = int(delay_match.group(1)) + 2 if delay_match else (30 * (attempt + 1))
                    logger.warning(f"Rate limited (attempt {attempt+1}/{max_retries}). Waiting {wait_time}s...")
                    time.sleep(wait_time)  # OK — always called from thread context
                    continue
                else:
                    raise

        raise RateLimitError(provider=self._model_name, retry_after=60)

