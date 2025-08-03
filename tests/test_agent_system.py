"""
Test script for the Jarvis agent system.

This script demonstrates how to use the agent system, including agent registration,
initialization, and processing.
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jarvis import Jarvis
from jarvis.agents import create_agent, register_agent, get_agent_names
from jarvis.base_agent import BaseAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TestAgent(BaseAgent):
    """A simple test agent for demonstration purposes."""
    
    DEFAULT_AGENT_NAME = "test_agent"
    
    def __init__(self, agent_name: str = None, config: dict = None):
        super().__init__(agent_name or self.DEFAULT_AGENT_NAME, config or {})
        self.processed_count = 0
    
    async def initialize(self) -> bool:
        logger.info(f"Initializing {self.agent_name}")
        await asyncio.sleep(0.1)  # Simulate initialization
        self.initialized = True
        return True
    
    async def process(self, input_data: dict) -> dict:
        self.processed_count += 1
        return {
            'status': 'success',
            'agent': self.agent_name,
            'processed_count': self.processed_count,
            'input': input_data
        }
    
    async def shutdown(self) -> bool:
        logger.info(f"Shutting down {self.agent_name}")
        self.initialized = False
        return True

async def test_agent_lifecycle():
    """Test the complete lifecycle of an agent."""
    logger.info("Starting agent lifecycle test...")
    
    # Create and register the test agent
    test_agent = TestAgent()
    
    # Initialize the agent
    await test_agent.initialize()
    assert test_agent.initialized, "Agent should be initialized"
    
    # Process some data
    result = await test_agent.process({"test": "data"})
    assert result['status'] == 'success', "Processing should succeed"
    assert result['processed_count'] == 1, "Processed count should increment"
    
    # Get agent status
    status = test_agent.get_status()
    assert status['status'] == 'initialized', "Agent status should be initialized"
    
    # Shutdown the agent
    await test_agent.shutdown()
    assert not test_agent.initialized, "Agent should be shut down"
    
    logger.info("Agent lifecycle test completed successfully!")

async def test_jarvis_integration():
    """Test integration with the main Jarvis class."""
    logger.info("Starting Jarvis integration test...")
    
    # Create a Jarvis instance
    jarvis = Jarvis()
    
    # Create and register a test agent
    test_agent = TestAgent()
    jarvis.register_agent(test_agent)
    
    # Initialize all agents
    await jarvis.initialize_agents()
    assert test_agent.initialized, "Agent should be initialized by Jarvis"
    
    # Get agent status through Jarvis
    status = jarvis.get_agent_status(test_agent.agent_name)
    assert status is not None, "Should be able to get agent status"
    
    # Get agent instance
    agent = jarvis.get_agent(test_agent.agent_name)
    assert agent is not None, "Should be able to get agent instance"
    
    # Shutdown all agents
    await jarvis.shutdown_agents()
    assert not test_agent.initialized, "Agent should be shut down by Jarvis"
    
    logger.info("Jarvis integration test completed successfully!")

async def test_agent_factory():
    """Test the agent factory functionality."""
    logger.info("Starting agent factory test...")
    
    # Register the test agent class
    register_agent(TestAgent)
    
    # Create an agent using the factory
    agent = create_agent("test_agent")
    assert isinstance(agent, TestAgent), "Should create a TestAgent instance"
    
    # Initialize and test the agent
    await agent.initialize()
    result = await agent.process({"factory_test": True})
    assert result['status'] == 'success', "Agent should process data"
    await agent.shutdown()
    
    logger.info("Agent factory test completed successfully!")

async def main():
    """Run all tests."""
    try:
        logger.info("Starting agent system tests...")
        
        await test_agent_lifecycle()
        await test_jarvis_integration()
        await test_agent_factory()
        
        logger.info("All tests completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
