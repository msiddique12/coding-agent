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
            check=False
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

if __name__ == '__main__':
    unittest.main()
