from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    """Status of a task in the ADE platform"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    """Priority level for a task"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskType(str, Enum):
    """Type of task in the multi-agent system"""
    ARCHITECTURE_DESIGN = "architecture_design"
    CODE_GENERATION = "code_generation"
    TEST_WRITING = "test_writing"
    CODE_REVIEW = "code_review"
    DEPLOYMENT = "deployment"
    GENERAL = "general"

class Task(BaseModel):
    """Task model for the ADE platform"""
    id: str = Field(..., description="Unique task identifier")
    project_id: str = Field(..., description="ID of the project this task belongs to")
    
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Detailed task description")
    
    type: TaskType = Field(default=TaskType.GENERAL, description="Type of task")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    
    assigned_agent_id: Optional[str] = Field(None, description="ID of the agent assigned to this task")
    assigned_user_id: Optional[str] = Field(None, description="ID of the user assigned to this task")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Task creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    due_date: Optional[datetime] = Field(None, description="When the task should be completed")
    
    parent_task_id: Optional[str] = Field(None, description="ID of the parent task if this is a subtask")
    subtask_ids: List[str] = Field(default=[], description="IDs of subtasks")
    
    dependencies: List[str] = Field(default=[], description="IDs of tasks this task depends on")
    
    progress: float = Field(default=0.0, description="Task completion percentage (0-100)")
    metadata: Dict[str, Any] = Field(default={}, description="Additional task metadata")
    
    class Config:
        use_enum_values = True
