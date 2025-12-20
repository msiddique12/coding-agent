from agent.agent import CodingAgent
import json

class Orchestrator:
    def __init__(self, agent: CodingAgent):
        self.agent = agent

    def _create_plan(self, goal: str):
        """
        Calls the LLM to generate a dynamic plan based on the user's goal.
        """
        print("Orchestrator: Creating a dynamic plan...")
        
        tools = self.agent.list_tools()
        formatted_tools = "\n".join([f"- {name}: {desc}" for name, desc in tools.items()])
        
        prompt = f"""You are a helpful AI assistant that acts as a project manager.
Your goal is to create a plan to accomplish the following user request: "{goal}"

You have the following tools at your disposal:
{formatted_tools}

Your plan should be a sequence of tool calls in JSON format.
Each step in the plan should be a JSON object with two keys: "tool" and "args".
The "tool" key should be the name of the tool to use.
The "args" key should be a dictionary of arguments for the tool.

Return only the JSON array of tool calls, without any explanation.
Example:
[
    {{
        "tool": "file_search",
        "args": {{"pattern": "*.py"}}
    }}
]
"""
        
        try:
            response = self.agent.get_response(prompt)
            plan = json.loads(response)
            return plan
        except json.JSONDecodeError:
            return [{"tool": "error", "args": {"message": "Failed to decode LLM response as JSON."}}]
        except Exception as e:
            return [{"tool": "error", "args": {"message": f"An error occurred during plan creation: {e}"}}]

    def _execute_plan(self, plan: list):
        """
        Executes a plan by calling the agent's tools in sequence.
        """
        print(f"Orchestrator: Executing plan...")
        results = []
        for step in plan:
            tool_name = step.get("tool")
            tool_args = step.get("args", {})

            if tool_name == "error":
                results.append(f"Error in plan: {tool_args.get('message')}")
                break

            if not tool_name:
                results.append("Error: Step in plan is missing a 'tool' key.")
                continue

            print(f"  - Using tool: {tool_name} with args: {tool_args}")
            try:
                result = self.agent.use_tool(tool_name, **tool_args)
                results.append(str(result))
            except Exception as e:
                error_message = f"Error using tool {tool_name}: {e}"
                print(f"    {error_message}")
                results.append(error_message)
                break # Stop execution on error
        
        return "\n".join(results)

    def run(self, goal: str):
        """
        Creates and executes a plan based on the user's goal.
        """
        print(f"Orchestrator received goal: {goal}")
        
        plan = self._create_plan(goal)
        result = self._execute_plan(plan)
        
        return result
