from .base import AgentTool
import subprocess

class GitStatusTool(AgentTool):
    def name(self):
        return "git_status"

    def description(self):
        return "Show git status of the repository."
    
    def args(self):
        return {}
    
    def run(self):
        try:
            output = subprocess.check_output(["git", "status"], text=True)
            return output
        except Exception as e:
            return f"Failed to run git status: {e}"
        
class GitDiffTool(AgentTool):
    def name(self):
        return "git_diff"

    def description(self):
        return "Show git diff of unstaged or staged changes."
    
    def args(self):
        return {"path": str}
    
    def run(self, path=None):
        cmd = ["git", "diff"]
        if path:
            cmd.append(path)
        try:
            output = subprocess.check_output(cmd, text=True)
            return output if output else "No changes."
        except Exception as e:
            return f"Failed to run git diff: {e}"