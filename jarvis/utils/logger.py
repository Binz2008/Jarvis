"""
Logging configuration for Jarvis.

This module provides a logging utility with both console and file handlers,
with configurable log levels and output formats.
"""
import logging
import sys
from pathlib import Path
from typing import Optional

from .config import config


def setup_logger(name: str = 'jarvis', log_level: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.

    Args:
        name: Name of the logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                  If None, uses the level from config.

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set log level
    level = getattr(logging, log_level or config.LOG_LEVEL, logging.INFO)
    logger.setLevel(level)

    # Clear any existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add file handler if log file is specified
    if config.LOG_FILE:
        try:
            log_path = Path(config.LOG_FILE).resolve()
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (IOError, OSError) as e:
            logger.error(f"Failed to set up file logging: {e}")

    return logger


# Create default logger instance
logger = setup_logger()
