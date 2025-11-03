import os
from .nvidia_nim import NIMProvider


def get_llm_client(provider_name: str | None = None):
	"""Return a simple LLM client instance. Default provider is 'nim'.

	This is intentionally minimal. Will be extended later when more providers are added
	"""
	name = provider_name or os.getenv("LLM_PROVIDER", "nim")
	if name == "nim":
		return NIMProvider()
	raise ValueError(f"Unsupported provider: {name}")


__all__ = ["get_llm_client"]
