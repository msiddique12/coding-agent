from llm_providers.nvidia_nim import NIMProvider
from llm_providers.huggingface import HuggingFaceProvider
from utils.filesystem import list_code_files, read_file
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

    def list_files(self):
        return list_code_files()
    
    def summarize_readme(self):
        if not os.path.exists("README.md"):
            return "No README.md found in the current directory."
        content = read_file("README.md")
        prompt = f"Summarize the following README.md for quick project understanding:\n\n{content}"
        return self.get_response(prompt)
    
    def summarize_file(self, fp):
        if not os.path.exists(fp):
            return f"File {fp} does not exist!"
        content = read_file(fp)
        prompt = f"Summarize this file with a focus on key purpose and usage:\n\n{content}"
        return self.get_response(prompt)
        
        