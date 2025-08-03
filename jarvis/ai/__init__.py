"""
JARVIS AI Integration Module
---------------------------
This module provides the main interface for JARVIS AI capabilities,
including code analysis, text generation, and other AI-powered features.
"""

from .ai_task_router import AITaskRouter, TaskType
from .fallback_ai_manager import FallbackAIManager
from ..utils.code_analyzer import CodeAnalyzer

# Initialize core components
router = AITaskRouter()
fallback_manager = FallbackAIManager()
code_analyzer = CodeAnalyzer()

__all__ = [
    'router',
    'fallback_manager',
    'code_analyzer',
    'AITaskRouter',
    'TaskType',
    'FallbackAIManager',
    'CodeAnalyzer'
]
