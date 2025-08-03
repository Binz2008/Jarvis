from .ai_task_router import AITaskRouter
import time

# This is a mock function to simulate calling an AI model API
def call_model_api(model_name, prompt):
    """Mock function to simulate an API call to an AI model."""
    print(f"--> Attempting to call model: {model_name}")
    
    # Simulate failures for certain models to test fallback
    if 'specialized_trading_model_v2' in model_name or 'deepseek-coder' in model_name:
        print(f"<-- MOCK FAILURE: Model '{model_name}' is currently unavailable.")
        return None # Simulate API failure
    
    # Simulate a successful response
    time.sleep(1) # Simulate network latency
    response = f"Response from '{model_name}': The prompt was '{prompt[:30]}...'"
    print(f"<-- Success from model: {model_name}")
    return response

class FallbackAIManager:
    """Manages the execution of AI tasks with a fallback mechanism."""

    def execute_task(self, task_config: dict, prompt: str) -> str:
        """
        Executes a task using the primary model, and uses fallback models if it fails.

        Args:
            task_config (dict): The configuration for the task, including primary and fallback models.
            prompt (str): The user's input prompt.

        Returns:
            str: The response from a successful model call, or an error message.
        """
        primary_model = task_config.get('primary_model')
        fallback_models = task_config.get('fallback_models', [])

        # 1. Try the primary model first
        if primary_model:
            response = call_model_api(primary_model, prompt)
            if response:
                return response
            else:
                print(f"--- Primary model '{primary_model}' failed. Initiating fallback sequence. ---")
        else:
            print("--- No primary model defined. Proceeding directly to fallbacks. ---")

        # 2. If primary fails or doesn't exist, iterate through fallback models
        for fallback_model in fallback_models:
            response = call_model_api(fallback_model, prompt)
            if response:
                return response
        
        # 3. If all models fail
        print("!!! All primary and fallback models failed to provide a response.")
        return "Error: All available AI models failed to process the request."

# Example Usage (for testing purposes)
if __name__ == '__main__':
    router = AITaskRouter()
    manager = FallbackAIManager()

    print("========= TEST CASE 1: Code Analysis (Primary OK) =========")
    prompt1 = "analyze this python code"
    config1 = router.route_task(prompt1)
    result1 = manager.execute_task(config1, prompt1)
    print(f"\nFINAL RESULT: {result1}\n" + "="*50 + "\n")

    print("========= TEST CASE 2: Trading Signal (Primary Fails, Fallback OK) =========")
    prompt2 = "give me a btc signal"
    config2 = router.route_task(prompt2)
    result2 = manager.execute_task(config2, prompt2)
    print(f"\nFINAL RESULT: {result2}\n" + "="*50 + "\n")

    print("========= TEST CASE 3: General Chat (Default Task) =========")
    prompt3 = "Hello there!"
    config3 = router.route_task(prompt3)
    result3 = manager.execute_task(config3, prompt3)
    print(f"\nFINAL RESULT: {result3}\n" + "="*50 + "\n")
