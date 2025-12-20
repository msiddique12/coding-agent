from .base import AgentTool
from llm_providers import get_llm_client

class FileSummarizeTool(AgentTool):
    def name(self):
        return "summarize_file"
    
    def description(self):
        return "Summarize any source or text file contents"
    
    def args(self):
        return {"filename": str}
    
    def run(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return f"Error reading file {filename}: {str(e)}"
        
        llm = get_llm_client()
        prompt = f"Please summarize the following file content:\n\n{content}"
        summary = llm.query(prompt)
        return summary
        