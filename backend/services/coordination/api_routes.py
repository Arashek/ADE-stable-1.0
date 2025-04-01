"""
API Routes for Agent Coordination System

This module implements the API routes for the agent coordination system,
providing endpoints for task creation, status checking, and result retrieval.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from services.coordination.agent_coordinator import AgentCoordinator
from services.coordination.task_manager import TaskManager, TaskStatus, TaskPriority
from services.coordination.collaboration_patterns import CollaborationPattern

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/coordination",
    tags=["coordination"],
    responses={404: {"description": "Not found"}},
)

# Models for request and response
class TaskRequest(BaseModel):
    """Model for task creation request"""
    task_type: str = Field(..., description="Type of task to be performed")
    requirements: Dict[str, Any] = Field(..., description="Task requirements and parameters")
    collaboration_pattern: str = Field(
        default=CollaborationPattern.PARALLEL.value,
        description="Collaboration pattern to use"
    )
    priority: str = Field(
        default=TaskPriority.MEDIUM.value,
        description="Task priority"
    )
    dependencies: List[str] = Field(
        default=[],
        description="List of task IDs that must be completed before this task"
    )

class TaskResponse(BaseModel):
    """Model for task creation response"""
    task_id: str = Field(..., description="ID of the created task")
    status: str = Field(..., description="Current status of the task")
    message: str = Field(..., description="Response message")

class TaskStatusResponse(BaseModel):
    """Model for task status response"""
    task_id: str = Field(..., description="ID of the task")
    status: str = Field(..., description="Current status of the task")
    progress: Optional[float] = Field(None, description="Task progress (0-1)")
    started_at: Optional[str] = Field(None, description="When the task started")
    completed_at: Optional[str] = Field(None, description="When the task completed")
    duration: Optional[float] = Field(None, description="Task duration in seconds")

class TaskResultResponse(BaseModel):
    """Model for task result response"""
    task_id: str = Field(..., description="ID of the task")
    status: str = Field(..., description="Current status of the task")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result")
    errors: List[Dict[str, Any]] = Field(default=[], description="Task errors")

class TaskAnalyticsResponse(BaseModel):
    """Model for task analytics response"""
    total_tasks: int = Field(..., description="Total number of tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    failed_tasks: int = Field(..., description="Number of failed tasks")
    pending_tasks: int = Field(..., description="Number of pending tasks")
    in_progress_tasks: int = Field(..., description="Number of in-progress tasks")
    cancelled_tasks: int = Field(..., description="Number of cancelled tasks")
    average_completion_time: float = Field(..., description="Average task completion time in seconds")
    average_wait_time: float = Field(..., description="Average task wait time in seconds")
    task_type_distribution: Dict[str, int] = Field(..., description="Distribution of task types")

# Dependency for getting coordinator and task manager instances
async def get_coordinator():
    """Get AgentCoordinator instance"""
    return AgentCoordinator()

async def get_task_manager():
    """Get TaskManager instance"""
    return TaskManager()

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_request: TaskRequest,
    background_tasks: BackgroundTasks,
    coordinator: AgentCoordinator = Depends(get_coordinator),
    task_manager: TaskManager = Depends(get_task_manager)
):
    """
    Create a new task for agent coordination.
    
    Args:
        task_request: Task creation request
        background_tasks: FastAPI background tasks
        coordinator: Agent coordinator instance
        task_manager: Task manager instance
        
    Returns:
        Task creation response
    """
    logger.info("Received task creation request for task type: %s", task_request.task_type)
    
    try:
        # Create task in task manager
        task_id = await task_manager.create_task(
            task_request.task_type,
            task_request.requirements,
            task_request.priority,
            task_request.dependencies
        )
        
        # Process task in background
        background_tasks.add_task(
            process_task,
            task_id,
            task_request,
            coordinator,
            task_manager
        )
        
        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING.value,
            message="Task created successfully"
        )
    
    except Exception as e:
        logger.error("Error creating task: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

@router.get("/tasks/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    task_manager: TaskManager = Depends(get_task_manager)
):
    """
    Get the status of a task.
    
    Args:
        task_id: ID of the task to get status for
        task_manager: Task manager instance
        
    Returns:
        Task status response
    """
    logger.info("Received task status request for task ID: %s", task_id)
    
    try:
        # Get task from task manager
        task = await task_manager.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        # Calculate progress if in progress
        progress = None
        if task["status"] == TaskStatus.IN_PROGRESS.value:
            # This is a placeholder - actual progress calculation would depend on the task
            progress = 0.5
        
        return TaskStatusResponse(
            task_id=task_id,
            status=task["status"],
            progress=progress,
            started_at=task["started_at"],
            completed_at=task["completed_at"],
            duration=task["duration"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting task status: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error getting task status: {str(e)}")

@router.get("/tasks/{task_id}/result", response_model=TaskResultResponse)
async def get_task_result(
    task_id: str,
    task_manager: TaskManager = Depends(get_task_manager)
):
    """
    Get the result of a task.
    
    Args:
        task_id: ID of the task to get result for
        task_manager: Task manager instance
        
    Returns:
        Task result response
    """
    logger.info("Received task result request for task ID: %s", task_id)
    
    try:
        # Get task from task manager
        task = await task_manager.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        # Check if task is completed
        if task["status"] != TaskStatus.COMPLETED.value:
            return TaskResultResponse(
                task_id=task_id,
                status=task["status"],
                result=None,
                errors=task["errors"]
            )
        
        return TaskResultResponse(
            task_id=task_id,
            status=task["status"],
            result=task["result"],
            errors=task["errors"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting task result: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error getting task result: {str(e)}")

@router.get("/tasks/analytics", response_model=TaskAnalyticsResponse)
async def get_task_analytics(
    task_manager: TaskManager = Depends(get_task_manager)
):
    """
    Get analytics for tasks.
    
    Args:
        task_manager: Task manager instance
        
    Returns:
        Task analytics response
    """
    logger.info("Received task analytics request")
    
    try:
        # Get analytics from task manager
        analytics = await task_manager.get_task_analytics()
        
        return TaskAnalyticsResponse(**analytics)
    
    except Exception as e:
        logger.error("Error getting task analytics: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error getting task analytics: {str(e)}")

@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    task_manager: TaskManager = Depends(get_task_manager)
):
    """
    Cancel a task.
    
    Args:
        task_id: ID of the task to cancel
        task_manager: Task manager instance
        
    Returns:
        Cancellation response
    """
    logger.info("Received task cancellation request for task ID: %s", task_id)
    
    try:
        # Cancel task in task manager
        success = await task_manager.cancel_task(task_id)
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Could not cancel task {task_id}")
        
        return {"message": f"Task {task_id} cancelled successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error cancelling task: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error cancelling task: {str(e)}")

async def process_task(
    task_id: str,
    task_request: TaskRequest,
    coordinator: AgentCoordinator,
    task_manager: TaskManager
):
    """
    Process a task in the background.
    
    Args:
        task_id: ID of the task to process
        task_request: Task request
        coordinator: Agent coordinator instance
        task_manager: Task manager instance
    """
    logger.info("Processing task %s in background", task_id)
    
    try:
        # Update task status to in progress
        await task_manager.update_task_status(task_id, TaskStatus.IN_PROGRESS.value)
        
        # Process task with coordinator
        result = await coordinator.process_user_request({
            "task_id": task_id,
            "task_type": task_request.task_type,
            "requirements": task_request.requirements,
            "collaboration_pattern": task_request.collaboration_pattern,
            "priority": task_request.priority
        })
        
        # Update task status to completed with result
        await task_manager.update_task_status(task_id, TaskStatus.COMPLETED.value, result)
        
        logger.info("Task %s completed successfully", task_id)
    
    except Exception as e:
        logger.error("Error processing task %s: %s", task_id, str(e))
        
        # Update task status to failed with error
        await task_manager.update_task_status(
            task_id, 
            TaskStatus.FAILED.value, 
            error=str(e)
        )
