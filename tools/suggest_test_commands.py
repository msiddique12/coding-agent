import os
import subprocess

from .base import AgentTool
from utils.filesystem import IGNORE_DIRS


class SuggestTestCommandsTool(AgentTool):
    def name(self):
        return "suggest_test_commands"

    def description(self):
        return "Suggest targeted test commands from changed files (git diff) or provided paths."

    def args(self):
        return {"paths": str}

    def run(self, paths: str = ""):
        changed_paths = self._parse_paths(paths) if paths else self._get_changed_paths()
        if not changed_paths:
            return "No changed files detected. Suggested command:\n- pytest -q"

        commands = self._suggest_commands(changed_paths)
        lines = [
            "Changed files:",
            *[f"- {p}" for p in changed_paths],
            "",
            "Suggested test commands (most targeted first):",
            *[f"- {cmd}" for cmd in commands],
        ]
        return "\n".join(lines)

    def _parse_paths(self, paths: str):
        return [p.strip() for p in paths.split(",") if p.strip()]

    def _get_changed_paths(self):
        candidates = []
        seen = set()

        commands = [
            ["git", "diff", "--name-only"],
            ["git", "diff", "--name-only", "--cached"],
            ["git", "ls-files", "--others", "--exclude-standard"],
        ]
        for cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            except Exception:
                continue
            for line in result.stdout.splitlines():
                path = line.strip()
                if not path or path in seen:
                    continue
                seen.add(path)
                candidates.append(path)
        return candidates

    def _suggest_commands(self, changed_paths):
        suggestions = []
        seen_cmds = set()

        for path in changed_paths:
            if not path.endswith(".py"):
                continue

            if self._is_test_file(path):
                self._add(suggestions, seen_cmds, f"pytest -q {path}")
                continue

            for candidate in self._candidate_tests_for_source(path):
                if os.path.exists(candidate):
                    self._add(suggestions, seen_cmds, f"pytest -q {candidate}")

        if not suggestions:
            self._add(suggestions, seen_cmds, "pytest -q")
        else:
            # Keep a broader fallback at the end.
            self._add(suggestions, seen_cmds, "pytest -q")

        return suggestions

    def _is_test_file(self, path):
        base = os.path.basename(path)
        return path.startswith("tests" + os.sep) or base.startswith("test_") or base.endswith("_test.py")

    def _candidate_tests_for_source(self, path):
        base = os.path.basename(path)
        stem = base[:-3] if base.endswith(".py") else base
        direct_candidates = [
            os.path.join("tests", f"test_{stem}.py"),
            os.path.join("tests", f"{stem}_test.py"),
        ]

        # Include package-aware mirror path, e.g. src/foo/bar.py -> tests/foo/test_bar.py
        parts = path.split(os.sep)
        if len(parts) > 1:
            rel_dir = os.path.join(*parts[:-1])
            if rel_dir and rel_dir not in {".", "tests"}:
                direct_candidates.append(os.path.join("tests", rel_dir, f"test_{stem}.py"))
                direct_candidates.append(os.path.join("tests", rel_dir, f"{stem}_test.py"))

        # Broad scan fallback for basename-based test files.
        for root, dirs, files in os.walk("tests"):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for filename in files:
                if filename in {f"test_{stem}.py", f"{stem}_test.py"}:
                    direct_candidates.append(os.path.join(root, filename))

        # Preserve order, dedupe.
        seen = set()
        ordered = []
        for c in direct_candidates:
            if c not in seen:
                seen.add(c)
                ordered.append(c)
        return ordered

    def _add(self, suggestions, seen_cmds, cmd):
        if cmd not in seen_cmds:
            seen_cmds.add(cmd)
            suggestions.append(cmd)
