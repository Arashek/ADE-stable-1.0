import pytest
from fastapi.testclient import TestClient
from main import app
from core.security import API_KEY

client = TestClient(app)

def test_execute_command_success():
    """Test successful command execution"""
    response = client.post(
        "/api/ai/execute",
        json={
            "command": "echo 'test'",
            "env": {"TEST_VAR": "test_value"}
        },
        headers={"X-API-Key": API_KEY}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "output" in data
    assert "error" in data
    assert "execution_time" in data
    assert "resource_usage" in data
    assert data["error"] is None

def test_execute_command_invalid_api_key():
    """Test command execution with invalid API key"""
    response = client.post(
        "/api/ai/execute",
        json={"command": "echo 'test'"},
        headers={"X-API-Key": "invalid_key"}
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API key"

def test_execute_command_missing_api_key():
    """Test command execution without API key"""
    response = client.post(
        "/api/ai/execute",
        json={"command": "echo 'test'"}
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API key"

def test_execute_command_dangerous_command():
    """Test execution of dangerous command"""
    response = client.post(
        "/api/ai/execute",
        json={"command": "rm -rf /"},
        headers={"X-API-Key": API_KEY}
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Command not allowed"

def test_execute_command_rate_limit():
    """Test rate limiting"""
    # Make multiple requests quickly
    for _ in range(3):
        response = client.post(
            "/api/ai/execute",
            json={"command": "echo 'test'"},
            headers={"X-API-Key": API_KEY}
        )
    
    assert response.status_code == 429
    assert response.json()["detail"] == "Too many requests"

def test_execute_command_with_env_vars():
    """Test command execution with environment variables"""
    response = client.post(
        "/api/ai/execute",
        json={
            "command": "echo $TEST_VAR",
            "env": {"TEST_VAR": "test_value"}
        },
        headers={"X-API-Key": API_KEY}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "test_value" in data["output"]

def test_execute_command_error():
    """Test command execution with error"""
    response = client.post(
        "/api/ai/execute",
        json={"command": "nonexistent_command"},
        headers={"X-API-Key": API_KEY}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["error"] is not None
    assert data["output"] is None

def test_execute_command_invalid_json():
    """Test command execution with invalid JSON"""
    response = client.post(
        "/api/ai/execute",
        data="invalid json",
        headers={"X-API-Key": API_KEY}
    )
    
    assert response.status_code == 422

def test_execute_command_missing_command():
    """Test command execution without command"""
    response = client.post(
        "/api/ai/execute",
        json={},
        headers={"X-API-Key": API_KEY}
    )
    
    assert response.status_code == 422

def test_execute_command_with_timestamp():
    """Test command execution with timestamp"""
    response = client.post(
        "/api/ai/execute",
        json={
            "command": "echo 'test'",
            "timestamp": "2024-01-01T00:00:00"
        },
        headers={"X-API-Key": API_KEY}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "commandHash" in data 