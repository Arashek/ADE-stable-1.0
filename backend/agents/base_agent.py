"""
Base Agent Module

This module provides the BaseAgent class that all specialized agents inherit from.
It defines the common interface and functionality for all agents in the ADE platform.
"""

from typing import Dict, List, Any, Optional
import logging
import asyncio
import uuid

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for all agents in the ADE platform"""
    
    def __init__(self, agent_id: Optional[str] = None, agent_type: str = "base"):
        """Initialize the base agent
        
        Args:
            agent_id: Unique identifier for this agent instance
            agent_type: Type of agent (e.g., 'design', 'development')
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.agent_type = agent_type
        self.status = "initialized"
        self.capabilities = []
        logger.info(f"Initialized {agent_type} agent with ID {self.agent_id}")
    
    async def initialize(self) -> bool:
        """Initialize the agent's resources and connections
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        self.status = "ready"
        return True
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request and return a response
        
        Args:
            request: Dictionary containing the request parameters
            
        Returns:
            Dict[str, Any]: Response from the agent
        """
        raise NotImplementedError("Subclasses must implement process_request()")
    
    async def cleanup(self) -> bool:
        """Clean up resources used by the agent
        
        Returns:
            bool: True if cleanup was successful, False otherwise
        """
        self.status = "terminated"
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent
        
        Returns:
            Dict[str, Any]: Dictionary with status information
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "capabilities": self.capabilities
        }
