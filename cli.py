import argparse
from agent.agent import CodingAgent
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()

def main():
    parser = argparse.ArgumentParser(description="CLI Coding Agent (Modular LLM Client)")
    parser.add_argument("--provider", choices=["nim", "huggingface"], default="nim", help="LLM provider to use")
    parser.add_argument("command", choices=["ask"], help="Supported command")
    parser.add_argument("prompt", help="Prompt to send to the LLM")
    args = parser.parse_args()

    agent = CodingAgent(provider_name=args.provider)
    console.print(f"[bold blue]Provider:[/bold blue] {args.provider} | [bold]Model:[/bold] {getattr(agent.llm, 'model', 'unknown')}", style="bold cyan")
    
    if args.command == "ask":
        console.print(f"[bold white]User:[/bold white] {args.prompt}\n", style="bold")
        response = agent.get_response(args.prompt)
        if "error" in response.lower():
            console.print(f"[red]Agent Error:[/red] {response}")
        else:
            console.print(f"[green]Agent:[/green] {response}")

if __name__ == "__main__":
    main()
