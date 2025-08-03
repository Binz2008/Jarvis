import yaml
import os

class AITaskRouter:
    """Routes user prompts to the appropriate AI task based on configuration."""

    def __init__(self, config_path=None):
        """
        Initializes the router and loads the configuration file.

        Args:
            config_path (str, optional): Path to the YAML config file. 
                                         Defaults to a path relative to this file.
        """
        if config_path is None:
            # Default path assumes config is at F:\A+\Jarvis\jarvis_config.yaml
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(base_dir, 'jarvis_config.yaml')

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        if not self.config or 'tasks' not in self.config:
            raise ValueError("Invalid configuration: 'tasks' section is missing.")

    def route_task(self, prompt: str) -> dict:
        """
        Determines the appropriate task for a given prompt.

        Args:
            prompt (str): The user's input prompt.

        Returns:
            dict: The configuration dictionary for the matched task.
        """
        prompt_lower = prompt.lower()

        for task_name, task_config in self.config['tasks'].items():
            for keyword in task_config.get('routing_keywords', []):
                if keyword.lower() in prompt_lower:
                    print(f"Routing to task: {task_name}")
                    return task_config

        # If no specific task is matched, return the default task config
        default_task_name = self.config.get('default_task', 'general_chat')
        print(f"No specific keywords matched. Routing to default task: {default_task_name}")
        return self.config['tasks'].get(default_task_name, {})

# Example Usage (for testing purposes)
if __name__ == '__main__':
    # This assumes the script is run from a directory where the relative path to config works
    # For direct execution, you might need to provide an absolute path to AITaskRouter
    try:
        router = AITaskRouter()

        prompt1 = "Can you analyze this piece of code for me?"
        task1_config = router.route_task(prompt1)
        print(f"Prompt: '{prompt1}' -> Config: {task1_config}\n")

        prompt2 = "مرحبا، كيف حالك اليوم؟"
        task2_config = router.route_task(prompt2)
        print(f"Prompt: '{prompt2}' -> Config: {task2_config}\n")

        prompt3 = "What's the weather like?"
        task3_config = router.route_task(prompt3)
        print(f"Prompt: '{prompt3}' -> Config: {task3_config}\n")

        prompt4 = "I need a trading signal for BTC."
        task4_config = router.route_task(prompt4)
        print(f"Prompt: '{prompt4}' -> Config: {task4_config}\n")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error during initialization: {e}")
