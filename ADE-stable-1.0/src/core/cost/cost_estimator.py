from typing import Dict, Any, Optional
import logging
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CostMetrics:
    """Cost metrics for a task or model"""
    estimated_tokens: int
    estimated_cost: float
    confidence: float
    timestamp: datetime
    model_name: str
    task_type: str
    resource_requirements: Dict[str, float]

class CostEstimator:
    """Estimates costs for tasks and model usage"""
    
    def __init__(self):
        # Token cost rates per model (cost per 1K tokens)
        self.token_costs = {
            "codellama/CodeLlama-13b": {"input": 0.0001, "output": 0.0002},
            "codellama/CodeLlama-34b": {"input": 0.0002, "output": 0.0004},
            "bigcode/starcoder": {"input": 0.0001, "output": 0.0002},
            "bigcode/starcoder2-33b": {"input": 0.0002, "output": 0.0004},
            "anthropic/claude-3-sonnet": {"input": 0.0003, "output": 0.0006},
            "gpt-4-turbo-preview": {"input": 0.0004, "output": 0.0008}
        }
        
        # Resource cost rates
        self.resource_costs = {
            "cpu": 0.0001,  # Cost per CPU-second
            "memory": 0.00001,  # Cost per MB-second
            "gpu": 0.001,  # Cost per GPU-second
            "storage": 0.000001  # Cost per MB
        }
    
    def estimate_task_cost(self, task: Dict[str, Any], model_name: str) -> CostMetrics:
        """Estimate cost for a specific task
        
        Args:
            task: Task description and parameters
            model_name: Name of the model to use
            
        Returns:
            CostMetrics object with cost estimates
        """
        try:
            # Estimate token usage
            estimated_tokens = self._estimate_tokens(task)
            
            # Calculate token costs
            token_cost = self._calculate_token_cost(estimated_tokens, model_name)
            
            # Estimate resource requirements
            resource_requirements = self._estimate_resource_requirements(task)
            
            # Calculate resource costs
            resource_cost = self._calculate_resource_cost(resource_requirements)
            
            # Calculate total cost
            total_cost = token_cost + resource_cost
            
            # Calculate confidence score
            confidence = self._calculate_confidence(task)
            
            return CostMetrics(
                estimated_tokens=estimated_tokens,
                estimated_cost=total_cost,
                confidence=confidence,
                timestamp=datetime.now(),
                model_name=model_name,
                task_type=task.get("type", "unknown"),
                resource_requirements=resource_requirements
            )
            
        except Exception as e:
            logger.error(f"Failed to estimate task cost: {str(e)}")
            raise
    
    def _estimate_tokens(self, task: Dict[str, Any]) -> int:
        """Estimate number of tokens for a task"""
        # Simple estimation based on task description length
        description = task.get("description", "")
        return len(description.split()) * 1.3  # Rough estimate: 1.3 tokens per word
    
    def _calculate_token_cost(self, tokens: int, model_name: str) -> float:
        """Calculate token-based cost"""
        if model_name not in self.token_costs:
            return 0.0
            
        costs = self.token_costs[model_name]
        input_tokens = int(tokens * 0.7)  # Assume 70% input, 30% output
        output_tokens = tokens - input_tokens
        
        input_cost = (input_tokens * costs["input"]) / 1000
        output_cost = (output_tokens * costs["output"]) / 1000
        
        return input_cost + output_cost
    
    def _estimate_resource_requirements(self, task: Dict[str, Any]) -> Dict[str, float]:
        """Estimate resource requirements for a task"""
        # Default resource requirements
        requirements = {
            "cpu": 1.0,  # CPU seconds
            "memory": 100.0,  # MB
            "gpu": 0.0,  # GPU seconds
            "storage": 10.0  # MB
        }
        
        # Adjust based on task type
        task_type = task.get("type", "")
        if "training" in task_type:
            requirements["gpu"] = 60.0  # 1 minute GPU time
            requirements["memory"] *= 2
        elif "inference" in task_type:
            requirements["gpu"] = 5.0  # 5 seconds GPU time
        elif "analysis" in task_type:
            requirements["cpu"] *= 2
            requirements["memory"] *= 1.5
            
        return requirements
    
    def _calculate_resource_cost(self, requirements: Dict[str, float]) -> float:
        """Calculate resource-based cost"""
        total_cost = 0.0
        for resource, amount in requirements.items():
            if resource in self.resource_costs:
                total_cost += amount * self.resource_costs[resource]
        return total_cost
    
    def _calculate_confidence(self, task: Dict[str, Any]) -> float:
        """Calculate confidence score for the estimate"""
        # Base confidence
        confidence = 0.7
        
        # Adjust based on task complexity
        complexity = task.get("complexity", 0.5)
        confidence -= (complexity - 0.5) * 0.2  # Reduce confidence for complex tasks
        
        # Adjust based on task type
        task_type = task.get("type", "")
        if task_type in ["training", "inference", "analysis"]:
            confidence += 0.1  # Higher confidence for standard task types
            
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence)) 