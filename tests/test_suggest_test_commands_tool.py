import os
import shutil
import unittest
from unittest.mock import patch, MagicMock

from tools.suggest_test_commands import SuggestTestCommandsTool


class TestSuggestTestCommandsTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tmp_suggest_tests"
        os.makedirs(self.test_dir, exist_ok=True)
        self.prev_cwd = os.getcwd()
        os.chdir(self.test_dir)

        os.makedirs("agent", exist_ok=True)
        os.makedirs("tests", exist_ok=True)
        with open("agent/example.py", "w", encoding="utf-8") as f:
            f.write("x = 1\n")
        with open("tests/test_example.py", "w", encoding="utf-8") as f:
            f.write("def test_x():\n    assert True\n")

        self.tool = SuggestTestCommandsTool()

    def tearDown(self):
        os.chdir(self.prev_cwd)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_suggests_targeted_test_for_source_file(self):
        result = self.tool.run(paths="agent/example.py")
        self.assertIn("pytest -q tests/test_example.py", result)
        self.assertIn("pytest -q", result)

    def test_suggests_test_file_directly(self):
        result = self.tool.run(paths="tests/test_example.py")
        self.assertIn("- pytest -q tests/test_example.py", result)

    @patch("subprocess.run")
    def test_uses_git_changed_files_when_paths_not_provided(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "agent/example.py\n"
        mock_run.return_value = mock_result

        result = self.tool.run()

        self.assertIn("Changed files:", result)
        self.assertIn("agent/example.py", result)
        self.assertIn("pytest -q tests/test_example.py", result)

    @patch("subprocess.run")
    def test_falls_back_when_no_changes(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        result = self.tool.run()
        self.assertIn("No changed files detected", result)
        self.assertIn("pytest -q", result)


if __name__ == "__main__":
    unittest.main()
