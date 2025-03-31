from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class CostMetrics:
    """Cost metrics for a model or task"""
    timestamp: datetime
    model_name: str
    task_type: str
    token_usage: Dict[str, int]
    resource_usage: Dict[str, float]
    cost: float
    confidence: float

class CostDashboard:
    """Dashboard for displaying and managing cost-related information"""
    
    def __init__(self, data_dir: str = "data/cost"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_history: Dict[str, List[CostMetrics]] = defaultdict(list)
        self.current_metrics: Dict[str, CostMetrics] = {}
        self.budgets: Dict[str, float] = {}
        self._load_data()
    
    def _load_data(self):
        """Load historical cost data"""
        try:
            metrics_file = self.data_dir / "metrics.json"
            if metrics_file.exists():
                with open(metrics_file, "r") as f:
                    data = json.load(f)
                    for model_name, metrics_list in data.items():
                        self.metrics_history[model_name] = [
                            CostMetrics(
                                timestamp=datetime.fromisoformat(m["timestamp"]),
                                model_name=m["model_name"],
                                task_type=m["task_type"],
                                token_usage=m["token_usage"],
                                resource_usage=m["resource_usage"],
                                cost=m["cost"],
                                confidence=m["confidence"]
                            )
                            for m in metrics_list
                        ]
            
            budget_file = self.data_dir / "budgets.json"
            if budget_file.exists():
                with open(budget_file, "r") as f:
                    self.budgets = json.load(f)
                    
        except Exception as e:
            logger.error(f"Failed to load cost data: {str(e)}")
    
    def _save_data(self):
        """Save cost data to disk"""
        try:
            # Save metrics
            metrics_data = {
                model_name: [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "model_name": m.model_name,
                        "task_type": m.task_type,
                        "token_usage": m.token_usage,
                        "resource_usage": m.resource_usage,
                        "cost": m.cost,
                        "confidence": m.confidence
                    }
                    for m in metrics_list
                ]
                for model_name, metrics_list in self.metrics_history.items()
            }
            
            with open(self.data_dir / "metrics.json", "w") as f:
                json.dump(metrics_data, f)
            
            # Save budgets
            with open(self.data_dir / "budgets.json", "w") as f:
                json.dump(self.budgets, f)
                
        except Exception as e:
            logger.error(f"Failed to save cost data: {str(e)}")
    
    def record_metrics(self, metrics: CostMetrics):
        """Record cost metrics
        
        Args:
            metrics: Cost metrics to record
        """
        try:
            model_name = metrics.model_name
            
            # Update current metrics
            self.current_metrics[model_name] = metrics
            
            # Add to history
            self.metrics_history[model_name].append(metrics)
            
            # Save data
            self._save_data()
            
        except Exception as e:
            logger.error(f"Failed to record metrics: {str(e)}")
    
    def set_budget(self, model_name: str, budget: float):
        """Set budget for a model
        
        Args:
            model_name: Name of the model
            budget: Budget amount
        """
        self.budgets[model_name] = budget
        self._save_data()
    
    def get_cost_summary(self, time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Get cost summary for all models
        
        Args:
            time_window: Time window for summary
            
        Returns:
            Dictionary of cost summaries
        """
        summary = {}
        try:
            cutoff_time = datetime.now() - time_window
            
            for model_name, history in self.metrics_history.items():
                recent_metrics = [m for m in history if m.timestamp >= cutoff_time]
                if not recent_metrics:
                    continue
                
                costs = [m.cost for m in recent_metrics]
                total_tokens = sum(
                    sum(m.token_usage.values()) for m in recent_metrics
                )
                
                summary[model_name] = {
                    "total_cost": sum(costs),
                    "avg_cost": sum(costs) / len(costs),
                    "total_tokens": total_tokens,
                    "cost_per_token": sum(costs) / total_tokens if total_tokens > 0 else 0,
                    "budget": self.budgets.get(model_name, 0),
                    "budget_remaining": self.budgets.get(model_name, 0) - sum(costs),
                    "num_requests": len(recent_metrics)
                }
            
        except Exception as e:
            logger.error(f"Failed to get cost summary: {str(e)}")
        
        return summary
    
    def get_cost_alerts(self) -> List[Dict[str, Any]]:
        """Get cost-related alerts
        
        Returns:
            List of cost alerts
        """
        alerts = []
        try:
            summary = self.get_cost_summary()
            
            for model_name, metrics in summary.items():
                # Check budget
                if metrics["budget"] > 0 and metrics["budget_remaining"] < 0:
                    alerts.append({
                        "type": "budget_exceeded",
                        "severity": "error",
                        "model": model_name,
                        "message": f"Budget exceeded by ${abs(metrics['budget_remaining']):.2f}"
                    })
                
                # Check high cost per token
                if metrics["cost_per_token"] > 0.01:  # $0.01 per token threshold
                    alerts.append({
                        "type": "high_cost_per_token",
                        "severity": "warning",
                        "model": model_name,
                        "message": f"High cost per token: ${metrics['cost_per_token']:.4f}"
                    })
                
                # Check budget usage
                if metrics["budget"] > 0 and metrics["total_cost"] / metrics["budget"] > 0.8:
                    alerts.append({
                        "type": "high_budget_usage",
                        "severity": "warning",
                        "model": model_name,
                        "message": f"High budget usage: {metrics['total_cost'] / metrics['budget']:.1%}"
                    })
            
        except Exception as e:
            logger.error(f"Failed to get cost alerts: {str(e)}")
        
        return alerts
    
    def get_cost_trends(self, model_name: str, time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Get cost trends for a model
        
        Args:
            model_name: Name of the model
            time_window: Time window for trends
            
        Returns:
            Dictionary of cost trends
        """
        trends = {}
        try:
            if model_name not in self.metrics_history:
                return trends
            
            cutoff_time = datetime.now() - time_window
            recent_metrics = [
                m for m in self.metrics_history[model_name]
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return trends
            
            # Sort by timestamp
            recent_metrics.sort(key=lambda x: x.timestamp)
            
            # Calculate trends
            costs = [m.cost for m in recent_metrics]
            timestamps = [m.timestamp for m in recent_metrics]
            
            trends = {
                "costs": costs,
                "timestamps": [t.isoformat() for t in timestamps],
                "total_cost": sum(costs),
                "avg_cost": sum(costs) / len(costs),
                "cost_trend": (costs[-1] - costs[0]) / len(costs) if len(costs) > 1 else 0,
                "num_requests": len(recent_metrics)
            }
            
        except Exception as e:
            logger.error(f"Failed to get cost trends: {str(e)}")
        
        return trends 