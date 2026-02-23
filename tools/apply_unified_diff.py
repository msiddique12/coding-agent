import os
import re

from .base import AgentTool


HUNK_RE = re.compile(
    r"^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))? \+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@"
)


class UnifiedDiffApplyTool(AgentTool):
    def name(self):
        return "apply_unified_diff"

    def description(self):
        return "Apply a unified diff patch deterministically across one or more files. Fails if context does not match."

    def args(self):
        return {"patch": str}

    def run(self, patch: str):
        try:
            file_diffs = self._parse_patch(patch)
            planned_writes = self._apply_in_memory(file_diffs)
            self._write_all(planned_writes)
        except Exception as e:
            return f"Patch apply failed: {e}"

        summary = []
        for path, content in planned_writes:
            if content is None:
                summary.append(f"Deleted {path}")
            elif os.path.exists(path):
                summary.append(f"Updated {path}")
            else:
                summary.append(f"Created {path}")
        return "Patch applied successfully.\n" + "\n".join(summary)

    def _parse_patch(self, patch: str):
        lines = patch.splitlines(keepends=True)
        i = 0
        file_diffs = []

        while i < len(lines):
            line = lines[i]
            if line.startswith("diff --git "):
                i += 1
                continue
            if line.startswith("--- "):
                old_path = self._normalize_path(line[4:].strip())
                i += 1
                if i >= len(lines) or not lines[i].startswith("+++ "):
                    raise ValueError("Malformed patch: missing '+++' header")
                new_path = self._normalize_path(lines[i][4:].strip())
                i += 1

                hunks = []
                while i < len(lines):
                    if lines[i].startswith("diff --git ") or lines[i].startswith("--- "):
                        break
                    if lines[i].startswith("@@ "):
                        header = lines[i].rstrip("\n")
                        match = HUNK_RE.match(header)
                        if not match:
                            raise ValueError(f"Malformed hunk header: {header}")
                        i += 1
                        hunk_lines = []
                        while i < len(lines):
                            if lines[i].startswith("@@ ") or lines[i].startswith("--- ") or lines[i].startswith("diff --git "):
                                break
                            if lines[i].startswith("\\ No newline at end of file"):
                                i += 1
                                continue
                            hunk_lines.append(lines[i])
                            i += 1
                        hunks.append(
                            {
                                "old_start": int(match.group("old_start")),
                                "old_count": int(match.group("old_count") or "1"),
                                "new_start": int(match.group("new_start")),
                                "new_count": int(match.group("new_count") or "1"),
                                "lines": hunk_lines,
                            }
                        )
                    else:
                        i += 1

                file_diffs.append(
                    {
                        "old_path": old_path,
                        "new_path": new_path,
                        "hunks": hunks,
                    }
                )
                continue
            i += 1

        if not file_diffs:
            raise ValueError("No file diffs found in patch")
        return file_diffs

    def _normalize_path(self, raw: str):
        if raw == "/dev/null":
            return None
        if raw.startswith("a/") or raw.startswith("b/"):
            return raw[2:]
        return raw

    def _read_lines(self, path):
        if path is None:
            return []
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().splitlines(keepends=True)

    def _apply_in_memory(self, file_diffs):
        planned = []
        for fd in file_diffs:
            old_path = fd["old_path"]
            new_path = fd["new_path"]
            hunks = fd["hunks"]

            is_create = old_path is None and new_path is not None
            is_delete = new_path is None and old_path is not None
            source_path = old_path if old_path is not None else new_path

            original_lines = [] if is_create else self._read_lines(source_path)
            updated_lines = self._apply_hunks_to_lines(original_lines, hunks, source_path or new_path)

            if is_delete:
                if updated_lines:
                    raise ValueError(f"Delete patch for {old_path} did not remove all content")
                planned.append((old_path, None))
            else:
                target_path = new_path or old_path
                planned.append((target_path, "".join(updated_lines)))
        return planned

    def _apply_hunks_to_lines(self, original_lines, hunks, path_label):
        out = []
        cursor = 0

        for hunk in hunks:
            start_idx = max(0, hunk["old_start"] - 1)
            if start_idx < cursor:
                raise ValueError(f"Overlapping hunks for {path_label}")

            out.extend(original_lines[cursor:start_idx])
            src_idx = start_idx

            for raw_line in hunk["lines"]:
                if not raw_line:
                    continue
                marker = raw_line[0]
                content = raw_line[1:]
                if marker == " ":
                    if src_idx >= len(original_lines) or original_lines[src_idx] != content:
                        raise ValueError(
                            f"Context mismatch in {path_label} at line {src_idx + 1}: expected {content!r}"
                        )
                    out.append(original_lines[src_idx])
                    src_idx += 1
                elif marker == "-":
                    if src_idx >= len(original_lines) or original_lines[src_idx] != content:
                        raise ValueError(
                            f"Removal mismatch in {path_label} at line {src_idx + 1}: expected {content!r}"
                        )
                    src_idx += 1
                elif marker == "+":
                    out.append(content)
                else:
                    raise ValueError(f"Invalid hunk line prefix {marker!r} in {path_label}")

            cursor = src_idx

        out.extend(original_lines[cursor:])
        return out

    def _write_all(self, planned_writes):
        for path, content in planned_writes:
            if content is None:
                if os.path.exists(path):
                    os.remove(path)
                continue
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
