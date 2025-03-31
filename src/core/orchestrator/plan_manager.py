"""Plan manager for orchestrator using provider registry."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from .models import Plan, PlanStep, PlanStatus, StepStatus
from .state_manager import StateManager
from .task_executor import TaskExecutor
from ..providers import ModelRouter, ProviderRegistry, Capability, PlanResponse

logger = logging.getLogger(__name__)

class PlanExecutionError(Exception):
    """Error during plan execution"""
    pass

class PlanManager:
    """Manages plan creation and execution"""
    
    def __init__(self, state_manager: StateManager, model_router: ModelRouter, task_executor: TaskExecutor):
        self.state_manager = state_manager
        self.model_router = model_router
        self.task_executor = task_executor
    
    def create_plan(self, goal: str, user_id: Optional[str] = None) -> Plan:
        """
        Create a plan for a goal
        
        Args:
            goal: The goal to create a plan for
            user_id: The ID of the user creating the plan
            
        Returns:
            Plan: The created plan
        """
        # Create initial plan
        plan = Plan(
            goal=goal,
            status=PlanStatus.PLANNING,
            metadata={"user_id": user_id} if user_id else {}
        )
        
        # Save initial plan state
        self.state_manager.save_plan(plan)
        
        # Create a task to generate the plan
        self.task_executor.submit_task(
            task_id=f"plan_creation_{plan.id}",
            task_func=self._generate_plan,
            task_args={"plan_id": plan.id, "goal": goal},
            on_success=self._on_plan_generation_success,
            on_failure=self._on_plan_generation_failure
        )
        
        return plan
    
    def _generate_plan(self, plan_id: str, goal: str) -> PlanResponse:
        """
        Generate a plan using the model router
        
        Args:
            plan_id: The ID of the plan to generate
            goal: The goal to create a plan for
            
        Returns:
            PlanResponse: The response from the model
        """
        logger.info(f"Generating plan for goal: {goal}")
        response = self.model_router.route_plan_creation(goal)
        
        if not response.success:
            raise PlanExecutionError(f"Failed to generate plan: {response.error}")
        
        return response
    
    def _on_plan_generation_success(self, task_id: str, result: PlanResponse, execution_time: float):
        """
        Handle successful plan generation
        
        Args:
            task_id: The ID of the task
            result: The plan generation result
            execution_time: The time taken to generate the plan
        """
        # Extract plan_id from task_id
        plan_id = task_id.replace("plan_creation_", "")
        
        # Get the plan
        plan = self.state_manager.get_plan(plan_id)
        if not plan:
            logger.error(f"Plan {plan_id} not found")
            return
        
        # Update plan with generated steps
        steps = []
        for step_data in result.plan.get("steps", []):
            step = PlanStep(
                id=step_data.get("id", f"step-{len(steps)+1}"),
                name=step_data.get("name", f"Step {len(steps)+1}"),
                description=step_data.get("description", ""),
                inputs=step_data.get("inputs", []),
                outputs=step_data.get("outputs", []),
                challenges=step_data.get("challenges", []),
                mitigations=step_data.get("mitigations", []),
                status=StepStatus.PENDING
            )
            steps.append(step)
        
        plan.steps = steps
        plan.status = PlanStatus.READY
        plan.provider = result.provider
        plan.updated_at = datetime.now()
        plan.metadata["execution_time"] = execution_time
        
        # Save updated plan
        self.state_manager.save_plan(plan)
        logger.info(f"Plan {plan_id} generated successfully with {len(steps)} steps")
    
    def _on_plan_generation_failure(self, task_id: str, error: str):
        """
        Handle failed plan generation
        
        Args:
            task_id: The ID of the task
            error: The error message
        """
        # Extract plan_id from task_id
        plan_id = task_id.replace("plan_creation_", "")
        
        # Get the plan
        plan = self.state_manager.get_plan(plan_id)
        if not plan:
            logger.error(f"Plan {plan_id} not found")
            return
        
        # Update plan with error
        plan.status = PlanStatus.FAILED
        plan.error = error
        plan.updated_at = datetime.now()
        
        # Save updated plan
        self.state_manager.save_plan(plan)
        logger.error(f"Plan {plan_id} generation failed: {error}")
    
    def execute_plan(self, plan_id: str, user_id: Optional[str] = None) -> Plan:
        """
        Execute a plan
        
        Args:
            plan_id: The ID of the plan to execute
            user_id: The ID of the user executing the plan
            
        Returns:
            Plan: The updated plan
        """
        # Get the plan
        plan = self.state_manager.get_plan(plan_id)
        if not plan:
            raise PlanExecutionError(f"Plan {plan_id} not found")
        
        # Check if plan is ready
        if plan.status != PlanStatus.READY:
            raise PlanExecutionError(f"Plan {plan_id} is not ready for execution (status: {plan.status})")
        
        # Update plan status
        plan.status = PlanStatus.EXECUTING
        plan.started_at = datetime.now()
        plan.current_step_index = 0
        plan.updated_at = datetime.now()
        
        if user_id:
            plan.metadata["executed_by"] = user_id
        
        # Save updated plan
        self.state_manager.save_plan(plan)
        
        # Start executing the first step
        self._execute_next_step(plan_id)
        
        return plan
    
    def _execute_next_step(self, plan_id: str):
        """
        Execute the next step in a plan
        
        Args:
            plan_id: The ID of the plan
        """
        # Get the plan
        plan = self.state_manager.get_plan(plan_id)
        if not plan:
            logger.error(f"Plan {plan_id} not found")
            return
        
        # Check if we've completed all steps
        if plan.current_step_index is None or plan.current_step_index >= len(plan.steps):
            plan.status = PlanStatus.COMPLETED
            plan.completed_at = datetime.now()
            plan.updated_at = datetime.now()
            self.state_manager.save_plan(plan)
            logger.info(f"Plan {plan_id} completed successfully")
            return
        
        # Get the current step
        current_step = plan.steps[plan.current_step_index]
        current_step.status = StepStatus.RUNNING
        current_step.started_at = datetime.now()
        
        # Save updated plan
        self.state_manager.save_plan(plan)
        
        # Execute the step
        self.task_executor.submit_task(
            task_id=f"step_execution_{plan_id}_{current_step.id}",
            task_func=self._execute_step,
            task_args={"plan_id": plan_id, "step_index": plan.current_step_index},
            on_success=self._on_step_execution_success,
            on_failure=self._on_step_execution_failure
        )
    
    def _execute_step(self, plan_id: str, step_index: int) -> Dict[str, Any]:
        """
        Execute a step in a plan
        
        Args:
            plan_id: The ID of the plan
            step_index: The index of the step to execute
            
        Returns:
            Dict: The step execution result
        """
        # Get the plan
        plan = self.state_manager.get_plan(plan_id)
        if not plan:
            raise PlanExecutionError(f"Plan {plan_id} not found")
        
        # Get the step
        if step_index >= len(plan.steps):
            raise PlanExecutionError(f"Step index {step_index} out of range for plan {plan_id}")
        
        step = plan.steps[step_index]
        logger.info(f"Executing step {step.id}: {step.name}")
        
        # This would be where we actually execute the step
        # For demonstration, we'll just return a success result
        
        # In a real implementation, this would use the appropriate providers
        # to execute the specific actions required by the step
        
        return {
            "success": True,
            "message": f"Step {step.id} executed successfully"
        }
    
    def _on_step_execution_success(self, task_id: str, result: Dict[str, Any], execution_time: float):
        """
        Handle successful step execution
        
        Args:
            task_id: The ID of the task
            result: The step execution result
            execution_time: The time taken to execute the step
        """
        # Extract plan_id and step_id from task_id
        _, plan_id, step_id = task_id.split("_", 2)
        
        # Get the plan
        plan = self.state_manager.get_plan(plan_id)
        if not plan:
            logger.error(f"Plan {plan_id} not found")
            return
        
        # Get the current step
        if plan.current_step_index is None or plan.current_step_index >= len(plan.steps):
            logger.error(f"Invalid step index {plan.current_step_index} for plan {plan_id}")
            return
        
        current_step = plan.steps[plan.current_step_index]
        
        # Update step status
        current_step.status = StepStatus.SUCCEEDED
        current_step.completed_at = datetime.now()
        current_step.result = result
        
        # Move to the next step
        plan.current_step_index += 1
        plan.updated_at = datetime.now()
        
        # Save updated plan
        self.state_manager.save_plan(plan)
        
        # Execute the next step
        self._execute_next_step(plan_id)
    
    def _on_step_execution_failure(self, task_id: str, error: str):
        """
        Handle failed step execution
        
        Args:
            task_id: The ID of the task
            error: The error message
        """
        # Extract plan_id and step_id from task_id
        _, plan_id, step_id = task_id.split("_", 2)
        
        # Get the plan
        plan = self.state_manager.get_plan(plan_id)
        if not plan:
            logger.error(f"Plan {plan_id} not found")
            return
        
        # Get the current step
        if plan.current_step_index is None or plan.current_step_index >= len(plan.steps):
            logger.error(f"Invalid step index {plan.current_step_index} for plan {plan_id}")
            return
        
        current_step = plan.steps[plan.current_step_index]
        
        # Update step status
        current_step.status = StepStatus.FAILED
        current_step.completed_at = datetime.now()
        current_step.error = error
        
        # Update plan status
        plan.status = PlanStatus.FAILED
        plan.error = f"Step {current_step.id} failed: {error}"
        plan.updated_at = datetime.now()
        
        # Save updated plan
        self.state_manager.save_plan(plan)
        logger.error(f"Plan {plan_id} failed at step {current_step.id}: {error}")
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """
        Get a plan by ID
        
        Args:
            plan_id: The ID of the plan
            
        Returns:
            Plan: The plan, or None if not found
        """
        return self.state_manager.get_plan(plan_id)
    
    def get_plans(self, status: Optional[PlanStatus] = None, limit: int = 100, skip: int = 0) -> List[Plan]:
        """
        Get plans, optionally filtered by status
        
        Args:
            status: The status to filter by
            limit: The maximum number of plans to return
            skip: The number of plans to skip
            
        Returns:
            List[Plan]: The plans
        """
        return self.state_manager.get_plans(status, limit, skip)
    
    def cancel_plan(self, plan_id: str) -> bool:
        """
        Cancel a plan
        
        Args:
            plan_id: The ID of the plan to cancel
            
        Returns:
            bool: True if the plan was cancelled, False otherwise
        """
        # Get the plan
        plan = self.state_manager.get_plan(plan_id)
        if not plan:
            logger.error(f"Plan {plan_id} not found")
            return False
        
        # Update plan status
        plan.status = PlanStatus.CANCELLED
        plan.updated_at = datetime.now()
        
        # Update current step if there is one
        if plan.current_step_index is not None and plan.current_step_index < len(plan.steps):
            current_step = plan.steps[plan.current_step_index]
            if current_step.status == StepStatus.RUNNING:
                current_step.status = StepStatus.SKIPPED
                current_step.completed_at = datetime.now()
        
        # Save updated plan
        self.state_manager.save_plan(plan)
        logger.info(f"Plan {plan_id} cancelled")
        
        return True

    # Helper methods for common operations
    def get_active_plans(self) -> List[Plan]:
        """Get all active plans (not in terminal state)"""
        return self.state_manager.get_active_plans()
    
    def get_plan_progress(self, plan_id: str) -> float:
        """
        Get the progress of a plan as a percentage
        
        Args:
            plan_id: The ID of the plan
            
        Returns:
            float: The progress percentage (0-100)
        """
        plan = self.get_plan(plan_id)
        if not plan:
            return 0.0
        return plan.progress
    
    def get_plan_duration(self, plan_id: str) -> Optional[float]:
        """
        Get the duration of a plan in seconds
        
        Args:
            plan_id: The ID of the plan
            
        Returns:
            Optional[float]: The duration in seconds, or None if not completed
        """
        plan = self.get_plan(plan_id)
        if not plan:
            return None
        return plan.duration
    
    def get_plan_history(self, plan_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the history of a plan
        
        Args:
            plan_id: The ID of the plan
            limit: The maximum number of history entries to return
            
        Returns:
            List[Dict[str, Any]]: The plan history
        """
        return self.state_manager.get_plan_history(plan_id, limit)
    
    def retry_failed_step(self, plan_id: str, step_id: str) -> bool:
        """
        Retry a failed step in a plan
        
        Args:
            plan_id: The ID of the plan
            step_id: The ID of the step to retry
            
        Returns:
            bool: True if the step was retried, False otherwise
        """
        plan = self.get_plan(plan_id)
        if not plan:
            return False
        
        # Find the step
        step_index = None
        for i, step in enumerate(plan.steps):
            if step.id == step_id:
                step_index = i
                break
        
        if step_index is None:
            return False
        
        # Update step status
        plan.steps[step_index].status = StepStatus.PENDING
        plan.steps[step_index].error = None
        plan.steps[step_index].result = None
        plan.steps[step_index].started_at = None
        plan.steps[step_index].completed_at = None
        
        # Update plan status
        plan.status = PlanStatus.EXECUTING
        plan.current_step_index = step_index
        plan.error = None
        plan.updated_at = datetime.now()
        
        # Save updated plan
        self.state_manager.save_plan(plan)
        
        # Execute the step
        self._execute_next_step(plan_id)
        
        return True 