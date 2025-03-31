from typing import Dict, Any, List, Optional, Set, Tuple
import logging
from datetime import datetime
from dataclasses import dataclass
import json
import uuid

from ..agents.base import BaseAgent
from ..agents.custom_agent import CustomAgent
from ..agents.custom_agent_manager import CustomAgentManager
from ..memory.memory_manager import MemoryManager
from ..database.mongodb import MongoDB

logger = logging.getLogger(__name__)

@dataclass
class Task:
    """Represents a task to be executed by an agent"""
    id: str = None
    agent_id: str = None
    type: str = None
    status: str = "pending"
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    input_data: Dict[str, Any] = None
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.input_data:
            self.input_data = {}

class Orchestrator:
    """Coordinates interactions between agents and manages system state"""
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        mongodb: MongoDB
    ):
        self.memory_manager = memory_manager
        self.mongodb = mongodb
        
        # Initialize agent management
        self.agents: Dict[str, BaseAgent] = {}
        self.custom_agent_manager = CustomAgentManager(
            orchestrator=self,
            memory_manager=memory_manager,
            mongodb=mongodb
        )
        
        # System state
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.status = "initialized"
    
    async def initialize(self) -> None:
        """Initialize the orchestrator"""
        try:
            # Load existing agents
            await self._load_agents()
            
            # Load custom agents
            await self._load_custom_agents()
            
            self.status = "ready"
            logger.info("Orchestrator initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {str(e)}")
            raise
    
    async def _load_agents(self) -> None:
        """Load existing agents from database"""
        try:
            # Get agent documents
            agent_docs = await self.mongodb.find_documents("agents", {})
            
            # Load each agent
            for doc in agent_docs:
                agent_id = doc["id"]
                agent_type = doc["type"]
                
                # Create appropriate agent instance
                if agent_type == "custom":
                    agent = await self.custom_agent_manager.load_agent(agent_id)
                else:
                    # TODO: Load other agent types
                    continue
                
                # Register agent
                await self.register_agent(agent)
                
        except Exception as e:
            logger.error(f"Failed to load agents: {str(e)}")
            raise
    
    async def _load_custom_agents(self) -> None:
        """Load custom agents from database"""
        try:
            # Get custom agent documents
            agent_docs = await self.mongodb.find_documents("custom_agents", {})
            
            # Load each custom agent
            for doc in agent_docs:
                agent_id = doc["id"]
                await self.custom_agent_manager.load_agent(agent_id)
                
        except Exception as e:
            logger.error(f"Failed to load custom agents: {str(e)}")
            raise
    
    async def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator
        
        Args:
            agent: Agent to register
        """
        try:
            # Add to agents dictionary
            self.agents[agent.id] = agent
            
            # Update last active timestamp
            self.last_active = datetime.now()
            
            logger.info(f"Registered agent: {agent.name} ({agent.id})")
            
        except Exception as e:
            logger.error(f"Failed to register agent: {str(e)}")
            raise
    
    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the orchestrator
        
        Args:
            agent_id: ID of agent to unregister
        """
        try:
            if agent_id in self.agents:
                del self.agents[agent_id]
                logger.info(f"Unregistered agent: {agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to unregister agent: {str(e)}")
            raise
    
    async def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent or None if not found
        """
        try:
            # Check registered agents
            if agent_id in self.agents:
                return self.agents[agent_id]
            
            # Try to load custom agent
            return await self.custom_agent_manager.get_agent(agent_id)
            
        except Exception as e:
            logger.error(f"Failed to get agent: {str(e)}")
            return None
    
    async def list_agents(
        self,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """List all agents
        
        Args:
            include_inactive: Whether to include inactive agents
            
        Returns:
            List of agent information
        """
        try:
            agents = []
            
            # Add registered agents
            for agent in self.agents.values():
                agent_info = {
                    "id": agent.id,
                    "name": agent.name,
                    "type": "base",
                    "status": getattr(agent, "status", "unknown")
                }
                agents.append(agent_info)
            
            # Add custom agents
            custom_agents = await self.custom_agent_manager.list_agents(include_inactive)
            for agent_info in custom_agents:
                agent_info["type"] = "custom"
                agents.append(agent_info)
            
            return agents
            
        except Exception as e:
            logger.error(f"Failed to list agents: {str(e)}")
            return []
    
    async def create_custom_agent(
        self,
        name: str,
        description: str,
        capabilities: List[Dict[str, Any]],
        personality: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> CustomAgent:
        """Create a new custom agent
        
        Args:
            name: Agent name
            description: Agent description
            capabilities: List of capability definitions
            personality: Personality definition
            metadata: Additional metadata
            
        Returns:
            Created custom agent
        """
        try:
            # Create agent
            agent = await self.custom_agent_manager.create_agent(
                name=name,
                description=description,
                capabilities=capabilities,
                personality=personality,
                metadata=metadata
            )
            
            # Register agent
            await self.register_agent(agent)
            
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create custom agent: {str(e)}")
            raise
    
    async def update_custom_agent(
        self,
        agent_id: str,
        updates: Dict[str, Any]
    ) -> Optional[CustomAgent]:
        """Update a custom agent
        
        Args:
            agent_id: Agent ID
            updates: Dictionary of updates
            
        Returns:
            Updated agent or None if not found
        """
        try:
            # Update agent
            agent = await self.custom_agent_manager.update_agent(agent_id, updates)
            
            if agent:
                # Update registration
                await self.register_agent(agent)
            
            return agent
            
        except Exception as e:
            logger.error(f"Failed to update custom agent: {str(e)}")
            return None
    
    async def delete_custom_agent(self, agent_id: str) -> bool:
        """Delete a custom agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Whether deletion was successful
        """
        try:
            # Delete agent
            success = await self.custom_agent_manager.delete_agent(agent_id)
            
            if success:
                # Unregister agent
                await self.unregister_agent(agent_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete custom agent: {str(e)}")
            return False
    
    async def get_agent_capabilities(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get capabilities of an agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            List of capability information
        """
        try:
            # Get agent
            agent = await self.get_agent(agent_id)
            if not agent:
                return []
            
            # Handle custom agents
            if isinstance(agent, CustomAgent):
                return await self.custom_agent_manager.get_agent_capabilities(agent_id)
            
            # TODO: Handle other agent types
            return []
            
        except Exception as e:
            logger.error(f"Failed to get agent capabilities: {str(e)}")
            return []
    
    async def get_agent_personality(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get personality of an agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Personality information or None if agent not found
        """
        try:
            # Get agent
            agent = await self.get_agent(agent_id)
            if not agent:
                return None
            
            # Handle custom agents
            if isinstance(agent, CustomAgent):
                return await self.custom_agent_manager.get_agent_personality(agent_id)
            
            # TODO: Handle other agent types
            return None
            
        except Exception as e:
            logger.error(f"Failed to get agent personality: {str(e)}")
            return None
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Status information or None if agent not found
        """
        try:
            # Get agent
            agent = await self.get_agent(agent_id)
            if not agent:
                return None
            
            # Handle custom agents
            if isinstance(agent, CustomAgent):
                return await self.custom_agent_manager.get_agent_status(agent_id)
            
            # TODO: Handle other agent types
            return None
            
        except Exception as e:
            logger.error(f"Failed to get agent status: {str(e)}")
            return None 