from dataclasses import dataclass
from typing import Optional, Dict, Any
import json
import yaml
from pathlib import Path

@dataclass
class ModelConfig:
    """Configuration class for model parameters"""
    name: str
    model_type: str
    hidden_size: int = 768
    num_layers: int = 12
    num_heads: int = 12
    ffn_size: int = 3072
    max_position: int = 2048
    vocab_size: int = 50257
    batch_size: int = 4
    learning_rate: float = 2e-5
    epochs: int = 3
    warmup_steps: int = 100
    weight_decay: float = 0.01
    gradient_clipping: float = 1.0
    custom_params: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        config_dict = {
            "name": self.name,
            "model_type": self.model_type,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "num_heads": self.num_heads,
            "ffn_size": self.ffn_size,
            "max_position": self.max_position,
            "vocab_size": self.vocab_size,
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "epochs": self.epochs,
            "warmup_steps": self.warmup_steps,
            "weight_decay": self.weight_decay,
            "gradient_clipping": self.gradient_clipping
        }
        if self.custom_params:
            config_dict.update(self.custom_params)
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ModelConfig':
        """Create config from dictionary"""
        return cls(**config_dict)
    
    def save(self, path: str, format: str = 'json'):
        """Save configuration to file"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        config_dict = self.to_dict()
        if format.lower() == 'json':
            with open(path, 'w') as f:
                json.dump(config_dict, f, indent=4)
        elif format.lower() == 'yaml':
            with open(path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @classmethod
    def load(cls, path: str, format: str = 'json') -> 'ModelConfig':
        """Load configuration from file"""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
            
        if format.lower() == 'json':
            with open(path, 'r') as f:
                config_dict = json.load(f)
        elif format.lower() == 'yaml':
            with open(path, 'r') as f:
                config_dict = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        return cls.from_dict(config_dict)
    
    def update(self, **kwargs):
        """Update configuration parameters"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                if self.custom_params is None:
                    self.custom_params = {}
                self.custom_params[key] = value 