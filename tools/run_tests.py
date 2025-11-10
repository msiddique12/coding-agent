from .base import AgentTool
import subprocess

class RunTestsTool(AgentTool):
    def name(self):
        return "run_tests"
    
    def description(self):
        return "Run tests using the default test command (pytest, npm test, etc.)."
    
    def args(self):
        return {"command": str}
    
    def run(self, command="pytest"):
        try:
            output = subprocess.check_output(command.split(), text=True)
            return output
        except Exception as e:
            return f"Failed to run tests({command}): {e}"