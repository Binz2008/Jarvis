""
Tests for GPU and CUDA functionality.
"""
import unittest
import torch
from jarvis.utils import gpu_manager

class TestGPU(unittest.TestCase):
    """Test cases for GPU functionality."""
    
    def test_cuda_available(self):
        """Test if CUDA is available."""
        self.assertEqual(torch.cuda.is_available(), 
                        gpu_manager.device.type == 'cuda',
                        "CUDA availability mismatch between PyTorch and GPU manager")
    
    def test_gpu_info(self):
        """Test if GPU information is being collected correctly."""
        if torch.cuda.is_available():
            info = gpu_manager.get_status()
            self.assertIn('name', info, "GPU name not found in info")
            self.assertIn('load', info, "GPU load not found in info")
            self.assertIn('total_memory', info, "GPU total memory not found in info")
    
    def test_tensor_operations(self):
        """Test basic tensor operations on GPU if available."""
        if torch.cuda.is_available():
            # Create two random tensors
            a = torch.randn(1000, 1000, device=gpu_manager.device)
            b = torch.randn(1000, 1000, device=gpu_manager.device)
            
            # Perform matrix multiplication
            c = torch.matmul(a, b)
            
            # Verify the result is on the correct device
            self.assertEqual(c.device, gpu_manager.device, 
                           "Tensor is not on the expected device")
            
            # Verify the operation produced a valid result
            self.assertFalse(torch.isnan(c).any(), "Matrix multiplication produced NaN values")
            self.assertFalse(torch.isinf(c).any(), "Matrix multiplication produced Inf values")

if __name__ == '__main__':
    unittest.main()
