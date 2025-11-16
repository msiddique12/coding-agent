import os
from .nvidia_nim import NIMProvider
from .huggingface import HuggingFaceProvider
from .dummy import DummyProvider


def get_llm_client(provider_name: str | None = None):
	"""Return a simple LLM client instance. Default provider is 'nim'.

	Supports: 'nim', 'huggingface', and 'dummy' (for tests).
	"""
	name = provider_name or os.getenv("LLM_PROVIDER", "nim")
	if name == "nim":
		return NIMProvider()
	if name == "huggingface":
		return HuggingFaceProvider()
	if name == "dummy":
		return DummyProvider()
	raise ValueError(f"Unsupported provider: {name}")


__all__ = ["get_llm_client"]
