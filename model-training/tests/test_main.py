import pytest
from unittest.mock import patch, MagicMock
from ade_model_training.main import parse_args, setup_environment, main

def test_parse_args():
    """Test command line argument parsing."""
    with patch('sys.argv', ['script.py', '--config', 'test.json', '--debug', '--no-gui']):
        args = parse_args()
        assert args.config == 'test.json'
        assert args.debug is True
        assert args.no_gui is True
        assert args.standalone is False

def test_setup_environment(tmp_path):
    """Test environment setup and configuration loading."""
    config = setup_environment()
    assert config.get("batch_size") == 32
    assert config.get("learning_rate") == 0.001

    # Test loading from file
    config_path = tmp_path / "test_config.json"
    test_config = {
        "batch_size": 64,
        "learning_rate": 0.0005
    }
    with open(config_path, 'w') as f:
        import json
        json.dump(test_config, f)
    
    config = setup_environment(str(config_path))
    assert config.get("batch_size") == 64
    assert config.get("learning_rate") == 0.0005

@pytest.mark.gui
def test_main_with_gui(mock_tkinter, mock_torch, mock_plotly):
    """Test main function with GUI enabled."""
    with patch('sys.argv', ['script.py']):
        with patch('ade_model_training.gui.LearningHubInterface') as mock_interface:
            mock_interface.return_value = MagicMock()
            main()
            mock_interface.return_value.run.assert_called_once()

@pytest.mark.gui
def test_main_without_gui(mock_torch, mock_plotly):
    """Test main function without GUI."""
    with patch('sys.argv', ['script.py', '--no-gui']):
        with patch('ade_model_training.trainer.DistributedTrainer') as mock_trainer:
            mock_trainer.return_value = MagicMock()
            main()
            mock_trainer.return_value.train.assert_called_once()

def test_main_error_handling(mock_torch, mock_plotly):
    """Test main function error handling."""
    with patch('sys.argv', ['script.py']):
        with patch('ade_model_training.config.Config') as mock_config:
            mock_config.side_effect = Exception("Test error")
            with pytest.raises(SystemExit):
                main() 