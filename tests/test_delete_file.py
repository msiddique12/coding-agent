import unittest
import os
from tools.delete_file import DeleteFileTool

class TestDeleteFileTool(unittest.TestCase):
    def setUp(self):
        self.tool = DeleteFileTool()
        self.test_filename = "test_file_for_delete.txt"
        with open(self.test_filename, "w") as f:
            f.write("This is a test file.")

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_run_deletes_file(self):
        # Act
        result = self.tool.run(filename=self.test_filename)
        
        # Assert
        self.assertEqual(result, f"Successfully deleted file: {self.test_filename}")
        self.assertFalse(os.path.exists(self.test_filename))

    def test_run_on_nonexistent_file(self):
        # Arrange
        non_existent_file = "non_existent_file.txt"
        
        # Act
        result = self.tool.run(filename=non_existent_file)
        
        # Assert
        self.assertEqual(result, f"File not found: {non_existent_file}")

if __name__ == '__main__':
    unittest.main()
