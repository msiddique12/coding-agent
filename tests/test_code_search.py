import unittest
from unittest.mock import patch, MagicMock
import subprocess
import json
from tools.code_search import CodeSearchTool

class TestCodeSearchTool(unittest.TestCase):

    @patch('shutil.which', return_value=True)
    def setUp(self, mock_which):
        self.tool = CodeSearchTool()

    @patch('subprocess.run')
    def test_run_successful_search(self, mock_run):
        # Arrange
        rg_output = {
            "type": "match",
            "data": {
                "path": {"text": "test_file.py"},
                "lines": {"text": "Line 1\nLine 2 with banana\nLine 3"},
                "line_number": 2,
            }
        }
        mock_result = MagicMock()
        mock_result.stdout = json.dumps(rg_output)
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Act
        result = self.tool.run(pattern="banana", context_lines=1)

        # Assert
        self.assertIn("File: test_file.py (Line: 2)", result)
        self.assertIn("Line 2 with banana", result)
        
        expected_command = ["rg", "--json", "-C1", "banana", "."]
        mock_run.assert_called_once_with(
            expected_command,
            capture_output=True,
            text=True,
            check=True
        )

    @patch('subprocess.run')
    def test_run_no_matches(self, mock_run):
        # Arrange
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="rg", output="", stderr=""
        )

        # Act
        result = self.tool.run(pattern="banana")

        # Assert
        self.assertEqual(result, "No matches found for 'banana'")

    @patch('shutil.which', return_value=None)
    def test_init_raises_error_if_rg_not_found(self, mock_which):
        # Assert
        with self.assertRaisesRegex(RuntimeError, "Ripgrep \(rg\) is not installed"):
            CodeSearchTool()

if __name__ == '__main__':
    # Need to import json for the test
    unittest.main()