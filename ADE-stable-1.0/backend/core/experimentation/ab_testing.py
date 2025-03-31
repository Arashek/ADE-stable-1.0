from typing import Dict, List, Any, Optional, Callable
import random
from datetime import datetime
import asyncio
from pydantic import BaseModel
import json
import logging
from ..monitoring.telemetry import TelemetryManager

logger = logging.getLogger(__name__)

class Experiment(BaseModel):
    id: str
    name: str
    description: str
    variants: Dict[str, float]  # variant_name -> traffic_percentage
    metrics: List[str]
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool = True

class ExperimentResult(BaseModel):
    experiment_id: str
    variant: str
    user_id: str
    metrics: Dict[str, float]
    timestamp: datetime

class ABTestingManager:
    def __init__(self, telemetry: TelemetryManager):
        self.experiments: Dict[str, Experiment] = {}
        self.results: List[ExperimentResult] = []
        self.telemetry = telemetry
        self.user_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {experiment_id -> variant}
        
    def create_experiment(self, experiment: Experiment):
        """Create a new experiment"""
        # Validate variant percentages sum to 100
        total_percentage = sum(experiment.variants.values())
        if not 99.9 <= total_percentage <= 100.1:
            raise ValueError("Variant percentages must sum to 100")
            
        self.experiments[experiment.id] = experiment
        logger.info(f"Created experiment: {experiment.name}")
        
    def get_variant(self, experiment_id: str, user_id: str) -> str:
        """Get the variant for a user in an experiment"""
        # Check if user already has an assignment
        if user_id in self.user_assignments and experiment_id in self.user_assignments[user_id]:
            return self.user_assignments[user_id][experiment_id]
            
        experiment = self.experiments.get(experiment_id)
        if not experiment or not experiment.is_active:
            return "control"  # Default to control if experiment doesn't exist or is inactive
            
        # Deterministic random assignment based on user_id and experiment_id
        random.seed(f"{user_id}:{experiment_id}")
        rand_val = random.random() * 100
        
        cumulative = 0
        for variant, percentage in experiment.variants.items():
            cumulative += percentage
            if rand_val <= cumulative:
                # Store assignment
                if user_id not in self.user_assignments:
                    self.user_assignments[user_id] = {}
                self.user_assignments[user_id][experiment_id] = variant
                return variant
                
        return "control"  # Fallback to control
        
    async def record_metric(
        self,
        experiment_id: str,
        user_id: str,
        metric_name: str,
        value: float
    ):
        """Record a metric value for an experiment"""
        experiment = self.experiments.get(experiment_id)
        if not experiment or not experiment.is_active:
            return
            
        variant = self.get_variant(experiment_id, user_id)
        
        result = ExperimentResult(
            experiment_id=experiment_id,
            variant=variant,
            user_id=user_id,
            metrics={metric_name: value},
            timestamp=datetime.utcnow()
        )
        
        self.results.append(result)
        
        # Create span for telemetry
        with self.telemetry.create_span(
            "experiment_metric",
            {
                "experiment_id": experiment_id,
                "variant": variant,
                "metric": metric_name,
                "value": value
            }
        ):
            # In production, you would want to store this in a database
            await self._store_result(result)
            
    async def _store_result(self, result: ExperimentResult):
        """Store experiment result (implement proper storage in production)"""
        # Example implementation - replace with proper storage
        with open(f"experiment_results_{result.experiment_id}.json", "a") as f:
            f.write(json.dumps(result.dict()) + "\n")
            
    def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Analyze experiment results"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")
            
        results = [r for r in self.results if r.experiment_id == experiment_id]
        
        analysis = {
            "experiment_id": experiment_id,
            "name": experiment.name,
            "total_participants": len(set(r.user_id for r in results)),
            "variants": {}
        }
        
        for variant in experiment.variants.keys():
            variant_results = [r for r in results if r.variant == variant]
            
            if not variant_results:
                continue
                
            metrics = {}
            for metric in experiment.metrics:
                values = [
                    r.metrics[metric]
                    for r in variant_results
                    if metric in r.metrics
                ]
                
                if values:
                    metrics[metric] = {
                        "count": len(values),
                        "mean": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values)
                    }
                    
            analysis["variants"][variant] = {
                "participants": len(set(r.user_id for r in variant_results)),
                "metrics": metrics
            }
            
        return analysis

# Example usage:
"""
# Create experiment
experiment = Experiment(
    id="model_improvement_test",
    name="Model Improvement A/B Test",
    description="Testing new model architecture",
    variants={
        "control": 50,
        "new_model": 50
    },
    metrics=["accuracy", "latency", "user_satisfaction"],
    start_date=datetime.utcnow()
)

# Initialize manager
ab_manager = ABTestingManager(telemetry_manager)
ab_manager.create_experiment(experiment)

# Get variant for user
variant = ab_manager.get_variant("model_improvement_test", "user123")

# Record metrics
await ab_manager.record_metric(
    "model_improvement_test",
    "user123",
    "accuracy",
    0.95
)

# Analyze results
results = ab_manager.analyze_experiment("model_improvement_test")
"""
