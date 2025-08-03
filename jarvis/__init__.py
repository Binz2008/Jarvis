"""
Jarvis - Your Personal Assistant

This module provides the core functionality for the Jarvis personal assistant system,
including the base agent interface and core components.
"""
import os
from typing import Optional, Dict, Any, Type, TypeVar, Generic

from .utils.config import config
from .utils.logger import logger
from .base_agent import BaseAgent
from .ai.ai_task_router import AITaskRouter
from .ai.fallback_ai_manager import FallbackAIManager

__version__ = "0.1.0"

# Type variable for agent classes
AgentType = TypeVar('AgentType', bound=BaseAgent)

class Jarvis:
    """
    Main class for the Jarvis personal assistant system.
    
    This class manages the lifecycle of agents and coordinates their interactions.
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize Jarvis with the given name or use the configured name.
        
        Args:
            name: Optional name for the assistant. If not provided, uses the configured name.
        """
        self.name = name or config.NAME
        self.is_listening = False
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logger.getChild('core')
        self.logger.info(f"Jarvis assistant '{self.name}' initialized.")
        
        try:
            config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'jarvis_config.yaml'))
            self.logger.info(f"Configuration loaded from: {config_path}")
            # Initialize AI Task Router and Fallback Manager
            self.task_router = AITaskRouter(config_path)
            self.fallback_manager = FallbackAIManager(config_path)
            self.logger.info("AI Task Router and Fallback Manager initialized successfully.")
        except Exception as e:
            self.logger.critical(f"Failed to initialize Jarvis components: {e}", exc_info=True)
            # Re-raise the exception to be caught by the main entry point
            raise
            self.fallback_manager = None
    
    def greet(self) -> str:
        """
        Return a greeting message.
        
        Returns:
            str: A greeting message with the assistant's name.
        """
        greeting = f"Hello! I am {self.name}, your personal assistant. How may I assist you today?"
        self.logger.info(f"Greeting user: {greeting}")
        return greeting
    
    def start_listening(self) -> None:
        """Start listening for voice commands and update the listening state."""
        self.is_listening = True
        self.logger.info("Started listening for voice commands")
        print(f"{self.name} is now listening...")
    
    def stop_listening(self) -> None:
        """Stop listening for voice commands and update the listening state."""
        self.is_listening = False
        self.logger.info("Stopped listening for voice commands")
        print(f"{self.name} has stopped listening.")
    
    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register a new agent with the system.
        
        Args:
            agent: An instance of a class that inherits from BaseAgent
            
        Raises:
            ValueError: If an agent with the same name is already registered
        """
        if agent.agent_name in self.agents:
            raise ValueError(f"Agent with name '{agent.agent_name}' is already registered")
        
        self.agents[agent.agent_name] = agent
        self.logger.info(f"Registered agent: {agent.agent_name}")
    
    async def initialize_agents(self) -> None:
        """Initialize all registered agents."""
        self.logger.info("Initializing all registered agents...")
        for agent_name, agent in self.agents.items():
            try:
                await agent.initialize()
                self.logger.info(f"Agent '{agent_name}' initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize agent '{agent_name}': {str(e)}", exc_info=True)
    
    async def shutdown_agents(self) -> None:
        """Shut down all registered agents."""
        self.logger.info("Shutting down all registered agents...")
        for agent_name, agent in self.agents.items():
            try:
                await agent.shutdown()
                self.logger.info(f"Agent '{agent_name}' shut down successfully")
            except Exception as e:
                self.logger.error(f"Error shutting down agent '{agent_name}': {str(e)}", exc_info=True)
    
    async def process_user_prompt(self, prompt: str) -> str:
        """
        Processes a user prompt, routes it to the correct AI task, and returns the response.
        
        Args:
            prompt: The user's input prompt.
        
        Returns:
            The AI-generated response.
        """
        self.logger.info(f"Processing prompt: '{prompt}'")
        if not self.task_router or not self.fallback_manager:
            error_msg = "AI routing/fallback system not initialized. Cannot process prompt."
            self.logger.error(error_msg)
            return error_msg

        try:
            task_name = self.task_router.route_task(prompt)
            if task_name:
                self.logger.info(f"Prompt routed to task: '{task_name}'")
                # The execute_task function in the current FallbackAIManager is a mock.
                # It will be replaced with actual model calls in a future step.
                response = await self.fallback_manager.execute_task(task_name, prompt)
                self.logger.info(f"Received response for task '{task_name}': '{response}'")
                return response
            else:
                default_response = "I'm not sure how to handle that request. Could you be more specific?"
                self.logger.warning(f"No route found for prompt. Returning default response.")
                return default_response
        except Exception as e:
            error_msg = f"An error occurred while processing your request: {e}"
            self.logger.error(error_msg, exc_info=True)
            return error_msg

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """
        Get a registered agent by name.
        
        Args:
            agent_name: Name of the agent to retrieve
            
        Returns:
            The agent instance if found, None otherwise
        """
        return self.agents.get(agent_name)
    
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a registered agent.
        
        Args:
            agent_name: Name of the agent to get status for
            
        Returns:
            Status dictionary if agent exists, None otherwise
        """
        agent = self.get_agent(agent_name)
        return agent.get_status() if agent else None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of Jarvis.
        
        Returns:
            Dict containing status information.
        """
        return {
            'name': self.name,
            'version': __version__,
            'is_listening': self.is_listening,
            'config': config.to_dict()
        }
