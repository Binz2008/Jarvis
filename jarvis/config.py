import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# API Configuration
class Config:
    # Bybit API
    BYBIT_API_KEY = os.getenv('BYBIT_API_KEY')
    BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET')
    
    # Trading Settings
    TRADING_PAIR = os.getenv('TRADING_PAIR', 'BTCUSDT')
    LEVERAGE = int(os.getenv('LEVERAGE', 10))
    
    @classmethod
    def validate_config(cls):
        """Validate that all required environment variables are set."""
        required_vars = ['BYBIT_API_KEY', 'BYBIT_API_SECRET']
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Validate configuration on import
Config.validate_config()
