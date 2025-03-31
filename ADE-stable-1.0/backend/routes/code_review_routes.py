from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from ..services.code_review_service import CodeReviewService
from ..models.code_review import ReviewStatus
from ..core.config import settings
from ..core.auth import get_current_user

router = APIRouter(prefix="/api/code-review", tags=["code-review"])

@router.post("/pull-requests")
async def create_pull_request(
    title: str,
    description: str,
    source_branch: str,
    target_branch: str,
    current_user: Dict = Depends(get_current_user)
):
    """Create a new pull request."""
    code_review_service = CodeReviewService(settings.STORAGE_PATH)
    result = code_review_service.create_pull_request(
        title=title,
        description=description,
        source_branch=source_branch,
        target_branch=target_branch,
        author=current_user["username"]
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/pull-requests/{pr_id}/comments")
async def add_review_comment(
    pr_id: str,
    file_path: str,
    line_number: int,
    comment: str,
    current_user: Dict = Depends(get_current_user)
):
    """Add a review comment to a pull request."""
    code_review_service = CodeReviewService(settings.STORAGE_PATH)
    result = code_review_service.add_review_comment(
        pr_id=pr_id,
        file_path=file_path,
        line_number=line_number,
        comment=comment,
        reviewer=current_user["username"]
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.put("/pull-requests/{pr_id}/status")
async def update_pr_status(
    pr_id: str,
    status: ReviewStatus,
    current_user: Dict = Depends(get_current_user)
):
    """Update the status of a pull request."""
    code_review_service = CodeReviewService(settings.STORAGE_PATH)
    result = code_review_service.update_pr_status(pr_id, status)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.get("/pull-requests/{pr_id}")
async def get_pull_request(
    pr_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get a pull request by ID."""
    code_review_service = CodeReviewService(settings.STORAGE_PATH)
    result = code_review_service.get_pull_request(pr_id)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.get("/pull-requests")
async def list_pull_requests(
    status: Optional[ReviewStatus] = None,
    current_user: Dict = Depends(get_current_user)
):
    """List all pull requests, optionally filtered by status."""
    code_review_service = CodeReviewService(settings.STORAGE_PATH)
    result = code_review_service.list_pull_requests(status)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/integrations/{service_type}")
async def integrate_with_external_service(
    service_type: str,
    credentials: Dict,
    current_user: Dict = Depends(get_current_user)
):
    """Integrate with external Git hosting services."""
    code_review_service = CodeReviewService(settings.STORAGE_PATH)
    result = code_review_service.integrate_with_external_service(
        service_type=service_type,
        credentials=credentials
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result 