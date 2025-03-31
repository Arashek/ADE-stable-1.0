import pytest
import asyncio
import psutil
import resource
from datetime import datetime, timedelta
from src.core.resource.resource_manager import (
    ResourceManager,
    ResourceQuota,
    ResourceUsage,
    ResourceType,
    ResourceViolationType
)
from src.core.monitoring.metrics import MetricsCollector
from src.core.monitoring.analytics import AnalyticsEngine

@pytest.fixture
def metrics_collector():
    return MetricsCollector()

@pytest.fixture
def analytics_engine():
    return AnalyticsEngine()

@pytest.fixture
def resource_quota():
    return ResourceQuota(
        memory_limit=256,  # 256MB
        cpu_percent=50.0,
        disk_io=50,  # 50MB/s
        network_io=50,  # 50MB/s
        open_files=50,
        max_threads=2,
        timeout=5.0,
        swap_limit=512,  # 512MB
        iops_limit=500,
        gpu_memory_limit=1024,  # 1GB
        soft_limit_percent=80.0
    )

@pytest.fixture
def resource_manager(metrics_collector, analytics_engine, resource_quota):
    return ResourceManager(
        quota=resource_quota,
        metrics_collector=metrics_collector,
        analytics_engine=analytics_engine
    )

@pytest.mark.asyncio
async def test_resource_monitoring_start_stop(resource_manager):
    """Test starting and stopping resource monitoring"""
    # Start monitoring
    await resource_manager.start_monitoring(psutil.Process().pid)
    assert resource_manager.process is not None
    assert resource_manager.monitor_task is not None
    
    # Wait for some monitoring data
    await asyncio.sleep(0.2)
    
    # Stop monitoring
    await resource_manager.stop_monitoring()
    assert resource_manager.process is None
    assert resource_manager.monitor_task is None
    assert len(resource_manager.usage_history) > 0

@pytest.mark.asyncio
async def test_resource_limits(resource_manager, resource_quota):
    """Test resource limit enforcement"""
    await resource_manager.start_monitoring(psutil.Process().pid)
    
    # Create usage that exceeds limits
    usage = ResourceUsage(
        memory_used=resource_quota.memory_limit * 1.2,  # 120% of limit
        cpu_percent=resource_quota.cpu_percent * 1.2,
        disk_read=resource_quota.disk_io * 0.6,
        disk_write=resource_quota.disk_io * 0.6,
        network_sent=resource_quota.network_io * 0.6,
        network_recv=resource_quota.network_io * 0.6,
        open_files=resource_quota.open_files + 1,
        thread_count=resource_quota.max_threads + 1,
        swap_used=resource_quota.swap_limit * 1.2,
        iops=resource_quota.iops_limit + 100,
        gpu_memory_used=resource_quota.gpu_memory_limit * 1.2,
        timestamp=datetime.now()
    )
    
    # Check violations
    violations = resource_manager._check_resource_limits(usage)
    
    # Verify all violations are detected
    violation_types = {v.type for v in violations}
    expected_types = {
        ResourceViolationType.MEMORY_EXCEEDED,
        ResourceViolationType.CPU_EXCEEDED,
        ResourceViolationType.DISK_IO_EXCEEDED,
        ResourceViolationType.NETWORK_IO_EXCEEDED,
        ResourceViolationType.OPEN_FILES_EXCEEDED,
        ResourceViolationType.THREADS_EXCEEDED,
        ResourceViolationType.SWAP_EXCEEDED,
        ResourceViolationType.IOPS_EXCEEDED,
        ResourceViolationType.GPU_EXCEEDED
    }
    assert violation_types == expected_types
    
    await resource_manager.stop_monitoring()

@pytest.mark.asyncio
async def test_resource_usage_tracking(resource_manager):
    """Test resource usage tracking"""
    await resource_manager.start_monitoring(psutil.Process().pid)
    
    # Wait for some monitoring data
    await asyncio.sleep(0.2)
    
    # Check usage history
    assert len(resource_manager.usage_history) > 0
    latest_usage = resource_manager.usage_history[-1]
    
    # Verify all metrics are present
    assert latest_usage.memory_used >= 0
    assert latest_usage.cpu_percent >= 0
    assert latest_usage.disk_read >= 0
    assert latest_usage.disk_write >= 0
    assert latest_usage.network_sent >= 0
    assert latest_usage.network_recv >= 0
    assert latest_usage.open_files >= 0
    assert latest_usage.thread_count >= 0
    assert latest_usage.swap_used >= 0
    assert latest_usage.iops >= 0
    assert latest_usage.timestamp is not None
    
    await resource_manager.stop_monitoring()

@pytest.mark.asyncio
async def test_resource_limit_exceeded(resource_manager, resource_quota):
    """Test handling of exceeded resource limits"""
    await resource_manager.start_monitoring(psutil.Process().pid)
    
    # Create usage that exceeds soft limit but not hard limit
    usage = ResourceUsage(
        memory_used=resource_quota.memory_limit * 0.9,  # 90% of limit
        cpu_percent=resource_quota.cpu_percent * 0.9,
        disk_read=resource_quota.disk_io * 0.9,
        disk_write=resource_quota.disk_io * 0.9,
        network_sent=resource_quota.network_io * 0.9,
        network_recv=resource_quota.network_io * 0.9,
        open_files=int(resource_quota.open_files * 0.9),
        thread_count=int(resource_quota.max_threads * 0.9),
        swap_used=resource_quota.swap_limit * 0.9,
        iops=int(resource_quota.iops_limit * 0.9),
        gpu_memory_used=resource_quota.gpu_memory_limit * 0.9,
        timestamp=datetime.now()
    )
    
    # Check violations
    violations = resource_manager._check_resource_limits(usage)
    
    # Verify soft limit warnings
    warning_violations = [v for v in violations if v.severity == "warning"]
    assert len(warning_violations) > 0
    
    await resource_manager.stop_monitoring()

@pytest.mark.asyncio
async def test_resource_history_cleanup(resource_manager):
    """Test cleanup of old resource history"""
    await resource_manager.start_monitoring(psutil.Process().pid)
    
    # Add some old history
    old_time = datetime.now() - timedelta(hours=2)
    resource_manager.usage_history.append(ResourceUsage(
        memory_used=100,
        cpu_percent=50,
        disk_read=10,
        disk_write=10,
        network_sent=10,
        network_recv=10,
        open_files=10,
        thread_count=1,
        swap_used=50,
        iops=100,
        timestamp=old_time
    ))
    
    # Wait for cleanup
    await asyncio.sleep(0.2)
    
    # Verify old history is cleaned up
    current_time = datetime.now()
    old_entries = [
        usage for usage in resource_manager.usage_history
        if (current_time - usage.timestamp).total_seconds() > 3600
    ]
    assert len(old_entries) == 0
    
    await resource_manager.stop_monitoring()

@pytest.mark.asyncio
async def test_metrics_recording(resource_manager, metrics_collector):
    """Test recording of resource metrics"""
    await resource_manager.start_monitoring(psutil.Process().pid)
    
    # Wait for some metrics to be recorded
    await asyncio.sleep(0.2)
    
    # Check basic metrics
    metrics = metrics_collector.get_metrics()
    assert "memory_usage" in metrics
    assert "cpu_usage" in metrics
    assert "disk_read" in metrics
    assert "disk_write" in metrics
    assert "network_sent" in metrics
    assert "network_recv" in metrics
    assert "open_files" in metrics
    assert "thread_count" in metrics
    assert "swap_usage" in metrics
    assert "iops" in metrics
    
    # Check derived metrics
    assert "total_disk_io" in metrics
    assert "total_network_io" in metrics
    assert "memory_utilization" in metrics
    assert "cpu_utilization" in metrics
    
    await resource_manager.stop_monitoring()

@pytest.mark.asyncio
async def test_resource_trends(resource_manager):
    """Test resource usage trend tracking"""
    await resource_manager.start_monitoring(psutil.Process().pid)
    
    # Wait for some trend data
    await asyncio.sleep(0.2)
    
    # Check trend data
    trends = resource_manager.get_resource_trends()
    assert len(trends) > 0
    
    # Verify trend data structure
    for resource_type, trend_data in trends.items():
        assert len(trend_data) > 0
        for entry in trend_data:
            assert "timestamp" in entry
            assert "value" in entry
            assert isinstance(entry["value"], (int, float))
    
    await resource_manager.stop_monitoring()

@pytest.mark.asyncio
async def test_resource_patterns(resource_manager, analytics_engine):
    """Test resource pattern detection"""
    await resource_manager.start_monitoring(psutil.Process().pid)
    
    # Add some spike data
    current_time = datetime.now()
    for i in range(10):
        resource_manager._trend_data[ResourceType.MEMORY].append((
            current_time + timedelta(seconds=i),
            100 if i == 5 else 50  # Create a spike at i=5
        ))
    
    # Trigger pattern analysis
    resource_manager._analyze_resource_patterns()
    
    # Check analytics for spike detection
    analytics = analytics_engine.get_analytics()
    assert "resource_patterns" in analytics
    memory_patterns = [
        p for p in analytics["resource_patterns"]
        if p["resource_type"] == "memory" and p["pattern_type"] == "spike"
    ]
    assert len(memory_patterns) > 0
    
    await resource_manager.stop_monitoring()

@pytest.mark.asyncio
async def test_violation_history(resource_manager, resource_quota):
    """Test resource violation history tracking"""
    await resource_manager.start_monitoring(psutil.Process().pid)
    
    # Create a violation
    usage = ResourceUsage(
        memory_used=resource_quota.memory_limit * 1.2,
        cpu_percent=resource_quota.cpu_percent * 1.2,
        disk_read=0,
        disk_write=0,
        network_sent=0,
        network_recv=0,
        open_files=0,
        thread_count=0,
        swap_used=0,
        iops=0,
        timestamp=datetime.now()
    )
    
    violations = resource_manager._check_resource_limits(usage)
    for violation in violations:
        resource_manager._record_violation(violation)
    
    # Check violation history
    history = resource_manager.get_violation_history()
    assert len(history) > 0
    
    # Verify violation data structure
    for entry in history:
        assert "timestamp" in entry
        assert "type" in entry
        assert "resource_type" in entry
        assert "current_value" in entry
        assert "limit" in entry
        assert "severity" in entry
        assert "details" in entry
    
    await resource_manager.stop_monitoring()

@pytest.mark.asyncio
async def test_current_usage(resource_manager):
    """Test current resource usage reporting"""
    await resource_manager.start_monitoring(psutil.Process().pid)
    
    # Wait for some usage data
    await asyncio.sleep(0.2)
    
    # Get current usage
    usage = resource_manager.get_current_usage()
    assert usage is not None
    
    # Verify usage data structure
    assert "timestamp" in usage
    assert "memory_used" in usage
    assert "cpu_percent" in usage
    assert "disk_read" in usage
    assert "disk_write" in usage
    assert "network_sent" in usage
    assert "network_recv" in usage
    assert "open_files" in usage
    assert "thread_count" in usage
    assert "swap_used" in usage
    assert "iops" in usage
    assert "gpu_memory_used" in usage
    assert "utilization" in usage
    
    # Verify utilization metrics
    utilization = usage["utilization"]
    assert "memory" in utilization
    assert "cpu" in utilization
    assert "disk_io" in utilization
    assert "network_io" in utilization
    assert "open_files" in utilization
    assert "threads" in utilization
    assert "swap" in utilization
    assert "iops" in utilization
    
    await resource_manager.stop_monitoring() 