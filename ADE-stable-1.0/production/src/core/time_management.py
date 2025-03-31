from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set
import asyncio
import logging
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    STALLED = "stalled"
    INTERRUPTED = "interrupted"

@dataclass
class TaskMetrics:
    start_time: float
    last_progress_time: float
    checkpoints: List[float] = field(default_factory=list)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    estimated_completion: Optional[float] = None
    actual_completion: Optional[float] = None
    retry_count: int = 0
    stall_count: int = 0

@dataclass
class Task:
    task_id: str
    agent_id: str
    priority: TaskPriority
    dependencies: Set[str] = field(default_factory=set)
    resources: Set[str] = field(default_factory=set)
    timeout: float
    status: TaskStatus = TaskStatus.PENDING
    metrics: TaskMetrics = field(default_factory=lambda: TaskMetrics(
        start_time=time.time(),
        last_progress_time=time.time()
    ))
    content: Dict = field(default_factory=dict)

class TimeManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.resource_locks: Dict[str, str] = {}  # resource -> task_id
        self.agent_heartbeats: Dict[str, float] = {}
        self.task_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.stall_threshold = 300  # 5 minutes
        self.heartbeat_interval = 60  # 1 minute
        self._lock = asyncio.Lock()
        self._resource_locks: Dict[str, asyncio.Lock] = {}
        self._task_locks: Dict[str, asyncio.Lock] = {}

    async def register_task(self, task: Task) -> bool:
        """Register a new task with time and resource management."""
        async with self._lock:
            if task.task_id in self.tasks:
                return False

            # Check for circular dependencies
            if self._has_circular_dependency(task.task_id, task.dependencies):
                logger.warning(f"Circular dependency detected for task {task.task_id}")
                return False

            # Check resource availability
            if not await self._check_resource_availability(task):
                return False

            self.tasks[task.task_id] = task
            self.task_dependencies[task.task_id] = task.dependencies.copy()
            
            # Create locks for the task
            self._task_locks[task.task_id] = asyncio.Lock()
            for resource in task.resources:
                if resource not in self._resource_locks:
                    self._resource_locks[resource] = asyncio.Lock()

            return True

    async def update_task_progress(self, task_id: str, progress: float) -> bool:
        """Update task progress and check for stalls."""
        async with self._task_locks.get(task_id, asyncio.Lock()):
            if task_id not in self.tasks:
                return False

            task = self.tasks[task_id]
            task.metrics.last_progress_time = time.time()
            task.metrics.checkpoints.append(time.time())
            
            # Update estimated completion time
            if progress > 0:
                elapsed = time.time() - task.metrics.start_time
                task.metrics.estimated_completion = time.time() + (elapsed / progress) * (1 - progress)

            # Check for stalls
            if self._is_task_stalled(task):
                await self._handle_stalled_task(task)

            return True

    async def acquire_resources(self, task_id: str) -> bool:
        """Acquire resources for a task with deadlock prevention."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        
        # Sort resources to prevent deadlocks
        sorted_resources = sorted(list(task.resources))
        
        try:
            # Try to acquire all resources in order
            for resource in sorted_resources:
                async with self._resource_locks[resource]:
                    if resource in self.resource_locks:
                        # Resource is already locked by another task
                        return False
                    self.resource_locks[resource] = task_id
            return True
        except Exception as e:
            logger.error(f"Error acquiring resources for task {task_id}: {e}")
            return False

    async def release_resources(self, task_id: str) -> None:
        """Release resources held by a task."""
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]
        for resource in task.resources:
            if resource in self.resource_locks and self.resource_locks[resource] == task_id:
                del self.resource_locks[resource]

    async def update_heartbeat(self, agent_id: str) -> None:
        """Update agent heartbeat to detect stalls."""
        self.agent_heartbeats[agent_id] = time.time()

    async def check_agent_health(self) -> List[str]:
        """Check for stalled or unresponsive agents."""
        current_time = time.time()
        stalled_agents = []
        
        for agent_id, last_heartbeat in self.agent_heartbeats.items():
            if current_time - last_heartbeat > self.heartbeat_interval * 2:
                stalled_agents.append(agent_id)
                logger.warning(f"Agent {agent_id} appears to be stalled")
        
        return stalled_agents

    def _has_circular_dependency(self, task_id: str, dependencies: Set[str]) -> bool:
        """Check for circular dependencies in the task graph."""
        visited = set()
        path = set()

        def dfs(current: str) -> bool:
            if current in path:
                return True
            if current in visited:
                return False

            visited.add(current)
            path.add(current)

            for dep in self.task_dependencies.get(current, set()):
                if dfs(dep):
                    return True

            path.remove(current)
            return False

        return dfs(task_id)

    async def _check_resource_availability(self, task: Task) -> bool:
        """Check if all required resources are available."""
        for resource in task.resources:
            if resource in self.resource_locks:
                return False
        return True

    def _is_task_stalled(self, task: Task) -> bool:
        """Check if a task is stalled based on progress and time."""
        if task.status != TaskStatus.RUNNING:
            return False

        current_time = time.time()
        time_since_progress = current_time - task.metrics.last_progress_time

        # Check for timeout
        if current_time - task.metrics.start_time > task.timeout:
            return True

        # Check for stall based on lack of progress
        if time_since_progress > self.stall_threshold:
            return True

        return False

    async def _handle_stalled_task(self, task: Task) -> None:
        """Handle a stalled task with escalation and retry logic."""
        task.metrics.stall_count += 1
        task.status = TaskStatus.STALLED

        # Release resources
        await self.release_resources(task.task_id)

        # Log stall details
        logger.warning(
            f"Task {task.task_id} stalled. "
            f"Stall count: {task.metrics.stall_count}, "
            f"Time since last progress: {time.time() - task.metrics.last_progress_time}s"
        )

        # Implement retry logic based on stall count
        if task.metrics.stall_count <= 3:
            # Retry with different strategy
            task.status = TaskStatus.PENDING
            task.metrics.retry_count += 1
            task.metrics.last_progress_time = time.time()
        else:
            # Escalate to error state
            task.status = TaskStatus.FAILED
            logger.error(f"Task {task.task_id} failed after {task.metrics.stall_count} stalls")

    async def get_task_metrics(self, task_id: str) -> Optional[Dict]:
        """Get detailed metrics for a task."""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        return {
            "task_id": task.task_id,
            "status": task.status.value,
            "priority": task.priority.value,
            "start_time": task.metrics.start_time,
            "last_progress_time": task.metrics.last_progress_time,
            "estimated_completion": task.metrics.estimated_completion,
            "actual_completion": task.metrics.actual_completion,
            "retry_count": task.metrics.retry_count,
            "stall_count": task.metrics.stall_count,
            "resource_usage": task.metrics.resource_usage,
            "checkpoints": task.metrics.checkpoints
        }

    async def adjust_task_priority(self, task_id: str) -> Optional[TaskPriority]:
        """Dynamically adjust task priority based on time and progress."""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        current_time = time.time()

        # Calculate time pressure
        if task.metrics.estimated_completion:
            time_pressure = (task.metrics.estimated_completion - current_time) / task.timeout
        else:
            time_pressure = 1.0

        # Adjust priority based on time pressure and stall count
        if time_pressure < 0.2 or task.metrics.stall_count > 0:
            return TaskPriority.CRITICAL
        elif time_pressure < 0.5:
            return TaskPriority.HIGH
        elif task.metrics.retry_count > 0:
            return TaskPriority.NORMAL
        else:
            return task.priority 