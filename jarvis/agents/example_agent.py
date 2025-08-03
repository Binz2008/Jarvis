"""
Example agent demonstrating how to implement a custom agent using the BaseAgent class.
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..base_agent import BaseAgent
from ..config import config
from ..utils.agent_utils import log_errors, retry_on_error, validate_agent_config

logger = logging.getLogger(__name__)

class ExampleAgent(BaseAgent):
    """
    Example agent demonstrating the implementation of a custom agent.
    
    This agent provides a template for creating new agents that integrate with
    the Jarvis system using the BaseAgent interface.
    """
    
    def __init__(self, agent_name: str = "example_agent", config: Optional[Dict[str, Any]] = None):
        """
        Initialize the example agent.
        
        Args:
            agent_name: Unique name for this agent instance
            config: Optional configuration overrides
        """
        super().__init__(agent_name, config)
        self.counter = 0
        self.last_processed = None
        
        # Default configuration
        self.default_config = {
            'greeting': 'Hello from ExampleAgent!',
            'max_processing_time': 10.0,
            'features': ['feature1', 'feature2']
        }
        
        # Merge default config with provided config
        if config:
            self.default_config.update(config)
    
    async def initialize(self) -> bool:
        """
        Initialize the agent and any required resources.
        
        Returns:
            bool: True if initialization was successful
            
        Raises:
            AgentInitializationError: If initialization fails
        """
        logger.info(f"Initializing {self.agent_name}...")
        
        try:
            # Validate required configuration
            validate_agent_config(
                self.default_config,
                required_fields=['greeting', 'max_processing_time']
            )
            
            # Simulate resource initialization
            await asyncio.sleep(0.5)
            
            # Update status
            self.initialized = True
            self.last_updated = datetime.utcnow()
            logger.info(f"{self.agent_name} initialized successfully")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize {self.agent_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.initialized = False
            raise AgentInitializationError(error_msg) from e
    
    @log_errors
    @retry_on_error(max_retries=3, delay=1.0)
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return a response.
        
        Args:
            input_data: Dictionary containing input data
            
        Returns:
            Dictionary containing the processing results
            
        Raises:
            AgentProcessingError: If processing fails
        """
        if not self.initialized:
            raise AgentProcessingError("Agent not initialized")
        
        logger.debug(f"Processing input: {input_data}")
        
        # Simulate some processing
        self.counter += 1
        self.last_processed = datetime.utcnow()
        
        # Update metrics
        self.update_metrics({
            'requests_processed': 1,
            'last_processed': self.last_processed.isoformat()
        })
        
        # Prepare response
        response = {
            'status': 'success',
            'message': self.default_config['greeting'],
            'request_id': input_data.get('request_id', 'unknown'),
            'processed_by': self.agent_name,
            'counter': self.counter,
            'timestamp': datetime.utcnow().isoformat(),
            'config': {
                'features': self.default_config['features'],
                'max_processing_time': self.default_config['max_processing_time']
            }
        }
        
        return response
    
    async def shutdown(self) -> bool:
        """
        Clean up resources before shutting down the agent.
        
        Returns:
            bool: True if shutdown was successful
        """
        logger.info(f"Shutting down {self.agent_name}...")
        
        try:
            # Clean up resources here
            self.initialized = False
            self.last_updated = datetime.utcnow()
            
            logger.info(f"{self.agent_name} shut down successfully")
            return True
            
        except Exception as e:
            error_msg = f"Error shutting down {self.agent_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise AgentProcessingError(error_msg) from e
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent.
        
        Returns:
            Dictionary containing status information
        """
        status = super().get_status()
        status.update({
            'counter': self.counter,
            'last_processed': self.last_processed.isoformat() if self.last_processed else None,
            'config': {
                'features': self.default_config['features'],
                'max_processing_time': self.default_config['max_processing_time']
            }
        })
        return status


# Example usage
async def main():
    """Example usage of the ExampleAgent."""
    # Create and initialize the agent
    agent = ExampleAgent()
    
    try:
        # Initialize the agent
        await agent.initialize()
        
        # Process some data
        result = await agent.process({
            'request_id': 'test_123',
            'data': 'Test input'
        })
        print("Processing result:", result)
        
        # Get agent status
        status = agent.get_status()
        print("Agent status:", status)
        
    finally:
        # Clean up
        await agent.shutdown()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
