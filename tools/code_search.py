from .base import AgentTool
import os, re

class CodeSearchTool(AgentTool):
    def name(self):
        return "code_search"
    
    def description(self):
        return "Search all text files for a regex or string pattern"

    def args(self):
        return {"pattern": str}
    
    def run(self, pattern):
        res = []
        regex = re.compile(pattern)
        
        for root, _, files in os.walk("."):
            for filename in files:
                path = os.path.join(root, filename)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if regex.search(content):
                                res.append(f"{path}")
                except Exception:
                    #binary files and other non-text files
                    continue
        return "\n".join(res) if res else f"No matches for {pattern}"
    
    
                