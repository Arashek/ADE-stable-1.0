import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.core.resource.visualization import ResourceVisualizer
from src.core.resource.resource_manager import ResourceUsage, ResourceType

@pytest.fixture
def visualizer():
    return ResourceVisualizer()

@pytest.fixture
def sample_usage_history():
    """Create sample resource usage history"""
    history = []
    current_time = datetime.now()
    
    for i in range(10):
        history.append(ResourceUsage(
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
    
    return history

@pytest.fixture
def sample_violation_history():
    """Create sample violation history"""
    current_time = datetime.now()
    return [
        {
            'timestamp': current_time + timedelta(seconds=i),
            'type': 'memory_exceeded',
            'current_value': 300 + i * 10,
            'severity': 'error'
        }
        for i in range(5)
    ] + [
        {
            'timestamp': current_time + timedelta(seconds=i),
            'type': 'cpu_exceeded',
            'current_value': 80 + i * 5,
            'severity': 'warning'
        }
        for i in range(5)
    ]

@pytest.fixture
def sample_current_usage():
    """Create sample current usage data"""
    return {
        'timestamp': datetime.now().isoformat(),
        'memory_used': 150,
        'cpu_percent': 45,
        'disk_read': 20,
        'disk_write': 20,
        'network_sent': 15,
        'network_recv': 15,
        'open_files': 15,
        'thread_count': 5,
        'swap_used': 75,
        'iops': 200,
        'gpu_memory_used': 400,
        'utilization': {
            'memory': 0.6,
            'cpu': 0.45,
            'disk_io': 0.4,
            'network_io': 0.3,
            'open_files': 0.3,
            'threads': 0.5,
            'swap': 0.15,
            'iops': 0.2
        }
    }

def test_create_usage_timeline(visualizer, sample_usage_history):
    """Test creation of usage timeline visualization"""
    fig = visualizer.create_usage_timeline(sample_usage_history)
    assert fig is not None
    assert len(fig.data) > 0
    
    # Verify all resource types are included
    resource_types = {trace.name.split(' ')[0].lower() for trace in fig.data}
    expected_types = {'memory', 'cpu', 'disk', 'network', 'open', 'threads', 'swap', 'iops', 'gpu'}
    assert resource_types.issuperset(expected_types)

def test_create_resource_distribution(visualizer, sample_usage_history):
    """Test creation of resource distribution visualization"""
    fig = visualizer.create_resource_distribution(sample_usage_history)
    assert fig is not None
    assert len(fig.data) > 0
    
    # Verify all resources are included
    resource_names = {trace.name.lower() for trace in fig.data}
    expected_names = {'memory', 'cpu', 'disk io', 'network io', 'open files', 
                     'threads', 'swap', 'iops', 'gpu'}
    assert resource_names.issuperset(expected_names)

def test_create_heatmap(visualizer, sample_usage_history):
    """Test creation of resource correlation heatmap"""
    fig = visualizer.create_heatmap(sample_usage_history)
    assert fig is not None
    assert len(fig.data) == 1  # Heatmap has one trace
    
    # Verify heatmap data
    heatmap_data = fig.data[0]
    assert heatmap_data.type == 'heatmap'
    assert heatmap_data.z is not None
    assert heatmap_data.x is not None
    assert heatmap_data.y is not None
    
    # Verify correlation matrix dimensions
    n_resources = len(heatmap_data.x)
    assert n_resources > 0
    assert heatmap_data.z.shape == (n_resources, n_resources)

def test_create_violation_timeline(visualizer, sample_violation_history):
    """Test creation of violation timeline visualization"""
    fig = visualizer.create_violation_timeline(sample_violation_history)
    assert fig is not None
    assert len(fig.data) > 0
    
    # Verify violation types are included
    violation_types = {trace.name.lower() for trace in fig.data}
    expected_types = {'memory exceeded', 'cpu exceeded'}
    assert violation_types == expected_types
    
    # Verify severity colors
    for trace in fig.data:
        if 'memory' in trace.name.lower():
            assert trace.marker.color == 'red'  # error severity
        elif 'cpu' in trace.name.lower():
            assert trace.marker.color == 'yellow'  # warning severity

def test_create_utilization_gauge(visualizer, sample_current_usage):
    """Test creation of utilization gauge visualization"""
    fig = visualizer.create_utilization_gauge(sample_current_usage)
    assert fig is not None
    assert len(fig.data) > 0
    
    # Verify all resources are included
    resource_names = {trace.title.text.lower() for trace in fig.data}
    expected_names = {'memory', 'cpu', 'disk i/o', 'network i/o', 'open files', 
                     'threads', 'swap', 'iops'}
    assert resource_names == expected_names
    
    # Verify gauge values
    for trace in fig.data:
        resource_name = trace.title.text.lower()
        if resource_name == 'memory':
            assert trace.value == 60.0  # 0.6 * 100
        elif resource_name == 'cpu':
            assert trace.value == 45.0  # 0.45 * 100

def test_save_and_show_visualization(visualizer, sample_usage_history, tmp_path):
    """Test saving and showing visualizations"""
    # Create a visualization
    fig = visualizer.create_usage_timeline(sample_usage_history)
    
    # Test saving
    filename = tmp_path / "test_visualization.html"
    visualizer.save_visualization(fig, str(filename))
    assert filename.exists()
    
    # Test showing (this will just verify the method exists and doesn't raise an error)
    visualizer.show_visualization(fig)

def test_visualization_with_empty_data(visualizer):
    """Test visualization methods with empty data"""
    # Test usage timeline
    fig = visualizer.create_usage_timeline([])
    assert fig is not None
    assert len(fig.data) == 0
    
    # Test resource distribution
    fig = visualizer.create_resource_distribution([])
    assert fig is not None
    assert len(fig.data) == 0
    
    # Test heatmap
    fig = visualizer.create_heatmap([])
    assert fig is not None
    assert len(fig.data) == 1
    assert fig.data[0].z is not None
    assert fig.data[0].z.size == 0
    
    # Test violation timeline
    fig = visualizer.create_violation_timeline([])
    assert fig is not None
    assert len(fig.data) == 0

def test_visualization_with_partial_data(visualizer):
    """Test visualization methods with partial data"""
    # Create usage history with some missing values
    history = [
        ResourceUsage(
            memory_used=100,
            cpu_percent=20,
            disk_read=10,
            disk_write=10,
            network_sent=5,
            network_recv=5,
            open_files=10,
            thread_count=2,
            swap_used=50,
            iops=100,
            gpu_memory_used=None,  # Missing GPU data
            timestamp=datetime.now()
        )
    ]
    
    # Test usage timeline
    fig = visualizer.create_usage_timeline(history)
    assert fig is not None
    assert len(fig.data) > 0
    
    # Test resource distribution
    fig = visualizer.create_resource_distribution(history)
    assert fig is not None
    assert len(fig.data) > 0
    
    # Test heatmap
    fig = visualizer.create_heatmap(history)
    assert fig is not None
    assert len(fig.data) == 1
    assert fig.data[0].z is not None
    assert fig.data[0].z.size > 0 