import pytest
from ade_model_training.exceptions import (
    ModelTrainingError,
    ConfigurationError,
    DataError,
    TrainingError,
    ValidationError,
    VisualizationError,
    ResourceError,
    DistributedError,
    CheckpointError,
    MetricsError
)

def test_model_training_error():
    """Test ModelTrainingError."""
    with pytest.raises(ModelTrainingError) as exc_info:
        raise ModelTrainingError("Test error")
    assert str(exc_info.value) == "Test error"

def test_configuration_error():
    """Test ConfigurationError."""
    with pytest.raises(ConfigurationError) as exc_info:
        raise ConfigurationError("Invalid configuration")
    assert str(exc_info.value) == "Invalid configuration"

def test_data_error():
    """Test DataError."""
    with pytest.raises(DataError) as exc_info:
        raise DataError("Data loading failed")
    assert str(exc_info.value) == "Data loading failed"

def test_training_error():
    """Test TrainingError."""
    with pytest.raises(TrainingError) as exc_info:
        raise TrainingError("Training failed")
    assert str(exc_info.value) == "Training failed"

def test_validation_error():
    """Test ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        raise ValidationError("Validation failed")
    assert str(exc_info.value) == "Validation failed"

def test_visualization_error():
    """Test VisualizationError."""
    with pytest.raises(VisualizationError) as exc_info:
        raise VisualizationError("Visualization failed")
    assert str(exc_info.value) == "Visualization failed"

def test_resource_error():
    """Test ResourceError."""
    with pytest.raises(ResourceError) as exc_info:
        raise ResourceError("Resource allocation failed")
    assert str(exc_info.value) == "Resource allocation failed"

def test_distributed_error():
    """Test DistributedError."""
    with pytest.raises(DistributedError) as exc_info:
        raise DistributedError("Distributed training failed")
    assert str(exc_info.value) == "Distributed training failed"

def test_checkpoint_error():
    """Test CheckpointError."""
    with pytest.raises(CheckpointError) as exc_info:
        raise CheckpointError("Checkpoint operation failed")
    assert str(exc_info.value) == "Checkpoint operation failed"

def test_metrics_error():
    """Test MetricsError."""
    with pytest.raises(MetricsError) as exc_info:
        raise MetricsError("Metrics calculation failed")
    assert str(exc_info.value) == "Metrics calculation failed"

def test_error_inheritance():
    """Test error inheritance hierarchy."""
    assert issubclass(ConfigurationError, ModelTrainingError)
    assert issubclass(DataError, ModelTrainingError)
    assert issubclass(TrainingError, ModelTrainingError)
    assert issubclass(ValidationError, ModelTrainingError)
    assert issubclass(VisualizationError, ModelTrainingError)
    assert issubclass(ResourceError, ModelTrainingError)
    assert issubclass(DistributedError, ModelTrainingError)
    assert issubclass(CheckpointError, ModelTrainingError)
    assert issubclass(MetricsError, ModelTrainingError)

def test_error_with_details():
    """Test error with additional details."""
    error = ModelTrainingError("Test error", details={"cause": "test"})
    assert str(error) == "Test error"
    assert error.details == {"cause": "test"}

def test_error_with_cause():
    """Test error with cause."""
    cause = Exception("Original error")
    error = ModelTrainingError("Test error", cause=cause)
    assert str(error) == "Test error"
    assert error.cause == cause

def test_error_attributes():
    """Test error attributes."""
    error = ModelTrainingError("Test error")
    assert hasattr(error, "message")
    assert hasattr(error, "details")
    assert hasattr(error, "cause")
    assert error.message == "Test error"
    assert error.details is None
    assert error.cause is None 