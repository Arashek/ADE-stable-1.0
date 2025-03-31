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
    with patch("...core.api.github_endpoints.get_current_user") as mock_get_user:
        mock_get_user.return_value = mock_user
        yield mock_get_user

def test_list_repositories(mock_auth):
    """Test listing repositories endpoint."""
    mock_repos = [
        {
            "name": "test-repo",
            "full_name": "user/test-repo",
            "description": "Test repository",
            "private": False
        }
    ]
    
    with patch("...core.integrations.github.GitHubClient.get_user_repositories") as mock_get_repos:
        mock_get_repos.return_value = mock_repos
        
        response = client.get("/api/github/repos")
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "test-repo"

def test_clone_repository(mock_auth):
    """Test cloning repository endpoint."""
    request_data = {
        "repo_url": "https://github.com/user/test-repo.git",
        "local_path": "/tmp/test-repo"
    }
    
    mock_repo = {
        "name": "test-repo",
        "full_name": "user/test-repo",
        "description": "Test repository"
    }
    
    with patch("...core.integrations.github.GitHubClient.clone_repository") as mock_clone:
        mock_clone.return_value = mock_repo
        
        response = client.post("/api/github/repos/clone", json=request_data)
        
        assert response.status_code == 200
        assert response.json()["name"] == "test-repo"

def test_list_branches(mock_auth):
    """Test listing branches endpoint."""
    mock_branches = [
        {
            "name": "main",
            "commit": {"sha": "abc123"}
        }
    ]
    
    with patch("...core.integrations.github.GitHubClient.get_branches") as mock_get_branches:
        mock_get_branches.return_value = mock_branches
        
        response = client.get("/api/github/repos/test-repo/branches")
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "main"

def test_create_branch(mock_auth):
    """Test creating branch endpoint."""
    request_data = {
        "branch_name": "feature/test",
        "base_branch": "main"
    }
    
    mock_branch = {
        "name": "feature/test",
        "commit": {"sha": "abc123"}
    }
    
    with patch("...core.integrations.github.GitHubClient.create_branch") as mock_create:
        mock_create.return_value = mock_branch
        
        response = client.post(
            "/api/github/repos/test-repo/branches",
            json=request_data
        )
        
        assert response.status_code == 200
        assert response.json()["name"] == "feature/test"

def test_commit_changes(mock_auth):
    """Test committing changes endpoint."""
    request_data = {
        "branch": "feature/test",
        "files": [{"path": "test.txt", "content": "test"}],
        "message": "Test commit"
    }
    
    mock_commit = {
        "sha": "abc123",
        "message": "Test commit"
    }
    
    with patch("...core.integrations.github.GitHubClient.commit_changes") as mock_commit_changes:
        mock_commit_changes.return_value = mock_commit
        
        response = client.post(
            "/api/github/repos/test-repo/commit",
            json=request_data
        )
        
        assert response.status_code == 200
        assert response.json()["sha"] == "abc123"

def test_list_pull_requests(mock_auth):
    """Test listing pull requests endpoint."""
    mock_prs = [
        {
            "number": 1,
            "title": "Test PR",
            "body": "Test description"
        }
    ]
    
    with patch("...core.integrations.github.GitHubClient.get_pull_requests") as mock_get_prs:
        mock_get_prs.return_value = mock_prs
        
        response = client.get("/api/github/repos/test-repo/pulls")
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["number"] == 1

def test_create_pull_request(mock_auth):
    """Test creating pull request endpoint."""
    request_data = {
        "title": "Test PR",
        "body": "Test description",
        "head_branch": "feature/test",
        "base_branch": "main"
    }
    
    mock_pr = {
        "number": 1,
        "title": "Test PR",
        "body": "Test description"
    }
    
    with patch("...core.integrations.github.GitHubClient.create_pull_request") as mock_create:
        mock_create.return_value = mock_pr
        
        response = client.post(
            "/api/github/repos/test-repo/pulls",
            json=request_data
        )
        
        assert response.status_code == 200
        assert response.json()["number"] == 1

def test_update_pull_request(mock_auth):
    """Test updating pull request endpoint."""
    request_data = {
        "title": "Updated PR",
        "body": "Updated description",
        "state": "closed"
    }
    
    mock_pr = {
        "number": 1,
        "title": "Updated PR",
        "body": "Updated description",
        "state": "closed"
    }
    
    with patch("...core.integrations.github.GitHubClient.update_pull_request") as mock_update:
        mock_update.return_value = mock_pr
        
        response = client.patch(
            "/api/github/repos/test-repo/pulls/1",
            json=request_data
        )
        
        assert response.status_code == 200
        assert response.json()["state"] == "closed"

def test_error_handling(mock_auth):
    """Test error handling in endpoints."""
    with patch("...core.integrations.github.GitHubClient.get_user_repositories") as mock_get_repos:
        mock_get_repos.side_effect = Exception("API Error")
        
        response = client.get("/api/github/repos")
        
        assert response.status_code == 500
        assert "Error fetching repositories" in response.json()["detail"] 