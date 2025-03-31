from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import logging
import json
from pathlib import Path

@dataclass
class CostPrediction:
    timestamp: datetime
    model_name: str
    task_type: str
    predicted_cost: float
    confidence: float
    features: Dict[str, float]
    actual_cost: Optional[float] = None

class MLCostOptimizer:
    def __init__(
        self,
        data_dir: str = "data/cost/ml",
        model_update_interval: int = 24,  # hours
        min_samples: int = 100
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.model_update_interval = model_update_interval
        self.min_samples = min_samples
        self.logger = logging.getLogger(__name__)
        
        # Initialize ML components
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        # Load historical data
        self.predictions: List[CostPrediction] = []
        self._load_historical_data()
        
        # Initialize or update model
        self._initialize_model()

    def _load_historical_data(self):
        """Load historical cost predictions and actual costs."""
        history_file = self.data_dir / "history.json"
        if history_file.exists():
            try:
                with open(history_file, "r") as f:
                    data = json.load(f)
                    self.predictions = [
                        CostPrediction(
                            timestamp=datetime.fromisoformat(p["timestamp"]),
                            model_name=p["model_name"],
                            task_type=p["task_type"],
                            predicted_cost=p["predicted_cost"],
                            confidence=p["confidence"],
                            features=p["features"],
                            actual_cost=p.get("actual_cost")
                        )
                        for p in data
                    ]
            except Exception as e:
                self.logger.error(f"Error loading historical data: {e}")
                self.predictions = []

    def _save_historical_data(self):
        """Save historical cost predictions and actual costs."""
        history_file = self.data_dir / "history.json"
        try:
            with open(history_file, "w") as f:
                json.dump(
                    [
                        {
                            "timestamp": p.timestamp.isoformat(),
                            "model_name": p.model_name,
                            "task_type": p.task_type,
                            "predicted_cost": p.predicted_cost,
                            "confidence": p.confidence,
                            "features": p.features,
                            "actual_cost": p.actual_cost
                        }
                        for p in self.predictions
                    ],
                    f,
                    indent=2
                )
        except Exception as e:
            self.logger.error(f"Error saving historical data: {e}")

    def _initialize_model(self):
        """Initialize or update the ML model with historical data."""
        if len(self.predictions) < self.min_samples:
            self.logger.warning("Insufficient historical data for model training")
            return
            
        # Prepare training data
        X = []
        y = []
        for pred in self.predictions:
            if pred.actual_cost is not None:
                X.append(list(pred.features.values()))
                y.append(pred.actual_cost)
                
        if not X or not y:
            self.logger.warning("No valid training data available")
            return
            
        # Scale features
        X = self.scaler.fit_transform(X)
        
        # Train model
        try:
            self.model.fit(X, y)
            self.logger.info("ML model trained successfully")
        except Exception as e:
            self.logger.error(f"Error training ML model: {e}")

    def _extract_features(
        self,
        task: Dict,
        model_name: str,
        resource_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """Extract features for cost prediction."""
        return {
            "task_complexity": task.get("complexity", 0.5),
            "task_length": len(task.get("description", "")),
            "model_cost_per_1k": self._get_model_cost_per_1k(model_name),
            "cpu_usage": resource_metrics.get("cpu_percent", 0),
            "memory_usage": resource_metrics.get("memory_percent", 0),
            "gpu_usage": resource_metrics.get("gpu_percent", 0),
            "hour_of_day": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
            "is_weekend": int(datetime.now().weekday() >= 5)
        }

    def _get_model_cost_per_1k(self, model_name: str) -> float:
        """Get cost per 1k tokens for a model."""
        # This should be replaced with actual model cost data
        costs = {
            "gpt-4-turbo-preview": 0.03,
            "gpt-3.5-turbo": 0.002,
            "codellama/CodeLlama-13b": 0.0
        }
        return costs.get(model_name, 0.01)

    def predict_cost(
        self,
        task: Dict,
        model_name: str,
        resource_metrics: Dict[str, float]
    ) -> CostPrediction:
        """
        Predict the cost of a task using the ML model.
        
        Args:
            task: Task description and requirements
            model_name: Name of the model to use
            resource_metrics: Current resource usage metrics
            
        Returns:
            CostPrediction object with predicted cost and confidence
        """
        # Extract features
        features = self._extract_features(task, model_name, resource_metrics)
        
        # Check if model needs updating
        if self._should_update_model():
            self._initialize_model()
        
        # Prepare features for prediction
        X = self.scaler.transform([list(features.values())])
        
        # Make prediction
        try:
            predicted_cost = float(self.model.predict(X)[0])
            confidence = self._calculate_confidence(features)
            
            prediction = CostPrediction(
                timestamp=datetime.now(),
                model_name=model_name,
                task_type=task.get("type", "general"),
                predicted_cost=predicted_cost,
                confidence=confidence,
                features=features
            )
            
            # Store prediction
            self.predictions.append(prediction)
            self._save_historical_data()
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error making cost prediction: {e}")
            return CostPrediction(
                timestamp=datetime.now(),
                model_name=model_name,
                task_type=task.get("type", "general"),
                predicted_cost=0.0,
                confidence=0.0,
                features=features
            )

    def _should_update_model(self) -> bool:
        """Check if the model should be updated based on time interval."""
        if not self.predictions:
            return True
            
        last_update = max(p.timestamp for p in self.predictions)
        return datetime.now() - last_update > timedelta(hours=self.model_update_interval)

    def _calculate_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence score for the prediction."""
        # This is a simple implementation - could be enhanced with more sophisticated methods
        feature_variance = np.var(list(features.values()))
        return 1.0 / (1.0 + feature_variance)

    def record_actual_cost(
        self,
        prediction: CostPrediction,
        actual_cost: float
    ):
        """
        Record the actual cost for a prediction to improve future predictions.
        
        Args:
            prediction: The original cost prediction
            actual_cost: The actual cost incurred
        """
        prediction.actual_cost = actual_cost
        self._save_historical_data()
        
        # Update model if we have enough new samples
        if self._should_update_model():
            self._initialize_model()

    def get_cost_optimization_suggestions(
        self,
        task: Dict,
        current_cost: float,
        resource_metrics: Dict[str, float]
    ) -> List[Dict]:
        """
        Get suggestions for cost optimization based on historical data.
        
        Args:
            task: Current task description
            current_cost: Current cost of the task
            resource_metrics: Current resource usage metrics
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        # Analyze resource usage
        if resource_metrics.get("cpu_percent", 0) > 80:
            suggestions.append({
                "type": "resource_optimization",
                "message": "High CPU usage detected. Consider optimizing task processing.",
                "potential_savings": current_cost * 0.1
            })
            
        if resource_metrics.get("memory_percent", 0) > 80:
            suggestions.append({
                "type": "resource_optimization",
                "message": "High memory usage detected. Consider implementing memory optimization.",
                "potential_savings": current_cost * 0.15
            })
            
        # Analyze historical patterns
        similar_tasks = [
            p for p in self.predictions
            if p.task_type == task.get("type", "general")
            and p.actual_cost is not None
        ]
        
        if similar_tasks:
            avg_cost = np.mean([p.actual_cost for p in similar_tasks])
            if current_cost > avg_cost * 1.2:
                suggestions.append({
                    "type": "cost_reduction",
                    "message": f"Current cost is {((current_cost/avg_cost)-1)*100:.1f}% higher than average for similar tasks.",
                    "potential_savings": current_cost - avg_cost
                })
        
        # Add model-specific suggestions
        model_name = task.get("model_name")
        if model_name:
            model_costs = [
                p.actual_cost for p in self.predictions
                if p.model_name == model_name and p.actual_cost is not None
            ]
            if model_costs:
                avg_model_cost = np.mean(model_costs)
                if current_cost > avg_model_cost * 1.1:
                    suggestions.append({
                        "type": "model_optimization",
                        "message": f"Consider using a more cost-efficient model for this task type.",
                        "potential_savings": current_cost - avg_model_cost
                    })
        
        return suggestions

    def get_cost_trends(
        self,
        time_window: timedelta = timedelta(days=7)
    ) -> Dict:
        """
        Analyze cost trends over a specified time window.
        
        Args:
            time_window: Time window to analyze
            
        Returns:
            Dictionary containing cost trend analysis
        """
        cutoff_time = datetime.now() - time_window
        recent_predictions = [
            p for p in self.predictions
            if p.timestamp >= cutoff_time and p.actual_cost is not None
        ]
        
        if not recent_predictions:
            return {
                "total_cost": 0.0,
                "average_cost": 0.0,
                "cost_trend": 0.0,
                "model_costs": {},
                "task_type_costs": {}
            }
        
        # Calculate basic metrics
        costs = [p.actual_cost for p in recent_predictions]
        total_cost = sum(costs)
        average_cost = np.mean(costs)
        
        # Calculate trend
        if len(costs) > 1:
            cost_trend = np.polyfit(range(len(costs)), costs, 1)[0]
        else:
            cost_trend = 0.0
        
        # Calculate costs by model
        model_costs = {}
        for pred in recent_predictions:
            model_costs[pred.model_name] = model_costs.get(pred.model_name, 0) + pred.actual_cost
        
        # Calculate costs by task type
        task_type_costs = {}
        for pred in recent_predictions:
            task_type_costs[pred.task_type] = task_type_costs.get(pred.task_type, 0) + pred.actual_cost
        
        return {
            "total_cost": total_cost,
            "average_cost": average_cost,
            "cost_trend": cost_trend,
            "model_costs": model_costs,
            "task_type_costs": task_type_costs
        } 