import os
import tempfile

from llm_providers import get_llm_client
from agent.agent import CodingAgent
from tools.code_edit import CodeEditTool


def test_dummy_provider_echo():
    client = get_llm_client("dummy")
    resp = client.query("hello world")
    assert resp.startswith("[DUMMY]")
    assert "hello world" in resp


def test_agent_with_dummy_provider():
    agent = CodingAgent(provider_name="dummy")
    resp = agent.get_response("ping")
    assert resp.startswith("[DUMMY]")
    assert "ping" in resp


def test_code_edit_tool_with_dummy_provider(tmp_path, monkeypatch):
    # ensure get_llm_client() picks up dummy by default
    monkeypatch.setenv("LLM_PROVIDER", "dummy")

    src = tmp_path / "sample.txt"
    src.write_text("original content\n")

    tool = CodeEditTool()
    out = tool.run(str(src), "make a trivial edit")
    # Dummy provider echoes the prompt; ensure we got a dummy response
    assert isinstance(out, str)
    assert out.startswith("[DUMMY]")
