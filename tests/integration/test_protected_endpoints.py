import pytest
from fastapi.testclient import TestClient
from src.interfaces.api.main import app
from src.interfaces.api.auth import User, UserRole
from src.interfaces.api.auth import create_access_token

client = TestClient(app)

# Test data
test_users = {
    "regular_user": User(
        username="test_user",
        email="test@example.com",
        roles=[UserRole.USER]
    ),
    "developer": User(
        username="dev_user",
        email="dev@example.com",
        roles=[UserRole.USER, UserRole.DEVELOPER]
    ),
    "admin": User(
        username="admin_user",
        email="admin@example.com",
        roles=[UserRole.USER, UserRole.ADMIN]
    )
}

def get_auth_headers(user: User) -> dict:
    access_token = create_access_token(data={"sub": user.username, "roles": [role.value for role in user.roles]})
    return {"Authorization": f"Bearer {access_token}"}

def test_public_endpoint():
    """Test that public endpoint is accessible without authentication"""
    response = client.get("/api/public")
    assert response.status_code == 200
    assert response.json() == {"message": "This is a public endpoint"}

def test_user_endpoint_unauthorized():
    """Test that user endpoint requires authentication"""
    response = client.get("/api/user")
    assert response.status_code == 401

def test_user_endpoint_authorized():
    """Test that user endpoint is accessible with valid authentication"""
    headers = get_auth_headers(test_users["regular_user"])
    response = client.get("/api/user", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Hello, {test_users['regular_user'].username}!"
    assert data["roles"] == [UserRole.USER.value]

def test_developer_endpoint_unauthorized():
    """Test that developer endpoint requires DEVELOPER role"""
    headers = get_auth_headers(test_users["regular_user"])
    response = client.get("/api/developer", headers=headers)
    assert response.status_code == 403

def test_developer_endpoint_authorized():
    """Test that developer endpoint is accessible with DEVELOPER role"""
    headers = get_auth_headers(test_users["developer"])
    response = client.get("/api/developer", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Developer access granted"
    assert data["user"] == test_users["developer"].username
    assert UserRole.DEVELOPER.value in data["roles"]

def test_admin_endpoint_unauthorized():
    """Test that admin endpoint requires ADMIN role"""
    headers = get_auth_headers(test_users["developer"])
    response = client.get("/api/admin", headers=headers)
    assert response.status_code == 403

def test_admin_endpoint_authorized():
    """Test that admin endpoint is accessible with ADMIN role"""
    headers = get_auth_headers(test_users["admin"])
    response = client.get("/api/admin", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Admin access granted"
    assert data["user"] == test_users["admin"].username
    assert UserRole.ADMIN.value in data["roles"]

def test_management_endpoint_unauthorized():
    """Test that management endpoint requires either ADMIN or DEVELOPER role"""
    headers = get_auth_headers(test_users["regular_user"])
    response = client.get("/api/manage", headers=headers)
    assert response.status_code == 403

def test_management_endpoint_developer_authorized():
    """Test that management endpoint is accessible with DEVELOPER role"""
    headers = get_auth_headers(test_users["developer"])
    response = client.get("/api/manage", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Management access granted"
    assert data["user"] == test_users["developer"].username
    assert UserRole.DEVELOPER.value in data["roles"]

def test_management_endpoint_admin_authorized():
    """Test that management endpoint is accessible with ADMIN role"""
    headers = get_auth_headers(test_users["admin"])
    response = client.get("/api/manage", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Management access granted"
    assert data["user"] == test_users["admin"].username
    assert UserRole.ADMIN.value in data["roles"] 