import unittest
import os
import shutil
import subprocess
from tools.git_tools import GitStatusTool, GitDiffTool, GitAddTool, GitCommitTool

class TestGitTools(unittest.TestCase):
    def setUp(self):
        self.test_dir = "temp_git_test_dir"
        os.makedirs(self.test_dir, exist_ok=True)
        os.chdir(self.test_dir)

        # Initialize a new git repository
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], capture_output=True)


        self.status_tool = GitStatusTool()
        self.diff_tool = GitDiffTool()
        self.add_tool = GitAddTool()
        self.commit_tool = GitCommitTool()

    def tearDown(self):
        os.chdir("..")
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_git_status_tool(self):
        # Arrange
        with open("test_file.txt", "w") as f:
            f.write("initial content")

        # Act
        result = self.status_tool.run()

        # Assert
        self.assertIn("Untracked files", result)
        self.assertIn("test_file.txt", result)

    def test_git_add_and_commit_tools(self):
        # Arrange
        filename = "new_file.txt"
        with open(filename, "w") as f:
            f.write("content to be committed")

        # Act (Add)
        add_result = self.add_tool.run(files=filename)
        
        # Assert (Add)
        self.assertIn("Exit Code: 0", add_result)
        status_after_add = self.status_tool.run()
        self.assertIn("Changes to be committed", status_after_add)
        self.assertIn(filename, status_after_add)

        # Act (Commit)
        commit_message = "Test commit"
        commit_result = self.commit_tool.run(message=commit_message)

        # Assert (Commit)
        self.assertIn("Exit Code: 0", commit_result)
        log_result = subprocess.run(["git", "log", "-1"], capture_output=True, text=True)
        self.assertIn(commit_message, log_result.stdout)

    def test_git_diff_tool(self):
        # Arrange
        filename = "diff_test.txt"
        with open(filename, "w") as f:
            f.write("line 1\n")
        self.add_tool.run(files=filename)
        self.commit_tool.run(message="Initial commit for diff test")

        with open(filename, "a") as f:
            f.write("line 2\n")

        # Act
        result = self.diff_tool.run(path=filename)

        # Assert
        self.assertIn("Exit Code: 0", result)
        self.assertIn("+line 2", result)

if __name__ == '__main__':
    unittest.main()
