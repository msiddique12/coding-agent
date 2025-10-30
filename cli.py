import argparse
from agent.agent import CodingAgent

def main():
    parser = argparse.ArgumentParser(description="CLI Coding Agent (Modular LLM Client)")
    parser.add_argument("--provider", choices=["nim", "huggingface"], default="nim", help="LLM provider to use")
    parser.add_argument("command", choices=["ask"], help="Supported command")
    parser.add_argument("prompt", help="Prompt to send to the LLM")
    args = parser.parse_args()

    agent = CodingAgent(provider_name=args.provider)
    if args.command == "ask":
        response = agent.get_response(args.prompt)
        print("LLM Response:", response)

if __name__ == "__main__":
    main()
