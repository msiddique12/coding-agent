from .base import AgentTool
import os, re

class CodeSearchTool(AgentTool):
    def name(self):
        return "code_search"
    
    def description(self):
        return "Search code for a string or regex."

    def args(self):
        return {"pattern": str}
    
    def run(self, pattern):
        res = []
        regex = re.compile(pattern)
        
        for root, _, files in os.walk("."):
            for fn in files:
                if fn.endswith(".py"):
                    path = os.path.join(root, fn)
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if regex.search(content):
                                res.append(f"{path}")
        return "\n".join(res) if res else f"No results for {pattern}"
    
    
                