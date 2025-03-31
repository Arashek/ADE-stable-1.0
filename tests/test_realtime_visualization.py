import pytest
import dash
from dash.testing.application_runners import import_app
from dash.testing.composite import DashComposite
from datetime import datetime, timedelta
from src.core.resource.realtime_visualization import RealTimeResourceVisualizer
from src.core.resource.resource_manager import ResourceManager, ResourceUsage, ResourceQuota
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
    """Create sample resource usage history"""
    current_time = datetime.now()
    for i in range(10):
        resource_manager.usage_history.append(ResourceUsage(
            memory_used=100 + i * 10,
            cpu_percent=20 + i * 5,
            disk_read=10 + i * 2,
            disk_write=10 + i * 2,
            network_sent=5 + i,
            network_recv=5 + i,
            open_files=10 + i,
            thread_count=2 + i,
            swap_used=50 + i * 5,
            iops=100 + i * 20,
            gpu_memory_used=200 + i * 30,
            timestamp=current_time + timedelta(seconds=i)
        ))

@pytest.fixture
def realtime_visualizer(resource_manager):
    """Create a RealTimeResourceVisualizer instance for testing"""
    return RealTimeResourceVisualizer(resource_manager, update_interval=0.1)

def test_visualizer_initialization(realtime_visualizer):
    """Test RealTimeResourceVisualizer initialization"""
    assert realtime_visualizer is not None
    assert realtime_visualizer.resource_manager is not None
    assert realtime_visualizer.update_interval == 0.1
    assert realtime_visualizer.is_running is False
    assert realtime_visualizer.update_thread is None

def test_dash_app_initialization(realtime_visualizer):
    """Test Dash app initialization"""
    assert isinstance(realtime_visualizer.app, dash.Dash)
    assert realtime_visualizer.app.layout is not None

def test_visualization_components(realtime_visualizer):
    """Test presence of all visualization components"""
    layout = realtime_visualizer.app.layout
    assert layout is not None
    
    # Check for main sections
    sections = [child for child in layout.children if isinstance(child, dash.html.Div)]
    section_titles = [section.children[0].children for section in sections]
    
    expected_sections = [
        "Real-Time Resource Monitoring",
        "Current Resource Utilization",
        "Resource Usage Timeline",
        "Resource Distribution",
        "Resource Correlation",
        "Resource Violations",
        "Resource Trends",
        "Resource Alerts"
    ]
    
    for title in expected_sections:
        assert any(title in str(section) for section in section_titles)

def test_utilization_gauges_update(realtime_visualizer, resource_manager):
    """Test utilization gauges update callback"""
    # Set current usage
    resource_manager.process = type('Process', (), {'pid': 1234})()
    resource_manager.usage_history.append(ResourceUsage(
        memory_used=200,
        cpu_percent=40,
        disk_read=20,
        disk_write=20,
        network_sent=10,
        network_recv=10,
        open_files=20,
        thread_count=3,
        swap_used=100,
        iops=200,
        gpu_memory_used=400,
        timestamp=datetime.now()
    ))
    
    # Trigger callback
    result = realtime_visualizer.app.callback_context.triggered[0]
    gauges = realtime_visualizer.app.callback_map["utilization-gauges.children"](result)
    
    assert gauges is not None
    assert len(gauges) > 0
    
    # Verify gauge properties
    for gauge in gauges:
        assert isinstance(gauge, dash.html.Div)
        assert len(gauge.children) == 2  # Title and graph
        assert isinstance(gauge.children[1], dash.dcc.Graph)

def test_timeline_update(realtime_visualizer, sample_usage_history):
    """Test timeline update callback"""
    result = realtime_visualizer.app.callback_context.triggered[0]
    fig = realtime_visualizer.app.callback_map["usage-timeline.figure"](result)
    
    assert fig is not None
    assert len(fig.data) > 0
    assert fig.layout.title.text == "Resource Usage Timeline"

def test_distribution_update(realtime_visualizer, sample_usage_history):
    """Test distribution update callback"""
    result = realtime_visualizer.app.callback_context.triggered[0]
    fig = realtime_visualizer.app.callback_map["resource-distribution.figure"](result)
    
    assert fig is not None
    assert len(fig.data) > 0
    assert fig.layout.title.text == "Resource Usage Distribution"

def test_heatmap_update(realtime_visualizer, sample_usage_history):
    """Test heatmap update callback"""
    result = realtime_visualizer.app.callback_context.triggered[0]
    fig = realtime_visualizer.app.callback_map["correlation-heatmap.figure"](result)
    
    assert fig is not None
    assert len(fig.data) == 1  # Heatmap has one trace
    assert fig.layout.title.text == "Resource Usage Correlation Heatmap"

def test_violation_timeline_update(realtime_visualizer, resource_manager):
    """Test violation timeline update callback"""
    # Add some violations
    resource_manager.violation_history.append({
        "timestamp": datetime.now(),
        "type": "memory_exceeded",
        "current_value": 600,
        "limit": 512,
        "severity": "error"
    })
    
    result = realtime_visualizer.app.callback_context.triggered[0]
    fig = realtime_visualizer.app.callback_map["violation-timeline.figure"](result)
    
    assert fig is not None
    assert len(fig.data) > 0
    assert fig.layout.title.text == "Resource Violations Timeline"

def test_trend_analysis_update(realtime_visualizer, resource_manager):
    """Test trend analysis update callback"""
    result = realtime_visualizer.app.callback_context.triggered[0]
    fig = realtime_visualizer.app.callback_map["trend-analysis.figure"](result)
    
    assert fig is not None
    assert len(fig.data) >= 0  # May be 0 if no trend data
    assert fig.layout.title is None  # No title for subplots

def test_alert_update(realtime_visualizer, resource_manager):
    """Test alert update callback"""
    # Add some violations
    resource_manager.violation_history.append({
        "timestamp": datetime.now(),
        "type": "memory_exceeded",
        "current_value": 600,
        "limit": 512,
        "severity": "error"
    })
    
    result = realtime_visualizer.app.callback_context.triggered[0]
    alerts = realtime_visualizer.app.callback_map["alert-container.children"](result)
    
    assert alerts is not None
    assert len(alerts) > 0
    
    # Verify alert properties
    for alert in alerts:
        assert isinstance(alert, dash.html.Div)
        assert "alert" in alert.children[0].className
        assert "memory exceeded" in alert.children[0].children.lower()

def test_visualizer_start_stop(realtime_visualizer):
    """Test visualizer start and stop functionality"""
    # Start visualizer
    realtime_visualizer.start(host="127.0.0.1", port=8051)
    assert realtime_visualizer.is_running is True
    assert realtime_visualizer.update_thread is not None
    assert realtime_visualizer.update_thread.is_alive()
    
    # Stop visualizer
    realtime_visualizer.stop()
    assert realtime_visualizer.is_running is False
    assert not realtime_visualizer.update_thread.is_alive() 