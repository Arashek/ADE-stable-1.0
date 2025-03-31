from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"

class SprintStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(BaseModel):
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    sprint_id: Optional[str] = None
    estimated_hours: float
    actual_hours: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    tags: List[str] = []
    dependencies: List[str] = []
    attachments: List[str] = []
    comments: List[Dict[str, Any]] = []
    time_entries: List[Dict[str, Any]] = []

class Sprint(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: SprintStatus = SprintStatus.PLANNED
    start_date: datetime
    end_date: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    goals: List[str] = []
    tasks: List[str] = []  # List of task IDs
    velocity: float = 0.0
    story_points: float = 0.0
    completed_points: float = 0.0

class Project(BaseModel):
    id: str
    name: str
    description: str
    owner: str
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Project management
    tasks: List[Task] = []
    sprints: List[Sprint] = []
    members: List[str] = []
    tags: List[str] = []
    
    # Project configuration
    settings: Dict[str, Any] = Field(default_factory=dict)
    external_tool_integrations: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Development environment
    repository: Optional[Dict[str, Any]] = None
    container_config: Optional[Dict[str, Any]] = None
    build_config: Optional[Dict[str, Any]] = None
    deployment_config: Optional[Dict[str, Any]] = None
    
    # Resource management
    resource_allocations: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    
    # Project metrics
    total_tasks: int = 0
    completed_tasks: int = 0
    total_sprints: int = 0
    completed_sprints: int = 0
    total_story_points: float = 0.0
    completed_story_points: float = 0.0
    average_velocity: float = 0.0
    
    def update_metrics(self):
        """Update project metrics based on current state"""
        self.total_tasks = len(self.tasks)
        self.completed_tasks = len([t for t in self.tasks if t.status == TaskStatus.DONE])
        self.total_sprints = len(self.sprints)
        self.completed_sprints = len([s for s in self.sprints if s.status == SprintStatus.COMPLETED])
        
        # Calculate story points and velocity
        total_points = sum(t.estimated_hours for t in self.tasks)
        completed_points = sum(t.actual_hours for t in self.tasks if t.status == TaskStatus.DONE)
        
        self.total_story_points = total_points
        self.completed_story_points = completed_points
        
        # Calculate average velocity
        completed_sprints = [s for s in self.sprints if s.status == SprintStatus.COMPLETED]
        if completed_sprints:
            self.average_velocity = sum(s.completed_points for s in completed_sprints) / len(completed_sprints)
        else:
            self.average_velocity = 0.0
            
        self.updated_at = datetime.now()

class TimeEntry(BaseModel):
    id: str
    task_id: str
    user_id: str
    hours: float
    description: str
    date: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ProjectTemplate(BaseModel):
    id: str
    name: str
    description: str
    structure: Dict[str, str]  # Maps source paths to target paths
    dependencies: Dict[str, Dict[str, str]]  # Maps language to package versions
    setup_scripts: List[str]  # List of setup script paths
    default_settings: Dict[str, Any] = Field(default_factory=dict)
    default_container_config: Dict[str, Any] = Field(default_factory=dict)
    default_build_config: Dict[str, Any] = Field(default_factory=dict)
    default_deployment_config: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now) 