"""Main orchestrator for the ADE system."""
import logging
from typing import Dict, List, Any, Optional, Union
import uuid
from datetime import datetime

from .models import Plan, Task, HistoryEntry, PlanStatus, TaskStatus
from .state_manager import StateManager
from .task_executor import TaskExecutor
from .plan_manager import PlanManager
from ..providers import ProviderRegistry, ModelRouter, Capability, ProviderConfig
from ..utils.events import EventType, event_emitter
from ..api.websocket_server import websocket_server

logger = logging.getLogger(__name__)

class OrchestratorError(Exception):
    """Base class for orchestrator errors"""
    pass

class Orchestrator:
    """Main orchestrator for the ADE system"""
    
    def __init__(self, 
                provider_registry: ProviderRegistry, 
                mongodb_uri: str, 
                database_name: str = "ade",
                max_workers: int = 5):
        """
        Initialize the orchestrator
        
        Args:
            provider_registry: The provider registry to use
            mongodb_uri: The MongoDB URI for state persistence
            database_name: The MongoDB database name
            max_workers: The maximum number of worker threads
        """
        self.provider_registry = provider_registry
        
        # Create model router
        self.model_router = ModelRouter(provider_registry)
        
        # Initialize state manager
        self.state_manager = StateManager(mongodb_uri, database_name)
        
        # Initialize task executor
        self.task_executor = TaskExecutor(max_workers=max_workers)
        self.task_executor.start()
        
        # Initialize plan manager
        self.plan_manager = PlanManager(
            state_manager=self.state_manager,
            model_router=self.model_router,
            task_executor=self.task_executor
        )
        
        # Register event handlers
        self._setup_event_handlers()
        
        logger.info("Orchestrator initialized successfully")
    
    def _setup_event_handlers(self):
        """Set up event handlers for broadcasting events."""
        async def broadcast_event(event):
            await websocket_server.broadcast_event(event)
            
        # Register handlers for all event types
        for event_type in EventType:
            event_emitter.on(event_type, broadcast_event)
    
    async def create_plan(self, goal: str, user_id: Optional[str] = None) -> Plan:
        """
        Create a plan for a goal
        
        Args:
            goal: The goal to create a plan for
            user_id: The ID of the user creating the plan
            
        Returns:
            Plan: The created plan
        """
        try:
            plan = self.plan_manager.create_plan(goal, user_id)
            
            # Log the action in history
            self._add_history_entry(
                entity_type="plan",
                entity_id=plan.id,
                action="create",
                details=f"Created plan for goal: {goal}",
                metadata={"user_id": user_id} if user_id else {}
            )
            
            # Emit event
            await event_emitter.emit(
                EventType.PLAN_CREATED,
                {
                    "plan_id": plan.id,
                    "goal": goal,
                    "user_id": user_id,
                    "status": plan.status.value
                }
            )
            
            return plan
        except Exception as e:
            logger.error(f"Error creating plan: {str(e)}")
            raise OrchestratorError(f"Failed to create plan: {str(e)}")
    
    async def execute_plan(self, plan_id: str, user_id: Optional[str] = None) -> Plan:
        """
        Execute a plan
        
        Args:
            plan_id: The ID of the plan to execute
            user_id: The ID of the user executing the plan
            
        Returns:
            Plan: The updated plan
        """
        try:
            plan = self.plan_manager.execute_plan(plan_id, user_id)
            
            # Log the action in history
            self._add_history_entry(
                entity_type="plan",
                entity_id=plan_id,
                action="execute",
                details=f"Started execution of plan: {plan.goal}",
                metadata={"user_id": user_id} if user_id else {}
            )
            
            # Emit event
            await event_emitter.emit(
                EventType.PLAN_STARTED,
                {
                    "plan_id": plan_id,
                    "user_id": user_id,
                    "status": plan.status.value
                }
            )
            
            return plan
        except Exception as e:
            logger.error(f"Error executing plan {plan_id}: {str(e)}")
            raise OrchestratorError(f"Failed to execute plan: {str(e)}")
    
    async def cancel_plan(self, plan_id: str, user_id: Optional[str] = None) -> bool:
        """
        Cancel a plan
        
        Args:
            plan_id: The ID of the plan to cancel
            user_id: The ID of the user cancelling the plan
            
        Returns:
            bool: True if the plan was cancelled, False otherwise
        """
        try:
            result = self.plan_manager.cancel_plan(plan_id)
            
            if result:
                # Log the action in history
                self._add_history_entry(
                    entity_type="plan",
                    entity_id=plan_id,
                    action="cancel",
                    details=f"Cancelled plan",
                    metadata={"user_id": user_id} if user_id else {}
                )
                
                # Emit event
                await event_emitter.emit(
                    EventType.PLAN_CANCELLED,
                    {
                        "plan_id": plan_id,
                        "user_id": user_id
                    }
                )
            
            return result
        except Exception as e:
            logger.error(f"Error cancelling plan {plan_id}: {str(e)}")
            raise OrchestratorError(f"Failed to cancel plan: {str(e)}")
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """
        Get a plan by ID
        
        Args:
            plan_id: The ID of the plan
            
        Returns:
            Plan: The plan, or None if not found
        """
        try:
            return self.plan_manager.get_plan(plan_id)
        except Exception as e:
            logger.error(f"Error getting plan {plan_id}: {str(e)}")
            raise OrchestratorError(f"Failed to get plan: {str(e)}")
    
    def get_plans(self, status: Optional[Union[PlanStatus, str]] = None, 
                limit: int = 100, skip: int = 0) -> List[Plan]:
        """
        Get plans, optionally filtered by status
        
        Args:
            status: The status to filter by (can be enum or string)
            limit: The maximum number of plans to return
            skip: The number of plans to skip
            
        Returns:
            List[Plan]: The plans
        """
        try:
            # Convert string status to enum if needed
            if isinstance(status, str):
                try:
                    status = PlanStatus(status)
                except ValueError:
                    raise OrchestratorError(f"Invalid status: {status}")
            
            return self.plan_manager.get_plans(status, limit, skip)
        except Exception as e:
            if not isinstance(e, OrchestratorError):
                logger.error(f"Error getting plans: {str(e)}")
                raise OrchestratorError(f"Failed to get plans: {str(e)}")
            raise
    
    async def create_task(self, description: str, plan_id: Optional[str] = None, 
                   environment_id: Optional[str] = None, user_id: Optional[str] = None) -> Task:
        """
        Create a task
        
        Args:
            description: The task description
            plan_id: The ID of the plan this task belongs to (optional)
            environment_id: The ID of the environment to use (optional)
            user_id: The ID of the user creating the task
            
        Returns:
            Task: The created task
        """
        try:
            # Create task
            task = Task(
                description=description,
                plan_id=plan_id,
                environment_id=environment_id,
                metadata={"user_id": user_id} if user_id else {}
            )
            
            # Save task
            self.state_manager.save_task(task)
            
            # Log the action in history
            self._add_history_entry(
                entity_type="task",
                entity_id=task.id,
                action="create",
                details=f"Created task: {description}",
                metadata={
                    "user_id": user_id,
                    "plan_id": plan_id
                } if user_id else {"plan_id": plan_id} if plan_id else {}
            )
            
            # Emit event
            await event_emitter.emit(
                EventType.TASK_CREATED,
                {
                    "task_id": task.id,
                    "description": description,
                    "plan_id": plan_id,
                    "user_id": user_id,
                    "status": task.status.value
                }
            )
            
            return task
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise OrchestratorError(f"Failed to create task: {str(e)}")
    
    async def execute_task(self, task_id: str, user_id: Optional[str] = None) -> Task:
        """
        Execute a task
        
        Args:
            task_id: The ID of the task to execute
            user_id: The ID of the user executing the task
            
        Returns:
            Task: The updated task
        """
        try:
            # Get the task
            task = self.state_manager.get_task(task_id)
            if not task:
                raise OrchestratorError(f"Task {task_id} not found")
            
            # Update task status
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            task.updated_at = datetime.now()
            
            if user_id:
                task.metadata["executed_by"] = user_id
            
            # Save updated task
            self.state_manager.save_task(task)
            
            # Log the action in history
            self._add_history_entry(
                entity_type="task",
                entity_id=task_id,
                action="execute",
                details=f"Started execution of task: {task.description}",
                metadata={"user_id": user_id} if user_id else {}
            )
            
            # Emit event
            await event_emitter.emit(
                EventType.TASK_STARTED,
                {
                    "task_id": task_id,
                    "user_id": user_id,
                    "status": task.status.value
                }
            )
            
            # In a real implementation, we would execute the task here
            # For now, we'll just update it to succeeded
            task.status = TaskStatus.SUCCEEDED
            task.completed_at = datetime.now()
            task.updated_at = datetime.now()
            task.result = {"message": "Task executed successfully"}
            
            # Save updated task
            self.state_manager.save_task(task)
            
            # Emit completion event
            await event_emitter.emit(
                EventType.TASK_COMPLETED,
                {
                    "task_id": task_id,
                    "user_id": user_id,
                    "status": task.status.value,
                    "result": task.result
                }
            )
            
            return task
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            raise OrchestratorError(f"Failed to execute task: {str(e)}")
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID
        
        Args:
            task_id: The ID of the task
            
        Returns:
            Task: The task, or None if not found
        """
        try:
            return self.state_manager.get_task(task_id)
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {str(e)}")
            raise OrchestratorError(f"Failed to get task: {str(e)}")
    
    def get_tasks(self, plan_id: Optional[str] = None, 
                status: Optional[Union[TaskStatus, str]] = None,
                limit: int = 100, skip: int = 0) -> List[Task]:
        """
        Get tasks, optionally filtered by plan_id and status
        
        Args:
            plan_id: The ID of the plan to filter by
            status: The status to filter by (can be enum or string)
            limit: The maximum number of tasks to return
            skip: The number of tasks to skip
            
        Returns:
            List[Task]: The tasks
        """
        try:
            # Convert string status to enum if needed
            if isinstance(status, str):
                try:
                    status = TaskStatus(status)
                except ValueError:
                    raise OrchestratorError(f"Invalid status: {status}")
            
            return self.state_manager.get_tasks(plan_id, status, limit, skip)
        except Exception as e:
            if not isinstance(e, OrchestratorError):
                logger.error(f"Error getting tasks: {str(e)}")
                raise OrchestratorError(f"Failed to get tasks: {str(e)}")
            raise
    
    def get_history(self, entity_type: Optional[str] = None, 
                  entity_id: Optional[str] = None,
                  limit: int = 100, skip: int = 0) -> List[HistoryEntry]:
        """
        Get history entries, optionally filtered by entity_type and entity_id
        
        Args:
            entity_type: The type of entity to filter by
            entity_id: The ID of the entity to filter by
            limit: The maximum number of entries to return
            skip: The number of entries to skip
            
        Returns:
            List[HistoryEntry]: The history entries
        """
        try:
            return self.state_manager.get_history(entity_type, entity_id, limit, skip)
        except Exception as e:
            logger.error(f"Error getting history: {str(e)}")
            raise OrchestratorError(f"Failed to get history: {str(e)}")
    
    def _add_history_entry(self, entity_type: str, entity_id: str, 
                         action: str, details: Optional[str] = None,
                         metadata: Dict[str, Any] = None) -> bool:
        """
        Add a history entry
        
        Args:
            entity_type: The type of entity (plan, task, step)
            entity_id: The ID of the entity
            action: The action performed
            details: Additional details
            metadata: Additional metadata
            
        Returns:
            bool: True if the entry was added, False otherwise
        """
        try:
            entry = HistoryEntry(
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                details=details,
                metadata=metadata or {}
            )
            
            return self.state_manager.add_history_entry(entry)
        except Exception as e:
            logger.error(f"Error adding history entry: {str(e)}")
            return False
    
    def shutdown(self):
        """Shutdown the orchestrator"""
        try:
            # Stop task executor
            self.task_executor.stop()
            
            # Close state manager
            self.state_manager.close()
            
            # Remove event handlers
            event_emitter.remove_all_listeners()
            
            logger.info("Orchestrator shutdown complete")
        except Exception as e:
            logger.error(f"Error during orchestrator shutdown: {str(e)}")

    # Helper methods for common operations
    def get_active_plans(self) -> List[Plan]:
        """Get all active plans (not in terminal state)"""
        return self.plan_manager.get_active_plans()
    
    def get_plan_progress(self, plan_id: str) -> float:
        """
        Get the progress of a plan as a percentage
        
        Args:
            plan_id: The ID of the plan
            
        Returns:
            float: The progress percentage (0-100)
        """
        return self.plan_manager.get_plan_progress(plan_id)
    
    def get_plan_duration(self, plan_id: str) -> Optional[float]:
        """
        Get the duration of a plan in seconds
        
        Args:
            plan_id: The ID of the plan
            
        Returns:
            Optional[float]: The duration in seconds, or None if not completed
        """
        return self.plan_manager.get_plan_duration(plan_id)
    
    def get_plan_history(self, plan_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the history of a plan
        
        Args:
            plan_id: The ID of the plan
            limit: The maximum number of history entries to return
            
        Returns:
            List[Dict[str, Any]]: The plan history
        """
        return self.plan_manager.get_plan_history(plan_id, limit)
    
    def retry_failed_step(self, plan_id: str, step_id: str) -> bool:
        """
        Retry a failed step in a plan
        
        Args:
            plan_id: The ID of the plan
            step_id: The ID of the step to retry
            
        Returns:
            bool: True if the step was retried, False otherwise
        """
        return self.plan_manager.retry_failed_step(plan_id, step_id)
    
    def get_active_tasks(self, plan_id: Optional[str] = None) -> List[Task]:
        """
        Get all active tasks (not in terminal state)
        
        Args:
            plan_id: Optional plan ID to filter by
            
        Returns:
            List[Task]: The active tasks
        """
        return self.state_manager.get_active_tasks(plan_id)
    
    def get_task_duration(self, task_id: str) -> Optional[float]:
        """
        Get the duration of a task in seconds
        
        Args:
            task_id: The ID of the task
            
        Returns:
            Optional[float]: The duration in seconds, or None if not completed
        """
        task = self.get_task(task_id)
        if not task:
            return None
        return task.duration
    
    def get_task_history(self, task_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the history of a task
        
        Args:
            task_id: The ID of the task
            limit: The maximum number of history entries to return
            
        Returns:
            List[Dict[str, Any]]: The task history
        """
        return self.state_manager.get_task_history(task_id, limit)
    
    def get_plan_tasks(self, plan_id: str) -> List[Task]:
        """
        Get all tasks associated with a plan
        
        Args:
            plan_id: The ID of the plan
            
        Returns:
            List[Task]: The tasks
        """
        return self.state_manager.get_plan_tasks(plan_id)