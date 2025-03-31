import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration for the model trainer."""
    
    # MongoDB settings
    mongodb_uri: str = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    mongodb_database: str = os.getenv('MONGODB_DATABASE', 'ade_platform')
    
    # Redis settings
    redis_host: str = os.getenv('REDIS_HOST', 'localhost')
    redis_port: int = int(os.getenv('REDIS_PORT', '6379'))
    redis_password: Optional[str] = os.getenv('REDIS_PASSWORD')
    
    # Training settings
    batch_size: int = int(os.getenv('BATCH_SIZE', '32'))
    learning_rate: float = float(os.getenv('LEARNING_RATE', '0.001'))
    epochs: int = int(os.getenv('EPOCHS', '10'))
    
    # Model settings
    model_type: str = os.getenv('MODEL_TYPE', 'default')
    model_path: Optional[str] = os.getenv('MODEL_PATH')
    
    # Data settings
    data_dir: Path = Path(os.getenv('DATA_DIR', 'data'))
    models_dir: Path = Path(os.getenv('MODELS_DIR', 'models'))
    
    def __post_init__(self):
        """Ensure directories exist."""
        self.data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """Load configuration from a file."""
        # TODO: Implement configuration file loading
        return cls()

class ConfigManager:
    """Configuration manager for the Model-Training application."""
    
    def __init__(self):
        self.config: Dict[str, Any] = {
            # Training settings
            "batch_size": 32,
            "learning_rate": 0.001,
            "num_epochs": 100,
            "gradient_accumulation_steps": 1,
            "mixed_precision": True,
            "gradient_clipping": 1.0,
            
            # Distributed training settings
            "use_distributed": False,
            "use_model_parallel": False,
            "use_pipeline_parallel": False,
            "use_tensor_parallel": False,
            "num_gpus": 1,
            
            # Visualization settings
            "visualization_dir": "visualizations",
            "update_interval": 5,  # seconds
            "save_interval": 100,  # steps
            
            # Model settings
            "model_type": "transformer",
            "model_config": {
                "hidden_size": 768,
                "num_attention_heads": 12,
                "num_hidden_layers": 6,
                "intermediate_size": 3072,
                "hidden_dropout_prob": 0.1,
                "attention_dropout_prob": 0.1,
                "max_position_embeddings": 512,
                "type_vocab_size": 2,
                "vocab_size": 30522,
            },
            
            # Data settings
            "data_dir": "data",
            "train_file": "train.txt",
            "eval_file": "eval.txt",
            "max_seq_length": 128,
            
            # Logging settings
            "log_dir": "logs",
            "log_level": "INFO",
            
            # GUI settings
            "theme": "default",
            "window_size": (1200, 800),
            "refresh_rate": 1.0,  # seconds
        }
    
    def load(self, config_path: str) -> None:
        """Load configuration from a JSON file."""
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                self.config.update(user_config)
                logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    def save(self, config_path: str) -> None:
        """Save current configuration to a JSON file."""
        try:
            config_dir = Path(config_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"Saved configuration to {config_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.config[key] = value
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """Update multiple configuration values."""
        self.config.update(config_dict)
    
    def validate(self) -> bool:
        """Validate the current configuration."""
        try:
            # Validate required directories
            for dir_key in ["visualization_dir", "data_dir", "log_dir"]:
                Path(self.config[dir_key]).mkdir(parents=True, exist_ok=True)
            
            # Validate numeric values
            assert self.config["batch_size"] > 0
            assert self.config["learning_rate"] > 0
            assert self.config["num_epochs"] > 0
            assert self.config["gradient_accumulation_steps"] > 0
            assert self.config["num_gpus"] > 0
            
            # Validate model configuration
            model_config = self.config["model_config"]
            assert model_config["hidden_size"] > 0
            assert model_config["num_attention_heads"] > 0
            assert model_config["num_hidden_layers"] > 0
            assert model_config["intermediate_size"] > 0
            assert 0 <= model_config["hidden_dropout_prob"] <= 1
            assert 0 <= model_config["attention_dropout_prob"] <= 1
            
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False 