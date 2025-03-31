import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from .agent import Agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskPlannerAgent(Agent):
    """Specialized agent for task planning and coordination."""
    
    def __init__(self, agent_id: str, name: str, config_path: Optional[str] = None):
        """Initialize the task planner agent."""
        capabilities = [
            "task_decomposition",
            "dependency_analysis",
            "resource_allocation",
            "schedule_optimization",
            "progress_tracking",
            "risk_assessment"
        ]
        super().__init__(agent_id, name, capabilities, config_path)
        
        # Initialize task planning specific metrics
        self.metrics.update({
            "tasks_planned": 0,
            "tasks_completed": 0,
            "average_planning_time": 0,
            "schedule_efficiency": 0
        })
        
        # Task planning state
        self.task_graph: Dict[str, Set[str]] = {}  # Task ID -> Dependencies
        self.resource_allocations: Dict[str, Dict[str, Any]] = {}  # Task ID -> Resource info
        self.schedule: Dict[str, datetime] = {}  # Task ID -> Scheduled time
        self.risks: Dict[str, List[Dict[str, Any]]] = {}  # Task ID -> Risk assessments

    def create_task_plan(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed plan for a task."""
        try:
            # Decompose task into subtasks
            subtasks = self._decompose_task(task_data)
            
            # Analyze dependencies
            dependencies = self._analyze_dependencies(subtasks)
            
            # Allocate resources
            resources = self._allocate_resources(subtasks)
            
            # Create schedule
            schedule = self._create_schedule(subtasks, dependencies)
            
            # Assess risks
            risks = self._assess_risks(subtasks)
            
            # Create plan
            plan = {
                "task_id": task_id,
                "subtasks": subtasks,
                "dependencies": dependencies,
                "resources": resources,
                "schedule": schedule,
                "risks": risks,
                "created_at": datetime.now()
            }
            
            # Update metrics
            self._update_planning_metrics(plan)
            
            return plan
            
        except Exception as e:
            self._handle_error(e, task_id)
            return {}

    def _decompose_task(self, task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Break down a task into smaller subtasks."""
        subtasks = []
        
        # Extract task components
        components = task_data.get("components", [])
        for component in components:
            subtask = {
                "id": f"{task_data['task_id']}_{len(subtasks)}",
                "name": component.get("name", ""),
                "description": component.get("description", ""),
                "estimated_duration": component.get("duration", 0),
                "required_skills": component.get("skills", []),
                "priority": component.get("priority", 0)
            }
            subtasks.append(subtask)
        
        return subtasks

    def _analyze_dependencies(self, subtasks: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
        """Analyze dependencies between subtasks."""
        dependencies = {}
        
        for subtask in subtasks:
            subtask_id = subtask["id"]
            dependencies[subtask_id] = set()
            
            # Check for explicit dependencies
            if "depends_on" in subtask:
                dependencies[subtask_id].update(subtask["depends_on"])
            
            # Check for implicit dependencies based on skills
            required_skills = set(subtask["required_skills"])
            for other_subtask in subtasks:
                if other_subtask["id"] != subtask_id:
                    other_skills = set(other_subtask["required_skills"])
                    if required_skills & other_skills:  # If there's skill overlap
                        dependencies[subtask_id].add(other_subtask["id"])
        
        return dependencies

    def _allocate_resources(self, subtasks: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Allocate resources to subtasks."""
        allocations = {}
        
        for subtask in subtasks:
            subtask_id = subtask["id"]
            
            # Determine required resources
            required_resources = {
                "skills": subtask["required_skills"],
                "estimated_duration": subtask["estimated_duration"],
                "priority": subtask["priority"]
            }
            
            # Add resource constraints
            if "resource_constraints" in subtask:
                required_resources.update(subtask["resource_constraints"])
            
            allocations[subtask_id] = required_resources
        
        return allocations

    def _create_schedule(self, subtasks: List[Dict[str, Any]], 
                        dependencies: Dict[str, Set[str]]) -> Dict[str, datetime]:
        """Create an optimized schedule for subtasks."""
        schedule = {}
        current_time = datetime.now()
        
        # Sort subtasks by priority and dependencies
        sorted_subtasks = self._sort_subtasks(subtasks, dependencies)
        
        # Assign start times
        for subtask in sorted_subtasks:
            subtask_id = subtask["id"]
            
            # Find earliest possible start time based on dependencies
            earliest_start = current_time
            for dep_id in dependencies[subtask_id]:
                if dep_id in schedule:
                    dep_end = schedule[dep_id] + subtasks[int(dep_id.split('_')[-1])]["estimated_duration"]
                    earliest_start = max(earliest_start, dep_end)
            
            schedule[subtask_id] = earliest_start
        
        return schedule

    def _sort_subtasks(self, subtasks: List[Dict[str, Any]], 
                       dependencies: Dict[str, Set[str]]) -> List[Dict[str, Any]]:
        """Sort subtasks based on dependencies and priority."""
        # Create a graph of dependencies
        graph = {subtask["id"]: dependencies[subtask["id"]] for subtask in subtasks}
        
        # Topological sort with priority consideration
        sorted_ids = []
        visited = set()
        
        def visit(subtask_id: str) -> None:
            if subtask_id in visited:
                return
            visited.add(subtask_id)
            
            # Visit dependencies first
            for dep_id in graph[subtask_id]:
                visit(dep_id)
            
            sorted_ids.append(subtask_id)
        
        # Visit all subtasks
        for subtask in subtasks:
            visit(subtask["id"])
        
        # Sort by priority within each dependency level
        return sorted(subtasks, key=lambda x: (sorted_ids.index(x["id"]), -x["priority"]))

    def _assess_risks(self, subtasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Assess risks for each subtask."""
        risks = {}
        
        for subtask in subtasks:
            subtask_id = subtask["id"]
            risk_assessments = []
            
            # Assess technical risks
            if "required_skills" in subtask:
                risk_assessments.append({
                    "type": "technical",
                    "description": "Required skills may not be available",
                    "severity": "medium",
                    "mitigation": "Ensure resource availability"
                })
            
            # Assess schedule risks
            if "estimated_duration" in subtask:
                risk_assessments.append({
                    "type": "schedule",
                    "description": "Task may take longer than estimated",
                    "severity": "low",
                    "mitigation": "Include buffer time in schedule"
                })
            
            # Assess dependency risks
            if "depends_on" in subtask:
                risk_assessments.append({
                    "type": "dependency",
                    "description": "Dependent tasks may be delayed",
                    "severity": "high",
                    "mitigation": "Monitor dependent tasks closely"
                })
            
            risks[subtask_id] = risk_assessments
        
        return risks

    def _update_planning_metrics(self, plan: Dict[str, Any]) -> None:
        """Update agent metrics with planning results."""
        with self.state_lock:
            self.metrics["tasks_planned"] += 1
            
            # Calculate planning time
            planning_time = (datetime.now() - plan["created_at"]).total_seconds()
            current_avg = self.metrics["average_planning_time"]
            self.metrics["average_planning_time"] = (
                (current_avg * (self.metrics["tasks_planned"] - 1) + planning_time) 
                / self.metrics["tasks_planned"]
            )
            
            # Calculate schedule efficiency
            subtasks = plan["subtasks"]
            total_duration = sum(subtask["estimated_duration"] for subtask in subtasks)
            schedule_duration = (
                max(plan["schedule"].values()) - min(plan["schedule"].values())
            ).total_seconds()
            
            if schedule_duration > 0:
                self.metrics["schedule_efficiency"] = total_duration / schedule_duration

    def update_task_status(self, task_id: str, status: str, 
                          completion_percentage: float = 0.0) -> None:
        """Update the status of a task."""
        with self.state_lock:
            if task_id in self.task_graph:
                if status == "completed":
                    self.metrics["tasks_completed"] += 1
                elif status == "failed":
                    self.metrics["tasks_failed"] += 1
                
                # Update task graph
                for subtask_id in self.task_graph[task_id]:
                    if subtask_id in self.schedule:
                        # Adjust schedule based on completion
                        if completion_percentage > 0:
                            original_duration = (
                                self.resource_allocations[subtask_id]["estimated_duration"]
                            )
                            remaining_duration = original_duration * (1 - completion_percentage)
                            self.schedule[subtask_id] = datetime.now() + remaining_duration 