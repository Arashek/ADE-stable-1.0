from typing import Dict, Any, List, Optional, Set, Tuple
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

from .time_aware import TimeAwareProjectManager, Task, Milestone, TaskStatus

logger = logging.getLogger(__name__)

@dataclass
class TaskSchedule:
    """Represents a task schedule"""
    task_id: str
    start_time: datetime
    end_time: datetime
    dependencies: List[str]
    priority: int
    status: TaskStatus
    metadata: Dict[str, Any] = None

@dataclass
class SchedulePlan:
    """Represents a complete schedule plan"""
    schedules: Dict[str, TaskSchedule]
    start_time: datetime
    end_time: datetime
    metadata: Dict[str, Any] = None

class TaskScheduler:
    """Handles task scheduling and optimization"""
    
    def __init__(self, project_manager: TimeAwareProjectManager):
        self.project_manager = project_manager
        self.current_schedule: Optional[SchedulePlan] = None
    
    async def update_schedule(self) -> SchedulePlan:
        """Update task schedule based on current state
        
        Returns:
            Updated schedule plan
        """
        try:
            # Get all tasks
            tasks = self.project_manager.timeline.tasks
            
            # Get all milestones
            milestones = self.project_manager.timeline.milestones
            
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(tasks, milestones)
            
            # Calculate earliest start times
            earliest_starts = self._calculate_earliest_starts(dependency_graph)
            
            # Calculate latest end times
            latest_ends = self._calculate_latest_ends(dependency_graph, earliest_starts)
            
            # Create schedules
            schedules = {}
            for task_id, task in tasks.items():
                if task.status == TaskStatus.COMPLETED:
                    continue
                
                schedule = TaskSchedule(
                    task_id=task_id,
                    start_time=earliest_starts[task_id],
                    end_time=latest_ends[task_id],
                    dependencies=list(task.dependencies),
                    priority=task.priority,
                    status=task.status,
                    metadata={
                        "estimated_duration": str(task.estimated_duration) if task.estimated_duration else None,
                        "assigned_to": task.assigned_to,
                        "tags": list(task.tags)
                    }
                )
                schedules[task_id] = schedule
            
            # Create schedule plan
            self.current_schedule = SchedulePlan(
                schedules=schedules,
                start_time=min(s.start_time for s in schedules.values()) if schedules else datetime.now(),
                end_time=max(s.end_time for s in schedules.values()) if schedules else datetime.now(),
                metadata={
                    "num_tasks": len(schedules),
                    "num_milestones": len(milestones),
                    "total_duration": str(max(s.end_time for s in schedules.values()) - min(s.start_time for s in schedules.values())) if schedules else "0:00:00"
                }
            )
            
            return self.current_schedule
            
        except Exception as e:
            logger.error(f"Failed to update schedule: {str(e)}")
            raise
    
    def _build_dependency_graph(
        self,
        tasks: Dict[str, Task],
        milestones: Dict[str, Milestone]
    ) -> Dict[str, Set[str]]:
        """Build dependency graph
        
        Args:
            tasks: Dictionary of tasks
            milestones: Dictionary of milestones
            
        Returns:
            Dictionary mapping task IDs to sets of dependent task IDs
        """
        try:
            graph = defaultdict(set)
            
            # Add task dependencies
            for task_id, task in tasks.items():
                graph[task_id].update(task.dependencies)
            
            # Add milestone dependencies
            for milestone in milestones.values():
                for task_id in milestone.tasks:
                    # Add milestone deadline as constraint
                    graph[task_id].add(f"milestone_{milestone.id}")
                    
                    # Add dependencies from milestone tasks
                    for other_task_id in milestone.tasks:
                        if other_task_id != task_id:
                            graph[task_id].add(other_task_id)
            
            return dict(graph)
            
        except Exception as e:
            logger.error(f"Failed to build dependency graph: {str(e)}")
            raise
    
    def _calculate_earliest_starts(
        self,
        dependency_graph: Dict[str, Set[str]]
    ) -> Dict[str, datetime]:
        """Calculate earliest possible start times
        
        Args:
            dependency_graph: Dependency graph
            
        Returns:
            Dictionary mapping task IDs to earliest start times
        """
        try:
            earliest_starts = {}
            visited = set()
            
            def calculate_start(task_id: str) -> datetime:
                if task_id in earliest_starts:
                    return earliest_starts[task_id]
                
                if task_id in visited:
                    raise ValueError(f"Circular dependency detected: {task_id}")
                
                visited.add(task_id)
                
                # Get task
                task = self.project_manager.timeline.tasks.get(task_id)
                if not task:
                    return datetime.now()
                
                # Calculate earliest start based on dependencies
                earliest = datetime.now()
                for dep_id in dependency_graph.get(task_id, set()):
                    if dep_id.startswith("milestone_"):
                        # Handle milestone dependency
                        milestone_id = dep_id[10:]  # Remove "milestone_" prefix
                        milestone = self.project_manager.timeline.milestones.get(milestone_id)
                        if milestone:
                            earliest = max(earliest, milestone.deadline)
                    else:
                        # Handle task dependency
                        dep_start = calculate_start(dep_id)
                        dep_task = self.project_manager.timeline.tasks.get(dep_id)
                        if dep_task and dep_task.estimated_duration:
                            earliest = max(earliest, dep_start + dep_task.estimated_duration)
                
                earliest_starts[task_id] = earliest
                return earliest
            
            # Calculate starts for all tasks
            for task_id in dependency_graph:
                if task_id not in earliest_starts:
                    calculate_start(task_id)
            
            return earliest_starts
            
        except Exception as e:
            logger.error(f"Failed to calculate earliest starts: {str(e)}")
            raise
    
    def _calculate_latest_ends(
        self,
        dependency_graph: Dict[str, Set[str]],
        earliest_starts: Dict[str, datetime]
    ) -> Dict[str, datetime]:
        """Calculate latest possible end times
        
        Args:
            dependency_graph: Dependency graph
            earliest_starts: Dictionary of earliest start times
            
        Returns:
            Dictionary mapping task IDs to latest end times
        """
        try:
            latest_ends = {}
            visited = set()
            
            def calculate_end(task_id: str) -> datetime:
                if task_id in latest_ends:
                    return latest_ends[task_id]
                
                if task_id in visited:
                    raise ValueError(f"Circular dependency detected: {task_id}")
                
                visited.add(task_id)
                
                # Get task
                task = self.project_manager.timeline.tasks.get(task_id)
                if not task:
                    return datetime.now()
                
                # Calculate latest end based on dependencies
                latest = datetime.max
                for dep_id in dependency_graph.get(task_id, set()):
                    if dep_id.startswith("milestone_"):
                        # Handle milestone dependency
                        milestone_id = dep_id[10:]  # Remove "milestone_" prefix
                        milestone = self.project_manager.timeline.milestones.get(milestone_id)
                        if milestone:
                            latest = min(latest, milestone.deadline)
                    else:
                        # Handle task dependency
                        dep_end = calculate_end(dep_id)
                        latest = min(latest, dep_end)
                
                # If no dependencies, use milestone deadline
                if latest == datetime.max:
                    for milestone in self.project_manager.timeline.milestones.values():
                        if task_id in milestone.tasks:
                            latest = min(latest, milestone.deadline)
                
                # If still no deadline, use reasonable future date
                if latest == datetime.max:
                    latest = earliest_starts[task_id] + (task.estimated_duration or timedelta(days=7))
                
                latest_ends[task_id] = latest
                return latest
            
            # Calculate ends for all tasks
            for task_id in dependency_graph:
                if task_id not in latest_ends:
                    calculate_end(task_id)
            
            return latest_ends
            
        except Exception as e:
            logger.error(f"Failed to calculate latest ends: {str(e)}")
            raise
    
    async def get_task_schedule(
        self,
        task_id: str
    ) -> Optional[TaskSchedule]:
        """Get schedule for a specific task
        
        Args:
            task_id: Task ID
            
        Returns:
            Task schedule or None if not found
        """
        try:
            if not self.current_schedule:
                await self.update_schedule()
            
            return self.current_schedule.schedules.get(task_id)
            
        except Exception as e:
            logger.error(f"Failed to get task schedule: {str(e)}")
            return None
    
    async def get_upcoming_tasks(
        self,
        time_window: timedelta = timedelta(days=7)
    ) -> List[TaskSchedule]:
        """Get tasks scheduled to start within time window
        
        Args:
            time_window: Time window to look ahead
            
        Returns:
            List of upcoming task schedules
        """
        try:
            if not self.current_schedule:
                await self.update_schedule()
            
            now = datetime.now()
            window_end = now + time_window
            
            return [
                schedule for schedule in self.current_schedule.schedules.values()
                if schedule.start_time >= now and schedule.start_time <= window_end
            ]
            
        except Exception as e:
            logger.error(f"Failed to get upcoming tasks: {str(e)}")
            return []
    
    async def get_overdue_tasks(self) -> List[TaskSchedule]:
        """Get tasks that are overdue
        
        Returns:
            List of overdue task schedules
        """
        try:
            if not self.current_schedule:
                await self.update_schedule()
            
            now = datetime.now()
            
            return [
                schedule for schedule in self.current_schedule.schedules.values()
                if schedule.end_time < now and schedule.status != TaskStatus.COMPLETED
            ]
            
        except Exception as e:
            logger.error(f"Failed to get overdue tasks: {str(e)}")
            return []
    
    async def get_critical_path(self) -> List[TaskSchedule]:
        """Get tasks on critical path
        
        Returns:
            List of critical path task schedules
        """
        try:
            if not self.current_schedule:
                await self.update_schedule()
            
            critical_path = []
            
            # Find tasks with no slack time
            for schedule in self.current_schedule.schedules.values():
                if schedule.end_time - schedule.start_time == schedule.metadata.get("estimated_duration", timedelta()):
                    critical_path.append(schedule)
            
            # Sort by start time
            critical_path.sort(key=lambda s: s.start_time)
            
            return critical_path
            
        except Exception as e:
            logger.error(f"Failed to get critical path: {str(e)}")
            return []
    
    async def get_resource_utilization(
        self,
        agent_id: str
    ) -> Dict[str, Any]:
        """Get resource utilization for an agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Dictionary of utilization metrics
        """
        try:
            if not self.current_schedule:
                await self.update_schedule()
            
            # Get agent's tasks
            agent_tasks = [
                schedule for schedule in self.current_schedule.schedules.values()
                if schedule.metadata.get("assigned_to") == agent_id
            ]
            
            if not agent_tasks:
                return {
                    "num_tasks": 0,
                    "total_duration": "0:00:00",
                    "utilization_percentage": 0.0
                }
            
            # Calculate metrics
            total_duration = sum(
                schedule.end_time - schedule.start_time
                for schedule in agent_tasks
            )
            
            # Calculate utilization percentage
            time_window = max(s.end_time for s in agent_tasks) - min(s.start_time for s in agent_tasks)
            utilization_percentage = (total_duration.total_seconds() / time_window.total_seconds()) * 100
            
            return {
                "num_tasks": len(agent_tasks),
                "total_duration": str(total_duration),
                "utilization_percentage": utilization_percentage,
                "tasks": [
                    {
                        "task_id": schedule.task_id,
                        "start_time": schedule.start_time.isoformat(),
                        "end_time": schedule.end_time.isoformat(),
                        "duration": str(schedule.end_time - schedule.start_time),
                        "priority": schedule.priority
                    }
                    for schedule in agent_tasks
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get resource utilization: {str(e)}")
            return {
                "num_tasks": 0,
                "total_duration": "0:00:00",
                "utilization_percentage": 0.0
            } 