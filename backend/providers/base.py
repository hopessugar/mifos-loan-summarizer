from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):

    @abstractmethod
    def get_model_name(self) -> str: ...

    @abstractmethod
    def health_check(self) -> bool: ...

    @property
    @abstractmethod
    def raw_client(self): ...


# Alias for backwards compatibility
LLMProvider = BaseLLMProvider