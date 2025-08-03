import sys
import os

# Fix for running the script directly. Adds the parent directory to the Python path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



"""
Main entry point for the Jarvis personal assistant.
"""
import argparse
import asyncio
from . import Jarvis

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Jarvis - Your Personal Assistant')
    parser.add_argument('--name', type=str, default='Jarvis',
                      help='Name of your assistant')
    parser.add_argument('--version', action='version', 
                      version=f'%(prog)s {Jarvis.__version__}')
    return parser.parse_args()

async def main():
    """Run the Jarvis assistant."""
    args = parse_arguments()
    try:
        assistant = Jarvis.Jarvis(args.name)
        print(assistant.greet())
    except Exception as e:
        print(f"Critical Error during Jarvis initialization: {e}")
        import traceback
        traceback.print_exc()
        return

    while True:
            prompt = input("\nYou: ")
            if prompt.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            response = await assistant.process_user_prompt(prompt)
            print(f"Jarvis: {response}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nJarvis shutting down.")
