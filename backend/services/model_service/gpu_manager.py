from typing import Dict, List, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import torch, but provide fallbacks if not available
TORCH_AVAILABLE = False
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch (torch) not available. GPU management will be simulated.")

@dataclass
class GPUConfig:
    min_batch_size: int
    max_batch_size: int
    cuda_memory_fraction: float

class GPUManager:
    def __init__(self, config: Dict):
        self.config = config
        self.gpu_configs = {}
        self.using_gpu = TORCH_AVAILABLE and self._is_gpu_available()
        if not TORCH_AVAILABLE:
            logger.info("Operating in CPU-only mode (PyTorch not installed)")
        elif not self.using_gpu:
            logger.info("No usable GPU detected, operating in CPU-only mode")
        else:
            logger.info(f"GPU enabled with {self._get_gpu_count()} devices available")
        self._initialize_gpu_configs()
        
    def _initialize_gpu_configs(self):
        """Initialize GPU configurations for each model"""
        if not self.config.get('gpu_acceleration', {}).get('enabled', False):
            logger.warning("GPU acceleration is disabled")
            return
            
        strategies = self.config['gpu_acceleration']['strategies']
        for strategy in strategies:
            models = strategy['model'] if isinstance(strategy['model'], list) else [strategy['model']]
            for model in models:
                self.gpu_configs[model] = GPUConfig(
                    min_batch_size=strategy['min_batch_size'],
                    max_batch_size=strategy['max_batch_size'],
                    cuda_memory_fraction=strategy['cuda_memory_fraction']
                )
                
    def get_gpu_config(self, model_name: str) -> Optional[GPUConfig]:
        """Get GPU configuration for a specific model"""
        return self.gpu_configs.get(model_name)
        
    def _is_gpu_available(self) -> bool:
        """Check if GPU is available"""
        if not TORCH_AVAILABLE:
            return False
        return torch.cuda.is_available()
        
    def _get_gpu_count(self) -> int:
        """Get number of available GPUs"""
        if not TORCH_AVAILABLE or not self.using_gpu:
            return 0
        return torch.cuda.device_count()
        
    def get_available_memory(self) -> float:
        """Get available GPU memory in GB"""
        if not self.using_gpu:
            return 0.0
        return self._get_available_gpu_memory() / 1024**3
        
    def _get_available_gpu_memory(self) -> int:
        """Get available GPU memory in bytes"""
        if not self.using_gpu:
            return 0
            
        # Get largest free memory across all GPUs
        max_free = 0
        for i in range(self._get_gpu_count()):
            free_memory = self._get_gpu_free_memory(i)
            max_free = max(max_free, free_memory)
            
        return max_free
        
    def _get_gpu_free_memory(self, device_id: int = 0) -> int:
        """Get free memory on specified GPU in bytes"""
        if not self.using_gpu:
            return 0
            
        try:
            torch.cuda.set_device(device_id)
            free_memory = torch.cuda.mem_get_info()[0]  # Returns (free, total)
            return free_memory
        except Exception as e:
            logger.warning(f"Error getting GPU memory: {str(e)}")
            # Fallback to a conservative estimate
            return 2 * 1024 * 1024 * 1024  # 2 GB
        
    def optimize_batch_size(self, model_name: str, input_length: int) -> int:
        """Optimize batch size based on input length and available memory"""
        if not self.using_gpu:
            return 1
            
        config = self.get_gpu_config(model_name)
        if not config:
            return 1
            
        available_memory = self.get_available_memory() * config.cuda_memory_fraction
        
        # Estimate memory needed per sample (this is a simplified estimation)
        memory_per_sample = (input_length * 2) / 1024  # in MB
        
        max_possible_batch = int(available_memory * 1024 / memory_per_sample)
        optimal_batch = min(max_possible_batch, config.max_batch_size)
        
        return max(optimal_batch, config.min_batch_size)
        
    def prepare_model_for_gpu(self, model_name: str) -> Dict:
        """Prepare GPU configuration for model loading"""
        if not self.using_gpu:
            return {'device': 'cpu', 'batch_size': 1}
            
        config = self.get_gpu_config(model_name)
        if not config:
            return {'device': 'cpu', 'batch_size': 1}
            
        return {
            'device': 'cuda',
            'batch_size': config.min_batch_size,
            'memory_fraction': config.cuda_memory_fraction
        }
        
    def monitor_gpu_usage(self) -> Dict:
        """Monitor current GPU usage"""
        if not self.using_gpu:
            return {'status': 'gpu_not_available'}
            
        return {
            'total_memory': torch.cuda.get_device_properties(0).total_memory / 1024**3,
            'allocated_memory': torch.cuda.memory_allocated(0) / 1024**3,
            'cached_memory': torch.cuda.memory_reserved(0) / 1024**3,
            'utilization': torch.cuda.utilization()
        }
