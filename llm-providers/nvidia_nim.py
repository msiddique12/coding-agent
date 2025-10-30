import os
import requests
from llm_providers.base import LLMProvider

class NIMProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("NIM_API_KEY")
        self.endpoint = "https://api.nim.nvidia.com/v1/chat/completions"
        self.model = "Model-Name"  #later: add model name

    def query(self, prompt: str) -> str:
        if not self.api_key:
            return "Error: NIM API key not found in environment."

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"NIM API error: {e}"
