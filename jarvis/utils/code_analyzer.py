"""
Code Analysis Module for JARVIS
-----------------------------
This module provides code analysis capabilities using Ollama's AI models.
It's designed to work with the JARVIS assistant for code-related tasks.
"""

import subprocess
import json
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """
    A class to handle code analysis using Ollama's AI models.
    """
    
    def __init__(self, model: str = "codellama:7b-instruct"):
        """
        Initialize the CodeAnalyzer with a specific model.
        
        Args:
            model (str): The Ollama model to use for code analysis.
                        Default is 'codellama:7b-instruct'.
        """
        self.model = model
        self.available_models = self._get_available_models()
        
    def _get_available_models(self) -> List[str]:
        """Get list of available Ollama models."""
        try:
            result = subprocess.run(
                ["ollama", "list", "--json"],
                capture_output=True,
                text=True,
                check=True
            )
            models = json.loads(result.stdout)
            return [m['name'] for m in models]
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.warning(f"Could not fetch available models: {e}")
            return []
    
    def analyze_code(self, code: str, task: str = "analyze") -> str:
        """
        Analyze code using the specified Ollama model.
        
        Args:
            code (str): The code to analyze.
            task (str): The type of analysis to perform.
                       Options: 'analyze', 'explain', 'optimize', 'debug'.
                       
        Returns:
            str: The analysis result from the model.
        """
        prompt = self._build_prompt(code, task)
        
        try:
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                input=code,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_msg = f"Error running code analysis: {e.stderr}"
            logger.error(error_msg)
            return error_msg
    
    def _build_prompt(self, code: str, task: str) -> str:
        """Build the prompt for the AI model based on the task."""
        task_prompts = {
            "analyze": "Analyze the following code and provide insights:\n\n",
            "explain": "Explain how this code works:\n\n",
            "optimize": "Optimize the following code and explain the improvements:\n\n",
            "debug": "Find and fix any bugs in this code. Explain the issues and solutions:\n\n",
            "document": "Generate documentation for this code:\n\n"
        }
        
        base_prompt = task_prompts.get(task.lower(), "Analyze this code:\n\n")
        return f"[INST] {base_prompt}{code} [/INST]"
    
    def get_model_info(self) -> Dict:
        """Get information about the current model and available models."""
        return {
            "current_model": self.model,
            "available_models": self.available_models,
            "gpu_enabled": self._check_gpu()
        }
    
    def _check_gpu(self) -> Tuple[bool, str]:
        """Check if GPU is available for PyTorch."""
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            gpu_name = torch.cuda.get_device_name(0) if cuda_available else "No GPU"
            return cuda_available, gpu_name
        except ImportError:
            return False, "PyTorch not installed"

def test_code_analysis():
    """Test the code analysis functionality."""
    analyzer = CodeAnalyzer()
    
    # Test code
    test_code = """
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    """
    
    print("=== Testing Code Analysis ===")
    print("Model Info:", analyzer.get_model_info())
    
    print("\n=== Code Explanation ===")
    print(analyzer.analyze_code(test_code, "explain"))
    
    print("\n=== Code Optimization ===")
    print(analyzer.analyze_code(test_code, "optimize"))

if __name__ == "__main__":
    test_code_analysis()
