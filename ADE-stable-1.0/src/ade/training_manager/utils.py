import logging
from pathlib import Path
from typing import Dict, Any, Optional
import json
import yaml
from datetime import datetime

def setup_logging(log_dir: str, level: int = logging.INFO) -> None:
    """Set up logging configuration."""
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path / f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler()
        ]
    )

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    with open(path, 'r') as f:
        if path.suffix == '.json':
            return json.load(f)
        elif path.suffix in ['.yml', '.yaml']:
            return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {path.suffix}")

def save_config(config: Dict[str, Any], config_path: str) -> None:
    """Save configuration to file."""
    path = Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        if path.suffix == '.json':
            json.dump(config, f, indent=2)
        elif path.suffix in ['.yml', '.yaml']:
            yaml.dump(config, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported configuration file format: {path.suffix}")

def create_default_configs() -> None:
    """Create default configuration files."""
    # Create config directory
    config_dir = Path('config')
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create AWS configuration
    aws_config = {
        'region': 'us-east-1',
        'access_key': None,
        'secret_key': None,
        'session_token': None,
        'profile_name': None,
        's3_bucket': 'ade-platform-models',
        'sagemaker_role': 'ade-platform-sagemaker-role',
        'endpoint_name': 'ade-platform-endpoint'
    }
    save_config(aws_config, config_dir / 'aws_config.json')
    
    # Create training configuration
    training_config = {
        'aws_config_path': 'config/aws_config.json',
        'output_dir': 'output',
        'checkpoint_dir': 'checkpoints',
        'log_dir': 'logs',
        'models': [
            {
                'name': 'code_assistant',
                'type': 'transformer',
                'base_model': 'microsoft/codebert-base',
                'max_length': 512,
                'batch_size': 8,
                'learning_rate': 2e-5,
                'num_train_epochs': 3,
                'warmup_steps': 1000,
                'weight_decay': 0.01,
                'gradient_accumulation_steps': 4,
                'fp16': True,
                'device_map': 'auto'
            }
        ],
        'datasets': {
            'code_completion': {
                'train_data_path': 'data/train/code_completion.json',
                'validation_data_path': 'data/validation/code_completion.json',
                'test_data_path': 'data/test/code_completion.json'
            },
            'tool_use': {
                'train_data_path': 'data/train/tool_use.json',
                'validation_data_path': 'data/validation/tool_use.json',
                'test_data_path': 'data/test/tool_use.json'
            }
        },
        'evaluation_metrics': ['accuracy', 'f1', 'rouge'],
        'early_stopping_patience': 3,
        'max_checkpoints': 5
    }
    save_config(training_config, config_dir / 'training_config.json')
    
    # Create sync configuration
    sync_config = {
        'platform_url': 'https://api.ade-platform.com',
        'api_key': None,
        'status_dir': 'sync_status',
        'retry_attempts': 3,
        'retry_delay': 5,
        'timeout': 30
    }
    save_config(sync_config, config_dir / 'sync_config.json')

def format_metrics(metrics: Dict[str, float]) -> str:
    """Format metrics for display."""
    lines = []
    for metric, value in metrics.items():
        lines.append(f"{metric}: {value:.4f}")
    return "\n".join(lines)

def get_git_info() -> Dict[str, str]:
    """Get Git repository information."""
    try:
        import git
        repo = git.Repo(search_parent_directories=True)
        return {
            'branch': repo.active_branch.name,
            'commit': repo.head.object.hexsha,
            'remote_url': repo.remotes.origin.url if repo.remotes else None
        }
    except Exception:
        return {
            'branch': 'unknown',
            'commit': 'unknown',
            'remote_url': None
        }

def get_system_info() -> Dict[str, str]:
    """Get system information."""
    import platform
    import psutil
    
    return {
        'os': platform.system(),
        'os_version': platform.version(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
        'gpu_available': torch.cuda.is_available(),
        'gpu_count': torch.cuda.device_count() if torch.cuda.is_available() else 0
    }

def create_experiment_tracking() -> Dict[str, Any]:
    """Create experiment tracking information."""
    return {
        'timestamp': datetime.now().isoformat(),
        'git_info': get_git_info(),
        'system_info': get_system_info(),
        'config': {
            'aws': load_config('config/aws_config.json'),
            'training': load_config('config/training_config.json'),
            'sync': load_config('config/sync_config.json')
        }
    }

def save_experiment_info(experiment_info: Dict[str, Any], output_dir: str) -> None:
    """Save experiment tracking information."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    save_config(
        experiment_info,
        output_path / f"experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    ) 