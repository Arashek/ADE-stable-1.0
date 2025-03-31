import pytest
import numpy as np
from pathlib import Path
from ade_model_training.utils import (
    setup_seed,
    get_device,
    count_parameters,
    format_time,
    format_size,
    create_directory,
    save_json,
    load_json,
    calculate_gradient_norm,
    calculate_parameter_norm,
    calculate_model_size,
    calculate_flops,
    calculate_memory_usage,
    calculate_cpu_usage,
    calculate_gpu_usage,
    calculate_throughput
)

def test_setup_seed():
    """Test random seed setup."""
    setup_seed(42)
    # Add assertions for random number generation if needed

def test_get_device():
    """Test device selection."""
    device = get_device()
    assert device is not None
    assert device.type in ['cpu', 'cuda']

def test_count_parameters():
    """Test parameter counting."""
    class MockModel:
        def parameters(self):
            return [np.random.rand(10, 10), np.random.rand(5, 5)]
    
    model = MockModel()
    num_params = count_parameters(model)
    assert num_params == 125  # 10*10 + 5*5

def test_format_time():
    """Test time formatting."""
    assert format_time(0) == "0:00:00"
    assert format_time(60) == "0:01:00"
    assert format_time(3600) == "1:00:00"

def test_format_size():
    """Test size formatting."""
    assert format_size(0) == "0 B"
    assert format_size(1024) == "1.0 KB"
    assert format_size(1024*1024) == "1.0 MB"

def test_create_directory(tmp_path):
    """Test directory creation."""
    dir_path = tmp_path / "test_dir"
    create_directory(str(dir_path))
    assert dir_path.exists()
    assert dir_path.is_dir()

def test_save_load_json(tmp_path):
    """Test JSON saving and loading."""
    data = {"test": "data"}
    file_path = tmp_path / "test.json"
    
    save_json(data, str(file_path))
    assert file_path.exists()
    
    loaded_data = load_json(str(file_path))
    assert loaded_data == data

def test_calculate_gradient_norm():
    """Test gradient norm calculation."""
    gradients = [np.random.rand(10, 10), np.random.rand(5, 5)]
    norm = calculate_gradient_norm(gradients)
    assert norm >= 0

def test_calculate_parameter_norm():
    """Test parameter norm calculation."""
    parameters = [np.random.rand(10, 10), np.random.rand(5, 5)]
    norm = calculate_parameter_norm(parameters)
    assert norm >= 0

def test_calculate_model_size():
    """Test model size calculation."""
    class MockModel:
        def parameters(self):
            return [np.random.rand(10, 10), np.random.rand(5, 5)]
    
    model = MockModel()
    size = calculate_model_size(model)
    assert size >= 0

def test_calculate_flops():
    """Test FLOPS calculation."""
    class MockModel:
        def __call__(self, x):
            return x
    
    model = MockModel()
    input_size = (1, 3, 224, 224)
    flops = calculate_flops(model, input_size)
    assert flops >= 0

def test_calculate_memory_usage():
    """Test memory usage calculation."""
    usage = calculate_memory_usage()
    assert usage >= 0

def test_calculate_cpu_usage():
    """Test CPU usage calculation."""
    usage = calculate_cpu_usage()
    assert 0 <= usage <= 100

def test_calculate_gpu_usage():
    """Test GPU usage calculation."""
    usage = calculate_gpu_usage()
    assert usage >= 0

def test_calculate_throughput():
    """Test throughput calculation."""
    throughput = calculate_throughput(samples=100, time=1.0)
    assert throughput == 100.0

def test_error_handling():
    """Test error handling in utility functions."""
    # Test invalid JSON
    with pytest.raises(Exception):
        load_json("nonexistent.json")
    
    # Test invalid directory creation
    with pytest.raises(Exception):
        create_directory("/invalid/path")
    
    # Test invalid model for parameter counting
    with pytest.raises(AttributeError):
        count_parameters(None)
    
    # Test invalid input for FLOPS calculation
    with pytest.raises(Exception):
        calculate_flops(None, None)

def test_edge_cases():
    """Test edge cases in utility functions."""
    # Test zero values
    assert format_size(0) == "0 B"
    assert format_time(0) == "0:00:00"
    
    # Test large values
    assert format_size(1024**4) == "1.0 TB"
    assert format_time(3600*24) == "24:00:00"
    
    # Test negative values
    assert format_size(-1) == "-1 B"
    assert format_time(-1) == "-1:00:00"
    
    # Test empty lists
    assert calculate_gradient_norm([]) == 0
    assert calculate_parameter_norm([]) == 0 