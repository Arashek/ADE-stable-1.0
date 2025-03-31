from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from src.core.cost.cost_estimator import CostEstimator, CostMetrics
from src.core.monitoring.model_performance import ModelPerformanceMonitor, PerformanceMetrics
from src.core.resource.resource_tracker import ResourceTracker, ResourceMetrics

@dataclass
class ModelConfig:
    name: str
    cost_per_1k_tokens: float
    max_tokens: int
    min_latency: float
    max_latency: float
    min_throughput: int
    max_throughput: int
    min_success_rate: float
    max_error_rate: float
    resource_requirements: Dict[str, float]
    priority: int  # Higher number = higher priority
    capabilities: List[str]  # List of task types this model can handle
    quality_threshold: float  # Minimum quality score required
    reliability_score: float  # Model's historical reliability (0-1)
    cost_efficiency: float  # Cost per quality point (0-1)
    context_window: int  # Maximum context window size
    token_speed: float  # Tokens processed per second
    memory_efficiency: float  # Memory usage efficiency (0-1)
    gpu_efficiency: float  # GPU utilization efficiency (0-1)
    fallback_models: List[str]  # List of fallback models if this one fails
    specializations: Dict[str, float]  # Task type to specialization score mapping

class ModelSwitcher:
    def __init__(
        self,
        cost_estimator: CostEstimator,
        performance_monitor: ModelPerformanceMonitor,
        resource_tracker: ResourceTracker,
        model_configs: Dict[str, ModelConfig]
    ):
        self.cost_estimator = cost_estimator
        self.performance_monitor = performance_monitor
        self.resource_tracker = resource_tracker
        self.model_configs = model_configs
        self.current_model: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        self.quality_weights = {
            "latency": 0.2,
            "throughput": 0.15,
            "success_rate": 0.25,
            "error_rate": 0.15,
            "resource_efficiency": 0.15,
            "cost_efficiency": 0.1
        }

    def select_model(
        self,
        task: Dict,
        budget: Optional[float] = None,
        min_success_rate: Optional[float] = None
    ) -> Tuple[str, float]:
        """
        Select the most appropriate model for the task based on cost, performance, and resource availability.
        
        Args:
            task: Task description and requirements
            budget: Optional budget constraint
            min_success_rate: Optional minimum success rate requirement
            
        Returns:
            Tuple of (selected_model_name, confidence_score)
        """
        task_type = task.get("type", "general")
        
        # Get current resource metrics
        resource_metrics = self.resource_tracker.collect_metrics(
            model_name=self.current_model or "system",
            task_id=task.get("id", "unknown")
        )
        
        # Get performance metrics for all models
        model_performances = {}
        for model_name in self.model_configs:
            performance = self.performance_monitor.get_model_performance(model_name)
            if performance:
                model_performances[model_name] = performance
        
        # Calculate scores for each model
        model_scores = {}
        for model_name, config in self.model_configs.items():
            # Skip if model doesn't support the task type
            if task_type not in config.capabilities:
                continue
                
            # Skip if model doesn't meet basic requirements
            if not self._meets_basic_requirements(model_name, config, resource_metrics):
                continue
                
            # Calculate cost score
            cost_metrics = self.cost_estimator.estimate_task_cost(task, model_name)
            if budget and cost_metrics.estimated_cost > budget:
                continue
                
            # Calculate performance score
            performance = model_performances.get(model_name, {})
            performance_score = self._calculate_performance_score(
                performance,
                config,
                min_success_rate
            )
            
            # Calculate resource score
            resource_score = self._calculate_resource_score(
                config.resource_requirements,
                resource_metrics,
                task_type
            )
            
            # Calculate specialization score
            specialization_score = config.specializations.get(task_type, 0.5)
            
            # Calculate final score with all factors
            final_score = (
                performance_score * 0.35 +
                resource_score * 0.25 +
                specialization_score * 0.2 +
                (1 - cost_metrics.estimated_cost / (budget or float('inf'))) * 0.2
            ) * config.priority
            
            model_scores[model_name] = final_score
        
        if not model_scores:
            self.logger.warning("No suitable models found for the task")
            return None, 0.0
            
        # Select model with highest score
        selected_model = max(model_scores.items(), key=lambda x: x[1])
        confidence = min(selected_model[1] / 100, 1.0)  # Normalize confidence
        
        self.logger.info(
            f"Selected model {selected_model[0]} with confidence {confidence:.2f}"
        )
        return selected_model[0], confidence

    def _meets_basic_requirements(
        self,
        model_name: str,
        config: ModelConfig,
        resource_metrics: ResourceMetrics
    ) -> bool:
        """Check if model meets basic resource and performance requirements."""
        # Check resource availability
        if resource_metrics.cpu_percent + config.resource_requirements.get("cpu", 0) > 90:
            return False
        if resource_metrics.memory_percent + config.resource_requirements.get("memory", 0) > 90:
            return False
        if resource_metrics.gpu_percent + config.resource_requirements.get("gpu", 0) > 90:
            return False
            
        # Check performance metrics
        performance = self.performance_monitor.get_model_performance(model_name)
        if not performance:
            return True  # No performance data yet, assume model is viable
            
        current = performance.get("current", {})
        if current.get("error_rate", 0) > config.max_error_rate:
            return False
        if current.get("success_rate", 1) < config.min_success_rate:
            return False
            
        return True

    def _calculate_performance_score(
        self,
        performance: Dict,
        config: ModelConfig,
        min_success_rate: Optional[float]
    ) -> float:
        """Calculate performance score based on current metrics and model capabilities."""
        if not performance:
            return 1.0
            
        current = performance.get("current", {})
        stats = performance.get("statistics", {})
        
        # Calculate weighted scores for each metric
        scores = {}
        
        # Latency score with context window consideration
        latency = current.get("latency", 0)
        context_factor = min(
            config.context_window / 8192,  # Normalize to standard context window
            1.0
        )
        latency_score = (1 - min(
            (latency - config.min_latency) / (config.max_latency - config.min_latency),
            1
        )) * context_factor
        
        # Throughput score with token speed consideration
        throughput = current.get("throughput", 0)
        speed_factor = min(
            throughput / config.token_speed,
            1.0
        )
        throughput_score = min(
            throughput / config.max_throughput,
            1
        ) * speed_factor
        
        # Success rate score with reliability consideration
        success_rate = current.get("success_rate", 1)
        min_rate = min_success_rate or config.min_success_rate
        success_score = max(0, (success_rate - min_rate) / (1 - min_rate)) * config.reliability_score
        
        # Error rate score with quality threshold
        error_rate = current.get("error_rate", 0)
        error_score = (1 - min(error_rate / config.max_error_rate, 1)) * config.quality_threshold
        
        # Resource efficiency score
        resource_efficiency = (
            config.memory_efficiency * 0.4 +
            config.gpu_efficiency * 0.4 +
            config.cost_efficiency * 0.2
        )
        
        # Calculate final weighted score
        final_score = (
            latency_score * self.quality_weights["latency"] +
            throughput_score * self.quality_weights["throughput"] +
            success_score * self.quality_weights["success_rate"] +
            error_score * self.quality_weights["error_rate"] +
            resource_efficiency * self.quality_weights["resource_efficiency"] +
            config.cost_efficiency * self.quality_weights["cost_efficiency"]
        )
        
        return final_score

    def _calculate_resource_score(
        self,
        requirements: Dict[str, float],
        current_metrics: ResourceMetrics,
        task_type: str
    ) -> float:
        """Calculate resource availability score with task-specific considerations."""
        # Base resource scores
        cpu_score = 1 - min(
            (current_metrics.cpu_percent + requirements.get("cpu", 0)) / 100,
            1
        )
        memory_score = 1 - min(
            (current_metrics.memory_percent + requirements.get("memory", 0)) / 100,
            1
        )
        gpu_score = 1 - min(
            (current_metrics.gpu_percent + requirements.get("gpu", 0)) / 100,
            1
        )
        
        # Task-specific resource efficiency
        task_efficiency = 1.0
        if task_type in ["inference", "generation"]:
            task_efficiency = min(
                current_metrics.gpu_percent / 100,
                1.0
            )
        elif task_type in ["analysis", "processing"]:
            task_efficiency = min(
                current_metrics.cpu_percent / 100,
                1.0
            )
        
        # Calculate weighted final score
        return (
            cpu_score * 0.3 +
            memory_score * 0.3 +
            gpu_score * 0.2 +
            task_efficiency * 0.2
        )

    def switch_model(self, new_model: str) -> bool:
        """
        Switch to a new model if it's different from the current one.
        
        Args:
            new_model: Name of the model to switch to
            
        Returns:
            bool: True if switch was successful, False otherwise
        """
        if new_model == self.current_model:
            return True
            
        if new_model not in self.model_configs:
            self.logger.error(f"Model {new_model} not found in configurations")
            return False
            
        # Check if we have enough resources for the new model
        config = self.model_configs[new_model]
        resource_metrics = self.resource_tracker.collect_metrics(
            model_name=self.current_model or "system",
            task_id="model_switch"
        )
        
        if not self._meets_basic_requirements(new_model, config, resource_metrics):
            self.logger.warning(f"Insufficient resources for model {new_model}")
            return False
            
        self.logger.info(f"Switching from {self.current_model} to {new_model}")
        self.current_model = new_model
        return True

    def get_model_recommendations(
        self,
        task: Dict,
        budget: Optional[float] = None,
        min_success_rate: Optional[float] = None,
        max_recommendations: int = 3
    ) -> List[Dict]:
        """
        Get recommendations for models to use, ordered by suitability.
        
        Args:
            task: Task description and requirements
            budget: Optional budget constraint
            min_success_rate: Optional minimum success rate requirement
            max_recommendations: Maximum number of recommendations to return
            
        Returns:
            List of model recommendations with scores and reasons
        """
        recommendations = []
        
        for model_name, config in self.model_configs.items():
            # Skip if model doesn't meet basic requirements
            resource_metrics = self.resource_tracker.collect_metrics(
                model_name=self.current_model or "system",
                task_id=task.get("id", "unknown")
            )
            
            if not self._meets_basic_requirements(model_name, config, resource_metrics):
                continue
                
            # Calculate cost
            cost_metrics = self.cost_estimator.estimate_task_cost(task, model_name)
            if budget and cost_metrics.estimated_cost > budget:
                continue
                
            # Get performance metrics
            performance = self.performance_monitor.get_model_performance(model_name)
            
            # Calculate scores
            performance_score = self._calculate_performance_score(
                performance,
                config,
                min_success_rate
            )
            resource_score = self._calculate_resource_score(
                config.resource_requirements,
                resource_metrics,
                task.get("type", "general")
            )
            cost_score = 1 - min(
                cost_metrics.estimated_cost / (budget or float('inf')),
                1
            )
            
            # Calculate final score
            final_score = (
                performance_score * 0.4 +
                resource_score * 0.3 +
                cost_score * 0.3
            ) * config.priority
            
            recommendations.append({
                "model_name": model_name,
                "score": final_score,
                "cost": cost_metrics.estimated_cost,
                "performance_score": performance_score,
                "resource_score": resource_score,
                "cost_score": cost_score,
                "priority": config.priority
            })
        
        # Sort by score and limit recommendations
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:max_recommendations] 