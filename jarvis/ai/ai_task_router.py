"""
AI Task Router for JARVIS
------------------------
This module handles intelligent routing of tasks to the most appropriate AI model
based on the task type, complexity, and available system resources.
"""

import logging
from typing import Dict, List, Optional, Tuple
import json
import subprocess
from dataclasses import dataclass
from enum import Enum, auto

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Enumeration of different task types."""
    CODE_ANALYSIS = auto()
    CODE_GENERATION = auto()
    TEXT_GENERATION = auto()
    IMAGE_ANALYSIS = auto()
    GENERAL_QA = auto()
    DOCUMENTATION = auto()
    DEBUGGING = auto()
    OPTIMIZATION = auto()

@dataclass
class AIModel:
    """Data class representing an AI model configuration."""
    name: str
    task_types: List[TaskType]
    priority: int
    memory_requirement: int  # in MB
    is_available: bool = True
    
    def to_dict(self) -> Dict:
        """Convert model to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'task_types': [t.name for t in self.task_types],
            'priority': self.priority,
            'memory_requirement_mb': self.memory_requirement,
            'is_available': self.is_available
        }

class AITaskRouter:
    """
    Routes tasks to the most appropriate AI model based on task type and system resources.
    """
    
    def __init__(self):
        """Initialize the AI Task Router with available models."""
        self.available_models = self._initialize_models()
        self.model_metrics = {}
        self.update_model_availability()
    
    def _initialize_models(self) -> Dict[str, AIModel]:
        """Initialize available AI models with their configurations."""
        return {
            'codellama:7b-instruct': AIModel(
                name='codellama:7b-instruct',
                task_types=[
                    TaskType.CODE_ANALYSIS,
                    TaskType.CODE_GENERATION,
                    TaskType.DEBUGGING,
                    TaskType.OPTIMIZATION,
                    TaskType.DOCUMENTATION
                ],
                priority=1,
                memory_requirement=3800
            ),
            'llama3:8b': AIModel(
                name='llama3:8b',
                task_types=[
                    TaskType.TEXT_GENERATION,
                    TaskType.GENERAL_QA,
                    TaskType.DOCUMENTATION
                ],
                priority=2,
                memory_requirement=4700
            ),
            'mistral:latest': AIModel(
                name='mistral:latest',
                task_types=[
                    TaskType.TEXT_GENERATION,
                    TaskType.GENERAL_QA
                ],
                priority=3,
                memory_requirement=4400
            ),
            'llava:latest': AIModel(
                name='llava:latest',
                task_types=[
                    TaskType.IMAGE_ANALYSIS
                ],
                priority=4,
                memory_requirement=4700
            ),
            'zephyr:7b-beta': AIModel(
                name='zephyr:7b-beta',
                task_types=[
                    TaskType.TEXT_GENERATION,
                    TaskType.GENERAL_QA
                ],
                priority=5,
                memory_requirement=4100
            ),
            'gemma:2b': AIModel(
                name='gemma:2b',
                task_types=[
                    TaskType.TEXT_GENERATION,
                    TaskType.GENERAL_QA
                ],
                priority=6,
                memory_requirement=1700
            )
        }
    
    def update_model_availability(self) -> None:
        """Update the availability status of all models."""
        try:
            # Get list of installed models
            result = subprocess.run(
                ["ollama", "list", "--json"],
                capture_output=True,
                text=True,
                check=True
            )
            installed_models = {m['name'] for m in json.loads(result.stdout)}
            
            # Update availability
            for model_name, model in self.available_models.items():
                model.is_available = model_name in installed_models
                
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.error(f"Error updating model availability: {e}")
    
    def get_available_memory(self) -> int:
        """Get available GPU memory in MB."""
        try:
            import torch
            if torch.cuda.is_available():
                return torch.cuda.get_device_properties(0).total_memory // (1024 * 1024)
        except ImportError:
            pass
        
        # Fallback to system command if PyTorch not available
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                check=True
            )
            return int(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            # Default to 6GB if can't determine
            return 6 * 1024
    
    def route_task(self, task_type: TaskType, context: Optional[Dict] = None) -> Tuple[str, Dict]:
        """
        Route a task to the most appropriate AI model.
        
        Args:
            task_type: The type of task to route.
            context: Additional context for routing decisions.
            
        Returns:
            Tuple of (model_name, model_config)
        """
        if context is None:
            context = {}
        
        # Filter models that can handle this task type
        suitable_models = [
            model for model in self.available_models.values()
            if task_type in model.task_types and model.is_available
        ]
        
        if not suitable_models:
            raise ValueError(f"No suitable models available for task type: {task_type}")
        
        # Sort by priority (lower is better) and memory requirement (lower is better)
        suitable_models.sort(key=lambda m: (m.priority, m.memory_requirement))
        
        # Get available memory
        available_memory = self.get_available_memory()
        
        # Find the best model that fits in available memory
        for model in suitable_models:
            if model.memory_requirement <= available_memory:
                return model.name, model.to_dict()
        
        # If no model fits, return the smallest one with a warning
        smallest_model = min(suitable_models, key=lambda m: m.memory_requirement)
        logger.warning(
            f"No model fits in available memory ({available_memory}MB). "
            f"Using smallest model: {smallest_model.name} ({smallest_model.memory_requirement}MB)"
        )
        return smallest_model.name, smallest_model.to_dict()
    
    def get_model_info(self, model_name: str) -> Dict:
        """Get information about a specific model."""
        if model_name not in self.available_models:
            raise ValueError(f"Unknown model: {model_name}")
        return self.available_models[model_name].to_dict()
    
    def list_models(self) -> List[Dict]:
        """Get information about all available models."""
        return [model.to_dict() for model in self.available_models.values()]
    
    def get_system_status(self) -> Dict:
        """Get system and models status."""
        return {
            'gpu_available': self.get_available_memory() > 0,
            'gpu_memory_mb': self.get_available_memory(),
            'models': [model.to_dict() for model in self.available_models.values()]
        }

def test_router():
    """Test the AI task router."""
    router = AITaskRouter()
    
    print("=== System Status ===")
    print(json.dumps(router.get_system_status(), indent=2))
    
    print("\n=== Testing Task Routing ===")
    test_cases = [
        (TaskType.CODE_ANALYSIS, "Code analysis task"),
        (TaskType.TEXT_GENERATION, "Text generation task"),
        (TaskType.IMAGE_ANALYSIS, "Image analysis task"),
        (TaskType.DEBUGGING, "Debugging task")
    ]
    
    for task_type, description in test_cases:
        model_name, config = router.route_task(task_type)
        print(f"\n{description} -> {model_name}")
        print(f"  Memory: {config['memory_requirement_mb']}MB")
        print(f"  Priority: {config['priority']}")

if __name__ == "__main__":
    test_router()
