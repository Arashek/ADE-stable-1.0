import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from ...core.api.app import app
from ...core.models.user import User

client = TestClient(app)

@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    return User(
        id="test-user",
        username="testuser",
        email="test@example.com"
    )

@pytest.fixture
def mock_auth(mock_user):
    """Mock authentication."""
    with patch("...core.api.github_auth.get_current_user") as mock_get_user:
        mock_get_user.return_value = mock_user
        yield mock_get_user

def test_authorize_github(mock_auth):
    """Test GitHub OAuth authorization endpoint."""
    mock_auth_url = "https://github.com/login/oauth/authorize?client_id=test&state=test-state"
    
    with patch("...core.integrations.github.GitHubClient.get_oauth_authorization_url") as mock_get_url:
        mock_get_url.return_value = mock_auth_url
        
        response = client.get("/api/github/auth/oauth/authorize")
        
        assert response.status_code == 200
        assert response.json()["authorization_url"] == mock_auth_url

def test_github_oauth_callback(mock_auth):
    """Test GitHub OAuth callback endpoint."""
    mock_token_info = {
        "access_token": "test-token",
        "token_type": "bearer",
        "scope": "repo",
        "expires_in": 3600
    }
    
    with patch("...core.integrations.github.GitHubClient.validate_oauth_state") as mock_validate:
        mock_validate.return_value = True
        
        with patch("...core.integrations.github.GitHubClient.exchange_oauth_code") as mock_exchange:
            mock_exchange.return_value = mock_token_info
            
            response = client.get(
                "/api/github/auth/oauth/callback",
                params={"code": "test-code", "state": "test-state"}
            )
            
            assert response.status_code == 200
            assert response.json()["access_token"] == "test-token"

def test_github_oauth_callback_invalid_state(mock_auth):
    """Test GitHub OAuth callback with invalid state."""
    with patch("...core.integrations.github.GitHubClient.validate_oauth_state") as mock_validate:
        mock_validate.return_value = False
        
        response = client.get(
            "/api/github/auth/oauth/callback",
            params={"code": "test-code", "state": "invalid-state"}
        )
        
        assert response.status_code == 400
        assert "Invalid OAuth state" in response.json()["detail"]

def test_create_personal_token(mock_auth):
    """Test creating personal access token endpoint."""
    request_data = {
        "scopes": ["repo", "workflow"]
    }
    
    mock_token_info = {
        "access_token": "test-token",
        "token_type": "bearer",
        "scope": "repo workflow",
        "expires_in": 3600
    }
    
    with patch("...core.integrations.github.GitHubClient.create_personal_token") as mock_create:
        mock_create.return_value = mock_token_info
        
        response = client.post(
            "/api/github/auth/token",
            json=request_data
        )
        
        assert response.status_code == 200
        assert response.json()["access_token"] == "test-token"

def test_validate_token(mock_auth):
    """Test token validation endpoint."""
    mock_validation = {
        "valid": True,
        "scopes": ["repo", "workflow"],
        "expires_at": "2024-12-31T23:59:59Z"
    }
    
    with patch("...core.integrations.github.GitHubClient.validate_token") as mock_validate:
        mock_validate.return_value = mock_validation
        
        response = client.get("/api/github/auth/token/validate")
        
        assert response.status_code == 200
        assert response.json()["valid"] is True

def test_revoke_token(mock_auth):
    """Test token revocation endpoint."""
    with patch("...core.integrations.github.GitHubClient.revoke_token") as mock_revoke:
        mock_revoke.return_value = None
        
        response = client.delete("/api/github/auth/token")
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"

def test_error_handling(mock_auth):
    """Test error handling in authentication endpoints."""
    with patch("...core.integrations.github.GitHubClient.get_oauth_authorization_url") as mock_get_url:
        mock_get_url.side_effect = Exception("OAuth Error")
        
        response = client.get("/api/github/auth/oauth/authorize")
        
        assert response.status_code == 500
        assert "Error initiating OAuth flow" in response.json()["detail"] 