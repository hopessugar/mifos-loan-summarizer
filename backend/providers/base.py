from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    def get_model_name(self) -> str: ...

    @abstractmethod
    def health_check(self) -> bool: ...

    @property
    @abstractmethod
    def raw_client(self): ...