import os
from .nvidia_nim import NIMProvider
from .openai_provider import OpenAIProvider
from .huggingface import HuggingFaceProvider
from .dummy import DummyProvider

PROVIDER_SPECS = {
    "openai": {
        "env_vars": ["OPENAI_API_KEY"],
        "description": "OpenAI chat completions API",
    },
    "nim": {
        "env_vars": ["NIM_API_KEY"],
        "description": "NVIDIA NIM OpenAI-compatible API",
    },
    "huggingface": {
        "env_vars": ["HUGGINGFACE_API_KEY"],
        "description": "Hugging Face Inference API",
    },
    "dummy": {
        "env_vars": [],
        "description": "Local dummy provider for tests/development",
    },
}


def supported_provider_names() -> list[str]:
    return list(PROVIDER_SPECS.keys())


def validate_provider_environment(provider_name: str | None = None) -> dict:
    name = provider_name or os.getenv("LLM_PROVIDER", "nim")
    if name not in PROVIDER_SPECS:
        return {
            "provider": name,
            "supported": False,
            "missing_env": [],
            "ok": False,
            "message": f"Unsupported provider: {name}",
        }

    required = PROVIDER_SPECS[name]["env_vars"]
    missing = [var for var in required if not os.getenv(var)]
    return {
        "provider": name,
        "supported": True,
        "missing_env": missing,
        "ok": len(missing) == 0,
        "message": "OK" if not missing else f"Missing environment variables: {', '.join(missing)}",
    }


def get_llm_client(provider_name: str | None = None):
    """Return a simple LLM client instance. Default provider is 'nim'."""
    name = provider_name or os.getenv("LLM_PROVIDER", "nim")
    if name == "openai":
        return OpenAIProvider()
    if name == "nim":
        return NIMProvider()
    if name == "huggingface":
        return HuggingFaceProvider()
    if name == "dummy":
        return DummyProvider()

    supported = ", ".join(supported_provider_names())
    raise ValueError(f"Unsupported provider: {name}. Supported providers: {supported}")


__all__ = [
    "get_llm_client",
    "supported_provider_names",
    "validate_provider_environment",
]
