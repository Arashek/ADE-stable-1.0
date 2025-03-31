import pytest
from pathlib import Path
from ade_model_training.visualizer import LearningVisualizer
from ade_model_training.config import Config

@pytest.fixture
def visualizer(tmp_path):
    config = Config()
    config.set("visualization_dir", str(tmp_path / "visualizations"))
    return LearningVisualizer(config)

def test_create_attention_map(visualizer, mock_plotly):
    """Test creating attention map visualization."""
    attention_data = {
        "layer_0": [[0.1, 0.2], [0.3, 0.4]],
        "layer_1": [[0.5, 0.6], [0.7, 0.8]]
    }
    output_path = visualizer.create_attention_map(attention_data)
    assert Path(output_path).exists()

def test_create_gradient_flow(visualizer, mock_plotly):
    """Test creating gradient flow visualization."""
    gradient_data = {
        "magnitude": [0.1, 0.2, 0.3],
        "direction": [0.4, 0.5, 0.6]
    }
    output_path = visualizer.create_gradient_flow(gradient_data)
    assert Path(output_path).exists()

def test_create_code_quality_metrics(visualizer, mock_plotly):
    """Test creating code quality metrics visualization."""
    metrics_data = {
        "complexity": [10, 15, 20],
        "maintainability": [80, 75, 70],
        "readability": [85, 80, 75]
    }
    output_path = visualizer.create_code_quality_metrics(metrics_data)
    assert Path(output_path).exists()

def test_create_performance_metrics(visualizer, mock_plotly):
    """Test creating performance metrics visualization."""
    metrics_data = {
        "memory": [1000, 2000, 3000],
        "cpu": [50, 60, 70],
        "gpu": [30, 40, 50]
    }
    output_path = visualizer.create_performance_metrics(metrics_data)
    assert Path(output_path).exists()

def test_create_model_comparison(visualizer, mock_plotly):
    """Test creating model comparison visualization."""
    comparison_data = {
        "model_1": {"rewards": [0.1, 0.2, 0.3], "accuracy": [0.8, 0.85, 0.9]},
        "model_2": {"rewards": [0.2, 0.3, 0.4], "accuracy": [0.85, 0.9, 0.95]}
    }
    output_path = visualizer.create_model_comparison(comparison_data)
    assert Path(output_path).exists()

def test_create_hyperparameter_analysis(visualizer, mock_plotly):
    """Test creating hyperparameter analysis visualization."""
    analysis_data = {
        "learning_rate": [0.001, 0.0001, 0.00001],
        "batch_size": [32, 64, 128],
        "rewards": [[0.1, 0.2, 0.3], [0.2, 0.3, 0.4], [0.3, 0.4, 0.5]],
        "accuracy": [[0.8, 0.85, 0.9], [0.85, 0.9, 0.95], [0.9, 0.95, 1.0]]
    }
    output_path = visualizer.create_hyperparameter_analysis(analysis_data)
    assert Path(output_path).exists()

def test_create_model_architecture(visualizer, mock_plotly):
    """Test creating model architecture visualization."""
    model = mock_plotly.graph_objects.Figure()
    output_path = visualizer.create_model_architecture(model)
    assert Path(output_path).exists()

def test_create_code_coverage_metrics(visualizer, mock_plotly):
    """Test creating code coverage metrics visualization."""
    coverage_data = {
        "line_coverage": [80, 85, 90],
        "branch_coverage": [70, 75, 80],
        "function_coverage": [90, 95, 100],
        "complexity": [10, 15, 20]
    }
    output_path = visualizer.create_code_coverage_metrics(coverage_data)
    assert Path(output_path).exists() 