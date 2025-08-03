"""
Base Agent Interface for Jarvis AI System.

This module defines the abstract base class that all agents should inherit from
to ensure consistent behavior and integration across the system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the Jarvis system.
    
    This class defines the common interface that all agents must implement
    to ensure consistent behavior and integration with the system.
    """
    
    def __init__(self, agent_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Unique identifier for this agent
            config: Configuration dictionary for the agent
        """
        self.agent_name = agent_name
        self.config = config or {}
        self.initialized = False
        self.last_updated = datetime.utcnow()
        self.metrics = {
            'start_time': datetime.utcnow().isoformat(),
            'requests_processed': 0,
            'errors': 0,
            'last_error': None
        }
        
        logger.info(f"Initializing agent: {agent_name}")
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the agent and any required resources.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        self.initialized = True
        self.last_updated = datetime.utcnow()
        logger.info(f"Agent {self.agent_name} initialized successfully")
        return True
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return a response.
        
        Args:
            input_data: Dictionary containing input data for processing
            
        Returns:
            Dictionary containing the processing results
        """
        self.metrics['requests_processed'] += 1
        self.last_updated = datetime.utcnow()
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """
        Clean up resources before shutting down the agent.
        
        Returns:
            bool: True if shutdown was successful, False otherwise
        """
        self.initialized = False
        logger.info(f"Agent {self.agent_name} shutdown successfully")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent.
        
        Returns:
            Dictionary containing status information including:
            - agent_name: Name of the agent
            - status: Current status (initialized/running/error)
            - last_updated: Timestamp of last update
            - metrics: Performance and operational metrics
        """
        return {
            'agent_name': self.agent_name,
            'status': 'initialized' if self.initialized else 'uninitialized',
            'last_updated': self.last_updated.isoformat(),
            'metrics': self.metrics
        }
    
    def update_metrics(self, metric_updates: Dict[str, Any]) -> None:
        """
        Update agent metrics with new values.
        
        Args:
            metric_updates: Dictionary of metric updates
        """
        self.metrics.update(metric_updates)
        self.last_updated = datetime.utcnow()
        
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error that occurred during processing.
        
        Args:
            error: The exception that was raised
            context: Additional context about the error
        """
        self.metrics['errors'] += 1
        self.metrics['last_error'] = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': error.__class__.__name__,
            'error_message': str(error),
            'context': context or {}
        }
        logger.error(
            f"Error in agent {self.agent_name}: {str(error)}",
            exc_info=True,
            extra={'context': context or {}}
        )
