"""Tests for the Provider Registry API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime
import os

from src.core.models.provider_registry import ModelCapability, ProviderRegistry, Provider, ProviderType
from src.interfaces.api.providers import router
from src.interfaces.api.auth import User, UserRole
from src.main import app
from src.utils.encryption import encrypt_value, decrypt_value

# Test data
TEST_PROVIDER = {
    "provider_id": "test-provider-id",
    "provider_type": ProviderType.OPENAI,
    "api_key": "test-api-key",
    "model_map": {"gpt-4": "gpt-4", "gpt-3.5-turbo": "gpt-3.5-turbo"},
    "default_parameters": {"temperature": 0.7},
    "description": "Test OpenAI Provider",
    "rate_limit": 60,
    "is_active": True,
    "created_at": datetime.now(),
    "updated_at": datetime.now()
}

# Fixtures
@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

@pytest.fixture
def mock_provider_registry():
    """Create a mock provider registry."""
    with patch('src.interfaces.api.providers.provider_registry') as mock:
        yield mock

@pytest.fixture
def admin_user():
    """Create an admin user."""
    return User(
        id="admin-id",
        username="admin",
        email="admin@example.com",
        role=UserRole.ADMIN,
        is_active=True
    )

@pytest.fixture
def regular_user():
    """Create a regular user."""
    return User(
        id="user-id",
        username="user",
        email="user@example.com",
        role=UserRole.USER,
        is_active=True
    )

@pytest.fixture
def test_provider():
    """Create a test provider instance."""
    return Provider(**TEST_PROVIDER)

# Test cases
def test_register_provider_admin(client, mock_provider_registry, admin_user):
    """Test registering a provider (admin only)."""
    # Mock the provider registry
    mock_provider = MagicMock(**TEST_PROVIDER)
    mock_provider_registry.register_provider.return_value = mock_provider
    
    # Test the endpoint
    response = client.post(
        "/providers/",
        json={
            "provider_type": "openai",
            "api_key": "test-api-key",
            "model_map": {"gpt-4": "gpt-4"},
            "description": "Test Provider"
        },
        headers={"Authorization": f"Bearer {admin_user.id}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["provider_id"] == TEST_PROVIDER["provider_id"]
    assert data["provider_type"] == "openai"
    assert data["is_active"] is True
    
    # Verify the provider registry was called
    mock_provider_registry.register_provider.assert_called_once()

def test_register_provider_unauthorized(client, regular_user):
    """Test registering a provider without admin role."""
    response = client.post(
        "/providers/",
        json={
            "provider_type": "openai",
            "api_key": "test-api-key"
        },
        headers={"Authorization": f"Bearer {regular_user.id}"}
    )
    
    assert response.status_code == 403

def test_list_providers(client, mock_provider_registry, regular_user):
    """Test listing providers."""
    # Mock the provider registry
    mock_provider = MagicMock(**TEST_PROVIDER)
    mock_provider_registry.list_providers.return_value = [mock_provider]
    
    # Test the endpoint
    response = client.get(
        "/providers/",
        headers={"Authorization": f"Bearer {regular_user.id}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["provider_id"] == TEST_PROVIDER["provider_id"]
    
    # Verify the provider registry was called
    mock_provider_registry.list_providers.assert_called_once_with(include_inactive=False)

def test_get_provider(client, mock_provider_registry, regular_user):
    """Test getting a provider by ID."""
    # Mock the provider registry
    mock_provider = MagicMock(**TEST_PROVIDER)
    mock_provider_registry.get_provider.return_value = mock_provider
    
    # Test the endpoint
    response = client.get(
        f"/providers/{TEST_PROVIDER['provider_id']}",
        headers={"Authorization": f"Bearer {regular_user.id}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["provider_id"] == TEST_PROVIDER["provider_id"]
    
    # Verify the provider registry was called
    mock_provider_registry.get_provider.assert_called_once_with(TEST_PROVIDER["provider_id"])

def test_get_provider_not_found(client, mock_provider_registry, regular_user):
    """Test getting a non-existent provider."""
    # Mock the provider registry
    mock_provider_registry.get_provider.return_value = None
    
    # Test the endpoint
    response = client.get(
        "/providers/non-existent-id",
        headers={"Authorization": f"Bearer {regular_user.id}"}
    )
    
    # Verify response
    assert response.status_code == 404

def test_update_provider_admin(client, mock_provider_registry, admin_user):
    """Test updating a provider (admin only)."""
    # Mock the provider registry
    mock_provider = MagicMock(**TEST_PROVIDER)
    mock_provider_registry.get_provider.return_value = mock_provider
    mock_provider_registry.update_provider.return_value = True
    
    # Test the endpoint
    response = client.put(
        f"/providers/{TEST_PROVIDER['provider_id']}",
        json={
            "description": "Updated Description",
            "rate_limit": 120
        },
        headers={"Authorization": f"Bearer {admin_user.id}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["provider_id"] == TEST_PROVIDER["provider_id"]
    assert data["description"] == "Updated Description"
    assert data["rate_limit"] == 120
    
    # Verify the provider registry was called
    mock_provider_registry.get_provider.assert_called_once()
    mock_provider_registry.update_provider.assert_called_once()

def test_update_provider_unauthorized(client, regular_user):
    """Test updating a provider without admin role."""
    response = client.put(
        f"/providers/{TEST_PROVIDER['provider_id']}",
        json={"description": "Updated Description"},
        headers={"Authorization": f"Bearer {regular_user.id}"}
    )
    
    assert response.status_code == 403

def test_delete_provider_admin(client, mock_provider_registry, admin_user):
    """Test deleting a provider (admin only)."""
    # Mock the provider registry
    mock_provider_registry.unregister_provider.return_value = True
    
    # Test the endpoint
    response = client.delete(
        f"/providers/{TEST_PROVIDER['provider_id']}",
        headers={"Authorization": f"Bearer {admin_user.id}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Provider {TEST_PROVIDER['provider_id']} deleted successfully"
    
    # Verify the provider registry was called
    mock_provider_registry.unregister_provider.assert_called_once_with(TEST_PROVIDER["provider_id"])

def test_delete_provider_unauthorized(client, regular_user):
    """Test deleting a provider without admin role."""
    response = client.delete(
        f"/providers/{TEST_PROVIDER['provider_id']}",
        headers={"Authorization": f"Bearer {regular_user.id}"}
    )
    
    assert response.status_code == 403

def test_list_capabilities(client, regular_user):
    """Test listing available capabilities."""
    # Test the endpoint
    response = client.get(
        "/providers/capabilities/",
        headers={"Authorization": f"Bearer {regular_user.id}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "capabilities" in data
    assert all(isinstance(cap, str) for cap in data["capabilities"])
    assert all(cap in [c.value for c in ModelCapability] for cap in data["capabilities"])

def test_test_provider_admin(client, mock_provider_registry, admin_user):
    """Test testing a provider (admin only)."""
    # Mock the provider registry
    mock_provider = MagicMock(**TEST_PROVIDER)
    mock_provider_registry.get_provider.return_value = mock_provider
    mock_provider_registry.test_provider.return_value = {
        "success": True,
        "message": "Provider test successful",
        "capabilities_tested": ["text_generation", "planning"],
        "errors": []
    }
    
    # Test the endpoint
    response = client.get(
        f"/providers/{TEST_PROVIDER['provider_id']}/test",
        headers={"Authorization": f"Bearer {admin_user.id}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["provider_id"] == TEST_PROVIDER["provider_id"]
    assert len(data["capabilities_tested"]) > 0
    
    # Verify the provider registry was called
    mock_provider_registry.get_provider.assert_called_once()
    mock_provider_registry.test_provider.assert_called_once()

def test_test_provider_unauthorized(client, regular_user):
    """Test testing a provider without admin role."""
    response = client.get(
        f"/providers/{TEST_PROVIDER['provider_id']}/test",
        headers={"Authorization": f"Bearer {regular_user.id}"}
    )
    
    assert response.status_code == 403

def test_test_provider_not_found(client, mock_provider_registry, admin_user):
    """Test testing a non-existent provider."""
    # Mock the provider registry
    mock_provider_registry.get_provider.return_value = None
    
    # Test the endpoint
    response = client.get(
        "/providers/non-existent-id/test",
        headers={"Authorization": f"Bearer {admin_user.id}"}
    )
    
    # Verify response
    assert response.status_code == 404

def test_invalid_provider_type(client, mock_provider_registry, admin_user):
    """Test registering a provider with invalid type."""
    # Mock the provider registry to raise ValueError
    mock_provider_registry.register_provider.side_effect = ValueError("Invalid provider type")
    
    # Test the endpoint
    response = client.post(
        "/providers/",
        json={
            "provider_type": "invalid-type",
            "api_key": "test-api-key"
        },
        headers={"Authorization": f"Bearer {admin_user.id}"}
    )
    
    # Verify response
    assert response.status_code == 400
    assert "Invalid provider type" in response.json()["detail"]

# Encryption tests
def test_provider_encryption(test_provider):
    """Test provider credential encryption."""
    # Test encryption
    provider_dict = test_provider.to_dict()
    assert provider_dict["api_key"] != TEST_PROVIDER["api_key"]
    assert provider_dict["api_key"] == encrypt_value(TEST_PROVIDER["api_key"])
    
    # Test decryption
    decrypted_provider = Provider.from_dict(provider_dict)
    assert decrypted_provider.api_key == TEST_PROVIDER["api_key"]

def test_provider_update_with_encryption(mock_provider_registry, admin_user):
    """Test updating provider with encrypted credentials."""
    # Mock the provider registry
    mock_provider = MagicMock(**TEST_PROVIDER)
    mock_provider_registry.get_provider.return_value = mock_provider
    mock_provider_registry.update_provider.return_value = True
    
    # Test updating with new API key
    new_api_key = "new-api-key"
    response = client.put(
        f"/providers/{TEST_PROVIDER['provider_id']}",
        json={"api_key": new_api_key},
        headers={"Authorization": f"Bearer {admin_user.id}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["provider_id"] == TEST_PROVIDER["provider_id"]
    
    # Verify the provider registry was called with encrypted API key
    mock_provider_registry.update_provider.assert_called_once()
    call_args = mock_provider_registry.update_provider.call_args[1]
    assert call_args["api_key"] == encrypt_value(new_api_key)

def test_provider_registry_encryption(test_provider):
    """Test provider registry encryption handling."""
    registry = ProviderRegistry()
    
    # Register provider
    registry.register_provider(test_provider)
    
    # Verify provider is stored with encrypted credentials
    stored_provider = registry.get_provider(test_provider.provider_id)
    assert stored_provider.api_key == test_provider.api_key
    
    # Verify raw storage is encrypted
    raw_provider = registry._providers[test_provider.provider_id]
    assert raw_provider.api_key != test_provider.api_key
    assert raw_provider.api_key == encrypt_value(test_provider.api_key) 