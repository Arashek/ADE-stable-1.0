from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ..agent.base import BaseAgent, AgentCapability
from ...agents.development.workflow_manager import WorkflowManagerAgent
from ...agents.development.planner import PlannerAgent
from ...agents.leadership.architect import ArchitectAgent

logger = logging.getLogger(__name__)

class AgentRegistry:
    """Registry for managing ADE platform agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_capabilities: Dict[str, List[AgentCapability]] = {}
        self.active_collaborations: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
        
    def register_agent(self, agent: BaseAgent) -> bool:
        """Register a new agent in the registry"""
        try:
            if agent.agent_id in self.agents:
                self.logger.warning(f"Agent {agent.agent_id} is already registered")
                return False
                
            self.agents[agent.agent_id] = agent
            self.agent_capabilities[agent.agent_id] = agent.capabilities
            self.logger.info(f"Successfully registered agent {agent.agent_id} with capabilities {agent.capabilities}")
            return True
        except Exception as e:
            self.logger.error(f"Error registering agent: {str(e)}")
            return False
            
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the registry"""
        try:
            if agent_id not in self.agents:
                self.logger.warning(f"Agent {agent_id} is not registered")
                return False
                
            del self.agents[agent_id]
            del self.agent_capabilities[agent_id]
            self.logger.info(f"Successfully unregistered agent {agent_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error unregistering agent: {str(e)}")
            return False
            
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
        
    def get_agents_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        """Get all agents with a specific capability"""
        return [
            agent for agent_id, agent in self.agents.items()
            if capability in self.agent_capabilities[agent_id]
        ]
        
    def initialize_workflow_agents(self, provider_registry: Any) -> None:
        """Initialize workflow-related agents"""
        try:
            # Initialize workflow manager agent
            workflow_manager = WorkflowManagerAgent(
                agent_id="workflow_manager_1",
                provider_registry=provider_registry
            )
            self.register_agent(workflow_manager)
            
            # Initialize planner agent
            planner = PlannerAgent(
                agent_id="planner_1",
                provider_registry=provider_registry
            )
            self.register_agent(planner)
            
            # Initialize architect agent
            architect = ArchitectAgent(
                agent_id="architect_1",
                provider_registry=provider_registry
            )
            self.register_agent(architect)
            
            self.logger.info("Successfully initialized workflow agents")
        except Exception as e:
            self.logger.error(f"Error initializing workflow agents: {str(e)}")
            
    def start_collaboration(self, source_agent_id: str, target_agent_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Start a collaboration between two agents"""
        try:
            if source_agent_id not in self.agents or target_agent_id not in self.agents:
                return {"status": "error", "message": "One or both agents not found"}
                
            source_agent = self.agents[source_agent_id]
            target_agent = self.agents[target_agent_id]
            
            collaboration_id = f"collab_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.active_collaborations[collaboration_id] = {
                "source_agent": source_agent_id,
                "target_agent": target_agent_id,
                "task": task,
                "start_time": datetime.now(),
                "status": "active"
            }
            
            return {
                "status": "success",
                "collaboration_id": collaboration_id,
                "message": "Collaboration started successfully"
            }
        except Exception as e:
            self.logger.error(f"Error starting collaboration: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def end_collaboration(self, collaboration_id: str) -> Dict[str, Any]:
        """End an active collaboration"""
        try:
            if collaboration_id not in self.active_collaborations:
                return {"status": "error", "message": "Collaboration not found"}
                
            collaboration = self.active_collaborations[collaboration_id]
            collaboration["end_time"] = datetime.now()
            collaboration["status"] = "completed"
            
            return {
                "status": "success",
                "message": "Collaboration ended successfully"
            }
        except Exception as e:
            self.logger.error(f"Error ending collaboration: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def get_collaboration_status(self, collaboration_id: str) -> Dict[str, Any]:
        """Get the status of a collaboration"""
        try:
            if collaboration_id not in self.active_collaborations:
                return {"status": "error", "message": "Collaboration not found"}
                
            return {
                "status": "success",
                "data": self.active_collaborations[collaboration_id]
            }
        except Exception as e:
            self.logger.error(f"Error getting collaboration status: {str(e)}")
            return {"status": "error", "message": str(e)} 