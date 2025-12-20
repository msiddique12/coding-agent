from .base import AgentTool
import os

class CreateFileTool(AgentTool):
    def name(self):
        return "create_file"
    
    def description(self):
        return "Create a new file with specified content. Will create directories if they don't exist."
    
    def args(self):
        return {"filename": str, "content": str}
    
    def run(self, filename: str, content: str):
        try:
            # Create directories if they don't exist
            dir_path = os.path.dirname(filename)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully created file: {filename}"
        except Exception as e:
            return f"Error creating file {filename}: {str(e)}"
