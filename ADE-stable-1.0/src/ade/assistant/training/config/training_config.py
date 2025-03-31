from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import json
import logging
from enum import Enum

class TrainingPhase(Enum):
    """Training phases for the model."""
    BASE_UNDERSTANDING = "base_understanding"
    COMPLETION_SPECIALIZATION = "completion_specialization"
    TOOL_USE_INTERACTION = "tool_use_interaction"
    SPECIALIZED_TRAINING = "specialized_training"

@dataclass
class ModelConfig:
    """Configuration for model architecture and training."""
    model_name: str
    model_type: str
    max_length: int
    batch_size: int
    learning_rate: float
    num_train_epochs: int
    warmup_steps: int
    weight_decay: float
    gradient_accumulation_steps: int
    fp16: bool = True
    device_map: str = "auto"

@dataclass
class DatasetConfig:
    """Configuration for dataset handling."""
    train_data_path: str
    validation_data_path: str
    test_data_path: str
    max_samples: Optional[int] = None
    shuffle: bool = True
    seed: int = 42

@dataclass
class PhaseConfig:
    """Configuration for a specific training phase."""
    phase: TrainingPhase
    model_config: ModelConfig
    dataset_config: DatasetConfig
    evaluation_metrics: List[str]
    checkpoint_dir: str
    output_dir: str
    early_stopping_patience: int = 3
    max_checkpoints: int = 5

@dataclass
class TrainingPipelineConfig:
    """Complete configuration for the training pipeline."""
    phases: List[PhaseConfig]
    aws_config_path: str
    s3_bucket: str
    sagemaker_role: str
    experiment_name: str
    log_dir: str
    tensorboard_dir: str
    wandb_project: Optional[str] = None
    wandb_entity: Optional[str] = None
    wandb_api_key: Optional[str] = None

class TrainingConfigManager:
    """Manages training configuration."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        
    def load_config(self) -> Optional[TrainingPipelineConfig]:
        """Load training configuration from file."""
        try:
            if not self.config_path.exists():
                self.logger.error(f"Config file not found: {self.config_path}")
                return None
                
            with open(self.config_path, "r") as f:
                config_data = json.load(f)
                
            # Convert nested dictionaries to appropriate dataclass instances
            phases = []
            for phase_data in config_data.get("phases", []):
                model_config = ModelConfig(**phase_data.get("model_config", {}))
                dataset_config = DatasetConfig(**phase_data.get("dataset_config", {}))
                phase_config = PhaseConfig(
                    phase=TrainingPhase(phase_data.get("phase")),
                    model_config=model_config,
                    dataset_config=dataset_config,
                    evaluation_metrics=phase_data.get("evaluation_metrics", []),
                    checkpoint_dir=phase_data.get("checkpoint_dir"),
                    output_dir=phase_data.get("output_dir"),
                    early_stopping_patience=phase_data.get("early_stopping_patience", 3),
                    max_checkpoints=phase_data.get("max_checkpoints", 5)
                )
                phases.append(phase_config)
                
            return TrainingPipelineConfig(
                phases=phases,
                aws_config_path=config_data.get("aws_config_path"),
                s3_bucket=config_data.get("s3_bucket"),
                sagemaker_role=config_data.get("sagemaker_role"),
                experiment_name=config_data.get("experiment_name"),
                log_dir=config_data.get("log_dir"),
                tensorboard_dir=config_data.get("tensorboard_dir"),
                wandb_project=config_data.get("wandb_project"),
                wandb_entity=config_data.get("wandb_entity"),
                wandb_api_key=config_data.get("wandb_api_key")
            )
            
        except Exception as e:
            self.logger.error(f"Failed to load training config: {e}")
            return None
            
    def save_config(self, config: TrainingPipelineConfig) -> bool:
        """Save training configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert dataclass instances to dictionaries
            config_dict = {
                "phases": [
                    {
                        "phase": phase.phase.value,
                        "model_config": phase.model_config.__dict__,
                        "dataset_config": phase.dataset_config.__dict__,
                        "evaluation_metrics": phase.evaluation_metrics,
                        "checkpoint_dir": phase.checkpoint_dir,
                        "output_dir": phase.output_dir,
                        "early_stopping_patience": phase.early_stopping_patience,
                        "max_checkpoints": phase.max_checkpoints
                    }
                    for phase in config.phases
                ],
                "aws_config_path": config.aws_config_path,
                "s3_bucket": config.s3_bucket,
                "sagemaker_role": config.sagemaker_role,
                "experiment_name": config.experiment_name,
                "log_dir": config.log_dir,
                "tensorboard_dir": config.tensorboard_dir,
                "wandb_project": config.wandb_project,
                "wandb_entity": config.wandb_entity,
                "wandb_api_key": config.wandb_api_key
            }
            
            with open(self.config_path, "w") as f:
                json.dump(config_dict, f, indent=2)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save training config: {e}")
            return False
            
    def create_default_config(self) -> TrainingPipelineConfig:
        """Create a default training configuration."""
        default_model_config = ModelConfig(
            model_name="microsoft/codebert-base",
            model_type="transformer",
            max_length=512,
            batch_size=8,
            learning_rate=2e-5,
            num_train_epochs=3,
            warmup_steps=1000,
            weight_decay=0.01,
            gradient_accumulation_steps=4
        )
        
        default_dataset_config = DatasetConfig(
            train_data_path="data/train",
            validation_data_path="data/validation",
            test_data_path="data/test"
        )
        
        phases = []
        for phase in TrainingPhase:
            phase_config = PhaseConfig(
                phase=phase,
                model_config=default_model_config,
                dataset_config=default_dataset_config,
                evaluation_metrics=["accuracy", "loss"],
                checkpoint_dir=f"checkpoints/{phase.value}",
                output_dir=f"outputs/{phase.value}"
            )
            phases.append(phase_config)
            
        return TrainingPipelineConfig(
            phases=phases,
            aws_config_path="config/aws_config.json",
            s3_bucket="ade-training-data",
            sagemaker_role="ade-sagemaker-role",
            experiment_name="ade-training",
            log_dir="logs",
            tensorboard_dir="runs"
        ) 