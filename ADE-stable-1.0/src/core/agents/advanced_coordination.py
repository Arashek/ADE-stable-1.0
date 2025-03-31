from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging
from enum import Enum
import heapq
from collections import defaultdict

logger = logging.getLogger(__name__)

class AgentRole(Enum):
    DEVELOPER = "developer"
    TESTER = "tester"
    REVIEWER = "reviewer"
    MANAGER = "manager"
    SPECIALIST = "specialist"

class ExpertiseLevel(Enum):
    BEGINNER = 1
    INTERMEDIATE = 2
    EXPERT = 3

@dataclass
class AgentCapability:
    name: str
    description: str
    expertise_level: ExpertiseLevel
    supported_roles: Set[AgentRole]
    performance_metrics: Dict[str, float] = None

@dataclass
class Task:
    id: str
    title: str
    description: str
    required_capabilities: Set[str]
    priority: int
    deadline: Optional[datetime]
    assigned_agents: Set[str] = None
    status: str = "pending"
    metrics: Dict[str, Any] = None

@dataclass
class AgentState:
    agent_id: str
    role: AgentRole
    capabilities: Dict[str, AgentCapability]
    current_tasks: List[Task]
    workload: float
    performance_metrics: Dict[str, float]
    collaboration_history: List[Dict[str, Any]]

class AdvancedAgentCoordinator:
    def __init__(self):
        self.agents: Dict[str, AgentState] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []
        self.coordination_lock = asyncio.Lock()
        self.performance_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.collaboration_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    async def register_agent(self, agent_id: str, role: AgentRole,
                           capabilities: List[AgentCapability]) -> bool:
        """Register a new agent with their role and capabilities."""
        try:
            agent_state = AgentState(
                agent_id=agent_id,
                role=role,
                capabilities={cap.name: cap for cap in capabilities},
                current_tasks=[],
                workload=0.0,
                performance_metrics={
                    "task_completion_rate": 0.0,
                    "collaboration_score": 0.0,
                    "efficiency": 0.0
                },
                collaboration_history=[]
            )
            self.agents[agent_id] = agent_state
            return True
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {str(e)}")
            return False
            
    async def create_task(self, task: Task) -> None:
        """Create a new task and dynamically allocate it to appropriate agents."""
        self.tasks[task.id] = task
        heapq.heappush(self.task_queue, (-task.priority, task))
        
        # Find suitable agents based on capabilities and workload
        suitable_agents = await self._find_suitable_agents(task)
        
        # Optimize agent selection based on collaboration patterns
        selected_agents = await self._optimize_agent_selection(task, suitable_agents)
        
        # Assign task to selected agents
        task.assigned_agents = selected_agents
        for agent_id in selected_agents:
            agent = self.agents[agent_id]
            agent.current_tasks.append(task)
            agent.workload += 1.0 / len(selected_agents)
            
        # Update collaboration patterns
        await self._update_collaboration_patterns(selected_agents)
        
    async def _find_suitable_agents(self, task: Task) -> Set[str]:
        """Find agents with required capabilities and reasonable workload."""
        suitable_agents = set()
        
        for agent_id, agent in self.agents.items():
            # Check capabilities
            has_capabilities = all(
                cap in agent.capabilities
                for cap in task.required_capabilities
            )
            
            # Check workload
            workload_ok = agent.workload < 0.8  # 80% threshold
            
            if has_capabilities and workload_ok:
                suitable_agents.add(agent_id)
                
        return suitable_agents
        
    async def _optimize_agent_selection(self, task: Task,
                                      suitable_agents: Set[str]) -> Set[str]:
        """Optimize agent selection based on collaboration patterns and performance."""
        if not suitable_agents:
            return set()
            
        # Calculate collaboration scores
        collaboration_scores = {}
        for agent_id in suitable_agents:
            agent = self.agents[agent_id]
            score = self._calculate_collaboration_score(agent, suitable_agents)
            collaboration_scores[agent_id] = score
            
        # Select agents with best collaboration scores
        selected_agents = set()
        max_agents = min(3, len(suitable_agents))  # Limit to 3 agents per task
        
        for agent_id, _ in sorted(
            collaboration_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:max_agents]:
            selected_agents.add(agent_id)
            
        return selected_agents
        
    def _calculate_collaboration_score(self, agent: AgentState,
                                     potential_collaborators: Set[str]) -> float:
        """Calculate collaboration score based on history and performance."""
        score = 0.0
        
        # Consider past collaborations
        for history in agent.collaboration_history:
            if history["agent_id"] in potential_collaborators:
                score += history["success_rate"] * 0.6
                
        # Consider performance metrics
        score += agent.performance_metrics["collaboration_score"] * 0.4
        
        return score
        
    async def _update_collaboration_patterns(self, agent_ids: Set[str]) -> None:
        """Update collaboration patterns based on agent interactions."""
        for i, agent_id1 in enumerate(agent_ids):
            for agent_id2 in list(agent_ids)[i+1:]:
                pattern_key = f"{agent_id1}_{agent_id2}"
                self.collaboration_patterns[pattern_key].append({
                    "timestamp": datetime.now(),
                    "task_count": 1,
                    "success_rate": 1.0
                })
                
                # Keep only recent patterns
                self.collaboration_patterns[pattern_key] = \
                    self.collaboration_patterns[pattern_key][-10:]
                    
    async def optimize_agent_specialization(self, agent_id: str) -> None:
        """Optimize agent specialization based on performance and task history."""
        agent = self.agents[agent_id]
        
        # Analyze task success patterns
        success_patterns = self._analyze_success_patterns(agent)
        
        # Update capabilities based on success patterns
        for capability_name, success_rate in success_patterns.items():
            if capability_name in agent.capabilities:
                capability = agent.capabilities[capability_name]
                if success_rate > 0.8:  # High success rate
                    capability.expertise_level = ExpertiseLevel.EXPERT
                elif success_rate > 0.6:  # Medium success rate
                    capability.expertise_level = ExpertiseLevel.INTERMEDIATE
                    
        # Update performance metrics
        agent.performance_metrics.update({
            "task_completion_rate": self._calculate_completion_rate(agent),
            "efficiency": self._calculate_efficiency(agent)
        })
        
    def _analyze_success_patterns(self, agent: AgentState) -> Dict[str, float]:
        """Analyze success patterns in agent's task history."""
        success_patterns = defaultdict(lambda: {"success": 0, "total": 0})
        
        for task in agent.current_tasks:
            if task.status == "completed":
                for capability in task.required_capabilities:
                    if capability in agent.capabilities:
                        success_patterns[capability]["success"] += 1
                        success_patterns[capability]["total"] += 1
                        
        return {
            cap: stats["success"] / stats["total"]
            for cap, stats in success_patterns.items()
            if stats["total"] > 0
        }
        
    def _calculate_completion_rate(self, agent: AgentState) -> float:
        """Calculate task completion rate for an agent."""
        completed = sum(1 for task in agent.current_tasks if task.status == "completed")
        total = len(agent.current_tasks)
        return completed / total if total > 0 else 0.0
        
    def _calculate_efficiency(self, agent: AgentState) -> float:
        """Calculate agent efficiency based on task completion and resource usage."""
        if not agent.current_tasks:
            return 0.0
            
        # Consider task completion rate
        completion_rate = self._calculate_completion_rate(agent)
        
        # Consider average task duration
        durations = [
            (task.metrics["end_time"] - task.metrics["start_time"]).total_seconds()
            for task in agent.current_tasks
            if task.status == "completed" and "start_time" in task.metrics
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Calculate efficiency score
        efficiency = completion_rate * (1.0 - min(avg_duration / 3600, 1.0))
        return efficiency
        
    async def get_coordination_metrics(self) -> Dict[str, Any]:
        """Get metrics about agent coordination and collaboration."""
        metrics = {
            "total_agents": len(self.agents),
            "active_tasks": len(self.tasks),
            "agent_workloads": {},
            "collaboration_patterns": {},
            "performance_metrics": {}
        }
        
        # Calculate agent workloads
        for agent_id, agent in self.agents.items():
            metrics["agent_workloads"][agent_id] = {
                "current_workload": agent.workload,
                "task_count": len(agent.current_tasks),
                "completion_rate": self._calculate_completion_rate(agent)
            }
            
        # Analyze collaboration patterns
        for pattern_key, history in self.collaboration_patterns.items():
            if history:
                latest = history[-1]
                metrics["collaboration_patterns"][pattern_key] = {
                    "success_rate": latest["success_rate"],
                    "task_count": latest["task_count"],
                    "last_updated": latest["timestamp"].isoformat()
                }
                
        # Aggregate performance metrics
        for agent_id, agent in self.agents.items():
            metrics["performance_metrics"][agent_id] = agent.performance_metrics
            
        return metrics 