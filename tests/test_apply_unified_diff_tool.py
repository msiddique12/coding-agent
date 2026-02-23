import os
import shutil
import unittest

from tools.apply_unified_diff import UnifiedDiffApplyTool


class TestApplyUnifiedDiffTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tmp_patch_tool"
        os.makedirs(self.test_dir, exist_ok=True)
        self.tool = UnifiedDiffApplyTool()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _write(self, rel, content):
        path = os.path.join(self.test_dir, rel)
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def _read(self, rel):
        with open(os.path.join(self.test_dir, rel), "r", encoding="utf-8") as f:
            return f.read()

    def test_apply_modify_patch(self):
        self._write("a.txt", "one\ntwo\nthree\n")
        patch = """--- a/tmp_patch_tool/a.txt
+++ b/tmp_patch_tool/a.txt
@@ -1,3 +1,3 @@
 one
-two
+TWO
 three
"""
        result = self.tool.run(patch=patch)
        self.assertIn("Patch applied successfully", result)
        self.assertEqual(self._read("a.txt"), "one\nTWO\nthree\n")

    def test_rejects_context_mismatch_without_partial_write(self):
        self._write("a.txt", "one\ntwo\nthree\n")
        patch = """--- a/tmp_patch_tool/a.txt
+++ b/tmp_patch_tool/a.txt
@@ -1,3 +1,3 @@
 one
-wrong
+TWO
 three
"""
        result = self.tool.run(patch=patch)
        self.assertIn("Patch apply failed", result)
        self.assertEqual(self._read("a.txt"), "one\ntwo\nthree\n")

    def test_apply_create_and_delete(self):
        self._write("gone.txt", "bye\n")
        patch = """--- /dev/null
+++ b/tmp_patch_tool/new.txt
@@ -0,0 +1,2 @@
+hello
+world
--- a/tmp_patch_tool/gone.txt
+++ /dev/null
@@ -1,1 +0,0 @@
-bye
"""
        result = self.tool.run(patch=patch)
        self.assertIn("Patch applied successfully", result)
        self.assertEqual(self._read("new.txt"), "hello\nworld\n")
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, "gone.txt")))


if __name__ == "__main__":
    unittest.main()
