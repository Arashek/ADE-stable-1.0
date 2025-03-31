"""
Consensus Mechanism for ADE Platform

This module implements a consensus mechanism for resolving conflicting agent recommendations
in the ADE platform. It provides methods for building consensus among agents and
resolving conflicts based on various strategies.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import asyncio
import uuid
import math

# Configure logging
logger = logging.getLogger(__name__)

class ConflictResolutionStrategy(Enum):
    """Enumeration of conflict resolution strategies"""
    PRIORITY_BASED = "priority_based"
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_VOTE = "weighted_vote"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    HYBRID = "hybrid"

class ConsensusThreshold(Enum):
    """Enumeration of consensus threshold levels"""
    LOW = 0.5
    MEDIUM = 0.7
    HIGH = 0.85
    UNANIMOUS = 1.0

class ConsensusMechanism:
    """
    Consensus mechanism for resolving conflicting agent recommendations.
    
    This class provides methods for building consensus among agents and
    resolving conflicts based on various strategies.
    """
    
    def __init__(self, agent_priorities: Dict[str, int] = None):
        """
        Initialize the consensus mechanism.
        
        Args:
            agent_priorities: Dictionary mapping agent types to priority levels
        """
        self.agent_priorities = agent_priorities or {}
        logger.info("Consensus mechanism initialized")
    
    async def resolve_conflict(self, 
                             conflict: Dict[str, Any],
                             agent_recommendations: Dict[str, Dict[str, Any]],
                             strategy: str = ConflictResolutionStrategy.HYBRID.value,
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Resolve a conflict between agent recommendations.
        
        Args:
            conflict: Conflict details
            agent_recommendations: Recommendations from different agents
            strategy: Conflict resolution strategy to use
            context: Additional context for conflict resolution
            
        Returns:
            Resolved recommendation
        """
        logger.info("Resolving conflict using %s strategy", strategy)
        
        # Select resolution strategy
        if strategy == ConflictResolutionStrategy.PRIORITY_BASED.value:
            resolution = self._resolve_by_priority(conflict, agent_recommendations)
        elif strategy == ConflictResolutionStrategy.MAJORITY_VOTE.value:
            resolution = self._resolve_by_majority_vote(conflict, agent_recommendations)
        elif strategy == ConflictResolutionStrategy.WEIGHTED_VOTE.value:
            resolution = self._resolve_by_weighted_vote(conflict, agent_recommendations)
        elif strategy == ConflictResolutionStrategy.CONFIDENCE_WEIGHTED.value:
            resolution = self._resolve_by_confidence(conflict, agent_recommendations)
        elif strategy == ConflictResolutionStrategy.HYBRID.value:
            resolution = self._resolve_by_hybrid(conflict, agent_recommendations, context)
        else:
            logger.warning("Unknown resolution strategy %s, using hybrid", strategy)
            resolution = self._resolve_by_hybrid(conflict, agent_recommendations, context)
        
        # Add metadata to resolution
        resolution["conflict_id"] = conflict.get("id", str(uuid.uuid4()))
        resolution["resolution_strategy"] = strategy
        resolution["agents_involved"] = list(agent_recommendations.keys())
        
        return resolution
    
    def _resolve_by_priority(self, 
                           conflict: Dict[str, Any],
                           agent_recommendations: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve conflict by selecting the recommendation from the highest priority agent.
        
        Args:
            conflict: Conflict details
            agent_recommendations: Recommendations from different agents
            
        Returns:
            Resolved recommendation
        """
        # Find agent with highest priority
        highest_priority = -1
        highest_priority_agent = None
        
        for agent_type, recommendation in agent_recommendations.items():
            priority = self.agent_priorities.get(agent_type, 0)
            if priority > highest_priority:
                highest_priority = priority
                highest_priority_agent = agent_type
        
        if highest_priority_agent:
            selected_recommendation = agent_recommendations[highest_priority_agent]
            
            return {
                "resolution_method": "priority_based",
                "selected_agent": highest_priority_agent,
                "agent_priority": highest_priority,
                "recommendation": selected_recommendation,
                "confidence": 1.0  # Maximum confidence since we're using strict priority
            }
        else:
            # Fallback if no priorities are set
            return self._resolve_by_majority_vote(conflict, agent_recommendations)
    
    def _resolve_by_majority_vote(self, 
                                conflict: Dict[str, Any],
                                agent_recommendations: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve conflict by majority vote among agent recommendations.
        
        Args:
            conflict: Conflict details
            agent_recommendations: Recommendations from different agents
            
        Returns:
            Resolved recommendation
        """
        # Extract the conflicting attribute
        conflict_attribute = conflict.get("attribute", "")
        
        if not conflict_attribute:
            logger.warning("No conflict attribute specified, cannot resolve by majority vote")
            return {
                "resolution_method": "majority_vote",
                "error": "No conflict attribute specified",
                "recommendation": next(iter(agent_recommendations.values()), {}),
                "confidence": 0.0
            }
        
        # Count votes for each value
        votes = {}
        for agent_type, recommendation in agent_recommendations.items():
            value = self._extract_attribute_value(recommendation, conflict_attribute)
            value_str = str(value)  # Convert to string for comparison
            
            if value_str not in votes:
                votes[value_str] = []
            votes[value_str].append(agent_type)
        
        # Find value with most votes
        most_votes = 0
        selected_value = None
        selected_agents = []
        
        for value_str, agents in votes.items():
            if len(agents) > most_votes:
                most_votes = len(agents)
                selected_value = value_str
                selected_agents = agents
        
        # Calculate confidence based on vote distribution
        total_agents = len(agent_recommendations)
        confidence = most_votes / total_agents if total_agents > 0 else 0
        
        # Get a complete recommendation that contains the selected value
        selected_recommendation = {}
        if selected_agents:
            selected_recommendation = agent_recommendations[selected_agents[0]]
        
        return {
            "resolution_method": "majority_vote",
            "selected_value": selected_value,
            "vote_count": most_votes,
            "total_votes": total_agents,
            "supporting_agents": selected_agents,
            "recommendation": selected_recommendation,
            "confidence": confidence
        }
    
    def _resolve_by_weighted_vote(self, 
                                conflict: Dict[str, Any],
                                agent_recommendations: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve conflict by weighted vote based on agent priorities.
        
        Args:
            conflict: Conflict details
            agent_recommendations: Recommendations from different agents
            
        Returns:
            Resolved recommendation
        """
        # Extract the conflicting attribute
        conflict_attribute = conflict.get("attribute", "")
        
        if not conflict_attribute:
            logger.warning("No conflict attribute specified, cannot resolve by weighted vote")
            return {
                "resolution_method": "weighted_vote",
                "error": "No conflict attribute specified",
                "recommendation": next(iter(agent_recommendations.values()), {}),
                "confidence": 0.0
            }
        
        # Count weighted votes for each value
        weighted_votes = {}
        total_weight = 0
        
        for agent_type, recommendation in agent_recommendations.items():
            value = self._extract_attribute_value(recommendation, conflict_attribute)
            value_str = str(value)  # Convert to string for comparison
            weight = self.agent_priorities.get(agent_type, 1)
            total_weight += weight
            
            if value_str not in weighted_votes:
                weighted_votes[value_str] = {
                    "weight": 0,
                    "agents": []
                }
            weighted_votes[value_str]["weight"] += weight
            weighted_votes[value_str]["agents"].append(agent_type)
        
        # Find value with highest weighted vote
        highest_weight = 0
        selected_value = None
        selected_data = None
        
        for value_str, data in weighted_votes.items():
            if data["weight"] > highest_weight:
                highest_weight = data["weight"]
                selected_value = value_str
                selected_data = data
        
        # Calculate confidence based on vote distribution
        confidence = highest_weight / total_weight if total_weight > 0 else 0
        
        # Get a complete recommendation that contains the selected value
        selected_recommendation = {}
        if selected_data and selected_data["agents"]:
            selected_recommendation = agent_recommendations[selected_data["agents"][0]]
        
        return {
            "resolution_method": "weighted_vote",
            "selected_value": selected_value,
            "weighted_vote": highest_weight,
            "total_weight": total_weight,
            "supporting_agents": selected_data["agents"] if selected_data else [],
            "recommendation": selected_recommendation,
            "confidence": confidence
        }
    
    def _resolve_by_confidence(self, 
                             conflict: Dict[str, Any],
                             agent_recommendations: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve conflict by selecting the recommendation with highest confidence.
        
        Args:
            conflict: Conflict details
            agent_recommendations: Recommendations from different agents
            
        Returns:
            Resolved recommendation
        """
        # Find recommendation with highest confidence
        highest_confidence = -1
        selected_agent = None
        
        for agent_type, recommendation in agent_recommendations.items():
            confidence = recommendation.get("confidence", 0)
            if confidence > highest_confidence:
                highest_confidence = confidence
                selected_agent = agent_type
        
        if selected_agent:
            selected_recommendation = agent_recommendations[selected_agent]
            
            return {
                "resolution_method": "confidence_based",
                "selected_agent": selected_agent,
                "agent_confidence": highest_confidence,
                "recommendation": selected_recommendation,
                "confidence": highest_confidence
            }
        else:
            # Fallback if no confidences are provided
            return self._resolve_by_majority_vote(conflict, agent_recommendations)
    
    def _resolve_by_hybrid(self, 
                         conflict: Dict[str, Any],
                         agent_recommendations: Dict[str, Dict[str, Any]],
                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Resolve conflict using a hybrid approach that combines multiple strategies.
        
        Args:
            conflict: Conflict details
            agent_recommendations: Recommendations from different agents
            context: Additional context for conflict resolution
            
        Returns:
            Resolved recommendation
        """
        # Get results from different strategies
        priority_result = self._resolve_by_priority(conflict, agent_recommendations)
        majority_result = self._resolve_by_majority_vote(conflict, agent_recommendations)
        weighted_result = self._resolve_by_weighted_vote(conflict, agent_recommendations)
        confidence_result = self._resolve_by_confidence(conflict, agent_recommendations)
        
        # Determine weights for each strategy based on context
        context = context or {}
        strategy_weights = {
            "priority_based": context.get("priority_weight", 0.4),
            "majority_vote": context.get("majority_weight", 0.2),
            "weighted_vote": context.get("weighted_weight", 0.3),
            "confidence_based": context.get("confidence_weight", 0.1)
        }
        
        # Normalize weights
        total_weight = sum(strategy_weights.values())
        if total_weight > 0:
            for key in strategy_weights:
                strategy_weights[key] /= total_weight
        
        # Calculate final confidence
        final_confidence = (
            priority_result["confidence"] * strategy_weights["priority_based"] +
            majority_result["confidence"] * strategy_weights["majority_vote"] +
            weighted_result["confidence"] * strategy_weights["weighted_vote"] +
            confidence_result["confidence"] * strategy_weights["confidence_based"]
        )
        
        # Select recommendation based on highest individual confidence
        strategies = [
            ("priority_based", priority_result),
            ("majority_vote", majority_result),
            ("weighted_vote", weighted_result),
            ("confidence_based", confidence_result)
        ]
        
        # Sort strategies by confidence * weight
        sorted_strategies = sorted(
            strategies,
            key=lambda x: x[1]["confidence"] * strategy_weights[x[0]],
            reverse=True
        )
        
        selected_strategy, selected_result = sorted_strategies[0]
        
        return {
            "resolution_method": "hybrid",
            "primary_strategy": selected_strategy,
            "strategy_weights": strategy_weights,
            "recommendation": selected_result["recommendation"],
            "confidence": final_confidence,
            "strategy_confidences": {
                "priority_based": priority_result["confidence"],
                "majority_vote": majority_result["confidence"],
                "weighted_vote": weighted_result["confidence"],
                "confidence_based": confidence_result["confidence"]
            }
        }
    
    def _extract_attribute_value(self, recommendation: Dict[str, Any], attribute_path: str) -> Any:
        """
        Extract a value from a nested dictionary using a dot-separated path.
        
        Args:
            recommendation: The recommendation dictionary
            attribute_path: Dot-separated path to the attribute
            
        Returns:
            Extracted value or None if not found
        """
        parts = attribute_path.split('.')
        current = recommendation
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    async def build_consensus(self, 
                            decision_point: Dict[str, Any],
                            agent_interfaces: Dict[str, Any],
                            context: Dict[str, Any] = None,
                            threshold: float = ConsensusThreshold.MEDIUM.value) -> Dict[str, Any]:
        """
        Build consensus among agents for a decision point.
        
        Args:
            decision_point: Decision point details
            agent_interfaces: Dictionary mapping agent types to interfaces
            context: Additional context for consensus building
            threshold: Consensus threshold
            
        Returns:
            Consensus result
        """
        logger.info("Building consensus for decision point: %s", decision_point.get("key"))
        
        # Generate a unique decision ID
        decision_id = decision_point.get("id", f"decision_{uuid.uuid4().hex[:8]}")
        
        # Extract options if available
        options = decision_point.get("options", [])
        
        # Collect votes from agents
        votes = {}
        tasks = []
        
        # Send vote requests to all agents
        for agent_type, interface in agent_interfaces.items():
            # Create task to get vote from agent
            task = self._get_agent_vote(
                agent_type=agent_type,
                interface=interface,
                decision_id=decision_id,
                decision_point=decision_point,
                context=context
            )
            tasks.append(task)
        
        # Wait for all votes
        agent_votes = await asyncio.gather(*tasks)
        
        # Process votes
        for vote in agent_votes:
            if vote:
                agent_type = vote.get("agent_type")
                if agent_type:
                    votes[agent_type] = vote
        
        # Calculate consensus
        consensus_result = self._calculate_consensus(votes, threshold)
        
        # Add decision metadata
        consensus_result["decision_id"] = decision_id
        consensus_result["decision_key"] = decision_point.get("key")
        consensus_result["decision_description"] = decision_point.get("description")
        consensus_result["threshold"] = threshold
        
        # If consensus not reached, try to enhance consensus
        if not consensus_result.get("consensus_reached", False):
            enhanced_result = await self._enhance_consensus(
                decision_point=decision_point,
                agent_interfaces=agent_interfaces,
                votes=votes,
                context=context,
                threshold=threshold
            )
            return enhanced_result
        
        return consensus_result
    
    async def _get_agent_vote(self,
                            agent_type: str,
                            interface: Any,
                            decision_id: str,
                            decision_point: Dict[str, Any],
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get a vote from an agent for a decision point.
        
        Args:
            agent_type: Type of agent
            interface: Agent interface
            decision_id: Decision ID
            decision_point: Decision point details
            context: Additional context
            
        Returns:
            Agent vote
        """
        try:
            # In a real implementation, this would send a message through the interface
            # and wait for a response. For now, simulate a vote.
            
            # Create vote request
            vote_request = {
                "decision_id": decision_id,
                "decision_key": decision_point.get("key"),
                "description": decision_point.get("description"),
                "options": decision_point.get("options", []),
                "context": context or {}
            }
            
            # Simulate agent vote (this would be replaced with actual agent communication)
            import random
            options = decision_point.get("options", [])
            if not options:
                return None
            
            selected_option = random.choice(options)
            confidence = random.uniform(0.6, 0.95)
            
            # Adjust confidence based on agent priority
            priority = self.agent_priorities.get(agent_type, 1)
            adjusted_confidence = min(confidence * (1 + 0.1 * priority), 1.0)
            
            return {
                "agent_type": agent_type,
                "decision_id": decision_id,
                "vote": selected_option,
                "confidence": adjusted_confidence,
                "reasoning": f"Simulated vote from {agent_type} agent"
            }
            
        except Exception as e:
            logger.error("Error getting vote from %s agent: %s", agent_type, str(e))
            return None
    
    def _calculate_consensus(self, 
                           votes: Dict[str, Dict[str, Any]],
                           threshold: float) -> Dict[str, Any]:
        """
        Calculate consensus from agent votes.
        
        Args:
            votes: Dictionary mapping agent types to votes
            threshold: Consensus threshold
            
        Returns:
            Consensus result
        """
        if not votes:
            return {
                "consensus_reached": False,
                "confidence": 0.0,
                "votes": {}
            }
        
        # Count votes for each option
        vote_counts = {}
        confidence_sums = {}
        weighted_votes = {}
        total_weight = 0
        
        for agent_type, vote in votes.items():
            option = str(vote.get("vote"))
            confidence = vote.get("confidence", 0.5)
            weight = self.agent_priorities.get(agent_type, 1)
            total_weight += weight
            
            if option not in vote_counts:
                vote_counts[option] = 0
                confidence_sums[option] = 0
                weighted_votes[option] = 0
            
            vote_counts[option] += 1
            confidence_sums[option] += confidence
            weighted_votes[option] += weight * confidence
        
        # Find option with highest weighted vote
        highest_weighted_vote = 0
        selected_option = None
        
        for option, weighted_vote in weighted_votes.items():
            if weighted_vote > highest_weighted_vote:
                highest_weighted_vote = weighted_vote
                selected_option = option
        
        # Calculate metrics
        total_votes = len(votes)
        vote_percentage = vote_counts.get(selected_option, 0) / total_votes if total_votes > 0 else 0
        avg_confidence = confidence_sums.get(selected_option, 0) / vote_counts.get(selected_option, 1)
        weighted_confidence = highest_weighted_vote / total_weight if total_weight > 0 else 0
        
        # Determine if consensus is reached
        consensus_reached = weighted_confidence >= threshold
        
        return {
            "consensus_reached": consensus_reached,
            "selected_option": selected_option,
            "vote_counts": vote_counts,
            "vote_percentage": vote_percentage,
            "average_confidence": avg_confidence,
            "weighted_confidence": weighted_confidence,
            "confidence": weighted_confidence,
            "votes": votes
        }
    
    async def _enhance_consensus(self,
                               decision_point: Dict[str, Any],
                               agent_interfaces: Dict[str, Any],
                               votes: Dict[str, Dict[str, Any]],
                               context: Dict[str, Any] = None,
                               threshold: float = ConsensusThreshold.MEDIUM.value) -> Dict[str, Any]:
        """
        Enhance consensus through additional deliberation.
        
        Args:
            decision_point: Decision point details
            agent_interfaces: Dictionary mapping agent types to interfaces
            votes: Current votes
            context: Additional context
            threshold: Consensus threshold
            
        Returns:
            Enhanced consensus result
        """
        logger.info("Enhancing consensus for decision point: %s", decision_point.get("key"))
        
        # Create enhanced context with current votes
        enhanced_context = context.copy() if context else {}
        enhanced_context["current_votes"] = votes
        enhanced_context["enhancement_round"] = True
        
        # Send enhanced vote requests to all agents
        tasks = []
        for agent_type, interface in agent_interfaces.items():
            # Create task to get enhanced vote from agent
            task = self._get_enhanced_agent_vote(
                agent_type=agent_type,
                interface=interface,
                decision_point=decision_point,
                current_votes=votes,
                context=enhanced_context
            )
            tasks.append(task)
        
        # Wait for all enhanced votes
        enhanced_votes = await asyncio.gather(*tasks)
        
        # Process enhanced votes
        enhanced_vote_dict = {}
        for vote in enhanced_votes:
            if vote:
                agent_type = vote.get("agent_type")
                if agent_type:
                    enhanced_vote_dict[agent_type] = vote
        
        # Calculate consensus with enhanced votes
        consensus_result = self._calculate_consensus(enhanced_vote_dict, threshold)
        
        # Add decision metadata
        consensus_result["decision_id"] = decision_point.get("id")
        consensus_result["decision_key"] = decision_point.get("key")
        consensus_result["decision_description"] = decision_point.get("description")
        consensus_result["threshold"] = threshold
        consensus_result["enhanced"] = True
        
        return consensus_result
    
    async def _get_enhanced_agent_vote(self,
                                     agent_type: str,
                                     interface: Any,
                                     decision_point: Dict[str, Any],
                                     current_votes: Dict[str, Dict[str, Any]],
                                     context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get an enhanced vote from an agent after seeing other votes.
        
        Args:
            agent_type: Type of agent
            interface: Agent interface
            decision_point: Decision point details
            current_votes: Current votes from all agents
            context: Additional context
            
        Returns:
            Enhanced agent vote
        """
        try:
            # In a real implementation, this would send a message through the interface
            # and wait for a response. For now, simulate an enhanced vote.
            
            # Get current vote for this agent
            current_vote = current_votes.get(agent_type, {})
            current_option = current_vote.get("vote")
            
            # Find the majority vote
            vote_counts = {}
            for vote in current_votes.values():
                option = str(vote.get("vote"))
                if option not in vote_counts:
                    vote_counts[option] = 0
                vote_counts[option] += 1
            
            majority_option = max(vote_counts.items(), key=lambda x: x[1])[0] if vote_counts else None
            
            # Simulate agent reconsidering its vote
            import random
            
            # Higher chance of switching to majority if lower priority agent
            priority = self.agent_priorities.get(agent_type, 1)
            max_priority = max(self.agent_priorities.values()) if self.agent_priorities else 1
            switch_probability = 0.3 * (1 - (priority / max_priority))
            
            # Decide whether to switch vote
            if majority_option and current_option != majority_option and random.random() < switch_probability:
                selected_option = majority_option
                confidence = random.uniform(0.7, 0.9)  # Higher confidence for consensus
            else:
                selected_option = current_option
                confidence = current_vote.get("confidence", 0.8) * 1.1  # Slightly higher confidence
            
            # Ensure confidence is not greater than 1.0
            confidence = min(confidence, 1.0)
            
            return {
                "agent_type": agent_type,
                "decision_id": decision_point.get("id"),
                "vote": selected_option,
                "confidence": confidence,
                "reasoning": f"Enhanced vote from {agent_type} agent after deliberation",
                "changed_vote": selected_option != current_option
            }
            
        except Exception as e:
            logger.error("Error getting enhanced vote from %s agent: %s", agent_type, str(e))
            return current_votes.get(agent_type)  # Return original vote on error


class ConflictDetector:
    """
    Utility class for detecting conflicts in agent recommendations.
    """
    
    @staticmethod
    def detect_conflicts(recommendations: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect conflicts between agent recommendations.
        
        Args:
            recommendations: Dictionary mapping agent types to recommendations
            
        Returns:
            List of detected conflicts
        """
        if len(recommendations) <= 1:
            return []  # No conflicts with 0 or 1 recommendation
        
        conflicts = []
        
        # Extract all keys from all recommendations
        all_keys = set()
        for recommendation in recommendations.values():
            ConflictDetector._extract_keys(recommendation, "", all_keys)
        
        # Check each key for conflicts
        for key in all_keys:
            values = {}
            for agent_type, recommendation in recommendations.items():
                value = ConflictDetector._extract_value(recommendation, key)
                if value is not None:
                    if str(value) not in values:
                        values[str(value)] = []
                    values[str(value)].append(agent_type)
            
            # If there's more than one distinct value, we have a conflict
            if len(values) > 1:
                conflicts.append({
                    "id": f"conflict_{len(conflicts) + 1}",
                    "attribute": key,
                    "values": values,
                    "agents": {agent: list(values.keys())[0] for agent, values in values.items()}
                })
        
        return conflicts
    
    @staticmethod
    def _extract_keys(obj: Any, prefix: str, keys: set) -> None:
        """
        Extract all keys from a nested object.
        
        Args:
            obj: The object to extract keys from
            prefix: Prefix for nested keys
            keys: Set to add keys to
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                keys.add(full_key)
                ConflictDetector._extract_keys(value, full_key, keys)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                full_key = f"{prefix}[{i}]"
                ConflictDetector._extract_keys(item, full_key, keys)
    
    @staticmethod
    def _extract_value(obj: Any, key_path: str) -> Any:
        """
        Extract a value from a nested object using a key path.
        
        Args:
            obj: The object to extract from
            key_path: Path to the key
            
        Returns:
            Extracted value or None if not found
        """
        parts = key_path.split('.')
        current = obj
        
        for part in parts:
            # Handle array indices
            if '[' in part and ']' in part:
                key, idx_str = part.split('[', 1)
                idx = int(idx_str.rstrip(']'))
                
                if key:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        return None
                
                if isinstance(current, list) and 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return None
            else:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
        
        return current
