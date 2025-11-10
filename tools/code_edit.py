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
        
        llm = get_llm_client()
        
        prompt = f"""You are a helpful and precise code editor.
        Given the following source code, apply the user instruction below and return the full updated code.

        Source code:
        {content}

        User instruction:
        {instruction}

        Return only the updated code without explanation.
        """
        try:
            completion = self.client.chat.completions.create(
                model="qwen/qwen2.5-coder-32b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature = 0.1,
                max_tokens = 2048,
                stream = False   
            )
            edited_content = completion.choices[0].message.content
            return edited_content
        except Exception as e:
            return f"LLM editing error: {str(e)}"
    