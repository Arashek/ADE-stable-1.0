from typing import Dict, Any, List, Optional, Set, Tuple
import logging
from datetime import datetime
from dataclasses import dataclass
import json
import uuid

from .base import BaseAgent
from ..core.orchestrator import Orchestrator
from ..memory.memory_manager import MemoryManager
from ..database.mongodb import MongoDB

logger = logging.getLogger(__name__)

@dataclass
class AgentCapability:
    """Represents a capability of a custom agent"""
    name: str
    description: str
    parameters: Dict[str, Any]
    return_type: str
    examples: List[Dict[str, Any]] = None

@dataclass
class AgentPersonality:
    """Represents the personality traits of a custom agent"""
    traits: Dict[str, float]  # Trait name to value (0-1)
    communication_style: str
    decision_making_style: str
    expertise_level: float  # 0-1
    metadata: Dict[str, Any] = None

class CustomAgent(BaseAgent):
    """Represents a user-defined custom agent"""
    
    def __init__(
        self,
        orchestrator: Orchestrator,
        memory_manager: MemoryManager,
        mongodb: MongoDB,
        name: str,
        description: str,
        capabilities: List[AgentCapability],
        personality: AgentPersonality,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(orchestrator, memory_manager, mongodb)
        
        # Generate unique agent ID
        self.id = f"custom_agent_{uuid.uuid4().hex}"
        
        # Basic information
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.personality = personality
        self.metadata = metadata or {}
        
        # State
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.status = "initialized"
        
        # Initialize capability handlers
        self._capability_handlers = {}
        self._initialize_capability_handlers()
    
    def _initialize_capability_handlers(self) -> None:
        """Initialize handlers for each capability"""
        try:
            for capability in self.capabilities:
                handler_name = f"handle_{capability.name.lower().replace(' ', '_')}"
                if hasattr(self, handler_name):
                    self._capability_handlers[capability.name] = getattr(self, handler_name)
                else:
                    logger.warning(f"No handler found for capability: {capability.name}")
        
        except Exception as e:
            logger.error(f"Failed to initialize capability handlers: {str(e)}")
            raise
    
    async def initialize(self) -> None:
        """Initialize the custom agent"""
        try:
            # Register agent with orchestrator
            await self.orchestrator.register_agent(self)
            
            # Initialize memory system
            await self.memory_manager.initialize_agent_memory(self.id)
            
            # Save agent definition
            await self._save_agent_definition()
            
            self.status = "ready"
            logger.info(f"Custom agent initialized: {self.name} ({self.id})")
            
        except Exception as e:
            logger.error(f"Failed to initialize custom agent: {str(e)}")
            raise
    
    async def process_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process an incoming message
        
        Args:
            message: Input message
            context: Additional context
            
        Returns:
            Response message
        """
        try:
            # Update last active timestamp
            self.last_active = datetime.now()
            
            # Get relevant memories
            memories = await self.memory_manager.get_relevant_memories(
                self.id,
                message,
                context=context
            )
            
            # Determine appropriate capability
            capability = self._determine_capability(message, memories)
            
            if capability:
                # Execute capability
                response = await self._execute_capability(capability, message, context)
            else:
                # Default response
                response = self._generate_default_response(message, memories)
            
            # Store interaction in memory
            await self.memory_manager.store_interaction(
                self.id,
                message,
                response,
                context=context
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process message: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _determine_capability(
        self,
        message: str,
        memories: List[Dict[str, Any]]
    ) -> Optional[AgentCapability]:
        """Determine which capability to use for the message
        
        Args:
            message: Input message
            memories: Relevant memories
            
        Returns:
            Selected capability or None
        """
        try:
            # TODO: Implement more sophisticated capability selection
            # For now, return first matching capability
            for capability in self.capabilities:
                if capability.name.lower() in message.lower():
                    return capability
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to determine capability: {str(e)}")
            return None
    
    async def _execute_capability(
        self,
        capability: AgentCapability,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute a capability
        
        Args:
            capability: Capability to execute
            message: Input message
            context: Additional context
            
        Returns:
            Response message
        """
        try:
            if capability.name in self._capability_handlers:
                handler = self._capability_handlers[capability.name]
                return await handler(message, context)
            else:
                return f"I understand you want me to {capability.name}, but I don't have a handler for that yet."
            
        except Exception as e:
            logger.error(f"Failed to execute capability: {str(e)}")
            return f"I encountered an error while trying to {capability.name}: {str(e)}"
    
    def _generate_default_response(
        self,
        message: str,
        memories: List[Dict[str, Any]]
    ) -> str:
        """Generate a default response when no capability matches
        
        Args:
            message: Input message
            memories: Relevant memories
            
        Returns:
            Default response message
        """
        try:
            # Use personality traits to influence response
            traits = self.personality.traits
            
            if traits.get("helpfulness", 0.5) > 0.7:
                return "I'm here to help! Could you please clarify what you'd like me to do?"
            elif traits.get("directness", 0.5) > 0.7:
                return "I don't have a specific capability for that request. What would you like me to do?"
            else:
                return "I'm not sure how to help with that. Could you please rephrase your request?"
            
        except Exception as e:
            logger.error(f"Failed to generate default response: {str(e)}")
            return "I apologize, but I'm not sure how to respond to that."
    
    async def _save_agent_definition(self) -> None:
        """Save agent definition to database"""
        try:
            agent_data = {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "capabilities": [
                    {
                        "name": cap.name,
                        "description": cap.description,
                        "parameters": cap.parameters,
                        "return_type": cap.return_type,
                        "examples": cap.examples
                    }
                    for cap in self.capabilities
                ],
                "personality": {
                    "traits": self.personality.traits,
                    "communication_style": self.personality.communication_style,
                    "decision_making_style": self.personality.decision_making_style,
                    "expertise_level": self.personality.expertise_level,
                    "metadata": self.personality.metadata
                },
                "metadata": self.metadata,
                "created_at": self.created_at.isoformat(),
                "last_active": self.last_active.isoformat(),
                "status": self.status
            }
            
            await self.mongodb.update_document(
                "custom_agents",
                {"id": self.id},
                agent_data,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Failed to save agent definition: {str(e)}")
            raise
    
    async def update_status(self, status: str) -> None:
        """Update agent status
        
        Args:
            status: New status
        """
        try:
            self.status = status
            self.last_active = datetime.now()
            await self._save_agent_definition()
            
        except Exception as e:
            logger.error(f"Failed to update status: {str(e)}")
            raise
    
    async def add_capability(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        return_type: str,
        handler: callable,
        examples: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add a new capability to the agent
        
        Args:
            name: Capability name
            description: Capability description
            parameters: Parameter definitions
            return_type: Return type
            handler: Handler function
            examples: Example usages
        """
        try:
            # Create capability
            capability = AgentCapability(
                name=name,
                description=description,
                parameters=parameters,
                return_type=return_type,
                examples=examples
            )
            
            # Add to capabilities list
            self.capabilities.append(capability)
            
            # Add handler
            self._capability_handlers[name] = handler
            
            # Save updated definition
            await self._save_agent_definition()
            
        except Exception as e:
            logger.error(f"Failed to add capability: {str(e)}")
            raise
    
    async def update_personality(
        self,
        traits: Optional[Dict[str, float]] = None,
        communication_style: Optional[str] = None,
        decision_making_style: Optional[str] = None,
        expertise_level: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update agent personality
        
        Args:
            traits: Updated traits
            communication_style: Updated communication style
            decision_making_style: Updated decision making style
            expertise_level: Updated expertise level
            metadata: Updated metadata
        """
        try:
            if traits:
                self.personality.traits.update(traits)
            if communication_style:
                self.personality.communication_style = communication_style
            if decision_making_style:
                self.personality.decision_making_style = decision_making_style
            if expertise_level is not None:
                self.personality.expertise_level = expertise_level
            if metadata:
                self.personality.metadata.update(metadata)
            
            # Save updated definition
            await self._save_agent_definition()
            
        except Exception as e:
            logger.error(f"Failed to update personality: {str(e)}")
            raise
    
    @classmethod
    async def load_agent(
        cls,
        orchestrator: Orchestrator,
        memory_manager: MemoryManager,
        mongodb: MongoDB,
        agent_id: str
    ) -> 'CustomAgent':
        """Load a custom agent from database
        
        Args:
            orchestrator: Orchestrator instance
            memory_manager: Memory manager instance
            mongodb: MongoDB instance
            agent_id: Agent ID
            
        Returns:
            Loaded custom agent
        """
        try:
            # Load agent data
            agent_data = await mongodb.get_document(
                "custom_agents",
                {"id": agent_id}
            )
            
            if not agent_data:
                raise ValueError(f"Agent not found: {agent_id}")
            
            # Create capabilities
            capabilities = [
                AgentCapability(
                    name=cap["name"],
                    description=cap["description"],
                    parameters=cap["parameters"],
                    return_type=cap["return_type"],
                    examples=cap.get("examples")
                )
                for cap in agent_data["capabilities"]
            ]
            
            # Create personality
            personality = AgentPersonality(
                traits=agent_data["personality"]["traits"],
                communication_style=agent_data["personality"]["communication_style"],
                decision_making_style=agent_data["personality"]["decision_making_style"],
                expertise_level=agent_data["personality"]["expertise_level"],
                metadata=agent_data["personality"].get("metadata")
            )
            
            # Create agent
            agent = cls(
                orchestrator=orchestrator,
                memory_manager=memory_manager,
                mongodb=mongodb,
                name=agent_data["name"],
                description=agent_data["description"],
                capabilities=capabilities,
                personality=personality,
                metadata=agent_data.get("metadata")
            )
            
            # Set additional attributes
            agent.id = agent_data["id"]
            agent.created_at = datetime.fromisoformat(agent_data["created_at"])
            agent.last_active = datetime.fromisoformat(agent_data["last_active"])
            agent.status = agent_data["status"]
            
            return agent
            
        except Exception as e:
            logger.error(f"Failed to load agent: {str(e)}")
            raise 