import json
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from flask import Flask
from ade_model_training.web.app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_data_capture():
    """Create a mock ADE data capture instance."""
    with patch('ade_model_training.web.app.data_capture') as mock:
        yield mock

def test_index(client):
    """Test the index page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'ADE Data Capture Manager' in response.data

def test_get_status(client, mock_data_capture):
    """Test getting system status."""
    mock_data_capture.session.get.return_value.json.return_value = [
        {'id': 'test-session'}
    ]
    
    response = client.get('/api/status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'running'
    assert 'stats' in data
    assert 'config' in data

def test_list_datasets(client, mock_data_capture, tmp_path):
    """Test listing available datasets."""
    # Create test dataset files
    dataset_dir = tmp_path / "learning"
    dataset_dir.mkdir(parents=True)
    (dataset_dir / "dataset_1.csv").touch()
    (dataset_dir / "dataset_2.csv").touch()
    
    mock_data_capture.config = {
        'learning_data_dir': str(dataset_dir)
    }
    
    response = client.get('/api/datasets')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert all('name' in dataset for dataset in data)

def test_download_dataset(client, mock_data_capture, tmp_path):
    """Test downloading a dataset."""
    # Create test dataset file
    dataset_dir = tmp_path / "learning"
    dataset_dir.mkdir(parents=True)
    test_file = dataset_dir / "test_dataset.csv"
    test_file.write_text("test,data\n1,2")
    
    mock_data_capture.config = {
        'learning_data_dir': str(dataset_dir)
    }
    
    response = client.get('/api/datasets/test_dataset.csv')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'

def test_list_sessions(client, mock_data_capture):
    """Test listing active sessions."""
    mock_data_capture.session.get.return_value.json.return_value = [
        {'id': 'session1'},
        {'id': 'session2'}
    ]
    
    response = client.get('/api/sessions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert all('id' in session for session in data)

def test_get_session_metrics(client, mock_data_capture, tmp_path):
    """Test getting session metrics."""
    # Create test metrics file
    metrics_dir = tmp_path / "learning" / "metrics"
    metrics_dir.mkdir(parents=True)
    metrics_file = metrics_dir / "test-session.json"
    metrics_file.write_text(json.dumps({'accuracy': 0.95}))
    
    mock_data_capture.config = {
        'learning_data_dir': str(tmp_path / "learning")
    }
    
    response = client.get('/api/sessions/test-session/metrics')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['accuracy'] == 0.95

def test_process_data(client, mock_data_capture):
    """Test processing learning data."""
    mock_data_capture.prepare_training_data.return_value = MagicMock(
        empty=False,
        __len__=lambda self: 10
    )
    
    response = client.post('/api/process', json={
        'session_ids': ['session1', 'session2']
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Data processed successfully'
    assert data['num_samples'] == 10

def test_process_data_no_sessions(client):
    """Test processing data with no sessions selected."""
    response = client.post('/api/process', json={'session_ids': []})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_handle_config_get(client, mock_data_capture):
    """Test getting configuration."""
    mock_data_capture.config = {
        'ade_api_url': 'http://test-api',
        'ade_api_key': 'test-key',
        'learning_data_dir': 'test/data',
        'model_data_dir': 'test/models'
    }
    
    response = client.get('/api/config')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == mock_data_capture.config

def test_handle_config_post(client, mock_data_capture, tmp_path):
    """Test updating configuration."""
    config_file = tmp_path / "config" / "ade_integration.json"
    config_file.parent.mkdir(parents=True)
    
    mock_data_capture.config = {
        'ade_api_url': 'http://old-api',
        'ade_api_key': 'old-key',
        'learning_data_dir': 'old/data',
        'model_data_dir': 'old/models'
    }
    
    new_config = {
        'ade_api_url': 'http://new-api',
        'ade_api_key': 'new-key',
        'learning_data_dir': 'new/data',
        'model_data_dir': 'new/models'
    }
    
    with patch('ade_model_training.web.app.Path') as mock_path:
        mock_path.return_value = config_file
        response = client.post('/api/config', json=new_config)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Configuration updated successfully'
        assert data['config'] == new_config

def test_upload_file(client, mock_data_capture, tmp_path):
    """Test file upload."""
    upload_dir = tmp_path / "learning"
    upload_dir.mkdir(parents=True)
    
    mock_data_capture.config = {
        'learning_data_dir': str(upload_dir)
    }
    
    data = {
        'file': (b'test,data\n1,2', 'test.csv')
    }
    
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'File uploaded successfully'
    assert data['filename'] == 'test.csv'

def test_upload_file_no_file(client):
    """Test file upload with no file."""
    response = client.post('/api/upload', data={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_error_handling(client, mock_data_capture):
    """Test error handling in various endpoints."""
    # Test status endpoint error
    mock_data_capture.session.get.side_effect = Exception("Test error")
    response = client.get('/api/status')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    
    # Test sessions endpoint error
    response = client.get('/api/sessions')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    
    # Test datasets endpoint error
    mock_data_capture.config = {'learning_data_dir': '/nonexistent'}
    response = client.get('/api/datasets')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data

def test_invalid_routes(client):
    """Test handling of invalid routes."""
    response = client.get('/invalid/route')
    assert response.status_code == 404 