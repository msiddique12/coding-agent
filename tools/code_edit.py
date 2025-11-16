from .base import AgentTool
from llm_providers import get_llm_client

class CodeEditTool(AgentTool):
    def name(self):
        return "code_edit"
    
    def description(self):
        return "Edit any text/code file based on instructions using an LLM."
    
    def args(self):
        return {"filename": str, "instruction": str}
    
    def run(self, filename, instruction):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return f"Cannot read file {filename}: {str(e)}"
        # Use the generic provider client and its `query` method.
        llm = get_llm_client()

        prompt = f"""You are a helpful and precise code editor.
                    Given the following source code, apply the user 
                    instruction below and return the full updated code.

                    Source code:
                    {content}

                    User instruction:
                    {instruction}

                    Return only the updated code without explanation.
                    """
        try:
            # The provider exposes a simple `query(prompt)` interface returning text.
            edited_content = llm.query(prompt)
            return edited_content
        except Exception as e:
            return f"LLM editing error: {str(e)}"
    