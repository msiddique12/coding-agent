from .base import AgentTool
from llm_providers import get_llm_client

class CodeEditTool(AgentTool):
    def name(self):
        return "code_edit"
    
    def description(self):
        return "Edit any text/code file using instructions via LLM."
    
    def args(self):
        return {"filename": str, "instruction": str}
    
    def run(self, filename, instruction):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return f"Cannot read file {filename}: {str(e)}"
        
        llm = get_llm_client()
        edited_content = content #TODO: incomplete: figure out how to make this tool work + be efficient

        return edited_content
    