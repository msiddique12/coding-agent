import os
import unittest

from tools.append_file import AppendFileTool


class TestAppendFileTool(unittest.TestCase):
    def setUp(self):
        self.filename = "test_append_file.txt"
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("start\n")
        self.tool = AppendFileTool()

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_append_content(self):
        result = self.tool.run(self.filename, "end\n")
        self.assertIn("Appended", result)
        with open(self.filename, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "start\nend\n")


if __name__ == "__main__":
    unittest.main()
