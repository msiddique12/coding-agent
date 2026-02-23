from .base import AgentTool
import subprocess


def _truncate_output(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n...[truncated {len(text) - max_chars} chars]"


class ShellCommandTool(AgentTool):
    def name(self):
        return "shell_command"
    
    def description(self):
        return "Execute a shell command. Use with extreme caution. Only run safe and necessary commands."
    
    def args(self):
        return {"command": str, "cwd": str, "timeout_seconds": int, "max_output_chars": int}
    
    def run(
        self,
        command: str,
        cwd: str | None = None,
        timeout_seconds: int = 30,
        max_output_chars: int = 8000,
    ):
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True,
                cwd=cwd or None,
                timeout=timeout_seconds if timeout_seconds and timeout_seconds > 0 else None,
            )
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            if not output:
                return "Command executed successfully with no output."
            return _truncate_output(output, max_output_chars)
        except subprocess.CalledProcessError as e:
            text = f"Command failed with exit code {e.returncode}.\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
            return _truncate_output(text, max_output_chars)
        except subprocess.TimeoutExpired as e:
            stdout = e.stdout or ""
            stderr = e.stderr or ""
            text = (
                f"Command timed out after {timeout_seconds} seconds.\n"
                f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}"
            )
            return _truncate_output(text, max_output_chars)
        except Exception as e:
            return f"An error occurred: {str(e)}"
