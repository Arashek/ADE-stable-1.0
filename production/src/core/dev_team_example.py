import asyncio
from typing import Dict, Any, List
from .agent_specialization import (
    AgentSpecializationManager, AgentRole, ExpertiseLevel,
    AgentCapability, Team
)

class DevelopmentTeamExample:
    def __init__(self):
        self.specialization_manager = AgentSpecializationManager()
        self._register_agents()
    
    async def _register_agents(self):
        """Register various specialized agents."""
        # Register Manager
        await self.specialization_manager.register_agent(
            agent_id="manager1",
            primary_role=AgentRole.MANAGER,
            capabilities=[
                AgentCapability(
                    name="team_management",
                    description="Manages team activities and coordination",
                    expertise_level=ExpertiseLevel.EXPERT,
                    supported_roles={AgentRole.MANAGER}
                ),
                AgentCapability(
                    name="resource_allocation",
                    description="Allocates and optimizes team resources",
                    expertise_level=ExpertiseLevel.EXPERT,
                    supported_roles={AgentRole.MANAGER}
                )
            ]
        )
        
        # Register Developers
        await self.specialization_manager.register_agent(
            agent_id="dev1",
            primary_role=AgentRole.DEVELOPER,
            capabilities=[
                AgentCapability(
                    name="code_analysis",
                    description="Analyzes code for potential issues",
                    expertise_level=ExpertiseLevel.EXPERT,
                    supported_roles={AgentRole.DEVELOPER, AgentRole.ARCHITECT}
                ),
                AgentCapability(
                    name="code_review",
                    description="Reviews code changes",
                    expertise_level=ExpertiseLevel.EXPERT,
                    supported_roles={AgentRole.DEVELOPER}
                )
            ]
        )
        
        await self.specialization_manager.register_agent(
            agent_id="dev2",
            primary_role=AgentRole.DEVELOPER,
            capabilities=[
                AgentCapability(
                    name="code_analysis",
                    description="Analyzes code for potential issues",
                    expertise_level=ExpertiseLevel.INTERMEDIATE,
                    supported_roles={AgentRole.DEVELOPER}
                ),
                AgentCapability(
                    name="test_development",
                    description="Develops test cases",
                    expertise_level=ExpertiseLevel.INTERMEDIATE,
                    supported_roles={AgentRole.DEVELOPER, AgentRole.TESTER}
                )
            ]
        )
        
        # Register Testers
        await self.specialization_manager.register_agent(
            agent_id="tester1",
            primary_role=AgentRole.TESTER,
            capabilities=[
                AgentCapability(
                    name="test_execution",
                    description="Executes test suites",
                    expertise_level=ExpertiseLevel.EXPERT,
                    supported_roles={AgentRole.TESTER}
                ),
                AgentCapability(
                    name="test_automation",
                    description="Develops automated tests",
                    expertise_level=ExpertiseLevel.EXPERT,
                    supported_roles={AgentRole.TESTER}
                )
            ]
        )
        
        # Register Architect
        await self.specialization_manager.register_agent(
            agent_id="architect1",
            primary_role=AgentRole.ARCHITECT,
            capabilities=[
                AgentCapability(
                    name="system_design",
                    description="Designs system architecture",
                    expertise_level=ExpertiseLevel.EXPERT,
                    supported_roles={AgentRole.ARCHITECT}
                ),
                AgentCapability(
                    name="code_analysis",
                    description="Analyzes code for potential issues",
                    expertise_level=ExpertiseLevel.EXPERT,
                    supported_roles={AgentRole.ARCHITECT}
                )
            ]
        )
    
    async def setup_development_teams(self) -> Dict[str, Team]:
        """Set up development teams for a project."""
        teams = {}
        
        # Create Frontend Team
        frontend_team = await self.specialization_manager.create_team(
            name="Frontend Development Team",
            manager_id="manager1",
            required_roles={AgentRole.DEVELOPER, AgentRole.TESTER}
        )
        
        # Assign agents to Frontend Team
        await self.specialization_manager.assign_agent_to_team(
            team_id=frontend_team.team_id,
            agent_id="dev1",
            role=AgentRole.DEVELOPER
        )
        
        await self.specialization_manager.assign_agent_to_team(
            team_id=frontend_team.team_id,
            agent_id="tester1",
            role=AgentRole.TESTER
        )
        
        teams["frontend"] = frontend_team
        
        # Create Backend Team
        backend_team = await self.specialization_manager.create_team(
            name="Backend Development Team",
            manager_id="manager1",
            required_roles={AgentRole.DEVELOPER, AgentRole.TESTER, AgentRole.ARCHITECT}
        )
        
        # Assign agents to Backend Team
        await self.specialization_manager.assign_agent_to_team(
            team_id=backend_team.team_id,
            agent_id="dev2",
            role=AgentRole.DEVELOPER
        )
        
        await self.specialization_manager.assign_agent_to_team(
            team_id=backend_team.team_id,
            agent_id="architect1",
            role=AgentRole.ARCHITECT
        )
        
        teams["backend"] = backend_team
        
        return teams
    
    async def coordinate_development_effort(self, teams: Dict[str, Team]) -> Dict[str, Any]:
        """Coordinate development effort between teams."""
        # Get coordination data
        coordination_data = await self.specialization_manager.coordinate_teams(
            list(teams.values())
        )
        
        # Optimize team configurations
        for team in teams.values():
            await self.specialization_manager.optimize_team_configuration(team.team_id)
        
        return coordination_data
    
    async def handle_development_scenario(self) -> Dict[str, Any]:
        """Handle a complete development scenario."""
        # Set up teams
        teams = await self.setup_development_teams()
        
        # Simulate some development work
        for team in teams.values():
            # Add some metrics
            for member in team.members.values():
                member.contribution_metrics = {
                    "efficiency": 0.8,
                    "coordination": 0.7,
                    "code_quality": 0.9
                }
            
            team.performance_metrics = {
                "efficiency": 0.85,
                "resource_utilization": 0.75,
                "code_coverage": 0.9
            }
        
        # Coordinate teams
        coordination_data = await self.coordinate_development_effort(teams)
        
        # Find specialists for a specific task
        specialists = await self.specialization_manager.find_specialist(
            required_role=AgentRole.DEVELOPER,
            min_expertise=ExpertiseLevel.EXPERT
        )
        
        return {
            "teams": teams,
            "coordination": coordination_data,
            "available_specialists": specialists
        }
    
    async def cleanup_development_effort(self, teams: Dict[str, Team]) -> bool:
        """Clean up development effort by dissolving teams."""
        success = True
        for team in teams.values():
            if not await self.specialization_manager.dissolve_team(team.team_id):
                success = False
        return success

async def main():
    """Example usage of the development team system."""
    # Create example instance
    example = DevelopmentTeamExample()
    
    # Handle development scenario
    result = await example.handle_development_scenario()
    
    # Print results
    print("\nDevelopment Teams:")
    for team_name, team in result["teams"].items():
        print(f"\n{team_name} Team:")
        print(f"Status: {team.status}")
        print(f"Members: {len(team.members)}")
        print(f"Performance Metrics: {team.performance_metrics}")
    
    print("\nCoordination Data:")
    print(f"Resource Sharing: {result['coordination']['resource_sharing']}")
    print(f"Team Priorities: {result['coordination']['priorities']}")
    print(f"Conflicts: {result['coordination']['conflicts']}")
    print(f"Overall Progress: {result['coordination']['progress']['overall']}")
    
    print("\nAvailable Specialists:")
    for specialist_id in result["available_specialists"]:
        print(f"- {specialist_id}")
    
    # Clean up
    await example.cleanup_development_effort(result["teams"])

if __name__ == "__main__":
    asyncio.run(main()) 