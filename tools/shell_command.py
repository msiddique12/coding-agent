from .base import AgentTool
import subprocess

class ShellCommandTool(AgentTool):
    def name(self):
        return "shell_command"
    
    def description(self):
        return "Execute a shell command. Use with extreme caution. Only run safe and necessary commands."
    
    def args(self):
        return {"command": str}
    
    def run(self, command: str):
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            if not output:
                return "Command executed successfully with no output."
            return output
        except subprocess.CalledProcessError as e:
            return f"Command failed with exit code {e.returncode}.\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        except Exception as e:
            return f"An error occurred: {str(e)}"