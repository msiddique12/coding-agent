from typing import Any, Dict

class AgentTool:
    def name(self) -> str:
        """Return tool name."""
        raise NotImplementedError
    
    def description(self) -> str:
        """Return what the tool does."""
        raise NotImplementedError
    
    def args(self) -> dict:
        """Return dict of named params and types(for agent utilization)"""
        return {}
    
    def run(self, **kwargs) -> Any:
        """Run the tool with provided arguments."""
        raise NotImplementedError
    
        