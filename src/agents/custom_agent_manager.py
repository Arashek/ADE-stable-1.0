from typing import Dict, Any, List, Optional, Set, Tuple
import logging
from datetime import datetime
from dataclasses import dataclass
import json
import uuid

from ..core.orchestrator import Orchestrator
from ..memory.memory_manager import MemoryManager
from ..database.mongodb import MongoDB
from .custom_agent import CustomAgent, AgentCapability, AgentPersonality

logger = logging.getLogger(__name__)

class CustomAgentManager:
    """Manages custom agents in the system"""
    
    def __init__(
        self,
        orchestrator: Orchestrator,
        memory_manager: MemoryManager,
        mongodb: MongoDB
    ):
        self.orchestrator = orchestrator
        self.memory_manager = memory_manager
        self.mongodb = mongodb
        self.active_agents: Dict[str, CustomAgent] = {}
    
    async def create_agent(
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
            # Create capability objects
            agent_capabilities = [
                AgentCapability(
                    name=cap["name"],
                    description=cap["description"],
                    parameters=cap["parameters"],
                    return_type=cap["return_type"],
                    examples=cap.get("examples")
                )
                for cap in capabilities
            ]
            
            # Create personality object
            agent_personality = AgentPersonality(
                traits=personality["traits"],
                communication_style=personality["communication_style"],
                decision_making_style=personality["decision_making_style"],
                expertise_level=personality["expertise_level"],
                metadata=personality.get("metadata")
            )
            
            # Create agent
            agent = CustomAgent(
                orchestrator=self.orchestrator,
                memory_manager=self.memory_manager,
                mongodb=self.mongodb,
                name=name,
                description=description,
                capabilities=agent_capabilities,
                personality=agent_personality,
                metadata=metadata
            )
            
            # Initialize agent
            await agent.initialize()
            
            # Add to active agents
            self.active_agents[agent.id] = agent
            
            logger.info(f"Created custom agent: {name} ({agent.id})")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create custom agent: {str(e)}")
            raise
    
    async def load_agent(self, agent_id: str) -> CustomAgent:
        """Load a custom agent from database
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Loaded custom agent
        """
        try:
            # Check if already loaded
            if agent_id in self.active_agents:
                return self.active_agents[agent_id]
            
            # Load agent
            agent = await CustomAgent.load_agent(
                orchestrator=self.orchestrator,
                memory_manager=self.memory_manager,
                mongodb=self.mongodb,
                agent_id=agent_id
            )
            
            # Add to active agents
            self.active_agents[agent_id] = agent
            
            logger.info(f"Loaded custom agent: {agent.name} ({agent_id})")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to load custom agent: {str(e)}")
            raise
    
    async def get_agent(self, agent_id: str) -> Optional[CustomAgent]:
        """Get a custom agent by ID
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Custom agent or None if not found
        """
        try:
            # Check active agents
            if agent_id in self.active_agents:
                return self.active_agents[agent_id]
            
            # Try to load from database
            return await self.load_agent(agent_id)
            
        except Exception as e:
            logger.error(f"Failed to get custom agent: {str(e)}")
            return None
    
    async def list_agents(
        self,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """List all custom agents
        
        Args:
            include_inactive: Whether to include inactive agents
            
        Returns:
            List of agent information
        """
        try:
            # Get all agent documents
            query = {} if include_inactive else {"status": "ready"}
            agent_docs = await self.mongodb.find_documents("custom_agents", query)
            
            # Format agent information
            agents = []
            for doc in agent_docs:
                agent_info = {
                    "id": doc["id"],
                    "name": doc["name"],
                    "description": doc["description"],
                    "status": doc["status"],
                    "created_at": doc["created_at"],
                    "last_active": doc["last_active"],
                    "num_capabilities": len(doc["capabilities"]),
                    "personality": {
                        "traits": doc["personality"]["traits"],
                        "communication_style": doc["personality"]["communication_style"],
                        "decision_making_style": doc["personality"]["decision_making_style"],
                        "expertise_level": doc["personality"]["expertise_level"]
                    }
                }
                agents.append(agent_info)
            
            return agents
            
        except Exception as e:
            logger.error(f"Failed to list custom agents: {str(e)}")
            return []
    
    async def update_agent(
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
            # Get agent
            agent = await self.get_agent(agent_id)
            if not agent:
                return None
            
            # Update basic information
            if "name" in updates:
                agent.name = updates["name"]
            if "description" in updates:
                agent.description = updates["description"]
            if "metadata" in updates:
                agent.metadata.update(updates["metadata"])
            
            # Update capabilities
            if "capabilities" in updates:
                for cap_update in updates["capabilities"]:
                    await agent.add_capability(
                        name=cap_update["name"],
                        description=cap_update["description"],
                        parameters=cap_update["parameters"],
                        return_type=cap_update["return_type"],
                        handler=cap_update.get("handler"),
                        examples=cap_update.get("examples")
                    )
            
            # Update personality
            if "personality" in updates:
                await agent.update_personality(
                    traits=updates["personality"].get("traits"),
                    communication_style=updates["personality"].get("communication_style"),
                    decision_making_style=updates["personality"].get("decision_making_style"),
                    expertise_level=updates["personality"].get("expertise_level"),
                    metadata=updates["personality"].get("metadata")
                )
            
            # Update status
            if "status" in updates:
                await agent.update_status(updates["status"])
            
            # Save changes
            await agent._save_agent_definition()
            
            logger.info(f"Updated custom agent: {agent.name} ({agent_id})")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to update custom agent: {str(e)}")
            return None
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete a custom agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Whether deletion was successful
        """
        try:
            # Get agent
            agent = await self.get_agent(agent_id)
            if not agent:
                return False
            
            # Remove from active agents
            if agent_id in self.active_agents:
                del self.active_agents[agent_id]
            
            # Delete from database
            await self.mongodb.delete_document(
                "custom_agents",
                {"id": agent_id}
            )
            
            # Clean up memory
            await self.memory_manager.delete_agent_memory(agent_id)
            
            logger.info(f"Deleted custom agent: {agent.name} ({agent_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete custom agent: {str(e)}")
            return False
    
    async def get_agent_capabilities(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get capabilities of a custom agent
        
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
            
            # Format capability information
            return [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "parameters": cap.parameters,
                    "return_type": cap.return_type,
                    "examples": cap.examples
                }
                for cap in agent.capabilities
            ]
            
        except Exception as e:
            logger.error(f"Failed to get agent capabilities: {str(e)}")
            return []
    
    async def get_agent_personality(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get personality of a custom agent
        
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
            
            # Format personality information
            return {
                "traits": agent.personality.traits,
                "communication_style": agent.personality.communication_style,
                "decision_making_style": agent.personality.decision_making_style,
                "expertise_level": agent.personality.expertise_level,
                "metadata": agent.personality.metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to get agent personality: {str(e)}")
            return None
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a custom agent
        
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
            
            # Format status information
            return {
                "id": agent.id,
                "name": agent.name,
                "status": agent.status,
                "created_at": agent.created_at.isoformat(),
                "last_active": agent.last_active.isoformat(),
                "num_capabilities": len(agent.capabilities)
            }
            
        except Exception as e:
            logger.error(f"Failed to get agent status: {str(e)}")
            return None 