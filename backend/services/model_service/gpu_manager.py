from typing import Dict, List, Optional
import torch
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GPUConfig:
    min_batch_size: int
    max_batch_size: int
    cuda_memory_fraction: float

class GPUManager:
    def __init__(self, config: Dict):
        self.config = config
        self.gpu_configs = {}
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
        
    def is_gpu_available(self) -> bool:
        """Check if GPU is available"""
        return torch.cuda.is_available()
        
    def get_available_memory(self) -> float:
        """Get available GPU memory in GB"""
        if not self.is_gpu_available():
            return 0.0
        return torch.cuda.get_device_properties(0).total_memory / 1024**3
        
    def optimize_batch_size(self, model_name: str, input_length: int) -> int:
        """Optimize batch size based on input length and available memory"""
        if not self.is_gpu_available():
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
        if not self.is_gpu_available():
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
        if not self.is_gpu_available():
            return {'status': 'gpu_not_available'}
            
        return {
            'total_memory': torch.cuda.get_device_properties(0).total_memory / 1024**3,
            'allocated_memory': torch.cuda.memory_allocated(0) / 1024**3,
            'cached_memory': torch.cuda.memory_reserved(0) / 1024**3,
            'utilization': torch.cuda.utilization()
        }
