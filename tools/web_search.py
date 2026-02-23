from tools.base import AgentTool

try:
    from duckduckgo_search import DDGS
except ModuleNotFoundError:  # pragma: no cover - exercised via runtime environment
    DDGS = None

class WebSearchTool(AgentTool):
    def name(self) -> str:
        return "web_search"

    def description(self) -> str:
        return "Search the web for a given query and returns the top results. Use this to find information on topics you don't know about, or to find solutions to problems."

    def args(self) -> dict:
        return {"query": str}

    def run(self, query: str) -> str:
        """
        Searches the web with the given query and returns the top results.
        """
        try:
            if DDGS is None:
                return "Web search dependency not installed. Install 'duckduckgo-search' to use this tool."

            # DDGS context manager for clean session handling
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                if not results:
                    return "No results found."

                # Format the results into a string
                formatted_results = []
                for i, result in enumerate(results):
                    formatted_results.append(
                        f"Result {i+1}:\n"
                        f"  Title: {result.get('title', 'N/A')}\n"
                        f"  URL: {result.get('href', 'N/A')}\n"
                        f"  Snippet: {result.get('body', 'N/A')}"
                    )
                return "\n".join(formatted_results)
        except Exception as e:
            return f"An error occurred during the web search: {e}"
