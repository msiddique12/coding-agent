from .base import AgentTool
import os, re
from utils.filesystem import IGNORE_DIRS

class ToDoFinderTool(AgentTool):
    def name(self):
        return "todo_finder"
    
    def description(self):
        return "Find all TODO/FIXME and similar notes in any text files."
    
    def args(self):
        return {}
    
    def run(self):
        todo_pattern = re.compile(r'(TODO|FIXME|NOTE|XXX)', re.IGNORECASE)
        todos = []
        for root, dirs, files in os.walk("."):
            # Exclude ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for fname in files:
                path = os.path.join(root, fname)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        for lineno, line in enumerate(f, start=1):
                            if todo_pattern.search(line):
                                # Check for common comment markers to reduce false positives
                                if any(marker in line for marker in ['#', '//', '/*', '<!--']):
                                    todos.append(f"{path}:{lineno}: {line.strip()}")
                except Exception:
                    continue
        return "\n".join(todos) if todos else "No TODOs found."