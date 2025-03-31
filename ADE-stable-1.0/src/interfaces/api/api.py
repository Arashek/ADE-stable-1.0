"""API module initialization."""
from typing import Dict, Any, List, Optional
import logging
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.core.orchestrator import Orchestrator
from src.core.models import ModelCapability
from src.interfaces.api.providers import router as providers_router
from src.interfaces.api.tasks import router as tasks_router
from src.interfaces.api.metrics import router as metrics_router
from src.interfaces.api.auth import User, get_current_active_user
from src.interfaces.api.dependencies import get_orchestrator, get_config

logger = logging.getLogger(__name__)

# Pydantic models for API requests and responses
class PlanRequest(BaseModel):
    goal: str = Field(..., description="Goal to create a plan for")

class TaskRequest(BaseModel):
    description: str = Field(..., description="Description of the task")
    task_type: str = Field("develop", description="Type of task (develop, test, analyze)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters for the task")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")

# Create FastAPI application
app = FastAPI(
    title="ADE Platform API",
    description="API for the ADE Platform",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to the ADE API", "version": "0.1.0"}

@app.post("/plans/", response_model=Dict[str, Any], responses={400: {"model": ErrorResponse}})
async def create_plan(
    request: PlanRequest,
    current_user: User = Depends(get_current_active_user),
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Create a plan for a goal"""
    try:
        result = orchestrator.create_plan(request.goal)
        
        if "error" in result:
            return HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        logger.error(f"Failed to create plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create plan: {str(e)}")

@app.post("/tasks/", response_model=Dict[str, Any], responses={400: {"model": ErrorResponse}})
async def execute_task(
    request: TaskRequest,
    current_user: User = Depends(get_current_active_user),
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Execute a task"""
    try:
        result = orchestrator.execute_task(
            task_description=request.description,
            task_type=request.task_type,
            parameters=request.parameters
        )
        
        if "error" in result:
            return HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        logger.error(f"Failed to execute task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute task: {str(e)}")

@app.get("/tasks/", response_model=List[Dict[str, Any]])
async def get_task_history(
    current_user: User = Depends(get_current_active_user),
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Get task history"""
    try:
        return orchestrator.get_task_history()
    except Exception as e:
        logger.error(f"Failed to get task history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get task history: {str(e)}")

@app.get("/tasks/{task_id}", response_model=Dict[str, Any], responses={404: {"model": ErrorResponse}})
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Get a task by ID"""
    try:
        task = orchestrator.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")

# Include routers
app.include_router(providers_router, prefix="/providers", tags=["providers"])
app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])