import asyncio
import sys
import os

# Add project root to the path to allow running from any directory
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jarvis import Jarvis

async def run_test():
    """Initializes Jarvis and tests a simple prompt."""
    print("--- Jarvis Integration Test ---")
    try:
        assistant = Jarvis("TestRunner")
        print(assistant.greet())
        
        prompt = "hello what is the capital of france"
        print(f"\n[User]: {prompt}")
        
        response = await assistant.process_user_prompt(prompt)
        print(f"\n[Jarvis]: {response}")
        
    except Exception as e:
        print(f"\nAn error occurred during the test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n--- Test Complete ---")

if __name__ == "__main__":
    asyncio.run(run_test())
