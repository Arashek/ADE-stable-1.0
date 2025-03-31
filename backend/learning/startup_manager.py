import os
import torch
import torch.distributed as dist
from typing import Dict, Any, Optional
from .hub.interface import LearningHubInterface
from .distributed.trainer import DistributedTrainer
from .visualization.learning_visualizer import LearningVisualizer
from .config.training_config import ConfigManager
from ..config.logging_config import logger

class LearningStartupManager:
    """Manages automatic initialization of learning components"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.interface = None
        self.trainer = None
        self.visualizer = None
        self.config_manager = None
        
    def initialize(self):
        """Initialize all learning components"""
        try:
            # Initialize configuration manager
            self.config_manager = ConfigManager()
            
            # Initialize visualizer
            self.visualizer = LearningVisualizer()
            
            # Initialize distributed training if enabled
            if self._should_use_distributed():
                self._initialize_distributed()
                
            # Initialize GUI
            self._initialize_gui()
            
            logger.info("Successfully initialized learning components")
            
        except Exception as e:
            logger.error(f"Error initializing learning components: {str(e)}")
            raise
            
    def _should_use_distributed(self) -> bool:
        """Check if distributed training should be used"""
        try:
            # Check config
            if not self.config.get('use_distributed', False):
                return False
                
            # Check CUDA availability
            if not torch.cuda.is_available():
                return False
                
            # Check number of GPUs
            num_gpus = torch.cuda.device_count()
            if num_gpus < 2:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking distributed training: {str(e)}")
            return False
            
    def _initialize_distributed(self):
        """Initialize distributed training"""
        try:
            # Set environment variables
            os.environ['WORLD_SIZE'] = str(torch.cuda.device_count())
            os.environ['RANK'] = '0'
            os.environ['MASTER_ADDR'] = 'localhost'
            os.environ['MASTER_PORT'] = '29500'
            
            # Initialize process group
            dist.init_process_group(
                backend='nccl',
                init_method='env://'
            )
            
            # Create distributed trainer
            self.trainer = DistributedTrainer(
                model=None,  # Model will be set by user
                optimizer=None,  # Optimizer will be set by user
                train_dataset=None,  # Dataset will be set by user
                config=self._get_distributed_config(),
                output_dir="data/learning/training"
            )
            
            logger.info("Successfully initialized distributed training")
            
        except Exception as e:
            logger.error(f"Error initializing distributed training: {str(e)}")
            raise
            
    def _initialize_gui(self):
        """Initialize GUI in a separate process"""
        try:
            # Create and run interface
            self.interface = LearningHubInterface()
            
            # Start interface in a separate thread
            import threading
            interface_thread = threading.Thread(target=self.interface.run)
            interface_thread.daemon = True
            interface_thread.start()
            
            logger.info("Successfully initialized GUI")
            
        except Exception as e:
            logger.error(f"Error initializing GUI: {str(e)}")
            raise
            
    def _get_distributed_config(self) -> Dict[str, Any]:
        """Get distributed training configuration"""
        return {
            'use_distributed': True,
            'use_model_parallel': True,
            'use_pipeline_parallel': True,
            'use_tensor_parallel': True,
            'gradient_accumulation_steps': 4,
            'use_amp': True,
            'grad_clip_value': 1.0,
            'scheduler': {
                'type': 'cosine',
                'T_max': 100,
                'eta_min': 0.0001
            },
            'micro_batch_size': 4,
            'num_micro_batches': 8,
            'pipeline_stages': 4
        }
        
    def cleanup(self):
        """Cleanup learning components"""
        try:
            if self.trainer:
                self.trainer.cleanup()
                
            if self.interface:
                self.interface.root.quit()
                
            logger.info("Successfully cleaned up learning components")
            
        except Exception as e:
            logger.error(f"Error cleaning up learning components: {str(e)}")
            raise 