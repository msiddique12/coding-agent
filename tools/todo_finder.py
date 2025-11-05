from .base import AgentTool
import os, re

class ToDoFinderTool(AgentTool):
    def name(self):
        return "todo_finder"
    
    def description(self):
        return "Find all TODO/FIXME and similar notes in any text files."
    
    def args(self):
        return {}
    
    def run(self):
        todo_pattern = re.compile(r'#|//|<!--|--|;\s*(TODO|FIXME|NOTE|XXX)', re.IGNORECASE)
        todos = []
        for root, _, files in os.walk("."):
            for fname in files:
                path = os.path.join(root, fname)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        for lineno, line in enumerate(f, start=1):
                            if todo_pattern.search(line):
                                todos.append(f"{path}:{lineno}: {line.strip()}")
                except Exception:
                    continue
        return "\n".join(todos) if todos else "No TODOs found."