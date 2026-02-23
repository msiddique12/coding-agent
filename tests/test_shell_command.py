import unittest
from unittest.mock import patch
import subprocess
from tools.shell_command import ShellCommandTool

class TestShellCommandTool(unittest.TestCase):
    def setUp(self):
        self.tool = ShellCommandTool()

    def test_run_simple_command(self):
        # Arrange
        command = 'echo "Hello, shell!"'
        
        # Act
        result = self.tool.run(command=command)
        
        # Assert
        self.assertIn("Hello, shell!", result)
        self.assertIn("STDOUT:", result)

    def test_run_command_with_error(self):
        # Arrange
        command = 'ls non_existent_directory'
        
        # Act
        result = self.tool.run(command=command)
        
        # Assert
        self.assertIn("failed", result)
        self.assertIn("STDERR:", result)
        self.assertIn("No such file or directory", result)

    @patch("subprocess.run")
    def test_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="sleep 10", timeout=1, output="...", stderr="")
        result = self.tool.run(command="sleep 10", timeout_seconds=1)
        self.assertIn("timed out after 1 seconds", result)

    @patch("subprocess.run")
    def test_truncates_output(self, mock_run):
        class Result:
            stdout = "a" * 400
            stderr = ""

        mock_run.return_value = Result()
        result = self.tool.run(command="echo hi", max_output_chars=50)
        self.assertIn("[truncated", result)

if __name__ == '__main__':
    unittest.main()
