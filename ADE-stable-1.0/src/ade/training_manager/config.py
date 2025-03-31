from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import yaml

@dataclass
class AWSConfig:
    """AWS configuration settings."""
    region: str
    access_key: str
    secret_key: str
    session_token: Optional[str] = None
    profile_name: Optional[str] = None
    s3_bucket: str
    sagemaker_role: str
    endpoint_name: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AWSConfig':
        """Create AWSConfig from dictionary."""
        return cls(
            region=data['region'],
            access_key=data['access_key'],
            secret_key=data['secret_key'],
            session_token=data.get('session_token'),
            profile_name=data.get('profile_name'),
            s3_bucket=data['s3_bucket'],
            sagemaker_role=data['sagemaker_role'],
            endpoint_name=data['endpoint_name']
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert AWSConfig to dictionary."""
        return {
            'region': self.region,
            'access_key': self.access_key,
            'secret_key': self.secret_key,
            'session_token': self.session_token,
            'profile_name': self.profile_name,
            's3_bucket': self.s3_bucket,
            'sagemaker_role': self.sagemaker_role,
            'endpoint_name': self.endpoint_name
        }

@dataclass
class ModelConfig:
    """Model configuration settings."""
    name: str
    type: str
    base_model: str
    max_length: int
    batch_size: int
    learning_rate: float
    num_train_epochs: int
    warmup_steps: int
    weight_decay: float
    gradient_accumulation_steps: int
    fp16: bool
    device_map: str
    scheduler_type: str = 'linear'  # 'linear', 'cosine', or 'one_cycle'
    steps_per_epoch: Optional[int] = None
    gradient_checkpointing: bool = False
    mixed_precision: bool = True
    gradient_clipping: Optional[float] = 1.0
    label_smoothing: float = 0.0
    max_grad_norm: float = 1.0
    warmup_ratio: Optional[float] = None
    lr_scheduler_kwargs: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelConfig':
        """Create ModelConfig from dictionary."""
        return cls(
            name=data['name'],
            type=data['type'],
            base_model=data['base_model'],
            max_length=data['max_length'],
            batch_size=data['batch_size'],
            learning_rate=data['learning_rate'],
            num_train_epochs=data['num_train_epochs'],
            warmup_steps=data['warmup_steps'],
            weight_decay=data['weight_decay'],
            gradient_accumulation_steps=data['gradient_accumulation_steps'],
            fp16=data['fp16'],
            device_map=data['device_map'],
            scheduler_type=data.get('scheduler_type', 'linear'),
            steps_per_epoch=data.get('steps_per_epoch'),
            gradient_checkpointing=data.get('gradient_checkpointing', False),
            mixed_precision=data.get('mixed_precision', True),
            gradient_clipping=data.get('gradient_clipping', 1.0),
            label_smoothing=data.get('label_smoothing', 0.0),
            max_grad_norm=data.get('max_grad_norm', 1.0),
            warmup_ratio=data.get('warmup_ratio'),
            lr_scheduler_kwargs=data.get('lr_scheduler_kwargs')
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert ModelConfig to dictionary."""
        return {
            'name': self.name,
            'type': self.type,
            'base_model': self.base_model,
            'max_length': self.max_length,
            'batch_size': self.batch_size,
            'learning_rate': self.learning_rate,
            'num_train_epochs': self.num_train_epochs,
            'warmup_steps': self.warmup_steps,
            'weight_decay': self.weight_decay,
            'gradient_accumulation_steps': self.gradient_accumulation_steps,
            'fp16': self.fp16,
            'device_map': self.device_map,
            'scheduler_type': self.scheduler_type,
            'steps_per_epoch': self.steps_per_epoch,
            'gradient_checkpointing': self.gradient_checkpointing,
            'mixed_precision': self.mixed_precision,
            'gradient_clipping': self.gradient_clipping,
            'label_smoothing': self.label_smoothing,
            'max_grad_norm': self.max_grad_norm,
            'warmup_ratio': self.warmup_ratio,
            'lr_scheduler_kwargs': self.lr_scheduler_kwargs
        }

@dataclass
class DatasetConfig:
    """Dataset configuration settings."""
    train_data_path: str
    validation_data_path: str
    test_data_path: str
    sample_limit: Optional[int] = None
    shuffle: bool = True
    seed: int = 42
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatasetConfig':
        """Create DatasetConfig from dictionary."""
        return cls(
            train_data_path=data['train_data_path'],
            validation_data_path=data['validation_data_path'],
            test_data_path=data['test_data_path'],
            sample_limit=data.get('sample_limit'),
            shuffle=data.get('shuffle', True),
            seed=data.get('seed', 42)
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert DatasetConfig to dictionary."""
        return {
            'train_data_path': self.train_data_path,
            'validation_data_path': self.validation_data_path,
            'test_data_path': self.test_data_path,
            'sample_limit': self.sample_limit,
            'shuffle': self.shuffle,
            'seed': self.seed
        }

@dataclass
class TrainingConfig:
    """Main training configuration settings."""
    aws_config_path: str
    output_dir: str
    checkpoint_dir: str
    log_dir: str
    models: List[ModelConfig]
    datasets: Dict[str, DatasetConfig]
    evaluation_metrics: List[str]
    early_stopping_patience: int
    max_checkpoints: int
    wandb_project: Optional[str] = None
    wandb_entity: Optional[str] = None
    wandb_run_name: Optional[str] = None
    wandb_tags: Optional[List[str]] = None
    wandb_mode: str = 'online'
    seed: int = 42
    num_workers: int = 4
    pin_memory: bool = True
    prefetch_factor: int = 2
    persistent_workers: bool = True
    use_amp: bool = True
    amp_dtype: str = 'float16'
    amp_opt_level: str = 'O1'
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrainingConfig':
        """Create TrainingConfig from dictionary."""
        return cls(
            aws_config_path=data['aws_config_path'],
            output_dir=data['output_dir'],
            checkpoint_dir=data['checkpoint_dir'],
            log_dir=data['log_dir'],
            models=[ModelConfig.from_dict(m) for m in data['models']],
            datasets={k: DatasetConfig.from_dict(v) for k, v in data['datasets'].items()},
            evaluation_metrics=data['evaluation_metrics'],
            early_stopping_patience=data['early_stopping_patience'],
            max_checkpoints=data['max_checkpoints'],
            wandb_project=data.get('wandb_project'),
            wandb_entity=data.get('wandb_entity'),
            wandb_run_name=data.get('wandb_run_name'),
            wandb_tags=data.get('wandb_tags'),
            wandb_mode=data.get('wandb_mode', 'online'),
            seed=data.get('seed', 42),
            num_workers=data.get('num_workers', 4),
            pin_memory=data.get('pin_memory', True),
            prefetch_factor=data.get('prefetch_factor', 2),
            persistent_workers=data.get('persistent_workers', True),
            use_amp=data.get('use_amp', True),
            amp_dtype=data.get('amp_dtype', 'float16'),
            amp_opt_level=data.get('amp_opt_level', 'O1')
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert TrainingConfig to dictionary."""
        return {
            'aws_config_path': self.aws_config_path,
            'output_dir': self.output_dir,
            'checkpoint_dir': self.checkpoint_dir,
            'log_dir': self.log_dir,
            'models': [m.to_dict() for m in self.models],
            'datasets': {k: v.to_dict() for k, v in self.datasets.items()},
            'evaluation_metrics': self.evaluation_metrics,
            'early_stopping_patience': self.early_stopping_patience,
            'max_checkpoints': self.max_checkpoints,
            'wandb_project': self.wandb_project,
            'wandb_entity': self.wandb_entity,
            'wandb_run_name': self.wandb_run_name,
            'wandb_tags': self.wandb_tags,
            'wandb_mode': self.wandb_mode,
            'seed': self.seed,
            'num_workers': self.num_workers,
            'pin_memory': self.pin_memory,
            'prefetch_factor': self.prefetch_factor,
            'persistent_workers': self.persistent_workers,
            'use_amp': self.use_amp,
            'amp_dtype': self.amp_dtype,
            'amp_opt_level': self.amp_opt_level
        }
        
    @classmethod
    def create_default(cls) -> 'TrainingConfig':
        """Create a default training configuration."""
        return cls(
            aws_config_path='config/aws_config.json',
            output_dir='output',
            checkpoint_dir='checkpoints',
            log_dir='logs',
            models=[
                ModelConfig(
                    name='code_assistant',
                    type='transformer',
                    base_model='microsoft/codebert-base',
                    max_length=512,
                    batch_size=8,
                    learning_rate=2e-5,
                    num_train_epochs=3,
                    warmup_steps=1000,
                    weight_decay=0.01,
                    gradient_accumulation_steps=4,
                    fp16=True,
                    device_map='auto',
                    scheduler_type='cosine',
                    gradient_checkpointing=True,
                    mixed_precision=True,
                    gradient_clipping=1.0,
                    label_smoothing=0.1,
                    max_grad_norm=1.0,
                    warmup_ratio=0.1
                )
            ],
            datasets={
                'code_completion': DatasetConfig(
                    train_data_path='data/train/code_completion.json',
                    validation_data_path='data/validation/code_completion.json',
                    test_data_path='data/test/code_completion.json'
                ),
                'tool_use': DatasetConfig(
                    train_data_path='data/train/tool_use.json',
                    validation_data_path='data/validation/tool_use.json',
                    test_data_path='data/test/tool_use.json'
                )
            },
            evaluation_metrics=[
                'accuracy', 'f1', 'precision', 'recall', 'roc_auc',
                'mse', 'mae', 'rouge', 'bleu', 'perplexity'
            ],
            early_stopping_patience=3,
            max_checkpoints=5,
            wandb_project='ade-platform-training',
            wandb_mode='online',
            seed=42,
            num_workers=4,
            pin_memory=True,
            prefetch_factor=2,
            persistent_workers=True,
            use_amp=True,
            amp_dtype='float16',
            amp_opt_level='O1'
        )

def load_config(config_path: str) -> Any:
    """Load configuration from file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    with open(path, 'r') as f:
        if path.suffix == '.json':
            data = json.load(f)
        elif path.suffix in ['.yml', '.yaml']:
            data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {path.suffix}")
            
    if path.name == 'aws_config.json':
        return AWSConfig.from_dict(data)
    else:
        return TrainingConfig.from_dict(data)

def save_config(config: Any, config_path: str) -> None:
    """Save configuration to file."""
    path = Path(config_path)
    data = config.to_dict()
    
    with open(path, 'w') as f:
        if path.suffix == '.json':
            json.dump(data, f, indent=2)
        elif path.suffix in ['.yml', '.yaml']:
            yaml.dump(data, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported configuration file format: {path.suffix}") 