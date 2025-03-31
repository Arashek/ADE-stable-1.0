from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
from ..storage.project_store import ProjectStore

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Task:
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee_id: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    dependencies: List[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class Milestone:
    id: str
    title: str
    description: str
    due_date: datetime
    status: str
    tasks: List[str]
    created_at: datetime
    updated_at: datetime

class ProjectState:
    def __init__(self, project_store: ProjectStore):
        self.project_store = project_store
        self._tasks: Dict[str, Task] = {}
        self._milestones: Dict[str, Milestone] = {}
        self._dependencies: Dict[str, List[str]] = {}
        self._resource_allocations: Dict[str, Dict[str, Any]] = {}

    async def initialize(self):
        """Initialize the project state from storage."""
        tasks = await self.project_store.get_all_tasks()
        milestones = await self.project_store.get_all_milestones()
        dependencies = await self.project_store.get_all_dependencies()
        resources = await self.project_store.get_resource_allocations()

        self._tasks = {task.id: task for task in tasks}
        self._milestones = {milestone.id: milestone for milestone in milestones}
        self._dependencies = dependencies
        self._resource_allocations = resources

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        if task_id not in self._tasks:
            task = await self.project_store.get_task(task_id)
            if task:
                self._tasks[task_id] = task
        return self._tasks.get(task_id)

    async def get_milestone(self, milestone_id: str) -> Optional[Milestone]:
        """Get a milestone by ID."""
        if milestone_id not in self._milestones:
            milestone = await self.project_store.get_milestone(milestone_id)
            if milestone:
                self._milestones[milestone_id] = milestone
        return self._milestones.get(milestone_id)

    async def update_task_status(self, task_id: str, new_status: TaskStatus) -> bool:
        """Update a task's status and handle related state changes."""
        task = await self.get_task(task_id)
        if not task:
            return False

        old_status = task.status
        task.status = new_status
        task.updated_at = datetime.now()

        # Update storage
        await self.project_store.update_task(task)

        # Handle status transition effects
        await self._handle_status_transition(task_id, old_status, new_status)

        return True

    async def update_task_priority(self, task_id: str, new_priority: TaskPriority) -> bool:
        """Update a task's priority."""
        task = await self.get_task(task_id)
        if not task:
            return False

        task.priority = new_priority
        task.updated_at = datetime.now()

        # Update storage
        await self.project_store.update_task(task)

        return True

    async def assign_task(self, task_id: str, assignee_id: str) -> bool:
        """Assign a task to a team member."""
        task = await self.get_task(task_id)
        if not task:
            return False

        task.assignee_id = assignee_id
        task.updated_at = datetime.now()

        # Update storage
        await self.project_store.update_task(task)

        return True

    async def add_task_dependency(self, task_id: str, dependency_id: str) -> bool:
        """Add a dependency between tasks."""
        if task_id not in self._dependencies:
            self._dependencies[task_id] = []

        if dependency_id not in self._dependencies[task_id]:
            self._dependencies[task_id].append(dependency_id)
            await self.project_store.add_dependency(task_id, dependency_id)

        return True

    async def remove_task_dependency(self, task_id: str, dependency_id: str) -> bool:
        """Remove a dependency between tasks."""
        if task_id in self._dependencies and dependency_id in self._dependencies[task_id]:
            self._dependencies[task_id].remove(dependency_id)
            await self.project_store.remove_dependency(task_id, dependency_id)

        return True

    async def update_milestone_status(self, milestone_id: str, new_status: str) -> bool:
        """Update a milestone's status."""
        milestone = await self.get_milestone(milestone_id)
        if not milestone:
            return False

        milestone.status = new_status
        milestone.updated_at = datetime.now()

        # Update storage
        await self.project_store.update_milestone(milestone)

        return True

    async def allocate_resource(self, resource_id: str, task_id: str, hours: float) -> bool:
        """Allocate resource hours to a task."""
        if resource_id not in self._resource_allocations:
            self._resource_allocations[resource_id] = {}

        self._resource_allocations[resource_id][task_id] = hours
        await self.project_store.update_resource_allocation(resource_id, task_id, hours)

        return True

    async def update_task_progress(self, task_id: str, hours_worked: float) -> bool:
        """Update task progress with actual hours worked."""
        task = await self.get_task(task_id)
        if not task:
            return False

        task.actual_hours = (task.actual_hours or 0) + hours_worked
        task.updated_at = datetime.now()

        # Update storage
        await self.project_store.update_task(task)

        return True

    async def get_blocked_tasks(self) -> List[Task]:
        """Get all blocked tasks."""
        return [task for task in self._tasks.values() if task.status == TaskStatus.BLOCKED]

    async def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        now = datetime.now()
        return [
            task for task in self._tasks.values()
            if task.end_date and task.end_date < now and task.status != TaskStatus.COMPLETED
        ]

    async def get_critical_path(self) -> List[str]:
        """Calculate the critical path of tasks."""
        # Implementation of critical path calculation
        # This is a simplified version - in practice, you'd want a more sophisticated algorithm
        critical_path = []
        for task_id, task in self._tasks.items():
            if task.status != TaskStatus.COMPLETED:
                dependencies = self._dependencies.get(task_id, [])
                if not dependencies:
                    critical_path.append(task_id)
                else:
                    all_deps_completed = all(
                        self._tasks[dep_id].status == TaskStatus.COMPLETED
                        for dep_id in dependencies
                    )
                    if all_deps_completed:
                        critical_path.append(task_id)
        return critical_path

    async def get_resource_utilization(self, resource_id: str) -> float:
        """Calculate resource utilization rate."""
        if resource_id not in self._resource_allocations:
            return 0.0

        total_allocated = sum(self._resource_allocations[resource_id].values())
        total_available = 40.0  # Assuming 40 hours per week
        return min(1.0, total_allocated / total_available)

    async def _handle_status_transition(self, task_id: str, old_status: TaskStatus, new_status: TaskStatus):
        """Handle effects of task status transitions."""
        # Update dependent tasks if this task is blocked
        if new_status == TaskStatus.BLOCKED:
            for dep_task_id, deps in self._dependencies.items():
                if task_id in deps:
                    dep_task = await self.get_task(dep_task_id)
                    if dep_task and dep_task.status != TaskStatus.BLOCKED:
                        await self.update_task_status(dep_task_id, TaskStatus.BLOCKED)

        # Check if blocking tasks are resolved
        elif old_status == TaskStatus.BLOCKED and new_status != TaskStatus.BLOCKED:
            for dep_task_id, deps in self._dependencies.items():
                if task_id in deps:
                    dep_task = await self.get_task(dep_task_id)
                    if dep_task and dep_task.status == TaskStatus.BLOCKED:
                        # Check if all other dependencies are resolved
                        other_deps = [d for d in deps if d != task_id]
                        all_other_deps_resolved = all(
                            self._tasks[dep_id].status != TaskStatus.BLOCKED
                            for dep_id in other_deps
                        )
                        if all_other_deps_resolved:
                            await self.update_task_status(dep_task_id, TaskStatus.TODO)

        # Update milestone status if task is completed
        if new_status == TaskStatus.COMPLETED:
            for milestone in self._milestones.values():
                if task_id in milestone.tasks:
                    all_tasks_completed = all(
                        self._tasks[task_id].status == TaskStatus.COMPLETED
                        for task_id in milestone.tasks
                    )
                    if all_tasks_completed:
                        await self.update_milestone_status(milestone.id, "completed") 