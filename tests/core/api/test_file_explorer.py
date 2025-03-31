import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import shutil
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import json
import asyncio
from fastapi.websockets import WebSocket
import io
import zipfile

from src.core.api.file_explorer import router, FileWatcher, FileSystemEvent
from src.core.models.user import User

# Test fixtures
@pytest.fixture
def app():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router, prefix="/api/files")
    return app

@pytest.fixture
def test_client(app):
    return TestClient(app)

@pytest.fixture
def mock_user():
    return User(
        id="test_user_id",
        username="test_user",
        email="test@example.com",
        is_active=True,
        is_superuser=False
    )

@pytest.fixture
def test_directory():
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    os.environ['ALLOWED_BASE_PATH'] = temp_dir
    
    # Create test files and directories
    test_files = {
        'test.txt': 'Hello, World!',
        'test.py': 'def hello():\n    print("Hello")',
        'test.json': '{"key": "value"}',
        'test.bin': b'\x00\x01\x02\x03'
    }
    
    for filename, content in test_files.items():
        file_path = Path(temp_dir) / filename
        if isinstance(content, str):
            file_path.write_text(content)
        else:
            file_path.write_bytes(content)
    
    # Create a test directory
    test_dir = Path(temp_dir) / 'test_dir'
    test_dir.mkdir()
    (test_dir / 'nested.txt').write_text('Nested file')
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)

def test_list_files(test_client, test_directory, mock_user):
    with patch('src.core.api.file_explorer.get_current_user', return_value=mock_user):
        response = test_client.get(f"/api/files/list?path={test_directory}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check file items
        file_items = {item['name']: item for item in data}
        assert 'test.txt' in file_items
        assert 'test.py' in file_items
        assert 'test_dir' in file_items
        
        # Check metadata
        test_txt = file_items['test.txt']
        assert test_txt['type'] == 'file'
        assert test_txt['mime_type'] == 'text/plain'
        assert test_txt['size'] > 0
        assert 'created_at' in test_txt
        assert 'modified_at' in test_txt

def test_get_file_content(test_client, test_directory, mock_user):
    with patch('src.core.api.file_explorer.get_current_user', return_value=mock_user):
        # Test text file
        response = test_client.get(f"/api/files/content?path={os.path.join(test_directory, 'test.txt')}")
        assert response.status_code == 200
        
        data = response.json()
        assert data['content'] == 'Hello, World!'
        assert data['encoding'] == 'utf-8'
        assert data['mime_type'] == 'text/plain'
        
        # Test binary file
        response = test_client.get(f"/api/files/content?path={os.path.join(test_directory, 'test.bin')}")
        assert response.status_code == 400
        assert "Cannot read binary file" in response.json()['detail']

def test_update_file_content(test_client, test_directory, mock_user):
    with patch('src.core.api.file_explorer.get_current_user', return_value=mock_user):
        update_data = {
            "path": os.path.join(test_directory, 'test.txt'),
            "content": "Updated content",
            "encoding": "utf-8"
        }
        
        response = test_client.put("/api/files/content", json=update_data)
        assert response.status_code == 200
        
        # Verify update
        response = test_client.get(f"/api/files/content?path={update_data['path']}")
        assert response.status_code == 200
        assert response.json()['content'] == "Updated content"

def test_create_directory(test_client, test_directory, mock_user):
    with patch('src.core.api.file_explorer.get_current_user', return_value=mock_user):
        directory_data = {
            "path": test_directory,
            "name": "new_dir"
        }
        
        response = test_client.post("/api/files/directory", json=directory_data)
        assert response.status_code == 200
        
        # Verify directory was created
        new_dir = Path(test_directory) / "new_dir"
        assert new_dir.exists()
        assert new_dir.is_dir()

def test_delete_path(test_client, test_directory, mock_user):
    with patch('src.core.api.file_explorer.get_current_user', return_value=mock_user):
        # Test deleting a file
        file_path = os.path.join(test_directory, 'test.txt')
        response = test_client.delete(f"/api/files/path?path={file_path}")
        assert response.status_code == 200
        
        # Verify file was deleted
        assert not Path(file_path).exists()
        
        # Test deleting a directory
        dir_path = os.path.join(test_directory, 'test_dir')
        response = test_client.delete(f"/api/files/path?path={dir_path}")
        assert response.status_code == 200
        
        # Verify directory was deleted
        assert not Path(dir_path).exists()

def test_search_files(test_client, test_directory, mock_user):
    with patch('src.core.api.file_explorer.get_current_user', return_value=mock_user):
        # Test simple text search
        search_data = {
            "pattern": "Hello",
            "use_regex": False,
            "case_sensitive": True
        }
        
        response = test_client.post("/api/files/search", json=search_data)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        assert any('test.txt' in result['path'] for result in data)
        
        # Test regex search
        search_data = {
            "pattern": r"def\s+\w+",
            "use_regex": True,
            "case_sensitive": True
        }
        
        response = test_client.post("/api/files/search", json=search_data)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        assert any('test.py' in result['path'] for result in data)
        
        # Test file type filter
        search_data = {
            "pattern": "Hello",
            "file_types": [".txt"]
        }
        
        response = test_client.post("/api/files/search", json=search_data)
        assert response.status_code == 200
        
        data = response.json()
        assert all(result['path'].endswith('.txt') for result in data)

def test_error_handling(test_client, test_directory, mock_user):
    with patch('src.core.api.file_explorer.get_current_user', return_value=mock_user):
        # Test invalid path
        response = test_client.get("/api/files/list?path=/invalid/path")
        assert response.status_code == 400
        
        # Test file not found
        response = test_client.get(f"/api/files/content?path={os.path.join(test_directory, 'nonexistent.txt')}")
        assert response.status_code == 400
        
        # Test directory already exists
        directory_data = {
            "path": test_directory,
            "name": "test_dir"  # Already exists
        }
        response = test_client.post("/api/files/directory", json=directory_data)
        assert response.status_code == 400

def test_concurrent_modification(test_client, test_directory, mock_user):
    with patch('src.core.api.file_explorer.get_current_user', return_value=mock_user):
        # First, get the file content to get its modification time
        response = test_client.get(f"/api/files/content?path={os.path.join(test_directory, 'test.txt')}")
        assert response.status_code == 200
        modified_at = response.json()['modified_at']
        
        # Try to update with an old modification time
        update_data = {
            "path": os.path.join(test_directory, 'test.txt'),
            "content": "Updated content",
            "encoding": "utf-8",
            "modified_at": (datetime.fromisoformat(modified_at) - timedelta(minutes=1)).isoformat()
        }
        
        response = test_client.put("/api/files/content", json=update_data)
        assert response.status_code == 409
        assert "File has been modified" in response.json()['detail']

def test_large_file_handling(test_client, test_directory, mock_user):
    with patch('src.core.api.file_explorer.get_current_user', return_value=mock_user):
        # Create a large file
        large_file = Path(test_directory) / 'large.txt'
        with open(large_file, 'w') as f:
            f.write('x' * (100 * 1024 * 1024 + 1))  # 100MB + 1 byte
        
        # Try to read the large file
        response = test_client.get(f"/api/files/content?path={large_file}")
        assert response.status_code == 413
        assert "File too large" in response.json()['detail']

def test_file_upload(test_client, test_directory, mock_user):
    with patch('src.core.api.file_explorer.get_current_user', return_value=mock_user):
        # Create a test file
        test_content = "Test upload content"
        files = {'file': ('test_upload.txt', test_content)}
        data = {'path': test_directory}
        
        response = test_client.post("/api/files/upload", files=files, data=data)
        assert response.status_code == 200
        
        # Verify file was created
        uploaded_file = Path(test_directory) / 'test_upload.txt'
        assert uploaded_file.exists()
        assert uploaded_file.read_text() == test_content

def test_file_download(test_client, test_directory, mock_user):
    with patch('src.core.api.file_explorer.get_current_user', return_value=mock_user):
        # Test regular download
        response = test_client.get(f"/api/files/download?path={os.path.join(test_directory, 'test.txt')}")
        assert response.status_code == 200
        assert response.text == 'Hello, World!'
        
        # Test compressed download
        response = test_client.get(f"/api/files/download?path={os.path.join(test_directory, 'test.txt')}&compress=true")
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/zip'
        
        # Verify zip content
        zip_buffer = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_buffer) as zip_file:
            assert 'test.txt' in zip_file.namelist()
            assert zip_file.read('test.txt').decode() == 'Hello, World!'

def test_file_compression(test_client, test_directory, mock_user):
    with patch('src.core.api.file_explorer.get_current_user', return_value=mock_user):
        # Test compression
        response = test_client.post(f"/api/files/compress?path={os.path.join(test_directory, 'test.txt')}")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'success'
        assert data['original_size'] > 0
        assert data['compressed_size'] > 0
        assert 0 < data['compression_ratio'] < 1
        
        # Verify compressed file exists
        compressed_file = Path(test_directory) / 'test.txt.zip'
        assert compressed_file.exists()
        
        # Test decompression
        response = test_client.post(f"/api/files/decompress?path={compressed_file}")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'success'
        
        # Verify extracted content
        extracted_dir = Path(test_directory) / 'test.txt'
        assert extracted_dir.exists()
        assert (extracted_dir / 'test.txt').read_text() == 'Hello, World!'

@pytest.mark.asyncio
async def test_websocket_file_watching(test_client, test_directory):
    # Create a test WebSocket connection
    websocket = AsyncMock(spec=WebSocket)
    websocket.accept = AsyncMock()
    websocket.send_json = AsyncMock()
    websocket.receive_text = AsyncMock(return_value='{"type": "ping"}')
    
    # Test file watcher
    watcher = FileWatcher(Path(test_directory))
    
    # Simulate file system events
    test_file = Path(test_directory) / 'watched.txt'
    test_file.write_text('Test content')
    
    # Trigger events
    watcher.on_created(Mock(src_path=str(test_file), is_directory=False))
    watcher.on_modified(Mock(src_path=str(test_file), is_directory=False))
    test_file.unlink()
    watcher.on_deleted(Mock(src_path=str(test_file), is_directory=False))
    
    # Verify WebSocket messages
    assert websocket.send_json.call_count >= 3
    calls = websocket.send_json.call_args_list
    
    # Check created event
    created_event = calls[0][0][0]
    assert created_event['event_type'] == 'created'
    assert created_event['path'] == 'watched.txt'
    assert not created_event['is_directory']
    assert created_event['metadata'] is not None
    
    # Check modified event
    modified_event = calls[1][0][0]
    assert modified_event['event_type'] == 'modified'
    assert modified_event['path'] == 'watched.txt'
    assert not modified_event['is_directory']
    assert modified_event['metadata'] is not None
    
    # Check deleted event
    deleted_event = calls[2][0][0]
    assert deleted_event['event_type'] == 'deleted'
    assert deleted_event['path'] == 'watched.txt'
    assert not deleted_event['is_directory']
    assert deleted_event['metadata'] is None

def test_enhanced_search(test_client, test_directory, mock_user):
    with patch('src.core.api.file_explorer.get_current_user', return_value=mock_user):
        # Test size-based search
        search_data = {
            "pattern": "Hello",
            "min_size": 10,
            "max_size": 100
        }
        response = test_client.post("/api/files/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        
        # Test content type filter
        search_data = {
            "pattern": "Hello",
            "content_type": "text/plain"
        }
        response = test_client.post("/api/files/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        assert all(result['metadata']['mime_type'] == 'text/plain' for result in data)
        
        # Test language filter
        search_data = {
            "pattern": "def",
            "language": "python"
        }
        response = test_client.post("/api/files/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        assert all(result['metadata']['language'] == 'python' for result in data)
        
        # Test hash-based search
        test_file = Path(test_directory) / 'test.txt'
        file_hash = test_file.read_bytes().hex()
        search_data = {
            "pattern": "Hello",
            "hash": file_hash
        }
        response = test_client.post("/api/files/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['path'] == 'test.txt' 