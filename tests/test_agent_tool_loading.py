from agent.agent import CodingAgent


def test_agent_skips_unavailable_optional_tool(monkeypatch):
    def broken_code_search():
        raise RuntimeError("rg missing")

    monkeypatch.setattr("agent.agent.CodeSearchTool", broken_code_search)

    agent = CodingAgent(provider_name="dummy")

    assert "code_search" in agent.unavailable_tools
    assert "rg missing" in agent.unavailable_tools["code_search"]
    assert "file_search" in agent.tools
