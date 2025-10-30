from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def query(self, prompt: str) -> str:
        """Send a prompt to the LLM and return the response."""
        pass
