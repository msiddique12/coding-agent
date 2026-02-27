import os
import requests
from llm_providers.base import LLMProvider

class HuggingFaceProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        model = os.getenv("HUGGINGFACE_MODEL")
        if not model:
            raise ValueError(
                "HUGGINGFACE_MODEL environment variable is required. "
                "Set it to the HuggingFace model ID, e.g. 'mistralai/Mixtral-8x7B-Instruct-v0.1'."
            )
        self.endpoint = f"https://api-inference.huggingface.co/models/{model}"

    def query(self, prompt: str) -> str:
        if not self.api_key:
            return "Error: Hugging Face API key not found in environment."

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": prompt}
        try:
            resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            output = resp.json()
            # Custom parsing may be needed depending on model, this is generic
            if isinstance(output, dict) and "error" in output:
                return output["error"]
            return str(output)
        except Exception as e:
            return f"Hugging Face API error: {e}"
