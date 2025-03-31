from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class PlanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PlanType(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"

class PlanCreate(BaseModel):
    name: str = Field(..., description="Name of the plan")
    description: Optional[str] = Field(None, description="Description of the plan")
    type: PlanType = Field(..., description="Type of the plan")
    steps: List[Dict[str, Any]] = Field(..., description="List of steps in the plan")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Plan parameters")
    timeout: Optional[int] = Field(default=3600, description="Plan timeout in seconds")
    retry_count: Optional[int] = Field(default=3, description="Number of retry attempts")
    retry_delay: Optional[int] = Field(default=60, description="Delay between retries in seconds")

class PlanUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the plan")
    description: Optional[str] = Field(None, description="Description of the plan")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Plan parameters")
    timeout: Optional[int] = Field(None, description="Plan timeout in seconds")
    retry_count: Optional[int] = Field(None, description="Number of retry attempts")
    retry_delay: Optional[int] = Field(None, description="Delay between retries in seconds")

class PlanResponse(BaseModel):
    id: str = Field(..., description="Unique identifier of the plan")
    name: str = Field(..., description="Name of the plan")
    description: Optional[str] = Field(None, description="Description of the plan")
    type: PlanType = Field(..., description="Type of the plan")
    status: PlanStatus = Field(..., description="Current status of the plan")
    steps: List[Dict[str, Any]] = Field(..., description="List of steps in the plan")
    parameters: Dict[str, Any] = Field(default={}, description="Plan parameters")
    timeout: int = Field(..., description="Plan timeout in seconds")
    retry_count: int = Field(..., description="Number of retry attempts")
    retry_delay: int = Field(..., description="Delay between retries in seconds")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    started_at: Optional[datetime] = Field(None, description="Execution start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error: Optional[str] = Field(None, description="Error message if plan failed")
    progress: float = Field(default=0.0, description="Execution progress (0-100)")
    current_step: Optional[int] = Field(None, description="Current step index")
    step_results: Optional[List[Dict[str, Any]]] = Field(None, description="Results of completed steps")

class PlanListResponse(BaseModel):
    plans: List[PlanResponse] = Field(..., description="List of plans")
    total: int = Field(..., description="Total number of plans")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")

class PlanFilter(BaseModel):
    status: Optional[PlanStatus] = Field(None, description="Filter by plan status")
    type: Optional[PlanType] = Field(None, description="Filter by plan type")
    created_after: Optional[datetime] = Field(None, description="Filter plans created after this timestamp")
    created_before: Optional[datetime] = Field(None, description="Filter plans created before this timestamp")
    search: Optional[str] = Field(None, description="Search in plan name and description")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details") 