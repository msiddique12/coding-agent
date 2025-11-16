from llm_providers.base import LLMProvider
import os


class DummyProvider(LLMProvider):
    """A tiny local provider for tests and local development.

    Behavior modes (controlled by env var DUMMY_MODE or constructor):
    - echo (default): returns "[DUMMY] " + prompt
    - fixed: returns a constant string from DUMMY_FIXED_RESPONSE or constructor
    - error: raises an exception to simulate provider failures
    """

    def __init__(self, mode: str | None = None, fixed_response: str | None = None):
        self.mode = mode or os.getenv("DUMMY_MODE", "echo")
        self.fixed_response = fixed_response or os.getenv("DUMMY_FIXED_RESPONSE")

    def query(self, prompt: str) -> str:
        if self.mode == "error":
            raise RuntimeError("Dummy provider simulated error")
        if self.mode == "fixed" and self.fixed_response is not None:
            return self.fixed_response
        # default: echo the prompt with a small marker
        return f"[DUMMY] {prompt}"
