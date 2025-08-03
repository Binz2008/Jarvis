print("--- Script starting ---", flush=True)
import sys
import os

# Add the project root to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now that the path is set, we can import our modules
from jarvis.ai.ai_task_router import AITaskRouter
from jarvis.ai.fallback_ai_manager import FallbackAIManager

def run_tests():
    """Runs a series of tests on the AI routing and fallback system."""
    try:
        print("--- Initializing router and manager ---", flush=True)
        router = AITaskRouter()
        manager = FallbackAIManager()
        print("--- Initialization complete ---", flush=True)

        print("\n========= TEST CASE 1: Code Analysis (Primary OK) =========", flush=True)
        prompt1 = "analyze this python code"
        config1 = router.route_task(prompt1)
        result1 = manager.execute_task(config1, prompt1)
        print(f"\nFINAL RESULT: {result1}\n" + "="*50 + "\n", flush=True)

        print("========= TEST CASE 2: Trading Signal (Primary Fails, Fallback OK) =========", flush=True)
        prompt2 = "give me a btc signal"
        config2 = router.route_task(prompt2)
        result2 = manager.execute_task(config2, prompt2)
        print(f"\nFINAL RESULT: {result2}\n" + "="*50 + "\n", flush=True)

        print("========= TEST CASE 3: General Chat (Default Task) =========", flush=True)
        prompt3 = "Hello there!"
        config3 = router.route_task(prompt3)
        result3 = manager.execute_task(config3, prompt3)
        print(f"\nFINAL RESULT: {result3}\n" + "="*50 + "\n", flush=True)

        print("========= TEST CASE 4: Code Analysis in Arabic (Keyword Match) =========", flush=True)
        prompt4 = "ممكن مراجعة الكود هذا؟"
        config4 = router.route_task(prompt4)
        result4 = manager.execute_task(config4, prompt4)
        print(f"\nFINAL RESULT: {result4}\n" + "="*50 + "\n", flush=True)

    except (FileNotFoundError, ValueError) as e:
        print(f"An error occurred during testing: {e}", flush=True)

if __name__ == '__main__':
    print("--- Entering main execution block ---", flush=True)
    run_tests()
    print("--- Exiting main execution block ---", flush=True)

