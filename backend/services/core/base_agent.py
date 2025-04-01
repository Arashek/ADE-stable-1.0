"""
Base Agent Module for ADE Platform

This module defines the BaseAgent class that all specialized agents inherit from.
It provides common functionality and interfaces for agent operations.
"""

import logging
from typing import Dict, List, Any, Optional
from enum import Enum
import json
import uuid

class AgentStatus(str, Enum):
    """Enum representing the possible statuses of an agent"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"

class BaseAgent:
    """Base class for all specialized agents in the ADE platform"""
    
    def __init__(self, agent_id: str):
        """Initialize the base agent with a unique ID
        
        Args:
            agent_id: Unique identifier for the agent
        """
        self.agent_id = agent_id
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.task_history = []
        self.capabilities = {}
    
    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task assigned to the agent
        
        Args:
            task_data: Dictionary containing task information
            
        Returns:
            Dictionary containing the results of the task processing
        """
        task_id = task_data.get("task_id", str(uuid.uuid4()))
        self.logger.info(f"Processing task {task_id}")
        
        try:
            self.status = AgentStatus.BUSY
            result = self._execute_task(task_data)
            self.status = AgentStatus.IDLE
            
            # Record task in history
            self.task_history.append({
                "task_id": task_id,
                "status": "completed",
                "result": "success"
            })
            
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result
            }
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"Error processing task {task_id}: {str(e)}")
            
            # Record task in history
            self.task_history.append({
                "task_id": task_id,
                "status": "failed",
                "error": str(e)
            })
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e)
            }
    
    def _execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the task logic (to be implemented by derived classes)
        
        Args:
            task_data: Dictionary containing task information
            
        Returns:
            Dictionary containing the results of the task execution
        """
        raise NotImplementedError("Subclasses must implement _execute_task")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent
        
        Returns:
            Dictionary containing status information
        """
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "task_count": len(self.task_history),
            "capabilities": list(self.capabilities.keys())
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the agent
        
        Returns:
            Dictionary containing capability information
        """
        return self.capabilities
    
    def register_capability(self, capability_name: str, capability_info: Dict[str, Any]) -> None:
        """Register a new capability for the agent
        
        Args:
            capability_name: Name of the capability
            capability_info: Dictionary containing capability information
        """
        self.capabilities[capability_name] = capability_info
        self.logger.info(f"Registered capability: {capability_name}")
