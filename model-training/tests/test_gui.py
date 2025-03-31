import pytest
from unittest.mock import MagicMock, patch
from ade_model_training.gui import LearningHubInterface
from ade_model_training.config import Config
from ade_model_training.trainer import DistributedTrainer
from ade_model_training.visualizer import LearningVisualizer

@pytest.fixture
def interface(tmp_path):
    config = Config()
    config.set("log_dir", str(tmp_path / "logs"))
    trainer = DistributedTrainer(config)
    visualizer = LearningVisualizer(config)
    return LearningHubInterface(config, trainer, visualizer)

def test_init(interface):
    """Test interface initialization."""
    assert interface.config is not None
    assert interface.trainer is not None
    assert interface.visualizer is not None
    assert interface.root is not None

def test_create_training_tab(interface):
    """Test training tab creation."""
    tab = interface._create_training_tab()
    assert tab is not None

def test_create_monitoring_tab(interface):
    """Test monitoring tab creation."""
    tab = interface._create_monitoring_tab()
    assert tab is not None

def test_create_visualization_tab(interface):
    """Test visualization tab creation."""
    tab = interface._create_visualization_tab()
    assert tab is not None

def test_create_analysis_tab(interface):
    """Test analysis tab creation."""
    tab = interface._create_analysis_tab()
    assert tab is not None

def test_create_config_tab(interface):
    """Test configuration tab creation."""
    tab = interface._create_config_tab()
    assert tab is not None

def test_start_training(interface):
    """Test training start."""
    with patch('ade_model_training.trainer.DistributedTrainer.train') as mock_train:
        interface.start_training()
        assert mock_train.called

def test_stop_training(interface):
    """Test training stop."""
    interface.stop_training()
    assert interface.is_training is False

def test_update_metrics(interface):
    """Test metrics update."""
    with patch('ade_model_training.trainer.DistributedTrainer.get_metrics') as mock_metrics:
        mock_metrics.return_value = {
            "loss": 0.5,
            "accuracy": 0.8
        }
        interface._update_metrics()
        assert mock_metrics.called

def test_update_visualizations(interface):
    """Test visualizations update."""
    with patch('ade_model_training.visualizer.LearningVisualizer.create_visualization') as mock_viz:
        interface._update_visualizations()
        assert mock_viz.called

def test_generate_analysis(interface):
    """Test analysis generation."""
    with patch('ade_model_training.visualizer.LearningVisualizer.create_visualization') as mock_viz:
        interface._generate_analysis()
        assert mock_viz.called

def test_save_config(interface, tmp_path):
    """Test configuration saving."""
    config_path = tmp_path / "test_config.json"
    interface.save_config(str(config_path))
    assert config_path.exists()

def test_load_config(interface, tmp_path):
    """Test configuration loading."""
    config_path = tmp_path / "test_config.json"
    config_path.touch()
    interface.load_config(str(config_path))
    assert interface.config is not None

def test_create_custom_widget(interface):
    """Test custom widget creation."""
    widget = interface._create_custom_widget("test_widget", "Test Widget")
    assert widget is not None

def test_create_layout(interface):
    """Test layout creation."""
    layout = interface._create_layout("test_layout")
    assert layout is not None

def test_save_layout(interface, tmp_path):
    """Test layout saving."""
    layout_path = tmp_path / "test_layout.json"
    interface.save_layout(str(layout_path))
    assert layout_path.exists()

def test_load_layout(interface, tmp_path):
    """Test layout loading."""
    layout_path = tmp_path / "test_layout.json"
    layout_path.touch()
    interface.load_layout(str(layout_path))
    assert interface.current_layout is not None 