"""
Agent Registry for ADE Platform

This module implements a registry for specialized agents in the ADE platform.
It provides a centralized way to register, discover, and manage agents,
ensuring that the coordination system can locate and communicate with all agents.
"""

import logging
from typing import Dict, List, Any, Optional, Set
import asyncio
from enum import Enum

from services.coordination.agent_interface import AgentInterface, AgentCapability

# Configure logging
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Enumeration of agent statuses"""
    OFFLINE = "offline"
    ONLINE = "online"
    BUSY = "busy"
    MAINTENANCE = "maintenance"

class AgentRegistry:
    """
    Registry for specialized agents.
    
    This class provides a centralized registry for all specialized agents in the
    ADE platform, allowing the coordination system to discover and communicate
    with agents based on their capabilities and status.
    """
    
    _instance = None
    
    def __new__(cls):
        """
        Create a singleton instance of the agent registry.
        
        Returns:
            Singleton instance of AgentRegistry
        """
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialize the agent registry.
        """
        if self._initialized:
            return
        
        # Initialize registry data structures
        self.agents = {}  # agent_id -> agent_data
        self.interfaces = {}  # agent_id -> agent_interface
        self.capabilities = {}  # capability -> set of agent_ids
        self.agent_types = {}  # agent_type -> set of agent_ids
        
        # Initialize registry lock
        self._lock = asyncio.Lock()
        
        # Initialize event listeners
        self.event_listeners = {}
        
        self._initialized = True
        logger.info("Agent registry initialized")
    
    async def register_agent(self, agent_id: str, agent_type: str, 
                           capabilities: List[str], interface: AgentInterface) -> bool:
        """
        Register an agent in the registry.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent
            capabilities: List of agent capabilities
            interface: Agent interface instance
            
        Returns:
            True if registration was successful, False otherwise
        """
        async with self._lock:
            # Check if agent already registered
            if agent_id in self.agents:
                logger.warning("Agent %s already registered", agent_id)
                return False
            
            # Register agent
            self.agents[agent_id] = {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "capabilities": capabilities,
                "status": AgentStatus.ONLINE.value,
                "metadata": {}
            }
            
            # Register interface
            self.interfaces[agent_id] = interface
            
            # Register capabilities
            for capability in capabilities:
                if capability not in self.capabilities:
                    self.capabilities[capability] = set()
                self.capabilities[capability].add(agent_id)
            
            # Register agent type
            if agent_type not in self.agent_types:
                self.agent_types[agent_type] = set()
            self.agent_types[agent_type].add(agent_id)
            
            logger.info("Registered agent %s of type %s with capabilities %s", 
                       agent_id, agent_type, capabilities)
            
            # Notify event listeners
            await self._notify_event("agent_registered", {
                "agent_id": agent_id,
                "agent_type": agent_type
            })
            
            return True
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the registry.
        
        Args:
            agent_id: ID of the agent to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        async with self._lock:
            # Check if agent is registered
            if agent_id not in self.agents:
                logger.warning("Agent %s not registered", agent_id)
                return False
            
            # Get agent data
            agent_data = self.agents[agent_id]
            agent_type = agent_data["agent_type"]
            capabilities = agent_data["capabilities"]
            
            # Unregister capabilities
            for capability in capabilities:
                if capability in self.capabilities:
                    self.capabilities[capability].discard(agent_id)
                    if not self.capabilities[capability]:
                        del self.capabilities[capability]
            
            # Unregister agent type
            if agent_type in self.agent_types:
                self.agent_types[agent_type].discard(agent_id)
                if not self.agent_types[agent_type]:
                    del self.agent_types[agent_type]
            
            # Unregister interface
            if agent_id in self.interfaces:
                del self.interfaces[agent_id]
            
            # Unregister agent
            del self.agents[agent_id]
            
            logger.info("Unregistered agent %s", agent_id)
            
            # Notify event listeners
            await self._notify_event("agent_unregistered", {
                "agent_id": agent_id
            })
            
            return True
    
    async def update_agent_status(self, agent_id: str, status: str) -> bool:
        """
        Update an agent's status.
        
        Args:
            agent_id: ID of the agent to update
            status: New status
            
        Returns:
            True if update was successful, False otherwise
        """
        async with self._lock:
            # Check if agent is registered
            if agent_id not in self.agents:
                logger.warning("Agent %s not registered", agent_id)
                return False
            
            # Check if status is valid
            try:
                status = AgentStatus(status).value
            except ValueError:
                logger.warning("Invalid status %s", status)
                return False
            
            # Update status
            old_status = self.agents[agent_id]["status"]
            self.agents[agent_id]["status"] = status
            
            logger.info("Updated agent %s status from %s to %s", 
                       agent_id, old_status, status)
            
            # Notify event listeners
            await self._notify_event("agent_status_changed", {
                "agent_id": agent_id,
                "old_status": old_status,
                "new_status": status
            })
            
            return True
    
    async def update_agent_metadata(self, agent_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update an agent's metadata.
        
        Args:
            agent_id: ID of the agent to update
            metadata: New metadata
            
        Returns:
            True if update was successful, False otherwise
        """
        async with self._lock:
            # Check if agent is registered
            if agent_id not in self.agents:
                logger.warning("Agent %s not registered", agent_id)
                return False
            
            # Update metadata
            self.agents[agent_id]["metadata"].update(metadata)
            
            logger.info("Updated agent %s metadata", agent_id)
            
            return True
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent data by ID.
        
        Args:
            agent_id: ID of the agent to get
            
        Returns:
            Agent data or None if not found
        """
        async with self._lock:
            return self.agents.get(agent_id)
    
    async def get_agent_interface(self, agent_id: str) -> Optional[AgentInterface]:
        """
        Get agent interface by ID.
        
        Args:
            agent_id: ID of the agent to get interface for
            
        Returns:
            Agent interface or None if not found
        """
        async with self._lock:
            return self.interfaces.get(agent_id)
    
    async def get_agents_by_capability(self, capability: str) -> List[str]:
        """
        Get agents with a specific capability.
        
        Args:
            capability: Capability to filter by
            
        Returns:
            List of agent IDs with the capability
        """
        async with self._lock:
            return list(self.capabilities.get(capability, set()))
    
    async def get_agents_by_type(self, agent_type: str) -> List[str]:
        """
        Get agents of a specific type.
        
        Args:
            agent_type: Agent type to filter by
            
        Returns:
            List of agent IDs of the type
        """
        async with self._lock:
            return list(self.agent_types.get(agent_type, set()))
    
    async def get_available_agents(self, capability: str = None, 
                                 agent_type: str = None) -> List[str]:
        """
        Get available agents, optionally filtered by capability and type.
        
        Args:
            capability: Optional capability to filter by
            agent_type: Optional agent type to filter by
            
        Returns:
            List of available agent IDs
        """
        async with self._lock:
            # Start with all agents
            available_agents = set(self.agents.keys())
            
            # Filter by status
            available_agents = {
                agent_id for agent_id in available_agents
                if self.agents[agent_id]["status"] == AgentStatus.ONLINE.value
            }
            
            # Filter by capability
            if capability:
                capability_agents = self.capabilities.get(capability, set())
                available_agents &= capability_agents
            
            # Filter by type
            if agent_type:
                type_agents = self.agent_types.get(agent_type, set())
                available_agents &= type_agents
            
            return list(available_agents)
    
    async def get_all_agents(self) -> List[Dict[str, Any]]:
        """
        Get all registered agents.
        
        Returns:
            List of all agent data
        """
        async with self._lock:
            return list(self.agents.values())
    
    async def get_agent_count(self) -> int:
        """
        Get the number of registered agents.
        
        Returns:
            Number of registered agents
        """
        async with self._lock:
            return len(self.agents)
    
    async def add_event_listener(self, event_type: str, listener) -> None:
        """
        Add an event listener.
        
        Args:
            event_type: Type of event to listen for
            listener: Async function to call when event occurs
        """
        async with self._lock:
            if event_type not in self.event_listeners:
                self.event_listeners[event_type] = set()
            self.event_listeners[event_type].add(listener)
            
            logger.info("Added listener for event type %s", event_type)
    
    async def remove_event_listener(self, event_type: str, listener) -> None:
        """
        Remove an event listener.
        
        Args:
            event_type: Type of event
            listener: Listener to remove
        """
        async with self._lock:
            if event_type in self.event_listeners:
                self.event_listeners[event_type].discard(listener)
                if not self.event_listeners[event_type]:
                    del self.event_listeners[event_type]
                
                logger.info("Removed listener for event type %s", event_type)
    
    async def _notify_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Notify event listeners of an event.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        listeners = set()
        async with self._lock:
            if event_type in self.event_listeners:
                listeners = self.event_listeners[event_type].copy()
        
        for listener in listeners:
            try:
                await listener(event_data)
            except Exception as e:
                logger.error("Error in event listener: %s", str(e))

class AgentRegistryManager:
    """
    Manager for agent registry operations.
    
    This class provides higher-level operations on the agent registry,
    such as selecting agents for tasks based on capabilities and load balancing.
    """
    
    def __init__(self):
        """
        Initialize the agent registry manager.
        """
        self.registry = AgentRegistry()
        logger.info("Agent registry manager initialized")
    
    async def select_agent_for_task(self, capability: str, 
                                  agent_type: str = None) -> Optional[str]:
        """
        Select the best agent for a task.
        
        Args:
            capability: Required capability
            agent_type: Optional preferred agent type
            
        Returns:
            ID of the selected agent, or None if no suitable agent found
        """
        # Get available agents with the capability
        available_agents = await self.registry.get_available_agents(
            capability=capability, agent_type=agent_type)
        
        if not available_agents:
            logger.warning("No available agents with capability %s", capability)
            return None
        
        # For now, just return the first available agent
        # In a real implementation, this would consider load balancing, agent performance, etc.
        selected_agent = available_agents[0]
        
        logger.info("Selected agent %s for task requiring capability %s", 
                   selected_agent, capability)
        
        return selected_agent
    
    async def select_agents_for_collaboration(self, capabilities: List[str], 
                                           count: int = None) -> List[str]:
        """
        Select agents for collaboration on a task.
        
        Args:
            capabilities: List of required capabilities
            count: Optional maximum number of agents to select
            
        Returns:
            List of selected agent IDs
        """
        selected_agents = set()
        
        # Select agents for each capability
        for capability in capabilities:
            agents = await self.registry.get_available_agents(capability=capability)
            if agents:
                selected_agents.add(agents[0])
        
        # Limit number of agents if specified
        if count and len(selected_agents) > count:
            selected_agents = list(selected_agents)[:count]
        
        logger.info("Selected %d agents for collaboration on capabilities %s", 
                   len(selected_agents), capabilities)
        
        return list(selected_agents)
    
    async def get_agent_capabilities(self, agent_id: str) -> List[str]:
        """
        Get an agent's capabilities.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List of agent capabilities
        """
        agent_data = await self.registry.get_agent(agent_id)
        if agent_data:
            return agent_data["capabilities"]
        return []
    
    async def get_agents_by_capabilities(self, capabilities: List[str], 
                                      require_all: bool = False) -> List[str]:
        """
        Get agents with specified capabilities.
        
        Args:
            capabilities: List of capabilities to filter by
            require_all: If True, agents must have all capabilities; if False, any capability
            
        Returns:
            List of agent IDs
        """
        async with self.registry._lock:
            if not capabilities:
                return []
            
            if require_all:
                # Agents must have all capabilities
                result = None
                for capability in capabilities:
                    agents = self.registry.capabilities.get(capability, set())
                    if result is None:
                        result = agents
                    else:
                        result &= agents
                return list(result or [])
            else:
                # Agents must have any capability
                result = set()
                for capability in capabilities:
                    agents = self.registry.capabilities.get(capability, set())
                    result |= agents
                return list(result)
    
    async def get_capability_coverage(self) -> Dict[str, int]:
        """
        Get coverage of capabilities across all agents.
        
        Returns:
            Dictionary mapping capabilities to number of agents
        """
        async with self.registry._lock:
            return {
                capability: len(agents)
                for capability, agents in self.registry.capabilities.items()
            }
    
    async def get_agent_type_distribution(self) -> Dict[str, int]:
        """
        Get distribution of agent types.
        
        Returns:
            Dictionary mapping agent types to number of agents
        """
        async with self.registry._lock:
            return {
                agent_type: len(agents)
                for agent_type, agents in self.registry.agent_types.items()
            }
