"""
Custom exception classes for the Mifos Loan Summarizer.

Using specific exceptions instead of generic Exception allows:
- Targeted error handling (e.g., returning 429 for rate limits)
- Better logging and monitoring
- Cleaner control flow
"""


class RateLimitError(Exception):
    """Raised when an LLM API rate limit is exceeded."""

    def __init__(self, provider: str, retry_after: int = 60):
        self.provider = provider
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded for {provider}. Retry after {retry_after}s.")


class ProviderError(Exception):
    """Raised when an LLM provider fails for non-rate-limit reasons."""

    def __init__(self, provider: str, detail: str):
        self.provider = provider
        self.detail = detail
        super().__init__(f"{provider}: {detail}")


class ContractTooLargeError(Exception):
    """Raised when contract text exceeds API size limits."""

    def __init__(self, size: int, max_size: int):
        self.size = size
        self.max_size = max_size
        super().__init__(f"Contract size ({size} chars) exceeds limit ({max_size} chars)")


class ExtractionError(Exception):
    """Raised when all LLM providers fail to extract data."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"All providers failed: {'; '.join(errors)}")
