"""
Utility functions for working with agents in the Jarvis system.
"""
import asyncio
import logging
from typing import Any, Dict, Optional, Type, TypeVar, Generic, Callable, Awaitable
from functools import wraps
import inspect

from ..base_agent import BaseAgent
from ..config import config

logger = logging.getLogger(__name__)

# Type variable for agent classes
AgentType = TypeVar('AgentType', bound=BaseAgent)

class AgentError(Exception):
    """Base exception for agent-related errors."""
    pass

class AgentInitializationError(AgentError):
    """Raised when an agent fails to initialize."""
    pass

class AgentProcessingError(AgentError):
    """Raised when an agent encounters an error during processing."""
    pass

def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry a function on error.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func):
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(max_retries):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_retries - 1:  # Don't sleep on the last attempt
                            await asyncio.sleep(delay * (attempt + 1))  # Exponential backoff
                        continue
                raise AgentProcessingError(
                    f"Function {func.__name__} failed after {max_retries} attempts") from last_exception
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_retries - 1:  # Don't sleep on the last attempt
                            import time
                            time.sleep(delay * (attempt + 1))  # Exponential backoff
                        continue
                raise AgentProcessingError(
                    f"Function {func.__name__} failed after {max_retries} attempts") from last_exception
            return sync_wrapper
    return decorator

def log_errors(func: Callable) -> Callable:
    """
    Decorator to log errors that occur in agent methods.
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function with error logging
    """
    @wraps(func)
    async def async_wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except Exception as e:
            self.log_error(e, {
                'function': func.__name__,
                'args': args,
                'kwargs': kwargs
            })
            raise
    
    @wraps(func)
    def sync_wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.log_error(e, {
                'function': func.__name__,
                'args': args,
                'kwargs': kwargs
            })
            raise
    
    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

def validate_agent_config(config: Dict[str, Any], required_fields: list) -> None:
    """
    Validate that a configuration dictionary contains all required fields.
    
    Args:
        config: Configuration dictionary to validate
        required_fields: List of required field names
        
    Raises:
        ValueError: If any required fields are missing
    """
    missing = [field for field in required_fields if field not in config]
    if missing:
        raise ValueError(f"Missing required configuration fields: {', '.join(missing)}")

async def run_agent_task(agent: BaseAgent, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run an agent's process method with proper error handling and metrics.
    
    Args:
        agent: The agent to run
        input_data: Input data for the agent
        
    Returns:
        The result of the agent's process method
    """
    try:
        if not agent.initialized:
            await agent.initialize()
        
        result = await agent.process(input_data)
        agent.update_metrics({
            'requests_processed': 1,
            'last_success': datetime.utcnow().isoformat()
        })
        return result
    except Exception as e:
        agent.log_error(e, {'input_data': input_data})
        agent.update_metrics({
            'errors': 1,
            'last_error': datetime.utcnow().isoformat()
        })
        raise AgentProcessingError(f"Error in agent {agent.agent_name}: {str(e)}") from e

def get_agent_class(module_path: str, class_name: str) -> Type[BaseAgent]:
    """
    Dynamically import an agent class from a module.
    
    Args:
        module_path: Path to the module containing the agent class
        class_name: Name of the agent class
        
    Returns:
        The agent class
        
    Raises:
        ImportError: If the module or class cannot be imported
    """
    try:
        module = __import__(module_path, fromlist=[class_name])
        agent_class = getattr(module, class_name)
        if not issubclass(agent_class, BaseAgent):
            raise TypeError(f"{class_name} is not a subclass of BaseAgent")
        return agent_class
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not import agent class {class_name} from {module_path}: {str(e)}")
