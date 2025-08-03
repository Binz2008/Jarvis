"""
GPU and CUDA utility functions for Jarvis.

This module provides functionality to manage and monitor GPU resources,
including CUDA availability checks, memory management, and performance optimization.
"""
import torch
import GPUtil
from typing import Optional, Dict, Any, Tuple
import logging
from pathlib import Path
import json
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class GPUManager:
    """
    A class to manage GPU resources and CUDA operations.
    """
    
    def __init__(self, enable_benchmark: bool = True):
        """
        Initialize the GPU manager.
        
        Args:
            enable_benchmark: Whether to enable cudnn benchmark for faster training
        """
        self.device = None
        self.gpu_info = {}
        self.log_file = Path("gpu_usage.log")
        self._setup_device()
        
        if enable_benchmark and torch.cuda.is_available():
            torch.backends.cudnn.benchmark = True
            logger.info("Enabled cudnn benchmark for optimal performance")
    
    def _setup_device(self) -> None:
        """Set up the device (CPU/GPU) based on availability."""
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            self._update_gpu_info()
            logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA Version: {torch.version.cuda}")
        else:
            self.device = torch.device("cpu")
            logger.warning("CUDA is not available. Using CPU.")
    
    def _update_gpu_info(self) -> None:
        """Update GPU information using GPUtil."""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Get first GPU
                self.gpu_info = {
                    "name": gpu.name,
                    "load": gpu.load,
                    "free_memory": gpu.memoryFree,
                    "used_memory": gpu.memoryUsed,
                    "total_memory": gpu.memoryTotal,
                    "temperature": gpu.temperature,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error updating GPU info: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current GPU status.
        
        Returns:
            Dict containing GPU status information
        """
        self._update_gpu_info()
        return self.gpu_info
    
    def log_gpu_status(self) -> None:
        """Log the current GPU status to a file."""
        try:
            status = self.get_status()
            with open(self.log_file, "a") as f:
                f.write(json.dumps(status) + "\n")
        except Exception as e:
            logger.error(f"Error logging GPU status: {e}")
    
    def clear_memory_cache(self) -> None:
        """Clear the CUDA memory cache."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("Cleared CUDA memory cache")
    
    def get_available_memory(self) -> Tuple[float, float]:
        """
        Get the available and total GPU memory in MB.
        
        Returns:
            Tuple of (available_memory, total_memory) in MB
        """
        if torch.cuda.is_available():
            self._update_gpu_info()
            return (self.gpu_info.get("free_memory", 0), 
                   self.gpu_info.get("total_memory", 0))
        return (0, 0)

# Create a singleton instance
gpu_manager = GPUManager()
