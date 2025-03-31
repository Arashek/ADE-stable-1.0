import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum

from src.core.orchestrator import Orchestrator
from src.project_management.task_scheduler import TaskScheduler
from src.project_management.timeline_tracker import TimelineTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ade-workflow")

class WorkflowStatus(Enum):
    """Status of a workflow execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    name: str
    action: Callable[[], Awaitable[Any]]
    timeout: timedelta
    retries: int = 3
    retry_delay: timedelta = timedelta(seconds=1)
    dependencies: List[str] = None
    validation: Optional[Callable[[Any], Awaitable[bool]]] = None

class WorkflowRunner:
    """Utility for executing and monitoring multi-step workflows"""
    
    def __init__(
        self,
        orchestrator: Orchestrator,
        task_scheduler: TaskScheduler,
        timeline_tracker: TimelineTracker,
        timeout: timedelta = timedelta(minutes=30)
    ):
        """
        Initialize the workflow runner
        
        Args:
            orchestrator: ADE platform orchestrator
            task_scheduler: Task scheduler for workflow steps
            timeline_tracker: Timeline tracker for monitoring
            timeout: Overall workflow timeout
        """
        self.orchestrator = orchestrator
        self.task_scheduler = task_scheduler
        self.timeline_tracker = timeline_tracker
        self.timeout = timeout
        self.steps: Dict[str, WorkflowStep] = {}
        self.results: Dict[str, Any] = {}
        self.status = WorkflowStatus.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def add_step(
        self,
        name: str,
        action: Callable[[], Awaitable[Any]],
        timeout: timedelta,
        retries: int = 3,
        retry_delay: timedelta = timedelta(seconds=1),
        dependencies: List[str] = None,
        validation: Optional[Callable[[Any], Awaitable[bool]]] = None
    ):
        """
        Add a step to the workflow
        
        Args:
            name: Step name
            action: Async function to execute
            timeout: Step timeout
            retries: Number of retry attempts
            retry_delay: Delay between retries
            dependencies: List of step names this step depends on
            validation: Optional validation function
        """
        self.steps[name] = WorkflowStep(
            name=name,
            action=action,
            timeout=timeout,
            retries=retries,
            retry_delay=retry_delay,
            dependencies=dependencies or [],
            validation=validation
        )
    
    async def execute_step(self, step: WorkflowStep) -> Any:
        """
        Execute a single workflow step
        
        Args:
            step: Workflow step to execute
            
        Returns:
            Step execution result
        """
        logger.info(f"Executing step: {step.name}")
        
        for attempt in range(step.retries):
            try:
                # Execute step with timeout
                result = await asyncio.wait_for(
                    step.action(),
                    timeout=step.timeout.total_seconds()
                )
                
                # Validate result if validation function provided
                if step.validation:
                    is_valid = await step.validation(result)
                    if not is_valid:
                        raise ValueError(f"Step {step.name} validation failed")
                
                logger.info(f"Step completed: {step.name}")
                return result
                
            except asyncio.TimeoutError:
                logger.error(f"Step timeout: {step.name}")
                if attempt < step.retries - 1:
                    await asyncio.sleep(step.retry_delay.total_seconds())
                    continue
                raise
            except Exception as e:
                logger.error(f"Step failed: {step.name}, error: {str(e)}")
                if attempt < step.retries - 1:
                    await asyncio.sleep(step.retry_delay.total_seconds())
                    continue
                raise
    
    async def execute(self) -> Dict[str, Any]:
        """
        Execute the complete workflow
        
        Returns:
            Dictionary of step results
        """
        self.status = WorkflowStatus.RUNNING
        self.start_time = datetime.utcnow()
        
        try:
            # Create execution order based on dependencies
            execution_order = self._get_execution_order()
            
            # Execute steps in order
            for step_name in execution_order:
                step = self.steps[step_name]
                
                # Check dependencies
                for dep in step.dependencies:
                    if dep not in self.results:
                        raise ValueError(f"Missing dependency: {dep}")
                
                # Execute step
                result = await self.execute_step(step)
                self.results[step_name] = result
            
            self.status = WorkflowStatus.COMPLETED
            self.end_time = datetime.utcnow()
            return self.results
            
        except Exception as e:
            self.status = WorkflowStatus.FAILED
            self.end_time = datetime.utcnow()
            logger.error(f"Workflow failed: {str(e)}")
            raise
    
    def _get_execution_order(self) -> List[str]:
        """
        Get ordered list of steps based on dependencies
        
        Returns:
            List of step names in execution order
        """
        # Simple topological sort for dependencies
        visited = set()
        order = []
        
        def visit(step_name: str):
            if step_name in visited:
                return
            visited.add(step_name)
            
            step = self.steps[step_name]
            for dep in step.dependencies:
                visit(dep)
            
            order.append(step_name)
        
        for step_name in self.steps:
            visit(step_name)
        
        return order
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get summary of workflow execution
        
        Returns:
            Dictionary containing execution summary
        """
        duration = None
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
        
        return {
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": duration,
            "steps": {
                name: {
                    "status": "completed" if name in self.results else "pending",
                    "result": self.results.get(name)
                }
                for name in self.steps
            }
        }
    
    async def cleanup(self):
        """Clean up resources after workflow execution"""
        # Add cleanup logic here
        pass 