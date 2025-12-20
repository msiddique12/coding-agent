from agent.agent import CodingAgent

class Orchestrator:
    def __init__(self, agent: CodingAgent):
        self.agent = agent

    def run(self, goal: str):
        """
        For now, this is a simple pass-through to the agent.
        We will build more complex planning and execution logic here later.
        """
        print(f"Orchestrator received goal: {goal}")
        return self.agent.get_response(goal)
