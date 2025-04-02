"""
Task Allocator Service

This module implements a task allocation algorithm for specialized agents
based on complexity, priority, and resource requirements.
"""

import os
import sys
import logging
import asyncio
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import error logging if available
try:
    from scripts.basic_error_logging import log_error, ErrorCategory, ErrorSeverity
    error_logging_available = True
except ImportError:
    error_logging_available = False
    # Define fallback error categories and severities
    class ErrorCategory:
        TASK_ALLOCATION = "TASK_ALLOCATION"
        SYSTEM = "SYSTEM"
    
    class ErrorSeverity:
        ERROR = "ERROR"
        WARNING = "WARNING"
        INFO = "INFO"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("task_allocator")

class TaskPriority:
    """Task priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskComplexity:
    """Task complexity levels"""
    SIMPLE = "simple"      # Basic tasks requiring minimal resources
    MODERATE = "moderate"  # Medium complexity tasks
    COMPLEX = "complex"    # Complex tasks requiring significant resources
    CRITICAL = "critical"  # Mission-critical tasks with highest priority

class TaskStatus:
    """Task status values"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class AgentStatus:
    """Agent status values"""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    OVERLOADED = "overloaded"
    MAINTENANCE = "maintenance"

class TaskAllocationStrategy:
    """Base class for task allocation strategies"""
    
    def allocate(self, tasks: List[Dict[str, Any]], agents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Allocate tasks to agents
        
        Args:
            tasks: List of tasks with their details
            agents: List of agents with their details
            
        Returns:
            Dict[str, List[str]]: Agent IDs mapped to lists of task IDs
        """
        raise NotImplementedError("Allocation strategy not implemented")

class SimpleRoundRobinAllocator(TaskAllocationStrategy):
    """Allocates tasks in a simple round-robin fashion"""
    
    def allocate(self, tasks: List[Dict[str, Any]], agents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Allocate tasks using round-robin"""
        allocations = {agent["id"]: [] for agent in agents if agent["status"] == AgentStatus.AVAILABLE}
        available_agents = [agent["id"] for agent in agents if agent["status"] == AgentStatus.AVAILABLE]
        
        if not available_agents:
            logger.warning("No available agents for task allocation")
            return {}
        
        agent_idx = 0
        for task in tasks:
            if task["status"] != TaskStatus.PENDING:
                continue
                
            agent_id = available_agents[agent_idx]
            allocations[agent_id].append(task["id"])
            
            # Move to next agent (round-robin)
            agent_idx = (agent_idx + 1) % len(available_agents)
        
        return allocations

class PriorityBasedAllocator(TaskAllocationStrategy):
    """Allocates tasks based on priority and agent capabilities"""
    
    def allocate(self, tasks: List[Dict[str, Any]], agents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Allocate tasks based on priority"""
        allocations = {agent["id"]: [] for agent in agents if agent["status"] == AgentStatus.AVAILABLE}
        available_agents = [agent for agent in agents if agent["status"] == AgentStatus.AVAILABLE]
        
        if not available_agents:
            logger.warning("No available agents for task allocation")
            return {}
        
        # Sort tasks by priority (high to low)
        priority_order = {
            TaskPriority.HIGH: 0,
            TaskPriority.MEDIUM: 1,
            TaskPriority.LOW: 2
        }
        sorted_tasks = sorted(
            [t for t in tasks if t["status"] == TaskStatus.PENDING], 
            key=lambda t: priority_order.get(t.get("priority", TaskPriority.MEDIUM), 1)
        )
        
        # Track agent loads
        agent_loads = {agent["id"]: 0 for agent in available_agents}
        
        for task in sorted_tasks:
            # Find best agent for task based on capabilities and current load
            best_agent = None
            best_score = -1
            
            for agent in available_agents:
                # Calculate capability match score
                score = self._calculate_agent_task_match(agent, task)
                
                # Adjust score based on current load (prefer less loaded agents)
                load_factor = 1.0 / (1.0 + agent_loads[agent["id"]])
                score *= load_factor
                
                if score > best_score:
                    best_score = score
                    best_agent = agent
            
            if best_agent:
                allocations[best_agent["id"]].append(task["id"])
                agent_loads[best_agent["id"]] += self._get_task_weight(task)
        
        return allocations
    
    def _calculate_agent_task_match(self, agent: Dict[str, Any], task: Dict[str, Any]) -> float:
        """Calculate match score between an agent and task"""
        # Base score of 0.5
        score = 0.5
        
        # Check if agent has required capabilities
        required_capabilities = task.get("required_capabilities", [])
        agent_capabilities = agent.get("capabilities", [])
        
        if required_capabilities:
            capability_match_ratio = sum(1 for cap in required_capabilities if cap in agent_capabilities) / len(required_capabilities)
            score = capability_match_ratio
        
        # Bonus for specialized agents
        if task.get("type") == agent.get("specialization"):
            score += 0.3
        
        # Adjust based on agent performance history
        if "performance" in agent:
            score *= (1.0 + agent["performance"] / 100)
        
        return score
    
    def _get_task_weight(self, task: Dict[str, Any]) -> float:
        """Get the computational weight of a task"""
        complexity_weights = {
            TaskComplexity.SIMPLE: 1.0,
            TaskComplexity.MODERATE: 2.0,
            TaskComplexity.COMPLEX: 3.0,
            TaskComplexity.CRITICAL: 4.0
        }
        
        return complexity_weights.get(task.get("complexity", TaskComplexity.MODERATE), 2.0)

class WorkloadBalancingAllocator(TaskAllocationStrategy):
    """Allocates tasks with focus on balancing workload across agents"""
    
    def allocate(self, tasks: List[Dict[str, Any]], agents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Allocate tasks while balancing workload"""
        allocations = {agent["id"]: [] for agent in agents if agent["status"] == AgentStatus.AVAILABLE}
        available_agents = [agent for agent in agents if agent["status"] == AgentStatus.AVAILABLE]
        
        if not available_agents:
            logger.warning("No available agents for task allocation")
            return {}
        
        # Group tasks by their type
        task_groups = {}
        for task in tasks:
            if task["status"] != TaskStatus.PENDING:
                continue
            
            task_type = task.get("type", "unknown")
            if task_type not in task_groups:
                task_groups[task_type] = []
            task_groups[task_type].append(task)
        
        # Sort each group by priority
        priority_order = {
            TaskPriority.HIGH: 0,
            TaskPriority.MEDIUM: 1,
            TaskPriority.LOW: 2
        }
        for task_type in task_groups:
            task_groups[task_type] = sorted(
                task_groups[task_type],
                key=lambda t: priority_order.get(t.get("priority", TaskPriority.MEDIUM), 1)
            )
        
        # Calculate initial agent scores based on capabilities
        agent_scores = {}
        for task_type in task_groups:
            agent_scores[task_type] = {}
            for agent in available_agents:
                # Calculate base score for this agent and task type
                capability_score = 0.5  # Base score
                
                # Bonus for specialization
                if agent.get("specialization") == task_type:
                    capability_score += 0.3
                
                # Bonus for performance history with this task type
                if "performance_by_type" in agent and task_type in agent["performance_by_type"]:
                    capability_score *= (1.0 + agent["performance_by_type"][task_type] / 100)
                
                agent_scores[task_type][agent["id"]] = capability_score
        
        # Track agent workloads
        agent_workloads = {agent["id"]: 0.0 for agent in available_agents}
        
        # Distribute tasks
        for task_type, type_tasks in task_groups.items():
            for task in type_tasks:
                # Find agent with best combination of capability and available capacity
                best_agent_id = None
                best_allocation_score = -1
                
                for agent in available_agents:
                    # Skip agents that don't have the required capabilities
                    required_capabilities = task.get("required_capabilities", [])
                    agent_capabilities = agent.get("capabilities", [])
                    
                    if required_capabilities and not all(cap in agent_capabilities for cap in required_capabilities):
                        continue
                    
                    # Calculate allocation score
                    capability_score = agent_scores[task_type][agent["id"]]
                    workload_factor = 1.0 / (1.0 + agent_workloads[agent["id"]])
                    allocation_score = capability_score * workload_factor
                    
                    if allocation_score > best_allocation_score:
                        best_allocation_score = allocation_score
                        best_agent_id = agent["id"]
                
                if best_agent_id:
                    allocations[best_agent_id].append(task["id"])
                    task_weight = self._get_task_weight(task)
                    agent_workloads[best_agent_id] += task_weight
        
        return allocations
    
    def _get_task_weight(self, task: Dict[str, Any]) -> float:
        """Get the computational weight of a task"""
        complexity_weights = {
            TaskComplexity.SIMPLE: 1.0,
            TaskComplexity.MODERATE: 2.0,
            TaskComplexity.COMPLEX: 3.0,
            TaskComplexity.CRITICAL: 4.0
        }
        
        base_weight = complexity_weights.get(task.get("complexity", TaskComplexity.MODERATE), 2.0)
        
        # Adjust weight based on priority
        priority_factors = {
            TaskPriority.HIGH: 1.2,
            TaskPriority.MEDIUM: 1.0,
            TaskPriority.LOW: 0.8
        }
        priority_factor = priority_factors.get(task.get("priority", TaskPriority.MEDIUM), 1.0)
        
        return base_weight * priority_factor

class TaskAllocatorService:
    """
    Service for allocating tasks to specialized agents based on various strategies.
    This service considers task complexity, priority, and agent capabilities.
    """
    
    def __init__(self, strategy: str = "workload_balancing"):
        """
        Initialize the task allocator service
        
        Args:
            strategy: Allocation strategy ("round_robin", "priority_based", "workload_balancing")
        """
        self.set_strategy(strategy)
        logger.info(f"Task Allocator Service initialized with strategy: {strategy}")
    
    def set_strategy(self, strategy: str) -> None:
        """Set the allocation strategy"""
        strategies = {
            "round_robin": SimpleRoundRobinAllocator(),
            "priority_based": PriorityBasedAllocator(),
            "workload_balancing": WorkloadBalancingAllocator()
        }
        
        if strategy not in strategies:
            logger.warning(f"Unknown allocation strategy: {strategy}, defaulting to workload_balancing")
            strategy = "workload_balancing"
        
        self.strategy = strategies[strategy]
        self.current_strategy_name = strategy
    
    async def allocate_tasks(self, tasks: List[Dict[str, Any]], agents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Allocate tasks to agents using the current strategy
        
        Args:
            tasks: List of tasks with their details
            agents: List of agents with their details
            
        Returns:
            Dict[str, List[str]]: Agent IDs mapped to lists of task IDs
        """
        try:
            logger.info(f"Allocating {len([t for t in tasks if t['status'] == TaskStatus.PENDING])} pending tasks to {len([a for a in agents if a['status'] == AgentStatus.AVAILABLE])} available agents")
            allocations = self.strategy.allocate(tasks, agents)
            
            # Log allocation results
            total_allocated = sum(len(tasks) for tasks in allocations.values())
            logger.info(f"Allocated {total_allocated} tasks using {self.current_strategy_name} strategy")
            
            return allocations
        except Exception as e:
            if error_logging_available:
                log_error(
                    error=e,
                    category=ErrorCategory.TASK_ALLOCATION,
                    severity=ErrorSeverity.ERROR,
                    component="task_allocator",
                    context={"strategy": self.current_strategy_name}
                )
            logger.error(f"Error during task allocation: {str(e)}")
            return {}
    
    async def suggest_optimal_strategy(self, tasks: List[Dict[str, Any]], agents: List[Dict[str, Any]]) -> str:
        """
        Suggest the optimal allocation strategy for the current tasks and agents
        
        Args:
            tasks: List of tasks with their details
            agents: List of agents with their details
            
        Returns:
            str: Recommended strategy name
        """
        try:
            # Count tasks by complexity
            pending_tasks = [t for t in tasks if t["status"] == TaskStatus.PENDING]
            available_agents = [a for a in agents if a["status"] == AgentStatus.AVAILABLE]
            
            if not pending_tasks or not available_agents:
                return "round_robin"  # Default when no tasks or agents
            
            # Count tasks by complexity
            complexity_counts = {}
            for task in pending_tasks:
                complexity = task.get("complexity", TaskComplexity.MODERATE)
                complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
            
            # Count tasks by priority
            priority_counts = {}
            for task in pending_tasks:
                priority = task.get("priority", TaskPriority.MEDIUM)
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Calculate metrics
            total_tasks = len(pending_tasks)
            high_priority_ratio = priority_counts.get(TaskPriority.HIGH, 0) / total_tasks if total_tasks > 0 else 0
            complex_task_ratio = (complexity_counts.get(TaskComplexity.COMPLEX, 0) + 
                                  complexity_counts.get(TaskComplexity.CRITICAL, 0)) / total_tasks if total_tasks > 0 else 0
            
            # Decide based on metrics
            if high_priority_ratio > 0.3:
                # Many high priority tasks - use priority-based
                return "priority_based"
            elif complex_task_ratio > 0.3:
                # Many complex tasks - use workload balancing
                return "workload_balancing"
            elif len(pending_tasks) < len(available_agents) * 2:
                # Few tasks compared to agents - simple round robin is fine
                return "round_robin"
            else:
                # Default to workload balancing for balanced performance
                return "workload_balancing"
            
        except Exception as e:
            if error_logging_available:
                log_error(
                    error=e,
                    category=ErrorCategory.TASK_ALLOCATION,
                    severity=ErrorSeverity.WARNING,
                    component="task_allocator",
                    context={"operation": "suggest_strategy"}
                )
            logger.warning(f"Error suggesting optimal strategy: {str(e)}")
            return "workload_balancing"  # Default to workload balancing on error

# Singleton instance
_allocator_instance = None

def get_task_allocator(strategy: str = "workload_balancing") -> TaskAllocatorService:
    """
    Get the singleton instance of the task allocator service
    
    Args:
        strategy: Allocation strategy
        
    Returns:
        TaskAllocatorService: The singleton instance
    """
    global _allocator_instance
    
    if _allocator_instance is None:
        _allocator_instance = TaskAllocatorService(strategy)
    elif strategy != _allocator_instance.current_strategy_name:
        _allocator_instance.set_strategy(strategy)
    
    return _allocator_instance
