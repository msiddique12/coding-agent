import sys
import os
import pytest

# This module is a script-style smoke test for manual runs. Skip under pytest
pytest.skip("Script-style LLM smoke test; run as script", allow_module_level=True)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv; load_dotenv()
from agent.agent import CodingAgent

def test_provider(provider, prompt="Hello, world!"):
    print(f"Testing Provider: {provider}")
    agent = CodingAgent(provider_name=provider)
    response = agent.get_response(prompt)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}\n{'-'*40}")
    assert response and "error" not in response.lower()

if __name__ == "__main__":
    for provider in ["nim"]: #add others later
        try:
            test_provider(provider)
        except Exception as e:
            print(f"Test failed for {provider}: {e}")
