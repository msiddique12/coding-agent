from .base import AgentTool
import subprocess
import shutil
import json

class CodeSearchTool(AgentTool):
    def name(self):
        return "code_search"

    def description(self):
        return (
            "Uses Ripgrep (rg) to search for a regex pattern in the codebase. "
            "Returns matching lines with context."
        )

    def args(self):
        return {
            "pattern": str,
            "context_lines": int,
        }

    def __init__(self):
        super().__init__()
        if not shutil.which("rg"):
            raise RuntimeError("Ripgrep (rg) is not installed. Please install it to use the code_search tool.")

    def run(self, pattern: str, context_lines: int = 0) -> str:
        """
        Run Ripgrep to search for a pattern in the current directory.
        """
        try:
            command = [
                "rg",
                "--json",
                f"-C{context_lines}",
                pattern,
                "."
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            output_lines = result.stdout.strip().split('\n')
            formatted_results = []

            for line in output_lines:
                try:
                    data = json.loads(line)
                    if data["type"] == "match":
                        path = data["data"]["path"]["text"]
                        lines = data["data"]["lines"]["text"]
                        line_number = data["data"]["line_number"]
                        
                        # Simple formatting for now
                        formatted_results.append(f"File: {path} (Line: {line_number})\n---\n{lines}\n---\n")

                except (json.JSONDecodeError, KeyError):
                    # Ignore non-match lines or lines that don't parse correctly
                    continue
            
            if not formatted_results:
                return f"No matches found for '{pattern}'"
            
            return "\n".join(formatted_results)

        except FileNotFoundError:
            return "Error: Ripgrep (rg) is not installed or not in your PATH."
        except subprocess.CalledProcessError as e:
            # rg exits with 1 if no matches are found, which is not an error for us.
            if e.returncode == 1 and not e.stdout and not e.stderr:
                return f"No matches found for '{pattern}'"
            return f"An error occurred while running Ripgrep: {e.stderr}"