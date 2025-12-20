import unittest
import os
import shutil
from tools.create_file import CreateFileTool

class TestCreateFileTool(unittest.TestCase):
    def setUp(self):
        self.tool = CreateFileTool()
        self.test_dir = "test_dir_for_create"
        self.test_filename = os.path.join(self.test_dir, "test_file.txt")
        self.test_content = "Hello, new file!"

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_run_creates_file_and_directories(self):
        # Act
        result = self.tool.run(filename=self.test_filename, content=self.test_content)
        
        # Assert
        self.assertEqual(result, f"Successfully created file: {self.test_filename}")
        self.assertTrue(os.path.exists(self.test_filename))
        
        with open(self.test_filename, "r") as f:
            content = f.read()
        self.assertEqual(content, self.test_content)

if __name__ == '__main__':
    unittest.main()
