"""Task repository for document storage."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from src.storage.document.connection import MongoDBConnection

class Task(BaseModel):
    """Task model."""
    id: str = Field(..., description="Task ID")
    description: str = Field(..., description="Task description")
    task_type: str = Field(..., description="Type of task")
    parameters: dict = Field(default_factory=dict, description="Task parameters")
    status: str = Field("pending", description="Task status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

class TaskRepository:
    """Repository for task operations."""
    
    def __init__(self, db_connector: MongoDBConnection):
        """Initialize the task repository.
        
        Args:
            db_connector: MongoDB connection instance
        """
        self.db = db_connector.db
        self.collection = self.db["tasks"]
    
    async def create(self, task: Task) -> Task:
        """Create a new task.
        
        Args:
            task: Task to create
            
        Returns:
            Created task
        """
        result = await self.collection.insert_one(task.dict())
        task.id = str(result.inserted_id)
        return task
    
    async def get(self, task_id: str) -> Optional[Task]:
        """Get a task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task if found, None otherwise
        """
        result = await self.collection.find_one({"id": task_id})
        return Task(**result) if result else None
    
    async def list(self) -> List[Task]:
        """List all tasks.
        
        Returns:
            List of tasks
        """
        cursor = self.collection.find({})
        tasks = await cursor.to_list(length=None)
        return [Task(**task) for task in tasks]
    
    async def update(self, task: Task) -> Optional[Task]:
        """Update a task.
        
        Args:
            task: Task to update
            
        Returns:
            Updated task if found, None otherwise
        """
        result = await self.collection.find_one_and_update(
            {"id": task.id},
            {"$set": task.dict()},
            return_document=True
        )
        return Task(**result) if result else None
    
    async def delete(self, task_id: str) -> bool:
        """Delete a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if deleted, False otherwise
        """
        result = await self.collection.delete_one({"id": task_id})
        return result.deleted_count > 0 