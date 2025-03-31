from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from ..integrations.github import github_client
from ..models.user import User
from ..auth import get_current_user
from ..utils.events import EventType, event_emitter

router = APIRouter(prefix="/api/github", tags=["github"])

# Request/Response Models
class RepositoryCloneRequest(BaseModel):
    """Request model for cloning a repository."""
    repo_url: str
    local_path: str

class BranchCreateRequest(BaseModel):
    """Request model for creating a branch."""
    branch_name: str
    base_branch: str = "main"

class CommitRequest(BaseModel):
    """Request model for committing changes."""
    branch: str
    files: List[dict]
    message: str

class PullRequestCreateRequest(BaseModel):
    """Request model for creating a pull request."""
    title: str
    body: str
    head_branch: str
    base_branch: str = "main"

class PullRequestUpdateRequest(BaseModel):
    """Request model for updating a pull request."""
    title: Optional[str] = None
    body: Optional[str] = None
    state: Optional[str] = None

# Endpoints
@router.get("/repos", response_model=List[dict])
async def list_repositories(current_user: User = Depends(get_current_user)):
    """List user's GitHub repositories.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of repositories
    """
    try:
        repos = await github_client.get_user_repositories(current_user)
        return [repo.dict() for repo in repos]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching repositories: {str(e)}"
        )

@router.post("/repos/clone", response_model=dict)
async def clone_repository(
    request: RepositoryCloneRequest,
    current_user: User = Depends(get_current_user)
):
    """Clone a GitHub repository.
    
    Args:
        request: Clone request details
        current_user: Current authenticated user
        
    Returns:
        Repository information
    """
    try:
        repo = await github_client.clone_repository(
            request.repo_url,
            request.local_path
        )
        
        # Emit event
        event_emitter.emit(EventType.REPOSITORY_CLONED, {
            "repo_url": request.repo_url,
            "local_path": request.local_path
        })
        
        return repo.dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cloning repository: {str(e)}"
        )

@router.get("/repos/{repo_name}/branches", response_model=List[dict])
async def list_branches(
    repo_name: str,
    current_user: User = Depends(get_current_user)
):
    """List repository branches.
    
    Args:
        repo_name: Repository name
        current_user: Current authenticated user
        
    Returns:
        List of branches
    """
    try:
        branches = await github_client.get_branches(repo_name)
        return branches
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching branches: {str(e)}"
        )

@router.post("/repos/{repo_name}/branches", response_model=dict)
async def create_branch(
    repo_name: str,
    request: BranchCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new branch.
    
    Args:
        repo_name: Repository name
        request: Branch creation details
        current_user: Current authenticated user
        
    Returns:
        Branch information
    """
    try:
        branch = await github_client.create_branch(
            repo_name,
            request.branch_name,
            request.base_branch
        )
        
        # Emit event
        event_emitter.emit(EventType.BRANCH_CREATED, {
            "repo_name": repo_name,
            "branch_name": request.branch_name
        })
        
        return branch
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating branch: {str(e)}"
        )

@router.post("/repos/{repo_name}/commit", response_model=dict)
async def commit_changes(
    repo_name: str,
    request: CommitRequest,
    current_user: User = Depends(get_current_user)
):
    """Commit changes to repository.
    
    Args:
        repo_name: Repository name
        request: Commit details
        current_user: Current authenticated user
        
    Returns:
        Commit information
    """
    try:
        commit = await github_client.commit_changes(
            repo_name,
            request.branch,
            request.files,
            request.message
        )
        
        # Emit event
        event_emitter.emit(EventType.COMMIT_CREATED, {
            "repo_name": repo_name,
            "branch": request.branch,
            "message": request.message
        })
        
        return commit
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error committing changes: {str(e)}"
        )

@router.get("/repos/{repo_name}/pulls", response_model=List[dict])
async def list_pull_requests(
    repo_name: str,
    state: str = "open",
    current_user: User = Depends(get_current_user)
):
    """List repository pull requests.
    
    Args:
        repo_name: Repository name
        state: PR state (open, closed, all)
        current_user: Current authenticated user
        
    Returns:
        List of pull requests
    """
    try:
        prs = await github_client.get_pull_requests(repo_name, state)
        return prs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching pull requests: {str(e)}"
        )

@router.post("/repos/{repo_name}/pulls", response_model=dict)
async def create_pull_request(
    repo_name: str,
    request: PullRequestCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a pull request.
    
    Args:
        repo_name: Repository name
        request: PR creation details
        current_user: Current authenticated user
        
    Returns:
        Pull request information
    """
    try:
        pr = await github_client.create_pull_request(
            repo_name,
            request.title,
            request.body,
            request.head_branch,
            request.base_branch
        )
        return pr
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating pull request: {str(e)}"
        )

@router.patch("/repos/{repo_name}/pulls/{pr_number}", response_model=dict)
async def update_pull_request(
    repo_name: str,
    pr_number: int,
    request: PullRequestUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update a pull request.
    
    Args:
        repo_name: Repository name
        pr_number: PR number
        request: PR update details
        current_user: Current authenticated user
        
    Returns:
        Updated pull request information
    """
    try:
        pr = await github_client.update_pull_request(
            repo_name,
            pr_number,
            request.title,
            request.body,
            request.state
        )
        return pr
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating pull request: {str(e)}"
        ) 