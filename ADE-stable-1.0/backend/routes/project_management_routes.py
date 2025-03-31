from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel

from ..services.project_management_service import ProjectManagementService
from ..models.project_management import (
    Project, Task, Sprint, TimeEntry, ProjectTemplate,
    TaskStatus, SprintStatus, ProjectStatus, TaskPriority
)
from ..auth.auth import get_current_user

router = APIRouter(prefix="/api/project-management", tags=["project-management"])

# Request/Response Models
class ProjectCreate(BaseModel):
    name: str
    description: str
    template_id: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    settings: Optional[Dict] = None

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    sprint_id: Optional[str] = None
    estimated_hours: float
    due_date: Optional[datetime] = None
    tags: List[str] = []
    dependencies: List[str] = []

class SprintCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    goals: List[str] = []

class TimeEntryCreate(BaseModel):
    task_id: str
    hours: float
    description: str

class ExternalToolIntegration(BaseModel):
    tool_type: str
    credentials: Dict

# Initialize service
project_service = ProjectManagementService(storage_path="data/project-management")

# Project Routes
@router.post("/projects", response_model=Dict)
async def create_project(
    project: ProjectCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Create a new project"""
    result = project_service.create_project(
        name=project.name,
        description=project.description,
        owner=current_user["id"],
        template_id=project.template_id
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result["data"]

@router.get("/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get project by ID"""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    updates: ProjectUpdate,
    current_user: Dict = Depends(get_current_user)
):
    """Update project configuration"""
    result = project_service.update_project(project_id, updates.dict(exclude_unset=True))
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result["data"]

# Task Routes
@router.post("/projects/{project_id}/tasks", response_model=Task)
async def create_task(
    project_id: str,
    task: TaskCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Create a new task in a project"""
    result = project_service.create_task(project_id, task.dict())
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result["data"]

@router.put("/projects/{project_id}/tasks/{task_id}/status", response_model=Task)
async def update_task_status(
    project_id: str,
    task_id: str,
    status: TaskStatus,
    current_user: Dict = Depends(get_current_user)
):
    """Update task status"""
    result = project_service.update_task_status(project_id, task_id, status)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result["data"]

# Sprint Routes
@router.post("/projects/{project_id}/sprints", response_model=Sprint)
async def create_sprint(
    project_id: str,
    sprint: SprintCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Create a new sprint in a project"""
    result = project_service.create_sprint(project_id, sprint.dict())
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result["data"]

@router.get("/projects/{project_id}/sprints/{sprint_id}/tasks", response_model=List[Task])
async def get_sprint_tasks(
    project_id: str,
    sprint_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get all tasks assigned to a sprint"""
    result = project_service.get_sprint_tasks(project_id, sprint_id)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result["data"]

# Time Tracking Routes
@router.post("/projects/{project_id}/tasks/{task_id}/time", response_model=TimeEntry)
async def log_time(
    project_id: str,
    task_id: str,
    time_entry: TimeEntryCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Log time spent on a task"""
    result = project_service.log_time(
        project_id=project_id,
        task_id=task_id,
        user_id=current_user["id"],
        hours=time_entry.hours,
        description=time_entry.description
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result["data"]

# External Tool Integration Routes
@router.post("/projects/{project_id}/integrations", response_model=Dict)
async def integrate_external_tool(
    project_id: str,
    integration: ExternalToolIntegration,
    current_user: Dict = Depends(get_current_user)
):
    """Integrate with external project management tools"""
    result = project_service.integrate_with_external_tool(
        project_id=project_id,
        tool_type=integration.tool_type,
        credentials=integration.credentials
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

# Metrics Routes
@router.get("/projects/{project_id}/metrics", response_model=Dict)
async def get_project_metrics(
    project_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get project metrics and statistics"""
    result = project_service.get_project_metrics(project_id)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result["data"] 