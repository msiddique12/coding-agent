from agent.agent import CodingAgent
import re

class Orchestrator:
    def __init__(self, agent: CodingAgent):
        self.agent = agent

    def _create_plan(self, goal: str):
        """
        For now, this returns a hardcoded plan for testing.
        Later, this will call the LLM to generate a dynamic plan.
        """
        print("Orchestrator: Creating a plan...")
        
        # Hardcoded plan for demonstration purposes
        plan = [
            {"tool": "list_files", "args": {}}
        ]
        return plan

    def _execute_plan(self, plan: list):
        """
        For now, this is a placeholder for plan execution logic.
        """
        print(f"Orchestrator: Executing plan: {plan}")
        # Placeholder for execution logic
        return "Plan execution not implemented yet."

    def run(self, goal: str):
        """
        Creates and executes a plan based on the user's goal.
        """
        print(f"Orchestrator received goal: {goal}")
        
        plan = self._create_plan(goal)
        result = self._execute_plan(plan)
        
        return result
