"""
Configuration management for the Jarvis system.

This module provides a centralized configuration system that loads settings
from environment variables and configuration files, with support for agent-specific
configurations.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Type, TypeVar
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Type variable for configuration classes
T = TypeVar('T', bound='BaseConfig')

class BaseConfig:
    """Base class for all configuration classes."""
    
    @classmethod
    def from_env(cls: Type[T], prefix: str = '') -> T:
        """
        Create a config instance from environment variables with the given prefix.
        
        Args:
            prefix: Prefix for environment variable names
            
        Returns:
            An instance of the config class with values from environment variables
        """
        config = cls()
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                # Convert string values to appropriate types
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
                    value = float(value)
                setattr(config, config_key, value)
        return config
    
    @classmethod
    def from_dict(cls: Type[T], config_dict: Dict[str, Any]) -> T:
        """
        Create a config instance from a dictionary.
        
        Args:
            config_dict: Dictionary of configuration values
            
        Returns:
            An instance of the config class with values from the dictionary
        """
        config = cls()
        for key, value in config_dict.items():
            setattr(config, key, value)
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the config to a dictionary.
        
        Returns:
            Dictionary containing the configuration values
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def __str__(self) -> str:
        """Return a string representation of the configuration."""
        return json.dumps(self.to_dict(), indent=2)


class AgentConfig(BaseConfig):
    """Base configuration class for agents."""
    
    def __init__(self):
        self.enabled: bool = True
        self.log_level: str = 'INFO'
        self.max_retries: int = 3
        self.retry_delay: float = 1.0
        self.timeout: float = 30.0


class DatabaseConfig(BaseConfig):
    """Database configuration."""
    
    def __init__(self):
        self.host: str = os.getenv('DB_HOST', 'localhost')
        self.port: int = int(os.getenv('DB_PORT', '5432'))
        self.name: str = os.getenv('DB_NAME', 'jarvis')
        self.user: str = os.getenv('DB_USER', 'postgres')
        self.password: str = os.getenv('DB_PASSWORD', '')


class APIConfig(BaseConfig):
    """API configuration."""
    
    def __init__(self):
        self.host: str = os.getenv('API_HOST', '0.0.0.0')
        self.port: int = int(os.getenv('API_PORT', '8000'))
        self.debug: bool = os.getenv('API_DEBUG', 'False').lower() == 'true'
        self.secret_key: str = os.getenv('API_SECRET_KEY', 'dev-secret-key')


class TradingConfig(BaseConfig):
    """Trading configuration."""
    
    def __init__(self):
        # Use Bybit as primary trading API (matches .env variables)
        self.bybit_api_key: str = os.getenv('BYBIT_API_KEY', '')
        self.bybit_api_secret: str = os.getenv('BYBIT_API_SECRET', '')
        self.bybit_testnet: bool = os.getenv('BYBIT_TESTNET', 'true').lower() == 'true'
        
        # Binance API (secondary)
        self.binance_api_key: str = os.getenv('BINANCE_API_KEY', '')
        self.binance_secret_key: str = os.getenv('BINANCE_SECRET_KEY', '')
        
        # Trading settings
        self.default_symbol: str = os.getenv('DEFAULT_SYMBOL', 'BTCUSDT')
        self.default_quantity: float = float(os.getenv('DEFAULT_QUANTITY', '0.01'))
        self.max_concurrent_trades: int = int(os.getenv('MAX_CONCURRENT_TRADES', '5'))
        self.default_risk_percentage: float = float(os.getenv('DEFAULT_RISK_PERCENTAGE', '1.0'))
        
        # Risk management
        self.max_daily_loss_percent: float = float(os.getenv('MAX_DAILY_LOSS_PERCENT', '10.0'))
        self.max_position_size_percent: float = float(os.getenv('MAX_POSITION_SIZE_PERCENT', '2.0'))
        self.stop_loss_percent: float = float(os.getenv('STOP_LOSS_PERCENT', '3.0'))
        self.take_profit_percent: float = float(os.getenv('TAKE_PROFIT_PERCENT', '6.0'))
        self.enable_stop_loss: bool = os.getenv('ENABLE_STOP_LOSS', 'true').lower() == 'true'
        self.enable_take_profit: bool = os.getenv('ENABLE_TAKE_PROFIT', 'true').lower() == 'true'


class Config:
    """Main configuration class for the Jarvis system."""
    
    def __init__(self):
        self.env: str = os.getenv('ENV', 'development')
        self.debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO')
        self.data_dir: str = os.getenv('DATA_DIR', str(Path.home() / '.jarvis' / 'data'))
        
        # Sub-configurations
        self.api: APIConfig = APIConfig()
        self.database: DatabaseConfig = DatabaseConfig()
        self.trading: TradingConfig = TradingConfig()
        
        # Agent configurations (dynamically loaded)
        self.agents: Dict[str, AgentConfig] = {}
    
    def load_agent_config(self, agent_name: str, config_class: Type[AgentConfig] = AgentConfig) -> AgentConfig:
        """
        Load configuration for a specific agent.
        
        Args:
            agent_name: Name of the agent
            config_class: Configuration class to use (must inherit from AgentConfig)
            
        Returns:
            An instance of the specified config class
        """
        prefix = f'AGENT_{agent_name.upper()}_'
        config = config_class.from_env(prefix)
        self.agents[agent_name] = config
        return config
    
    def get_agent_config(self, agent_name: str) -> AgentConfig:
        """
        Get configuration for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            The agent's configuration, or a default config if not found
        """
        return self.agents.get(agent_name, AgentConfig())


# Global configuration instance
config = Config()

# Ensure data directory exists
os.makedirs(config.data_dir, exist_ok=True)
