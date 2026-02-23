from .base import AgentTool
import subprocess
import shlex


def _truncate_output(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n...[truncated {len(text) - max_chars} chars]"


class RunTestsTool(AgentTool):
    def name(self):
        return "run_tests"
    
    def description(self):
        return "Run a test command and capture the output. Important: Test failures will have a non-zero exit code."
    
    def args(self):
        return {"command": str, "cwd": str, "timeout_seconds": int, "max_output_chars": int}
    
    def run(
        self,
        command="pytest",
        cwd: str | None = None,
        timeout_seconds: int = 120,
        max_output_chars: int = 12000,
    ):
        """
        Runs the given test command and returns the exit code, stdout, and stderr.
        This is a 'dangerous' tool and requires user confirmation.
        """
        try:
            # Use shlex.split to handle complex commands safely
            args = shlex.split(command)
            
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                check=False,  # Do not raise an exception for non-zero exit codes
                cwd=cwd or None,
                timeout=timeout_seconds if timeout_seconds and timeout_seconds > 0 else None,
            )
            
            text = (
                f"Exit Code: {result.returncode}\n"
                f"--- STDOUT ---\n{result.stdout}\n"
                f"--- STDERR ---\n{result.stderr}"
            )
            return _truncate_output(text, max_output_chars)
        except FileNotFoundError:
            return f"Error: Command '{command}' not found. Please ensure the test runner is installed and in your PATH."
        except subprocess.TimeoutExpired as e:
            stdout = e.stdout or ""
            stderr = e.stderr or ""
            text = (
                f"Command timed out after {timeout_seconds} seconds.\n"
                f"--- STDOUT ---\n{stdout}\n"
                f"--- STDERR ---\n{stderr}"
            )
            return _truncate_output(text, max_output_chars)
        except Exception as e:
            return f"An unexpected error occurred while trying to run '{command}': {e}"
