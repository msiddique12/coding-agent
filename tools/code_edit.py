from .base import AgentTool
from llm_providers import get_llm_client


class CodeEditTool(AgentTool):
    def name(self):
        return "code_edit"
    
    def description(self):
        return "Edit any text/code file based on instructions using an LLM and writes the changes back to the file."
    
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
            edited_content = llm.query(prompt)
            # Clean the response from the LLM
            if edited_content.strip().startswith("```") and edited_content.strip().endswith("```"):
                lines = edited_content.strip().split("\n")
                # Remove the first and last lines if they are code fences
                if lines[0].strip().startswith("```") and lines[-1].strip() == "```":
                    edited_content = "\n".join(lines[1:-1])
            with open(filename, "w", encoding="utf-8") as f:
                f.write(edited_content)
            return edited_content
        except Exception as e:
            return f"LLM editing error: {str(e)}"
