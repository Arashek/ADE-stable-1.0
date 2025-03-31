from typing import Dict, Any, List, Optional, Set, Tuple
import logging
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from collections import defaultdict
import uuid
from enum import Enum

from ..core.orchestrator import Orchestrator
from ..agents.base import BaseAgent
from ..memory.memory_manager import MemoryManager
from ..database.mongodb import MongoDB

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task status enumeration"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EventType(Enum):
    """Project event type enumeration"""
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_BLOCKED = "task_blocked"
    TASK_CANCELLED = "task_cancelled"
    MILESTONE_CREATED = "milestone_created"
    MILESTONE_COMPLETED = "milestone_completed"
    DEADLINE_SET = "deadline_set"
    DEADLINE_MODIFIED = "deadline_modified"
    DEPENDENCY_ADDED = "dependency_added"
    DEPENDENCY_REMOVED = "dependency_removed"
    COMMENT_ADDED = "comment_added"
    STATUS_UPDATE = "status_update"

@dataclass
class Task:
    """Represents a project task"""
    id: str
    title: str
    description: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: Optional[timedelta] = None
    actual_duration: Optional[timedelta] = None
    dependencies: Set[str] = None  # Set of task IDs
    assigned_to: Optional[str] = None  # Agent ID
    priority: int = 0
    tags: Set[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class Milestone:
    """Represents a project milestone"""
    id: str
    title: str
    description: str
    deadline: datetime
    completed_at: Optional[datetime] = None
    tasks: Set[str] = None  # Set of task IDs
    dependencies: Set[str] = None  # Set of milestone IDs
    metadata: Dict[str, Any] = None

@dataclass
class TimelineEvent:
    """Represents an event in the project timeline"""
    id: str
    type: EventType
    timestamp: datetime
    project_id: str
    task_id: Optional[str] = None
    milestone_id: Optional[str] = None
    agent_id: Optional[str] = None
    details: Dict[str, Any] = None
    metadata: Dict[str, Any] = None

@dataclass
class ProjectTimeline:
    """Represents a project timeline"""
    project_id: str
    events: List[TimelineEvent]
    tasks: Dict[str, Task]
    milestones: Dict[str, Milestone]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = None

class TimeAwareProjectManager:
    """Handles time-aware project management"""
    
    def __init__(
        self,
        orchestrator: Orchestrator,
        memory_manager: MemoryManager,
        mongodb: MongoDB,
        project_id: str
    ):
        self.orchestrator = orchestrator
        self.memory_manager = memory_manager
        self.mongodb = mongodb
        self.project_id = project_id
        
        # Initialize timeline
        self.timeline = ProjectTimeline(
            project_id=project_id,
            events=[],
            tasks={},
            milestones={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Initialize components
        self.timeline_tracker = TimelineTracker(self)
        self.task_scheduler = TaskScheduler(self)
        self.reporting_engine = ReportingEngine(self)
        self.notification_system = NotificationSystem(self)
        
        # Load existing timeline data
        self._load_timeline_data()
    
    async def create_task(
        self,
        title: str,
        description: str,
        estimated_duration: Optional[timedelta] = None,
        dependencies: Optional[Set[str]] = None,
        assigned_to: Optional[str] = None,
        priority: int = 0,
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """Create a new task
        
        Args:
            title: Task title
            description: Task description
            estimated_duration: Estimated task duration
            dependencies: Set of dependent task IDs
            assigned_to: Agent ID to assign task to
            priority: Task priority
            tags: Set of task tags
            metadata: Additional task metadata
            
        Returns:
            Created task
        """
        try:
            # Generate task ID
            task_id = f"task_{uuid.uuid4().hex}"
            
            # Create task
            task = Task(
                id=task_id,
                title=title,
                description=description,
                status=TaskStatus.NOT_STARTED,
                created_at=datetime.now(),
                estimated_duration=estimated_duration,
                dependencies=dependencies or set(),
                assigned_to=assigned_to,
                priority=priority,
                tags=tags or set(),
                metadata=metadata or {}
            )
            
            # Add task to timeline
            self.timeline.tasks[task_id] = task
            
            # Record event
            event = TimelineEvent(
                id=f"event_{uuid.uuid4().hex}",
                type=EventType.TASK_CREATED,
                timestamp=datetime.now(),
                project_id=self.project_id,
                task_id=task_id,
                details={
                    "title": title,
                    "description": description,
                    "estimated_duration": str(estimated_duration) if estimated_duration else None,
                    "dependencies": list(dependencies) if dependencies else [],
                    "assigned_to": assigned_to,
                    "priority": priority,
                    "tags": list(tags) if tags else []
                }
            )
            self.timeline.events.append(event)
            
            # Update timeline
            self.timeline.updated_at = datetime.now()
            
            # Save to database
            await self._save_timeline_data()
            
            # Notify relevant agents
            await self.notification_system.notify_task_created(task)
            
            return task
            
        except Exception as e:
            logger.error(f"Failed to create task: {str(e)}")
            raise
    
    async def create_milestone(
        self,
        title: str,
        description: str,
        deadline: datetime,
        tasks: Optional[Set[str]] = None,
        dependencies: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Milestone:
        """Create a new milestone
        
        Args:
            title: Milestone title
            description: Milestone description
            deadline: Milestone deadline
            tasks: Set of task IDs
            dependencies: Set of dependent milestone IDs
            metadata: Additional milestone metadata
            
        Returns:
            Created milestone
        """
        try:
            # Generate milestone ID
            milestone_id = f"milestone_{uuid.uuid4().hex}"
            
            # Create milestone
            milestone = Milestone(
                id=milestone_id,
                title=title,
                description=description,
                deadline=deadline,
                tasks=tasks or set(),
                dependencies=dependencies or set(),
                metadata=metadata or {}
            )
            
            # Add milestone to timeline
            self.timeline.milestones[milestone_id] = milestone
            
            # Record event
            event = TimelineEvent(
                id=f"event_{uuid.uuid4().hex}",
                type=EventType.MILESTONE_CREATED,
                timestamp=datetime.now(),
                project_id=self.project_id,
                milestone_id=milestone_id,
                details={
                    "title": title,
                    "description": description,
                    "deadline": deadline.isoformat(),
                    "tasks": list(tasks) if tasks else [],
                    "dependencies": list(dependencies) if dependencies else []
                }
            )
            self.timeline.events.append(event)
            
            # Update timeline
            self.timeline.updated_at = datetime.now()
            
            # Save to database
            await self._save_timeline_data()
            
            # Notify relevant agents
            await self.notification_system.notify_milestone_created(milestone)
            
            return milestone
            
        except Exception as e:
            logger.error(f"Failed to create milestone: {str(e)}")
            raise
    
    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        agent_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update task status
        
        Args:
            task_id: Task ID
            status: New status
            agent_id: Agent making the update
            details: Additional update details
        """
        try:
            if task_id not in self.timeline.tasks:
                raise ValueError(f"Task not found: {task_id}")
            
            task = self.timeline.tasks[task_id]
            old_status = task.status
            task.status = status
            
            # Update timestamps
            if status == TaskStatus.IN_PROGRESS and not task.started_at:
                task.started_at = datetime.now()
            elif status == TaskStatus.COMPLETED and not task.completed_at:
                task.completed_at = datetime.now()
                if task.started_at:
                    task.actual_duration = task.completed_at - task.started_at
            
            # Record event
            event = TimelineEvent(
                id=f"event_{uuid.uuid4().hex}",
                type=EventType.STATUS_UPDATE,
                timestamp=datetime.now(),
                project_id=self.project_id,
                task_id=task_id,
                agent_id=agent_id,
                details={
                    "old_status": old_status.value,
                    "new_status": status.value,
                    "details": details or {}
                }
            )
            self.timeline.events.append(event)
            
            # Update timeline
            self.timeline.updated_at = datetime.now()
            
            # Save to database
            await self._save_timeline_data()
            
            # Update task schedule
            await self.task_scheduler.update_schedule()
            
            # Notify relevant agents
            await self.notification_system.notify_task_status_updated(task, old_status, status)
            
        except Exception as e:
            logger.error(f"Failed to update task status: {str(e)}")
            raise
    
    async def update_milestone_status(
        self,
        milestone_id: str,
        completed: bool,
        agent_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update milestone status
        
        Args:
            milestone_id: Milestone ID
            completed: Whether milestone is completed
            agent_id: Agent making the update
            details: Additional update details
        """
        try:
            if milestone_id not in self.timeline.milestones:
                raise ValueError(f"Milestone not found: {milestone_id}")
            
            milestone = self.timeline.milestones[milestone_id]
            old_completed = milestone.completed_at is not None
            milestone.completed_at = datetime.now() if completed else None
            
            # Record event
            event = TimelineEvent(
                id=f"event_{uuid.uuid4().hex}",
                type=EventType.MILESTONE_COMPLETED if completed else EventType.STATUS_UPDATE,
                timestamp=datetime.now(),
                project_id=self.project_id,
                milestone_id=milestone_id,
                agent_id=agent_id,
                details={
                    "old_completed": old_completed,
                    "new_completed": completed,
                    "details": details or {}
                }
            )
            self.timeline.events.append(event)
            
            # Update timeline
            self.timeline.updated_at = datetime.now()
            
            # Save to database
            await self._save_timeline_data()
            
            # Notify relevant agents
            await self.notification_system.notify_milestone_status_updated(milestone, old_completed, completed)
            
        except Exception as e:
            logger.error(f"Failed to update milestone status: {str(e)}")
            raise
    
    async def estimate_task_duration(
        self,
        task_id: str
    ) -> Optional[timedelta]:
        """Estimate task duration based on historical data
        
        Args:
            task_id: Task ID
            
        Returns:
            Estimated duration or None if estimation not possible
        """
        try:
            if task_id not in self.timeline.tasks:
                raise ValueError(f"Task not found: {task_id}")
            
            task = self.timeline.tasks[task_id]
            
            # Get similar completed tasks
            similar_tasks = await self._find_similar_tasks(task)
            
            if not similar_tasks:
                return None
            
            # Calculate average duration
            durations = []
            for similar_task in similar_tasks:
                if similar_task.actual_duration:
                    durations.append(similar_task.actual_duration)
            
            if not durations:
                return None
            
            # Calculate weighted average based on similarity
            total_weight = 0
            weighted_sum = timedelta()
            
            for similar_task, duration in zip(similar_tasks, durations):
                similarity = await self._calculate_task_similarity(task, similar_task)
                total_weight += similarity
                weighted_sum += duration * similarity
            
            if total_weight == 0:
                return None
            
            return weighted_sum / total_weight
            
        except Exception as e:
            logger.error(f"Failed to estimate task duration: {str(e)}")
            return None
    
    async def _find_similar_tasks(
        self,
        task: Task
    ) -> List[Task]:
        """Find similar completed tasks
        
        Args:
            task: Task to find similar tasks for
            
        Returns:
            List of similar tasks
        """
        try:
            similar_tasks = []
            
            # Get all completed tasks
            completed_tasks = [
                t for t in self.timeline.tasks.values()
                if t.status == TaskStatus.COMPLETED
            ]
            
            # Calculate similarity scores
            for completed_task in completed_tasks:
                similarity = await self._calculate_task_similarity(task, completed_task)
                if similarity > 0.5:  # Minimum similarity threshold
                    similar_tasks.append(completed_task)
            
            # Sort by similarity
            similar_tasks.sort(
                key=lambda t: self._calculate_task_similarity(task, t),
                reverse=True
            )
            
            return similar_tasks[:5]  # Return top 5 similar tasks
            
        except Exception as e:
            logger.error(f"Failed to find similar tasks: {str(e)}")
            return []
    
    async def _calculate_task_similarity(
        self,
        task1: Task,
        task2: Task
    ) -> float:
        """Calculate similarity between two tasks
        
        Args:
            task1: First task
            task2: Second task
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Calculate title similarity
            title_similarity = self._calculate_text_similarity(
                task1.title.lower(),
                task2.title.lower()
            )
            
            # Calculate description similarity
            desc_similarity = self._calculate_text_similarity(
                task1.description.lower(),
                task2.description.lower()
            )
            
            # Calculate tag similarity
            tag_similarity = len(task1.tags.intersection(task2.tags)) / len(task1.tags.union(task2.tags)) if task1.tags and task2.tags else 0.0
            
            # Calculate metadata similarity
            metadata_similarity = self._calculate_metadata_similarity(
                task1.metadata,
                task2.metadata
            )
            
            # Combine similarities with weights
            return (
                0.4 * title_similarity +
                0.3 * desc_similarity +
                0.2 * tag_similarity +
                0.1 * metadata_similarity
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate task similarity: {str(e)}")
            return 0.0
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Split into words
            words1 = set(text1.split())
            words2 = set(text2.split())
            
            # Calculate Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate text similarity: {str(e)}")
            return 0.0
    
    def _calculate_metadata_similarity(
        self,
        metadata1: Dict[str, Any],
        metadata2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between metadata dictionaries
        
        Args:
            metadata1: First metadata dictionary
            metadata2: Second metadata dictionary
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            if not metadata1 or not metadata2:
                return 0.0
            
            # Get common keys
            common_keys = set(metadata1.keys()).intersection(metadata2.keys())
            
            if not common_keys:
                return 0.0
            
            # Calculate value similarity for each common key
            similarities = []
            for key in common_keys:
                value1 = metadata1[key]
                value2 = metadata2[key]
                
                if isinstance(value1, str) and isinstance(value2, str):
                    similarities.append(self._calculate_text_similarity(value1, value2))
                elif isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                    # Normalize numeric values
                    max_val = max(abs(value1), abs(value2))
                    if max_val > 0:
                        similarities.append(1.0 - abs(value1 - value2) / max_val)
                    else:
                        similarities.append(1.0)
                else:
                    similarities.append(1.0 if value1 == value2 else 0.0)
            
            return sum(similarities) / len(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate metadata similarity: {str(e)}")
            return 0.0
    
    async def _load_timeline_data(self) -> None:
        """Load timeline data from database"""
        try:
            # Load timeline data
            timeline_data = await self.mongodb.get_document(
                "timelines",
                {"project_id": self.project_id}
            )
            
            if timeline_data:
                # Convert data to timeline objects
                self.timeline = self._deserialize_timeline(timeline_data)
            
        except Exception as e:
            logger.error(f"Failed to load timeline data: {str(e)}")
            raise
    
    async def _save_timeline_data(self) -> None:
        """Save timeline data to database"""
        try:
            # Convert timeline to dictionary
            timeline_data = self._serialize_timeline(self.timeline)
            
            # Save to database
            await self.mongodb.update_document(
                "timelines",
                {"project_id": self.project_id},
                timeline_data,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Failed to save timeline data: {str(e)}")
            raise
    
    def _serialize_timeline(self, timeline: ProjectTimeline) -> Dict[str, Any]:
        """Convert timeline to dictionary for storage
        
        Args:
            timeline: Timeline to serialize
            
        Returns:
            Dictionary representation
        """
        return {
            "project_id": timeline.project_id,
            "events": [
                {
                    "id": event.id,
                    "type": event.type.value,
                    "timestamp": event.timestamp.isoformat(),
                    "project_id": event.project_id,
                    "task_id": event.task_id,
                    "milestone_id": event.milestone_id,
                    "agent_id": event.agent_id,
                    "details": event.details,
                    "metadata": event.metadata
                }
                for event in timeline.events
            ],
            "tasks": {
                task_id: {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat(),
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "estimated_duration": str(task.estimated_duration) if task.estimated_duration else None,
                    "actual_duration": str(task.actual_duration) if task.actual_duration else None,
                    "dependencies": list(task.dependencies),
                    "assigned_to": task.assigned_to,
                    "priority": task.priority,
                    "tags": list(task.tags),
                    "metadata": task.metadata
                }
                for task_id, task in timeline.tasks.items()
            },
            "milestones": {
                milestone_id: {
                    "id": milestone.id,
                    "title": milestone.title,
                    "description": milestone.description,
                    "deadline": milestone.deadline.isoformat(),
                    "completed_at": milestone.completed_at.isoformat() if milestone.completed_at else None,
                    "tasks": list(milestone.tasks),
                    "dependencies": list(milestone.dependencies),
                    "metadata": milestone.metadata
                }
                for milestone_id, milestone in timeline.milestones.items()
            },
            "created_at": timeline.created_at.isoformat(),
            "updated_at": timeline.updated_at.isoformat(),
            "metadata": timeline.metadata
        }
    
    def _deserialize_timeline(self, data: Dict[str, Any]) -> ProjectTimeline:
        """Convert dictionary to timeline object
        
        Args:
            data: Dictionary representation
            
        Returns:
            Timeline object
        """
        return ProjectTimeline(
            project_id=data["project_id"],
            events=[
                TimelineEvent(
                    id=event["id"],
                    type=EventType(event["type"]),
                    timestamp=datetime.fromisoformat(event["timestamp"]),
                    project_id=event["project_id"],
                    task_id=event["task_id"],
                    milestone_id=event["milestone_id"],
                    agent_id=event["agent_id"],
                    details=event["details"],
                    metadata=event["metadata"]
                )
                for event in data["events"]
            ],
            tasks={
                task_id: Task(
                    id=task["id"],
                    title=task["title"],
                    description=task["description"],
                    status=TaskStatus(task["status"]),
                    created_at=datetime.fromisoformat(task["created_at"]),
                    started_at=datetime.fromisoformat(task["started_at"]) if task["started_at"] else None,
                    completed_at=datetime.fromisoformat(task["completed_at"]) if task["completed_at"] else None,
                    estimated_duration=timedelta.fromisoformat(task["estimated_duration"]) if task["estimated_duration"] else None,
                    actual_duration=timedelta.fromisoformat(task["actual_duration"]) if task["actual_duration"] else None,
                    dependencies=set(task["dependencies"]),
                    assigned_to=task["assigned_to"],
                    priority=task["priority"],
                    tags=set(task["tags"]),
                    metadata=task["metadata"]
                )
                for task_id, task in data["tasks"].items()
            },
            milestones={
                milestone_id: Milestone(
                    id=milestone["id"],
                    title=milestone["title"],
                    description=milestone["description"],
                    deadline=datetime.fromisoformat(milestone["deadline"]),
                    completed_at=datetime.fromisoformat(milestone["completed_at"]) if milestone["completed_at"] else None,
                    tasks=set(milestone["tasks"]),
                    dependencies=set(milestone["dependencies"]),
                    metadata=milestone["metadata"]
                )
                for milestone_id, milestone in data["milestones"].items()
            },
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data["metadata"]
        ) 