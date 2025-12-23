from .base import AgentTool
import subprocess
import shlex

class RunTestsTool(AgentTool):
    def name(self):
        return "run_tests"
    
    def description(self):
        return "Run a test command and capture the output. Important: Test failures will have a non-zero exit code."
    
    def args(self):
        return {"command": str}
    
    def run(self, command="pytest"):
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
                check=False  # Do not raise an exception for non-zero exit codes
            )
            
            return (
                f"Exit Code: {result.returncode}\n"
                f"--- STDOUT ---\n{result.stdout}\n"
                f"--- STDERR ---\n{result.stderr}"
            )
        except FileNotFoundError:
            return f"Error: Command '{command}' not found. Please ensure the test runner is installed and in your PATH."
        except Exception as e:
            return f"An unexpected error occurred while trying to run '{command}': {e}"