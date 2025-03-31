import pytest
from ade_model_training.constants import (
    # Training constants
    DEFAULT_BATCH_SIZE,
    DEFAULT_LEARNING_RATE,
    DEFAULT_NUM_EPOCHS,
    DEFAULT_WARMUP_STEPS,
    DEFAULT_GRADIENT_ACCUMULATION_STEPS,
    DEFAULT_MAX_GRAD_NORM,
    DEFAULT_WEIGHT_DECAY,
    DEFAULT_MIXED_PRECISION,
    
    # Model constants
    DEFAULT_MODEL_TYPE,
    DEFAULT_HIDDEN_SIZE,
    DEFAULT_NUM_LAYERS,
    DEFAULT_NUM_HEADS,
    DEFAULT_DROPOUT,
    DEFAULT_ACTIVATION,
    
    # Data constants
    DEFAULT_TRAIN_SPLIT,
    DEFAULT_VAL_SPLIT,
    DEFAULT_TEST_SPLIT,
    DEFAULT_RANDOM_SEED,
    DEFAULT_NUM_WORKERS,
    DEFAULT_PIN_MEMORY,
    
    # Optimization constants
    DEFAULT_OPTIMIZER_TYPE,
    DEFAULT_SCHEDULER_TYPE,
    DEFAULT_LOSS_TYPE,
    DEFAULT_METRICS,
    
    # Distributed constants
    DEFAULT_DISTRIBUTED_TYPE,
    DEFAULT_NUM_GPUS,
    DEFAULT_WORLD_SIZE,
    DEFAULT_RANK,
    DEFAULT_LOCAL_RANK,
    
    # Logging constants
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_FILE,
    DEFAULT_TENSORBOARD_DIR,
    
    # Checkpoint constants
    DEFAULT_CHECKPOINT_DIR,
    DEFAULT_CHECKPOINT_FREQUENCY,
    DEFAULT_MAX_CHECKPOINTS,
    
    # Visualization constants
    DEFAULT_VISUALIZATION_DIR,
    DEFAULT_PLOT_FREQUENCY,
    DEFAULT_FIGURE_SIZE,
    DEFAULT_COLOR_PALETTE,
    
    # Resource constants
    DEFAULT_MEMORY_LIMIT,
    DEFAULT_CPU_LIMIT,
    DEFAULT_GPU_LIMIT,
    DEFAULT_DISK_LIMIT,
    
    # File constants
    DEFAULT_CONFIG_FILE,
    DEFAULT_MODEL_FILE,
    DEFAULT_TOKENIZER_FILE,
    DEFAULT_VOCAB_FILE,
    DEFAULT_METRICS_FILE,
    
    # Time constants
    DEFAULT_TIMEOUT,
    DEFAULT_INTERVAL,
    DEFAULT_DELAY,
    DEFAULT_DURATION,
)

def test_training_constants():
    """Test training-related constants."""
    assert isinstance(DEFAULT_BATCH_SIZE, int)
    assert isinstance(DEFAULT_LEARNING_RATE, float)
    assert isinstance(DEFAULT_NUM_EPOCHS, int)
    assert isinstance(DEFAULT_WARMUP_STEPS, int)
    assert isinstance(DEFAULT_GRADIENT_ACCUMULATION_STEPS, int)
    assert isinstance(DEFAULT_MAX_GRAD_NORM, float)
    assert isinstance(DEFAULT_WEIGHT_DECAY, float)
    assert isinstance(DEFAULT_MIXED_PRECISION, bool)

def test_model_constants():
    """Test model-related constants."""
    assert isinstance(DEFAULT_MODEL_TYPE, str)
    assert isinstance(DEFAULT_HIDDEN_SIZE, int)
    assert isinstance(DEFAULT_NUM_LAYERS, int)
    assert isinstance(DEFAULT_NUM_HEADS, int)
    assert isinstance(DEFAULT_DROPOUT, float)
    assert isinstance(DEFAULT_ACTIVATION, str)

def test_data_constants():
    """Test data-related constants."""
    assert isinstance(DEFAULT_TRAIN_SPLIT, float)
    assert isinstance(DEFAULT_VAL_SPLIT, float)
    assert isinstance(DEFAULT_TEST_SPLIT, float)
    assert isinstance(DEFAULT_RANDOM_SEED, int)
    assert isinstance(DEFAULT_NUM_WORKERS, int)
    assert isinstance(DEFAULT_PIN_MEMORY, bool)

def test_optimization_constants():
    """Test optimization-related constants."""
    assert isinstance(DEFAULT_OPTIMIZER_TYPE, str)
    assert isinstance(DEFAULT_SCHEDULER_TYPE, str)
    assert isinstance(DEFAULT_LOSS_TYPE, str)
    assert isinstance(DEFAULT_METRICS, list)

def test_distributed_constants():
    """Test distributed-related constants."""
    assert isinstance(DEFAULT_DISTRIBUTED_TYPE, str)
    assert isinstance(DEFAULT_NUM_GPUS, int)
    assert isinstance(DEFAULT_WORLD_SIZE, int)
    assert isinstance(DEFAULT_RANK, int)
    assert isinstance(DEFAULT_LOCAL_RANK, int)

def test_logging_constants():
    """Test logging-related constants."""
    assert isinstance(DEFAULT_LOG_LEVEL, str)
    assert isinstance(DEFAULT_LOG_FORMAT, str)
    assert isinstance(DEFAULT_LOG_FILE, str)
    assert isinstance(DEFAULT_TENSORBOARD_DIR, str)

def test_checkpoint_constants():
    """Test checkpoint-related constants."""
    assert isinstance(DEFAULT_CHECKPOINT_DIR, str)
    assert isinstance(DEFAULT_CHECKPOINT_FREQUENCY, int)
    assert isinstance(DEFAULT_MAX_CHECKPOINTS, int)

def test_visualization_constants():
    """Test visualization-related constants."""
    assert isinstance(DEFAULT_VISUALIZATION_DIR, str)
    assert isinstance(DEFAULT_PLOT_FREQUENCY, int)
    assert isinstance(DEFAULT_FIGURE_SIZE, tuple)
    assert isinstance(DEFAULT_COLOR_PALETTE, list)

def test_resource_constants():
    """Test resource-related constants."""
    assert isinstance(DEFAULT_MEMORY_LIMIT, int)
    assert isinstance(DEFAULT_CPU_LIMIT, int)
    assert isinstance(DEFAULT_GPU_LIMIT, int)
    assert isinstance(DEFAULT_DISK_LIMIT, int)

def test_file_constants():
    """Test file-related constants."""
    assert isinstance(DEFAULT_CONFIG_FILE, str)
    assert isinstance(DEFAULT_MODEL_FILE, str)
    assert isinstance(DEFAULT_TOKENIZER_FILE, str)
    assert isinstance(DEFAULT_VOCAB_FILE, str)
    assert isinstance(DEFAULT_METRICS_FILE, str)

def test_time_constants():
    """Test time-related constants."""
    assert isinstance(DEFAULT_TIMEOUT, int)
    assert isinstance(DEFAULT_INTERVAL, int)
    assert isinstance(DEFAULT_DELAY, int)
    assert isinstance(DEFAULT_DURATION, int)

def test_constant_values():
    """Test constant values are within expected ranges."""
    assert 0 < DEFAULT_BATCH_SIZE <= 1024
    assert 0 < DEFAULT_LEARNING_RATE <= 1
    assert 0 < DEFAULT_NUM_EPOCHS <= 1000
    assert 0 <= DEFAULT_WARMUP_STEPS <= 10000
    assert 0 < DEFAULT_GRADIENT_ACCUMULATION_STEPS <= 100
    assert 0 < DEFAULT_MAX_GRAD_NORM <= 10
    assert 0 <= DEFAULT_WEIGHT_DECAY <= 1
    assert 0 < DEFAULT_HIDDEN_SIZE <= 4096
    assert 0 < DEFAULT_NUM_LAYERS <= 100
    assert 0 < DEFAULT_NUM_HEADS <= 64
    assert 0 <= DEFAULT_DROPOUT <= 1
    assert 0 < DEFAULT_TRAIN_SPLIT < 1
    assert 0 < DEFAULT_VAL_SPLIT < 1
    assert 0 < DEFAULT_TEST_SPLIT < 1
    assert 0 <= DEFAULT_RANDOM_SEED <= 2**32 - 1
    assert 0 <= DEFAULT_NUM_WORKERS <= 16
    assert 0 < DEFAULT_NUM_GPUS <= 16
    assert 0 <= DEFAULT_RANK < DEFAULT_WORLD_SIZE
    assert 0 <= DEFAULT_LOCAL_RANK < DEFAULT_NUM_GPUS
    assert 0 < DEFAULT_CHECKPOINT_FREQUENCY <= 1000
    assert 0 < DEFAULT_MAX_CHECKPOINTS <= 10
    assert 0 < DEFAULT_PLOT_FREQUENCY <= 1000
    assert 0 < DEFAULT_MEMORY_LIMIT <= 2**64
    assert 0 < DEFAULT_CPU_LIMIT <= 100
    assert 0 < DEFAULT_GPU_LIMIT <= 100
    assert 0 < DEFAULT_DISK_LIMIT <= 2**64
    assert 0 < DEFAULT_TIMEOUT <= 3600
    assert 0 < DEFAULT_INTERVAL <= 3600
    assert 0 <= DEFAULT_DELAY <= 3600
    assert 0 < DEFAULT_DURATION <= 3600 