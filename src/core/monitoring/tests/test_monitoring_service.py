import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import numpy as np
from ..monitoring_service import MonitoringService, Alert, MetricThreshold, AlertSeverity
from ...config.service_config import ServiceConfig

@pytest.fixture
def monitoring_service():
    """Create a monitoring service instance for testing."""
    config = ServiceConfig()
    service = MonitoringService(
        redis_url="redis://localhost:6379/0",
        prometheus_url="http://localhost:9090",
        service_config=config
    )
    return service

@pytest.mark.asyncio
async def test_system_metrics_collection(monitoring_service):
    """Test collection of system metrics."""
    # Start metrics collection
    await monitoring_service._collect_system_metrics()
    
    # Wait for metrics to be collected
    await asyncio.sleep(2)
    
    # Verify metrics are being collected
    assert monitoring_service.system_metrics["cpu_usage"]._value.get() > 0
    assert monitoring_service.system_metrics["memory_usage"]._value.get() > 0
    assert monitoring_service.system_metrics["process_count"]._value.get() > 0

@pytest.mark.asyncio
async def test_alert_creation(monitoring_service):
    """Test alert creation and management."""
    # Create a test threshold
    threshold = MetricThreshold(
        metric_name="test_metric",
        warning_threshold=80.0,
        critical_threshold=90.0,
        comparison="gt",
        window_size=300,
        aggregation="avg"
    )
    
    # Create an alert
    await monitoring_service._create_alert("test_metric", 95.0, threshold)
    
    # Verify alert was created
    assert len(monitoring_service.alerts) == 1
    alert = monitoring_service.alerts[0]
    assert alert.type == "test_metric"
    assert alert.severity == AlertSeverity.CRITICAL
    assert alert.details["value"] == 95.0
    
    # Test alert acknowledgment
    assert await monitoring_service.acknowledge_alert(alert.id)
    assert alert.acknowledged
    
    # Test alert resolution
    assert await monitoring_service.resolve_alert(alert.id)
    assert alert.resolved
    assert alert.resolution_time is not None

@pytest.mark.asyncio
async def test_metric_analysis(monitoring_service):
    """Test metric analysis functionality."""
    # Generate test metrics
    test_metrics = np.random.normal(50, 10, 100)
    test_metrics[-1] = 100  # Add an anomaly
    
    # Test trend calculation
    trend = monitoring_service._calculate_trend(test_metrics.tolist())
    assert trend in ["increasing", "decreasing", "stable"]
    
    # Test anomaly detection
    anomalies = monitoring_service._detect_anomalies(test_metrics.tolist())
    assert len(anomalies) > 0
    assert anomalies[-1]["value"] == 100
    
    # Test metric forecasting
    forecast = monitoring_service._forecast_metric(test_metrics.tolist())
    assert "forecast" in forecast
    assert "confidence" in forecast
    assert len(forecast["forecast"]) == 5
    assert 0 <= forecast["confidence"] <= 1

@pytest.mark.asyncio
async def test_health_checks(monitoring_service):
    """Test health check functionality."""
    # Start health checks
    await monitoring_service._check_health()
    
    # Wait for health checks to complete
    await asyncio.sleep(1)
    
    # Verify health checks are being performed
    assert "system" in monitoring_service.health_checks
    assert "application" in monitoring_service.health_checks
    assert "database" in monitoring_service.health_checks
    assert "external" in monitoring_service.health_checks

@pytest.mark.asyncio
async def test_metric_history(monitoring_service):
    """Test metric history functionality."""
    # Generate test data
    metric_name = "test_metric"
    start_time = datetime.now() - timedelta(hours=1)
    end_time = datetime.now()
    
    # Mock Redis client
    with patch.object(monitoring_service.redis_client, 'zrangebyscore') as mock_redis:
        mock_redis.return_value = [
            '{"value": 50, "timestamp": "2024-01-01T00:00:00"}',
            '{"value": 60, "timestamp": "2024-01-01T00:01:00"}'
        ]
        
        # Get metric history
        history = await monitoring_service.get_metric_history(
            metric_name, start_time, end_time
        )
        
        # Verify history
        assert len(history) == 2
        assert history[0]["value"] == 50
        assert history[1]["value"] == 60

@pytest.mark.asyncio
async def test_metrics_summary(monitoring_service):
    """Test metrics summary functionality."""
    # Mock metric summary methods
    with patch.object(monitoring_service, '_get_system_metrics_summary') as mock_system, \
         patch.object(monitoring_service, '_get_application_metrics_summary') as mock_app, \
         patch.object(monitoring_service, '_get_business_metrics_summary') as mock_business:
        
        mock_system.return_value = {"cpu": 50, "memory": 60}
        mock_app.return_value = {"requests": 100, "errors": 5}
        mock_business.return_value = {"transactions": 50, "conversion": 0.1}
        
        # Get metrics summary
        summary = await monitoring_service.get_metrics_summary()
        
        # Verify summary
        assert "system" in summary
        assert "application" in summary
        assert "business" in summary
        assert "health" in summary
        assert "alerts" in summary

@pytest.mark.asyncio
async def test_threshold_checking(monitoring_service):
    """Test threshold checking functionality."""
    # Create test thresholds
    thresholds = {
        "cpu_usage": MetricThreshold(
            metric_name="system_cpu_usage_percent",
            warning_threshold=80.0,
            critical_threshold=90.0,
            comparison="gt",
            window_size=300,
            aggregation="avg"
        ),
        "memory_usage": MetricThreshold(
            metric_name="system_memory_usage_bytes",
            warning_threshold=0.8,
            critical_threshold=0.9,
            comparison="gt",
            window_size=300,
            aggregation="avg"
        )
    }
    
    # Mock metric value retrieval
    with patch.object(monitoring_service, '_get_metric_value') as mock_get_value:
        # Test warning threshold
        mock_get_value.return_value = 85.0
        await monitoring_service._check_alerts()
        assert len(monitoring_service.alerts) == 1
        assert monitoring_service.alerts[0].severity == AlertSeverity.WARNING
        
        # Test critical threshold
        mock_get_value.return_value = 95.0
        await monitoring_service._check_alerts()
        assert len(monitoring_service.alerts) == 2
        assert monitoring_service.alerts[1].severity == AlertSeverity.CRITICAL 