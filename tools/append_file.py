from .base import AgentTool


class AppendFileTool(AgentTool):
    def name(self):
        return "append_file"

    def description(self):
        return "Append text to the end of an existing file."

    def args(self):
        return {"filename": str, "content": str}

    def run(self, filename: str, content: str):
        try:
            with open(filename, "a", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            return f"Error appending to file {filename}: {e}"
        return f"Appended {len(content)} characters to {filename}."
