"""Task management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from src.core.orchestrator import Orchestrator
from src.interfaces.api.auth import User, get_current_active_user
from src.interfaces.api.dependencies import get_orchestrator

# Create router
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

# Models
class TaskRequest(BaseModel):
    """Request model for creating a task."""
    description: str = Field(..., description="Description of the task")
    task_type: str = Field("develop", description="Type of task (develop, test, analyze)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters for the task")

class TaskResponse(BaseModel):
    """Response model for task information."""
    task_id: str = Field(..., description="Unique identifier for the task")
    description: str = Field(..., description="Description of the task")
    task_type: str = Field(..., description="Type of task")
    status: str = Field(..., description="Current status of the task")
    created_at: datetime = Field(..., description="When the task was created")
    updated_at: datetime = Field(..., description="When the task was last updated")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")

# Routes
@router.post("/", response_model=TaskResponse)
async def create_task(
    request: TaskRequest,
    current_user: User = Depends(get_current_active_user),
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Create a new task"""
    try:
        task = orchestrator.create_task(
            description=request.description,
            task_type=request.task_type,
            parameters=request.parameters
        )
        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    current_user: User = Depends(get_current_active_user),
    orchestrator: Orchestrator = Depends(get_orchestrator),
    status: Optional[str] = None,
    task_type: Optional[str] = None
):
    """List all tasks"""
    try:
        tasks = orchestrator.list_tasks(status=status, task_type=task_type)
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tasks: {str(e)}"
        )

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Get a task by ID"""
    try:
        task = orchestrator.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task: {str(e)}"
        )

@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Delete a task"""
    try:
        success = orchestrator.delete_task(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        return {"message": f"Task {task_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        ) 