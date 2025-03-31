import pytest
from fastapi.testclient import TestClient
import json
from unittest import mock

from src.main import app
from src.interfaces.api.auth import create_access_token, UserRole

# Test client
client = TestClient(app)

# Create test tokens
def get_admin_token():
    return create_access_token(
        data={"sub": "admin", "roles": [UserRole.ADMIN, UserRole.DEVELOPER, UserRole.VIEWER]}
    )

def get_developer_token():
    return create_access_token(
        data={"sub": "developer", "roles": [UserRole.DEVELOPER, UserRole.VIEWER]}
    )

def get_viewer_token():
    return create_access_token(
        data={"sub": "viewer", "roles": [UserRole.VIEWER]}
    )

# Mock provider registry
@pytest.fixture(autouse=True)
def mock_provider_registry():
    with mock.patch("src.interfaces.api.providers.provider_registry") as mock_registry:
        # Configure mock provider
        mock_provider = mock.MagicMock()
        mock_provider.provider_id = "test-provider-id"
        mock_provider.provider_type = "test"
        mock_provider.is_active.return_value = True
        mock_provider.list_available_models.return_value = ["test-model"]
        mock_provider.get_capabilities.return_value = ["code_generation", "chat"]
        
        # Configure mock registry
        mock_registry.register_provider.return_value = mock_provider
        mock_registry.list_providers.return_value = [mock_provider]
        mock_registry.get_provider.return_value = mock_provider
        mock_registry.unregister_provider.return_value = True
        
        yield mock_registry

# Tests for provider endpoints with different roles
def test_admin_can_register_provider():
    """Test that admin can register a provider"""
    token = get_admin_token()
    
    response = client.post(
        "/providers/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "provider_type": "test",
            "api_key": "test-api-key"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["provider_type"] == "test"
    assert "provider_id" in response.json()

def test_developer_cannot_register_provider():
    """Test that developer cannot register a provider"""
    token = get_developer_token()
    
    response = client.post(
        "/providers/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "provider_type": "test",
            "api_key": "test-api-key"
        }
    )
    
    assert response.status_code == 403

def test_all_roles_can_list_providers():
    """Test that all roles can list providers"""
    for token_func in [get_admin_token, get_developer_token, get_viewer_token]:
        token = token_func()
        
        response = client.get(
            "/providers/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0

def test_admin_can_delete_provider():
    """Test that admin can delete a provider"""
    token = get_admin_token()
    
    response = client.delete(
        "/providers/test-provider-id",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert "message" in response.json()

def test_developer_cannot_delete_provider():
    """Test that developer cannot delete a provider"""
    token = get_developer_token()
    
    response = client.delete(
        "/providers/test-provider-id",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403

def test_unauthenticated_cannot_access_providers():
    """Test that unauthenticated users cannot access providers"""
    # No token provided
    response = client.get("/providers/")
    assert response.status_code == 401
    
    response = client.post(
        "/providers/",
        json={
            "provider_type": "test",
            "api_key": "test-api-key"
        }
    )
    assert response.status_code == 401

def test_admin_can_update_provider():
    """Test that admin can update a provider"""
    token = get_admin_token()
    
    response = client.put(
        "/providers/test-provider-id",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "api_key": "new-api-key",
            "model_map": {"test": "new-model"}
        }
    )
    
    assert response.status_code == 200
    assert response.json()["provider_id"] == "test-provider-id"

def test_developer_cannot_update_provider():
    """Test that developer cannot update a provider"""
    token = get_developer_token()
    
    response = client.put(
        "/providers/test-provider-id",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "api_key": "new-api-key",
            "model_map": {"test": "new-model"}
        }
    )
    
    assert response.status_code == 403

def test_viewer_cannot_modify_providers():
    """Test that viewer role cannot modify providers"""
    token = get_viewer_token()
    
    # Test registration
    response = client.post(
        "/providers/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "provider_type": "test",
            "api_key": "test-api-key"
        }
    )
    assert response.status_code == 403
    
    # Test update
    response = client.put(
        "/providers/test-provider-id",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "api_key": "new-api-key"
        }
    )
    assert response.status_code == 403
    
    # Test deletion
    response = client.delete(
        "/providers/test-provider-id",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_invalid_token_cannot_access_providers():
    """Test that invalid tokens cannot access providers"""
    response = client.get(
        "/providers/",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401 