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
import time
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import services
try:
    from backend.services.task_allocator import get_task_allocator, TaskStatus, TaskPriority, TaskComplexity
    from backend.services.agent_cache import get_agent_cache
    task_allocator_available = True
    agent_cache_available = True
except ImportError:
    task_allocator_available = False
    agent_cache_available = False

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
        
        # Initialize services if available
        self.task_allocator = get_task_allocator() if task_allocator_available else None
        self.agent_cache = get_agent_cache() if agent_cache_available else None
        
        # Set up agent statuses
        self.agent_statuses = {}
        
        logger.info("Agent Coordinator initialized")
        if self.task_allocator:
            logger.info("Task Allocator service connected")
        if self.agent_cache:
            logger.info("Agent Cache service connected")
    
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
            
            # Initialize agent status
            self.agent_statuses[agent_type] = {
                "type": agent_type,
                "status": "available",
                "capabilities": getattr(agent_instance, 'capabilities', []),
                "specialization": agent_type,
                "performance": 1.0,
                "performance_by_type": {},
                "last_update": datetime.now().isoformat(),
                "id": agent_type  # Use type as ID for simplicity
            }
            
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
            # Generate task ID
            task_id = f"task_{len(self.task_history) + 1}"
            task_type = task_data.get("type", "unknown")
            
            # Check cache if enabled
            if self.agent_cache:
                prompt = task_data.get("prompt", "")
                context = task_data.get("context", {})
                
                # Try to get from cache
                cache_hit, cached_response, processing_time = await self.agent_cache.get(task_type, prompt, context)
                
                if cache_hit:
                    logger.info(f"Cache hit for task type {task_type}, returning cached response")
                    # Create a completed task entry for the history
                    task_entry = {
                        "id": task_id,
                        "type": task_type,
                        "agent_type": task_type,  # Use task type as agent type for cached responses
                        "status": "completed",
                        "data": task_data,
                        "result": cached_response,
                        "cached": True,
                        "processing_time": processing_time
                    }
                    
                    # Store in task history
                    self.task_history.append(task_entry)
                    
                    return {
                        "task_id": task_id,
                        "status": "completed",
                        "result": cached_response,
                        "cached": True,
                        "processing_time": processing_time
                    }
            
            # If not in cache or cache not available, proceed with normal task allocation
            
            # If task allocator is available, use it to determine agent type
            if self.task_allocator:
                # Prepare task for allocator
                task_entry = {
                    "id": task_id,
                    "type": task_type,
                    "status": TaskStatus.PENDING,
                    "priority": task_data.get("priority", TaskPriority.MEDIUM),
                    "complexity": task_data.get("complexity", TaskComplexity.MODERATE),
                    "data": task_data,
                    "required_capabilities": task_data.get("required_capabilities", [])
                }
                
                # Get agent allocations
                allocations = await self.task_allocator.allocate_tasks([task_entry], list(self.agent_statuses.values()))
                
                # Find which agent was allocated this task
                agent_type = None
                for agent_id, task_ids in allocations.items():
                    if task_id in task_ids:
                        agent_type = agent_id
                        break
                
                # If no agent was allocated, use fallback method
                if not agent_type:
                    agent_type = self._determine_agent_type(task_type, task_data)
            else:
                # Use fallback method
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
                "result": None,
                "start_time": time.time()
            }
            
            # Store in active tasks
            self.active_tasks[task_id] = task_entry
            self.task_history.append(task_entry)
            
            # Update agent status
            if agent_type in self.agent_statuses:
                self.agent_statuses[agent_type]["status"] = "busy"
                self.agent_statuses[agent_type]["last_update"] = datetime.now().isoformat()
            
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
                # Check task history
                for task in self.task_history:
                    if task["id"] == task_id:
                        return task
                
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
            
            # Add processing time if task is completed
            if status in ["completed", "failed"] and "start_time" in self.active_tasks[task_id]:
                processing_time = time.time() - self.active_tasks[task_id]["start_time"]
                self.active_tasks[task_id]["processing_time"] = processing_time
                
                # Cache successful results if cache is available
                if status == "completed" and self.agent_cache:
                    task_data = self.active_tasks[task_id]["data"]
                    prompt = task_data.get("prompt", "")
                    context = task_data.get("context", {})
                    
                    if prompt:  # Only cache if there's a prompt
                        task_type = self.active_tasks[task_id]["type"]
                        await self.agent_cache.set(
                            task_type, 
                            prompt, 
                            result, 
                            processing_time,
                            context
                        )
                        logger.info(f"Cached result for task {task_id} of type {task_type}")
            
            # Update agent status if task is completed or failed
            if status in ["completed", "failed"]:
                agent_type = self.active_tasks[task_id]["agent_type"]
                if agent_type in self.agent_statuses:
                    self.agent_statuses[agent_type]["status"] = "available"
                    self.agent_statuses[agent_type]["last_update"] = datetime.now().isoformat()
                    
                    # Update agent performance metrics
                    if "performance_by_type" not in self.agent_statuses[agent_type]:
                        self.agent_statuses[agent_type]["performance_by_type"] = {}
                    
                    task_type = self.active_tasks[task_id]["type"]
                    is_success = status == "completed"
                    
                    if task_type not in self.agent_statuses[agent_type]["performance_by_type"]:
                        self.agent_statuses[agent_type]["performance_by_type"][task_type] = 1.0 if is_success else 0.5
                    else:
                        # Adjust performance score (success improves, failure reduces)
                        current = self.agent_statuses[agent_type]["performance_by_type"][task_type]
                        if is_success:
                            # Increase performance score (up to 2.0 max)
                            self.agent_statuses[agent_type]["performance_by_type"][task_type] = min(2.0, current * 1.1)
                        else:
                            # Decrease performance score (to min 0.5)
                            self.agent_statuses[agent_type]["performance_by_type"][task_type] = max(0.5, current * 0.9)
                
            logger.info(f"Updated task {task_id} status to {status}")
            
            # If task is completed or failed, update task history
            if status in ["completed", "failed"]:
                task_index = next((i for i, task in enumerate(self.task_history) 
                                  if task["id"] == task_id), None)
                if task_index is not None:
                    self.task_history[task_index] = self.active_tasks[task_id]
                    # Remove from active tasks
                    del self.active_tasks[task_id]
                
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
            
            # Get cache stats if available
            cache_stats = None
            if self.agent_cache:
                cache_stats = await self.agent_cache.get_stats()
            
            return {
                "registered_agents": list(self.agents.keys()),
                "agent_statuses": self.agent_statuses,
                "active_tasks": len(self.active_tasks),
                "total_tasks": len(self.task_history),
                "errors": {
                    "total": len(self.errors),
                    "by_severity": error_counts
                },
                "services": {
                    "task_allocator": {
                        "available": task_allocator_available,
                        "strategy": self.task_allocator.current_strategy_name if self.task_allocator else None
                    },
                    "agent_cache": {
                        "available": agent_cache_available,
                        "stats": cache_stats
                    }
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
    
    async def optimize_allocation_strategy(self) -> str:
        """
        Optimize the task allocation strategy based on current workload
        
        Returns:
            str: The chosen strategy name
        """
        if not self.task_allocator:
            return "not_available"
        
        try:
            # Convert tasks to format expected by allocator
            tasks = []
            for task_id, task in self.active_tasks.items():
                tasks.append({
                    "id": task_id,
                    "type": task.get("type", "unknown"),
                    "status": task.get("status", "pending"),
                    "priority": task.get("priority", "medium"),
                    "complexity": task.get("complexity", "moderate"),
                    "required_capabilities": task.get("required_capabilities", [])
                })
            
            # Add recent history tasks for better optimization
            for task in self.task_history[-20:]:  # Last 20 tasks
                if task["id"] not in self.active_tasks:
                    tasks.append({
                        "id": task["id"],
                        "type": task.get("type", "unknown"),
                        "status": "completed",  # Already completed
                        "priority": task.get("priority", "medium"),
                        "complexity": task.get("complexity", "moderate"),
                        "required_capabilities": task.get("required_capabilities", [])
                    })
            
            # Get optimal strategy
            optimal_strategy = await self.task_allocator.suggest_optimal_strategy(tasks, list(self.agent_statuses.values()))
            
            # Apply the strategy
            self.task_allocator.set_strategy(optimal_strategy)
            logger.info(f"Optimized task allocation strategy to: {optimal_strategy}")
            
            return optimal_strategy
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.COORDINATION,
                severity=ErrorSeverity.WARNING,
                context={"action": "optimize_allocation_strategy"}
            )
            return "error"
    
    def _determine_agent_type(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """
        Determine which agent type should handle a given task (fallback method)
        
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
            return "development"  # Default fallback

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
