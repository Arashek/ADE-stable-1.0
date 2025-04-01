"""
Collaboration Patterns for ADE Platform

This module defines the collaboration patterns used by the agent coordination system
to facilitate effective collaboration between specialized agents in the ADE platform.
"""

from enum import Enum
from typing import Dict, List, Any, Optional
import logging
import time

# Import monitoring components
# Temporarily disabled for local testing
# from services.monitoring import track_collaboration_pattern

# Configure logging
logger = logging.getLogger(__name__)

# Temporary replacement for track_collaboration_pattern decorator
def track_collaboration_pattern(pattern_type):
    """Temporary replacement for the monitoring decorator"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            logger.info(f"Executing {pattern_type} collaboration pattern")
            result = await func(*args, **kwargs)
            logger.info(f"Completed {pattern_type} collaboration pattern")
            return result
        return wrapper
    return decorator

class CollaborationPattern(Enum):
    """Enumeration of collaboration patterns for agent coordination"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ITERATIVE = "iterative"
    CONSENSUS = "consensus"

class CollaborationPatternFactory:
    """
    Factory class for creating collaboration pattern configurations based on task types.
    
    This class provides predefined collaboration pattern configurations for different
    types of tasks in the ADE platform, ensuring consistent and effective agent collaboration.
    """
    
    def __init__(self):
        """Initialize the collaboration pattern factory."""
        self.pattern_metrics = {}
        for pattern in CollaborationPattern:
            self.pattern_metrics[pattern.value] = {
                "executions": 0,
                "success_rate": 1.0,
                "avg_duration": 0.0
            }
    
    @staticmethod
    def get_pattern_config(task_type: str, custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get the collaboration pattern configuration for a specific task type.
        
        Args:
            task_type: Type of task to be performed
            custom_config: Optional custom configuration to override defaults
            
        Returns:
            Collaboration pattern configuration
        """
        # Default configurations for different task types
        default_configs = {
            "application_creation": {
                "pattern": CollaborationPattern.ITERATIVE.value,
                "max_iterations": 3,
                "agent_sequence": ["architecture", "design", "security", "performance", "validation"],
                "consensus_threshold": 0.7
            },
            "code_review": {
                "pattern": CollaborationPattern.PARALLEL.value,
                "conflict_resolution_strategy": "priority_based",
                "agent_weights": {
                    "validation": 1.0,
                    "security": 1.2,
                    "performance": 0.8,
                    "architecture": 0.9
                }
            },
            "design_review": {
                "pattern": CollaborationPattern.CONSENSUS.value,
                "decision_points": ["layout", "color_scheme", "navigation", "accessibility"],
                "consensus_threshold": 0.8,
                "agent_weights": {
                    "design": 1.5,
                    "validation": 0.7,
                    "architecture": 0.8
                }
            },
            "security_assessment": {
                "pattern": CollaborationPattern.SEQUENTIAL.value,
                "agent_sequence": ["security", "architecture", "validation"],
                "feedback_loops": True
            },
            "performance_optimization": {
                "pattern": CollaborationPattern.ITERATIVE.value,
                "max_iterations": 5,
                "improvement_threshold": 0.05,
                "agent_weights": {
                    "performance": 1.5,
                    "architecture": 1.0,
                    "validation": 0.8
                }
            }
        }
        
        # Get default config for task type or use generic default
        config = default_configs.get(task_type, {
            "pattern": CollaborationPattern.PARALLEL.value,
            "conflict_resolution_strategy": "priority_based"
        })
        
        # Override with custom config if provided
        if custom_config:
            for key, value in custom_config.items():
                config[key] = value
        
        logger.info("Using %s collaboration pattern for task type: %s", 
                   config.get("pattern"), task_type)
        
        return config
    
    async def execute_pattern(self, pattern_type: str, task: Dict[str, Any], 
                             agents: Dict[str, Any], registry: Any, coordinator: Any) -> Dict[str, Any]:
        """
        Execute a collaboration pattern with metrics tracking.
        
        Args:
            pattern_type: Type of collaboration pattern
            task: Task to execute
            agents: Available agents
            registry: Agent registry
            coordinator: Agent coordinator
            
        Returns:
            Result of pattern execution
        """
        start_time = time.time()
        strategy = PatternStrategyFactory.create_strategy(pattern_type, {
            "conflict_resolution_strategy": "priority_based"
        })
        
        try:
            @track_collaboration_pattern(pattern_type)
            async def execute_with_tracking():
                return await strategy.execute(
                    coordinator=coordinator,
                    task_context=task
                )
            
            result = await execute_with_tracking()
            
            # Update metrics
            self.pattern_metrics[pattern_type]["executions"] += 1
            self.pattern_metrics[pattern_type]["success_rate"] = (
                0.9 * self.pattern_metrics[pattern_type]["success_rate"] + 
                0.1 * (1.0 if result.get("success", False) else 0.0)
            )
            
            duration = time.time() - start_time
            self.pattern_metrics[pattern_type]["avg_duration"] = (
                0.9 * self.pattern_metrics[pattern_type]["avg_duration"] + 
                0.1 * duration
            )
            
            return result
        except Exception as e:
            logger.error(f"Error executing {pattern_type} pattern: {str(e)}")
            
            # Update metrics on failure
            self.pattern_metrics[pattern_type]["executions"] += 1
            self.pattern_metrics[pattern_type]["success_rate"] = (
                0.9 * self.pattern_metrics[pattern_type]["success_rate"] + 0.1 * 0.0
            )
            
            duration = time.time() - start_time
            self.pattern_metrics[pattern_type]["avg_duration"] = (
                0.9 * self.pattern_metrics[pattern_type]["avg_duration"] + 
                0.1 * duration
            )
            
            raise

class PatternExecutionStrategy:
    """
    Base class for collaboration pattern execution strategies.
    
    This class defines the interface for executing different collaboration patterns
    and provides common functionality for pattern execution.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the pattern execution strategy.
        
        Args:
            config: Configuration for the pattern execution
        """
        self.config = config
    
    async def execute(self, coordinator, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the collaboration pattern.
        
        Args:
            coordinator: The agent coordinator instance
            task_context: Context for the current task
            
        Returns:
            Result of the pattern execution
        """
        raise NotImplementedError("Subclasses must implement execute method")

class SequentialStrategy(PatternExecutionStrategy):
    """
    Strategy for executing sequential collaboration pattern.
    
    In this pattern, agents work in a predefined sequence, with each agent
    building upon the work of previous agents.
    """
    
    async def execute(self, coordinator, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the sequential collaboration pattern.
        
        Args:
            coordinator: The agent coordinator instance
            task_context: Context for the current task
            
        Returns:
            Result of the sequential pattern execution
        """
        logger.info("Executing sequential collaboration for task %s", task_context["task_id"])
        
        # Get the agent sequence from config or use default
        sequence = self.config.get("agent_sequence", 
                                 ["architecture", "design", "security", "performance", "validation"])
        
        result = {"sequential_results": []}
        current_input = task_context["requirements"]
        
        # Process through each agent in sequence
        for agent_name in sequence:
            if agent_name in coordinator.agents:
                agent = coordinator.agents[agent_name]
                agent_response = await coordinator._delegate_to_agent(
                    agent, agent_name, current_input, task_context)
                
                # Store agent response
                task_context["agent_responses"][agent_name] = agent_response
                
                # Update input for next agent in sequence
                current_input = coordinator._merge_dictionaries(current_input, agent_response)
                
                # Add to sequential results
                result["sequential_results"].append({
                    "agent": agent_name,
                    "contribution": coordinator._summarize_contribution(agent_response)
                })
            else:
                logger.warning("Agent %s not found, skipping in sequence", agent_name)
        
        # Implement feedback loops if configured
        if self.config.get("feedback_loops", False):
            # Reverse the sequence for feedback
            feedback_sequence = sequence[::-1]
            
            for agent_name in feedback_sequence:
                if agent_name in coordinator.agents:
                    agent = coordinator.agents[agent_name]
                    
                    # Include feedback context
                    feedback_input = coordinator._merge_dictionaries(
                        current_input, {"feedback_phase": True})
                    
                    agent_response = await coordinator._delegate_to_agent(
                        agent, agent_name, feedback_input, task_context)
                    
                    # Update agent response with feedback
                    task_context["agent_responses"][agent_name] = coordinator._merge_dictionaries(
                        task_context["agent_responses"].get(agent_name, {}), 
                        {"feedback": agent_response})
                    
                    # Update input with feedback
                    current_input = coordinator._merge_dictionaries(current_input, agent_response)
                    
                    # Add to sequential results
                    result["sequential_results"].append({
                        "agent": f"{agent_name}_feedback",
                        "contribution": coordinator._summarize_contribution(agent_response)
                    })
        
        # Consolidate final result
        result["consolidated"] = current_input
        return result

class ParallelStrategy(PatternExecutionStrategy):
    """
    Strategy for executing parallel collaboration pattern.
    
    In this pattern, agents work simultaneously on the same task and their
    results are combined, with conflicts resolved according to defined strategies.
    """
    
    async def execute(self, coordinator, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the parallel collaboration pattern.
        
        Args:
            coordinator: The agent coordinator instance
            task_context: Context for the current task
            
        Returns:
            Result of the parallel pattern execution
        """
        logger.info("Executing parallel collaboration for task %s", task_context["task_id"])
        
        # Determine which agents to involve
        agents_to_involve = coordinator._get_relevant_agents(task_context["task_type"])
        
        # Apply agent weights if specified
        agent_weights = self.config.get("agent_weights", {})
        if agent_weights:
            # Update coordinator's agent priorities temporarily for this task
            original_priorities = coordinator.agent_priorities.copy()
            for agent, weight in agent_weights.items():
                if agent in coordinator.agent_priorities:
                    coordinator.agent_priorities[agent] = coordinator.agent_priorities[agent] * weight
        
        # Create tasks for all relevant agents
        import asyncio
        tasks = []
        for agent_name in agents_to_involve:
            if agent_name in coordinator.agents:
                agent = coordinator.agents[agent_name]
                tasks.append(coordinator._delegate_to_agent(
                    agent, agent_name, task_context["requirements"], task_context))
            else:
                logger.warning("Agent %s not found, skipping in parallel execution", agent_name)
        
        # Execute all agent tasks in parallel
        agent_responses = await asyncio.gather(*tasks)
        
        # Store agent responses
        for i, agent_name in enumerate(agents_to_involve):
            if i < len(agent_responses):
                task_context["agent_responses"][agent_name] = agent_responses[i]
        
        # Identify and resolve conflicts
        conflicts = coordinator._identify_conflicts(task_context)
        task_context["conflicts"] = conflicts
        
        # Get conflict resolution strategy
        resolution_strategy = self.config.get("conflict_resolution_strategy", "priority_based")
        
        if conflicts:
            resolved_conflicts = coordinator._resolve_conflicts(conflicts, task_context)
            task_context["resolved_conflicts"] = resolved_conflicts
        
        # Consolidate results
        consolidated_result = coordinator._consolidate_results(task_context)
        
        # Restore original agent priorities if they were modified
        if agent_weights:
            coordinator.agent_priorities = original_priorities
        
        return {
            "parallel_results": [
                {"agent": agent_name, "contribution": coordinator._summarize_contribution(
                    task_context["agent_responses"].get(agent_name, {}))}
                for agent_name in agents_to_involve if agent_name in task_context["agent_responses"]
            ],
            "conflicts": [{"description": conflict["description"], "resolution": conflict["resolution"]} 
                         for conflict in task_context.get("resolved_conflicts", [])],
            "resolution_strategy": resolution_strategy,
            "consolidated": consolidated_result
        }

class IterativeStrategy(PatternExecutionStrategy):
    """
    Strategy for executing iterative collaboration pattern.
    
    In this pattern, agents work through multiple iterations, refining their work
    based on feedback from previous iterations until convergence or a maximum
    number of iterations is reached.
    """
    
    async def execute(self, coordinator, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the iterative collaboration pattern.
        
        Args:
            coordinator: The agent coordinator instance
            task_context: Context for the current task
            
        Returns:
            Result of the iterative pattern execution
        """
        logger.info("Executing iterative collaboration for task %s", task_context["task_id"])
        
        # Maximum number of iterations
        max_iterations = self.config.get("max_iterations", 3)
        
        # Improvement threshold for early stopping
        improvement_threshold = self.config.get("improvement_threshold", 0.1)
        
        # Determine which agents to involve
        agents_to_involve = coordinator._get_relevant_agents(task_context["task_type"])
        
        # Initialize iteration tracking
        iterations = []
        current_input = task_context["requirements"]
        previous_quality_score = 0
        
        # Perform iterations
        import asyncio
        for iteration in range(max_iterations):
            iteration_results = {}
            
            # Execute all agent tasks in parallel
            tasks = []
            for agent_name in agents_to_involve:
                if agent_name in coordinator.agents:
                    agent = coordinator.agents[agent_name]
                    
                    # Add iteration context to input
                    iteration_input = coordinator._merge_dictionaries(
                        current_input, {"iteration": iteration + 1})
                    
                    tasks.append(coordinator._delegate_to_agent(
                        agent, agent_name, iteration_input, task_context))
                else:
                    logger.warning("Agent %s not found, skipping in iteration %d", 
                                  agent_name, iteration + 1)
            
            agent_responses = await asyncio.gather(*tasks)
            
            # Store agent responses for this iteration
            for i, agent_name in enumerate(agents_to_involve):
                if i < len(agent_responses):
                    iteration_results[agent_name] = agent_responses[i]
            
            # Store in task context
            if "iterations" not in task_context:
                task_context["iterations"] = []
            task_context["iterations"].append(iteration_results)
            
            # Identify conflicts
            conflicts = coordinator._identify_conflicts_from_iteration(iteration_results)
            
            # Calculate quality score for this iteration
            quality_score = self._calculate_quality_score(iteration_results)
            
            # Check for improvement
            improvement = quality_score - previous_quality_score
            
            # If improvement is below threshold and not first iteration, stop
            if iteration > 0 and improvement < improvement_threshold:
                logger.info("Improvement below threshold after iteration %d, stopping iterations", 
                           iteration + 1)
                break
            
            # Update previous quality score
            previous_quality_score = quality_score
            
            # If no conflicts and not first iteration, we can stop iterating
            if not conflicts and iteration > 0:
                logger.info("No conflicts found after iteration %d, stopping iterations", 
                           iteration + 1)
                break
            
            # Update input for next iteration with resolved conflicts
            if conflicts:
                resolved_conflicts = coordinator._resolve_conflicts(conflicts, task_context)
                current_input = coordinator._merge_dictionaries(
                    current_input, {"resolved_conflicts": resolved_conflicts})
            
            # Merge all agent responses for next iteration
            for agent_name, response in iteration_results.items():
                current_input = coordinator._merge_dictionaries(current_input, response)
            
            # Track iteration
            iterations.append({
                "iteration": iteration + 1,
                "conflicts": len(conflicts),
                "quality_score": quality_score,
                "improvement": improvement if iteration > 0 else None
            })
        
        # Consolidate final result from last iteration
        final_iteration = task_context["iterations"][-1]
        task_context["agent_responses"] = final_iteration
        consolidated_result = coordinator._consolidate_results(task_context)
        
        return {
            "iterations": iterations,
            "final_iteration": len(task_context["iterations"]),
            "final_quality_score": previous_quality_score,
            "consolidated": consolidated_result
        }
    
    def _calculate_quality_score(self, iteration_results: Dict[str, Any]) -> float:
        """
        Calculate a quality score for an iteration's results.
        
        Args:
            iteration_results: Results from a single iteration
            
        Returns:
            Quality score between 0 and 1
        """
        # This is a simple implementation that could be enhanced
        # with more sophisticated quality metrics
        
        # Count recommendations and decisions
        recommendation_count = 0
        decision_count = 0
        error_count = 0
        
        for agent_name, response in iteration_results.items():
            recommendation_count += len(response.get("recommendations", {}))
            decision_count += len(response.get("decisions", {}))
            if "error" in response:
                error_count += 1
        
        # Calculate base score
        base_score = 0.5
        
        # Adjust for recommendations and decisions
        if recommendation_count > 0:
            base_score += min(0.3, 0.02 * recommendation_count)
        
        if decision_count > 0:
            base_score += min(0.2, 0.02 * decision_count)
        
        # Penalize for errors
        if error_count > 0:
            base_score -= min(0.5, 0.1 * error_count)
        
        # Ensure score is between 0 and 1
        return max(0, min(1, base_score))

class ConsensusStrategy(PatternExecutionStrategy):
    """
    Strategy for executing consensus collaboration pattern.
    
    In this pattern, agents must reach agreement on key decision points through
    a consensus-building process.
    """
    
    async def execute(self, coordinator, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the consensus collaboration pattern.
        
        Args:
            coordinator: The agent coordinator instance
            task_context: Context for the current task
            
        Returns:
            Result of the consensus pattern execution
        """
        logger.info("Executing consensus collaboration for task %s", task_context["task_id"])
        
        # Get consensus threshold
        consensus_threshold = self.config.get("consensus_threshold", 0.7)
        
        # Get predefined decision points if any
        predefined_decision_points = self.config.get("decision_points", [])
        
        # Determine which agents to involve
        agents_to_involve = coordinator._get_relevant_agents(task_context["task_type"])
        
        # Apply agent weights if specified
        agent_weights = self.config.get("agent_weights", {})
        if agent_weights:
            # Update coordinator's agent priorities temporarily for this task
            original_priorities = coordinator.agent_priorities.copy()
            for agent, weight in agent_weights.items():
                if agent in coordinator.agent_priorities:
                    coordinator.agent_priorities[agent] = coordinator.agent_priorities[agent] * weight
        
        # Execute initial agent tasks in parallel
        import asyncio
        tasks = []
        for agent_name in agents_to_involve:
            if agent_name in coordinator.agents:
                agent = coordinator.agents[agent_name]
                
                # Include predefined decision points in input
                decision_input = coordinator._merge_dictionaries(
                    task_context["requirements"], 
                    {"decision_points": predefined_decision_points})
                
                tasks.append(coordinator._delegate_to_agent(
                    agent, agent_name, decision_input, task_context))
            else:
                logger.warning("Agent %s not found, skipping in consensus building", agent_name)
        
        agent_responses = await asyncio.gather(*tasks)
        
        # Store agent responses
        for i, agent_name in enumerate(agents_to_involve):
            if i < len(agent_responses):
                task_context["agent_responses"][agent_name] = agent_responses[i]
        
        # Identify decision points that need consensus
        decision_points = coordinator._identify_decision_points(task_context)
        
        # Add predefined decision points if not already identified
        for dp_name in predefined_decision_points:
            if not any(dp["key"] == dp_name for dp in decision_points):
                decision_points.append({
                    "id": f"decision_{len(decision_points) + 1}",
                    "key": dp_name,
                    "description": f"Decision on {dp_name}",
                    "opinions": {},
                    "consensus": None
                })
        
        # Build consensus for each decision point
        consensus_results = {}
        for decision_point in decision_points:
            consensus = await coordinator._build_consensus(
                decision_point, task_context, agents_to_involve)
            
            # Only accept consensus if confidence exceeds threshold
            if consensus.get("confidence", 0) >= consensus_threshold:
                consensus_results[decision_point["id"]] = consensus
            else:
                # If consensus confidence is below threshold, initiate additional round
                enhanced_consensus = await self._enhance_consensus(
                    coordinator, decision_point, task_context, agents_to_involve)
                
                consensus_results[decision_point["id"]] = enhanced_consensus
        
        # Store consensus results
        task_context["consensus"] = consensus_results
        
        # Consolidate final result with consensus decisions
        consolidated_result = coordinator._consolidate_results_with_consensus(task_context)
        
        # Restore original agent priorities if they were modified
        if agent_weights:
            coordinator.agent_priorities = original_priorities
        
        return {
            "decision_points": len(decision_points),
            "consensus_reached": len(consensus_results),
            "consensus_threshold": consensus_threshold,
            "consensus_details": [
                {
                    "decision_point": dp_id, 
                    "outcome": consensus["outcome"],
                    "confidence": consensus["confidence"]
                }
                for dp_id, consensus in consensus_results.items()
            ],
            "consolidated": consolidated_result
        }
    
    async def _enhance_consensus(self, coordinator, decision_point: Dict[str, Any],
                               task_context: Dict[str, Any], 
                               agents_involved: List[str]) -> Dict[str, Any]:
        """
        Enhance consensus for a decision point through additional deliberation.
        
        Args:
            coordinator: The agent coordinator instance
            decision_point: The decision point to enhance consensus for
            task_context: Context for the current task
            agents_involved: List of agents involved in the task
            
        Returns:
            Enhanced consensus details
        """
        logger.info("Enhancing consensus for decision point %s", decision_point["id"])
        
        # Extract current opinions
        opinions = decision_point["opinions"]
        
        # Create a focused task for this decision point
        focused_task = {
            "task_type": "consensus_building",
            "decision_point": decision_point["key"],
            "description": decision_point["description"],
            "current_opinions": opinions,
            "requirements": task_context["requirements"]
        }
        
        # Ask each agent to reconsider with knowledge of others' opinions
        import asyncio
        tasks = []
        for agent_name in agents_involved:
            if agent_name in coordinator.agents and agent_name in opinions:
                agent = coordinator.agents[agent_name]
                tasks.append(coordinator._delegate_to_agent(
                    agent, agent_name, focused_task, task_context))
        
        enhanced_responses = await asyncio.gather(*tasks)
        
        # Update opinions with enhanced responses
        enhanced_opinions = {}
        for i, agent_name in enumerate(agents_involved):
            if i < len(enhanced_responses) and agent_name in opinions:
                if "enhanced_opinion" in enhanced_responses[i]:
                    enhanced_opinions[agent_name] = enhanced_responses[i]["enhanced_opinion"]
                else:
                    enhanced_opinions[agent_name] = opinions[agent_name]
        
        # Calculate weighted votes
        vote_counts = {}
        for agent, opinion in enhanced_opinions.items():
            value = str(opinion.get("value"))
            if value in vote_counts:
                vote_counts[value] += coordinator.agent_priorities.get(agent, 1)
            else:
                vote_counts[value] = coordinator.agent_priorities.get(agent, 1)
        
        # Find option with highest vote count
        winning_value = max(vote_counts, key=vote_counts.get) if vote_counts else None
        total_votes = sum(vote_counts.values())
        confidence = vote_counts[winning_value] / total_votes if total_votes > 0 and winning_value else 0
        
        return {
            "method": "enhanced_consensus",
            "outcome": winning_value,
            "vote_counts": vote_counts,
            "confidence": confidence,
            "enhanced": True
        }

class PatternStrategyFactory:
    """
    Factory for creating pattern execution strategies.
    
    This class creates the appropriate strategy object for a given collaboration pattern.
    """
    
    @staticmethod
    def create_strategy(pattern: str, config: Dict[str, Any]) -> PatternExecutionStrategy:
        """
        Create a pattern execution strategy.
        
        Args:
            pattern: The collaboration pattern
            config: Configuration for the pattern execution
            
        Returns:
            Pattern execution strategy
        """
        strategies = {
            CollaborationPattern.SEQUENTIAL.value: SequentialStrategy,
            CollaborationPattern.PARALLEL.value: ParallelStrategy,
            CollaborationPattern.ITERATIVE.value: IterativeStrategy,
            CollaborationPattern.CONSENSUS.value: ConsensusStrategy
        }
        
        strategy_class = strategies.get(pattern)
        if not strategy_class:
            logger.warning("Unknown pattern %s, defaulting to parallel", pattern)
            strategy_class = ParallelStrategy
        
        return strategy_class(config)
