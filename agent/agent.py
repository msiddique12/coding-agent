from llm_providers.nvidia_nim import NIMProvider
from llm_providers.huggingface import HuggingFaceProvider

class CodingAgent:
    def __init__(self, provider_name="nim"):
        if provider_name == "nim":
            self.llm = NIMProvider()
        elif provider_name == "huggingface":
            self.llm = HuggingFaceProvider()
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

    def get_response(self, prompt: str) -> str:
        return self.llm.query(prompt)
