from typing import Dict, Any, Optional, List, Callable
import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class Task:
    id: str
    name: str
    func: Callable
    args: tuple
    kwargs: dict
    max_retries: int
    retry_delay: float
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0

class TaskQueueManager:
    """Manages task execution with error handling and retries"""
    
    def __init__(
        self,
        max_concurrent_tasks: int = 10,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.tasks: Dict[str, Task] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self._running = False
    
    async def start(self) -> None:
        """Start the task queue manager"""
        if self._running:
            return
            
        self._running = True
        logger.info("Task queue manager started")
    
    async def stop(self) -> None:
        """Stop the task queue manager"""
        self._running = False
        # Wait for running tasks to complete
        running_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]
        if running_tasks:
            await asyncio.gather(*[self._wait_for_task(t) for t in running_tasks])
        logger.info("Task queue manager stopped")
    
    async def submit_task(
        self,
        name: str,
        func: Callable,
        *args,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        **kwargs
    ) -> str:
        """Submit a new task to the queue"""
        task_id = f"{name}_{datetime.now().timestamp()}"
        
        task = Task(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            max_retries=max_retries or self.max_retries,
            retry_delay=retry_delay or self.retry_delay,
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )
        
        self.tasks[task_id] = task
        asyncio.create_task(self._process_task(task))
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task"""
        task = self.tasks.get(task_id)
        if not task:
            return None
            
        return {
            "id": task.id,
            "name": task.name,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error": task.error,
            "retry_count": task.retry_count
        }
    
    async def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List tasks with optional status filter"""
        tasks = self.tasks.values()
        if status:
            tasks = [t for t in tasks if t.status == status]
            
        return [
            await self.get_task_status(t.id)
            for t in sorted(tasks, key=lambda x: x.created_at, reverse=True)[:limit]
        ]
    
    async def _process_task(self, task: Task) -> None:
        """Process a task with retry logic"""
        while task.retry_count <= task.max_retries:
            try:
                async with self._semaphore:
                    task.status = TaskStatus.RUNNING
                    task.started_at = datetime.now()
                    
                    result = await self._execute_task(task)
                    
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now()
                    logger.info(f"Task {task.id} completed successfully")
                    return
                    
            except Exception as e:
                task.error = str(e)
                task.retry_count += 1
                
                if task.retry_count > task.max_retries:
                    task.status = TaskStatus.FAILED
                    task.completed_at = datetime.now()
                    logger.error(f"Task {task.id} failed after {task.max_retries} retries: {str(e)}")
                    return
                    
                task.status = TaskStatus.RETRYING
                logger.warning(f"Task {task.id} failed, retrying ({task.retry_count}/{task.max_retries})")
                await asyncio.sleep(task.retry_delay)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def _execute_task(self, task: Task) -> Any:
        """Execute a task with error handling"""
        try:
            return await task.func(*task.args, **task.kwargs)
        except Exception as e:
            logger.error(f"Error executing task {task.id}: {str(e)}")
            raise
    
    async def _wait_for_task(self, task: Task) -> None:
        """Wait for a task to complete"""
        while task.status in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.RETRYING]:
            await asyncio.sleep(0.1)
    
    async def health_check(self) -> Dict[str, Any]:
        """Get task queue health status"""
        return {
            "status": "healthy",
            "running": self._running,
            "total_tasks": len(self.tasks),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            "running_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]),
            "failed_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED]),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        } 