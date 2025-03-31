from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentRole:
    id: str
    title: str
    description: str
    capabilities: List[str]
    autonomy_level: int
    created_at: datetime
    updated_at: datetime

@dataclass
class TeamMember:
    id: str
    role_id: str
    name: str
    autonomy_level: int
    performance_metrics: Dict[str, float]
    joined_at: datetime

@dataclass
class Team:
    id: str
    name: str
    description: str
    members: List[TeamMember]
    created_at: datetime
    updated_at: datetime

class TeamManagementAPI:
    def __init__(self, project_store):
        self.project_store = project_store

    async def create_role(self, role_data: Dict[str, Any]) -> AgentRole:
        """Create a new agent role."""
        role = AgentRole(
            id=role_data['id'],
            title=role_data['title'],
            description=role_data['description'],
            capabilities=role_data['capabilities'],
            autonomy_level=role_data['autonomy_level'],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        await self.project_store.save_role(role)
        return role

    async def get_role(self, role_id: str) -> Optional[AgentRole]:
        """Retrieve an agent role by ID."""
        return await self.project_store.get_role(role_id)

    async def update_role(self, role_id: str, role_data: Dict[str, Any]) -> Optional[AgentRole]:
        """Update an existing agent role."""
        role = await self.get_role(role_id)
        if not role:
            return None

        for key, value in role_data.items():
            if hasattr(role, key):
                setattr(role, key, value)
        
        role.updated_at = datetime.now()
        await self.project_store.save_role(role)
        return role

    async def delete_role(self, role_id: str) -> bool:
        """Delete an agent role."""
        return await self.project_store.delete_role(role_id)

    async def create_team(self, team_data: Dict[str, Any]) -> Team:
        """Create a new team."""
        team = Team(
            id=team_data['id'],
            name=team_data['name'],
            description=team_data['description'],
            members=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        await self.project_store.save_team(team)
        return team

    async def get_team(self, team_id: str) -> Optional[Team]:
        """Retrieve a team by ID."""
        return await self.project_store.get_team(team_id)

    async def update_team(self, team_id: str, team_data: Dict[str, Any]) -> Optional[Team]:
        """Update an existing team."""
        team = await self.get_team(team_id)
        if not team:
            return None

        for key, value in team_data.items():
            if hasattr(team, key):
                setattr(team, key, value)
        
        team.updated_at = datetime.now()
        await self.project_store.save_team(team)
        return team

    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        return await self.project_store.delete_team(team_id)

    async def add_team_member(self, team_id: str, member_data: Dict[str, Any]) -> Optional[TeamMember]:
        """Add a new member to a team."""
        team = await self.get_team(team_id)
        if not team:
            return None

        member = TeamMember(
            id=member_data['id'],
            role_id=member_data['role_id'],
            name=member_data['name'],
            autonomy_level=member_data['autonomy_level'],
            performance_metrics=member_data.get('performance_metrics', {}),
            joined_at=datetime.now()
        )
        
        team.members.append(member)
        team.updated_at = datetime.now()
        await self.project_store.save_team(team)
        return member

    async def update_team_member(self, team_id: str, member_id: str, member_data: Dict[str, Any]) -> Optional[TeamMember]:
        """Update a team member's information."""
        team = await self.get_team(team_id)
        if not team:
            return None

        member = next((m for m in team.members if m.id == member_id), None)
        if not member:
            return None

        for key, value in member_data.items():
            if hasattr(member, key):
                setattr(member, key, value)

        team.updated_at = datetime.now()
        await self.project_store.save_team(team)
        return member

    async def remove_team_member(self, team_id: str, member_id: str) -> bool:
        """Remove a member from a team."""
        team = await self.get_team(team_id)
        if not team:
            return False

        team.members = [m for m in team.members if m.id != member_id]
        team.updated_at = datetime.now()
        await self.project_store.save_team(team)
        return True

    async def get_team_performance(self, team_id: str) -> Dict[str, Any]:
        """Calculate team performance metrics."""
        team = await self.get_team(team_id)
        if not team:
            return {}

        metrics = {
            'average_autonomy': sum(m.autonomy_level for m in team.members) / len(team.members),
            'member_count': len(team.members),
            'performance_scores': {}
        }

        for member in team.members:
            metrics['performance_scores'][member.id] = {
                'autonomy': member.autonomy_level,
                'metrics': member.performance_metrics
            }

        return metrics

    async def get_available_roles(self) -> List[AgentRole]:
        """Get all available agent roles."""
        return await self.project_store.get_all_roles()

    async def get_teams_by_role(self, role_id: str) -> List[Team]:
        """Get all teams that have members with a specific role."""
        teams = await self.project_store.get_all_teams()
        return [team for team in teams if any(m.role_id == role_id for m in team.members)]

    async def save_team_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a team composition as a template."""
        template = {
            'id': template_data['id'],
            'name': template_data['name'],
            'description': template_data['description'],
            'roles': template_data['roles'],
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        await self.project_store.save_team_template(template)
        return template

    async def load_team_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Load a team composition template."""
        return await self.project_store.get_team_template(template_id)

    async def get_all_team_templates(self) -> List[Dict[str, Any]]:
        """Get all available team composition templates."""
        return await self.project_store.get_all_team_templates() 