"""
Agent Coordination System for ADE Platform

This module implements the coordination system that enables collaboration between
specialized agents in the ADE platform. It manages task delegation, communication,
consensus building, and conflict resolution among agents.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import asyncio
import json
import uuid
from datetime import datetime

# Import specialized agents
from backend.services.agents.specialized.validation_agent import ValidationAgent
from backend.services.agents.specialized.design_agent import DesignAgent
from backend.services.agents.specialized.architecture_agent import ArchitectureAgent
from backend.services.agents.specialized.security_agent import SecurityAgent
from backend.services.agents.specialized.performance_agent import PerformanceAgent

# Import coordination components
from backend.services.coordination.agent_interface import AgentInterface, MessageType, AgentInterfaceFactory
from backend.services.coordination.agent_registry import AgentRegistry, AgentRegistryManager, AgentStatus
from backend.services.coordination.task_manager import TaskManager, TaskStatus
from backend.services.coordination.collaboration_patterns import CollaborationPatternFactory, PatternStrategyFactory
from backend.services.coordination.consensus_mechanism import ConsensusMechanism, ConflictDetector, ConflictResolutionStrategy

# Configure logging
logger = logging.getLogger(__name__)

class CollaborationPattern(Enum):
    """Enumeration of collaboration patterns for agent coordination"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ITERATIVE = "iterative"
    CONSENSUS = "consensus"

class TaskPriority(Enum):
    """Enumeration of task priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AgentCoordinator:
    """
    Coordinates collaboration between specialized agents in the ADE platform.
    
    This class is responsible for:
    1. Task delegation to appropriate agents
    2. Managing communication between agents
    3. Resolving conflicts in agent recommendations
    4. Building consensus for critical decisions
    5. Presenting unified results to the user
    """
    
    _instance = None
    
    def __new__(cls):
        """
        Create a singleton instance of the agent coordinator.
        
        Returns:
            Singleton instance of AgentCoordinator
        """
        if cls._instance is None:
            cls._instance = super(AgentCoordinator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialize the agent coordinator.
        """
        if self._initialized:
            return
        
        # Initialize task manager
        self.task_manager = TaskManager()
        
        # Initialize agent registry
        self.registry = AgentRegistry()
        self.registry_manager = AgentRegistryManager()
        
        # Initialize collaboration pattern factory
        self.pattern_factory = CollaborationPatternFactory()
        
        # Initialize consensus mechanism
        self.consensus_mechanism = ConsensusMechanism()
        
        # Initialize coordinator interface
        self.interface = AgentInterfaceFactory.create_interface(
            agent_id="coordinator",
            agent_type="coordinator"
        )
        
        # Initialize specialized agents
        self.specialized_agents = {}
        
        # Initialize agent priorities for conflict resolution
        self.agent_priorities = {
            "security": 5,  # Highest priority
            "architecture": 4,
            "validation": 3,
            "performance": 2,
            "design": 1     # Lowest priority
        }
        
        # Update consensus mechanism with agent priorities
        self.consensus_mechanism.agent_priorities = self.agent_priorities
        
        # Flag to track initialization status
        self._initialized = True
        
        # Initialize agents asynchronously
        asyncio.create_task(self._initialize_agents())
        
        logger.info("Agent coordinator initialized")
    
    async def _initialize_agents(self):
        """
        Initialize specialized agents and register them with the registry.
        """
        try:
            # Initialize validation agent
            validation_agent = ValidationAgent()
            validation_interface = AgentInterfaceFactory.create_interface(
                agent_id="validation_agent",
                agent_type="validation"
            )
            self.specialized_agents["validation"] = {
                "agent": validation_agent,
                "interface": validation_interface
            }
            await self.registry.register_agent(
                agent_id="validation_agent",
                agent_type="validation",
                capabilities=["code_review", "validation"],
                interface=validation_interface
            )
            
            # Initialize design agent
            design_agent = DesignAgent()
            design_interface = AgentInterfaceFactory.create_interface(
                agent_id="design_agent",
                agent_type="design"
            )
            self.specialized_agents["design"] = {
                "agent": design_agent,
                "interface": design_interface
            }
            await self.registry.register_agent(
                agent_id="design_agent",
                agent_type="design",
                capabilities=["design_creation", "design_review"],
                interface=design_interface
            )
            
            # Initialize architecture agent
            architecture_agent = ArchitectureAgent()
            architecture_interface = AgentInterfaceFactory.create_interface(
                agent_id="architecture_agent",
                agent_type="architecture"
            )
            self.specialized_agents["architecture"] = {
                "agent": architecture_agent,
                "interface": architecture_interface
            }
            await self.registry.register_agent(
                agent_id="architecture_agent",
                agent_type="architecture",
                capabilities=["architecture_analysis", "code_review"],
                interface=architecture_interface
            )
            
            # Initialize security agent
            security_agent = SecurityAgent()
            security_interface = AgentInterfaceFactory.create_interface(
                agent_id="security_agent",
                agent_type="security"
            )
            self.specialized_agents["security"] = {
                "agent": security_agent,
                "interface": security_interface
            }
            await self.registry.register_agent(
                agent_id="security_agent",
                agent_type="security",
                capabilities=["security_analysis", "code_review"],
                interface=security_interface
            )
            
            # Initialize performance agent
            performance_agent = PerformanceAgent()
            performance_interface = AgentInterfaceFactory.create_interface(
                agent_id="performance_agent",
                agent_type="performance"
            )
            self.specialized_agents["performance"] = {
                "agent": performance_agent,
                "interface": performance_interface
            }
            await self.registry.register_agent(
                agent_id="performance_agent",
                agent_type="performance",
                capabilities=["performance_analysis", "code_review"],
                interface=performance_interface
            )
            
            # Register coordinator with registry
            await self.registry.register_agent(
                agent_id="coordinator",
                agent_type="coordinator",
                capabilities=["requirements_analysis"],
                interface=self.interface
            )
            
            # Start message processing for all interfaces
            for agent_data in self.specialized_agents.values():
                asyncio.create_task(agent_data["interface"].process_messages())
            
            # Start message processing for coordinator interface
            asyncio.create_task(self.interface.process_messages())
            
            logger.info("All specialized agents initialized and registered")
        
        except Exception as e:
            logger.error("Error initializing agents: %s", str(e))
            raise
    
    async def process_user_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user request by coordinating specialized agents.
        
        Args:
            request: User request details
            
        Returns:
            Processing result
        """
        logger.info("Processing user request: %s", json.dumps(request))
        
        try:
            # Extract request details
            task_id = request.get("task_id", str(uuid.uuid4()))
            task_type = request.get("task_type", "unknown")
            requirements = request.get("requirements", {})
            collaboration_pattern_name = request.get(
                "collaboration_pattern", 
                CollaborationPattern.PARALLEL.value
            )
            priority = request.get("priority", TaskPriority.MEDIUM.value)
            
            # Create task if not already created
            if not await self.task_manager.get_task(task_id):
                await self.task_manager.create_task(
                    task_type=task_type,
                    requirements=requirements,
                    priority=priority
                )
            
            # Update task status
            await self.task_manager.update_task_status(
                task_id=task_id,
                status=TaskStatus.IN_PROGRESS.value
            )
            
            # Get collaboration pattern
            collaboration_pattern = self.pattern_factory.get_pattern(
                pattern_name=collaboration_pattern_name,
                task_type=task_type
            )
            
            # Determine required agent types based on task type and pattern
            required_agent_types = self._get_required_agent_types(task_type)
            
            # Get required capabilities based on task type
            required_capabilities = self._get_required_capabilities(task_type)
            
            # Select agents for the task
            selected_agents = await self._select_agents_for_task(
                required_agent_types, required_capabilities)
            
            if not selected_agents:
                error_msg = f"No suitable agents found for task type {task_type}"
                logger.error(error_msg)
                
                # Update task status
                await self.task_manager.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.FAILED.value,
                    error=error_msg
                )
                
                return {
                    "success": False,
                    "error": error_msg
                }
            
            # Create collaboration strategy
            strategy = collaboration_pattern.create_strategy(
                coordinator=self,
                task_id=task_id,
                agents=selected_agents,
                requirements=requirements
            )
            
            # Execute collaboration strategy
            result = await strategy.execute()
            
            # Update task status
            await self.task_manager.update_task_status(
                task_id=task_id,
                status=TaskStatus.COMPLETED.value,
                result=result
            )
            
            logger.info("User request processed successfully")
            
            return {
                "success": True,
                "task_id": task_id,
                "result": result
            }
        
        except Exception as e:
            error_msg = f"Error processing user request: {str(e)}"
            logger.error(error_msg)
            
            # Update task status if task_id is available
            if "task_id" in locals():
                await self.task_manager.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.FAILED.value,
                    error=error_msg
                )
            
            return {
                "success": False,
                "error": error_msg
            }
    
    async def delegate_task_to_agent(self, agent_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate a task to a specific type of agent.
        
        Args:
            agent_type: Type of agent to delegate to
            task_data: Task data
            
        Returns:
            Task result
        """
        logger.info("Delegating task to %s agent", agent_type)
        
        try:
            # Get agent interface
            agent_ids = await self.registry.get_agents_by_type(agent_type)
            
            if not agent_ids:
                error_msg = f"No {agent_type} agent available"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # For now, just use the first agent of the requested type
            agent_id = agent_ids[0]
            agent_interface = await self.registry.get_agent_interface(agent_id)
            
            if not agent_interface:
                error_msg = f"Interface for {agent_type} agent not found"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Send task request to agent
            message_id = await self.interface.send_message(
                target_agent_id=agent_id,
                message_type=MessageType.REQUEST.value,
                content={
                    "request_type": "process_task",
                    "request_data": {
                        "task_data": task_data
                    }
                }
            )
            
            # Wait for response (in a real implementation, this would use a callback or event)
            # For now, simulate a response
            # This is a placeholder - in a real implementation, we would wait for the actual response
            await asyncio.sleep(1)
            
            # Get the agent from specialized_agents
            agent_instance = self.specialized_agents.get(agent_type, {}).get("agent")
            
            if not agent_instance:
                error_msg = f"{agent_type} agent instance not found"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Process task with agent instance
            # This is a direct call for now - in a real implementation, this would be handled through the interface
            result = await self._process_with_agent(agent_instance, task_data)
            
            logger.info("Task delegated to %s agent successfully", agent_type)
            
            return {
                "success": True,
                "agent_type": agent_type,
                "result": result
            }
        
        except Exception as e:
            error_msg = f"Error delegating task to {agent_type} agent: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def _process_with_agent(self, agent, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task with an agent instance.
        
        Args:
            agent: Agent instance
            task_data: Task data
            
        Returns:
            Processing result
        """
        # This is a placeholder - in a real implementation, this would call the agent's process method
        # For now, return a dummy result
        return {
            "message": "Task processed by agent",
            "timestamp": datetime.now().isoformat()
        }
    
    async def resolve_conflicts(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve conflicts between agent results.
        
        Args:
            results: List of agent results
            
        Returns:
            Resolved result
        """
        logger.info("Resolving conflicts between %d agent results", len(results))
        
        # If there's only one result, no conflicts to resolve
        if len(results) <= 1:
            return results[0] if results else {}
        
        # Group results by agent type
        results_by_agent = {}
        for result in results:
            agent_type = result.get("agent_type")
            if agent_type:
                results_by_agent[agent_type] = result
        
        # Identify conflicts using the conflict detector
        conflicts = ConflictDetector.detect_conflicts(results_by_agent)
        
        if not conflicts:
            # No conflicts, merge results
            return self._merge_results(list(results_by_agent.values()))
        
        # Resolve each conflict using the consensus mechanism
        resolved_results = {}
        for conflict in conflicts:
            resolution = await self.consensus_mechanism.resolve_conflict(
                conflict=conflict,
                agent_recommendations=results_by_agent,
                strategy=ConflictResolutionStrategy.HYBRID.value,
                context={"task_type": "conflict_resolution"}
            )
            
            # Store resolution for this conflict
            resolved_results[conflict["attribute"]] = resolution
        
        # Merge results with resolutions
        merged_result = self._merge_results(list(results_by_agent.values()))
        
        # Apply resolutions to merged result
        for attribute, resolution in resolved_results.items():
            # Set the resolved value in the merged result
            self._set_nested_value(
                merged_result, 
                attribute, 
                resolution.get("recommendation", {})
            )
        
        # Add resolution metadata
        merged_result["conflict_resolutions"] = resolved_results
        
        logger.info("Conflicts resolved successfully")
        
        return merged_result
    
    def _identify_conflicts(self, results_by_agent: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identify conflicts between agent results.
        
        Args:
            results_by_agent: Results grouped by agent type
            
        Returns:
            Identified conflicts
        """
        # Use the ConflictDetector to identify conflicts
        return ConflictDetector.detect_conflicts(results_by_agent)
    
    def _set_nested_value(self, obj: Dict[str, Any], key_path: str, value: Any) -> None:
        """
        Set a value in a nested dictionary using a dot-separated path.
        
        Args:
            obj: The dictionary to modify
            key_path: Dot-separated path to the key
            value: Value to set
        """
        parts = key_path.split('.')
        current = obj
        
        # Navigate to the parent of the target key
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value at the target key
        current[parts[-1]] = value
    
    async def build_consensus(self, decision_point: str, options: List[Any], 
                             agents: List[str]) -> Any:
        """
        Build consensus among agents for a decision.
        
        Args:
            decision_point: Description of the decision point
            options: List of options to choose from
            agents: List of agent types to involve
            
        Returns:
            Consensus decision
        """
        logger.info("Building consensus for decision point: %s", decision_point)
        
        # Get agent interfaces
        agent_interfaces = {}
        for agent_type in agents:
            agent_ids = await self.registry.get_agents_by_type(agent_type)
            if agent_ids:
                agent_interface = await self.registry.get_agent_interface(agent_ids[0])
                if agent_interface:
                    agent_interfaces[agent_type] = agent_interface
        
        if not agent_interfaces:
            logger.warning("No agents available for consensus building")
            return options[0] if options else None
        
        # Create decision point structure
        decision_point_data = {
            "id": f"decision_{uuid.uuid4().hex[:8]}",
            "key": decision_point,
            "description": f"Decision on {decision_point}",
            "options": options
        }
        
        # Use the consensus mechanism to build consensus
        consensus_result = await self.consensus_mechanism.build_consensus(
            decision_point=decision_point_data,
            agent_interfaces=agent_interfaces,
            context={"task_type": "consensus_building"},
            threshold=0.7  # Medium threshold
        )
        
        # Extract the selected option
        selected_option = consensus_result.get("selected_option")
        
        logger.info("Consensus reached: %s", selected_option)
        
        return selected_option
    
    async def _build_consensus(self, decision_point: Dict[str, Any], 
                             task_context: Dict[str, Any], 
                             agents_involved: List[str]) -> Dict[str, Any]:
        """
        Build consensus for a decision point during task execution.
        
        Args:
            decision_point: Decision point details
            task_context: Task context
            agents_involved: List of agent types involved
            
        Returns:
            Consensus details
        """
        logger.info("Building consensus for decision point: %s", decision_point.get("key"))
        
        # Get agent interfaces
        agent_interfaces = {}
        for agent_type in agents_involved:
            agent_ids = await self.registry.get_agents_by_type(agent_type)
            if agent_ids:
                agent_interface = await self.registry.get_agent_interface(agent_ids[0])
                if agent_interface:
                    agent_interfaces[agent_type] = agent_interface
        
        # Use the consensus mechanism to build consensus
        consensus_result = await self.consensus_mechanism.build_consensus(
            decision_point=decision_point,
            agent_interfaces=agent_interfaces,
            context=task_context,
            threshold=0.7  # Medium threshold
        )
        
        return consensus_result
    
    def _get_required_agent_types(self, task_type: str) -> List[str]:
        """
        Get required agent types for a task.
        
        Args:
            task_type: Type of task
            
        Returns:
            List of required agent types
        """
        # Define required agent types based on task type
        task_type_mapping = {
            "code_review": ["validation", "security", "performance"],
            "design_review": ["design", "validation"],
            "architecture_review": ["architecture", "security", "performance"],
            "security_review": ["security"],
            "performance_review": ["performance"],
            "application_creation": ["architecture", "design", "security", "performance", "validation"],
            "default": ["validation"]
        }
        
        return task_type_mapping.get(task_type, task_type_mapping["default"])
    
    def _get_required_capabilities(self, task_type: str) -> List[str]:
        """
        Get required capabilities for a task.
        
        Args:
            task_type: Type of task
            
        Returns:
            List of required capabilities
        """
        # Define required capabilities based on task type
        task_capability_mapping = {
            "code_review": ["code_review"],
            "design_review": ["design_review"],
            "architecture_review": ["architecture_analysis"],
            "security_review": ["security_analysis"],
            "performance_review": ["performance_analysis"],
            "application_creation": ["architecture_analysis", "design_creation"],
            "default": ["validation"]
        }
        
        return task_capability_mapping.get(task_type, task_capability_mapping["default"])
    
    async def _select_agents_for_task(self, required_agent_types: List[str],
                                    required_capabilities: List[str]) -> List[str]:
        """
        Select agents for a task based on requirements.
        
        Args:
            required_agent_types: List of required agent types
            required_capabilities: List of required capabilities
            
        Returns:
            List of selected agent types
        """
        selected_agents = set()
        
        # Select agents by type
        for agent_type in required_agent_types:
            agent_ids = await self.registry.get_agents_by_type(agent_type)
            if agent_ids:
                selected_agents.add(agent_type)
        
        # Select agents by capability
        for capability in required_capabilities:
            agent_ids = await self.registry.get_agents_by_capability(capability)
            for agent_id in agent_ids:
                agent = await self.registry.get_agent(agent_id)
                if agent:
                    selected_agents.add(agent["agent_type"])
        
        return list(selected_agents)
    
    def _merge_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple agent results into a single result.
        
        Args:
            results: List of agent results
            
        Returns:
            Merged result
        """
        # Start with an empty result
        merged_result = {
            "success": True,
            "agent_contributions": []
        }
        
        # Merge each result
        for result in results:
            # Skip failed results
            if not result.get("success", True):
                continue
            
            # Add agent contribution
            agent_type = result.get("agent_type", "unknown")
            merged_result["agent_contributions"].append({
                "agent_type": agent_type,
                "contribution": result.get("result", {})
            })
            
            # Merge result data
            result_data = result.get("result", {})
            for key, value in result_data.items():
                # Skip metadata keys
                if key in ["agent_type", "timestamp"]:
                    continue
                
                # Add or append to merged result
                if key not in merged_result:
                    merged_result[key] = value
                elif isinstance(merged_result[key], list) and isinstance(value, list):
                    merged_result[key].extend(value)
                elif isinstance(merged_result[key], dict) and isinstance(value, dict):
                    merged_result[key].update(value)
                else:
                    # For conflicting values, keep the existing one
                    pass
        
        return merged_result
