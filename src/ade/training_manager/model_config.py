from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional

@dataclass
class ModelConfig:
    """Configuration for model training components"""
    
    # Base paths
    base_dir: Path = Path(__file__).parent
    models_dir: Path = base_dir / "models"
    data_dir: Path = base_dir / "data"
    metrics_dir: Path = base_dir / "metrics"
    
    # Model configurations
    components: Dict[str, Dict[str, Any]] = {
        "code_understanding": {
            "model": "codellama/CodeLlama-34b-Instruct-hf",
            "data_path": data_dir / "training/code_understanding",
            "output_dir": models_dir / "code_understanding",
            "batch_size": 4,
            "learning_rate": 2e-5,
            "num_epochs": 3
        },
        "tool_use": {
            "model": "anthropic/claude-3-sonnet-20240229",
            "data_path": data_dir / "training/tool_use",
            "output_dir": models_dir / "tool_use",
            "batch_size": 4,
            "learning_rate": 2e-5,
            "num_epochs": 3
        },
        "planning": {
            "model": "anthropic/claude-3-sonnet-20240229",
            "data_path": data_dir / "training/planning",
            "output_dir": models_dir / "planning",
            "batch_size": 4,
            "learning_rate": 2e-5,
            "num_epochs": 3
        },
        "code_generation": {
            "model": "bigcode/starcoder2-33b",
            "data_path": data_dir / "training/code_generation",
            "output_dir": models_dir / "code_generation",
            "batch_size": 4,
            "learning_rate": 2e-5,
            "num_epochs": 3
        }
    }
    
    # Training settings
    max_length: int = 2048
    warmup_steps: int = 100
    weight_decay: float = 0.01
    gradient_accumulation_steps: int = 4
    
    # Evaluation settings
    eval_batch_size: int = 8
    eval_steps: int = 100
    save_steps: int = 500
    
    # Logging settings
    logging_steps: int = 10
    wandb_project: str = "ade-training"
    
    def __post_init__(self):
        """Create necessary directories"""
        for component in self.components.values():
            component["data_path"].mkdir(parents=True, exist_ok=True)
            component["output_dir"].mkdir(parents=True, exist_ok=True)
        
        self.metrics_dir.mkdir(parents=True, exist_ok=True) 