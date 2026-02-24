from llm_providers import get_llm_client
from utils.filesystem import list_code_files, read_file
import logging
import os

from tools.code_search import CodeSearchTool
from tools.file_search import FileSearchTool
from tools.summarize import FileSummarizeTool
from tools.todo_finder import ToDoFinderTool
from tools.code_edit import CodeEditTool
from tools.git_tools import GitStatusTool, GitDiffTool, GitAddTool, GitCommitTool
from tools.run_tests import RunTestsTool
from tools.suggest_test_commands import SuggestTestCommandsTool
from tools.finish import FinishTool
from tools.create_file import CreateFileTool
from tools.apply_unified_diff import UnifiedDiffApplyTool
from tools.append_file import AppendFileTool
from tools.delete_file import DeleteFileTool
from tools.read_file import ReadFileTool
from tools.replace_in_file import ReplaceInFileTool
from tools.shell_command import ShellCommandTool
from tools.web_search import WebSearchTool

log_dir = "logs"
os.makedirs(log_dir, exist_ok = True)
logging.basicConfig(
    filename=os.path.join(log_dir, "agent.log"),
    filemode="a",
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO
)

class CodingAgent:
    def __init__(self, provider_name="nim"):
        # Use the provider factory so tests can inject a dummy provider
        self.llm = get_llm_client(provider_name)
        self.tools = {}
        self.unavailable_tools = {}
        self._load_tools()

    def _load_tools(self):
        tool_factories = [
            ("file_search", FileSearchTool),
            ("code_search", CodeSearchTool),
            ("summarize_file", FileSummarizeTool),
            ("todo_finder", ToDoFinderTool),
            ("code_edit", CodeEditTool),
            ("git_status", GitStatusTool),
            ("git_diff", GitDiffTool),
            ("git_add", GitAddTool),
            ("git_commit", GitCommitTool),
            ("run_tests", RunTestsTool),
            ("suggest_test_commands", SuggestTestCommandsTool),
            ("create_file", CreateFileTool),
            ("apply_unified_diff", UnifiedDiffApplyTool),
            ("append_file", AppendFileTool),
            ("delete_file", DeleteFileTool),
            ("read_file", ReadFileTool),
            ("replace_in_file", ReplaceInFileTool),
            ("shell_command", ShellCommandTool),
            ("web_search", WebSearchTool),
            ("finish", FinishTool),
        ]

        for tool_name, tool_cls in tool_factories:
            try:
                tool = tool_cls()
                self.tools[tool.name()] = tool
            except Exception as e:
                self.unavailable_tools[tool_name] = str(e)
                logging.warning("Skipping unavailable tool %s: %s", tool_name, e)

    def get_response(self, prompt: str) -> str:
        logging.info(f"Provider: {type(self.llm).__name__}, Prompt: {prompt!r}")
        response = self.llm.query(prompt)
        logging.info(f"Response: {response!r}")
        return response

    def list_files(self):
        return list_code_files()
    
    def summarize_readme(self):
        if not os.path.exists("README.md"):
            return "No README.md found in the current directory."
        content = read_file("README.md")
        prompt = f"Summarize the following README.md for quick project understanding:\n\n{content}"
        return self.get_response(prompt)
    
    def summarize_file(self, fp):
        if not os.path.exists(fp):
            return f"File {fp} does not exist!"
        content = read_file(fp)
        prompt = f"Summarize this file with a focus on key purpose and usage:\n\n{content}"
        return self.get_response(prompt)
    
    def use_tool(self, tool_name, **kwargs):
        tool = self.tools.get(tool_name)
        if not tool:
            unavailable_reason = self.unavailable_tools.get(tool_name)
            if unavailable_reason:
                raise ValueError(f"Tool '{tool_name}' is unavailable: {unavailable_reason}")
            raise ValueError(f"Tool '{tool_name}' not found.")
        return tool.run(**kwargs)
    
    def list_tools(self):
        return {name: tool.description() for name, tool in self.tools.items()}

    def get_tool_status(self):
        return {
            "available": self.list_tools(),
            "unavailable": dict(self.unavailable_tools),
        }
        
        
