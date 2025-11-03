from .base import AgentTool
import os

class FileSearchTool(AgentTool):
    def name(self): 
        return "file_search"
    
    def description(self): 
        return "List files in the project (optionally filter by extension)."
    
    def args(self): 
        return {"ext": str}
    
    def run(self, ext=None):
        res =[]
        for root, _, files in os.walk("."):
            for f in files:
                if (not ext) or f.endswith(ext):
                    res.append(os.path.join(root, f))
        return "\n".join(res)

            
    