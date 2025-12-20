from agent.agent import CodingAgent
import re

class Orchestrator:
    def __init__(self, agent: CodingAgent):
        self.agent = agent

    def run(self, goal: str):
        """
        Executes a plan based on the user's goal.
        """
        print(f"Orchestrator received goal: {goal}")

        if goal == "find and fix a todo":
            print("Orchestrator: Starting 'find and fix a todo' plan...")
            
            # 1. Find a TODO
            todo_result = self.agent.use_tool("todo_finder")
            
            if "No TODOs found." in todo_result:
                return "Orchestrator: No TODOs found to fix."
            
            print(f"Orchestrator: Found TODOs:\n{todo_result}")

            # For this simple plan, we'll just take the first TODO
            first_todo_line = todo_result.strip().split('\n')[0]
            
            # Extract filename from the line (assuming format "filename:line:col: text")
            match = re.match(r"([^:]+):", first_todo_line)
            if not match:
                return "Orchestrator: Could not parse filename from TODO."
            
            filename = match.group(1)
            
            # 2. Use the code_edit tool to fix the TODO
            instruction = f"In the file {filename}, find the first TODO comment and implement it. Remove the TODO comment after implementation."
            print(f"Orchestrator: Instructing code_edit tool to fix TODO in {filename}...")
            
            edit_result = self.agent.use_tool("code_edit", filename=filename, instruction=instruction)
            return f"Orchestrator: Finished 'find and fix a todo' plan.\n{edit_result}"

        else:
            # Default behavior: simple pass-through
            return self.agent.get_response(goal)
