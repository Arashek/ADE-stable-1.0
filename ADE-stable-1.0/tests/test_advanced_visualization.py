import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from src.core.resource.advanced_visualization import AdvancedResourceVisualizer
from src.core.resource.resource_manager import ResourceManager, ResourceType, ResourceUsage, ResourceQuota
from src.core.monitoring.metrics import MetricsCollector
from src.core.monitoring.analytics import AnalyticsEngine

@pytest.fixture
def resource_manager():
    """Create a ResourceManager instance for testing"""
    quota = ResourceQuota(
        memory_limit=512,
        cpu_percent=80.0,
        disk_io=100,
        network_io=100,
        open_files=100,
        max_threads=4,
        timeout=30.0
    )
    return ResourceManager(
        quota=quota,
        metrics_collector=MetricsCollector(),
        analytics_engine=AnalyticsEngine()
    )

@pytest.fixture
def sample_usage_history(resource_manager):
    """Create sample resource usage history with anomalies"""
    current_time = datetime.now()
    
    # Create normal usage pattern
    for i in range(20):
        resource_manager.usage_history.append(ResourceUsage(
            memory_used=100 + i * 5,
            cpu_percent=20 + i * 2,
            disk_read=10 + i,
            disk_write=10 + i,
            network_sent=5 + i * 0.5,
            network_recv=5 + i * 0.5,
            open_files=10 + i,
            thread_count=2 + i * 0.5,
            swap_used=50 + i * 2,
            iops=100 + i * 10,
            gpu_memory_used=200 + i * 15,
            timestamp=current_time + timedelta(seconds=i)
        ))
    
    # Add some anomalies
    for i in range(5):
        resource_manager.usage_history.append(ResourceUsage(
            memory_used=500 + i * 100,  # Sudden spike in memory
            cpu_percent=90 + i * 2,      # High CPU usage
            disk_read=50 + i * 10,       # High disk I/O
            disk_write=50 + i * 10,
            network_sent=100 + i * 20,   # High network I/O
            network_recv=100 + i * 20,
            open_files=200 + i * 20,     # Too many open files
            thread_count=10 + i * 2,     # Too many threads
            swap_used=1000 + i * 100,    # High swap usage
            iops=1000 + i * 100,         # High IOPS
            gpu_memory_used=1000 + i * 100,  # High GPU memory
            timestamp=current_time + timedelta(seconds=20+i)
        ))

@pytest.fixture
def advanced_visualizer(resource_manager):
    """Create an AdvancedResourceVisualizer instance for testing"""
    return AdvancedResourceVisualizer(resource_manager)

def test_visualizer_initialization(advanced_visualizer):
    """Test AdvancedResourceVisualizer initialization"""
    assert advanced_visualizer is not None
    assert advanced_visualizer.resource_manager is not None
    assert advanced_visualizer.anomaly_detector is not None
    assert advanced_visualizer.scaler is not None
    assert advanced_visualizer.prediction_window == timedelta(minutes=5)

def test_prediction_timeline(advanced_visualizer, sample_usage_history):
    """Test resource usage prediction timeline"""
    # Test memory prediction
    fig = advanced_visualizer.create_prediction_timeline(ResourceType.MEMORY)
    assert fig is not None
    assert len(fig.data) == 2  # Actual and predicted traces
    assert fig.layout.title.text == "Resource Usage Prediction - memory"
    
    # Test CPU prediction
    fig = advanced_visualizer.create_prediction_timeline(ResourceType.CPU)
    assert fig is not None
    assert len(fig.data) == 2
    assert fig.layout.title.text == "Resource Usage Prediction - cpu"

def test_anomaly_detection(advanced_visualizer, sample_usage_history):
    """Test anomaly detection visualization"""
    fig = advanced_visualizer.create_anomaly_detection_plot()
    assert fig is not None
    assert len(fig.data) == 2  # Normal and anomaly points
    
    # Verify anomaly points are marked in red
    anomaly_trace = next(trace for trace in fig.data if trace.name == 'Anomaly')
    assert anomaly_trace.marker.color == 'red'
    assert anomaly_trace.marker.size == 12
    
    # Verify normal points are marked in blue
    normal_trace = next(trace for trace in fig.data if trace.name == 'Normal')
    assert normal_trace.marker.color == 'blue'
    assert normal_trace.marker.size == 8

def test_correlation_matrix(advanced_visualizer, sample_usage_history):
    """Test resource correlation matrix"""
    fig = advanced_visualizer.create_resource_correlation_matrix()
    assert fig is not None
    assert len(fig.data) == 1  # Single heatmap
    
    # Verify matrix dimensions
    z_data = fig.data[0].z
    assert z_data.shape[0] == z_data.shape[1]  # Square matrix
    
    # Verify correlation values are between -1 and 1
    assert np.all(z_data >= -1) and np.all(z_data <= 1)

def test_resource_forecast(advanced_visualizer, sample_usage_history):
    """Test resource usage forecast"""
    # Test memory forecast
    fig = advanced_visualizer.create_resource_forecast(ResourceType.MEMORY)
    assert fig is not None
    assert len(fig.data) == 3  # Actual, rolling mean, and confidence interval
    assert fig.layout.title.text == "Resource Usage Forecast - memory"
    
    # Test CPU forecast
    fig = advanced_visualizer.create_resource_forecast(ResourceType.CPU)
    assert fig is not None
    assert len(fig.data) == 3
    assert fig.layout.title.text == "Resource Usage Forecast - cpu"

def test_prometheus_metrics(advanced_visualizer):
    """Test Prometheus metrics integration"""
    # Verify all metrics are created
    assert "memory_usage" in advanced_visualizer.prometheus_metrics
    assert "cpu_usage" in advanced_visualizer.prometheus_metrics
    assert "disk_io" in advanced_visualizer.prometheus_metrics
    assert "network_io" in advanced_visualizer.prometheus_metrics
    assert "open_files" in advanced_visualizer.prometheus_metrics
    assert "thread_count" in advanced_visualizer.prometheus_metrics
    assert "swap_usage" in advanced_visualizer.prometheus_metrics
    assert "iops" in advanced_visualizer.prometheus_metrics
    assert "gpu_memory_usage" in advanced_visualizer.prometheus_metrics
    assert "anomaly_score" in advanced_visualizer.prometheus_metrics
    assert "predicted_usage" in advanced_visualizer.prometheus_metrics
    assert "violation_count" in advanced_visualizer.prometheus_metrics
    
    # Test metric updates
    usage = {
        "memory_used": 200,
        "cpu_percent": 50,
        "disk_read": 10,
        "disk_write": 10,
        "network_sent": 5,
        "network_recv": 5,
        "open_files": 20,
        "thread_count": 3,
        "swap_used": 100,
        "iops": 200,
        "gpu_memory_used": 400,
        "anomaly_score": 0.8,
        "predicted_usage": 250
    }
    
    advanced_visualizer.update_prometheus_metrics(usage)
    
    # Test violation counter
    initial_count = advanced_visualizer.prometheus_metrics["violation_count"]._value.get()
    advanced_visualizer.increment_violation_counter()
    assert advanced_visualizer.prometheus_metrics["violation_count"]._value.get() == initial_count + 1

def test_feature_column_mapping(advanced_visualizer):
    """Test resource type to feature column mapping"""
    assert advanced_visualizer._get_feature_column(ResourceType.MEMORY) == 'memory_used'
    assert advanced_visualizer._get_feature_column(ResourceType.CPU) == 'cpu_percent'
    assert advanced_visualizer._get_feature_column(ResourceType.DISK_IO) == 'disk_read'
    assert advanced_visualizer._get_feature_column(ResourceType.NETWORK_IO) == 'network_sent'
    assert advanced_visualizer._get_feature_column(ResourceType.OPEN_FILES) == 'open_files'
    assert advanced_visualizer._get_feature_column(ResourceType.THREADS) == 'thread_count'
    assert advanced_visualizer._get_feature_column(ResourceType.SWAP) == 'swap_used'
    assert advanced_visualizer._get_feature_column(ResourceType.IOPS) == 'iops'
    assert advanced_visualizer._get_feature_column(ResourceType.GPU) == 'gpu_memory_used'

def test_empty_data_handling(advanced_visualizer):
    """Test handling of empty data"""
    # Test prediction with empty data
    with pytest.raises(ValueError, match="No historical data available for prediction"):
        advanced_visualizer.create_prediction_timeline(ResourceType.MEMORY)
    
    # Test anomaly detection with empty data
    with pytest.raises(ValueError, match="No historical data available for anomaly detection"):
        advanced_visualizer.create_anomaly_detection_plot()
    
    # Test correlation matrix with empty data
    with pytest.raises(ValueError, match="No historical data available for correlation analysis"):
        advanced_visualizer.create_resource_correlation_matrix()
    
    # Test forecast with empty data
    with pytest.raises(ValueError, match="No historical data available for forecasting"):
        advanced_visualizer.create_resource_forecast(ResourceType.MEMORY) 