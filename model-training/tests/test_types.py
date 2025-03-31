import pytest
from typing import Dict, List, Optional, Union, Any
from ade_model_training.types import (
    # Training types
    Batch,
    Epoch,
    Step,
    LearningRate,
    Loss,
    Metrics,
    
    # Model types
    ModelConfig,
    ModelState,
    ModelOutput,
    ModelInput,
    
    # Data types
    Dataset,
    DataLoader,
    DataConfig,
    DataState,
    
    # Optimization types
    OptimizerConfig,
    OptimizerState,
    SchedulerConfig,
    SchedulerState,
    
    # Distributed types
    DistributedConfig,
    DistributedState,
    ProcessGroup,
    Rank,
    
    # Logging types
    LogConfig,
    LogState,
    LogLevel,
    LogFormat,
    
    # Checkpoint types
    CheckpointConfig,
    CheckpointState,
    CheckpointPath,
    
    # Visualization types
    VisualizationConfig,
    VisualizationState,
    PlotType,
    Figure,
    
    # Resource types
    ResourceConfig,
    ResourceState,
    ResourceUsage,
    ResourceLimit,
    
    # File types
    FileConfig,
    FileState,
    FilePath,
    FileFormat,
    
    # Time types
    TimeConfig,
    TimeState,
    Duration,
    Interval,
)

def test_training_types():
    """Test training-related types."""
    batch: Batch = {"input": [1, 2, 3], "target": [4, 5, 6]}
    epoch: Epoch = 1
    step: Step = 100
    lr: LearningRate = 0.001
    loss: Loss = 0.5
    metrics: Metrics = {"accuracy": 0.95, "loss": 0.5}
    
    assert isinstance(batch, dict)
    assert isinstance(epoch, int)
    assert isinstance(step, int)
    assert isinstance(lr, float)
    assert isinstance(loss, float)
    assert isinstance(metrics, dict)

def test_model_types():
    """Test model-related types."""
    config: ModelConfig = {
        "type": "transformer",
        "hidden_size": 768,
        "num_layers": 12,
        "num_heads": 12,
        "dropout": 0.1,
        "activation": "gelu"
    }
    state: ModelState = {
        "parameters": {},
        "buffers": {},
        "optimizer_state": {}
    }
    output: ModelOutput = {
        "logits": [[0.1, 0.2, 0.3]],
        "loss": 0.5,
        "metrics": {"accuracy": 0.95}
    }
    input_data: ModelInput = {
        "input_ids": [[1, 2, 3]],
        "attention_mask": [[1, 1, 1]]
    }
    
    assert isinstance(config, dict)
    assert isinstance(state, dict)
    assert isinstance(output, dict)
    assert isinstance(input_data, dict)

def test_data_types():
    """Test data-related types."""
    dataset: Dataset = [{"input": [1, 2, 3], "target": [4, 5, 6]}]
    dataloader: DataLoader = None  # Mock DataLoader
    config: DataConfig = {
        "batch_size": 32,
        "num_workers": 4,
        "pin_memory": True
    }
    state: DataState = {
        "current_epoch": 1,
        "current_step": 100,
        "total_steps": 1000
    }
    
    assert isinstance(dataset, list)
    assert dataloader is None
    assert isinstance(config, dict)
    assert isinstance(state, dict)

def test_optimization_types():
    """Test optimization-related types."""
    optimizer_config: OptimizerConfig = {
        "type": "adam",
        "learning_rate": 0.001,
        "weight_decay": 0.01
    }
    optimizer_state: OptimizerState = {
        "state": {},
        "param_groups": []
    }
    scheduler_config: SchedulerConfig = {
        "type": "cosine",
        "num_steps": 1000,
        "warmup_steps": 100
    }
    scheduler_state: SchedulerState = {
        "last_epoch": 0,
        "last_step": 0
    }
    
    assert isinstance(optimizer_config, dict)
    assert isinstance(optimizer_state, dict)
    assert isinstance(scheduler_config, dict)
    assert isinstance(scheduler_state, dict)

def test_distributed_types():
    """Test distributed-related types."""
    config: DistributedConfig = {
        "type": "ddp",
        "world_size": 4,
        "rank": 0
    }
    state: DistributedState = {
        "initialized": True,
        "process_group": None
    }
    process_group: ProcessGroup = None  # Mock ProcessGroup
    rank: Rank = 0
    
    assert isinstance(config, dict)
    assert isinstance(state, dict)
    assert process_group is None
    assert isinstance(rank, int)

def test_logging_types():
    """Test logging-related types."""
    config: LogConfig = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "train.log"
    }
    state: LogState = {
        "initialized": True,
        "handlers": []
    }
    level: LogLevel = "INFO"
    format_str: LogFormat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    assert isinstance(config, dict)
    assert isinstance(state, dict)
    assert isinstance(level, str)
    assert isinstance(format_str, str)

def test_checkpoint_types():
    """Test checkpoint-related types."""
    config: CheckpointConfig = {
        "dir": "checkpoints",
        "frequency": 1000,
        "max_checkpoints": 5
    }
    state: CheckpointState = {
        "last_checkpoint": None,
        "checkpoints": []
    }
    path: CheckpointPath = "checkpoints/model.pt"
    
    assert isinstance(config, dict)
    assert isinstance(state, dict)
    assert isinstance(path, str)

def test_visualization_types():
    """Test visualization-related types."""
    config: VisualizationConfig = {
        "dir": "visualizations",
        "frequency": 100,
        "figure_size": (10, 6)
    }
    state: VisualizationState = {
        "initialized": True,
        "plots": []
    }
    plot_type: PlotType = "line"
    figure: Figure = None  # Mock Figure
    
    assert isinstance(config, dict)
    assert isinstance(state, dict)
    assert isinstance(plot_type, str)
    assert figure is None

def test_resource_types():
    """Test resource-related types."""
    config: ResourceConfig = {
        "memory_limit": 1024**3,
        "cpu_limit": 80,
        "gpu_limit": 90
    }
    state: ResourceState = {
        "memory_usage": 512**3,
        "cpu_usage": 50,
        "gpu_usage": 60
    }
    usage: ResourceUsage = {
        "memory": 512**3,
        "cpu": 50,
        "gpu": 60
    }
    limit: ResourceLimit = {
        "memory": 1024**3,
        "cpu": 80,
        "gpu": 90
    }
    
    assert isinstance(config, dict)
    assert isinstance(state, dict)
    assert isinstance(usage, dict)
    assert isinstance(limit, dict)

def test_file_types():
    """Test file-related types."""
    config: FileConfig = {
        "model_file": "model.pt",
        "config_file": "config.json",
        "metrics_file": "metrics.json"
    }
    state: FileState = {
        "model_file": "model.pt",
        "config_file": "config.json",
        "metrics_file": "metrics.json"
    }
    path: FilePath = "model.pt"
    format_str: FileFormat = "pt"
    
    assert isinstance(config, dict)
    assert isinstance(state, dict)
    assert isinstance(path, str)
    assert isinstance(format_str, str)

def test_time_types():
    """Test time-related types."""
    config: TimeConfig = {
        "timeout": 3600,
        "interval": 60,
        "delay": 0
    }
    state: TimeState = {
        "start_time": 0,
        "current_time": 0,
        "elapsed_time": 0
    }
    duration: Duration = 3600
    interval: Interval = 60
    
    assert isinstance(config, dict)
    assert isinstance(state, dict)
    assert isinstance(duration, int)
    assert isinstance(interval, int) 