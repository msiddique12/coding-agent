from agent.orchestrator import Orchestrator


class StubAgent:
    def __init__(self):
        self.tools = {"shell_command": object()}
        self.unavailable_tools = {}
        self.calls = []

    def use_tool(self, tool_name, **kwargs):
        self.calls.append((tool_name, kwargs))
        return "ok"


def test_dangerous_tool_auto_approved(monkeypatch):
    agent = StubAgent()
    orchestrator = Orchestrator(agent, auto_approve=True)

    def fail_input(_prompt):
        raise AssertionError("input() should not be called when auto_approve=True")

    monkeypatch.setattr("builtins.input", fail_input)

    result = orchestrator._act({"tool": "shell_command", "args": {"command": "echo hi"}})

    assert result == "ok"
    assert agent.calls == [("shell_command", {"command": "echo hi"})]
