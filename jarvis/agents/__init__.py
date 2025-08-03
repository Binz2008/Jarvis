"""
Jarvis Agents Package

This package contains all the agent implementations for the Jarvis system.
Each agent is designed to handle specific tasks and can be registered with
the main Jarvis instance for coordinated operation.
"""
from typing import Dict, Type, Any
import importlib
import pkgutil
import os

from ..base_agent import BaseAgent
from .example_agent import ExampleAgent

# Dictionary to store registered agent classes
_agent_classes: Dict[str, Type[BaseAgent]] = {
    'example_agent': ExampleAgent,
    # Add other agents here as they are implemented
}

def register_agent(agent_class: Type[BaseAgent]) -> None:
    """
    Register an agent class with the agent factory.
    
    Args:
        agent_class: The agent class to register
        
    Raises:
        TypeError: If agent_class is not a subclass of BaseAgent
        ValueError: If an agent with the same name is already registered
    """
    if not issubclass(agent_class, BaseAgent):
        raise TypeError(f"Agent class must be a subclass of BaseAgent, got {type(agent_class).__name__}")
    
    agent_name = getattr(agent_class, 'DEFAULT_AGENT_NAME', agent_class.__name__.lower())
    
    if agent_name in _agent_classes and _agent_classes[agent_name] is not agent_class:
        raise ValueError(f"An agent with name '{agent_name}' is already registered")
    
    _agent_classes[agent_name] = agent_class

def create_agent(agent_name: str, config: Dict[str, Any] = None, **kwargs) -> BaseAgent:
    """
    Create a new agent instance by name.
    
    Args:
        agent_name: Name of the agent to create
        config: Configuration dictionary for the agent
        **kwargs: Additional arguments to pass to the agent constructor
        
    Returns:
        A new instance of the specified agent
        
    Raises:
        ValueError: If no agent with the specified name is found
    """
    agent_class = _agent_classes.get(agent_name.lower())
    if agent_class is None:
        raise ValueError(f"No agent found with name '{agent_name}'. "
                         f"Available agents: {', '.join(_agent_classes.keys())}")
    
    # Merge config with any additional kwargs
    agent_config = config or {}
    if kwargs:
        agent_config = {**agent_config, **kwargs}
    
    return agent_class(agent_name=agent_name, config=agent_config)

def get_agent_names() -> list:
    """
    Get a list of all registered agent names.
    
    Returns:
        List of registered agent names
    """
    return list(_agent_classes.keys())

def discover_agents() -> None:
    """
    Discover and register all agent classes in the agents package.
    
    This function looks for Python modules in the agents directory and attempts
    to import and register any classes that inherit from BaseAgent.
    """
    from .. import base_agent
    
    # Get the directory containing the agents
    agents_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Import all modules in the agents directory
    for _, module_name, _ in pkgutil.iter_modules([agents_dir]):
        # Skip the base module and private modules
        if module_name == 'base_agent' or module_name.startswith('_'):
            continue
            
        try:
            # Import the module
            module = importlib.import_module(f'.{module_name}', package='jarvis.agents')
            
            # Find all classes that inherit from BaseAgent
            for name, obj in module.__dict__.items():
                if (isinstance(obj, type) and 
                    issubclass(obj, base_agent.BaseAgent) and 
                    obj is not base_agent.BaseAgent):
                    # Register the agent class
                    register_agent(obj)
                    
        except ImportError as e:
            import logging
            logging.getLogger(__name__).warning(
                f"Failed to import agent module '{module_name}': {str(e)}"
            )

# Auto-discover agents when the package is imported
discover_agents()

# Export the public API
__all__ = [
    'BaseAgent',
    'ExampleAgent',
    'register_agent',
    'create_agent',
    'get_agent_names',
    'discover_agents'
]
