"""Data models for the orchestrator module."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
import uuid

from pydantic import BaseModel, Field, ConfigDict


class TaskStatus(str, Enum):
    """Status of a task in the orchestrator"""
    CREATED = "created"
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        """Check if the status is a terminal state."""
        return self in {TaskStatus.SUCCEEDED, TaskStatus.FAILED, TaskStatus.CANCELLED}

    @property
    def is_active(self) -> bool:
        """Check if the status represents an active task."""
        return self in {TaskStatus.PENDING, TaskStatus.RUNNING}


class TaskType(str, Enum):
    """Enumeration of possible task types."""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"
    OPTIMIZATION = "optimization"


class ProviderType(str, Enum):
    """Enumeration of supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class TaskPriority(str, Enum):
    """Enumeration of task priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskContext(BaseModel):
    """Context information for a task."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    project_root: str = Field(..., description="Root directory of the project")
    relevant_files: List[str] = Field(default_factory=list, description="List of relevant file paths")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Project dependencies")
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    constraints: Dict[str, Union[str, int, float]] = Field(
        default_factory=dict,
        description="Task-specific constraints"
    )


class TaskInput(BaseModel):
    """Input parameters for a task."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    task_type: TaskType = Field(..., description="Type of task to execute")
    description: str = Field(..., description="Detailed task description")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    context: TaskContext = Field(..., description="Task context information")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    timeout: Optional[int] = Field(default=None, description="Task timeout in seconds")
    provider_preferences: List[ProviderType] = Field(
        default_factory=list,
        description="Preferred AI providers in order"
    )


class TaskOutput(BaseModel):
    """Output results from a task."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool = Field(..., description="Whether the task completed successfully")
    result: Optional[str] = Field(None, description="Task result or output")
    error: Optional[str] = Field(None, description="Error message if task failed")
    metrics: Dict[str, Union[str, int, float]] = Field(
        default_factory=dict,
        description="Task execution metrics"
    )
    artifacts: List[str] = Field(
        default_factory=list,
        description="Generated artifact file paths"
    )


class PlanStatus(str, Enum):
    """Status of a plan in the orchestrator"""
    CREATED = "created"
    PLANNING = "planning"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        """Check if the status is a terminal state."""
        return self in {PlanStatus.COMPLETED, PlanStatus.FAILED, PlanStatus.CANCELLED}

    @property
    def is_active(self) -> bool:
        """Check if the status represents an active plan."""
        return self in {PlanStatus.PLANNING, PlanStatus.READY, PlanStatus.EXECUTING}


class StepStatus(str, Enum):
    """Status of a step in a plan"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"

    @property
    def is_terminal(self) -> bool:
        """Check if the status is a terminal state."""
        return self in {StepStatus.SUCCEEDED, StepStatus.FAILED, StepStatus.SKIPPED}

    @property
    def is_active(self) -> bool:
        """Check if the status represents an active step."""
        return self in {StepStatus.PENDING, StepStatus.RUNNING}


class PlanStep(BaseModel):
    """A step in an execution plan"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    mitigations: List[str] = Field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def start(self) -> None:
        """Start the step execution."""
        self.status = StepStatus.RUNNING
        self.started_at = datetime.now()

    def complete(self, result: Optional[Dict[str, Any]] = None) -> None:
        """Complete the step successfully."""
        self.status = StepStatus.SUCCEEDED
        self.completed_at = datetime.now()
        if result:
            self.result = result

    def fail(self, error: str) -> None:
        """Mark the step as failed."""
        self.status = StepStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error

    def skip(self) -> None:
        """Skip the step."""
        self.status = StepStatus.SKIPPED
        self.completed_at = datetime.now()

    @property
    def duration(self) -> Optional[float]:
        """Calculate the step duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class Plan(BaseModel):
    """Execution plan for a goal"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str
    steps: List[PlanStep] = Field(default_factory=list)
    status: PlanStatus = PlanStatus.CREATED
    provider: str = "unknown"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_step_index: Optional[int] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_step(self, step: PlanStep) -> None:
        """Add a step to the plan."""
        self.steps.append(step)
        self.updated_at = datetime.now()

    def get_current_step(self) -> Optional[PlanStep]:
        """Get the current step being executed."""
        if self.current_step_index is not None and 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def start(self) -> None:
        """Start the plan execution."""
        self.status = PlanStatus.EXECUTING
        self.started_at = datetime.now()
        self.updated_at = datetime.now()

    def complete(self) -> None:
        """Complete the plan successfully."""
        self.status = PlanStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def fail(self, error: str) -> None:
        """Mark the plan as failed."""
        self.status = PlanStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error
        self.updated_at = datetime.now()

    def cancel(self) -> None:
        """Cancel the plan."""
        self.status = PlanStatus.CANCELLED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    @property
    def duration(self) -> Optional[float]:
        """Calculate the plan duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def progress(self) -> float:
        """Calculate the plan progress as a percentage."""
        if not self.steps:
            return 0.0
        completed_steps = sum(1 for step in self.steps if step.status.is_terminal)
        return (completed_steps / len(self.steps)) * 100


class Task(BaseModel):
    """A task to be executed by the orchestrator"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    plan_id: Optional[str] = None
    step_id: Optional[str] = None
    status: TaskStatus = TaskStatus.CREATED
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    environment_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def start(self) -> None:
        """Start the task execution."""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
        self.updated_at = datetime.now()

    def complete(self, result: Optional[Dict[str, Any]] = None) -> None:
        """Complete the task successfully."""
        self.status = TaskStatus.SUCCEEDED
        self.completed_at = datetime.now()
        self.result = result
        self.updated_at = datetime.now()

    def fail(self, error: str) -> None:
        """Mark the task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error
        self.updated_at = datetime.now()

    def cancel(self) -> None:
        """Cancel the task."""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    @property
    def duration(self) -> Optional[float]:
        """Calculate the task duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class HistoryEntry(BaseModel):
    """An entry in the orchestrator's history"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    entity_type: str  # "plan", "task", "step"
    entity_id: str
    action: str
    details: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_status_change(
        cls,
        entity_type: str,
        entity_id: str,
        old_status: str,
        new_status: str,
        details: Optional[str] = None
    ) -> "HistoryEntry":
        """Create a history entry for a status change."""
        return cls(
            entity_type=entity_type,
            entity_id=entity_id,
            action="status_change",
            details=f"Status changed from {old_status} to {new_status}. {details or ''}",
            metadata={"old_status": old_status, "new_status": new_status}
        )

    @classmethod
    def create_error(
        cls,
        entity_type: str,
        entity_id: str,
        error: str,
        details: Optional[str] = None
    ) -> "HistoryEntry":
        """Create a history entry for an error."""
        return cls(
            entity_type=entity_type,
            entity_id=entity_id,
            action="error",
            details=details or error,
            metadata={"error": error}
        )


class TaskResult(BaseModel):
    """Result model for task execution."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    task_id: str = Field(..., description="Task identifier")
    status: TaskStatus = Field(..., description="Final task status")
    output: TaskOutput = Field(..., description="Task output results")
    execution_time: float = Field(..., description="Total execution time in seconds")
    resource_usage: Dict[str, Union[str, int, float]] = Field(
        default_factory=dict,
        description="Resource usage metrics"
    )
    provider_metrics: Dict[str, Union[str, int, float]] = Field(
        default_factory=dict,
        description="Provider-specific metrics"
    ) 