from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectFromModel
import logging
import json
from pathlib import Path
import pandas as pd
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots

@dataclass
class EnhancedFeatures:
    basic_features: Dict[str, float]
    derived_features: Dict[str, float]
    temporal_features: Dict[str, float]
    resource_features: Dict[str, float]
    task_features: Dict[str, float]

class MLEnsemble:
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
        self.rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.gb_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        
        # Create ensemble
        self.ensemble = VotingRegressor([
            ('rf', self.rf_model),
            ('gb', self.gb_model)
        ])
        
        self.scaler = StandardScaler()
        self.feature_selector = SelectFromModel(self.rf_model)
        
        # Load historical data
        self.predictions: List[Dict] = []
        self._load_historical_data()
        
        # Initialize or update model
        self._initialize_model()

    def _load_historical_data(self):
        """Load historical cost predictions and actual costs."""
        history_file = self.data_dir / "history.json"
        if history_file.exists():
            try:
                with open(history_file, "r") as f:
                    self.predictions = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading historical data: {e}")
                self.predictions = []

    def _save_historical_data(self):
        """Save historical cost predictions and actual costs."""
        history_file = self.data_dir / "history.json"
        try:
            with open(history_file, "w") as f:
                json.dump(self.predictions, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving historical data: {e}")

    def _extract_enhanced_features(
        self,
        task: Dict,
        model_name: str,
        resource_metrics: Dict[str, float]
    ) -> EnhancedFeatures:
        """Extract enhanced features for cost prediction."""
        # Basic features
        basic_features = {
            "task_complexity": task.get("complexity", 0.5),
            "task_length": len(task.get("description", "")),
            "model_cost_per_1k": self._get_model_cost_per_1k(model_name),
            "cpu_usage": resource_metrics.get("cpu_percent", 0),
            "memory_usage": resource_metrics.get("memory_percent", 0),
            "gpu_usage": resource_metrics.get("gpu_percent", 0)
        }
        
        # Derived features
        derived_features = {
            "resource_utilization": (
                basic_features["cpu_usage"] +
                basic_features["memory_usage"] +
                basic_features["gpu_usage"]
            ) / 3,
            "task_density": basic_features["task_complexity"] * basic_features["task_length"],
            "cost_efficiency": basic_features["model_cost_per_1k"] * basic_features["task_complexity"]
        }
        
        # Temporal features
        now = datetime.now()
        temporal_features = {
            "hour_of_day": now.hour,
            "day_of_week": now.weekday(),
            "is_weekend": int(now.weekday() >= 5),
            "is_business_hour": int(9 <= now.hour <= 17),
            "is_peak_hour": int(now.hour in [10, 11, 14, 15]),
            "month": now.month,
            "season": (now.month % 12 + 3) // 3
        }
        
        # Resource features
        resource_features = {
            "cpu_memory_ratio": basic_features["cpu_usage"] / (basic_features["memory_usage"] + 1e-6),
            "gpu_utilization": basic_features["gpu_usage"] / 100,
            "resource_saturation": max(
                basic_features["cpu_usage"],
                basic_features["memory_usage"],
                basic_features["gpu_usage"]
            ) / 100
        }
        
        # Task features
        task_features = {
            "complexity_score": self._calculate_complexity_score(task),
            "priority_score": task.get("priority", 0.5),
            "urgency_score": task.get("urgency", 0.5),
            "dependency_score": len(task.get("dependencies", [])) / 10
        }
        
        return EnhancedFeatures(
            basic_features=basic_features,
            derived_features=derived_features,
            temporal_features=temporal_features,
            resource_features=resource_features,
            task_features=task_features
        )

    def _calculate_complexity_score(self, task: Dict) -> float:
        """Calculate task complexity score based on multiple factors."""
        description = task.get("description", "")
        complexity = task.get("complexity", 0.5)
        
        # Calculate code complexity indicators
        code_indicators = [
            "function", "class", "method", "loop", "condition",
            "exception", "recursion", "algorithm", "optimization"
        ]
        
        code_complexity = sum(
            1 for indicator in code_indicators
            if indicator in description.lower()
        ) / len(code_indicators)
        
        # Combine with explicit complexity
        return (complexity + code_complexity) / 2

    def _get_model_cost_per_1k(self, model_name: str) -> float:
        """Get cost per 1k tokens for a model."""
        costs = {
            "gpt-4-turbo-preview": 0.03,
            "gpt-3.5-turbo": 0.002,
            "codellama/CodeLlama-13b": 0.0
        }
        return costs.get(model_name, 0.01)

    def _prepare_features(self, features: EnhancedFeatures) -> np.ndarray:
        """Prepare features for model input."""
        all_features = {
            **features.basic_features,
            **features.derived_features,
            **features.temporal_features,
            **features.resource_features,
            **features.task_features
        }
        return np.array(list(all_features.values())).reshape(1, -1)

    def predict_cost(
        self,
        task: Dict,
        model_name: str,
        resource_metrics: Dict[str, float]
    ) -> Dict:
        """
        Predict the cost of a task using the ensemble model.
        
        Args:
            task: Task description and requirements
            model_name: Name of the model to use
            resource_metrics: Current resource usage metrics
            
        Returns:
            Dictionary containing prediction details
        """
        # Extract enhanced features
        features = self._extract_enhanced_features(task, model_name, resource_metrics)
        
        # Check if model needs updating
        if self._should_update_model():
            self._initialize_model()
        
        # Prepare features for prediction
        X = self._prepare_features(features)
        X_scaled = self.scaler.transform(X)
        
        # Make prediction
        try:
            predicted_cost = float(self.ensemble.predict(X_scaled)[0])
            confidence = self._calculate_confidence(features)
            
            prediction = {
                "timestamp": datetime.now().isoformat(),
                "model_name": model_name,
                "task_type": task.get("type", "general"),
                "predicted_cost": predicted_cost,
                "confidence": confidence,
                "features": {
                    "basic": features.basic_features,
                    "derived": features.derived_features,
                    "temporal": features.temporal_features,
                    "resource": features.resource_features,
                    "task": features.task_features
                }
            }
            
            # Store prediction
            self.predictions.append(prediction)
            self._save_historical_data()
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error making cost prediction: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "model_name": model_name,
                "task_type": task.get("type", "general"),
                "predicted_cost": 0.0,
                "confidence": 0.0,
                "features": {
                    "basic": features.basic_features,
                    "derived": features.derived_features,
                    "temporal": features.temporal_features,
                    "resource": features.resource_features,
                    "task": features.task_features
                }
            }

    def _should_update_model(self) -> bool:
        """Check if the model should be updated based on time interval."""
        if not self.predictions:
            return True
            
        last_update = max(
            datetime.fromisoformat(p["timestamp"])
            for p in self.predictions
        )
        return datetime.now() - last_update > timedelta(hours=self.model_update_interval)

    def _calculate_confidence(self, features: EnhancedFeatures) -> float:
        """Calculate confidence score for the prediction."""
        # Calculate feature stability scores
        basic_stability = 1.0 / (1.0 + np.var(list(features.basic_features.values())))
        derived_stability = 1.0 / (1.0 + np.var(list(features.derived_features.values())))
        resource_stability = 1.0 / (1.0 + np.var(list(features.resource_features.values())))
        
        # Calculate historical similarity score
        historical_similarity = self._calculate_historical_similarity(features)
        
        # Combine scores with weights
        return (
            0.3 * basic_stability +
            0.3 * derived_stability +
            0.2 * resource_stability +
            0.2 * historical_similarity
        )

    def _calculate_historical_similarity(self, features: EnhancedFeatures) -> float:
        """Calculate similarity score with historical predictions."""
        if not self.predictions:
            return 0.5
            
        # Extract feature vectors from historical predictions
        historical_features = []
        for pred in self.predictions:
            if "features" in pred:
                hist_features = {
                    **pred["features"]["basic"],
                    **pred["features"]["derived"],
                    **pred["features"]["resource"]
                }
                historical_features.append(list(hist_features.values()))
        
        if not historical_features:
            return 0.5
            
        # Calculate current feature vector
        current_features = {
            **features.basic_features,
            **features.derived_features,
            **features.resource_features
        }
        current_vector = list(current_features.values())
        
        # Calculate cosine similarity with historical features
        similarities = [
            np.dot(current_vector, hist) / (
                np.linalg.norm(current_vector) * np.linalg.norm(hist)
            )
            for hist in historical_features
        ]
        
        return np.mean(similarities)

    def visualize_cost_trends(
        self,
        time_window: timedelta = timedelta(days=7)
    ) -> go.Figure:
        """
        Create interactive visualizations for cost trends.
        
        Args:
            time_window: Time window to analyze
            
        Returns:
            Plotly figure with multiple subplots
        """
        cutoff_time = datetime.now() - time_window
        recent_predictions = [
            p for p in self.predictions
            if datetime.fromisoformat(p["timestamp"]) >= cutoff_time
        ]
        
        if not recent_predictions:
            return go.Figure()
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                "Cost Over Time",
                "Cost by Model",
                "Cost by Task Type",
                "Resource Usage vs Cost",
                "Prediction Confidence",
                "Feature Importance"
            )
        )
        
        # Cost over time
        times = [datetime.fromisoformat(p["timestamp"]) for p in recent_predictions]
        costs = [p["predicted_cost"] for p in recent_predictions]
        fig.add_trace(
            go.Scatter(x=times, y=costs, mode="lines+markers", name="Cost"),
            row=1, col=1
        )
        
        # Cost by model
        model_costs = {}
        for pred in recent_predictions:
            model = pred["model_name"]
            model_costs[model] = model_costs.get(model, 0) + pred["predicted_cost"]
        fig.add_trace(
            go.Bar(x=list(model_costs.keys()), y=list(model_costs.values()), name="Model Costs"),
            row=1, col=2
        )
        
        # Cost by task type
        task_costs = {}
        for pred in recent_predictions:
            task_type = pred["task_type"]
            task_costs[task_type] = task_costs.get(task_type, 0) + pred["predicted_cost"]
        fig.add_trace(
            go.Bar(x=list(task_costs.keys()), y=list(task_costs.values()), name="Task Costs"),
            row=2, col=1
        )
        
        # Resource usage vs cost
        cpu_usage = [p["features"]["basic"]["cpu_usage"] for p in recent_predictions]
        memory_usage = [p["features"]["basic"]["memory_usage"] for p in recent_predictions]
        costs = [p["predicted_cost"] for p in recent_predictions]
        
        fig.add_trace(
            go.Scatter(x=cpu_usage, y=costs, mode="markers", name="CPU vs Cost"),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(x=memory_usage, y=costs, mode="markers", name="Memory vs Cost"),
            row=2, col=2
        )
        
        # Prediction confidence
        confidences = [p["confidence"] for p in recent_predictions]
        fig.add_trace(
            go.Histogram(x=confidences, name="Confidence Distribution"),
            row=3, col=1
        )
        
        # Feature importance
        if hasattr(self.ensemble, "named_estimators_") and "rf" in self.ensemble.named_estimators_:
            rf_model = self.ensemble.named_estimators_["rf"]
            feature_importance = rf_model.feature_importances_
            feature_names = list(features.basic_features.keys()) + \
                          list(features.derived_features.keys()) + \
                          list(features.temporal_features.keys()) + \
                          list(features.resource_features.keys()) + \
                          list(features.task_features.keys())
            
            fig.add_trace(
                go.Bar(x=feature_names, y=feature_importance, name="Feature Importance"),
                row=3, col=2
            )
        
        # Update layout
        fig.update_layout(
            height=1200,
            showlegend=True,
            title_text="Cost Analysis Dashboard"
        )
        
        return fig

    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores from the model.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not hasattr(self.ensemble, "named_estimators_") or "rf" not in self.ensemble.named_estimators_:
            return {}
            
        rf_model = self.ensemble.named_estimators_["rf"]
        feature_importance = rf_model.feature_importances_
        
        # Get feature names from a sample prediction
        sample_features = self._extract_enhanced_features(
            {"description": "", "type": "general"},
            "gpt-4-turbo-preview",
            {"cpu_percent": 0, "memory_percent": 0, "gpu_percent": 0}
        )
        
        feature_names = (
            list(sample_features.basic_features.keys()) +
            list(sample_features.derived_features.keys()) +
            list(sample_features.temporal_features.keys()) +
            list(sample_features.resource_features.keys()) +
            list(sample_features.task_features.keys())
        )
        
        return dict(zip(feature_names, feature_importance))

    def get_model_performance_metrics(self) -> Dict:
        """
        Get model performance metrics.
        
        Returns:
            Dictionary containing various performance metrics
        """
        if len(self.predictions) < 2:
            return {}
            
        # Calculate prediction accuracy
        actual_costs = [p.get("actual_cost", 0) for p in self.predictions]
        predicted_costs = [p["predicted_cost"] for p in self.predictions]
        
        mse = np.mean((np.array(actual_costs) - np.array(predicted_costs)) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(np.array(actual_costs) - np.array(predicted_costs)))
        
        # Calculate R-squared score
        actual_mean = np.mean(actual_costs)
        ss_tot = np.sum((np.array(actual_costs) - actual_mean) ** 2)
        ss_res = np.sum((np.array(actual_costs) - np.array(predicted_costs)) ** 2)
        r2 = 1 - (ss_res / ss_tot)
        
        return {
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
            "total_predictions": len(self.predictions),
            "feature_importance": self.get_feature_importance()
        } 