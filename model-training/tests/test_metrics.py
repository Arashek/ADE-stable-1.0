import pytest
import numpy as np
from ade_model_training.metrics import MetricsTracker
from ade_model_training.config import Config

@pytest.fixture
def metrics_tracker(tmp_path):
    config = Config()
    config.set("log_dir", str(tmp_path / "logs"))
    return MetricsTracker(config)

def test_init(metrics_tracker):
    """Test metrics tracker initialization."""
    assert metrics_tracker.config is not None
    assert metrics_tracker.metrics == {}
    assert metrics_tracker.history == {}

def test_update_metrics(metrics_tracker):
    """Test metrics update."""
    metrics = {
        "loss": 0.5,
        "accuracy": 0.8,
        "learning_rate": 0.001
    }
    metrics_tracker.update(metrics)
    assert "loss" in metrics_tracker.metrics
    assert "accuracy" in metrics_tracker.metrics
    assert "learning_rate" in metrics_tracker.metrics

def test_get_metrics(metrics_tracker):
    """Test getting current metrics."""
    metrics = {
        "loss": 0.5,
        "accuracy": 0.8
    }
    metrics_tracker.update(metrics)
    current_metrics = metrics_tracker.get_metrics()
    assert current_metrics == metrics

def test_get_history(metrics_tracker):
    """Test getting metrics history."""
    metrics = {
        "loss": 0.5,
        "accuracy": 0.8
    }
    metrics_tracker.update(metrics)
    history = metrics_tracker.get_history()
    assert "loss" in history
    assert "accuracy" in history
    assert len(history["loss"]) == 1
    assert len(history["accuracy"]) == 1

def test_reset_metrics(metrics_tracker):
    """Test metrics reset."""
    metrics = {
        "loss": 0.5,
        "accuracy": 0.8
    }
    metrics_tracker.update(metrics)
    metrics_tracker.reset()
    assert metrics_tracker.metrics == {}
    assert metrics_tracker.history == {}

def test_calculate_statistics(metrics_tracker):
    """Test statistics calculation."""
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    stats = metrics_tracker.calculate_statistics(values)
    assert "mean" in stats
    assert "std" in stats
    assert "min" in stats
    assert "max" in stats
    assert stats["mean"] == np.mean(values)
    assert stats["std"] == np.std(values)
    assert stats["min"] == min(values)
    assert stats["max"] == max(values)

def test_save_metrics(metrics_tracker, tmp_path):
    """Test metrics saving."""
    metrics = {
        "loss": 0.5,
        "accuracy": 0.8
    }
    metrics_tracker.update(metrics)
    save_path = tmp_path / "metrics.json"
    metrics_tracker.save(str(save_path))
    assert save_path.exists()

def test_load_metrics(metrics_tracker, tmp_path):
    """Test metrics loading."""
    metrics = {
        "loss": 0.5,
        "accuracy": 0.8
    }
    metrics_tracker.update(metrics)
    save_path = tmp_path / "metrics.json"
    metrics_tracker.save(str(save_path))
    
    new_tracker = MetricsTracker(metrics_tracker.config)
    new_tracker.load(str(save_path))
    assert new_tracker.metrics == metrics

def test_plot_metrics(metrics_tracker, mock_plotly):
    """Test metrics plotting."""
    metrics = {
        "loss": 0.5,
        "accuracy": 0.8
    }
    metrics_tracker.update(metrics)
    plot = metrics_tracker.plot_metrics()
    assert plot is not None

def test_calculate_learning_rate(metrics_tracker):
    """Test learning rate calculation."""
    metrics_tracker.update({"learning_rate": 0.001})
    lr = metrics_tracker.calculate_learning_rate()
    assert lr == 0.001

def test_calculate_gradient_norm(metrics_tracker):
    """Test gradient norm calculation."""
    gradients = [1.0, 2.0, 3.0]
    norm = metrics_tracker.calculate_gradient_norm(gradients)
    assert norm == np.sqrt(sum(g * g for g in gradients))

def test_calculate_parameter_norm(metrics_tracker):
    """Test parameter norm calculation."""
    parameters = [1.0, 2.0, 3.0]
    norm = metrics_tracker.calculate_parameter_norm(parameters)
    assert norm == np.sqrt(sum(p * p for p in parameters))

def test_calculate_validation_metrics(metrics_tracker):
    """Test validation metrics calculation."""
    predictions = [0, 1, 0, 1]
    targets = [0, 1, 0, 1]
    metrics = metrics_tracker.calculate_validation_metrics(predictions, targets)
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics

def test_calculate_training_metrics(metrics_tracker):
    """Test training metrics calculation."""
    loss = 0.5
    metrics = metrics_tracker.calculate_training_metrics(loss)
    assert "loss" in metrics
    assert metrics["loss"] == loss

def test_calculate_performance_metrics(metrics_tracker):
    """Test performance metrics calculation."""
    metrics = metrics_tracker.calculate_performance_metrics()
    assert "memory_usage" in metrics
    assert "cpu_usage" in metrics
    assert "gpu_usage" in metrics 