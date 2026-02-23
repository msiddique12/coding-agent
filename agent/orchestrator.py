from agent.agent import CodingAgent
import json
from rich.console import Console
from rich.syntax import Syntax

DEFAULT_MAX_TURNS = 10
MAX_OBSERVATION_CHARS = 4000
MAX_HISTORY_ITEMS = 24
console = Console()

# Define tools that perform actions requiring user confirmation
DANGEROUS_TOOLS = {
    "run_tests",
    "shell_command",
    "code_edit",
    "create_file",
    "apply_unified_diff",
    "append_file",
    "delete_file",
    "replace_in_file",
    "git_add", 
    "git_commit"
}

class Orchestrator:
    def __init__(self, agent: CodingAgent, max_turns: int = DEFAULT_MAX_TURNS, auto_approve: bool = False):
        self.agent = agent
        self.max_turns = max_turns
        self.auto_approve = auto_approve

    def _truncate_text(self, value, max_chars=MAX_OBSERVATION_CHARS):
        text = value if isinstance(value, str) else repr(value)
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + f"\n...[truncated {len(text) - max_chars} chars]"

    def _parse_action_json(self, response_str: str) -> dict:
        cleaned = response_str.strip().replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(cleaned[start : end + 1])
            raise

    def _think(self, goal: str, history: list):
        """
        This is the "Reason" part of ReAct. It thinks about the next action.
        """
        # Add project structure to the context
        try:
            project_files = self.agent.use_tool("file_search")
        except Exception:
            project_files = "\n".join(self.agent.list_files())
        project_files = self._truncate_text(project_files, 3000)
        tools_with_args = []
        for tool_name, tool in self.agent.tools.items():
            args_str = ", ".join([f"{name}: {type.__name__}" for name, type in tool.args().items()])
            tools_with_args.append(f"- {tool_name}({args_str}): {tool.description()}")
        if self.agent.unavailable_tools:
            unavailable = "\n".join(
                f"- {name}: {reason}" for name, reason in self.agent.unavailable_tools.items()
            )
            tools_with_args.append("\nUNAVAILABLE TOOLS (do not select these):\n" + unavailable)

        formatted_tools = "\n".join(tools_with_args)
        history_str = "\n".join(history[-MAX_HISTORY_ITEMS:])

        prompt = f"""You are an autonomous AI agent. Your goal is to solve the user's request.

GOAL: "{goal}"

You have a general understanding of the project structure:
PROJECT STRUCTURE:
{project_files}

You will reason step-by-step, choosing one of the following tools to use at each step.
Prefer deterministic tools for code changes:
- Use read_file to inspect exact file contents / line ranges before editing.
- Use replace_in_file or append_file for targeted edits.
- Use apply_unified_diff for multi-line edits when you know exact context.
- Use code_edit only for complex refactors.
- Use git_diff and run_tests to validate before finishing.

TOOLS:
{formatted_tools}

HISTORY:
{history_str}

Based on the project structure and the history, decide on your next thought and action. 
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
            response = self._parse_action_json(response_str)
            return response
        except json.JSONDecodeError:
            # If the LLM returns a non-JSON response, we'll try to recover
            return {
                "thought": "The last response was not valid JSON. I will try again.",
                "action": {"tool": "finish", "args": {"answer": f"Stopped because the model returned invalid JSON: {response_str}"}}
            }

    def _act(self, action: dict):
        """
        This is the "Act" part of ReAct. It executes the chosen tool.
        """
        tool_name = action.get("tool")
        tool_args = action.get("args", {})

        if not tool_name:
            return "Error: LLM response did not include a 'tool' for the action."
        if not isinstance(tool_args, dict):
            return f"Error: Tool args for '{tool_name}' must be a JSON object."
        if tool_name not in self.agent.tools and tool_name != "finish":
            available = ", ".join(sorted(self.agent.tools.keys()))
            return f"Error: Unknown tool '{tool_name}'. Available tools: {available}"

        console.print(f"Action: Using tool [bold cyan]{tool_name}[/bold cyan] with args: {tool_args}")
        
        # Safety confirmation for dangerous tools
        if tool_name in DANGEROUS_TOOLS:
            if self.auto_approve:
                console.print("[yellow]Auto-approved dangerous tool execution.[/yellow]")
            else:
                confirm = input("Run this action? (y/n): ")
                if confirm.lower() != 'y':
                    return f"User denied execution of tool '{tool_name}'."

        try:
            observation = self.agent.use_tool(tool_name, **tool_args)
        except Exception as e:
            observation = f"Error using tool {tool_name}: {e}"
            
        return observation

    def _run_loop(self, goal: str, history: list | None = None):
        history = list(history or [])

        for i in range(self.max_turns):
            console.print(f"\n--- Turn {i+1}/{self.max_turns} ---")
            
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
            
            if action.get("tool") == "finish":
                final_answer = action.get("args", {}).get("answer", "No final answer provided.")
                console.print(f"Final Answer: {final_answer}", style="bold green")
                return final_answer, history
            
            # 2. Act
            observation = self._act(action)
            history.append(f"Action: {action}")
            history.append(f"Observation: {self._truncate_text(observation)}")

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

        final_answer = f"Reached max turns ({self.max_turns}), stopping."
        console.print(f"[bold red]{final_answer}[/bold red]")
        return final_answer, history

    def run(self, goal: str, history: list | None = None):
        """
        Runs the ReAct loop to accomplish a goal.
        """
        final_answer, _history = self._run_loop(goal, history=history)
        return final_answer

    def run_with_state(self, goal: str, history: list | None = None):
        final_answer, updated_history = self._run_loop(goal, history=history)
        return {"goal": goal, "history": updated_history, "final_answer": final_answer}
