from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from ..storage.project_store import ProjectStore
from ..orchestrator.project_state import ProjectState

@dataclass
class ProjectMetrics:
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    completion_rate: float
    average_task_duration: timedelta
    team_velocity: float
    resource_utilization: float
    risk_score: float
    milestone_completion: float

class ProjectMetricsAPI:
    def __init__(self, project_store: ProjectStore, project_state: ProjectState):
        self.project_store = project_store
        self.project_state = project_state

    async def calculate_project_metrics(self) -> ProjectMetrics:
        """Calculate overall project metrics."""
        tasks = await self.project_store.get_all_tasks()
        milestones = await self.project_store.get_all_milestones()
        resources = await self.project_store.get_resource_allocations()

        completed_tasks = [t for t in tasks if t.status == 'completed']
        in_progress_tasks = [t for t in tasks if t.status == 'in_progress']
        blocked_tasks = [t for t in tasks if t.status == 'blocked']

        # Calculate completion rate
        completion_rate = len(completed_tasks) / len(tasks) if tasks else 0

        # Calculate average task duration
        task_durations = [
            t.end_date - t.start_date
            for t in completed_tasks
            if t.start_date and t.end_date
        ]
        avg_duration = (
            sum(task_durations, timedelta()) / len(task_durations)
            if task_durations else timedelta()
        )

        # Calculate team velocity (tasks completed per week)
        recent_completed = [
            t for t in completed_tasks
            if t.end_date >= datetime.now() - timedelta(days=7)
        ]
        team_velocity = len(recent_completed)

        # Calculate resource utilization
        total_hours = sum(r.hours_allocated for r in resources)
        actual_hours = sum(r.hours_worked for r in resources)
        resource_utilization = actual_hours / total_hours if total_hours > 0 else 0

        # Calculate risk score
        risk_score = self._calculate_risk_score(tasks, milestones)

        # Calculate milestone completion
        completed_milestones = [m for m in milestones if m.status == 'completed']
        milestone_completion = len(completed_milestones) / len(milestones) if milestones else 0

        return ProjectMetrics(
            total_tasks=len(tasks),
            completed_tasks=len(completed_tasks),
            in_progress_tasks=len(in_progress_tasks),
            blocked_tasks=len(blocked_tasks),
            completion_rate=completion_rate,
            average_task_duration=avg_duration,
            team_velocity=team_velocity,
            resource_utilization=resource_utilization,
            risk_score=risk_score,
            milestone_completion=milestone_completion
        )

    async def calculate_task_metrics(self, task_id: str) -> Dict[str, Any]:
        """Calculate metrics for a specific task."""
        task = await self.project_store.get_task(task_id)
        if not task:
            return {}

        dependencies = await self.project_store.get_task_dependencies(task_id)
        assigned_resources = await self.project_store.get_task_resources(task_id)

        # Calculate progress
        progress = self._calculate_task_progress(task)

        # Calculate time metrics
        time_metrics = self._calculate_time_metrics(task)

        # Calculate dependency impact
        dependency_impact = self._calculate_dependency_impact(dependencies)

        # Calculate resource metrics
        resource_metrics = self._calculate_resource_metrics(assigned_resources)

        return {
            'id': task.id,
            'title': task.title,
            'progress': progress,
            'time_metrics': time_metrics,
            'dependency_impact': dependency_impact,
            'resource_metrics': resource_metrics,
            'status': task.status,
            'priority': task.priority
        }

    async def calculate_team_metrics(self) -> Dict[str, Any]:
        """Calculate metrics for the entire team."""
        team_members = await self.project_store.get_team_members()
        tasks = await self.project_store.get_all_tasks()

        team_metrics = {
            'member_metrics': {},
            'overall_performance': {},
            'workload_distribution': {}
        }

        for member in team_members:
            member_tasks = [t for t in tasks if t.assignee_id == member.id]
            completed_tasks = [t for t in member_tasks if t.status == 'completed']
            
            team_metrics['member_metrics'][member.id] = {
                'total_tasks': len(member_tasks),
                'completed_tasks': len(completed_tasks),
                'completion_rate': len(completed_tasks) / len(member_tasks) if member_tasks else 0,
                'average_task_duration': self._calculate_member_avg_duration(completed_tasks)
            }

        # Calculate overall team performance
        team_metrics['overall_performance'] = {
            'total_tasks': len(tasks),
            'completed_tasks': len([t for t in tasks if t.status == 'completed']),
            'average_completion_rate': sum(
                m['completion_rate'] for m in team_metrics['member_metrics'].values()
            ) / len(team_metrics['member_metrics']) if team_metrics['member_metrics'] else 0
        }

        # Calculate workload distribution
        team_metrics['workload_distribution'] = self._calculate_workload_distribution(tasks, team_members)

        return team_metrics

    async def calculate_resource_metrics(self) -> Dict[str, Any]:
        """Calculate resource allocation and utilization metrics."""
        resources = await self.project_store.get_resource_allocations()
        tasks = await self.project_store.get_all_tasks()

        resource_metrics = {
            'allocation': {},
            'utilization': {},
            'bottlenecks': []
        }

        # Calculate allocation metrics
        for resource in resources:
            resource_metrics['allocation'][resource.id] = {
                'total_hours': resource.hours_allocated,
                'actual_hours': resource.hours_worked,
                'utilization_rate': resource.hours_worked / resource.hours_allocated
                    if resource.hours_allocated > 0 else 0
            }

        # Calculate overall utilization
        total_allocated = sum(r.hours_allocated for r in resources)
        total_worked = sum(r.hours_worked for r in resources)
        resource_metrics['utilization'] = {
            'total_allocated': total_allocated,
            'total_worked': total_worked,
            'overall_rate': total_worked / total_allocated if total_allocated > 0 else 0
        }

        # Identify bottlenecks
        resource_metrics['bottlenecks'] = self._identify_resource_bottlenecks(resources, tasks)

        return resource_metrics

    def _calculate_risk_score(self, tasks: List[Any], milestones: List[Any]) -> float:
        """Calculate overall project risk score."""
        risk_factors = {
            'blocked_tasks': len([t for t in tasks if t.status == 'blocked']) / len(tasks) if tasks else 0,
            'overdue_tasks': len([t for t in tasks if t.end_date < datetime.now()]) / len(tasks) if tasks else 0,
            'missed_milestones': len([m for m in milestones if m.status == 'overdue']) / len(milestones) if milestones else 0,
            'resource_overload': self._calculate_resource_overload(tasks)
        }

        weights = {
            'blocked_tasks': 0.3,
            'overdue_tasks': 0.3,
            'missed_milestones': 0.2,
            'resource_overload': 0.2
        }

        return sum(risk_factors[factor] * weights[factor] for factor in risk_factors)

    def _calculate_task_progress(self, task: Any) -> float:
        """Calculate progress for a specific task."""
        if task.status == 'completed':
            return 100.0
        elif task.status == 'blocked':
            return 0.0
        elif task.start_date and task.end_date:
            total_duration = (task.end_date - task.start_date).total_seconds()
            elapsed_duration = (datetime.now() - task.start_date).total_seconds()
            return min(100.0, max(0.0, (elapsed_duration / total_duration) * 100))
        return 0.0

    def _calculate_time_metrics(self, task: Any) -> Dict[str, Any]:
        """Calculate time-related metrics for a task."""
        if not task.start_date or not task.end_date:
            return {}

        total_duration = task.end_date - task.start_date
        elapsed_time = datetime.now() - task.start_date
        remaining_time = task.end_date - datetime.now()

        return {
            'total_duration': total_duration,
            'elapsed_time': elapsed_time,
            'remaining_time': remaining_time,
            'is_overdue': remaining_time.total_seconds() < 0
        }

    def _calculate_dependency_impact(self, dependencies: List[Any]) -> Dict[str, Any]:
        """Calculate the impact of task dependencies."""
        if not dependencies:
            return {}

        blocked_dependencies = [d for d in dependencies if d.status == 'blocked']
        completed_dependencies = [d for d in dependencies if d.status == 'completed']

        return {
            'total_dependencies': len(dependencies),
            'blocked_dependencies': len(blocked_dependencies),
            'completed_dependencies': len(completed_dependencies),
            'blocking_factor': len(blocked_dependencies) / len(dependencies) if dependencies else 0
        }

    def _calculate_resource_metrics(self, resources: List[Any]) -> Dict[str, Any]:
        """Calculate metrics for assigned resources."""
        if not resources:
            return {}

        total_hours = sum(r.hours_allocated for r in resources)
        actual_hours = sum(r.hours_worked for r in resources)

        return {
            'total_resources': len(resources),
            'total_hours_allocated': total_hours,
            'actual_hours_worked': actual_hours,
            'utilization_rate': actual_hours / total_hours if total_hours > 0 else 0
        }

    def _calculate_member_avg_duration(self, tasks: List[Any]) -> timedelta:
        """Calculate average task duration for a team member."""
        durations = [
            t.end_date - t.start_date
            for t in tasks
            if t.start_date and t.end_date
        ]
        return sum(durations, timedelta()) / len(durations) if durations else timedelta()

    def _calculate_workload_distribution(self, tasks: List[Any], team_members: List[Any]) -> Dict[str, float]:
        """Calculate workload distribution across team members."""
        distribution = {}
        total_tasks = len(tasks)

        for member in team_members:
            member_tasks = [t for t in tasks if t.assignee_id == member.id]
            distribution[member.id] = len(member_tasks) / total_tasks if total_tasks > 0 else 0

        return distribution

    def _identify_resource_bottlenecks(self, resources: List[Any], tasks: List[Any]) -> List[Dict[str, Any]]:
        """Identify resource bottlenecks in the project."""
        bottlenecks = []
        utilization_threshold = 0.9  # 90% utilization threshold

        for resource in resources:
            utilization = resource.hours_worked / resource.hours_allocated if resource.hours_allocated > 0 else 0
            if utilization >= utilization_threshold:
                assigned_tasks = [t for t in tasks if t.assignee_id == resource.id]
                bottlenecks.append({
                    'resource_id': resource.id,
                    'name': resource.name,
                    'utilization_rate': utilization,
                    'assigned_tasks': len(assigned_tasks),
                    'overloaded': utilization > 1.0
                })

        return bottlenecks

    def _calculate_resource_overload(self, tasks: List[Any]) -> float:
        """Calculate the overall resource overload factor."""
        if not tasks:
            return 0.0

        total_allocated_hours = sum(t.estimated_hours for t in tasks if t.estimated_hours)
        total_available_hours = len(tasks) * 40  # Assuming 40 hours per week per resource

        return min(1.0, total_allocated_hours / total_available_hours) if total_available_hours > 0 else 0.0 