from .base import AgentTool
import os
import fnmatch

class FileSearchTool(AgentTool):
    def name(self): 
        return "file_search"
    
    def description(self): 
        return "List project files, optionally filter by wildcard pattern (e.g. '*.js', '.java')."
    
    def args(self): 
        return {"pattern": str}
    
    def run(self, pattern="*"):
        res = []
        for root, _, files in os.walk("."):
            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    res.append(os.path.join(root, filename))
        return "\n".join(res) if res else f"No files matched the pattern '{pattern}'."

            
    