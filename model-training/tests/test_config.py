import json
import os
import pytest
from pathlib import Path
from ade_model_training.config import Config

@pytest.fixture
def config():
    """Create a test configuration."""
    return Config()

@pytest.fixture
def config_file(tmp_path):
    """Create a temporary configuration file."""
    config_data = {
        "training": {
            "batch_size": 32,
            "learning_rate": 0.001,
            "num_epochs": 10,
            "warmup_steps": 1000,
            "gradient_accumulation_steps": 4,
            "max_grad_norm": 1.0,
            "weight_decay": 0.01,
            "mixed_precision": True
        },
        "model": {
            "type": "transformer",
            "hidden_size": 768,
            "num_layers": 12,
            "num_heads": 12,
            "dropout": 0.1,
            "activation": "gelu"
        },
        "data": {
            "train_split": 0.8,
            "val_split": 0.1,
            "test_split": 0.1,
            "random_seed": 42,
            "num_workers": 4,
            "pin_memory": True
        },
        "optimization": {
            "optimizer_type": "adam",
            "scheduler_type": "cosine",
            "loss_type": "cross_entropy",
            "metrics": ["accuracy", "loss"]
        },
        "distributed": {
            "type": "ddp",
            "num_gpus": 4,
            "world_size": 4,
            "rank": 0,
            "local_rank": 0
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "train.log",
            "tensorboard_dir": "runs"
        },
        "checkpoint": {
            "dir": "checkpoints",
            "frequency": 1000,
            "max_checkpoints": 5
        },
        "visualization": {
            "dir": "visualizations",
            "frequency": 100,
            "figure_size": [10, 6],
            "color_palette": ["#1f77b4", "#ff7f0e", "#2ca02c"]
        },
        "resource": {
            "memory_limit": 1024**3,
            "cpu_limit": 80,
            "gpu_limit": 90,
            "disk_limit": 1024**3
        },
        "file": {
            "config_file": "config.json",
            "model_file": "model.pt",
            "tokenizer_file": "tokenizer.json",
            "vocab_file": "vocab.txt",
            "metrics_file": "metrics.json"
        },
        "time": {
            "timeout": 3600,
            "interval": 60,
            "delay": 0,
            "duration": 3600
        }
    }
    
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config_data, f)
    return config_path

def test_init(config):
    """Test Config initialization."""
    assert isinstance(config, Config)
    assert hasattr(config, "training")
    assert hasattr(config, "model")
    assert hasattr(config, "data")
    assert hasattr(config, "optimization")
    assert hasattr(config, "distributed")
    assert hasattr(config, "logging")
    assert hasattr(config, "checkpoint")
    assert hasattr(config, "visualization")
    assert hasattr(config, "resource")
    assert hasattr(config, "file")
    assert hasattr(config, "time")

def test_load_config(config, config_file):
    """Test loading configuration from file."""
    config.load(config_file)
    
    # Test training config
    assert config.training.batch_size == 32
    assert config.training.learning_rate == 0.001
    assert config.training.num_epochs == 10
    assert config.training.warmup_steps == 1000
    assert config.training.gradient_accumulation_steps == 4
    assert config.training.max_grad_norm == 1.0
    assert config.training.weight_decay == 0.01
    assert config.training.mixed_precision is True
    
    # Test model config
    assert config.model.type == "transformer"
    assert config.model.hidden_size == 768
    assert config.model.num_layers == 12
    assert config.model.num_heads == 12
    assert config.model.dropout == 0.1
    assert config.model.activation == "gelu"
    
    # Test data config
    assert config.data.train_split == 0.8
    assert config.data.val_split == 0.1
    assert config.data.test_split == 0.1
    assert config.data.random_seed == 42
    assert config.data.num_workers == 4
    assert config.data.pin_memory is True
    
    # Test optimization config
    assert config.optimization.optimizer_type == "adam"
    assert config.optimization.scheduler_type == "cosine"
    assert config.optimization.loss_type == "cross_entropy"
    assert config.optimization.metrics == ["accuracy", "loss"]
    
    # Test distributed config
    assert config.distributed.type == "ddp"
    assert config.distributed.num_gpus == 4
    assert config.distributed.world_size == 4
    assert config.distributed.rank == 0
    assert config.distributed.local_rank == 0
    
    # Test logging config
    assert config.logging.level == "INFO"
    assert config.logging.format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    assert config.logging.file == "train.log"
    assert config.logging.tensorboard_dir == "runs"
    
    # Test checkpoint config
    assert config.checkpoint.dir == "checkpoints"
    assert config.checkpoint.frequency == 1000
    assert config.checkpoint.max_checkpoints == 5
    
    # Test visualization config
    assert config.visualization.dir == "visualizations"
    assert config.visualization.frequency == 100
    assert config.visualization.figure_size == [10, 6]
    assert config.visualization.color_palette == ["#1f77b4", "#ff7f0e", "#2ca02c"]
    
    # Test resource config
    assert config.resource.memory_limit == 1024**3
    assert config.resource.cpu_limit == 80
    assert config.resource.gpu_limit == 90
    assert config.resource.disk_limit == 1024**3
    
    # Test file config
    assert config.file.config_file == "config.json"
    assert config.file.model_file == "model.pt"
    assert config.file.tokenizer_file == "tokenizer.json"
    assert config.file.vocab_file == "vocab.txt"
    assert config.file.metrics_file == "metrics.json"
    
    # Test time config
    assert config.time.timeout == 3600
    assert config.time.interval == 60
    assert config.time.delay == 0
    assert config.time.duration == 3600

def test_save_config(config, config_file, tmp_path):
    """Test saving configuration to file."""
    # Load config
    config.load(config_file)
    
    # Save config
    save_path = tmp_path / "config_save.json"
    config.save(save_path)
    
    # Load saved config
    new_config = Config()
    new_config.load(save_path)
    
    # Compare configs
    assert config.training.batch_size == new_config.training.batch_size
    assert config.training.learning_rate == new_config.training.learning_rate
    assert config.training.num_epochs == new_config.training.num_epochs
    assert config.model.type == new_config.model.type
    assert config.model.hidden_size == new_config.model.hidden_size
    assert config.data.train_split == new_config.data.train_split
    assert config.optimization.optimizer_type == new_config.optimization.optimizer_type
    assert config.distributed.type == new_config.distributed.type
    assert config.logging.level == new_config.logging.level
    assert config.checkpoint.dir == new_config.checkpoint.dir
    assert config.visualization.dir == new_config.visualization.dir
    assert config.resource.memory_limit == new_config.resource.memory_limit
    assert config.file.config_file == new_config.file.config_file
    assert config.time.timeout == new_config.time.timeout

def test_update_config(config, config_file):
    """Test updating configuration."""
    # Load config
    config.load(config_file)
    
    # Update config
    config.update({
        "training": {
            "batch_size": 64,
            "learning_rate": 0.0005
        },
        "model": {
            "hidden_size": 1024
        }
    })
    
    # Check updates
    assert config.training.batch_size == 64
    assert config.training.learning_rate == 0.0005
    assert config.model.hidden_size == 1024
    
    # Check unchanged values
    assert config.training.num_epochs == 10
    assert config.model.num_layers == 12
    assert config.data.train_split == 0.8
    assert config.optimization.optimizer_type == "adam"
    assert config.distributed.type == "ddp"
    assert config.logging.level == "INFO"
    assert config.checkpoint.dir == "checkpoints"
    assert config.visualization.dir == "visualizations"
    assert config.resource.memory_limit == 1024**3
    assert config.file.config_file == "config.json"
    assert config.time.timeout == 3600

def test_validate_config(config, config_file):
    """Test configuration validation."""
    # Load valid config
    config.load(config_file)
    assert config.validate() is True
    
    # Test invalid batch size
    config.training.batch_size = -1
    with pytest.raises(ValueError):
        config.validate()
    
    # Test invalid learning rate
    config.training.batch_size = 32
    config.training.learning_rate = -0.001
    with pytest.raises(ValueError):
        config.validate()
    
    # Test invalid number of epochs
    config.training.learning_rate = 0.001
    config.training.num_epochs = 0
    with pytest.raises(ValueError):
        config.validate()
    
    # Test invalid model type
    config.training.num_epochs = 10
    config.model.type = "invalid"
    with pytest.raises(ValueError):
        config.validate()
    
    # Test invalid optimizer type
    config.model.type = "transformer"
    config.optimization.optimizer_type = "invalid"
    with pytest.raises(ValueError):
        config.validate()

def test_get_config_dict(config, config_file):
    """Test getting configuration as dictionary."""
    # Load config
    config.load(config_file)
    
    # Get config dict
    config_dict = config.get_dict()
    
    # Check dictionary structure
    assert isinstance(config_dict, dict)
    assert "training" in config_dict
    assert "model" in config_dict
    assert "data" in config_dict
    assert "optimization" in config_dict
    assert "distributed" in config_dict
    assert "logging" in config_dict
    assert "checkpoint" in config_dict
    assert "visualization" in config_dict
    assert "resource" in config_dict
    assert "file" in config_dict
    assert "time" in config_dict
    
    # Check values
    assert config_dict["training"]["batch_size"] == 32
    assert config_dict["model"]["type"] == "transformer"
    assert config_dict["data"]["train_split"] == 0.8
    assert config_dict["optimization"]["optimizer_type"] == "adam"
    assert config_dict["distributed"]["type"] == "ddp"
    assert config_dict["logging"]["level"] == "INFO"
    assert config_dict["checkpoint"]["dir"] == "checkpoints"
    assert config_dict["visualization"]["dir"] == "visualizations"
    assert config_dict["resource"]["memory_limit"] == 1024**3
    assert config_dict["file"]["config_file"] == "config.json"
    assert config_dict["time"]["timeout"] == 3600

def test_create_directories(config, config_file, tmp_path):
    """Test creating configuration directories."""
    # Load config
    config.load(config_file)
    
    # Update paths to use tmp_path
    config.logging.file = str(tmp_path / "train.log")
    config.logging.tensorboard_dir = str(tmp_path / "runs")
    config.checkpoint.dir = str(tmp_path / "checkpoints")
    config.visualization.dir = str(tmp_path / "visualizations")
    
    # Create directories
    config.create_directories()
    
    # Check directories exist
    assert os.path.exists(tmp_path / "runs")
    assert os.path.exists(tmp_path / "checkpoints")
    assert os.path.exists(tmp_path / "visualizations")
    
    # Check log file is created
    assert os.path.exists(tmp_path / "train.log") 