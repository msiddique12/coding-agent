import unittest
from tools.shell_command import ShellCommandTool

class TestShellCommandTool(unittest.TestCase):
    def setUp(self):
        self.tool = ShellCommandTool()

    def test_run_simple_command(self):
        # Arrange
        command = 'echo "Hello, shell!"'
        
        # Act
        result = self.tool.run(command=command)
        
        # Assert
        self.assertIn("Hello, shell!", result)
        self.assertIn("STDOUT:", result)

    def test_run_command_with_error(self):
        # Arrange
        command = 'ls non_existent_directory'
        
        # Act
        result = self.tool.run(command=command)
        
        # Assert
        self.assertIn("failed", result)
        self.assertIn("STDERR:", result)
        self.assertIn("No such file or directory", result)

if __name__ == '__main__':
    unittest.main()
