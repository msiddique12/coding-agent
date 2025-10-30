import os
import requests
from llm_providers.base import LLMProvider
from openai import OpenAI


class NIMProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("NIM_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.endpoint = "https://api.nim.nvidia.com/v1/chat/completions"
        self.model = "qwen/qwen2.5-coder-32b-instruct"
        
        if not self.api_key:
            raise ValueError("NIM_API_KEY not found")
        
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    def query(self, prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature = 0.2,
                top_p = 0.7,
                max_tokens = 1024,
                stream = False   
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"NIM (OpenAI SDK) error: {e}"
        