from typing import Dict, Any, List, Optional, Set, Tuple
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

from .time_aware import TimeAwareProjectManager, TimelineEvent, Task, Milestone, EventType

logger = logging.getLogger(__name__)

@dataclass
class TimelineView:
    """Represents a filtered view of the timeline"""
    events: List[TimelineEvent]
    start_time: datetime
    end_time: datetime
    filters: Dict[str, Any]
    metadata: Dict[str, Any] = None

@dataclass
class DependencyGraph:
    """Represents task and milestone dependencies"""
    nodes: Dict[str, Dict[str, Any]]  # Task/Milestone nodes
    edges: Dict[str, List[Dict[str, Any]]]  # Dependency edges
    metadata: Dict[str, Any] = None

class TimelineTracker:
    """Handles timeline tracking and visualization"""
    
    def __init__(self, project_manager: TimeAwareProjectManager):
        self.project_manager = project_manager
    
    async def get_timeline_view(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_types: Optional[Set[EventType]] = None,
        task_ids: Optional[Set[str]] = None,
        milestone_ids: Optional[Set[str]] = None,
        agent_ids: Optional[Set[str]] = None
    ) -> TimelineView:
        """Get filtered view of timeline
        
        Args:
            start_time: Start time filter
            end_time: End time filter
            event_types: Set of event types to include
            task_ids: Set of task IDs to include
            milestone_ids: Set of milestone IDs to include
            agent_ids: Set of agent IDs to include
            
        Returns:
            Filtered timeline view
        """
        try:
            # Apply filters
            filtered_events = self.project_manager.timeline.events
            
            if start_time:
                filtered_events = [
                    e for e in filtered_events
                    if e.timestamp >= start_time
                ]
            
            if end_time:
                filtered_events = [
                    e for e in filtered_events
                    if e.timestamp <= end_time
                ]
            
            if event_types:
                filtered_events = [
                    e for e in filtered_events
                    if e.type in event_types
                ]
            
            if task_ids:
                filtered_events = [
                    e for e in filtered_events
                    if not e.task_id or e.task_id in task_ids
                ]
            
            if milestone_ids:
                filtered_events = [
                    e for e in filtered_events
                    if not e.milestone_id or e.milestone_id in milestone_ids
                ]
            
            if agent_ids:
                filtered_events = [
                    e for e in filtered_events
                    if not e.agent_id or e.agent_id in agent_ids
                ]
            
            # Sort events by timestamp
            filtered_events.sort(key=lambda e: e.timestamp)
            
            # Create view
            view = TimelineView(
                events=filtered_events,
                start_time=start_time or filtered_events[0].timestamp if filtered_events else datetime.now(),
                end_time=end_time or filtered_events[-1].timestamp if filtered_events else datetime.now(),
                filters={
                    "event_types": [t.value for t in event_types] if event_types else None,
                    "task_ids": list(task_ids) if task_ids else None,
                    "milestone_ids": list(milestone_ids) if milestone_ids else None,
                    "agent_ids": list(agent_ids) if agent_ids else None
                }
            )
            
            return view
            
        except Exception as e:
            logger.error(f"Failed to get timeline view: {str(e)}")
            raise
    
    async def get_dependency_graph(
        self,
        include_tasks: bool = True,
        include_milestones: bool = True
    ) -> DependencyGraph:
        """Get dependency graph of tasks and milestones
        
        Args:
            include_tasks: Whether to include tasks
            include_milestones: Whether to include milestones
            
        Returns:
            Dependency graph
        """
        try:
            nodes = {}
            edges = {}
            
            # Add tasks
            if include_tasks:
                for task_id, task in self.project_manager.timeline.tasks.items():
                    nodes[task_id] = {
                        "id": task_id,
                        "type": "task",
                        "title": task.title,
                        "status": task.status.value,
                        "created_at": task.created_at.isoformat(),
                        "started_at": task.started_at.isoformat() if task.started_at else None,
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                        "estimated_duration": str(task.estimated_duration) if task.estimated_duration else None,
                        "actual_duration": str(task.actual_duration) if task.actual_duration else None,
                        "assigned_to": task.assigned_to,
                        "priority": task.priority,
                        "tags": list(task.tags)
                    }
                    
                    # Add task dependencies
                    if task.dependencies:
                        edges[task_id] = [
                            {
                                "target": dep_id,
                                "type": "task_dependency",
                                "created_at": task.created_at.isoformat()
                            }
                            for dep_id in task.dependencies
                        ]
            
            # Add milestones
            if include_milestones:
                for milestone_id, milestone in self.project_manager.timeline.milestones.items():
                    nodes[milestone_id] = {
                        "id": milestone_id,
                        "type": "milestone",
                        "title": milestone.title,
                        "deadline": milestone.deadline.isoformat(),
                        "completed_at": milestone.completed_at.isoformat() if milestone.completed_at else None,
                        "tasks": list(milestone.tasks)
                    }
                    
                    # Add milestone dependencies
                    if milestone.dependencies:
                        edges[milestone_id] = [
                            {
                                "target": dep_id,
                                "type": "milestone_dependency",
                                "created_at": milestone.deadline.isoformat()
                            }
                            for dep_id in milestone.dependencies
                        ]
                    
                    # Add milestone-task dependencies
                    if milestone.tasks:
                        for task_id in milestone.tasks:
                            if task_id not in edges:
                                edges[task_id] = []
                            edges[task_id].append({
                                "target": milestone_id,
                                "type": "milestone_task",
                                "created_at": milestone.deadline.isoformat()
                            })
            
            return DependencyGraph(
                nodes=nodes,
                edges=edges,
                metadata={
                    "num_nodes": len(nodes),
                    "num_edges": sum(len(edge_list) for edge_list in edges.values()),
                    "num_tasks": len([n for n in nodes.values() if n["type"] == "task"]),
                    "num_milestones": len([n for n in nodes.values() if n["type"] == "milestone"])
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get dependency graph: {str(e)}")
            raise
    
    async def get_event_chain(
        self,
        event_id: str,
        max_depth: int = 5
    ) -> List[TimelineEvent]:
        """Get chain of related events
        
        Args:
            event_id: ID of starting event
            max_depth: Maximum depth of chain
            
        Returns:
            List of related events
        """
        try:
            # Find starting event
            start_event = None
            for event in self.project_manager.timeline.events:
                if event.id == event_id:
                    start_event = event
                    break
            
            if not start_event:
                raise ValueError(f"Event not found: {event_id}")
            
            # Build event chain
            chain = [start_event]
            current_depth = 0
            
            while current_depth < max_depth:
                current_depth += 1
                last_event = chain[-1]
                
                # Find related events
                related_events = []
                for event in self.project_manager.timeline.events:
                    if event.id not in [e.id for e in chain]:
                        if self._are_events_related(last_event, event):
                            related_events.append(event)
                
                if not related_events:
                    break
                
                # Add most relevant event
                chain.append(max(
                    related_events,
                    key=lambda e: self._calculate_event_relevance(last_event, e)
                ))
            
            return chain
            
        except Exception as e:
            logger.error(f"Failed to get event chain: {str(e)}")
            raise
    
    def _are_events_related(
        self,
        event1: TimelineEvent,
        event2: TimelineEvent
    ) -> bool:
        """Check if two events are related
        
        Args:
            event1: First event
            event2: Second event
            
        Returns:
            Whether events are related
        """
        try:
            # Check if events are for same task/milestone
            if event1.task_id and event2.task_id and event1.task_id == event2.task_id:
                return True
            if event1.milestone_id and event2.milestone_id and event1.milestone_id == event2.milestone_id:
                return True
            
            # Check if events are by same agent
            if event1.agent_id and event2.agent_id and event1.agent_id == event2.agent_id:
                return True
            
            # Check if events are close in time
            time_diff = abs((event1.timestamp - event2.timestamp).total_seconds())
            if time_diff < 3600:  # Within 1 hour
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check event relation: {str(e)}")
            return False
    
    def _calculate_event_relevance(
        self,
        event1: TimelineEvent,
        event2: TimelineEvent
    ) -> float:
        """Calculate relevance between two events
        
        Args:
            event1: First event
            event2: Second event
            
        Returns:
            Relevance score between 0 and 1
        """
        try:
            relevance = 0.0
            
            # Task/Milestone match
            if event1.task_id and event2.task_id and event1.task_id == event2.task_id:
                relevance += 0.4
            if event1.milestone_id and event2.milestone_id and event1.milestone_id == event2.milestone_id:
                relevance += 0.4
            
            # Agent match
            if event1.agent_id and event2.agent_id and event1.agent_id == event2.agent_id:
                relevance += 0.2
            
            # Time proximity
            time_diff = abs((event1.timestamp - event2.timestamp).total_seconds())
            if time_diff < 3600:  # Within 1 hour
                relevance += 0.4 * (1 - time_diff / 3600)
            
            return min(relevance, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate event relevance: {str(e)}")
            return 0.0
    
    async def get_task_history(
        self,
        task_id: str
    ) -> List[TimelineEvent]:
        """Get history of events for a task
        
        Args:
            task_id: Task ID
            
        Returns:
            List of task events
        """
        try:
            # Get all events for task
            task_events = [
                event for event in self.project_manager.timeline.events
                if event.task_id == task_id
            ]
            
            # Sort by timestamp
            task_events.sort(key=lambda e: e.timestamp)
            
            return task_events
            
        except Exception as e:
            logger.error(f"Failed to get task history: {str(e)}")
            raise
    
    async def get_milestone_history(
        self,
        milestone_id: str
    ) -> List[TimelineEvent]:
        """Get history of events for a milestone
        
        Args:
            milestone_id: Milestone ID
            
        Returns:
            List of milestone events
        """
        try:
            # Get all events for milestone
            milestone_events = [
                event for event in self.project_manager.timeline.events
                if event.milestone_id == milestone_id
            ]
            
            # Sort by timestamp
            milestone_events.sort(key=lambda e: e.timestamp)
            
            return milestone_events
            
        except Exception as e:
            logger.error(f"Failed to get milestone history: {str(e)}")
            raise
    
    async def get_agent_history(
        self,
        agent_id: str
    ) -> List[TimelineEvent]:
        """Get history of events for an agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            List of agent events
        """
        try:
            # Get all events for agent
            agent_events = [
                event for event in self.project_manager.timeline.events
                if event.agent_id == agent_id
            ]
            
            # Sort by timestamp
            agent_events.sort(key=lambda e: e.timestamp)
            
            return agent_events
            
        except Exception as e:
            logger.error(f"Failed to get agent history: {str(e)}")
            raise 