"""
Task Manager for ADE Platform

This module implements the task management system for the agent coordination in the ADE platform.
It handles task creation, tracking, prioritization, and lifecycle management.
"""

import logging
from typing import Dict, List, Any, Optional
from enum import Enum
import asyncio
import uuid
import time
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Enumeration of task statuses"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """Enumeration of task priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskManager:
    """
    Manages tasks for the agent coordination system.
    
    This class is responsible for:
    1. Creating and tracking tasks
    2. Managing task priorities and dependencies
    3. Scheduling tasks for execution
    4. Monitoring task progress and status
    5. Providing task history and analytics
    """
    
    def __init__(self):
        """Initialize the task manager"""
        # Initialize task storage
        self.tasks = {}
        
        # Initialize task queues by priority
        self.task_queues = {
            TaskPriority.CRITICAL.value: [],
            TaskPriority.HIGH.value: [],
            TaskPriority.MEDIUM.value: [],
            TaskPriority.LOW.value: []
        }
        
        # Initialize task history
        self.task_history = []
        
        # Initialize task analytics
        self.analytics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_completion_time": 0
        }
        
        logger.info("Task Manager initialized")
    
    async def create_task(self, task_type: str, requirements: Dict[str, Any], 
                        priority: str = TaskPriority.MEDIUM.value,
                        dependencies: List[str] = None) -> str:
        """
        Create a new task.
        
        Args:
            task_type: Type of task to be performed
            requirements: Task requirements and parameters
            priority: Task priority
            dependencies: List of task IDs that must be completed before this task
            
        Returns:
            Task ID
        """
        # Generate task ID
        task_id = self._generate_task_id()
        
        # Create task object
        task = {
            "task_id": task_id,
            "task_type": task_type,
            "requirements": requirements,
            "priority": priority,
            "status": TaskStatus.PENDING.value,
            "dependencies": dependencies or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "duration": None,
            "result": None,
            "errors": []
        }
        
        # Store task
        self.tasks[task_id] = task
        
        # Add to appropriate queue
        self.task_queues[priority].append(task_id)
        
        # Update analytics
        self.analytics["total_tasks"] += 1
        
        logger.info("Created task %s of type %s with priority %s", 
                   task_id, task_type, priority)
        
        return task_id
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to get
            
        Returns:
            Task object or None if not found
        """
        return self.tasks.get(task_id)
    
    async def update_task_status(self, task_id: str, status: str, 
                               result: Dict[str, Any] = None,
                               error: str = None) -> bool:
        """
        Update the status of a task.
        
        Args:
            task_id: ID of the task to update
            status: New status
            result: Task result (for completed tasks)
            error: Error message (for failed tasks)
            
        Returns:
            True if update was successful, False otherwise
        """
        if task_id not in self.tasks:
            logger.warning("Attempted to update non-existent task %s", task_id)
            return False
        
        task = self.tasks[task_id]
        old_status = task["status"]
        task["status"] = status
        task["updated_at"] = datetime.now().isoformat()
        
        # Handle status-specific updates
        if status == TaskStatus.IN_PROGRESS.value and old_status == TaskStatus.PENDING.value:
            task["started_at"] = datetime.now().isoformat()
        
        elif status == TaskStatus.COMPLETED.value:
            task["completed_at"] = datetime.now().isoformat()
            if task["started_at"]:
                started = datetime.fromisoformat(task["started_at"])
                completed = datetime.fromisoformat(task["completed_at"])
                task["duration"] = (completed - started).total_seconds()
            
            if result:
                task["result"] = result
            
            # Update analytics
            self.analytics["completed_tasks"] += 1
            if task["duration"]:
                # Update average completion time
                total_completed = self.analytics["completed_tasks"]
                current_avg = self.analytics["average_completion_time"]
                new_avg = ((current_avg * (total_completed - 1)) + task["duration"]) / total_completed
                self.analytics["average_completion_time"] = new_avg
            
            # Add to task history
            self.task_history.append({
                "task_id": task_id,
                "task_type": task["task_type"],
                "priority": task["priority"],
                "created_at": task["created_at"],
                "completed_at": task["completed_at"],
                "duration": task["duration"]
            })
            
            # Check if any tasks depend on this one
            self._check_dependent_tasks(task_id)
        
        elif status == TaskStatus.FAILED.value:
            task["completed_at"] = datetime.now().isoformat()
            if task["started_at"]:
                started = datetime.fromisoformat(task["started_at"])
                completed = datetime.fromisoformat(task["completed_at"])
                task["duration"] = (completed - started).total_seconds()
            
            if error:
                task["errors"].append({
                    "message": error,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Update analytics
            self.analytics["failed_tasks"] += 1
        
        logger.info("Updated task %s status from %s to %s", task_id, old_status, status)
        return True
    
    async def get_next_task(self) -> Optional[Dict[str, Any]]:
        """
        Get the next task to be executed based on priority and dependencies.
        
        Returns:
            Next task or None if no tasks are available
        """
        # Check each priority queue in order
        for priority in [TaskPriority.CRITICAL.value, TaskPriority.HIGH.value, 
                        TaskPriority.MEDIUM.value, TaskPriority.LOW.value]:
            queue = self.task_queues[priority]
            
            # Find the first task that is pending and has all dependencies satisfied
            for i, task_id in enumerate(queue):
                task = self.tasks[task_id]
                
                if task["status"] == TaskStatus.PENDING.value:
                    # Check dependencies
                    dependencies_satisfied = True
                    for dep_id in task["dependencies"]:
                        if dep_id not in self.tasks or self.tasks[dep_id]["status"] != TaskStatus.COMPLETED.value:
                            dependencies_satisfied = False
                            break
                    
                    if dependencies_satisfied:
                        # Remove from queue
                        queue.pop(i)
                        return task
        
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending or in-progress task.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            True if cancellation was successful, False otherwise
        """
        if task_id not in self.tasks:
            logger.warning("Attempted to cancel non-existent task %s", task_id)
            return False
        
        task = self.tasks[task_id]
        
        # Only pending or in-progress tasks can be cancelled
        if task["status"] not in [TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value]:
            logger.warning("Attempted to cancel task %s with status %s", task_id, task["status"])
            return False
        
        # Update task status
        await self.update_task_status(task_id, TaskStatus.CANCELLED.value)
        
        # Remove from queue if pending
        if task["status"] == TaskStatus.PENDING.value:
            queue = self.task_queues[task["priority"]]
            if task_id in queue:
                queue.remove(task_id)
        
        logger.info("Cancelled task %s", task_id)
        return True
    
    async def get_task_status(self, task_id: str) -> Optional[str]:
        """
        Get the status of a task.
        
        Args:
            task_id: ID of the task to get status for
            
        Returns:
            Task status or None if task not found
        """
        if task_id in self.tasks:
            return self.tasks[task_id]["status"]
        return None
    
    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the result of a completed task.
        
        Args:
            task_id: ID of the task to get result for
            
        Returns:
            Task result or None if task not found or not completed
        """
        if task_id in self.tasks and self.tasks[task_id]["status"] == TaskStatus.COMPLETED.value:
            return self.tasks[task_id]["result"]
        return None
    
    async def get_task_analytics(self) -> Dict[str, Any]:
        """
        Get analytics for tasks.
        
        Returns:
            Task analytics
        """
        # Calculate additional analytics
        pending_tasks = sum(1 for task in self.tasks.values() 
                          if task["status"] == TaskStatus.PENDING.value)
        in_progress_tasks = sum(1 for task in self.tasks.values() 
                              if task["status"] == TaskStatus.IN_PROGRESS.value)
        cancelled_tasks = sum(1 for task in self.tasks.values() 
                            if task["status"] == TaskStatus.CANCELLED.value)
        
        # Calculate average wait time
        wait_times = []
        for task in self.tasks.values():
            if task["started_at"]:
                created = datetime.fromisoformat(task["created_at"])
                started = datetime.fromisoformat(task["started_at"])
                wait_times.append((started - created).total_seconds())
        
        avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0
        
        # Calculate task type distribution
        task_types = {}
        for task in self.tasks.values():
            task_type = task["task_type"]
            if task_type in task_types:
                task_types[task_type] += 1
            else:
                task_types[task_type] = 1
        
        # Return enhanced analytics
        return {
            **self.analytics,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "cancelled_tasks": cancelled_tasks,
            "average_wait_time": avg_wait_time,
            "task_type_distribution": task_types,
            "task_history_length": len(self.task_history)
        }
    
    async def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get task execution history.
        
        Args:
            limit: Maximum number of history entries to return
            
        Returns:
            List of task history entries
        """
        return self.task_history[-limit:]
    
    def _check_dependent_tasks(self, completed_task_id: str) -> None:
        """
        Check if any pending tasks depend on a completed task.
        
        Args:
            completed_task_id: ID of the completed task
        """
        for task_id, task in self.tasks.items():
            if (task["status"] == TaskStatus.PENDING.value and 
                completed_task_id in task["dependencies"]):
                
                # Check if all dependencies are now satisfied
                dependencies_satisfied = True
                for dep_id in task["dependencies"]:
                    if dep_id not in self.tasks or self.tasks[dep_id]["status"] != TaskStatus.COMPLETED.value:
                        dependencies_satisfied = False
                        break
                
                if dependencies_satisfied:
                    logger.info("All dependencies satisfied for task %s", task_id)
    
    def _generate_task_id(self) -> str:
        """
        Generate a unique task ID.
        
        Returns:
            Unique task ID
        """
        return f"task_{uuid.uuid4().hex[:8]}"
