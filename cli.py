import argparse

def main():
    parser = argparse.ArgumentParser(
        description="CLI Coding Agent"
    )
    
    parser.add_argument(
        'command',
        choices=['ask', 'run'],
        help="Choose 'ask' to request code, or 'run' to execute code."
    )
    
    parser.add_argument(
        'prompt',
        nargs='?',
        help="Choose 'ask' to request code, or 'run' to execute code."
    )
    
    args = parser.parse_args()
    
    if args.command == 'ask':
        print(f"Prompt for code: {args.prompt}")
        #Call Agent
    elif args.command == 'run':
        print("Code execution feature to be implemented")
        
if __name__ == "main":
    main()
    
    