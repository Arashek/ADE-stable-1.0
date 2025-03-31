from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from enum import Enum
import logging
from datetime import datetime
import asyncio
from .reasoning import Plan, Subgoal, PlanStatus

logger = logging.getLogger(__name__)

class CollaborationStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentRole:
    agent_id: str
    role: str
    capabilities: Set[str]
    assigned_subgoals: List[str] = field(default_factory=list)
    status: str = "active"
    last_update: datetime = field(default_factory=datetime.now)

@dataclass
class Collaboration:
    collaboration_id: str
    plan_id: str
    agents: Dict[str, AgentRole]
    status: CollaborationStatus = CollaborationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    progress: Dict[str, float] = field(default_factory=dict)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)

class CollaborativePlanning:
    def __init__(self):
        self.active_collaborations: Dict[str, Collaboration] = {}
        self.collaboration_history: Dict[str, List[Collaboration]] = {}
        self._lock = asyncio.Lock()

    async def initiate_collaboration(self,
                                   plan_id: str,
                                   agents: Dict[str, Set[str]]) -> Optional[Collaboration]:
        """Initiate a collaborative planning session."""
        async with self._lock:
            # Generate collaboration ID
            collaboration_id = f"collab_{datetime.now().timestamp()}"

            # Create agent roles
            agent_roles = {}
            for agent_id, capabilities in agents.items():
                agent_roles[agent_id] = AgentRole(
                    agent_id=agent_id,
                    role=self._determine_role(capabilities),
                    capabilities=capabilities
                )

            # Create collaboration
            collaboration = Collaboration(
                collaboration_id=collaboration_id,
                plan_id=plan_id,
                agents=agent_roles,
                metadata={
                    "created_at": datetime.now().isoformat(),
                    "agent_count": len(agents)
                }
            )

            # Store collaboration
            self.active_collaborations[collaboration_id] = collaboration
            for agent_id in agents:
                if agent_id not in self.collaboration_history:
                    self.collaboration_history[agent_id] = []
                self.collaboration_history[agent_id].append(collaboration)

            return collaboration

    async def assign_roles(self,
                          collaboration_id: str,
                          plan: Plan) -> bool:
        """Assign roles and subgoals to agents based on capabilities."""
        if collaboration_id not in self.active_collaborations:
            return False

        collaboration = self.active_collaborations[collaboration_id]
        
        # Sort subgoals by priority and dependencies
        sorted_subgoals = self._sort_subgoals(plan.subgoals, plan.dependencies)
        
        # Assign subgoals to agents based on capabilities
        for subgoal in sorted_subgoals:
            assigned = False
            for agent_id, role in collaboration.agents.items():
                if (role.status == "active" and
                    subgoal.required_capabilities.issubset(role.capabilities)):
                    role.assigned_subgoals.append(subgoal.goal_id)
                    subgoal.assigned_agent = agent_id
                    assigned = True
                    break
            
            if not assigned:
                logger.warning(f"Could not assign subgoal {subgoal.goal_id} to any agent")
                return False

        collaboration.status = CollaborationStatus.ACTIVE
        return True

    async def update_progress(self,
                            collaboration_id: str,
                            agent_id: str,
                            subgoal_id: str,
                            progress: float) -> bool:
        """Update progress of a subgoal in the collaboration."""
        if collaboration_id not in self.active_collaborations:
            return False

        collaboration = self.active_collaborations[collaboration_id]
        
        if agent_id not in collaboration.agents:
            return False

        # Update agent's last update time
        collaboration.agents[agent_id].last_update = datetime.now()
        
        # Update progress
        collaboration.progress[subgoal_id] = progress
        
        # Check for conflicts
        await self._check_conflicts(collaboration)
        
        return True

    async def resolve_conflict(self,
                             collaboration_id: str,
                             conflict_id: str,
                             resolution: Dict[str, Any]) -> bool:
        """Resolve a conflict in the collaboration."""
        if collaboration_id not in self.active_collaborations:
            return False

        collaboration = self.active_collaborations[collaboration_id]
        
        # Find and update conflict
        for conflict in collaboration.conflicts:
            if conflict["id"] == conflict_id:
                conflict["resolution"] = resolution
                conflict["resolved_at"] = datetime.now().isoformat()
                return True
        
        return False

    async def synchronize_progress(self,
                                 collaboration_id: str) -> Dict[str, Any]:
        """Synchronize progress across all agents in the collaboration."""
        if collaboration_id not in self.active_collaborations:
            return {}

        collaboration = self.active_collaborations[collaboration_id]
        
        # Calculate overall progress
        total_subgoals = sum(len(role.assigned_subgoals) for role in collaboration.agents.values())
        completed_subgoals = sum(
            1 for subgoal_id, progress in collaboration.progress.items()
            if progress >= 1.0
        )
        
        overall_progress = completed_subgoals / total_subgoals if total_subgoals > 0 else 0
        
        # Check for stalled agents
        stalled_agents = [
            agent_id for agent_id, role in collaboration.agents.items()
            if (role.status == "active" and
                (datetime.now() - role.last_update).total_seconds() > 300)  # 5 minutes
        ]
        
        return {
            "overall_progress": overall_progress,
            "stalled_agents": stalled_agents,
            "active_agents": len([a for a in collaboration.agents.values() if a.status == "active"]),
            "conflicts": len([c for c in collaboration.conflicts if "resolution" not in c])
        }

    def _determine_role(self, capabilities: Set[str]) -> str:
        """Determine agent role based on capabilities."""
        if "planning" in capabilities and "coordination" in capabilities:
            return "coordinator"
        elif "planning" in capabilities:
            return "planner"
        elif "implementation" in capabilities:
            return "implementer"
        elif "review" in capabilities:
            return "reviewer"
        else:
            return "participant"

    def _sort_subgoals(self,
                      subgoals: List[Subgoal],
                      dependencies: Dict[str, Set[str]]) -> List[Subgoal]:
        """Sort subgoals by priority and dependencies."""
        # Create dependency graph
        graph = {sg.goal_id: set() for sg in subgoals}
        for sg in subgoals:
            graph[sg.goal_id] = dependencies.get(sg.goal_id, set())
        
        # Topological sort with priority consideration
        visited = set()
        sorted_subgoals = []
        
        def visit(goal_id: str, path: Set[str]):
            if goal_id in path:
                raise ValueError("Circular dependency detected")
            if goal_id in visited:
                return
            
            path.add(goal_id)
            for dep in graph[goal_id]:
                visit(dep, path)
            path.remove(goal_id)
            
            visited.add(goal_id)
            sorted_subgoals.append(
                next(sg for sg in subgoals if sg.goal_id == goal_id)
            )
        
        # Sort by priority first
        priority_sorted = sorted(subgoals, key=lambda x: x.priority)
        
        # Then apply topological sort
        for subgoal in priority_sorted:
            if subgoal.goal_id not in visited:
                visit(subgoal.goal_id, set())
        
        return sorted_subgoals

    async def _check_conflicts(self, collaboration: Collaboration) -> None:
        """Check for conflicts in the collaboration."""
        # Check for resource conflicts
        for agent_id, role in collaboration.agents.items():
            for subgoal_id in role.assigned_subgoals:
                # Check if another agent is working on the same subgoal
                for other_id, other_role in collaboration.agents.items():
                    if (other_id != agent_id and
                        subgoal_id in other_role.assigned_subgoals):
                        conflict = {
                            "id": f"conflict_{len(collaboration.conflicts)}",
                            "type": "resource_conflict",
                            "subgoal_id": subgoal_id,
                            "agents": [agent_id, other_id],
                            "timestamp": datetime.now().isoformat()
                        }
                        collaboration.conflicts.append(conflict)
                        logger.warning(f"Resource conflict detected: {conflict}")

        # Check for dependency conflicts
        for agent_id, role in collaboration.agents.items():
            for subgoal_id in role.assigned_subgoals:
                # Check if dependencies are satisfied
                for dep_id in collaboration.agents[agent_id].assigned_subgoals:
                    if dep_id in collaboration.progress:
                        if collaboration.progress[dep_id] < 1.0:
                            conflict = {
                                "id": f"conflict_{len(collaboration.conflicts)}",
                                "type": "dependency_conflict",
                                "subgoal_id": subgoal_id,
                                "dependency_id": dep_id,
                                "agent_id": agent_id,
                                "timestamp": datetime.now().isoformat()
                            }
                            collaboration.conflicts.append(conflict)
                            logger.warning(f"Dependency conflict detected: {conflict}") 