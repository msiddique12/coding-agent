import unittest
import os
from unittest.mock import patch, MagicMock
from tools.code_edit import CodeEditTool

class TestCodeEditTool(unittest.TestCase):
    def setUp(self):
        self.tool = CodeEditTool()
        self.test_filename = "test_file.txt"
        with open(self.test_filename, "w") as f:
            f.write("Hello, world!")

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    @patch('tools.code_edit.get_llm_client')
    def test_run_writes_to_file(self, mock_get_llm_client):
        # Arrange
        mock_llm = MagicMock()
        mock_llm.query.return_value = "Hello, universe!"
        mock_get_llm_client.return_value = mock_llm

        instruction = "Change 'world' to 'universe'"
        
        # Act
        result = self.tool.run(self.test_filename, instruction)
        
        # Assert
        self.assertEqual(result, "Hello, universe!")
        
        with open(self.test_filename, "r") as f:
            content = f.read()
        self.assertEqual(content, "Hello, universe!")

        # Verify that the LLM was called with the correct prompt
        mock_llm.query.assert_called_once()
        call_args = mock_llm.query.call_args
        prompt = call_args[0][0]
        self.assertIn("Hello, world!", prompt)
        self.assertIn(instruction, prompt)

if __name__ == '__main__':
    unittest.main()
