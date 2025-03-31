from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
import json
from ..api.agent_communication import AgentCommunicationAPI, Agent, Message, MessageType

@dataclass
class Task:
    id: str
    title: str
    description: str
    assigned_agents: List[str]
    status: str
    priority: int
    created_at: datetime
    deadline: Optional[datetime] = None
    progress: float = 0.0
    dependencies: List[str] = None

class AgentCoordinator:
    def __init__(self):
        self.communication_api = AgentCommunicationAPI()
        self.tasks: Dict[str, Task] = {}
        self.agent_workloads: Dict[str, List[Task]] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.coordination_lock = asyncio.Lock()

    async def register_agent(self, agent: Agent) -> None:
        """Register a new agent and initialize their workload tracking."""
        await self.communication_api.register_agent(agent)
        self.agent_workloads[agent.id] = []

    async def create_task(self, task: Task) -> None:
        """Create a new task and assign it to appropriate agents."""
        self.tasks[task.id] = task
        await self.task_queue.put(task)
        
        # Initialize workload tracking for new agents
        for agent_id in task.assigned_agents:
            if agent_id not in self.agent_workloads:
                self.agent_workloads[agent_id] = []
            self.agent_workloads[agent_id].append(task)

        # Notify assigned agents
        await self._notify_agents_of_task(task)

    async def _notify_agents_of_task(self, task: Task) -> None:
        """Notify assigned agents about their new task."""
        task_message = Message(
            id=f"task_{task.id}",
            agent_id="system",
            content={
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "deadline": task.deadline.isoformat() if task.deadline else None
            },
            type=MessageType.STATUS,
            timestamp=datetime.now()
        )

        for agent_id in task.assigned_agents:
            await self.communication_api.send_message(task_message)

    async def update_task_progress(self, task_id: str, progress: float) -> None:
        """Update the progress of a task."""
        if task_id in self.tasks:
            self.tasks[task_id].progress = progress
            await self._notify_progress_update(task_id, progress)

    async def _notify_progress_update(self, task_id: str, progress: float) -> None:
        """Notify relevant agents about task progress updates."""
        task = self.tasks[task_id]
        progress_message = Message(
            id=f"progress_{task_id}_{datetime.now().timestamp()}",
            agent_id="system",
            content={
                "task_id": task_id,
                "progress": progress,
                "status": "completed" if progress >= 100 else "in_progress"
            },
            type=MessageType.STATUS,
            timestamp=datetime.now()
        )

        for agent_id in task.assigned_agents:
            await self.communication_api.send_message(progress_message)

    async def get_agent_workload(self, agent_id: str) -> List[Task]:
        """Get the current workload of an agent."""
        return self.agent_workloads.get(agent_id, [])

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            return {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "progress": task.progress,
                "assigned_agents": task.assigned_agents,
                "deadline": task.deadline.isoformat() if task.deadline else None
            }
        return None

    async def reassign_task(self, task_id: str, new_agents: List[str]) -> None:
        """Reassign a task to different agents."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            
            # Remove task from old agents' workloads
            for old_agent_id in task.assigned_agents:
                if old_agent_id in self.agent_workloads:
                    self.agent_workloads[old_agent_id] = [
                        t for t in self.agent_workloads[old_agent_id]
                        if t.id != task_id
                    ]

            # Add task to new agents' workloads
            task.assigned_agents = new_agents
            for new_agent_id in new_agents:
                if new_agent_id not in self.agent_workloads:
                    self.agent_workloads[new_agent_id] = []
                self.agent_workloads[new_agent_id].append(task)

            # Notify agents of reassignment
            await self._notify_task_reassignment(task_id, new_agents)

    async def _notify_task_reassignment(self, task_id: str, new_agents: List[str]) -> None:
        """Notify agents about task reassignment."""
        task = self.tasks[task_id]
        reassignment_message = Message(
            id=f"reassign_{task_id}_{datetime.now().timestamp()}",
            agent_id="system",
            content={
                "task_id": task_id,
                "title": task.title,
                "new_agents": new_agents
            },
            type=MessageType.STATUS,
            timestamp=datetime.now()
        )

        for agent_id in new_agents:
            await self.communication_api.send_message(reassignment_message)

    async def get_task_dependencies(self, task_id: str) -> List[Task]:
        """Get all dependencies for a task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.dependencies:
                return [
                    self.tasks[dep_id] for dep_id in task.dependencies
                    if dep_id in self.tasks
                ]
        return []

    async def check_task_completion(self, task_id: str) -> bool:
        """Check if a task and all its dependencies are completed."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        if task.progress < 100:
            return False

        # Check dependencies
        if task.dependencies:
            for dep_id in task.dependencies:
                if dep_id in self.tasks:
                    dep_task = self.tasks[dep_id]
                    if dep_task.progress < 100:
                        return False

        return True

    async def get_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """Get performance metrics for an agent."""
        if agent_id not in self.agent_workloads:
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "average_progress": 0,
                "on_time_completion_rate": 0
            }

        tasks = self.agent_workloads[agent_id]
        completed_tasks = [t for t in tasks if t.progress >= 100]
        on_time_tasks = [
            t for t in completed_tasks
            if not t.deadline or t.deadline >= datetime.now()
        ]

        return {
            "total_tasks": len(tasks),
            "completed_tasks": len(completed_tasks),
            "average_progress": sum(t.progress for t in tasks) / len(tasks) if tasks else 0,
            "on_time_completion_rate": len(on_time_tasks) / len(completed_tasks) if completed_tasks else 0
        }

    async def export_coordination_state(self) -> str:
        """Export the current coordination state as JSON."""
        state = {
            "tasks": {
                task_id: {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "progress": task.progress,
                    "assigned_agents": task.assigned_agents,
                    "deadline": task.deadline.isoformat() if task.deadline else None,
                    "dependencies": task.dependencies
                }
                for task_id, task in self.tasks.items()
            },
            "agent_workloads": {
                agent_id: [task.id for task in tasks]
                for agent_id, tasks in self.agent_workloads.items()
            }
        }
        return json.dumps(state, default=str) 