import os
import unittest

from tools.read_file import ReadFileTool


class TestReadFileTool(unittest.TestCase):
    def setUp(self):
        self.filename = "test_read_file_tool.txt"
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("a\nb\nc\n")
        self.tool = ReadFileTool()

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_read_whole_file(self):
        result = self.tool.run(self.filename)
        self.assertIn("Lines: 1-3 of 3", result)
        self.assertIn("1 | a", result)
        self.assertIn("3 | c", result)

    def test_read_range(self):
        result = self.tool.run(self.filename, start_line=2, end_line=2)
        self.assertIn("Lines: 2-2 of 3", result)
        self.assertIn("2 | b", result)
        self.assertNotIn("1 | a", result)


if __name__ == "__main__":
    unittest.main()
