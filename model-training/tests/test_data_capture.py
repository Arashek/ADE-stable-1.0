import json
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
from ade_model_training.ade.data_capture import ADEDataCapture

@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    return {
        "ade_api_url": "http://test-ade-api",
        "ade_api_key": "test-api-key",
        "data_capture_enabled": True,
        "learning_data_dir": "test_data/learning",
        "model_data_dir": "test_data/models"
    }

@pytest.fixture
def mock_response():
    """Create a mock response for testing."""
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    mock.json.return_value = {
        "id": "test-id",
        "content": "test content",
        "timestamp": "2024-01-01T00:00:00",
        "session_id": "test-session"
    }
    return mock

@pytest.fixture
def data_capture(mock_config):
    """Create a DataCapture instance for testing."""
    with patch('ade_model_training.ade.data_capture.ADEDataCapture._load_config', return_value=mock_config):
        capture = ADEDataCapture()
        return capture

def test_init(data_capture, mock_config):
    """Test initialization of DataCapture."""
    assert data_capture.config == mock_config
    assert data_capture.session.headers["Authorization"] == f"Bearer {mock_config['ade_api_key']}"

def test_setup_directories(data_capture, tmp_path):
    """Test directory setup."""
    with patch('ade_model_training.ade.data_capture.Path') as mock_path:
        mock_path.return_value.mkdir.return_value = None
        data_capture._setup_directories()
        assert mock_path.call_count == 5  # One call for each directory

def test_capture_prompt(data_capture, mock_response):
    """Test prompt capture functionality."""
    with patch('requests.Session.get', return_value=mock_response):
        prompt_data = data_capture.capture_prompt("test-prompt-id")
        assert prompt_data == mock_response.json()
        assert "content" in prompt_data
        assert "timestamp" in prompt_data

def test_capture_response(data_capture, mock_response):
    """Test response capture functionality."""
    with patch('requests.Session.get', return_value=mock_response):
        response_data = data_capture.capture_response("test-response-id")
        assert response_data == mock_response.json()
        assert "content" in response_data
        assert "timestamp" in response_data

def test_capture_metrics(data_capture, mock_response):
    """Test metrics capture functionality."""
    with patch('requests.Session.get', return_value=mock_response):
        metrics_data = data_capture.capture_metrics("test-session-id")
        assert metrics_data == mock_response.json()

def test_process_learning_data(data_capture, tmp_path):
    """Test learning data processing."""
    # Create test data files
    prompts_dir = tmp_path / "prompts"
    responses_dir = tmp_path / "responses"
    prompts_dir.mkdir()
    responses_dir.mkdir()
    
    # Create test prompt and response files
    prompt_data = {
        "id": "test-prompt",
        "content": "test prompt",
        "timestamp": "2024-01-01T00:00:00",
        "session_id": "test-session",
        "response_id": "test-response"
    }
    response_data = {
        "id": "test-response",
        "content": "test response",
        "timestamp": "2024-01-01T00:00:01"
    }
    
    with open(prompts_dir / "test-prompt.json", 'w') as f:
        json.dump(prompt_data, f)
    with open(responses_dir / "test-response.json", 'w') as f:
        json.dump(response_data, f)
    
    # Process the data
    with patch('ade_model_training.ade.data_capture.Path') as mock_path:
        mock_path.return_value = tmp_path
        df = data_capture.process_learning_data("test-session")
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "prompt" in df.columns
        assert "response" in df.columns
        assert "timestamp" in df.columns
        assert "session_id" in df.columns

def test_prepare_training_data(data_capture, tmp_path):
    """Test training data preparation."""
    # Create test datasets
    datasets = []
    for i in range(3):
        df = pd.DataFrame({
            'prompt': [f'prompt {i}'],
            'response': [f'response {i}'],
            'timestamp': ['2024-01-01T00:00:00'],
            'session_id': [f'session {i}']
        })
        datasets.append(df)
    
    # Mock process_learning_data to return test datasets
    with patch.object(data_capture, 'process_learning_data', side_effect=datasets):
        combined_df = data_capture.prepare_training_data(['session1', 'session2', 'session3'])
        
        assert isinstance(combined_df, pd.DataFrame)
        assert len(combined_df) == 3
        assert all(col in combined_df.columns for col in ['prompt', 'response', 'timestamp', 'session_id'])

def test_monitor_ade_activity(data_capture):
    """Test ADE activity monitoring."""
    mock_active_sessions = [{'id': 'test-session'}]
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = mock_active_sessions
    
    with patch('requests.Session.get', return_value=mock_response), \
         patch('time.sleep') as mock_sleep:
        # Simulate one iteration
        data_capture.monitor_ade_activity()
        assert mock_sleep.called

def test_error_handling(data_capture):
    """Test error handling in various methods."""
    with patch('requests.Session.get', side_effect=Exception("Test error")):
        # Test prompt capture error handling
        prompt_data = data_capture.capture_prompt("test-prompt-id")
        assert prompt_data == {}
        
        # Test response capture error handling
        response_data = data_capture.capture_response("test-response-id")
        assert response_data == {}
        
        # Test metrics capture error handling
        metrics_data = data_capture.capture_metrics("test-session-id")
        assert metrics_data == {}
        
        # Test learning data processing error handling
        df = data_capture.process_learning_data("test-session")
        assert isinstance(df, pd.DataFrame)
        assert df.empty

def test_main():
    """Test the main function."""
    with patch('ade_model_training.ade.data_capture.ADEDataCapture') as mock_capture, \
         patch('ade_model_training.ade.data_capture.logging.basicConfig') as mock_logging:
        mock_instance = MagicMock()
        mock_capture.return_value = mock_instance
        
        from ade_model_training.ade.data_capture import main
        main()
        
        assert mock_logging.called
        assert mock_capture.called
        assert mock_instance.monitor_ade_activity.called 