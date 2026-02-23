import os
import unittest

from tools.replace_in_file import ReplaceInFileTool


class TestReplaceInFileTool(unittest.TestCase):
    def setUp(self):
        self.filename = "test_replace_in_file.txt"
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("hello world\nhello world\n")
        self.tool = ReplaceInFileTool()

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_requires_specific_match_when_multiple(self):
        result = self.tool.run(self.filename, "hello", "hi")
        self.assertIn("replace_all=true", result)

    def test_replace_single_occurrence(self):
        result = self.tool.run(self.filename, "hello world\nhello", "hi world\nhello")
        self.assertIn("Replaced 1 occurrence", result)
        with open(self.filename, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content.count("hi world"), 1)
        self.assertEqual(content.count("hello world"), 1)

    def test_replace_all_occurrences(self):
        result = self.tool.run(self.filename, "hello world", "hi world", replace_all=True)
        self.assertIn("Replaced 2 occurrence", result)
        with open(self.filename, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("hello world", content)


if __name__ == "__main__":
    unittest.main()
