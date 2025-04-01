"""
Agent Coordinator Module

This module is responsible for coordinating the specialized agents in the ADE platform.
It manages the workflow between different agents and handles the orchestration of tasks.
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
import json
import asyncio
import traceback
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import error logging system
try:
    from scripts.basic_error_logging import log_error, ErrorCategory, ErrorSeverity
    error_logging_available = True
except ImportError:
    error_logging_available = False
    # Define fallback error categories and severities
    class ErrorCategory:
        COORDINATION = "COORDINATION"
        AGENT = "AGENT"
        COMMUNICATION = "COMMUNICATION"
        PROCESSING = "PROCESSING"
        SYSTEM = "SYSTEM"
        API = "API"
        VALIDATION = "VALIDATION"
        TASK = "TASK"
    
    class ErrorSeverity:
        CRITICAL = "CRITICAL"
        ERROR = "ERROR"
        WARNING = "WARNING"
        INFO = "INFO"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("agent_coordinator")

class AgentCoordinator:
    """
    The AgentCoordinator class is responsible for coordinating the different
    specialized agents in the ADE platform. It manages the workflow between
    agents and ensures proper task execution and data flow.
    """
    
    def __init__(self):
        """Initialize the agent coordinator"""
        self.agents = {}
        self.active_tasks = {}
        self.task_history = []
        self.errors = []
        logger.info("Agent Coordinator initialized")
    
    def log_error(self, error: Any, category: str = ErrorCategory.COORDINATION, 
                  severity: str = ErrorSeverity.ERROR, context: Dict[str, Any] = None):
        """
        Log an error using the error logging system
        
        Args:
            error: The error object or message
            category: Category of the error
            severity: Severity level of the error
            context: Additional context information
        """
        error_message = str(error)
        
        # Log to console
        logger.error(f"Error [{category}][{severity}]: {error_message}")
        
        # Log to error logging system if available
        if error_logging_available:
            try:
                error_id = log_error(
                    error=error,
                    category=category,
                    severity=severity,
                    component="agent_coordinator",
                    source="backend.agents.agent_coordinator",
                    context=context or {}
                )
                self.errors.append({
                    "id": error_id,
                    "message": error_message,
                    "category": category,
                    "severity": severity,
                    "context": context or {}
                })
            except Exception as e:
                logger.error(f"Failed to log error: {str(e)}")
    
    async def register_agent(self, agent_type: str, agent_instance: Any) -> bool:
        """
        Register a specialized agent with the coordinator
        
        Args:
            agent_type: Type of the agent (e.g., "design", "development")
            agent_instance: Instance of the specialized agent
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            if agent_type in self.agents:
                logger.warning(f"Agent of type {agent_type} already registered")
                return False
                
            self.agents[agent_type] = agent_instance
            logger.info(f"Registered agent of type: {agent_type}")
            return True
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.COORDINATION,
                severity=ErrorSeverity.ERROR,
                context={"action": "register_agent", "agent_type": agent_type}
            )
            return False
    
    async def start_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a new task with the appropriate specialized agent
        
        Args:
            task_data: Data for the task including type, requirements, etc.
            
        Returns:
            Dict: Task information including ID and status
        """
        try:
            task_id = f"task_{len(self.task_history) + 1}"
            task_type = task_data.get("type", "unknown")
            
            # Determine which agent should handle this task
            agent_type = self._determine_agent_type(task_type, task_data)
            
            if agent_type not in self.agents:
                error_msg = f"No agent available for type: {agent_type}"
                self.log_error(
                    error=error_msg,
                    category=ErrorCategory.COORDINATION,
                    severity=ErrorSeverity.ERROR,
                    context={"task_id": task_id, "task_type": task_type, "agent_type": agent_type}
                )
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "error": error_msg
                }
            
            # Create task entry
            task_entry = {
                "id": task_id,
                "type": task_type,
                "agent_type": agent_type,
                "status": "started",
                "data": task_data,
                "result": None
            }
            
            # Store in active tasks
            self.active_tasks[task_id] = task_entry
            self.task_history.append(task_entry)
            
            # Log the task start
            logger.info(f"Started task {task_id} of type {task_type} with agent {agent_type}")
            
            # For now, we'll just return the task info
            # In a real implementation, this would kick off an async task
            return {
                "task_id": task_id,
                "status": "started",
                "agent_type": agent_type
            }
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.COORDINATION,
                severity=ErrorSeverity.ERROR,
                context={"action": "start_task", "task_data": task_data}
            )
            return {
                "task_id": f"error_{len(self.task_history) + 1}",
                "status": "failed",
                "error": f"Internal error: {str(e)}"
            }
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the current status of a task
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            Dict: Current status and information about the task
        """
        try:
            if task_id not in self.active_tasks:
                logger.warning(f"Task {task_id} not found")
                return {
                    "task_id": task_id,
                    "status": "not_found"
                }
                
            return self.active_tasks[task_id]
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.COORDINATION,
                severity=ErrorSeverity.ERROR,
                context={"action": "get_task_status", "task_id": task_id}
            )
            return {
                "task_id": task_id,
                "status": "error",
                "error": f"Internal error: {str(e)}"
            }
    
    async def update_task_status(self, task_id: str, status: str, result: Any = None) -> bool:
        """
        Update the status of a task
        
        Args:
            task_id: ID of the task to update
            status: New status for the task
            result: Optional result data
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            if task_id not in self.active_tasks:
                logger.warning(f"Task {task_id} not found for status update")
                return False
                
            self.active_tasks[task_id]["status"] = status
            
            if result is not None:
                self.active_tasks[task_id]["result"] = result
                
            logger.info(f"Updated task {task_id} status to {status}")
            
            # If task is completed or failed, update task history
            if status in ["completed", "failed"]:
                task_index = next((i for i, task in enumerate(self.task_history) 
                                  if task["id"] == task_id), None)
                if task_index is not None:
                    self.task_history[task_index] = self.active_tasks[task_id]
                
                # Log failed tasks as errors
                if status == "failed" and result:
                    error_message = result.get("error", "Unknown error")
                    self.log_error(
                        error=error_message,
                        category=ErrorCategory.TASK,
                        severity=ErrorSeverity.ERROR,
                        context={
                            "task_id": task_id,
                            "task_type": self.active_tasks[task_id].get("type"),
                            "agent_type": self.active_tasks[task_id].get("agent_type")
                        }
                    )
            
            return True
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.COORDINATION,
                severity=ErrorSeverity.ERROR,
                context={"action": "update_task_status", "task_id": task_id, "status": status}
            )
            return False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent coordination system
        
        Returns:
            Dict: System status information
        """
        try:
            # Count errors by severity
            error_counts = {}
            for error in self.errors:
                severity = error.get("severity", "UNKNOWN")
                error_counts[severity] = error_counts.get(severity, 0) + 1
            
            return {
                "registered_agents": list(self.agents.keys()),
                "active_tasks": len(self.active_tasks),
                "total_tasks": len(self.task_history),
                "errors": {
                    "total": len(self.errors),
                    "by_severity": error_counts
                },
                "status": "operational"
            }
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.COORDINATION,
                severity=ErrorSeverity.ERROR,
                context={"action": "get_system_status"}
            )
            return {
                "status": "error",
                "error": f"Internal error: {str(e)}"
            }
    
    def _determine_agent_type(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """
        Determine which agent type should handle a given task
        
        Args:
            task_type: Type of the task
            task_data: Additional task data
            
        Returns:
            str: Agent type that should handle this task
        """
        try:
            # Simple mapping of task types to agent types
            task_agent_mapping = {
                "design": "design",
                "development": "development",
                "requirements": "requirements",
                "testing": "testing",
                "deployment": "deployment",
                "documentation": "documentation"
            }
            
            return task_agent_mapping.get(task_type.lower(), "development")
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.COORDINATION,
                severity=ErrorSeverity.ERROR,
                context={"action": "_determine_agent_type", "task_type": task_type}
            )
            return "development"  # Default to development agent as fallback

# Singleton instance of the agent coordinator
_coordinator_instance = None

def get_coordinator() -> AgentCoordinator:
    """
    Get the singleton instance of the agent coordinator
    
    Returns:
        AgentCoordinator: The singleton instance
    """
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = AgentCoordinator()
    return _coordinator_instance
