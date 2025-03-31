import pytest
import asyncio
from datetime import datetime
from production.src.core.agent_specialization import (
    AgentSpecializationManager, AgentRole, ExpertiseLevel, TeamStatus,
    AgentCapability, AgentSpecialization, TeamMember, Team
)

@pytest.fixture
async def specialization_manager():
    manager = AgentSpecializationManager()
    yield manager

@pytest.fixture
def sample_capabilities():
    return [
        AgentCapability(
            name="code_analysis",
            description="Analyzes code for potential issues",
            expertise_level=ExpertiseLevel.EXPERT,
            supported_roles={AgentRole.DEVELOPER, AgentRole.ARCHITECT}
        ),
        AgentCapability(
            name="test_execution",
            description="Executes test suites",
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            supported_roles={AgentRole.TESTER}
        )
    ]

@pytest.mark.asyncio
async def test_agent_registration(specialization_manager, sample_capabilities):
    """Test agent registration with capabilities."""
    success = await specialization_manager.register_agent(
        agent_id="agent1",
        primary_role=AgentRole.DEVELOPER,
        capabilities=sample_capabilities
    )
    
    assert success is True
    assert "agent1" in specialization_manager.agent_specializations
    
    agent = specialization_manager.agent_specializations["agent1"]
    assert agent.primary_role == AgentRole.DEVELOPER
    assert len(agent.capabilities) == 2
    assert "code_analysis" in agent.capabilities
    assert "test_execution" in agent.capabilities

@pytest.mark.asyncio
async def test_team_creation(specialization_manager, sample_capabilities):
    """Test team creation and management."""
    # Register manager agent
    await specialization_manager.register_agent(
        agent_id="manager1",
        primary_role=AgentRole.MANAGER,
        capabilities=[
            AgentCapability(
                name="team_management",
                description="Manages team activities",
                expertise_level=ExpertiseLevel.EXPERT,
                supported_roles={AgentRole.MANAGER}
            )
        ]
    )
    
    # Create team
    team = await specialization_manager.create_team(
        name="Development Team",
        manager_id="manager1",
        required_roles={AgentRole.DEVELOPER, AgentRole.TESTER}
    )
    
    assert team is not None
    assert team.name == "Development Team"
    assert team.manager_id == "manager1"
    assert team.status == TeamStatus.FORMING
    assert len(team.members) == 1
    assert team.members["manager1"].role == AgentRole.MANAGER

@pytest.mark.asyncio
async def test_agent_assignment(specialization_manager, sample_capabilities):
    """Test agent assignment to teams."""
    # Register agents
    await specialization_manager.register_agent(
        agent_id="manager1",
        primary_role=AgentRole.MANAGER,
        capabilities=[
            AgentCapability(
                name="team_management",
                description="Manages team activities",
                expertise_level=ExpertiseLevel.EXPERT,
                supported_roles={AgentRole.MANAGER}
            )
        ]
    )
    
    await specialization_manager.register_agent(
        agent_id="dev1",
        primary_role=AgentRole.DEVELOPER,
        capabilities=sample_capabilities
    )
    
    # Create team
    team = await specialization_manager.create_team(
        name="Development Team",
        manager_id="manager1",
        required_roles={AgentRole.DEVELOPER, AgentRole.TESTER}
    )
    
    # Assign developer to team
    success = await specialization_manager.assign_agent_to_team(
        team_id=team.team_id,
        agent_id="dev1",
        role=AgentRole.DEVELOPER
    )
    
    assert success is True
    assert "dev1" in team.members
    assert team.members["dev1"].role == AgentRole.DEVELOPER
    assert specialization_manager.agent_specializations["dev1"].current_team == team.team_id

@pytest.mark.asyncio
async def test_specialist_finding(specialization_manager, sample_capabilities):
    """Test finding specialists for specific roles."""
    # Register multiple agents with different expertise levels
    await specialization_manager.register_agent(
        agent_id="dev1",
        primary_role=AgentRole.DEVELOPER,
        capabilities=[
            AgentCapability(
                name="code_analysis",
                description="Analyzes code for potential issues",
                expertise_level=ExpertiseLevel.EXPERT,
                supported_roles={AgentRole.DEVELOPER}
            )
        ]
    )
    
    await specialization_manager.register_agent(
        agent_id="dev2",
        primary_role=AgentRole.DEVELOPER,
        capabilities=[
            AgentCapability(
                name="code_analysis",
                description="Analyzes code for potential issues",
                expertise_level=ExpertiseLevel.INTERMEDIATE,
                supported_roles={AgentRole.DEVELOPER}
            )
        ]
    )
    
    # Find specialists
    specialists = await specialization_manager.find_specialist(
        required_role=AgentRole.DEVELOPER,
        min_expertise=ExpertiseLevel.INTERMEDIATE
    )
    
    assert len(specialists) == 2
    assert specialists[0] == "dev1"  # Expert should be first
    assert specialists[1] == "dev2"  # Intermediate should be second

@pytest.mark.asyncio
async def test_team_optimization(specialization_manager, sample_capabilities):
    """Test team configuration optimization."""
    # Register agents
    await specialization_manager.register_agent(
        agent_id="manager1",
        primary_role=AgentRole.MANAGER,
        capabilities=[
            AgentCapability(
                name="team_management",
                description="Manages team activities",
                expertise_level=ExpertiseLevel.EXPERT,
                supported_roles={AgentRole.MANAGER}
            )
        ]
    )
    
    await specialization_manager.register_agent(
        agent_id="dev1",
        primary_role=AgentRole.DEVELOPER,
        capabilities=sample_capabilities
    )
    
    # Create and populate team
    team = await specialization_manager.create_team(
        name="Development Team",
        manager_id="manager1",
        required_roles={AgentRole.DEVELOPER}
    )
    
    await specialization_manager.assign_agent_to_team(
        team_id=team.team_id,
        agent_id="dev1",
        role=AgentRole.DEVELOPER
    )
    
    # Add some metrics
    team.members["dev1"].contribution_metrics = {
        "efficiency": 0.8,
        "coordination": 0.7
    }
    
    # Optimize team
    success = await specialization_manager.optimize_team_configuration(team.team_id)
    
    assert success is True
    assert "efficiency" in team.performance_metrics
    assert "coordination" in team.performance_metrics
    assert "resource_utilization" in team.performance_metrics

@pytest.mark.asyncio
async def test_team_coordination(specialization_manager, sample_capabilities):
    """Test coordination between multiple teams."""
    # Register agents
    await specialization_manager.register_agent(
        agent_id="manager1",
        primary_role=AgentRole.MANAGER,
        capabilities=[
            AgentCapability(
                name="team_management",
                description="Manages team activities",
                expertise_level=ExpertiseLevel.EXPERT,
                supported_roles={AgentRole.MANAGER}
            )
        ]
    )
    
    await specialization_manager.register_agent(
        agent_id="dev1",
        primary_role=AgentRole.DEVELOPER,
        capabilities=sample_capabilities
    )
    
    # Create two teams
    team1 = await specialization_manager.create_team(
        name="Frontend Team",
        manager_id="manager1",
        required_roles={AgentRole.DEVELOPER}
    )
    
    team2 = await specialization_manager.create_team(
        name="Backend Team",
        manager_id="manager1",
        required_roles={AgentRole.DEVELOPER}
    )
    
    # Assign developer to both teams
    await specialization_manager.assign_agent_to_team(
        team_id=team1.team_id,
        agent_id="dev1",
        role=AgentRole.DEVELOPER
    )
    
    await specialization_manager.assign_agent_to_team(
        team_id=team2.team_id,
        agent_id="dev1",
        role=AgentRole.DEVELOPER
    )
    
    # Add some metrics
    team1.performance_metrics = {"efficiency": 0.8, "resource_utilization": 0.6}
    team2.performance_metrics = {"efficiency": 0.7, "resource_utilization": 0.5}
    
    # Coordinate teams
    coordination_data = await specialization_manager.coordinate_teams(
        [team1.team_id, team2.team_id]
    )
    
    assert "resource_sharing" in coordination_data
    assert "priorities" in coordination_data
    assert "conflicts" in coordination_data
    assert "progress" in coordination_data
    assert len(coordination_data["conflicts"]) > 0  # Should detect resource conflict

@pytest.mark.asyncio
async def test_team_dissolution(specialization_manager, sample_capabilities):
    """Test team dissolution and resource reclamation."""
    # Register agents
    await specialization_manager.register_agent(
        agent_id="manager1",
        primary_role=AgentRole.MANAGER,
        capabilities=[
            AgentCapability(
                name="team_management",
                description="Manages team activities",
                expertise_level=ExpertiseLevel.EXPERT,
                supported_roles={AgentRole.MANAGER}
            )
        ]
    )
    
    await specialization_manager.register_agent(
        agent_id="dev1",
        primary_role=AgentRole.DEVELOPER,
        capabilities=sample_capabilities
    )
    
    # Create and populate team
    team = await specialization_manager.create_team(
        name="Development Team",
        manager_id="manager1",
        required_roles={AgentRole.DEVELOPER}
    )
    
    await specialization_manager.assign_agent_to_team(
        team_id=team.team_id,
        agent_id="dev1",
        role=AgentRole.DEVELOPER
    )
    
    # Dissolve team
    success = await specialization_manager.dissolve_team(team.team_id)
    
    assert success is True
    assert team.status == TeamStatus.DISSOLVED
    assert team.completed_at is not None
    assert specialization_manager.agent_specializations["dev1"].current_team is None
    assert specialization_manager.agent_specializations["dev1"].workload == 0.0 