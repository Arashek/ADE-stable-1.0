import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from ...core.integrations.github import GitHubClient, GitHubRateLimit

@pytest.fixture
def github_client():
    """Create a GitHub client instance for testing."""
    return GitHubClient()

@pytest.fixture
def rate_limit():
    """Create a rate limit instance for testing."""
    return GitHubRateLimit()

@pytest.mark.asyncio
async def test_get_user_repositories(github_client):
    """Test fetching user repositories."""
    # Mock API response
    mock_response = [
        {
            "name": "test-repo",
            "full_name": "user/test-repo",
            "description": "Test repository",
            "private": False
        }
    ]
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        
        repos = await github_client.get_user_repositories(Mock(id="test-user"))
        
        assert len(repos) == 1
        assert repos[0].name == "test-repo"
        assert repos[0].full_name == "user/test-repo"

@pytest.mark.asyncio
async def test_clone_repository(github_client):
    """Test cloning a repository."""
    repo_url = "https://github.com/user/test-repo.git"
    local_path = "/tmp/test-repo"
    
    with patch("git.Repo.clone_from") as mock_clone:
        repo = await github_client.clone_repository(repo_url, local_path)
        
        mock_clone.assert_called_once_with(repo_url, local_path)
        assert repo is not None

@pytest.mark.asyncio
async def test_get_branches(github_client):
    """Test fetching repository branches."""
    repo_name = "test-repo"
    mock_response = [
        {
            "name": "main",
            "commit": {"sha": "abc123"}
        }
    ]
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        
        branches = await github_client.get_branches(repo_name)
        
        assert len(branches) == 1
        assert branches[0]["name"] == "main"

@pytest.mark.asyncio
async def test_create_branch(github_client):
    """Test creating a new branch."""
    repo_name = "test-repo"
    branch_name = "feature/test"
    base_branch = "main"
    
    mock_response = {
        "name": branch_name,
        "commit": {"sha": "abc123"}
    }
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        
        branch = await github_client.create_branch(
            repo_name,
            branch_name,
            base_branch
        )
        
        assert branch["name"] == branch_name

@pytest.mark.asyncio
async def test_commit_changes(github_client):
    """Test committing changes to repository."""
    repo_name = "test-repo"
    branch = "feature/test"
    files = [{"path": "test.txt", "content": "test"}]
    message = "Test commit"
    
    mock_response = {
        "sha": "abc123",
        "message": message
    }
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        
        commit = await github_client.commit_changes(
            repo_name,
            branch,
            files,
            message
        )
        
        assert commit["sha"] == "abc123"
        assert commit["message"] == message

@pytest.mark.asyncio
async def test_create_pull_request(github_client):
    """Test creating a pull request."""
    repo_name = "test-repo"
    title = "Test PR"
    body = "Test description"
    head_branch = "feature/test"
    base_branch = "main"
    
    mock_response = {
        "number": 1,
        "title": title,
        "body": body
    }
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        
        pr = await github_client.create_pull_request(
            repo_name,
            title,
            body,
            head_branch,
            base_branch
        )
        
        assert pr["number"] == 1
        assert pr["title"] == title

@pytest.mark.asyncio
async def test_rate_limit_handling(rate_limit):
    """Test rate limit handling."""
    # Set initial rate limit
    rate_limit.update(5000, 5000, datetime.now())
    
    # Check if request is allowed
    assert rate_limit.can_make_request()
    
    # Update with depleted rate limit
    rate_limit.update(0, 5000, datetime.now())
    
    # Check if request is blocked
    assert not rate_limit.can_make_request()
    
    # Check delay calculation
    delay = rate_limit.get_delay()
    assert delay > 0

@pytest.mark.asyncio
async def test_token_management(github_client):
    """Test token management operations."""
    user_id = "test-user"
    token_info = {
        "access_token": "test-token",
        "token_type": "bearer",
        "scope": "repo"
    }
    
    # Test token storage
    await github_client.store_user_token(user_id, token_info)
    
    # Test token retrieval
    stored_token = await github_client.get_user_token(user_id)
    assert stored_token["access_token"] == "test-token"
    
    # Test token validation
    validation = await github_client.validate_token(user_id)
    assert validation["valid"]

@pytest.mark.asyncio
async def test_oauth_flow(github_client):
    """Test OAuth flow operations."""
    user_id = "test-user"
    
    # Test state generation
    state = github_client.generate_oauth_state(user_id)
    assert state is not None
    
    # Test state validation
    assert github_client.validate_oauth_state(state, user_id)
    
    # Test authorization URL generation
    auth_url = github_client.get_oauth_authorization_url(
        state=state,
        redirect_uri="http://localhost/callback"
    )
    assert "github.com" in auth_url
    assert state in auth_url

@pytest.mark.asyncio
async def test_error_handling(github_client):
    """Test error handling in GitHub client."""
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 404
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={"message": "Not Found"}
        )
        
        with pytest.raises(Exception) as exc_info:
            await github_client.get_user_repositories(Mock(id="test-user"))
        
        assert "Not Found" in str(exc_info.value) 