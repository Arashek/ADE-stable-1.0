from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
from .model_router import ModelRouter
from datetime import datetime, timedelta

class TaskStep(BaseModel):
    """A single step in a task plan"""
    id: str
    description: str
    dependencies: List[str]
    estimated_duration: float
    required_resources: List[str]
    priority: int
    status: str = "pending"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    actual_duration: Optional[float] = None
    cost: Optional[float] = None
    metadata: Dict[str, Any] = {}

class Resource(BaseModel):
    """A resource required for task execution"""
    name: str
    type: str
    capacity: float
    cost_per_unit: float
    availability: List[Tuple[datetime, datetime]]
    current_usage: float = 0.0
    metadata: Dict[str, Any] = {}

class TaskPlan(BaseModel):
    """A complete plan for executing a task"""
    task_id: str
    description: str
    steps: List[TaskStep]
    resources: List[Resource]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "pending"
    total_cost: Optional[float] = None
    metadata: Dict[str, Any] = {}

class PlanningModel:
    """Specialized model for task planning and resource allocation"""
    
    def __init__(self, model_router: ModelRouter):
        self.model_router = model_router
        self.resources: Dict[str, Resource] = {}
        self.plans: Dict[str, TaskPlan] = {}
        self.planning_metrics: Dict[str, Dict[str, float]] = {}
        
    def register_resource(self, resource: Resource):
        """Register a new resource"""
        self.resources[resource.name] = resource
        
    async def create_plan(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> TaskPlan:
        """Create a detailed plan for executing a task"""
        # Generate task steps using the model
        steps = await self._generate_task_steps(task_description, context)
        
        # Allocate resources to steps
        allocated_resources = await self._allocate_resources(steps)
        
        # Create task plan
        plan = TaskPlan(
            task_id=f"task_{len(self.plans) + 1}",
            description=task_description,
            steps=steps,
            resources=allocated_resources,
            metadata={"created_at": datetime.now().isoformat()}
        )
        
        # Store plan
        self.plans[plan.task_id] = plan
        
        return plan
        
    async def _generate_task_steps(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> List[TaskStep]:
        """Generate detailed task steps using the model"""
        prompt = f"""Create a detailed plan for the following task. Break it down into specific steps with dependencies, durations, and required resources.

        Task: {task_description}

        For each step, provide:
        1. A clear description of what needs to be done
        2. Dependencies on other steps (if any)
        3. Estimated duration in hours
        4. Required resources (e.g., compute, memory, storage)
        5. Priority level (1-5, where 1 is highest)

        Format each step as:
        Step ID: <unique_id>
        Description: <description>
        Dependencies: <comma-separated list of step IDs>
        Duration: <hours>
        Resources: <comma-separated list of resources>
        Priority: <1-5>
        """
        
        # Get model response
        response = await self.model_router.route_task({
            "task_type": "planning",
            "content": prompt,
            "context": context
        })
        
        # Parse response into task steps
        steps = []
        current_step = {}
        
        for line in response.content.split('\n'):
            line = line.strip()
            if not line:
                if current_step:
                    steps.append(TaskStep(**current_step))
                    current_step = {}
                continue
                
            if line.startswith('Step ID:'):
                if current_step:
                    steps.append(TaskStep(**current_step))
                current_step = {'id': line.split(':', 1)[1].strip()}
            elif line.startswith('Description:'):
                current_step['description'] = line.split(':', 1)[1].strip()
            elif line.startswith('Dependencies:'):
                current_step['dependencies'] = [d.strip() for d in line.split(':', 1)[1].strip().split(',')]
            elif line.startswith('Duration:'):
                current_step['estimated_duration'] = float(line.split(':', 1)[1].strip())
            elif line.startswith('Resources:'):
                current_step['required_resources'] = [r.strip() for r in line.split(':', 1)[1].strip().split(',')]
            elif line.startswith('Priority:'):
                current_step['priority'] = int(line.split(':', 1)[1].strip())
                
        if current_step:
            steps.append(TaskStep(**current_step))
            
        return steps
        
    async def _allocate_resources(self, steps: List[TaskStep]) -> List[Resource]:
        """Allocate resources to task steps"""
        allocated_resources = []
        resource_usage = {}
        
        # Sort steps by priority and dependencies
        sorted_steps = self._sort_steps(steps)
        
        for step in sorted_steps:
            for resource_name in step.required_resources:
                if resource_name not in self.resources:
                    raise ValueError(f"Resource {resource_name} not found")
                    
                resource = self.resources[resource_name]
                
                # Check resource availability
                if not self._is_resource_available(resource, step.estimated_duration):
                    # Try to find alternative resource
                    alternative = self._find_alternative_resource(resource)
                    if alternative:
                        resource = alternative
                    else:
                        raise ValueError(f"Resource {resource_name} not available")
                        
                # Allocate resource
                resource.current_usage += 1
                resource_usage[resource_name] = resource_usage.get(resource_name, 0) + 1
                
                if resource not in allocated_resources:
                    allocated_resources.append(resource)
                    
        return allocated_resources
        
    def _sort_steps(self, steps: List[TaskStep]) -> List[TaskStep]:
        """Sort steps by priority and dependencies"""
        # Create dependency graph
        graph = {step.id: set(step.dependencies) for step in steps}
        
        # Topological sort
        sorted_steps = []
        visited = set()
        
        def visit(step_id: str):
            if step_id in visited:
                return
            visited.add(step_id)
            
            for dep in graph[step_id]:
                visit(dep)
                
            step = next(s for s in steps if s.id == step_id)
            sorted_steps.append(step)
            
        for step in steps:
            if step.id not in visited:
                visit(step.id)
                
        # Sort by priority within each dependency level
        return sorted(sorted_steps, key=lambda x: x.priority)
        
    def _is_resource_available(self, resource: Resource, duration: float) -> bool:
        """Check if a resource is available for the given duration"""
        if resource.current_usage >= resource.capacity:
            return False
            
        # Check availability windows
        now = datetime.now()
        required_end = now + timedelta(hours=duration)
        
        for start, end in resource.availability:
            if start <= now and end >= required_end:
                return True
                
        return False
        
    def _find_alternative_resource(self, resource: Resource) -> Optional[Resource]:
        """Find an alternative resource with similar capabilities"""
        for alt_resource in self.resources.values():
            if (alt_resource.type == resource.type and
                alt_resource.capacity >= resource.capacity and
                self._is_resource_available(alt_resource, resource.capacity)):
                return alt_resource
        return None
        
    async def execute_plan(self, plan_id: str) -> TaskPlan:
        """Execute a task plan"""
        if plan_id not in self.plans:
            raise ValueError(f"Plan {plan_id} not found")
            
        plan = self.plans[plan_id]
        plan.start_time = datetime.now()
        plan.status = "in_progress"
        
        try:
            # Execute steps in order
            for step in plan.steps:
                if step.status == "pending":
                    step.start_time = datetime.now()
                    step.status = "in_progress"
                    
                    # Execute step
                    await self._execute_step(step)
                    
                    step.end_time = datetime.now()
                    step.status = "completed"
                    step.actual_duration = (step.end_time - step.start_time).total_seconds() / 3600
                    
            plan.end_time = datetime.now()
            plan.status = "completed"
            plan.total_cost = sum(step.cost or 0 for step in plan.steps)
            
            # Update planning metrics
            self._update_planning_metrics(plan)
            
            return plan
            
        except Exception as e:
            plan.status = "failed"
            plan.metadata["error"] = str(e)
            raise
            
    async def _execute_step(self, step: TaskStep):
        """Execute a single step"""
        # Get appropriate model for step execution
        model = await self.model_router.get_model_for_capability("planning")
        
        # Execute step using model
        result = await model.execute_step(step)
        
        # Update step metadata
        step.metadata.update(result.get("metadata", {}))
        step.cost = result.get("cost", 0)
        
    def _update_planning_metrics(self, plan: TaskPlan):
        """Update planning performance metrics"""
        if plan.task_id not in self.planning_metrics:
            self.planning_metrics[plan.task_id] = {
                "planning_accuracy": 0.0,
                "resource_efficiency": 0.0,
                "cost_efficiency": 0.0,
                "time_efficiency": 0.0
            }
            
        metrics = self.planning_metrics[plan.task_id]
        
        # Calculate planning accuracy
        total_duration_diff = sum(
            abs(step.actual_duration - step.estimated_duration)
            for step in plan.steps
            if step.actual_duration is not None
        )
        metrics["planning_accuracy"] = 1 - (total_duration_diff / len(plan.steps))
        
        # Calculate resource efficiency
        total_resources = sum(r.capacity for r in plan.resources)
        used_resources = sum(r.current_usage for r in plan.resources)
        metrics["resource_efficiency"] = used_resources / total_resources
        
        # Calculate cost efficiency
        metrics["cost_efficiency"] = 1 / (plan.total_cost + 1)
        
        # Calculate time efficiency
        planned_duration = sum(step.estimated_duration for step in plan.steps)
        actual_duration = (plan.end_time - plan.start_time).total_seconds() / 3600
        metrics["time_efficiency"] = planned_duration / actual_duration
        
    def get_plan_metrics(self, plan_id: str) -> Dict[str, float]:
        """Get performance metrics for a plan"""
        return self.planning_metrics.get(plan_id, {})
        
    def get_plan_status(self, plan_id: str) -> str:
        """Get the current status of a plan"""
        return self.plans.get(plan_id, TaskPlan(task_id="", description="")).status 