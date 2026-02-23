from .base import AgentTool


class ReadFileTool(AgentTool):
    def name(self):
        return "read_file"

    def description(self):
        return "Read a file. Supports optional line ranges for targeted inspection."

    def args(self):
        return {
            "filename": str,
            "start_line": int,
            "end_line": int,
        }

    def run(self, filename: str, start_line: int = 1, end_line: int = 0):
        if start_line < 1:
            return "Error: start_line must be >= 1"
        if end_line and end_line < start_line:
            return "Error: end_line must be >= start_line"

        try:
            with open(filename, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception as e:
            return f"Error reading file {filename}: {e}"

        if not lines:
            return f"File: {filename}\n(Empty file)"

        start_idx = start_line - 1
        end_idx = end_line if end_line else len(lines)
        selected = lines[start_idx:end_idx]
        if not selected:
            return f"Error: Requested range {start_line}-{end_line or len(lines)} is outside the file."

        rendered = []
        for offset, line in enumerate(selected, start=start_line):
            rendered.append(f"{offset:>6} | {line.rstrip()}")

        actual_end = start_line + len(selected) - 1
        return (
            f"File: {filename}\n"
            f"Lines: {start_line}-{actual_end} of {len(lines)}\n"
            + "\n".join(rendered)
        )
