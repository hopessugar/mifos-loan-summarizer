from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Abstract base for all LLM providers.
    
    Every provider must implement:
    - get_model_name(): Return the model identifier string
    - health_check(): Return True if the provider is reachable
    - raw_client: Return the underlying SDK client (for instructor/OpenAI-compat)
    
    Optionally:
    - generate_native(): Direct text generation (for non-OpenAI providers like Gemini)
    - supports_instructor: Whether this provider works with instructor library
    """

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model identifier (e.g. 'gemini-2.5-flash-lite')."""
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the provider API is configured and reachable."""
        ...

    @property
    @abstractmethod
    def raw_client(self):
        """Return the underlying SDK client for direct API calls."""
        ...

    @property
    def supports_instructor(self) -> bool:
        """Whether this provider supports the instructor library for structured output.
        Override and return False for providers that use generate_native() instead.
        """
        return True

    def generate_native(self, prompt: str, system: str = None, max_tokens: int = 1000, temperature: float = 0.1) -> str:
        """Generate text using the provider's native API.
        
        This is the fallback for providers that don't support OpenAI-compatible APIs.
        Must be called from asyncio.to_thread() to avoid blocking the event loop.
        
        Raises:
            NotImplementedError: If the provider doesn't support native generation
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support native generation")


# Alias for backwards compatibility
LLMProvider = BaseLLMProvider