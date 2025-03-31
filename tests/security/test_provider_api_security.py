import pytest
from fastapi.testclient import TestClient
import json
import jwt
from datetime import datetime, timedelta

from src.main import app
from src.interfaces.api.auth import create_access_token, UserRole, JWT_SECRET_KEY, JWT_ALGORITHM

# Test client
client = TestClient(app)

# Security test cases
def test_missing_auth_header():
    """Test access with missing Authorization header"""
    response = client.get("/providers/")
    assert response.status_code == 401

def test_invalid_token_format():
    """Test access with invalid token format"""
    response = client.get(
        "/providers/",
        headers={"Authorization": "NotBearer token123"}
    )
    assert response.status_code == 401

def test_expired_token():
    """Test access with expired token"""
    # Create expired token
    expired_data = {
        "sub": "admin",
        "roles": [UserRole.ADMIN],
        "exp": datetime.utcnow() - timedelta(minutes=30)
    }
    expired_token = jwt.encode(expired_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    response = client.get(
        "/providers/",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401

def test_tampered_token():
    """Test access with tampered token payload"""
    # Create valid token
    valid_token = create_access_token(
        data={"sub": "admin", "roles": [UserRole.ADMIN]}
    )
    
    # Decode, tamper, and re-encode with wrong secret
    payload = jwt.decode(valid_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    payload["roles"] = [UserRole.ADMIN, "superadmin"]  # Add non-existent role
    tampered_token = jwt.encode(payload, "wrong_secret", algorithm=JWT_ALGORITHM)
    
    response = client.get(
        "/providers/",
        headers={"Authorization": f"Bearer {tampered_token}"}
    )
    assert response.status_code == 401

def test_insufficient_permissions():
    """Test access with insufficient permissions"""
    # Create token with insufficient permissions
    viewer_token = create_access_token(
        data={"sub": "viewer", "roles": [UserRole.VIEWER]}
    )
    
    # Try to create a provider (requires ADMIN)
    response = client.post(
        "/providers/",
        headers={"Authorization": f"Bearer {viewer_token}"},
        json={"provider_type": "test", "api_key": "test-key"}
    )
    assert response.status_code == 403

def test_credential_leakage():
    """Test that API keys are not leaked in responses"""
    # Create admin token
    admin_token = create_access_token(
        data={"sub": "admin", "roles": [UserRole.ADMIN]}
    )
    
    # Register a provider
    response = client.post(
        "/providers/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"provider_type": "test", "api_key": "super-secret-api-key"}
    )
    
    # Check that API key is not in response
    assert response.status_code == 200
    assert "api_key" not in response.json()
    assert "super-secret-api-key" not in response.text
    
    # Get provider details
    provider_id = response.json()["provider_id"]
    response = client.get(
        f"/providers/{provider_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Check that API key is not in response
    assert response.status_code == 200
    assert "api_key" not in response.json()
    assert "super-secret-api-key" not in response.text

def test_rate_limiting():
    """Test API rate limiting"""
    # Create admin token
    admin_token = create_access_token(
        data={"sub": "admin", "roles": [UserRole.ADMIN]}
    )
    
    # Make multiple requests in quick succession
    for _ in range(100):  # Assuming rate limit is less than 100 requests per minute
        response = client.get(
            "/providers/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
    
    # Next request should be rate limited
    response = client.get(
        "/providers/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 429

def test_input_validation():
    """Test input validation for provider registration"""
    # Create admin token
    admin_token = create_access_token(
        data={"sub": "admin", "roles": [UserRole.ADMIN]}
    )
    
    # Test with invalid provider type
    response = client.post(
        "/providers/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"provider_type": "invalid_type", "api_key": "test-key"}
    )
    assert response.status_code == 422
    
    # Test with empty API key
    response = client.post(
        "/providers/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"provider_type": "openai", "api_key": ""}
    )
    assert response.status_code == 422

def test_csrf_protection():
    """Test CSRF protection"""
    # Create admin token
    admin_token = create_access_token(
        data={"sub": "admin", "roles": [UserRole.ADMIN]}
    )
    
    # Try to create provider without CSRF token
    response = client.post(
        "/providers/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"provider_type": "test", "api_key": "test-key"}
    )
    assert response.status_code == 403

def test_sql_injection_prevention():
    """Test SQL injection prevention"""
    # Create admin token
    admin_token = create_access_token(
        data={"sub": "admin", "roles": [UserRole.ADMIN]}
    )
    
    # Try to inject SQL in provider type
    response = client.post(
        "/providers/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "provider_type": "'; DROP TABLE providers; --",
            "api_key": "test-key"
        }
    )
    assert response.status_code == 422

def test_xss_prevention():
    """Test XSS prevention in provider responses"""
    # Create admin token
    admin_token = create_access_token(
        data={"sub": "admin", "roles": [UserRole.ADMIN]}
    )
    
    # Try to inject XSS in provider type
    response = client.post(
        "/providers/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "provider_type": "<script>alert('xss')</script>",
            "api_key": "test-key"
        }
    )
    assert response.status_code == 422 