import unittest
from unittest.mock import patch, MagicMock
import subprocess
from tools.run_tests import RunTestsTool

class TestRunTestsTool(unittest.TestCase):
    def setUp(self):
        self.tool = RunTestsTool()

    @patch('subprocess.run')
    def test_run_successful_command(self, mock_run):
        # Arrange
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "All tests passed!"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        command = "pytest"
        
        # Act
        result = self.tool.run(command=command)
        
        # Assert
        self.assertIn("Exit Code: 0", result)
        self.assertIn("--- STDOUT ---\nAll tests passed!", result)
        self.assertIn("--- STDERR ---\n", result)
        mock_run.assert_called_once_with(
            ["pytest"],
            capture_output=True,
            text=True,
            check=False,
            cwd=None,
            timeout=120,
        )

    @patch('subprocess.run')
    def test_run_failed_command(self, mock_run):
        # Arrange
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "1 test failed."
        mock_result.stderr = "AssertionError: 1 != 2"
        mock_run.return_value = mock_result

        command = "pytest"
        
        # Act
        result = self.tool.run(command=command)
        
        # Assert
        self.assertIn("Exit Code: 1", result)
        self.assertIn("--- STDOUT ---\n1 test failed.", result)
        self.assertIn("--- STDERR ---\nAssertionError: 1 != 2", result)

    @patch('subprocess.run')
    def test_command_not_found(self, mock_run):
        # Arrange
        mock_run.side_effect = FileNotFoundError

        command = "non_existent_command"
        
        # Act
        result = self.tool.run(command=command)
        
        # Assert
        self.assertIn("Error: Command 'non_existent_command' not found.", result)

    @patch('subprocess.run')
    def test_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["pytest"], timeout=5, output="partial", stderr="hang")

        result = self.tool.run(command="pytest", timeout_seconds=5)

        self.assertIn("timed out after 5 seconds", result)
        self.assertIn("partial", result)

    @patch('subprocess.run')
    def test_truncates_large_output(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "x" * 500
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = self.tool.run(command="pytest", max_output_chars=80)

        self.assertIn("[truncated", result)

if __name__ == '__main__':
    unittest.main()
