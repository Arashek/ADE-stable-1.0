from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import Enum
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

class GoalStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    ADAPTED = "adapted"

class GoalType(Enum):
    PROJECT = "project"
    MILESTONE = "milestone"
    TASK = "task"
    SUBTASK = "subtask"

@dataclass
class GoalMetrics:
    progress: float = 0.0
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    estimated_duration: float = 0.0
    actual_duration: Optional[float] = None
    confidence: float = 0.0
    risk_level: float = 0.0
    priority: int = 1
    dependencies_met: bool = False
    alignment_score: float = 0.0
    adaptation_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class Goal:
    goal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: GoalType = GoalType.TASK
    description: str = ""
    parent_id: Optional[str] = None
    subgoals: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    required_capabilities: Set[str] = field(default_factory=set)
    assigned_agents: Set[str] = field(default_factory=set)
    status: GoalStatus = GoalStatus.PENDING
    metrics: GoalMetrics = field(default_factory=GoalMetrics)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    user_intentions: List[str] = field(default_factory=list)
    alignment_checks: List[Dict[str, Any]] = field(default_factory=list)

class GoalManager:
    def __init__(self):
        self.goals: Dict[str, Goal] = {}
        self.goal_hierarchy: Dict[str, List[str]] = {}
        self.alignment_history: List[Dict[str, Any]] = []
        self.learning_data: Dict[str, List[Dict[str, Any]]] = {}
        
    async def create_goal(self, description: str, goal_type: GoalType,
                         parent_id: Optional[str] = None,
                         dependencies: Set[str] = None,
                         required_capabilities: Set[str] = None,
                         user_intentions: List[str] = None) -> Goal:
        """Create a new goal with hierarchical structure."""
        goal = Goal(
            description=description,
            type=goal_type,
            parent_id=parent_id,
            dependencies=dependencies or set(),
            required_capabilities=required_capabilities or set(),
            user_intentions=user_intentions or []
        )
        
        self.goals[goal.goal_id] = goal
        
        # Update hierarchy
        if parent_id:
            if parent_id not in self.goal_hierarchy:
                self.goal_hierarchy[parent_id] = []
            self.goal_hierarchy[parent_id].append(goal.goal_id)
        
        # Generate subgoals if needed
        if goal_type in [GoalType.PROJECT, GoalType.MILESTONE]:
            await self._generate_subgoals(goal)
        
        return goal
    
    async def _generate_subgoals(self, parent_goal: Goal) -> None:
        """Automatically generate subgoals based on goal type and description."""
        if parent_goal.type == GoalType.PROJECT:
            # Generate milestone subgoals
            milestones = [
                ("Planning Phase", "Define requirements and architecture"),
                ("Development Phase", "Implement core functionality"),
                ("Testing Phase", "Verify and validate implementation"),
                ("Deployment Phase", "Deploy and monitor system")
            ]
            
            for title, desc in milestones:
                milestone = await self.create_goal(
                    description=f"{title}: {desc}",
                    goal_type=GoalType.MILESTONE,
                    parent_id=parent_goal.goal_id
                )
                parent_goal.subgoals.append(milestone.goal_id)
        
        elif parent_goal.type == GoalType.MILESTONE:
            # Generate task subgoals based on milestone description
            tasks = [
                ("Analysis", "Analyze requirements and constraints"),
                ("Design", "Design solution architecture"),
                ("Implementation", "Implement required functionality"),
                ("Review", "Review and validate implementation")
            ]
            
            for title, desc in tasks:
                task = await self.create_goal(
                    description=f"{title}: {desc}",
                    goal_type=GoalType.TASK,
                    parent_id=parent_goal.goal_id
                )
                parent_goal.subgoals.append(task.goal_id)
    
    async def update_goal_progress(self, goal_id: str, progress: float,
                                 agent_id: str, context: Dict[str, Any] = None) -> bool:
        """Update goal progress and check alignment."""
        if goal_id not in self.goals:
            return False
        
        goal = self.goals[goal_id]
        goal.metrics.progress = progress
        goal.metrics.last_updated = datetime.now()
        goal.updated_at = datetime.now()
        
        # Check dependencies
        goal.metrics.dependencies_met = all(
            self.goals[dep_id].metrics.progress == 1.0
            for dep_id in goal.dependencies
        )
        
        # Update status based on progress
        if progress == 1.0:
            goal.status = GoalStatus.COMPLETED
            goal.metrics.completion_time = datetime.now()
            goal.metrics.actual_duration = (
                goal.metrics.completion_time - goal.metrics.start_time
            ).total_seconds()
        
        # Check alignment
        alignment_result = await self._check_goal_alignment(goal, agent_id, context)
        goal.alignment_checks.append(alignment_result)
        
        # Update parent goal progress
        if goal.parent_id:
            await self._update_parent_progress(goal.parent_id)
        
        return True
    
    async def _check_goal_alignment(self, goal: Goal, agent_id: str,
                                  context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Check if goal progress aligns with project objectives and user intentions."""
        alignment_result = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "alignment_score": 0.0,
            "issues": [],
            "suggestions": []
        }
        
        # Check against user intentions
        intention_alignment = await self._check_intention_alignment(goal)
        alignment_result["alignment_score"] += intention_alignment["score"]
        alignment_result["issues"].extend(intention_alignment["issues"])
        
        # Check against project objectives
        objective_alignment = await self._check_objective_alignment(goal, context)
        alignment_result["alignment_score"] += objective_alignment["score"]
        alignment_result["issues"].extend(objective_alignment["issues"])
        
        # Calculate final alignment score
        alignment_result["alignment_score"] /= 2
        
        # Store alignment check
        self.alignment_history.append(alignment_result)
        
        return alignment_result
    
    async def _check_intention_alignment(self, goal: Goal) -> Dict[str, Any]:
        """Check if goal aligns with user intentions."""
        result = {
            "score": 0.0,
            "issues": []
        }
        
        if not goal.user_intentions:
            result["issues"].append("No user intentions specified")
            return result
        
        # Analyze goal description against user intentions
        # This is a simplified version - in practice, you'd use NLP or similar
        intention_matches = sum(
            1 for intention in goal.user_intentions
            if intention.lower() in goal.description.lower()
        )
        
        result["score"] = intention_matches / len(goal.user_intentions)
        
        if result["score"] < 0.5:
            result["issues"].append("Goal may not fully align with user intentions")
        
        return result
    
    async def _check_objective_alignment(self, goal: Goal,
                                       context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Check if goal aligns with project objectives."""
        result = {
            "score": 0.0,
            "issues": []
        }
        
        # Check against project-level goals
        project_goal = await self._get_project_goal(goal)
        if not project_goal:
            result["issues"].append("No project-level goal found")
            return result
        
        # Analyze alignment with project objectives
        # This is a simplified version - in practice, you'd use more sophisticated analysis
        objective_matches = sum(
            1 for obj in project_goal.metadata.get("objectives", [])
            if obj.lower() in goal.description.lower()
        )
        
        result["score"] = objective_matches / len(project_goal.metadata.get("objectives", []))
        
        if result["score"] < 0.5:
            result["issues"].append("Goal may not fully align with project objectives")
        
        return result
    
    async def _get_project_goal(self, goal: Goal) -> Optional[Goal]:
        """Get the top-level project goal for a given goal."""
        current = goal
        while current.parent_id:
            current = self.goals[current.parent_id]
        return current if current.type == GoalType.PROJECT else None
    
    async def _update_parent_progress(self, parent_id: str) -> None:
        """Update parent goal progress based on subgoal progress."""
        if parent_id not in self.goals:
            return
        
        parent = self.goals[parent_id]
        if not parent.subgoals:
            return
        
        # Calculate average progress of subgoals
        total_progress = sum(
            self.goals[subgoal_id].metrics.progress
            for subgoal_id in parent.subgoals
        )
        parent.metrics.progress = total_progress / len(parent.subgoals)
        
        # Update parent status
        if parent.metrics.progress == 1.0:
            parent.status = GoalStatus.COMPLETED
        elif parent.metrics.progress > 0:
            parent.status = GoalStatus.IN_PROGRESS
        
        # Recursively update parent's parent
        if parent.parent_id:
            await self._update_parent_progress(parent.parent_id)
    
    async def adapt_goal(self, goal_id: str, changes: Dict[str, Any]) -> Optional[Goal]:
        """Adapt a goal based on changing requirements or issues."""
        if goal_id not in self.goals:
            return None
        
        goal = self.goals[goal_id]
        goal.metrics.adaptation_count += 1
        goal.status = GoalStatus.ADAPTED
        goal.updated_at = datetime.now()
        
        # Apply changes
        for key, value in changes.items():
            if hasattr(goal, key):
                setattr(goal, key, value)
            elif key in goal.metadata:
                goal.metadata[key] = value
        
        # Generate new subgoals if needed
        if goal.type in [GoalType.PROJECT, GoalType.MILESTONE]:
            await self._generate_subgoals(goal)
        
        # Store adaptation in learning data
        self.learning_data[goal_id] = self.learning_data.get(goal_id, [])
        self.learning_data[goal_id].append({
            "timestamp": datetime.now().isoformat(),
            "changes": changes,
            "reason": changes.get("reason", "Unknown")
        })
        
        return goal
    
    async def detect_unachievable_goals(self) -> List[Dict[str, Any]]:
        """Detect goals that may be unachievable based on current progress and constraints."""
        unachievable = []
        
        for goal_id, goal in self.goals.items():
            if goal.status == GoalStatus.FAILED:
                continue
            
            # Check for blocked dependencies
            if not goal.metrics.dependencies_met:
                unachievable.append({
                    "goal_id": goal_id,
                    "reason": "Blocked dependencies",
                    "blocked_by": [
                        dep_id for dep_id in goal.dependencies
                        if self.goals[dep_id].metrics.progress < 1.0
                    ]
                })
            
            # Check for time constraints
            if goal.metrics.estimated_duration > 0:
                elapsed = (datetime.now() - goal.metrics.start_time).total_seconds()
                if elapsed > goal.metrics.estimated_duration * 1.5:  # 50% over estimate
                    unachievable.append({
                        "goal_id": goal_id,
                        "reason": "Time exceeded",
                        "elapsed": elapsed,
                        "estimated": goal.metrics.estimated_duration
                    })
            
            # Check for resource constraints
            if goal.required_capabilities and not goal.assigned_agents:
                unachievable.append({
                    "goal_id": goal_id,
                    "reason": "Missing capabilities",
                    "required": goal.required_capabilities
                })
        
        return unachievable
    
    async def suggest_alternatives(self, goal_id: str) -> List[Dict[str, Any]]:
        """Suggest alternative approaches for a goal based on learning data."""
        if goal_id not in self.goals:
            return []
        
        goal = self.goals[goal_id]
        alternatives = []
        
        # Analyze learning data for similar situations
        similar_goals = [
            g for g in self.goals.values()
            if g.type == goal.type and g.goal_id != goal_id
        ]
        
        for similar_goal in similar_goals:
            if similar_goal.status == GoalStatus.COMPLETED:
                alternatives.append({
                    "goal_id": similar_goal.goal_id,
                    "description": similar_goal.description,
                    "success_rate": 1.0,
                    "approach": similar_goal.metadata.get("approach", "Unknown")
                })
        
        # Sort by success rate
        alternatives.sort(key=lambda x: x["success_rate"], reverse=True)
        
        return alternatives[:3]  # Return top 3 alternatives
    
    async def request_clarification(self, goal_id: str) -> List[str]:
        """Generate clarification requests for unclear goals."""
        if goal_id not in self.goals:
            return []
        
        goal = self.goals[goal_id]
        requests = []
        
        # Check for missing user intentions
        if not goal.user_intentions:
            requests.append("What are the key user intentions for this goal?")
        
        # Check for unclear dependencies
        if goal.dependencies:
            unclear_deps = [
                dep_id for dep_id in goal.dependencies
                if dep_id not in self.goals
            ]
            if unclear_deps:
                requests.append(f"Please clarify the following dependencies: {unclear_deps}")
        
        # Check for missing capabilities
        if goal.required_capabilities and not goal.assigned_agents:
            requests.append(
                f"Which agents have the required capabilities: {goal.required_capabilities}?"
            )
        
        # Check for alignment issues
        if goal.alignment_checks:
            latest_check = goal.alignment_checks[-1]
            if latest_check["alignment_score"] < 0.5:
                requests.append(
                    f"Please clarify how this goal aligns with project objectives: "
                    f"{latest_check['issues']}"
                )
        
        return requests 