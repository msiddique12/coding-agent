import argparse
import json
import os
from dotenv import load_dotenv
from rich.console import Console
from llm_providers import supported_provider_names, validate_provider_environment

load_dotenv()
console = Console()
DEFAULT_SESSION_FILE = os.path.join(".coding-agent", "session.json")


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


def _default_provider() -> str:
    return os.getenv("LLM_PROVIDER", "openai")


def _load_session(session_file: str):
    with open(session_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "goal" not in data:
        raise ValueError("Invalid session file format")
    data.setdefault("history", [])
    return data


def _save_session(session_file: str, state: dict):
    parent = os.path.dirname(session_file)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Context-aware CLI Coding Agent")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    providers = supported_provider_names()

    parser_run = subparsers.add_parser("run", help="Run the autonomous coding agent on a goal")
    parser_run.add_argument("--provider", choices=providers, default=_default_provider(), help="LLM provider")
    parser_run.add_argument("--max-turns", type=int, default=10, help="Maximum agent reasoning turns")
    parser_run.add_argument("--auto-approve", action="store_true", help="Auto-approve dangerous tools (tests/shell/edit/git)")
    parser_run.add_argument("--session-file", default=DEFAULT_SESSION_FILE, help="Path to save resumable session state")
    parser_run.add_argument("prompt", help="Coding goal for the autonomous agent")

    parser_ask = subparsers.add_parser("ask", help="Alias for 'run'")
    parser_ask.add_argument("--provider", choices=providers, default=_default_provider(), help="LLM provider")
    parser_ask.add_argument("--max-turns", type=int, default=10, help="Maximum agent reasoning turns")
    parser_ask.add_argument("--auto-approve", action="store_true", help="Auto-approve dangerous tools (tests/shell/edit/git)")
    parser_ask.add_argument("--session-file", default=DEFAULT_SESSION_FILE, help="Path to save resumable session state")
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
    parser_tools = subparsers.add_parser("tools", help="List available and unavailable tools")
    parser_tools.add_argument(
        "--provider",
        choices=providers,
        default="dummy",
        help="Provider used to initialize the agent while listing tools",
    )
    parser_resume = subparsers.add_parser("resume", help="Resume the last saved autonomous session")
    parser_resume.add_argument("--provider", choices=providers, default=_default_provider(), help="LLM provider")
    parser_resume.add_argument("--max-turns", type=int, default=10, help="Maximum additional agent reasoning turns")
    parser_resume.add_argument("--auto-approve", action="store_true", help="Auto-approve dangerous tools (tests/shell/edit/git)")
    parser_resume.add_argument("--session-file", default=DEFAULT_SESSION_FILE, help="Path to saved session state")

    args = parser.parse_args()

    if args.subcommand == "doctor":
        raise SystemExit(_print_doctor(args.provider))

    if args.subcommand == "index":
        from indexing.indexer import CodeIndexer

        indexer = CodeIndexer()
        indexer.index_project()
        return

    if args.subcommand == "tools":
        try:
            from agent.agent import CodingAgent
            agent = CodingAgent(provider_name=args.provider)
        except Exception as e:
            console.print(f"[red]Unable to load tools: {e}[/red]")
            raise SystemExit(2)

        status = agent.get_tool_status()
        console.print("[bold green]Available tools[/bold green]")
        for name, desc in status["available"].items():
            console.print(f"- [bold]{name}[/bold]: {desc}")
        if status["unavailable"]:
            console.print("[bold yellow]Unavailable tools[/bold yellow]")
            for name, reason in status["unavailable"].items():
                console.print(f"- [bold]{name}[/bold]: {reason}")
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

    max_turns = max(1, getattr(args, "max_turns", 10))
    auto_approve = bool(getattr(args, "auto_approve", False))
    orchestrator = Orchestrator(agent, max_turns=max_turns, auto_approve=auto_approve)
    
    if args.subcommand in {"ask", "run"}:
        console.print(f"[bold white]User:[/bold white] {args.prompt}")
        state = orchestrator.run_with_state(args.prompt)
        _save_session(args.session_file, state)
        console.print(f"[dim]Session saved to {args.session_file}[/dim]")
        response = state["final_answer"]
        console.print(f"[green]Agent:[/green] {response}")
    elif args.subcommand == "resume":
        try:
            prior = _load_session(args.session_file)
        except Exception as e:
            console.print(f"[red]Failed to load session: {e}[/red]")
            raise SystemExit(2)
        console.print(f"[bold white]Resuming goal:[/bold white] {prior['goal']}")
        state = orchestrator.run_with_state(prior["goal"], history=prior.get("history", []))
        _save_session(args.session_file, state)
        console.print(f"[dim]Session saved to {args.session_file}[/dim]")
        console.print(f"[green]Agent:[/green] {state['final_answer']}")
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
