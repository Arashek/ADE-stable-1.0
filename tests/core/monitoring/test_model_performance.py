import pytest
from datetime import datetime, timedelta
from src.core.monitoring.model_performance import ModelPerformanceMonitor, PerformanceMetrics

@pytest.fixture
def performance_monitor():
    return ModelPerformanceMonitor(window_size=100)

@pytest.fixture
def sample_metrics():
    return PerformanceMetrics(
        model_name="gpt-4-turbo-preview",
        timestamp=datetime.now(),
        latency=0.5,
        throughput=10,
        error_rate=0.02,
        success_rate=0.98,
        resource_usage={"cpu": 0.7, "memory": 0.6},
        cost_per_request=0.01,
        token_usage={"input": 100, "output": 50}
    )

def test_initialize_metrics(performance_monitor):
    """Test metrics initialization"""
    assert hasattr(performance_monitor, "metrics")
    assert "latency" in performance_monitor.metrics
    assert "throughput" in performance_monitor.metrics
    assert "error_rate" in performance_monitor.metrics
    assert "success_rate" in performance_monitor.metrics
    assert "resource_usage" in performance_monitor.metrics
    assert "cost_per_request" in performance_monitor.metrics
    assert "token_usage" in performance_monitor.metrics

def test_record_metrics(performance_monitor, sample_metrics):
    """Test recording metrics"""
    performance_monitor.record_metrics(sample_metrics)
    
    assert sample_metrics.model_name in performance_monitor.current_metrics
    assert sample_metrics.model_name in performance_monitor.metrics_history
    assert len(performance_monitor.metrics_history[sample_metrics.model_name]) == 1

def test_update_aggregated_metrics(performance_monitor, sample_metrics):
    """Test updating aggregated metrics"""
    performance_monitor.record_metrics(sample_metrics)
    
    # Check latency
    assert len(performance_monitor.metrics["latency"][sample_metrics.model_name]) == 1
    assert performance_monitor.metrics["latency"][sample_metrics.model_name][0] == 0.5
    
    # Check throughput
    assert performance_monitor.metrics["throughput"][sample_metrics.model_name] == 1
    
    # Check error and success rates
    assert performance_monitor.metrics["error_rate"][sample_metrics.model_name] == 1
    assert performance_monitor.metrics["success_rate"][sample_metrics.model_name] == 1
    
    # Check resource usage
    assert len(performance_monitor.metrics["resource_usage"][sample_metrics.model_name]) == 1
    assert performance_monitor.metrics["resource_usage"][sample_metrics.model_name][0] == {"cpu": 0.7, "memory": 0.6}
    
    # Check cost per request
    assert len(performance_monitor.metrics["cost_per_request"][sample_metrics.model_name]) == 1
    assert performance_monitor.metrics["cost_per_request"][sample_metrics.model_name][0] == 0.01
    
    # Check token usage
    assert performance_monitor.metrics["token_usage"][sample_metrics.model_name]["input"] == 100
    assert performance_monitor.metrics["token_usage"][sample_metrics.model_name]["output"] == 50

def test_get_model_performance(performance_monitor, sample_metrics):
    """Test getting model performance"""
    performance_monitor.record_metrics(sample_metrics)
    performance = performance_monitor.get_model_performance(sample_metrics.model_name)
    
    assert "current" in performance
    assert "statistics" in performance
    
    # Check current metrics
    current = performance["current"]
    assert current["latency"] == 0.5
    assert current["throughput"] == 10
    assert current["error_rate"] == 0.02
    assert current["success_rate"] == 0.98
    assert current["resource_usage"] == {"cpu": 0.7, "memory": 0.6}
    assert current["cost_per_request"] == 0.01
    assert current["token_usage"] == {"input": 100, "output": 50}
    
    # Check statistics
    stats = performance["statistics"]
    assert stats["avg_latency"] == 0.5
    assert stats["p95_latency"] == 0.5
    assert stats["avg_cost"] == 0.01
    assert stats["total_requests"] == 1
    assert stats["error_rate"] == 1.0
    assert stats["success_rate"] == 1.0

def test_get_performance_alerts(performance_monitor, sample_metrics):
    """Test getting performance alerts"""
    # Test with normal metrics
    performance_monitor.record_metrics(sample_metrics)
    alerts = performance_monitor.get_performance_alerts(sample_metrics.model_name)
    assert len(alerts) == 0
    
    # Test with high error rate
    high_error_metrics = PerformanceMetrics(
        model_name=sample_metrics.model_name,
        timestamp=datetime.now(),
        latency=0.5,
        throughput=10,
        error_rate=0.06,  # Above 5% threshold
        success_rate=0.94,
        resource_usage={"cpu": 0.7, "memory": 0.6},
        cost_per_request=0.01,
        token_usage={"input": 100, "output": 50}
    )
    performance_monitor.record_metrics(high_error_metrics)
    alerts = performance_monitor.get_performance_alerts(sample_metrics.model_name)
    assert len(alerts) > 0
    assert any(a["type"] == "high_error_rate" for a in alerts)

def test_get_performance_summary(performance_monitor, sample_metrics):
    """Test getting performance summary"""
    performance_monitor.record_metrics(sample_metrics)
    summary = performance_monitor.get_performance_summary(timedelta(hours=1))
    
    assert sample_metrics.model_name in summary
    model_summary = summary[sample_metrics.model_name]
    
    assert model_summary["total_requests"] == 1
    assert model_summary["avg_latency"] == 0.5
    assert model_summary["p95_latency"] == 0.5
    assert model_summary["avg_cost"] == 0.01
    assert model_summary["total_cost"] == 0.01
    assert model_summary["error_rate"] == 0.0
    assert model_summary["success_rate"] == 1.0

def test_window_size_limit(performance_monitor, sample_metrics):
    """Test window size limit"""
    # Add more metrics than window size
    for _ in range(150):  # Window size is 100
        performance_monitor.record_metrics(sample_metrics)
    
    # Check that history is trimmed
    assert len(performance_monitor.metrics_history[sample_metrics.model_name]) == 100
    
    # Check that aggregated metrics are trimmed
    assert len(performance_monitor.metrics["latency"][sample_metrics.model_name]) == 100
    assert len(performance_monitor.metrics["resource_usage"][sample_metrics.model_name]) == 100
    assert len(performance_monitor.metrics["cost_per_request"][sample_metrics.model_name]) == 100

def test_error_handling(performance_monitor):
    """Test error handling"""
    # Test with invalid model name
    performance = performance_monitor.get_model_performance("nonexistent_model")
    assert performance == {}
    
    # Test with invalid metrics
    with pytest.raises(Exception):
        performance_monitor.record_metrics(None) 