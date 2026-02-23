import argparse
from dotenv import load_dotenv
from rich.console import Console
from llm_providers import supported_provider_names, validate_provider_environment

load_dotenv()
console = Console()


def _print_doctor(provider: str):
    result = validate_provider_environment(provider)
    if result["ok"]:
        console.print(f"[green]Provider '{provider}' is configured.[/green]")
        return 0

    if not result["supported"]:
        console.print(f"[red]{result['message']}[/red]")
        return 2

    console.print(f"[yellow]Provider '{provider}' is not ready.[/yellow]")
    console.print(f"[yellow]{result['message']}[/yellow]")
    return 1


def main():
    parser = argparse.ArgumentParser(description="Context-aware CLI Coding Agent")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    providers = supported_provider_names()

    parser_ask = subparsers.add_parser("ask", help="Ask a question to the agent")
    parser_ask.add_argument("--provider", choices=providers, default="nim", help="LLM provider")
    parser_ask.add_argument("prompt")
    
    parser_list = subparsers.add_parser("list-files", help="List tracked code and doc files")
    
    parser_sum_readme = subparsers.add_parser("summarize-readme", help="Summarize the README.md in current folder")
    parser_sum_file = subparsers.add_parser("summarize-file", help="Summarize a specific file")
    parser_sum_file.add_argument("file_path")
    
    parser_greet = subparsers.add_parser("greet", help="Greet a person by name")
    parser_greet.add_argument("--name", required=True, help="Name of the person to greet")

    parser_index = subparsers.add_parser("index", help="Create or update the semantic index for the project")
    parser_doctor = subparsers.add_parser("doctor", help="Check API key configuration for a provider")
    parser_doctor.add_argument("--provider", choices=providers, default="openai", help="Provider to validate")

    args = parser.parse_args()

    if args.subcommand == "doctor":
        raise SystemExit(_print_doctor(args.provider))

    if args.subcommand == "index":
        from indexing.indexer import CodeIndexer

        indexer = CodeIndexer()
        indexer.index_project()
        return

    provider_name = getattr(args, "provider", "nim")
    try:
        from agent.agent import CodingAgent
        from agent.orchestrator import Orchestrator

        agent = CodingAgent(provider_name=provider_name)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        console.print(
            "[yellow]Run `python cli.py doctor --provider "
            f"{provider_name}` to verify environment variables.[/yellow]"
        )
        raise SystemExit(2)
    except ModuleNotFoundError as e:
        console.print(f"[red]Missing dependency: {e.name}[/red]")
        console.print("[yellow]Install project dependencies first: `pip install -r requirements.txt`[/yellow]")
        raise SystemExit(2)

    orchestrator = Orchestrator(agent)
    
    if args.subcommand == "ask":
        console.print(f"[bold white]User:[/bold white] {args.prompt}")
        response = orchestrator.run(args.prompt)
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
    elif args.subcommand == "greet":
        console.print(f"[magenta]Hello, {args.name}![/magenta]")

if __name__ == "__main__":
    main()
