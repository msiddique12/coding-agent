from .base import AgentTool

class FinishTool(AgentTool):
    def name(self):
        return "finish"
    
    def description(self):
        return "Signal that the task is complete and provide the final answer."
    
    def args(self):
        return {"answer": str}
    
    def run(self, answer: str):
        return f"Task complete. Final Answer: {answer}"
