from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from ..services.git_service import GitService
from ..core.config import settings
from ..core.auth import get_current_user

router = APIRouter(prefix="/api/git", tags=["git"])

@router.post("/clone")
async def clone_repository(
    url: str,
    branch: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Clone a remote repository."""
    git_service = GitService(settings.GIT_REPO_PATH)
    result = git_service.clone_repository(url, branch)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/commit")
async def commit_changes(
    message: str,
    files: Optional[List[str]] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Commit changes to the repository."""
    git_service = GitService(settings.GIT_REPO_PATH)
    result = git_service.commit_changes(message, files)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/push")
async def push_changes(
    remote: str = "origin",
    branch: str = "main",
    current_user: Dict = Depends(get_current_user)
):
    """Push changes to remote repository."""
    git_service = GitService(settings.GIT_REPO_PATH)
    result = git_service.push_changes(remote, branch)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/pull")
async def pull_changes(
    remote: str = "origin",
    branch: str = "main",
    current_user: Dict = Depends(get_current_user)
):
    """Pull changes from remote repository."""
    git_service = GitService(settings.GIT_REPO_PATH)
    result = git_service.pull_changes(remote, branch)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/branch")
async def create_branch(
    branch_name: str,
    source: str = "main",
    current_user: Dict = Depends(get_current_user)
):
    """Create a new branch."""
    git_service = GitService(settings.GIT_REPO_PATH)
    result = git_service.create_branch(branch_name, source)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/merge")
async def merge_branch(
    source_branch: str,
    target_branch: str = "main",
    current_user: Dict = Depends(get_current_user)
):
    """Merge a branch into target branch."""
    git_service = GitService(settings.GIT_REPO_PATH)
    result = git_service.merge_branch(source_branch, target_branch)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/rebase")
async def rebase_branch(
    source_branch: str,
    target_branch: str = "main",
    current_user: Dict = Depends(get_current_user)
):
    """Rebase a branch onto target branch."""
    git_service = GitService(settings.GIT_REPO_PATH)
    result = git_service.rebase_branch(source_branch, target_branch)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/resolve-conflicts")
async def resolve_conflicts(
    files: List[str],
    current_user: Dict = Depends(get_current_user)
):
    """Mark files as resolved after manual conflict resolution."""
    git_service = GitService(settings.GIT_REPO_PATH)
    result = git_service.resolve_conflicts(files)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.get("/status")
async def get_status(current_user: Dict = Depends(get_current_user)):
    """Get the current status of the repository."""
    git_service = GitService(settings.GIT_REPO_PATH)
    result = git_service.get_status()
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result 