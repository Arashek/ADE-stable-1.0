import pytest
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch
from ade_model_training.logger import Logger
from ade_model_training.config import Config

@pytest.fixture
def logger(tmp_path):
    config = Config()
    config.set("log_dir", str(tmp_path / "logs"))
    return Logger(config)

def test_init(logger):
    """Test logger initialization."""
    assert logger.config is not None
    assert logger.logger is not None
    assert isinstance(logger.logger, logging.Logger)

def test_setup_logging(logger, tmp_path):
    """Test logging setup."""
    log_file = tmp_path / "logs" / "test.log"
    logger.setup_logging(str(log_file))
    assert log_file.exists()

def test_log_info(logger):
    """Test info level logging."""
    with patch.object(logger.logger, 'info') as mock_info:
        logger.info("Test message")
        mock_info.assert_called_once_with("Test message")

def test_log_error(logger):
    """Test error level logging."""
    with patch.object(logger.logger, 'error') as mock_error:
        logger.error("Test error")
        mock_error.assert_called_once_with("Test error")

def test_log_warning(logger):
    """Test warning level logging."""
    with patch.object(logger.logger, 'warning') as mock_warning:
        logger.warning("Test warning")
        mock_warning.assert_called_once_with("Test warning")

def test_log_debug(logger):
    """Test debug level logging."""
    with patch.object(logger.logger, 'debug') as mock_debug:
        logger.debug("Test debug")
        mock_debug.assert_called_once_with("Test debug")

def test_log_exception(logger):
    """Test exception logging."""
    with patch.object(logger.logger, 'exception') as mock_exception:
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            logger.log_exception(e)
        mock_exception.assert_called_once()

def test_log_metrics(logger):
    """Test metrics logging."""
    metrics = {
        "loss": 0.5,
        "accuracy": 0.8
    }
    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_metrics(metrics)
        assert mock_info.call_count == 2

def test_log_training_progress(logger):
    """Test training progress logging."""
    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_training_progress(epoch=1, step=100, loss=0.5)
        mock_info.assert_called_once()

def test_log_validation_progress(logger):
    """Test validation progress logging."""
    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_validation_progress(epoch=1, loss=0.5, accuracy=0.8)
        mock_info.assert_called_once()

def test_log_model_info(logger):
    """Test model information logging."""
    model = MagicMock()
    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_model_info(model)
        mock_info.assert_called()

def test_log_config(logger):
    """Test configuration logging."""
    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_config()
        mock_info.assert_called()

def test_log_memory_usage(logger):
    """Test memory usage logging."""
    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_memory_usage()
        mock_info.assert_called_once()

def test_log_gpu_usage(logger):
    """Test GPU usage logging."""
    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_gpu_usage()
        mock_info.assert_called_once()

def test_log_checkpoint(logger):
    """Test checkpoint logging."""
    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_checkpoint(epoch=1, step=100)
        mock_info.assert_called_once()

def test_log_hyperparameters(logger):
    """Test hyperparameters logging."""
    hyperparameters = {
        "learning_rate": 0.001,
        "batch_size": 32
    }
    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_hyperparameters(hyperparameters)
        assert mock_info.call_count == 2

def test_log_distributed_info(logger):
    """Test distributed training information logging."""
    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_distributed_info(rank=0, world_size=4)
        mock_info.assert_called_once()

def test_log_performance_metrics(logger):
    """Test performance metrics logging."""
    metrics = {
        "memory_usage": 1000,
        "cpu_usage": 50,
        "gpu_usage": 30
    }
    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_performance_metrics(metrics)
        assert mock_info.call_count == 3 