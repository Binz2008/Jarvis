"""
Fallback AI Manager for JARVIS
----------------------------
This module provides fallback mechanisms and error handling for AI model interactions.
It ensures robust operation by automatically falling back to alternative models when needed.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union
from dataclasses import dataclass
import httpx
import json
from ...utils.config import config
from ...utils.logger import logger as jarvis_logger

logger = jarvis_logger.getChild('fallback_manager')

# Type variables for generic function typing
T = TypeVar('T')

@dataclass
class ModelAttempt:
    """Represents an attempt to use a specific model."""
    model_name: str
    success: bool = False
    response: Any = None
    error: Optional[Exception] = None
    duration: float = 0.0
    retry_count: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'model_name': self.model_name,
            'success': self.success,
            'error': str(self.error) if self.error else None,
            'duration': self.duration,
            'retry_count': self.retry_count
        }

class FallbackAIManager:
    """
    Manages fallback logic between different AI models.
    Handles retries, timeouts, and fallback to alternative models.
    """

    LOG_FILE = 'jarvis_performance.log'

    def _log_performance_event(self, event: dict):
        """Append a JSON event to the log file."""
        import json, os
        event['timestamp'] = time.time()
        try:
            with open(self.LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Failed to write performance log: {e}")
    
    def __init__(self, tasks_config: Dict, max_retries: int = 2, timeout: float = 60.0):
        """
        Initialize the Fallback AI Manager.
        
        Args:
            tasks_config: A dictionary defining tasks and their model chains.
            max_retries: Maximum number of retry attempts per model.
            timeout: Maximum time (in seconds) to wait for a response.
        """
        self.tasks_config = tasks_config
        self.max_retries = max_retries
        self.timeout = timeout
        self.model_metrics = {}
        logger.info(f"FallbackAIManager initialized with {len(tasks_config)} tasks.")

    async def execute_task(self, task_name: str, prompt: str) -> str:
        """
        Executes a task by trying a chain of models until one succeeds.
        
        Args:
            task_name: The name of the task to execute.
            prompt: The user prompt for the task.
            
        Returns:
            The response from the first successful model, or an error message.
        """
        if task_name not in self.tasks_config:
            logger.error(f"Task '{task_name}' not found in configuration.")
            return f"Error: Task '{task_name}' is not configured."

        model_chain = self.tasks_config[task_name].get('models', [])
        if not model_chain:
            logger.error(f"No models configured for task '{task_name}'.")
            return f"Error: No models configured for task '{task_name}'."

        logger.info(f"Executing task '{task_name}' with model chain: {model_chain}")
        
        last_error = None
        
        for model_name in model_chain:
            model_client = await self._get_model_client(model_name)
            if not model_client:
                logger.warning(f"Skipping model '{model_name}' as no client is available.")
                continue

            for attempt in range(self.max_retries):
                start_time = time.time()
                try:
                    logger.info(f"Attempting to use model '{model_name}' (Attempt {attempt + 1}/{self.max_retries}).")
                    response = await model_client(model_name, prompt)
                    duration = time.time() - start_time
                    self.update_model_metrics(model_name, success=True, duration=duration)
                    logger.info(f"Successfully received response from '{model_name}' in {duration:.2f}s.")
                    return response
                except Exception as e:
                    duration = time.time() - start_time
                    last_error = e
                    self.update_model_metrics(model_name, success=False, duration=duration)
                    logger.warning(
                        f"Model '{model_name}' failed on attempt {attempt + 1}: {e}"
                    )
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(1)  # Wait before retrying
            
            logger.error(f"All retries for model '{model_name}' failed. Falling back to the next model.")

        final_error_message = f"Task '{task_name}' failed. All models in the chain failed. Last error: {last_error}"
        logger.critical(final_error_message)
        return final_error_message

    async def _get_model_client(self, model_name: str) -> Optional[Callable]:
        """
        Get the appropriate client function based on the model name prefix.
        """
        if model_name.startswith('ollama/'):
            return self._call_ollama
        if model_name.startswith('openai/'):
            return self._call_openai
        if model_name.startswith('anthropic/'):
            return self._call_anthropic
        if model_name.startswith('deepseek/'):
            return self._call_deepseek
        
        logger.warning(f"No client found for model provider: {model_name}")
        return None

    async def _call_ollama(self, model_name: str, prompt: str) -> str:
        """
        Call a model hosted by a local Ollama instance.
        """
        model_tag = model_name.split('/', 1)[1]
        ollama_url = config.OLLAMA_URL or "http://localhost:11434"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{ollama_url}/api/generate",
                json={"model": model_tag, "prompt": prompt, "stream": False}
            )
            response.raise_for_status()
            # The response is a stream of JSON objects, we need to parse the final one
            full_response = ""
            for line in response.text.splitlines():
                if line:
                    full_response = json.loads(line).get("response", "")
            return full_response

    async def _call_openai(self, model_name: str, prompt: str) -> str:
        """
        Call an OpenAI or OpenAI-compatible model.
        """
        model_tag = model_name.split('/', 1)[1]
        api_key = config.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")
            
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model_tag,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def _call_anthropic(self, model_name: str, prompt: str) -> str:
        """
        Call an Anthropic model.
        """
        model_tag = model_name.split('/', 1)[1]
        api_key = config.ANTHROPIC_API_KEY
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured.")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": model_tag,
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]

    async def _call_deepseek(self, model_name: str, prompt: str) -> str:
        """
        Call a DeepSeek model using their OpenAI-compatible API.
        """
        model_tag = model_name.split('/', 1)[1]
        api_key = config.DEEPSEEK_API_KEY
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is not configured.")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model_tag,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def _get_model_client(self, model_name: str) -> Optional[Callable]:
        """
        Get the appropriate client function based on the model name prefix.
        """
        if model_name.startswith('ollama/'):
            return self._call_ollama
        if model_name.startswith('openai/'):
            return self._call_openai
        if model_name.startswith('anthropic/'):
            return self._call_anthropic
        if model_name.startswith('deepseek/'):
            return self._call_deepseek
        
        logger.warning(f"No client found for model provider: {model_name}")
        return None

    async def _call_ollama(self, model_name: str, prompt: str) -> str:
        """
        Call a model hosted by a local Ollama instance.
        """
        model_tag = model_name.split('/', 1)[1]
        ollama_url = config.OLLAMA_URL or "http://localhost:11434"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{ollama_url}/api/generate",
                json={"model": model_tag, "prompt": prompt, "stream": False}
            )
            response.raise_for_status()
            # The response is a stream of JSON objects, we need to parse the final one
            full_response = ""
            for line in response.text.splitlines():
                if line:
                    full_response = json.loads(line).get("response", "")
            return full_response

    async def _call_openai(self, model_name: str, prompt: str) -> str:
        """
        Call an OpenAI or OpenAI-compatible model.
        """
        model_tag = model_name.split('/', 1)[1]
        api_key = config.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")
            
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model_tag,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def _call_anthropic(self, model_name: str, prompt: str) -> str:
        """
        Call an Anthropic model.
        """
        model_tag = model_name.split('/', 1)[1]
        api_key = config.ANTHROPIC_API_KEY
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured.")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": model_tag,
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]

    async def _call_deepseek(self, model_name: str, prompt: str) -> str:
        """
        Call a DeepSeek model using their OpenAI-compatible API.
        """
        model_tag = model_name.split('/', 1)[1]
        api_key = config.DEEPSEEK_API_KEY
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is not configured.")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model_tag,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    

    
    def update_model_metrics(self, model_name: str, success: bool, duration: float) -> None:
        """
        Update performance metrics for a model.
        
        Args:
            model_name: Name of the model
            success: Whether the operation was successful
            duration: Time taken for the operation
        """
        if model_name not in self.model_metrics:
            self.model_metrics[model_name] = {
                'total_attempts': 0,
                'successful_attempts': 0,
                'total_duration': 0.0,
                'last_used': 0.0
            }
        
        metrics = self.model_metrics[model_name]
        metrics['total_attempts'] += 1
        metrics['total_duration'] += duration
        metrics['last_used'] = time.time()
        
        if success:
            metrics['successful_attempts'] += 1
    
    def get_model_success_rate(self, model_name: str) -> float:
        """Get the success rate of a model (0.0 to 1.0)."""
        if model_name not in self.model_metrics or self.model_metrics[model_name]['total_attempts'] == 0:
            return 1.0  # Assume perfect if no data
        
        metrics = self.model_metrics[model_name]
        return metrics['successful_attempts'] / metrics['total_attempts']
    
    def get_fallback_chain(self, task_type: str) -> List[str]:
        """
        Get the fallback chain for a specific task type.
        
        Args:
            task_type: Type of task ('code', 'text', 'image', etc.)
            
        Returns:
            List of model names in order of preference
        """
        # Default to text chain if specific chain not found
        return self.fallback_chains.get(task_type, self.fallback_chains['text'])
    
    async def execute_with_fallback(
        self,
        task_func: Callable[[str, Any], T],
        task_type: str,
        *args,
        **kwargs
    ) -> Tuple[Optional[T], ModelAttempt]:
        """
        Execute a task with automatic fallback to alternative models.
        
        Args:
            task_func: Function to execute (takes model_name as first argument)
            task_type: Type of task ('code', 'text', 'image', etc.)
            *args: Additional arguments to pass to task_func
            **kwargs: Additional keyword arguments to pass to task_func
            
        Returns:
            Tuple of (result, model_attempt)
        """
        fallback_chain = self.get_fallback_chain(task_type)
        last_error = None
        last_model_used = None
        fallback_event_chain = []

        for model_idx, model_name in enumerate(fallback_chain):
            attempt = ModelAttempt(model_name=model_name)
            start_time = time.time()

            for retry in range(self.max_retries):
                attempt.retry_count = retry
                try:
                    # Execute the task with timeout
                    result = await asyncio.wait_for(
                        task_func(model_name, *args, **kwargs),
                        timeout=self.timeout
                    )
                    
                    # If we get here, the task was successful
                    attempt.duration = time.time() - start_time
                    attempt.success = True
                    attempt.response = result
                    self.update_model_metrics(model_name, True, attempt.duration)
                    # Log successful attempt
                    self._log_performance_event({
                        'event': 'model_attempt',
                        'model_name': model_name,
                        'success': True,
                        'duration': attempt.duration,
                        'retry_count': attempt.retry_count,
                        'task_type': task_type,
                        'fallback_chain': fallback_chain,
                        'fallback_index': model_idx
                    })
                    return result, attempt

                except asyncio.TimeoutError:
                    error_msg = f"Model {model_name} timed out after {self.timeout}s"
                    last_error = TimeoutError(error_msg)
                    attempt.error = last_error
                    logger.warning(f"{error_msg} (attempt {retry + 1}/{self.max_retries})")
                except Exception as e:
                    attempt.error = e
                    last_error = e
                    logger.warning(f"Model {model_name} failed (attempt {retry + 1}/{self.max_retries}): {e}")
                finally:
                    attempt.duration = time.time() - start_time
                    self.update_model_metrics(model_name, attempt.success, attempt.duration)
                    # Log failed attempt if not successful
                    if not attempt.success:
                        self._log_performance_event({
                            'event': 'model_attempt',
                            'model_name': model_name,
                            'success': False,
                            'error': str(attempt.error) if attempt.error else None,
                            'duration': attempt.duration,
                            'retry_count': attempt.retry_count,
                            'task_type': task_type,
                            'fallback_chain': fallback_chain,
                            'fallback_index': model_idx
                        })

            # Log fallback event
            fallback_event_chain.append(attempt.to_dict())
            last_model_used = model_name
            # Fallback to next model

        # Log fallback chain summary
        self._log_performance_event({
            'event': 'fallback_chain_exhausted',
            'task_type': task_type,
            'fallback_chain': fallback_chain,
            'attempts': fallback_event_chain,
            'last_model_used': last_model_used,
            'success': False,
            'error': str(last_error) if last_error else None
        })
        return None, ModelAttempt(
            model_name="",
            success=False,
            error=RuntimeError("All models in fallback chain failed")
        )
    
    def get_system_health(self) -> Dict:
        """Get health status of the AI system."""
        health = {
            'models': {},
            'overall_health': 'healthy',
            'timestamp': time.time()
        }
        
        for model_name, metrics in self.model_metrics.items():
            success_rate = self.get_model_success_rate(model_name)
            health['models'][model_name] = {
                'success_rate': success_rate,
                'total_attempts': metrics['total_attempts'],
                'successful_attempts': metrics['successful_attempts'],
                'average_duration': metrics['total_duration'] / metrics['total_attempts'] if metrics['total_attempts'] > 0 else 0,
                'last_used': metrics['last_used'],
                'status': 'healthy' if success_rate > 0.8 else 'degraded' if success_rate > 0.5 else 'unhealthy'
            }
            
            if health['models'][model_name]['status'] != 'healthy':
                health['overall_health'] = 'degraded'
        
        return health

# Example usage
async def example_task(model_name: str, prompt: str) -> str:
    """Example task function that would call an AI model."""
    # This is a placeholder - in reality, you'd call your AI model here
    if "error" in prompt.lower():
        raise ValueError("Example error for testing")
    return f"Response from {model_name} for prompt: {prompt}"

async def test_fallback():
    """Test the fallback mechanism."""
    manager = FallbackAIManager(max_retries=2)
    
    # Test successful execution
    print("\n=== Testing successful execution ===")
    result, attempt = await manager.execute_with_fallback(
        example_task, 'text', "Hello, world!"
    )
    print(f"Result: {result}")
    print(f"Attempt: {attempt}")
    
    # Test with error (should fall through the chain)
    print("\n=== Testing with error ===")
    result, attempt = await manager.execute_with_fallback(
        example_task, 'text', "This is an error test"
    )
    print(f"Result: {result}")
    print(f"Attempt: {attempt}")
    
    # Print system health
    print("\n=== System Health ===")
    print(json.dumps(manager.get_system_health(), indent=2))

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_fallback())
