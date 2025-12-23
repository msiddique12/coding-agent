from .base import AgentTool
import subprocess
import shlex

def _run_git_command(command):
    """Helper function to run a git command and return a structured output."""
    try:
        args = shlex.split(command)
        if args[0] != 'git':
            raise ValueError("Command must start with 'git'")
            
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=False
        )
        return (
            f"Exit Code: {result.returncode}\n"
            f"--- STDOUT ---\n{result.stdout}\n"
            f"--- STDERR ---\n{result.stderr}"
        )
    except Exception as e:
        return f"An unexpected error occurred: {e}"

class GitStatusTool(AgentTool):
    def name(self):
        return "git_status"

    def description(self):
        return "Show the working tree status."
    
    def args(self):
        return {}
    
    def run(self):
        return _run_git_command("git status")

class GitDiffTool(AgentTool):
    def name(self):
        return "git_diff"

    def description(self):
        return "Show changes between commits, commit and working tree, etc."
    
    def args(self):
        return {"path": str} # Can be empty to diff all, or a specific path
    
    def run(self, path=""):
        return _run_git_command(f"git diff {path}")

class GitAddTool(AgentTool):
    def name(self):
        return "git_add"

    def description(self):
        return "Add file contents to the index (staging area)."
    
    def args(self):
        return {"files": str} # e.g., 'file1.py file2.py' or '.' for all
    
    def run(self, files: str):
        if not files:
            return "Error: No files specified to add."
        return _run_git_command(f"git add {files}")

class GitCommitTool(AgentTool):
    def name(self):
        return "git_commit"

    def description(self):
        return "Record changes to the repository."
    
    def args(self):
        return {"message": str}
    
    def run(self, message: str):
        if not message:
            return "Error: Commit message cannot be empty."
        # Use shlex.quote to handle messages with special characters
        return _run_git_command(f"git commit -m {shlex.quote(message)}")