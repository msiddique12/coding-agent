from .base import AgentTool
import os

class DeleteFileTool(AgentTool):
    def name(self):
        return "delete_file"
    
    def description(self):
        return "Delete a file. Use with caution."
    
    def args(self):
        return {"filename": str}
    
    def run(self, filename: str):
        try:
            if os.path.exists(filename):
                os.remove(filename)
                return f"Successfully deleted file: {filename}"
            else:
                return f"File not found: {filename}"
        except Exception as e:
            return f"Error deleting file {filename}: {str(e)}"
