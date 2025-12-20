from agent.agent import CodingAgent
import json
from rich.console import Console
from rich.syntax import Syntax

MAX_TURNS = 10
console = Console()

class Orchestrator:
    def __init__(self, agent: CodingAgent):
        self.agent = agent

    def _think(self, goal: str, history: list):
        """
        This is the "Reason" part of ReAct. It thinks about the next action.
        """
        tools_with_args = []
        for tool_name, tool in self.agent.tools.items():
            args_str = ", ".join([f"{name}: {type.__name__}" for name, type in tool.args().items()])
            tools_with_args.append(f"- {tool_name}({args_str}): {tool.description()}")
        
        formatted_tools = "\n".join(tools_with_args)
        history_str = "\n".join(history)

        prompt = f"""You are an autonomous AI agent. Your goal is to solve the user's request.

GOAL: "{goal}"

You will reason step-by-step, choosing one of the following tools to use at each step.

TOOLS:
{formatted_tools}

HISTORY:
{history_str}

Based on the history, decide on your next thought and action. 
Your action MUST be one of the tools listed above.
You MUST respond in the following JSON format, and nothing else:
{{
    "thought": "Your reasoning for the next action...",
    "action": {{
        "tool": "tool_name",
        "args": {{ "arg1": "value1", "arg2": "value2" }}
    }}
}}

If you have accomplished the goal, use the 'finish' tool.
"""
        
        response_str = self.agent.get_response(prompt)
        
        try:
            # The LLM can sometimes return markdown wrapping the JSON
            response_str = response_str.strip().replace("```json", "").replace("```", "")
            response = json.loads(response_str)
            return response
        except json.JSONDecodeError:
            # If the LLM returns a non-JSON response, we'll try to recover
            return {
                "thought": "The last response was not valid JSON. I will try again.",
                "action": {"tool": "error", "args": {"message": f"Invalid JSON response: {response_str}"}}
            }

    def _act(self, action: dict):
        """
        This is the "Act" part of ReAct. It executes the chosen tool.
        """
        tool_name = action.get("tool")
        tool_args = action.get("args", {})

        if not tool_name:
            return "Error: LLM response did not include a 'tool' for the action."

        console.print(f"Action: Using tool [bold cyan]{tool_name}[/bold cyan] with args: {tool_args}")
        
        try:
            observation = self.agent.use_tool(tool_name, **tool_args)
        except Exception as e:
            observation = f"Error using tool {tool_name}: {e}"
            
        return observation

    def run(self, goal: str):
        """
        Runs the ReAct loop to accomplish a goal.
        """
        history = []
        
        for i in range(MAX_TURNS):
            console.print(f"\n--- Turn {i+1}/{MAX_TURNS} ---")
            
            # 1. Think
            next_step = self._think(goal, history)
            thought = next_step.get("thought", "No thought provided.")
            action = next_step.get("action")

            if not action:
                final_answer = "Agent did not produce an action. Stopping."
                console.print(f"[bold red]{final_answer}[/bold red]")
                break
            
            history.append(f"Thought: {thought}")
            console.print(f"Thought: {thought}")
            
            if action["tool"] == "finish":
                final_answer = action.get("args", {}).get("answer", "No final answer provided.")
                console.print(f"Final Answer: {final_answer}", style="bold green")
                return final_answer
            
            # 2. Act
            observation = self._act(action)
            history.append(f"Action: {action}")
            history.append(f"Observation: {observation}")

            console.print("Observation:", style="bold yellow")
            # Pretty print code blocks if observation is a string
            if isinstance(observation, str):
                if "```" in observation:
                     syntax = Syntax(observation, "python", theme="solarized-dark", line_numbers=True)
                     console.print(syntax)
                else:
                    console.print(observation)
            else:
                console.print(observation)

        final_answer = "Reached max turns, stopping."
        console.print(f"[bold red]{final_answer}[/bold red]")
        return final_answer
