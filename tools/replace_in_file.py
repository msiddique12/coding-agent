from .base import AgentTool


class ReplaceInFileTool(AgentTool):
    def name(self):
        return "replace_in_file"

    def description(self):
        return "Replace exact text in a file. Safer and more deterministic than LLM editing for targeted changes."

    def args(self):
        return {
            "filename": str,
            "old_text": str,
            "new_text": str,
            "replace_all": bool,
        }

    def run(self, filename: str, old_text: str, new_text: str, replace_all: bool = False):
        if old_text == "":
            return "Error: old_text cannot be empty."

        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return f"Error reading file {filename}: {e}"

        occurrences = content.count(old_text)
        if occurrences == 0:
            return f"No occurrences found in {filename}."

        if occurrences > 1 and not replace_all:
            return (
                f"Error: Found {occurrences} occurrences in {filename}. "
                "Set replace_all=true or provide a more specific old_text."
            )

        updated = content.replace(old_text, new_text, -1 if replace_all else 1)
        replaced_count = occurrences if replace_all else 1

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(updated)
        except Exception as e:
            return f"Error writing file {filename}: {e}"

        return f"Replaced {replaced_count} occurrence(s) in {filename}."
