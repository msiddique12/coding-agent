from llm_providers.nvidia_nim import NIMProvider
from llm_providers.huggingface import HuggingFaceProvider
import logging
import os

log_dir = "logs"
os.makedirs(log_dir, exist_ok = True)
logging.basicConfig(
    filename=os.path.join(log_dir, "agent.log"),
    filemode="a",
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO
)

class CodingAgent:
    def __init__(self, provider_name="nim"):
        if provider_name == "nim":
            self.llm = NIMProvider()
        elif provider_name == "huggingface":
            self.llm = HuggingFaceProvider()
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

    def get_response(self, prompt: str) -> str:
        logging.info(f"Provider: {type(self.llm).__name__}, Prompt: {prompt!r}")
        response = self.llm.query(prompt)
        logging.info(f"Response: {response!r}")
        return response
