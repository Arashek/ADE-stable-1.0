import os
import sys
import pytest
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

@pytest.fixture(autouse=True)
def setup_test_env(tmp_path):
    """Set up the test environment before each test."""
    # Create necessary directories
    (tmp_path / "data").mkdir()
    (tmp_path / "logs").mkdir()
    (tmp_path / "visualizations").mkdir()
    
    # Set environment variables
    os.environ["ADE_MODEL_TRAINING_DATA_DIR"] = str(tmp_path / "data")
    os.environ["ADE_MODEL_TRAINING_LOG_DIR"] = str(tmp_path / "logs")
    os.environ["ADE_MODEL_TRAINING_VISUALIZATION_DIR"] = str(tmp_path / "visualizations")
    
    yield tmp_path
    
    # Clean up after test
    for path in tmp_path.glob("**/*"):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            path.rmdir()

@pytest.fixture
def mock_torch():
    """Mock PyTorch for testing."""
    import sys
    import types
    
    mock_torch = types.ModuleType("torch")
    mock_torch.cuda = types.ModuleType("torch.cuda")
    mock_torch.cuda.is_available = lambda: True
    mock_torch.cuda.device_count = lambda: 2
    
    mock_torch.nn = types.ModuleType("torch.nn")
    mock_torch.nn.Module = object
    mock_torch.nn.DataParallel = object
    mock_torch.nn.parallel = types.ModuleType("torch.nn.parallel")
    mock_torch.nn.parallel.DistributedDataParallel = object
    
    mock_torch.optim = types.ModuleType("torch.optim")
    mock_torch.optim.Adam = object
    
    sys.modules["torch"] = mock_torch
    return mock_torch

@pytest.fixture
def mock_plotly():
    """Mock Plotly for testing."""
    import sys
    import types
    
    mock_plotly = types.ModuleType("plotly")
    mock_plotly.graph_objects = types.ModuleType("plotly.graph_objects")
    mock_plotly.graph_objects.Figure = object
    
    sys.modules["plotly"] = mock_plotly
    return mock_plotly

@pytest.fixture
def mock_tkinter():
    """Mock Tkinter for testing."""
    import sys
    import types
    
    mock_tkinter = types.ModuleType("tkinter")
    mock_tkinter.Tk = object
    mock_tkinter.ttk = types.ModuleType("tkinter.ttk")
    mock_tkinter.ttk.Frame = object
    mock_tkinter.ttk.Label = object
    mock_tkinter.ttk.Button = object
    mock_tkinter.ttk.Entry = object
    mock_tkinter.ttk.Combobox = object
    mock_tkinter.ttk.Notebook = object
    
    sys.modules["tkinter"] = mock_tkinter
    return mock_tkinter 