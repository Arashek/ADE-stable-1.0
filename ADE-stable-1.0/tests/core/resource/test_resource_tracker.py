import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
from src.core.resource.resource_tracker import ResourceTracker, ResourceMetrics

@pytest.fixture
def resource_tracker(tmp_path):
    return ResourceTracker(data_dir=str(tmp_path))

@pytest.fixture
def sample_metrics():
    return ResourceMetrics(
        timestamp=datetime.now(),
        cpu_percent=50.0,
        memory_percent=60.0,
        gpu_percent=70.0,
        disk_usage_percent=40.0,
        network_io={"bytes_sent": 1000, "bytes_recv": 2000},
        process_count=100,
        thread_count=200,
        model_name="gpt-4-turbo-preview",
        task_id="task-123"
    )

def test_initialize_tracker(resource_tracker):
    """Test tracker initialization"""
    assert hasattr(resource_tracker, "metrics_history")
    assert hasattr(resource_tracker, "current_metrics")
    assert hasattr(resource_tracker, "resource_limits")
    assert isinstance(resource_tracker.metrics_history, list)
    assert resource_tracker.current_metrics is None
    assert isinstance(resource_tracker.resource_limits, dict)

def test_set_resource_limit(resource_tracker):
    """Test setting resource limits"""
    resource_tracker.set_resource_limit("cpu", 80.0)
    resource_tracker.set_resource_limit("memory", 90.0)
    
    assert resource_tracker.resource_limits["cpu"] == 80.0
    assert resource_tracker.resource_limits["memory"] == 90.0

def test_collect_metrics(resource_tracker):
    """Test collecting metrics"""
    metrics = resource_tracker.collect_metrics(
        model_name="gpt-4-turbo-preview",
        task_id="task-123"
    )
    
    assert isinstance(metrics, ResourceMetrics)
    assert metrics.model_name == "gpt-4-turbo-preview"
    assert metrics.task_id == "task-123"
    assert 0 <= metrics.cpu_percent <= 100
    assert 0 <= metrics.memory_percent <= 100
    assert 0 <= metrics.disk_usage_percent <= 100
    assert isinstance(metrics.network_io, dict)
    assert metrics.process_count > 0
    assert metrics.thread_count > 0

def test_get_resource_summary(resource_tracker, sample_metrics):
    """Test getting resource summary"""
    resource_tracker.metrics_history.append(sample_metrics)
    summary = resource_tracker.get_resource_summary(timedelta(hours=1))
    
    assert "cpu" in summary
    assert "memory" in summary
    assert "disk" in summary
    assert "network" in summary
    assert "processes" in summary
    assert "threads" in summary
    assert "gpu" in summary
    
    # Check CPU metrics
    assert summary["cpu"]["avg_percent"] == 50.0
    assert summary["cpu"]["max_percent"] == 50.0
    assert summary["cpu"]["limit"] == 100
    
    # Check memory metrics
    assert summary["memory"]["avg_percent"] == 60.0
    assert summary["memory"]["max_percent"] == 60.0
    assert summary["memory"]["limit"] == 100
    
    # Check disk metrics
    assert summary["disk"]["avg_percent"] == 40.0
    assert summary["disk"]["max_percent"] == 40.0
    assert summary["disk"]["limit"] == 100
    
    # Check network metrics
    assert summary["network"]["total_sent"] == 1000
    assert summary["network"]["total_recv"] == 2000
    
    # Check process and thread metrics
    assert summary["processes"]["avg_count"] == 100
    assert summary["processes"]["max_count"] == 100
    assert summary["threads"]["avg_count"] == 200
    assert summary["threads"]["max_count"] == 200
    
    # Check GPU metrics
    assert summary["gpu"]["avg_percent"] == 70.0
    assert summary["gpu"]["max_percent"] == 70.0
    assert summary["gpu"]["limit"] == 100

def test_get_resource_alerts(resource_tracker, sample_metrics):
    """Test getting resource alerts"""
    # Test with normal metrics
    resource_tracker.current_metrics = sample_metrics
    alerts = resource_tracker.get_resource_alerts()
    assert len(alerts) == 0
    
    # Test with high CPU usage
    resource_tracker.set_resource_limit("cpu", 40.0)
    alerts = resource_tracker.get_resource_alerts()
    assert len(alerts) > 0
    assert any(a["type"] == "high_cpu_usage" for a in alerts)
    
    # Test with high memory usage
    resource_tracker.set_resource_limit("memory", 40.0)
    alerts = resource_tracker.get_resource_alerts()
    assert any(a["type"] == "high_memory_usage" for a in alerts)
    
    # Test with high GPU usage
    resource_tracker.set_resource_limit("gpu", 40.0)
    alerts = resource_tracker.get_resource_alerts()
    assert any(a["type"] == "high_gpu_usage" for a in alerts)
    
    # Test with high disk usage
    resource_tracker.set_resource_limit("disk", 40.0)
    alerts = resource_tracker.get_resource_alerts()
    assert any(a["type"] == "high_disk_usage" for a in alerts)

def test_get_resource_trends(resource_tracker, sample_metrics):
    """Test getting resource trends"""
    resource_tracker.metrics_history.append(sample_metrics)
    trends = resource_tracker.get_resource_trends(timedelta(hours=1))
    
    assert "timestamps" in trends
    assert "cpu_percent" in trends
    assert "memory_percent" in trends
    assert "disk_usage_percent" in trends
    assert "process_count" in trends
    assert "thread_count" in trends
    assert "gpu_percent" in trends
    
    assert len(trends["timestamps"]) == 1
    assert len(trends["cpu_percent"]) == 1
    assert len(trends["memory_percent"]) == 1
    assert len(trends["disk_usage_percent"]) == 1
    assert len(trends["process_count"]) == 1
    assert len(trends["thread_count"]) == 1
    assert len(trends["gpu_percent"]) == 1

def test_data_persistence(resource_tracker, sample_metrics):
    """Test data persistence"""
    # Record metrics and set limits
    resource_tracker.metrics_history.append(sample_metrics)
    resource_tracker.set_resource_limit("cpu", 80.0)
    
    # Create new tracker instance
    new_tracker = ResourceTracker(data_dir=resource_tracker.data_dir)
    
    # Check that data was persisted
    assert len(new_tracker.metrics_history) == 1
    assert new_tracker.resource_limits["cpu"] == 80.0

def test_error_handling(resource_tracker):
    """Test error handling"""
    # Test with invalid metrics
    with pytest.raises(Exception):
        resource_tracker.metrics_history.append(None)
    
    # Test with invalid resource limit
    with pytest.raises(Exception):
        resource_tracker.set_resource_limit(None, 80.0)

def test_data_validation(resource_tracker, sample_metrics):
    """Test data validation"""
    # Test with invalid timestamp
    invalid_metrics = ResourceMetrics(
        timestamp=None,  # Invalid timestamp
        cpu_percent=sample_metrics.cpu_percent,
        memory_percent=sample_metrics.memory_percent,
        gpu_percent=sample_metrics.gpu_percent,
        disk_usage_percent=sample_metrics.disk_usage_percent,
        network_io=sample_metrics.network_io,
        process_count=sample_metrics.process_count,
        thread_count=sample_metrics.thread_count,
        model_name=sample_metrics.model_name,
        task_id=sample_metrics.task_id
    )
    with pytest.raises(Exception):
        resource_tracker.metrics_history.append(invalid_metrics)
    
    # Test with invalid CPU percentage
    invalid_metrics = ResourceMetrics(
        timestamp=sample_metrics.timestamp,
        cpu_percent=-1.0,  # Invalid percentage
        memory_percent=sample_metrics.memory_percent,
        gpu_percent=sample_metrics.gpu_percent,
        disk_usage_percent=sample_metrics.disk_usage_percent,
        network_io=sample_metrics.network_io,
        process_count=sample_metrics.process_count,
        thread_count=sample_metrics.thread_count,
        model_name=sample_metrics.model_name,
        task_id=sample_metrics.task_id
    )
    with pytest.raises(Exception):
        resource_tracker.metrics_history.append(invalid_metrics) 