"""
Configuration management for Jarvis.
"""
import os
from pathlib import Path
from typing import Dict, Any

# Load environment variables from .env file
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """
    Configuration class for Jarvis.
    
    This class holds all configuration settings loaded from environment variables
    with appropriate type conversion and default values.
    """
    
    # Application Settings
    NAME: str = os.getenv('JARVIS_NAME', 'Jarvis')
    DEFAULT_VOLUME: float = float(os.getenv('DEFAULT_VOLUME', '0.7'))
    LANGUAGE: str = os.getenv('LANGUAGE', 'en-US')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    BACKTEST_MODE: bool = os.getenv('BACKTEST_MODE', 'false').lower() == 'true'
    PAPER_TRADING: bool = os.getenv('PAPER_TRADING', 'false').lower() == 'true'
    MAX_CONCURRENT_TRADES: int = int(os.getenv('MAX_CONCURRENT_TRADES', '5'))
    DEFAULT_RISK_PERCENTAGE: float = float(os.getenv('DEFAULT_RISK_PERCENTAGE', '1.0'))
    
    # Database Configuration
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '5432'))
    DB_NAME: str = os.getenv('DB_NAME', 'mashaaer_trading')
    DB_USER: str = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///roben_trading.db')
    ENABLE_DATABASE_LOGGING: bool = os.getenv('ENABLE_DATABASE_LOGGING', 'false').lower() == 'true'
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', '6379'))
    
    # Web API Server Settings
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
    API_DEBUG: bool = os.getenv('API_DEBUG', 'false').lower() == 'true'
    API_SECRET_KEY: str = os.getenv('API_SECRET_KEY', 'dev_secret_key_change_me')
    
    # Webhook Settings
    WEBHOOK_SECRET: str = os.getenv('WEBHOOK_SECRET', 'change_this_secret')
    
    # NGROK Settings
    NGROK_AUTH_TOKEN: str = os.getenv('NGROK_AUTH_TOKEN', '')
    
    # Voice Settings
    VOICE_RATE: int = int(os.getenv('VOICE_RATE', '150'))
    VOICE_VOLUME: float = float(os.getenv('VOICE_VOLUME', '1.0'))
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    WEATHER_API_KEY: str = os.getenv('WEATHER_API_KEY', '')
    GITHUB_API_KEY: str = os.getenv('GITHUB_API_KEY', '')
    GRAFANA_API_KEY: str = os.getenv('grafana_api_key', '')
    GRAFANA_ALLOY_TOKEN: str = os.getenv('GRAFANA_ALLOY_TOKEN', '')
    ANTHROPIC_API_KEY: str = os.getenv('ANTHROPIC_API_KEY', '')
    
    # Trading Configuration
    BYBIT_API_KEY: str = os.getenv('BYBIT_API_KEY', '')
    BYBIT_API_SECRET: str = os.getenv('BYBIT_API_SECRET', '')
    BINANCE_API_KEY: str = os.getenv('BINANCE_API_KEY', '')
    BINANCE_SECRET_KEY: str = os.getenv('BINANCE_SECRET_KEY', '')
    BINANCE_TESTNET: bool = os.getenv('BINANCE_TESTNET', 'false').lower() == 'true'
    TRADING_PAIR: str = os.getenv('TRADING_PAIR', 'BTCUSDT')
    DEFAULT_TRADING_PAIRS: list = os.getenv('DEFAULT_TRADING_PAIRS', 'BTCUSDT,ETHUSDT').split(',')
    AUTO_MODE_INTERVAL: int = int(os.getenv('AUTO_MODE_INTERVAL', '30'))  # in seconds
    SNIPER_MODE_INTERVAL: int = int(os.getenv('SNIPER_MODE_INTERVAL', '15'))  # in seconds
    RISK_LEVEL: str = os.getenv('RISK_LEVEL', 'conservative').lower()
    LEVERAGE: int = int(os.getenv('LEVERAGE', '10'))
    
    # AI/ML Configuration
    ENABLE_AI_PREDICTIONS: bool = os.getenv('ENABLE_AI_PREDICTIONS', 'false').lower() == 'true'
    AI_MODEL_PATH: str = os.getenv('AI_MODEL_PATH', './models/trading_model.pkl')
    ENABLE_SENTIMENT_ANALYSIS: bool = os.getenv('ENABLE_SENTIMENT_ANALYSIS', 'false').lower() == 'true'
    NEWS_API_KEY: str = os.getenv('NEWS_API_KEY', '')
    
    # Notification Settings
    ENABLE_EMAIL_NOTIFICATIONS: bool = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
    EMAIL_SMTP_SERVER: str = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    EMAIL_SMTP_PORT: int = int(os.getenv('EMAIL_SMTP_PORT', '587'))
    EMAIL_USERNAME: str = os.getenv('EMAIL_USERNAME', '')
    EMAIL_PASSWORD: str = os.getenv('EMAIL_PASSWORD', '')
    
    # Backup Settings
    ENABLE_AUTO_BACKUP: bool = os.getenv('ENABLE_AUTO_BACKUP', 'false').lower() == 'true'
    BACKUP_INTERVAL_HOURS: int = int(os.getenv('BACKUP_INTERVAL_HOURS', '24'))
    BACKUP_LOCATION: str = os.getenv('BACKUP_LOCATION', './backups/')
    MAX_BACKUP_FILES: int = int(os.getenv('MAX_BACKUP_FILES', '30'))
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '')
    ENABLE_TELEGRAM_NOTIFICATIONS: bool = os.getenv('ENABLE_TELEGRAM_NOTIFICATIONS', 'false').lower() == 'true'
    
    # Hugging Face Configuration
    HF_TOKEN: str = os.getenv('HF_TOKEN', '')
    
    # Logging (LOG_LEVEL already defined above in Application Settings)
    LOG_FILE: str = os.getenv('LOG_FILE', 'jarvis.log')
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """
        Return all configuration as a dictionary.
        
        Returns:
            Dict[str, Any]: A dictionary containing all configuration settings.
        """
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and key.isupper()
        }

# Export config instance
config = Config()
