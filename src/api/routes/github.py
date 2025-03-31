from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from typing import List, Dict, Optional
import os
from src.core.auth import get_current_user
from src.core.github import GitHubManager, get_github_client
from src.models.user import User

router = APIRouter()

# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_CALLBACK_URL = os.getenv("GITHUB_CALLBACK_URL")

@router.get("/auth/github")
async def github_auth():
    """Initiate GitHub OAuth flow"""
    if not all([GITHUB_CLIENT_ID, GITHUB_CALLBACK_URL]):
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")
    
    auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_CALLBACK_URL}&scope=repo"
    return RedirectResponse(auth_url)

@router.get("/auth/github/callback")
async def github_callback(code: str, request: Request):
    """Handle GitHub OAuth callback"""
    if not all([GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_CALLBACK_URL]):
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")
    
    # Exchange code for access token
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_CALLBACK_URL
            }
        ) as response:
            data = await response.json()
            if "error" in data:
                raise HTTPException(status_code=400, detail=data.get("error_description", "GitHub OAuth failed"))
            
            access_token = data["access_token"]
            
            # Store the access token in the user's session or database
            # This is a simplified example - you should implement proper token storage
            request.session["github_token"] = access_token
            
            return RedirectResponse(url="/dashboard")

@router.post("/github/repos", response_model=Dict)
async def create_repository(
    name: str,
    description: str = "",
    private: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Create a new GitHub repository"""
    github_token = current_user.github_token  # You'll need to add this to your User model
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub not connected")
    
    github_client = await get_github_client(github_token)
    return await github_client.create_repository(name, description, private)

@router.get("/github/repos", response_model=List[Dict])
async def list_repositories(current_user: User = Depends(get_current_user)):
    """List all GitHub repositories"""
    github_token = current_user.github_token
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub not connected")
    
    github_client = await get_github_client(github_token)
    return await github_client.list_repositories()

@router.get("/github/repos/{repo_name}", response_model=Dict)
async def get_repository(
    repo_name: str,
    current_user: User = Depends(get_current_user)
):
    """Get repository details"""
    github_token = current_user.github_token
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub not connected")
    
    github_client = await get_github_client(github_token)
    return await github_client.get_repository(repo_name)

@router.post("/github/repos/{repo_name}/push")
async def push_code(
    repo_name: str,
    file_path: str,
    content: str,
    commit_message: str,
    current_user: User = Depends(get_current_user)
):
    """Push code to a GitHub repository"""
    github_token = current_user.github_token
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub not connected")
    
    github_client = await get_github_client(github_token)
    return await github_client.push_code(repo_name, file_path, content, commit_message)

@router.delete("/github/repos/{repo_name}")
async def delete_repository(
    repo_name: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a GitHub repository"""
    github_token = current_user.github_token
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub not connected")
    
    github_client = await get_github_client(github_token)
    return await github_client.delete_repository(repo_name)

# Branch Management
@router.post("/github/repos/{repo_name}/branches")
async def create_branch(
    repo_name: str,
    branch_name: str,
    base_branch: str = "main",
    current_user: User = Depends(get_current_user)
):
    """Create a new branch in a repository"""
    github_token = current_user.github_token
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub not connected")
    
    github_client = await get_github_client(github_token)
    return await github_client.create_branch(repo_name, branch_name, base_branch)

@router.get("/github/repos/{repo_name}/branches")
async def list_branches(
    repo_name: str,
    current_user: User = Depends(get_current_user)
):
    """List all branches in a repository"""
    github_token = current_user.github_token
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub not connected")
    
    github_client = await get_github_client(github_token)
    return await github_client.list_branches(repo_name)

# Pull Request Management
@router.post("/github/repos/{repo_name}/pull-requests")
async def create_pull_request(
    repo_name: str,
    title: str,
    body: str,
    head_branch: str,
    base_branch: str = "main",
    current_user: User = Depends(get_current_user)
):
    """Create a pull request"""
    github_token = current_user.github_token
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub not connected")
    
    github_client = await get_github_client(github_token)
    return await github_client.create_pull_request(
        repo_name, title, body, head_branch, base_branch
    )

@router.get("/github/repos/{repo_name}/pull-requests")
async def list_pull_requests(
    repo_name: str,
    state: str = Query("open", enum=["open", "closed", "all"]),
    sort: str = Query("created", enum=["created", "updated", "popularity", "long-running"]),
    direction: str = Query("desc", enum=["asc", "desc"]),
    current_user: User = Depends(get_current_user)
):
    """List pull requests in a repository"""
    github_token = current_user.github_token
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub not connected")
    
    github_client = await get_github_client(github_token)
    return await github_client.list_pull_requests(repo_name, state, sort, direction)

# Repository Templates
@router.post("/github/repos/from-template")
async def create_from_template(
    template_repo: str,
    name: str,
    description: str = "",
    private: bool = True,
    include_all_branches: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Create a repository from a template"""
    github_token = current_user.github_token
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub not connected")
    
    github_client = await get_github_client(github_token)
    return await github_client.create_from_template(
        template_repo, name, description, private, include_all_branches
    )

# Webhook Management
@router.post("/github/repos/{repo_name}/webhooks")
async def create_webhook(
    repo_name: str,
    webhook_url: str,
    events: List[str] = ["push", "pull_request"],
    content_type: str = "json",
    current_user: User = Depends(get_current_user)
):
    """Create a webhook for a repository"""
    github_token = current_user.github_token
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub not connected")
    
    github_client = await get_github_client(github_token)
    return await github_client.create_webhook(repo_name, webhook_url, events, content_type)

# Collaboration Management
@router.post("/github/repos/{repo_name}/collaborators/{username}")
async def add_collaborator(
    repo_name: str,
    username: str,
    permission: str = Query("push", enum=["pull", "push", "admin", "maintain", "triage"]),
    current_user: User = Depends(get_current_user)
):
    """Add a collaborator to a repository"""
    github_token = current_user.github_token
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub not connected")
    
    github_client = await get_github_client(github_token)
    return await github_client.add_collaborator(repo_name, username, permission)

@router.delete("/github/repos/{repo_name}/collaborators/{username}")
async def remove_collaborator(
    repo_name: str,
    username: str,
    current_user: User = Depends(get_current_user)
):
    """Remove a collaborator from a repository"""
    github_token = current_user.github_token
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub not connected")
    
    github_client = await get_github_client(github_token)
    return await github_client.remove_collaborator(repo_name, username)

@router.get("/github/repos/{repo_name}/collaborators")
async def list_collaborators(
    repo_name: str,
    current_user: User = Depends(get_current_user)
):
    """List all collaborators of a repository"""
    github_token = current_user.github_token
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub not connected")
    
    github_client = await get_github_client(github_token)
    return await github_client.list_collaborators(repo_name) 