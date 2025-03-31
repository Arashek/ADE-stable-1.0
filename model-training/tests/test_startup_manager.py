import pytest
from unittest.mock import MagicMock, patch
from ade_model_training.startup_manager import LearningStartupManager
from ade_model_training.config import Config

@pytest.fixture
def startup_manager(tmp_path):
    config = Config()
    config.set("log_dir", str(tmp_path / "logs"))
    return LearningStartupManager(config)

def test_init(startup_manager):
    """Test startup manager initialization."""
    assert startup_manager.config is not None
    assert startup_manager.interface is None
    assert startup_manager.trainer is None
    assert startup_manager.visualizer is None

def test_initialize(startup_manager):
    """Test component initialization."""
    startup_manager.initialize()
    assert startup_manager.visualizer is not None
    assert startup_manager.trainer is not None

def test_should_use_distributed(startup_manager):
    """Test distributed training check."""
    # Test with distributed enabled
    startup_manager.config.set("use_distributed", True)
    assert startup_manager._should_use_distributed() is True
    
    # Test with distributed disabled
    startup_manager.config.set("use_distributed", False)
    assert startup_manager._should_use_distributed() is False

def test_initialize_distributed(startup_manager, mock_torch):
    """Test distributed training initialization."""
    startup_manager.config.set("use_distributed", True)
    startup_manager.config.set("num_gpus", 2)
    startup_manager._initialize_distributed()
    assert startup_manager.trainer is not None

def test_initialize_gui(startup_manager, mock_tkinter):
    """Test GUI initialization."""
    startup_manager._initialize_gui()
    assert startup_manager.interface is not None

def test_get_distributed_config(startup_manager):
    """Test distributed configuration generation."""
    config = startup_manager._get_distributed_config()
    assert "gradient_accumulation_steps" in config
    assert "mixed_precision" in config
    assert "gradient_clipping" in config
    assert "learning_rate_scheduler" in config

def test_cleanup(startup_manager):
    """Test resource cleanup."""
    startup_manager.initialize()
    startup_manager.cleanup()
    assert startup_manager.interface is None
    assert startup_manager.trainer is None
    assert startup_manager.visualizer is None

def test_error_handling(startup_manager):
    """Test error handling during initialization."""
    with patch('ade_model_training.startup_manager.LearningStartupManager._initialize_distributed') as mock_init:
        mock_init.side_effect = Exception("Test error")
        with pytest.raises(Exception):
            startup_manager.initialize()

def test_environment_setup(startup_manager):
    """Test environment setup."""
    startup_manager._setup_environment()
    assert startup_manager.config.get("log_dir") is not None
    assert startup_manager.config.get("visualization_dir") is not None

def test_component_initialization_order(startup_manager):
    """Test component initialization order."""
    startup_manager.initialize()
    assert startup_manager.visualizer is not None
    assert startup_manager.trainer is not None
    assert startup_manager.interface is not None

def test_config_validation(startup_manager):
    """Test configuration validation during initialization."""
    startup_manager.config.set("batch_size", -1)
    with pytest.raises(ValueError):
        startup_manager.initialize() 