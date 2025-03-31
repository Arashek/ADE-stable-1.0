from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import logging
import uuid
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)

class AgentRole(Enum):
    MANAGER = "manager"
    DEVELOPER = "developer"
    TESTER = "tester"
    ARCHITECT = "architect"
    OPERATIONS = "operations"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    UTILITY = "utility"

class ExpertiseLevel(Enum):
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"
    MASTER = "master"

class TeamStatus(Enum):
    FORMING = "forming"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    DISSOLVED = "dissolved"

@dataclass
class AgentCapability:
    name: str
    description: str
    expertise_level: ExpertiseLevel
    supported_roles: Set[AgentRole]
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    last_used: Optional[datetime] = None
    success_rate: float = 0.0

@dataclass
class AgentSpecialization:
    agent_id: str
    primary_role: AgentRole
    secondary_roles: Set[AgentRole] = field(default_factory=set)
    capabilities: Dict[str, AgentCapability] = field(default_factory=dict)
    expertise_levels: Dict[AgentRole, ExpertiseLevel] = field(default_factory=dict)
    current_team: Optional[str] = None
    workload: float = 0.0
    availability: bool = True
    adaptive_roles: Dict[str, float] = field(default_factory=dict)  # Role adaptation scores
    learning_rate: float = 0.1  # Rate at which agent adapts to new roles
    role_history: List[Dict[str, Any]] = field(default_factory=list)  # History of role adaptations
    
    def adapt_role(self, new_role: AgentRole, success_metric: float) -> None:
        """Adapt agent's role based on performance and success metrics."""
        # Update adaptation score for the role
        current_score = self.adaptive_roles.get(new_role.value, 0.0)
        new_score = current_score + (success_metric - current_score) * self.learning_rate
        self.adaptive_roles[new_role.value] = new_score
        
        # Record role adaptation
        self.role_history.append({
            "role": new_role.value,
            "success_metric": success_metric,
            "timestamp": datetime.now(),
            "new_score": new_score
        })
        
        # If adaptation score exceeds threshold, add as secondary role
        if new_score > 0.7 and new_role not in self.secondary_roles:
            self.secondary_roles.add(new_role)
            self.expertise_levels[new_role] = ExpertiseLevel.INTERMEDIATE
    
    def get_role_adaptation_score(self, role: AgentRole) -> float:
        """Get the adaptation score for a specific role."""
        return self.adaptive_roles.get(role.value, 0.0)
    
    def get_best_adapted_roles(self, min_score: float = 0.5) -> List[AgentRole]:
        """Get roles that the agent has successfully adapted to."""
        adapted_roles = []
        for role_value, score in self.adaptive_roles.items():
            if score >= min_score:
                adapted_roles.append(AgentRole(role_value))
        return sorted(adapted_roles, key=lambda x: self.adaptive_roles[x.value], reverse=True)

@dataclass
class TeamMember:
    agent_id: str
    role: AgentRole
    assigned_tasks: List[str] = field(default_factory=list)
    status: str = "active"
    contribution_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class Team:
    team_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    manager_id: str
    members: Dict[str, TeamMember] = field(default_factory=dict)
    required_roles: Set[AgentRole] = field(default_factory=set)
    status: TeamStatus = TeamStatus.FORMING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)

class AgentSpecializationManager:
    def __init__(self):
        self.agent_specializations: Dict[str, AgentSpecialization] = {}
        self.teams: Dict[str, Team] = {}
        self.role_capabilities: Dict[AgentRole, Set[str]] = defaultdict(set)
        self.task_requirements: Dict[str, Set[AgentRole]] = {}
        self.team_coordination: Dict[str, Dict[str, Any]] = {}
        self.cross_team_projects: Dict[str, Dict[str, Any]] = {}  # Track cross-team projects
        self.team_performance_history: Dict[str, List[Dict[str, Any]]] = {}  # Track team performance
        
    async def register_agent(self, agent_id: str, primary_role: AgentRole,
                           capabilities: List[AgentCapability]) -> bool:
        """Register an agent with their specialization and capabilities."""
        try:
            specialization = AgentSpecialization(
                agent_id=agent_id,
                primary_role=primary_role
            )
            
            # Register capabilities
            for capability in capabilities:
                specialization.capabilities[capability.name] = capability
                specialization.expertise_levels[primary_role] = capability.expertise_level
                
                # Update role capabilities mapping
                for role in capability.supported_roles:
                    self.role_capabilities[role].add(capability.name)
            
            self.agent_specializations[agent_id] = specialization
            return True
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {str(e)}")
            return False
    
    async def create_team(self, name: str, manager_id: str,
                         required_roles: Set[AgentRole]) -> Optional[Team]:
        """Create a new team with specified requirements."""
        if manager_id not in self.agent_specializations:
            return None
        
        manager = self.agent_specializations[manager_id]
        if manager.primary_role != AgentRole.MANAGER:
            return None
        
        team = Team(
            name=name,
            manager_id=manager_id,
            required_roles=required_roles
        )
        
        # Add manager to team
        team.members[manager_id] = TeamMember(
            agent_id=manager_id,
            role=AgentRole.MANAGER
        )
        
        self.teams[team.team_id] = team
        manager.current_team = team.team_id
        return team
    
    async def assign_agent_to_team(self, team_id: str, agent_id: str,
                                 role: AgentRole) -> bool:
        """Assign an agent to a team in a specific role."""
        if team_id not in self.teams or agent_id not in self.agent_specializations:
            return False
        
        team = self.teams[team_id]
        agent = self.agent_specializations[agent_id]
        
        # Check if agent has required capabilities
        if not self._has_required_capabilities(agent, role):
            return False
        
        # Check workload
        if agent.workload > 0.8:  # 80% threshold
            return False
        
        # Add agent to team
        team.members[agent_id] = TeamMember(
            agent_id=agent_id,
            role=role
        )
        
        agent.current_team = team_id
        agent.workload += 0.2  # Increment workload
        
        # Update team status if all required roles are filled
        if self._are_all_roles_filled(team):
            team.status = TeamStatus.ACTIVE
        
        return True
    
    async def find_specialist(self, required_role: AgentRole,
                            min_expertise: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE) -> List[str]:
        """Find agents specialized in a particular role with minimum expertise level."""
        specialists = []
        
        for agent_id, specialization in self.agent_specializations.items():
            if not specialization.availability:
                continue
            
            expertise = specialization.expertise_levels.get(required_role)
            if expertise and expertise.value >= min_expertise.value:
                specialists.append(agent_id)
        
        # Sort by expertise level and workload
        specialists.sort(
            key=lambda x: (
                self.agent_specializations[x].expertise_levels[required_role].value,
                -self.agent_specializations[x].workload
            ),
            reverse=True
        )
        
        return specialists
    
    async def optimize_team_configuration(self, team_id: str) -> bool:
        """Optimize team configuration based on performance metrics."""
        if team_id not in self.teams:
            return False
        
        team = self.teams[team_id]
        
        # Calculate team performance metrics
        team.performance_metrics = self._calculate_team_metrics(team)
        
        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(team)
        
        # Optimize resource allocation
        for member_id, member in team.members.items():
            if member_id in bottlenecks:
                # Adjust workload or find additional resources
                await self._optimize_member_workload(team, member_id)
        
        return True
    
    async def coordinate_teams(self, team_ids: List[str]) -> Dict[str, Any]:
        """Coordinate multiple teams working on related tasks."""
        coordination_data = {
            "resource_sharing": {},
            "priorities": {},
            "conflicts": [],
            "progress": {}
        }
        
        # Analyze resource usage
        for team_id in team_ids:
            team = self.teams[team_id]
            coordination_data["resource_sharing"][team_id] = self._analyze_resource_usage(team)
        
        # Negotiate priorities
        coordination_data["priorities"] = await self._negotiate_priorities(team_ids)
        
        # Detect and resolve conflicts
        coordination_data["conflicts"] = await self._detect_conflicts(team_ids)
        
        # Track global progress
        coordination_data["progress"] = self._track_global_progress(team_ids)
        
        return coordination_data
    
    async def dissolve_team(self, team_id: str) -> bool:
        """Dissolve a team and reclaim resources."""
        if team_id not in self.teams:
            return False
        
        team = self.teams[team_id]
        
        # Update agent statuses
        for member_id in team.members:
            agent = self.agent_specializations[member_id]
            agent.current_team = None
            agent.workload = max(0.0, agent.workload - 0.2)
        
        # Update team status
        team.status = TeamStatus.DISSOLVED
        team.completed_at = datetime.now()
        
        return True
    
    def _has_required_capabilities(self, agent: AgentSpecialization,
                                 role: AgentRole) -> bool:
        """Check if agent has required capabilities for a role."""
        required_capabilities = self.role_capabilities[role]
        agent_capabilities = {cap.name for cap in agent.capabilities.values()}
        return required_capabilities.issubset(agent_capabilities)
    
    def _are_all_roles_filled(self, team: Team) -> bool:
        """Check if all required roles are filled in the team."""
        filled_roles = {member.role for member in team.members.values()}
        return team.required_roles.issubset(filled_roles)
    
    def _calculate_team_metrics(self, team: Team) -> Dict[str, float]:
        """Calculate team performance metrics."""
        metrics = {
            "efficiency": 0.0,
            "coordination": 0.0,
            "resource_utilization": 0.0
        }
        
        # Calculate efficiency based on task completion
        total_tasks = sum(len(member.assigned_tasks) for member in team.members.values())
        completed_tasks = sum(
            len([t for t in member.assigned_tasks if t.endswith("_completed")])
            for member in team.members.values()
        )
        metrics["efficiency"] = completed_tasks / total_tasks if total_tasks > 0 else 0.0
        
        # Calculate coordination score
        coordination_scores = []
        for member in team.members.values():
            if member.contribution_metrics:
                coordination_scores.append(
                    member.contribution_metrics.get("coordination", 0.0)
                )
        metrics["coordination"] = sum(coordination_scores) / len(coordination_scores) if coordination_scores else 0.0
        
        # Calculate resource utilization
        total_resources = sum(team.resource_usage.values())
        metrics["resource_utilization"] = total_resources / len(team.members) if team.members else 0.0
        
        return metrics
    
    def _identify_bottlenecks(self, team: Team) -> Set[str]:
        """Identify team members causing bottlenecks."""
        bottlenecks = set()
        
        for member_id, member in team.members.items():
            # Check task completion rate
            total_tasks = len(member.assigned_tasks)
            completed_tasks = len([t for t in member.assigned_tasks if t.endswith("_completed")])
            completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0.0
            
            # Check contribution metrics
            contribution = member.contribution_metrics.get("efficiency", 0.0)
            
            if completion_rate < 0.7 or contribution < 0.6:
                bottlenecks.add(member_id)
        
        return bottlenecks
    
    async def _optimize_member_workload(self, team: Team, member_id: str) -> None:
        """Optimize workload for a team member."""
        member = team.members[member_id]
        agent = self.agent_specializations[member_id]
        
        # Find potential helpers
        helpers = await self.find_specialist(
            member.role,
            min_expertise=ExpertiseLevel.INTERMEDIATE
        )
        
        # Redistribute tasks if possible
        if helpers:
            # Implementation of task redistribution logic
            pass
    
    def _analyze_resource_usage(self, team: Team) -> Dict[str, float]:
        """Analyze resource usage for a team."""
        return {
            "cpu_usage": sum(
                member.contribution_metrics.get("cpu_usage", 0.0)
                for member in team.members.values()
            ) / len(team.members),
            "memory_usage": sum(
                member.contribution_metrics.get("memory_usage", 0.0)
                for member in team.members.values()
            ) / len(team.members),
            "network_usage": sum(
                member.contribution_metrics.get("network_usage", 0.0)
                for member in team.members.values()
            ) / len(team.members)
        }
    
    async def _negotiate_priorities(self, team_ids: List[str]) -> Dict[str, int]:
        """Negotiate priorities between teams."""
        priorities = {}
        
        for team_id in team_ids:
            team = self.teams[team_id]
            
            # Calculate priority based on various factors
            priority_score = 0
            
            # Factor 1: Team progress (40%)
            progress = team.performance_metrics.get("efficiency", 0.0)
            priority_score += progress * 40
            
            # Factor 2: Resource utilization (30%)
            utilization = team.performance_metrics.get("resource_utilization", 0.0)
            priority_score += utilization * 30
            
            # Factor 3: Dependencies (30%)
            dependencies = len(self.team_coordination.get(team_id, {}).get("dependencies", []))
            priority_score += (1.0 - min(dependencies / 5, 1.0)) * 30
            
            priorities[team_id] = int(priority_score)
        
        return priorities
    
    async def _detect_conflicts(self, team_ids: List[str]) -> List[Dict[str, Any]]:
        """Detect conflicts between teams."""
        conflicts = []
        
        for i, team_id1 in enumerate(team_ids):
            for team_id2 in team_ids[i+1:]:
                team1 = self.teams[team_id1]
                team2 = self.teams[team_id2]
                
                # Check resource conflicts
                resource_conflicts = self._check_resource_conflicts(team1, team2)
                if resource_conflicts:
                    conflicts.append({
                        "type": "resource",
                        "teams": [team_id1, team_id2],
                        "details": resource_conflicts
                    })
                
                # Check dependency conflicts
                dependency_conflicts = self._check_dependency_conflicts(team1, team2)
                if dependency_conflicts:
                    conflicts.append({
                        "type": "dependency",
                        "teams": [team_id1, team_id2],
                        "details": dependency_conflicts
                    })
        
        return conflicts
    
    def _check_resource_conflicts(self, team1: Team, team2: Team) -> List[str]:
        """Check for resource conflicts between teams."""
        conflicts = []
        
        # Compare resource usage
        for resource, usage1 in team1.resource_usage.items():
            if resource in team2.resource_usage:
                usage2 = team2.resource_usage[resource]
                if usage1 + usage2 > 0.8:  # 80% threshold
                    conflicts.append(f"High {resource} usage: {usage1 + usage2:.2f}")
        
        return conflicts
    
    def _check_dependency_conflicts(self, team1: Team, team2: Team) -> List[str]:
        """Check for dependency conflicts between teams."""
        conflicts = []
        
        # Check circular dependencies
        if team1.team_id in self.team_coordination.get(team2.team_id, {}).get("dependencies", []) and \
           team2.team_id in self.team_coordination.get(team1.team_id, {}).get("dependencies", []):
            conflicts.append("Circular dependency detected")
        
        return conflicts
    
    def _track_global_progress(self, team_ids: List[str]) -> Dict[str, float]:
        """Track global progress across teams."""
        progress = {
            "overall": 0.0,
            "by_team": {},
            "by_role": defaultdict(float)
        }
        
        total_teams = len(team_ids)
        total_progress = 0.0
        
        for team_id in team_ids:
            team = self.teams[team_id]
            team_progress = team.performance_metrics.get("efficiency", 0.0)
            
            progress["by_team"][team_id] = team_progress
            total_progress += team_progress
            
            # Track progress by role
            for member in team.members.values():
                role_progress = member.contribution_metrics.get("efficiency", 0.0)
                progress["by_role"][member.role] += role_progress
        
        progress["overall"] = total_progress / total_teams if total_teams > 0 else 0.0
        
        return progress
    
    async def create_cross_team_project(self, project_id: str, team_ids: List[str],
                                      project_requirements: Dict[str, Any]) -> bool:
        """Create a project that requires coordination between multiple teams."""
        try:
            # Validate teams exist
            for team_id in team_ids:
                if team_id not in self.teams:
                    return False
            
            # Create cross-team project
            self.cross_team_projects[project_id] = {
                "team_ids": team_ids,
                "requirements": project_requirements,
                "status": "active",
                "created_at": datetime.now(),
                "coordination_data": {
                    "resource_sharing": {},
                    "dependencies": {},
                    "milestones": [],
                    "progress": {}
                }
            }
            
            # Initialize coordination data
            for team_id in team_ids:
                self.cross_team_projects[project_id]["coordination_data"]["progress"][team_id] = {
                    "completed_tasks": 0,
                    "total_tasks": 0,
                    "blockers": []
                }
            
            return True
        except Exception as e:
            logger.error(f"Failed to create cross-team project: {str(e)}")
            return False
    
    async def optimize_team_composition(self, team_id: str) -> bool:
        """Optimize team composition based on performance metrics and role adaptation."""
        if team_id not in self.teams:
            return False
        
        team = self.teams[team_id]
        
        # Get team performance history
        performance_history = self.team_performance_history.get(team_id, [])
        if not performance_history:
            return False
        
        # Analyze performance patterns
        performance_patterns = self._analyze_performance_patterns(performance_history)
        
        # Identify roles that need strengthening
        weak_roles = self._identify_weak_roles(team, performance_patterns)
        
        # Find agents with high adaptation scores for weak roles
        for role in weak_roles:
            potential_agents = await self.find_specialist(role, min_expertise=ExpertiseLevel.INTERMEDIATE)
            
            # Sort by adaptation score
            potential_agents.sort(
                key=lambda x: self.agent_specializations[x].get_role_adaptation_score(role),
                reverse=True
            )
            
            # Assign best matching agent if available
            if potential_agents:
                await self.assign_agent_to_team(team_id, potential_agents[0], role)
        
        return True
    
    async def coordinate_cross_team_project(self, project_id: str) -> Dict[str, Any]:
        """Coordinate activities between teams in a cross-team project."""
        if project_id not in self.cross_team_projects:
            return {"error": "Project not found"}
        
        project = self.cross_team_projects[project_id]
        coordination_data = project["coordination_data"]
        
        # Update resource sharing
        for team_id in project["team_ids"]:
            team = self.teams[team_id]
            coordination_data["resource_sharing"][team_id] = self._analyze_resource_usage(team)
        
        # Update dependencies
        coordination_data["dependencies"] = await self._analyze_cross_team_dependencies(project)
        
        # Update progress
        for team_id in project["team_ids"]:
            team = self.teams[team_id]
            coordination_data["progress"][team_id].update({
                "completed_tasks": len([t for t in team.tasks if t.status == "completed"]),
                "total_tasks": len(team.tasks),
                "blockers": self._identify_blockers(team)
            })
        
        # Check for project completion
        if self._is_project_completed(project):
            project["status"] = "completed"
            project["completed_at"] = datetime.now()
        
        return coordination_data
    
    def _analyze_performance_patterns(self, performance_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze team performance patterns to identify areas for improvement."""
        patterns = {
            "role_performance": {},
            "task_completion": {},
            "bottlenecks": []
        }
        
        # Analyze role performance
        for entry in performance_history:
            for role, metrics in entry.get("role_metrics", {}).items():
                if role not in patterns["role_performance"]:
                    patterns["role_performance"][role] = []
                patterns["role_performance"][role].append(metrics)
        
        # Calculate average performance per role
        for role, metrics_list in patterns["role_performance"].items():
            patterns["role_performance"][role] = {
                "average_efficiency": sum(m.get("efficiency", 0) for m in metrics_list) / len(metrics_list),
                "average_quality": sum(m.get("quality", 0) for m in metrics_list) / len(metrics_list),
                "trend": self._calculate_trend(metrics_list)
            }
        
        return patterns
    
    def _identify_weak_roles(self, team: Team, patterns: Dict[str, Any]) -> List[AgentRole]:
        """Identify roles that need strengthening based on performance patterns."""
        weak_roles = []
        
        for role, metrics in patterns["role_performance"].items():
            if (metrics["average_efficiency"] < 0.7 or
                metrics["average_quality"] < 0.7 or
                metrics["trend"] < 0):
                weak_roles.append(AgentRole(role))
        
        return weak_roles
    
    def _calculate_trend(self, metrics_list: List[Dict[str, Any]]) -> float:
        """Calculate the trend of performance metrics over time."""
        if len(metrics_list) < 2:
            return 0.0
        
        # Calculate simple linear regression
        x = range(len(metrics_list))
        y = [m.get("efficiency", 0) for m in metrics_list]
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_xx = sum(x[i] * x[i] for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        return slope
    
    def _is_project_completed(self, project: Dict[str, Any]) -> bool:
        """Check if all teams have completed their tasks in the project."""
        progress = project["coordination_data"]["progress"]
        return all(
            team_progress["completed_tasks"] == team_progress["total_tasks"]
            for team_progress in progress.values()
        )
    
    def _analyze_cross_team_dependencies(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cross-team dependencies for a project."""
        dependencies = {}
        
        for team_id in project["team_ids"]:
            team = self.teams[team_id]
            dependencies[team_id] = self._identify_dependencies(team)
        
        return dependencies
    
    def _identify_dependencies(self, team: Team) -> List[str]:
        """Identify dependencies for a team."""
        dependencies = []
        
        for member_id, member in team.members.items():
            for role in member.role.value:
                if role in self.role_capabilities:
                    for other_team_id, other_member in team.members.items():
                        if other_member.role.value in self.role_capabilities[role]:
                            dependencies.append(f"{member.role.value} -> {other_member.role.value}")
        
        return dependencies
    
    def _identify_blockers(self, team: Team) -> List[str]:
        """Identify blockers for a team."""
        blockers = []
        
        for member_id, member in team.members.items():
            if member.status == "blocked":
                blockers.append(f"{member.role.value} is blocked")
        
        return blockers 