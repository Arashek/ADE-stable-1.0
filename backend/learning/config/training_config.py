from typing import Dict, Any, Optional
from pathlib import Path
import yaml
from dataclasses import dataclass
from ...config.logging_config import logger

@dataclass
class AlgorithmConfig:
    """Configuration for a specific RL algorithm"""
    name: str
    params: Dict[str, Any]
    enabled: bool = True

@dataclass
class TrainingConfig:
    """Configuration for the training process"""
    num_episodes: int
    batch_size: int
    learning_rate: float
    checkpoint_frequency: int
    parallel_training: bool
    algorithms: Dict[str, AlgorithmConfig]
    output_dir: str
    resume_from: Optional[str] = None
    max_workers: int = 4
    evaluation_frequency: int = 100
    early_stopping_patience: int = 10
    early_stopping_threshold: float = 0.001

class ConfigManager:
    """Manages training configurations"""
    
    def __init__(self, config_path: str = "config/training"):
        self.config_path = Path(config_path)
        self.config_path.mkdir(parents=True, exist_ok=True)
        
    def load_config(self, config_name: str) -> TrainingConfig:
        """Load configuration from YAML file"""
        try:
            config_file = self.config_path / f"{config_name}.yaml"
            if not config_file.exists():
                raise FileNotFoundError(f"Config file not found: {config_file}")
                
            with open(config_file, 'r') as f:
                config_dict = yaml.safe_load(f)
                
            return self._create_config(config_dict)
            
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise
            
    def save_config(self, config: TrainingConfig, config_name: str):
        """Save configuration to YAML file"""
        try:
            config_file = self.config_path / f"{config_name}.yaml"
            
            config_dict = {
                'num_episodes': config.num_episodes,
                'batch_size': config.batch_size,
                'learning_rate': config.learning_rate,
                'checkpoint_frequency': config.checkpoint_frequency,
                'parallel_training': config.parallel_training,
                'algorithms': {
                    name: {
                        'params': alg_config.params,
                        'enabled': alg_config.enabled
                    }
                    for name, alg_config in config.algorithms.items()
                },
                'output_dir': config.output_dir,
                'resume_from': config.resume_from,
                'max_workers': config.max_workers,
                'evaluation_frequency': config.evaluation_frequency,
                'early_stopping_patience': config.early_stopping_patience,
                'early_stopping_threshold': config.early_stopping_threshold
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False)
                
            logger.info(f"Saved config to {config_file}")
            
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            raise
            
    def _create_config(self, config_dict: Dict[str, Any]) -> TrainingConfig:
        """Create TrainingConfig from dictionary"""
        try:
            algorithms = {
                name: AlgorithmConfig(
                    name=name,
                    params=alg_config['params'],
                    enabled=alg_config.get('enabled', True)
                )
                for name, alg_config in config_dict['algorithms'].items()
            }
            
            return TrainingConfig(
                num_episodes=config_dict['num_episodes'],
                batch_size=config_dict['batch_size'],
                learning_rate=config_dict['learning_rate'],
                checkpoint_frequency=config_dict['checkpoint_frequency'],
                parallel_training=config_dict['parallel_training'],
                algorithms=algorithms,
                output_dir=config_dict['output_dir'],
                resume_from=config_dict.get('resume_from'),
                max_workers=config_dict.get('max_workers', 4),
                evaluation_frequency=config_dict.get('evaluation_frequency', 100),
                early_stopping_patience=config_dict.get('early_stopping_patience', 10),
                early_stopping_threshold=config_dict.get('early_stopping_threshold', 0.001)
            )
            
        except Exception as e:
            logger.error(f"Error creating config: {str(e)}")
            raise 