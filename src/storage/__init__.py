from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class TaskEntity:
    """Entity representing a task in storage"""
    id: str
    description: str
    type: str
    status: str
    error: Optional[str]
    result: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class TaskRepository:
    """Repository for managing task entities"""
    
    def __init__(self):
        self.tasks = {}
    
    def save(self, task: TaskEntity) -> None:
        """Save a task entity"""
        self.tasks[task.id] = task
    
    def get(self, task_id: str) -> Optional[TaskEntity]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    def get_all(self) -> list[TaskEntity]:
        """Get all tasks"""
        return list(self.tasks.values())

__all__ = ['TaskEntity', 'TaskRepository'] 
