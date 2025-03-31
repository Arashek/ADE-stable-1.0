import pytest
import numpy as np
import plotly.graph_objects as go
from ade_model_training.visualization import (
    # Training visualizations
    TrainingMetricsPlot,
    LearningCurvePlot,
    GradientFlowPlot,
    ParameterDistributionPlot,
    
    # Model visualizations
    ModelArchitecturePlot,
    ModelSizePlot,
    FLOPsPlot,
    MemoryUsagePlot,
    
    # Data visualizations
    DatasetDistributionPlot,
    BatchSizePlot,
    DataPipelinePlot,
    
    # Resource visualizations
    ResourceUsagePlot,
    ResourceUtilizationPlot,
    ResourceTrendPlot,
    
    # Time visualizations
    TrainingTimePlot,
    EpochTimePlot,
    StepTimePlot,
    
    # Quality visualizations
    CodeQualityPlot,
    TestCoveragePlot,
    ComplexityPlot,
    MaintainabilityPlot,
    ReadabilityPlot
)

@pytest.fixture
def visualizations():
    """Create test visualizations."""
    return {
        "training_metrics": TrainingMetricsPlot(),
        "learning_curve": LearningCurvePlot(),
        "gradient_flow": GradientFlowPlot(),
        "parameter_distribution": ParameterDistributionPlot(),
        "model_architecture": ModelArchitecturePlot(),
        "model_size": ModelSizePlot(),
        "flops": FLOPsPlot(),
        "memory_usage": MemoryUsagePlot(),
        "dataset_distribution": DatasetDistributionPlot(),
        "batch_size": BatchSizePlot(),
        "data_pipeline": DataPipelinePlot(),
        "resource_usage": ResourceUsagePlot(),
        "resource_utilization": ResourceUtilizationPlot(),
        "resource_trend": ResourceTrendPlot(),
        "training_time": TrainingTimePlot(),
        "epoch_time": EpochTimePlot(),
        "step_time": StepTimePlot(),
        "code_quality": CodeQualityPlot(),
        "test_coverage": TestCoveragePlot(),
        "complexity": ComplexityPlot(),
        "maintainability": MaintainabilityPlot(),
        "readability": ReadabilityPlot()
    }

def test_training_metrics_plot(visualizations):
    """Test training metrics plot."""
    plot = visualizations["training_metrics"]
    
    # Test initialization
    assert isinstance(plot, TrainingMetricsPlot)
    assert plot.title == "Training Metrics"
    assert plot.xlabel == "Step"
    assert plot.ylabel == "Value"
    
    # Test data update
    data = {
        "accuracy": [0.8, 0.85, 0.9],
        "loss": [0.5, 0.4, 0.3]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2
    assert fig.layout.title.text == "Training Metrics"
    assert fig.layout.xaxis.title.text == "Step"
    assert fig.layout.yaxis.title.text == "Value"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_learning_curve_plot(visualizations):
    """Test learning curve plot."""
    plot = visualizations["learning_curve"]
    
    # Test initialization
    assert isinstance(plot, LearningCurvePlot)
    assert plot.title == "Learning Curve"
    assert plot.xlabel == "Epoch"
    assert plot.ylabel == "Loss"
    
    # Test data update
    data = {
        "train_loss": [0.5, 0.4, 0.3],
        "val_loss": [0.6, 0.5, 0.4]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2
    assert fig.layout.title.text == "Learning Curve"
    assert fig.layout.xaxis.title.text == "Epoch"
    assert fig.layout.yaxis.title.text == "Loss"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_gradient_flow_plot(visualizations):
    """Test gradient flow plot."""
    plot = visualizations["gradient_flow"]
    
    # Test initialization
    assert isinstance(plot, GradientFlowPlot)
    assert plot.title == "Gradient Flow"
    assert plot.xlabel == "Layer"
    assert plot.ylabel == "Gradient Norm"
    
    # Test data update
    data = {
        "gradient_norms": [0.1, 0.2, 0.3, 0.4],
        "layer_names": ["layer1", "layer2", "layer3", "layer4"]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Gradient Flow"
    assert fig.layout.xaxis.title.text == "Layer"
    assert fig.layout.yaxis.title.text == "Gradient Norm"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_parameter_distribution_plot(visualizations):
    """Test parameter distribution plot."""
    plot = visualizations["parameter_distribution"]
    
    # Test initialization
    assert isinstance(plot, ParameterDistributionPlot)
    assert plot.title == "Parameter Distribution"
    assert plot.xlabel == "Value"
    assert plot.ylabel == "Count"
    
    # Test data update
    data = {
        "parameter_values": np.random.normal(0, 1, 1000),
        "parameter_names": ["weight", "bias"]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2
    assert fig.layout.title.text == "Parameter Distribution"
    assert fig.layout.xaxis.title.text == "Value"
    assert fig.layout.yaxis.title.text == "Count"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_model_architecture_plot(visualizations):
    """Test model architecture plot."""
    plot = visualizations["model_architecture"]
    
    # Test initialization
    assert isinstance(plot, ModelArchitecturePlot)
    assert plot.title == "Model Architecture"
    assert plot.xlabel == "Layer"
    assert plot.ylabel == "Output Size"
    
    # Test data update
    data = {
        "layer_sizes": [768, 768, 768, 768],
        "layer_names": ["embedding", "transformer1", "transformer2", "output"]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Model Architecture"
    assert fig.layout.xaxis.title.text == "Layer"
    assert fig.layout.yaxis.title.text == "Output Size"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_model_size_plot(visualizations):
    """Test model size plot."""
    plot = visualizations["model_size"]
    
    # Test initialization
    assert isinstance(plot, ModelSizePlot)
    assert plot.title == "Model Size"
    assert plot.xlabel == "Component"
    assert plot.ylabel == "Size (MB)"
    
    # Test data update
    data = {
        "component_sizes": [100, 200, 300],
        "component_names": ["embeddings", "transformer", "output"]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Model Size"
    assert fig.layout.xaxis.title.text == "Component"
    assert fig.layout.yaxis.title.text == "Size (MB)"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_flops_plot(visualizations):
    """Test FLOPS plot."""
    plot = visualizations["flops"]
    
    # Test initialization
    assert isinstance(plot, FLOPsPlot)
    assert plot.title == "FLOPS"
    assert plot.xlabel == "Operation"
    assert plot.ylabel == "FLOPS"
    
    # Test data update
    data = {
        "operation_flops": [1e9, 2e9, 3e9],
        "operation_names": ["attention", "ffn", "output"]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "FLOPS"
    assert fig.layout.xaxis.title.text == "Operation"
    assert fig.layout.yaxis.title.text == "FLOPS"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_memory_usage_plot(visualizations):
    """Test memory usage plot."""
    plot = visualizations["memory_usage"]
    
    # Test initialization
    assert isinstance(plot, MemoryUsagePlot)
    assert plot.title == "Memory Usage"
    assert plot.xlabel == "Time"
    assert plot.ylabel == "Memory (MB)"
    
    # Test data update
    data = {
        "memory_values": [512, 768, 1024],
        "timestamps": [0, 1, 2]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Memory Usage"
    assert fig.layout.xaxis.title.text == "Time"
    assert fig.layout.yaxis.title.text == "Memory (MB)"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_dataset_distribution_plot(visualizations):
    """Test dataset distribution plot."""
    plot = visualizations["dataset_distribution"]
    
    # Test initialization
    assert isinstance(plot, DatasetDistributionPlot)
    assert plot.title == "Dataset Distribution"
    assert plot.xlabel == "Class"
    assert plot.ylabel == "Count"
    
    # Test data update
    data = {
        "class_counts": [100, 200, 300],
        "class_names": ["class1", "class2", "class3"]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Dataset Distribution"
    assert fig.layout.xaxis.title.text == "Class"
    assert fig.layout.yaxis.title.text == "Count"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_batch_size_plot(visualizations):
    """Test batch size plot."""
    plot = visualizations["batch_size"]
    
    # Test initialization
    assert isinstance(plot, BatchSizePlot)
    assert plot.title == "Batch Size"
    assert plot.xlabel == "Step"
    assert plot.ylabel == "Size"
    
    # Test data update
    data = {
        "batch_sizes": [32, 64, 128],
        "steps": [0, 1, 2]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Batch Size"
    assert fig.layout.xaxis.title.text == "Step"
    assert fig.layout.yaxis.title.text == "Size"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_data_pipeline_plot(visualizations):
    """Test data pipeline plot."""
    plot = visualizations["data_pipeline"]
    
    # Test initialization
    assert isinstance(plot, DataPipelinePlot)
    assert plot.title == "Data Pipeline"
    assert plot.xlabel == "Stage"
    assert plot.ylabel == "Time (ms)"
    
    # Test data update
    data = {
        "stage_times": [10, 20, 30],
        "stage_names": ["load", "preprocess", "augment"]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Data Pipeline"
    assert fig.layout.xaxis.title.text == "Stage"
    assert fig.layout.yaxis.title.text == "Time (ms)"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_resource_usage_plot(visualizations):
    """Test resource usage plot."""
    plot = visualizations["resource_usage"]
    
    # Test initialization
    assert isinstance(plot, ResourceUsagePlot)
    assert plot.title == "Resource Usage"
    assert plot.xlabel == "Time"
    assert plot.ylabel == "Usage (%)"
    
    # Test data update
    data = {
        "cpu_usage": [50, 60, 70],
        "gpu_usage": [60, 70, 80],
        "memory_usage": [40, 50, 60],
        "timestamps": [0, 1, 2]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 3
    assert fig.layout.title.text == "Resource Usage"
    assert fig.layout.xaxis.title.text == "Time"
    assert fig.layout.yaxis.title.text == "Usage (%)"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_resource_utilization_plot(visualizations):
    """Test resource utilization plot."""
    plot = visualizations["resource_utilization"]
    
    # Test initialization
    assert isinstance(plot, ResourceUtilizationPlot)
    assert plot.title == "Resource Utilization"
    assert plot.xlabel == "Resource"
    assert plot.ylabel == "Utilization (%)"
    
    # Test data update
    data = {
        "utilization": [50, 60, 70],
        "resource_names": ["CPU", "GPU", "Memory"]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Resource Utilization"
    assert fig.layout.xaxis.title.text == "Resource"
    assert fig.layout.yaxis.title.text == "Utilization (%)"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_resource_trend_plot(visualizations):
    """Test resource trend plot."""
    plot = visualizations["resource_trend"]
    
    # Test initialization
    assert isinstance(plot, ResourceTrendPlot)
    assert plot.title == "Resource Trend"
    assert plot.xlabel == "Time"
    assert plot.ylabel == "Usage (%)"
    
    # Test data update
    data = {
        "cpu_trend": [50, 55, 60],
        "gpu_trend": [60, 65, 70],
        "memory_trend": [40, 45, 50],
        "timestamps": [0, 1, 2]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 3
    assert fig.layout.title.text == "Resource Trend"
    assert fig.layout.xaxis.title.text == "Time"
    assert fig.layout.yaxis.title.text == "Usage (%)"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_training_time_plot(visualizations):
    """Test training time plot."""
    plot = visualizations["training_time"]
    
    # Test initialization
    assert isinstance(plot, TrainingTimePlot)
    assert plot.title == "Training Time"
    assert plot.xlabel == "Epoch"
    assert plot.ylabel == "Time (s)"
    
    # Test data update
    data = {
        "epoch_times": [300, 280, 290],
        "epochs": [1, 2, 3]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Training Time"
    assert fig.layout.xaxis.title.text == "Epoch"
    assert fig.layout.yaxis.title.text == "Time (s)"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_epoch_time_plot(visualizations):
    """Test epoch time plot."""
    plot = visualizations["epoch_time"]
    
    # Test initialization
    assert isinstance(plot, EpochTimePlot)
    assert plot.title == "Epoch Time"
    assert plot.xlabel == "Step"
    assert plot.ylabel == "Time (ms)"
    
    # Test data update
    data = {
        "step_times": [100, 90, 110],
        "steps": [0, 1, 2]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Epoch Time"
    assert fig.layout.xaxis.title.text == "Step"
    assert fig.layout.yaxis.title.text == "Time (ms)"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_step_time_plot(visualizations):
    """Test step time plot."""
    plot = visualizations["step_time"]
    
    # Test initialization
    assert isinstance(plot, StepTimePlot)
    assert plot.title == "Step Time"
    assert plot.xlabel == "Operation"
    assert plot.ylabel == "Time (ms)"
    
    # Test data update
    data = {
        "operation_times": [10, 20, 30],
        "operation_names": ["forward", "backward", "optimize"]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Step Time"
    assert fig.layout.xaxis.title.text == "Operation"
    assert fig.layout.yaxis.title.text == "Time (ms)"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_code_quality_plot(visualizations):
    """Test code quality plot."""
    plot = visualizations["code_quality"]
    
    # Test initialization
    assert isinstance(plot, CodeQualityPlot)
    assert plot.title == "Code Quality"
    assert plot.xlabel == "Metric"
    assert plot.ylabel == "Score"
    
    # Test data update
    data = {
        "metric_scores": [0.8, 0.7, 0.9],
        "metric_names": ["complexity", "maintainability", "readability"]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Code Quality"
    assert fig.layout.xaxis.title.text == "Metric"
    assert fig.layout.yaxis.title.text == "Score"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_test_coverage_plot(visualizations):
    """Test test coverage plot."""
    plot = visualizations["test_coverage"]
    
    # Test initialization
    assert isinstance(plot, TestCoveragePlot)
    assert plot.title == "Test Coverage"
    assert plot.xlabel == "Module"
    assert plot.ylabel == "Coverage (%)"
    
    # Test data update
    data = {
        "coverage_scores": [80, 90, 70],
        "module_names": ["module1", "module2", "module3"]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Test Coverage"
    assert fig.layout.xaxis.title.text == "Module"
    assert fig.layout.yaxis.title.text == "Coverage (%)"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_complexity_plot(visualizations):
    """Test complexity plot."""
    plot = visualizations["complexity"]
    
    # Test initialization
    assert isinstance(plot, ComplexityPlot)
    assert plot.title == "Code Complexity"
    assert plot.xlabel == "Function"
    assert plot.ylabel == "Complexity"
    
    # Test data update
    data = {
        "complexity_scores": [5, 10, 15],
        "function_names": ["func1", "func2", "func3"]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Code Complexity"
    assert fig.layout.xaxis.title.text == "Function"
    assert fig.layout.yaxis.title.text == "Complexity"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_maintainability_plot(visualizations):
    """Test maintainability plot."""
    plot = visualizations["maintainability"]
    
    # Test initialization
    assert isinstance(plot, MaintainabilityPlot)
    assert plot.title == "Code Maintainability"
    assert plot.xlabel == "Module"
    assert plot.ylabel == "Score"
    
    # Test data update
    data = {
        "maintainability_scores": [0.8, 0.7, 0.9],
        "module_names": ["module1", "module2", "module3"]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Code Maintainability"
    assert fig.layout.xaxis.title.text == "Module"
    assert fig.layout.yaxis.title.text == "Score"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]})

def test_readability_plot(visualizations):
    """Test readability plot."""
    plot = visualizations["readability"]
    
    # Test initialization
    assert isinstance(plot, ReadabilityPlot)
    assert plot.title == "Code Readability"
    assert plot.xlabel == "File"
    assert plot.ylabel == "Score"
    
    # Test data update
    data = {
        "readability_scores": [0.9, 0.8, 0.85],
        "file_names": ["file1.py", "file2.py", "file3.py"]
    }
    plot.update(data)
    
    # Test figure creation
    fig = plot.create_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Code Readability"
    assert fig.layout.xaxis.title.text == "File"
    assert fig.layout.yaxis.title.text == "Score"
    
    # Test data validation
    with pytest.raises(ValueError):
        plot.update({"invalid": [1, 2, 3]}) 