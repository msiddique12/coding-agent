import argparse
from agent.agent import CodingAgent
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()

def main():
    parser = argparse.ArgumentParser(description="Context-aware CLI Coding Agent")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    
    parser_ask = subparsers.add_parser("ask", help="Ask a question to the agent")
    parser_ask.add_argument("--provider", choices=["nim"], default="nim", help="LLM provider") #add more providers later
    parser_ask.add_argument("prompt")
    
    parser_list = subparsers.add_parser("list-files", help="List tracked code and doc files")
    
    parser_sum_readme = subparsers.add_parser("summarize-readme", help="Summarize the README.md in current folder")
    parser_sum_file = subparsers.add_parser("summarize-file", help="Summarize a specific file")
    parser_sum_file.add_argument("file_path")
    
    args = parser.parse_args()
    agent = CodingAgent(provider_name=getattr(args, "provider", "nim"))
    
    if args.subcommand == "ask":
        console.print(f"[bold white]User:[/bold white] {args.prompt}")
        response = agent.get_response(args.prompt)
        console.print(f"[green]Agent:[/green] {response}")
    elif args.subcommand == "list-files":
        files = agent.list_files()
        console.print("[bold yellow]Project Files:[/bold yellow]")
        for f in files:
            console.print(f"- [bold]{f}[/bold]")
    elif args.subcommand == "summarize-readme":
        summary = agent.summarize_readme()
        console.print(f"[blue]README summary:[/blue]\n{summary}")
    elif args.subcommand == "summarize-file":
        summary = agent.summarize_file(args.file_path)
        console.print(f"[blue]File summary:[/blue]\n{summary}")

if __name__ == "__main__":
    main()
