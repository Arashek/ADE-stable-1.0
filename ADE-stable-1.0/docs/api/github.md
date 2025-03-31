# GitHub Integration API Documentation

## Overview

The GitHub Integration API provides endpoints for interacting with GitHub repositories, including repository management, branch operations, commits, pull requests, and authentication.

## Authentication

All endpoints require authentication using a JWT token. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Repository Management

### List Repositories

```http
GET /api/github/repos
```

Lists all repositories accessible to the authenticated user.

**Response**
```json
[
  {
    "id": "123456789",
    "name": "example-repo",
    "url": "https://github.com/user/example-repo",
    "description": "Example repository",
    "owner": "user",
    "is_private": false,
    "last_updated": "2024-03-20T10:00:00Z",
    "language": "Python",
    "size": 1024,
    "metadata": {
      "stars": 10,
      "forks": 5,
      "issues": 2,
      "default_branch": "main"
    }
  }
]
```

### Clone Repository

```http
POST /api/github/repos/clone
```

Clones a GitHub repository to a specified local path.

**Request Body**
```json
{
  "repo_url": "https://github.com/user/example-repo.git",
  "local_path": "/path/to/local/directory"
}
```

**Response**
```json
{
  "id": "123456789",
  "name": "example-repo",
  "url": "https://github.com/user/example-repo",
  "local_path": "/path/to/local/directory",
  "description": "Example repository",
  "owner": "user",
  "is_private": false,
  "last_updated": "2024-03-20T10:00:00Z",
  "language": "Python",
  "size": 1024,
  "metadata": {
    "stars": 10,
    "forks": 5,
    "issues": 2,
    "default_branch": "main"
  }
}
```

## Branch Operations

### List Branches

```http
GET /api/github/repos/{repo_name}/branches
```

Lists all branches in a repository.

**Parameters**
- `repo_name`: Name of the repository (format: `owner/repo`)

**Response**
```json
[
  {
    "name": "main",
    "sha": "abc123...",
    "protected": true,
    "protection": {
      "required_status_checks": null,
      "enforce_admins": false
    }
  }
]
```

### Create Branch

```http
POST /api/github/repos/{repo_name}/branches
```

Creates a new branch in the repository.

**Parameters**
- `repo_name`: Name of the repository (format: `owner/repo`)

**Request Body**
```json
{
  "branch_name": "feature/new-feature",
  "base_branch": "main"
}
```

**Response**
```json
{
  "name": "feature/new-feature",
  "sha": "abc123...",
  "protected": false,
  "protection": null
}
```

## Commit Operations

### Commit Changes

```http
POST /api/github/repos/{repo_name}/commit
```

Commits changes to the repository.

**Parameters**
- `repo_name`: Name of the repository (format: `owner/repo`)

**Request Body**
```json
{
  "branch": "feature/new-feature",
  "files": [
    {
      "path": "path/to/file.txt",
      "content": "New file content"
    }
  ],
  "message": "Add new feature"
}
```

**Response**
```json
{
  "sha": "abc123...",
  "message": "Add new feature",
  "author": "John Doe",
  "date": "2024-03-20T10:00:00Z"
}
```

## Pull Request Operations

### List Pull Requests

```http
GET /api/github/repos/{repo_name}/pulls
```

Lists pull requests in a repository.

**Parameters**
- `repo_name`: Name of the repository (format: `owner/repo`)
- `state`: Filter by state (open, closed, all) (default: "open")

**Response**
```json
[
  {
    "number": 1,
    "title": "Add new feature",
    "body": "Description of changes",
    "state": "open",
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z",
    "head_branch": "feature/new-feature",
    "base_branch": "main",
    "user": "john-doe",
    "labels": ["enhancement"]
  }
]
```

### Create Pull Request

```http
POST /api/github/repos/{repo_name}/pulls
```

Creates a new pull request.

**Parameters**
- `repo_name`: Name of the repository (format: `owner/repo`)

**Request Body**
```json
{
  "title": "Add new feature",
  "body": "Description of changes",
  "head_branch": "feature/new-feature",
  "base_branch": "main"
}
```

**Response**
```json
{
  "number": 1,
  "title": "Add new feature",
  "body": "Description of changes",
  "state": "open",
  "created_at": "2024-03-20T10:00:00Z",
  "updated_at": "2024-03-20T10:00:00Z",
  "head_branch": "feature/new-feature",
  "base_branch": "main"
}
```

### Update Pull Request

```http
PATCH /api/github/repos/{repo_name}/pulls/{pr_number}
```

Updates an existing pull request.

**Parameters**
- `repo_name`: Name of the repository (format: `owner/repo`)
- `pr_number`: Pull request number

**Request Body**
```json
{
  "title": "Updated title",
  "body": "Updated description",
  "state": "closed"
}
```

**Response**
```json
{
  "number": 1,
  "title": "Updated title",
  "body": "Updated description",
  "state": "closed",
  "created_at": "2024-03-20T10:00:00Z",
  "updated_at": "2024-03-20T10:00:00Z",
  "head_branch": "feature/new-feature",
  "base_branch": "main"
}
```

## Authentication

### OAuth Authorization

```http
GET /api/github/auth/oauth/authorize
```

Initiates the GitHub OAuth flow.

**Response**
```json
{
  "authorization_url": "https://github.com/login/oauth/authorize?client_id=...&state=..."
}
```

### OAuth Callback

```http
GET /api/github/auth/oauth/callback
```

Handles the OAuth callback from GitHub.

**Parameters**
- `code`: OAuth authorization code
- `state`: OAuth state for CSRF protection

**Response**
```json
{
  "access_token": "gho_...",
  "token_type": "bearer",
  "scope": "repo",
  "expires_in": 3600
}
```

### Create Personal Token

```http
POST /api/github/auth/token
```

Creates a GitHub personal access token.

**Request Body**
```json
{
  "scopes": ["repo", "workflow"]
}
```

**Response**
```json
{
  "access_token": "gho_...",
  "token_type": "bearer",
  "scope": "repo workflow",
  "expires_in": 3600
}
```

### Validate Token

```http
GET /api/github/auth/token/validate
```

Validates the current GitHub token.

**Response**
```json
{
  "valid": true,
  "scopes": ["repo", "workflow"],
  "expires_at": "2024-12-31T23:59:59Z"
}
```

### Revoke Token

```http
DELETE /api/github/auth/token
```

Revokes the current GitHub token.

**Response**
```json
{
  "status": "success"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or missing authentication token"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

The API implements GitHub's rate limiting. When rate limits are exceeded, the API will:
1. Return a 403 Forbidden response
2. Include rate limit information in response headers
3. Automatically retry requests when the rate limit resets

### Rate Limit Headers

GitHub includes the following headers in all API responses:

```http
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4999
X-RateLimit-Reset: 1619999999
X-RateLimit-Used: 1
```

- `X-RateLimit-Limit`: Maximum number of requests per hour
- `X-RateLimit-Remaining`: Number of requests remaining in the current window
- `X-RateLimit-Reset`: Unix timestamp when the rate limit window resets
- `X-RateLimit-Used`: Number of requests made in the current window

### Handling Rate Limits

1. **Check Headers Before Making Requests**
```python
import time

def make_request():
    response = requests.get('/api/github/repos')
    remaining = int(response.headers['X-RateLimit-Remaining'])
    reset_time = int(response.headers['X-RateLimit-Reset'])
    
    if remaining <= 0:
        wait_time = reset_time - int(time.time())
        if wait_time > 0:
            time.sleep(wait_time)
        return make_request()
    return response
```

2. **Implement Exponential Backoff**
```python
def make_request_with_backoff(max_retries=5):
    for attempt in range(max_retries):
        try:
            return requests.get('/api/github/repos')
        except RateLimitExceeded:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
    raise MaxRetriesExceeded()
```

## Specific Error Scenarios

### Repository Errors

1. **Repository Not Found**
```json
{
  "detail": "Repository not found",
  "code": "REPO_NOT_FOUND",
  "repository": "owner/repo",
  "suggestions": [
    "Check if the repository name is correct",
    "Verify you have access to the repository",
    "Ensure the repository exists"
  ]
}
```

2. **Permission Denied**
```json
{
  "detail": "Permission denied",
  "code": "PERMISSION_DENIED",
  "repository": "owner/repo",
  "required_permissions": ["write", "admin"],
  "current_permissions": ["read"]
}
```

### Authentication Errors

1. **Token Expired**
```json
{
  "detail": "Token has expired",
  "code": "TOKEN_EXPIRED",
  "expired_at": "2024-03-20T10:00:00Z",
  "suggestions": [
    "Create a new token",
    "Refresh the existing token"
  ]
}
```

2. **Invalid Scopes**
```json
{
  "detail": "Insufficient scopes",
  "code": "INSUFFICIENT_SCOPES",
  "required_scopes": ["repo", "workflow"],
  "current_scopes": ["repo"],
  "suggestions": [
    "Update token with required scopes",
    "Create a new token with correct scopes"
  ]
}
```

## Use Case Examples

### 1. Creating a Feature Branch and Pull Request

```python
# 1. Create a new branch
branch_response = requests.post(
    '/api/github/repos/owner/repo/branches',
    json={
        "branch_name": "feature/user-authentication",
        "base_branch": "main"
    }
)

# 2. Commit changes
commit_response = requests.post(
    '/api/github/repos/owner/repo/commit',
    json={
        "branch": "feature/user-authentication",
        "files": [
            {
                "path": "src/auth/user.py",
                "content": "def authenticate_user(): ..."
            }
        ],
        "message": "Add user authentication feature"
    }
)

# 3. Create pull request
pr_response = requests.post(
    '/api/github/repos/owner/repo/pulls',
    json={
        "title": "Add user authentication",
        "body": "Implements JWT-based user authentication",
        "head_branch": "feature/user-authentication",
        "base_branch": "main"
    }
)
```

### 2. Automated Repository Backup

```python
def backup_repository(repo_name):
    # 1. List all branches
    branches = requests.get(f'/api/github/repos/{repo_name}/branches').json()
    
    # 2. Clone repository
    clone_response = requests.post(
        '/api/github/repos/clone',
        json={
            "repo_url": f"https://github.com/{repo_name}.git",
            "local_path": f"/backups/{repo_name}"
        }
    )
    
    # 3. Monitor progress via WebSocket
    ws = websocket.connect('ws://api.example.com/ws')
    ws.send(json.dumps({
        "type": "SUBSCRIBE",
        "event_type": "REPOSITORY_CLONED",
        "filters": {"repo_name": repo_name}
    }))
    
    # Wait for clone completion
    while True:
        event = json.loads(ws.recv())
        if event["type"] == "REPOSITORY_CLONED":
            break
```

## WebSocket Events

### Event Types and Payloads

1. **Repository Events**

```json
// REPOSITORY_CLONED
{
  "type": "REPOSITORY_CLONED",
  "data": {
    "repo_name": "owner/repo",
    "local_path": "/path/to/local/directory",
    "timestamp": "2024-03-20T10:00:00Z",
    "size": 1024,
    "branch_count": 5
  }
}

// BRANCH_CREATED
{
  "type": "BRANCH_CREATED",
  "data": {
    "repo_name": "owner/repo",
    "branch_name": "feature/new-feature",
    "base_branch": "main",
    "sha": "abc123...",
    "timestamp": "2024-03-20T10:00:00Z"
  }
}

// COMMIT_CREATED
{
  "type": "COMMIT_CREATED",
  "data": {
    "repo_name": "owner/repo",
    "branch": "feature/new-feature",
    "sha": "abc123...",
    "message": "Add new feature",
    "author": "John Doe",
    "timestamp": "2024-03-20T10:00:00Z",
    "files_changed": ["src/feature.py"]
  }
}
```

2. **Pull Request Events**

```json
// PULL_REQUEST_CREATED
{
  "type": "PULL_REQUEST_CREATED",
  "data": {
    "repo_name": "owner/repo",
    "number": 1,
    "title": "Add new feature",
    "state": "open",
    "user": "john-doe",
    "timestamp": "2024-03-20T10:00:00Z"
  }
}

// PULL_REQUEST_UPDATED
{
  "type": "PULL_REQUEST_UPDATED",
  "data": {
    "repo_name": "owner/repo",
    "number": 1,
    "state": "closed",
    "merged": true,
    "timestamp": "2024-03-20T10:00:00Z"
  }
}
```

### WebSocket Connection Example

```python
import websocket
import json

def connect_to_github_events():
    ws = websocket.connect('ws://api.example.com/ws')
    
    # Subscribe to repository events
    ws.send(json.dumps({
        "type": "SUBSCRIBE",
        "event_type": "REPOSITORY_EVENTS",
        "filters": {
            "repo_name": "owner/repo"
        }
    }))
    
    # Handle incoming events
    while True:
        try:
            event = json.loads(ws.recv())
            handle_event(event)
        except websocket.WebSocketConnectionClosedException:
            # Implement reconnection logic
            break

def handle_event(event):
    event_type = event["type"]
    data = event["data"]
    
    if event_type == "REPOSITORY_CLONED":
        print(f"Repository {data['repo_name']} cloned successfully")
    elif event_type == "BRANCH_CREATED":
        print(f"New branch {data['branch_name']} created")
    elif event_type == "COMMIT_CREATED":
        print(f"New commit: {data['message']}")
```

## Caching

### Repository Metadata Cache

Repository metadata is cached for 5 minutes to reduce API calls. The cache includes:
- Repository details
- Branch information
- Pull request counts
- Issue counts

### Cache Invalidation

The cache is automatically invalidated when:
1. A new commit is pushed
2. A branch is created or deleted
3. A pull request is created or updated
4. Repository settings are changed

### Cache Headers

```http
Cache-Control: public, max-age=300
ETag: "abc123..."
Last-Modified: Wed, 20 Mar 2024 10:00:00 GMT
```

### Cache Control Example

```python
def get_repository_metadata(repo_name):
    # Check cache first
    cache_key = f"repo:{repo_name}:metadata"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data
    
    # If not in cache, fetch from API
    response = requests.get(f'/api/github/repos/{repo_name}')
    data = response.json()
    
    # Store in cache
    cache.set(cache_key, data, timeout=300)  # 5 minutes
    
    return data
```

## Best Practices

1. **Authentication**
   - Use OAuth for web-based applications
   - Use personal access tokens for automated scripts
   - Store tokens securely and rotate them regularly

2. **Rate Limiting**
   - Monitor rate limit headers
   - Implement exponential backoff for retries
   - Cache responses when possible

3. **Repository Operations**
   - Use appropriate branch naming conventions
   - Write clear commit messages
   - Keep pull requests focused and small

4. **Security**
   - Validate all input parameters
   - Use HTTPS for all requests
   - Implement proper access controls
   - Follow the principle of least privilege 