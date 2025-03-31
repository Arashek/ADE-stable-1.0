from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for a model"""
    model_name: str
    timestamp: datetime
    latency: float
    throughput: int
    error_rate: float
    success_rate: float
    resource_usage: Dict[str, float]
    cost_per_request: float
    token_usage: Dict[str, int]

class ModelPerformanceMonitor:
    """Monitors and analyzes model performance metrics"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.metrics_history: Dict[str, List[PerformanceMetrics]] = defaultdict(list)
        self.current_metrics: Dict[str, PerformanceMetrics] = {}
        self._initialize_metrics()
    
    def _initialize_metrics(self):
        """Initialize metrics tracking"""
        self.metrics = {
            "latency": defaultdict(list),
            "throughput": defaultdict(int),
            "error_rate": defaultdict(int),
            "success_rate": defaultdict(int),
            "resource_usage": defaultdict(list),
            "cost_per_request": defaultdict(list),
            "token_usage": defaultdict(lambda: {"input": 0, "output": 0})
        }
    
    def record_metrics(self, metrics: PerformanceMetrics):
        """Record performance metrics for a model
        
        Args:
            metrics: Performance metrics to record
        """
        try:
            model_name = metrics.model_name
            
            # Update current metrics
            self.current_metrics[model_name] = metrics
            
            # Add to history
            self.metrics_history[model_name].append(metrics)
            
            # Trim history if needed
            if len(self.metrics_history[model_name]) > self.window_size:
                self.metrics_history[model_name] = self.metrics_history[model_name][-self.window_size:]
            
            # Update aggregated metrics
            self._update_aggregated_metrics(model_name, metrics)
            
        except Exception as e:
            logger.error(f"Failed to record metrics: {str(e)}")
    
    def _update_aggregated_metrics(self, model_name: str, metrics: PerformanceMetrics):
        """Update aggregated metrics for a model"""
        # Update latency
        self.metrics["latency"][model_name].append(metrics.latency)
        if len(self.metrics["latency"][model_name]) > self.window_size:
            self.metrics["latency"][model_name] = self.metrics["latency"][model_name][-self.window_size:]
        
        # Update throughput
        self.metrics["throughput"][model_name] += 1
        
        # Update error and success rates
        if metrics.error_rate > 0:
            self.metrics["error_rate"][model_name] += 1
        if metrics.success_rate > 0:
            self.metrics["success_rate"][model_name] += 1
        
        # Update resource usage
        for resource, usage in metrics.resource_usage.items():
            self.metrics["resource_usage"][model_name].append(usage)
            if len(self.metrics["resource_usage"][model_name]) > self.window_size:
                self.metrics["resource_usage"][model_name] = self.metrics["resource_usage"][model_name][-self.window_size:]
        
        # Update cost per request
        self.metrics["cost_per_request"][model_name].append(metrics.cost_per_request)
        if len(self.metrics["cost_per_request"][model_name]) > self.window_size:
            self.metrics["cost_per_request"][model_name] = self.metrics["cost_per_request"][model_name][-self.window_size:]
        
        # Update token usage
        self.metrics["token_usage"][model_name]["input"] += metrics.token_usage.get("input", 0)
        self.metrics["token_usage"][model_name]["output"] += metrics.token_usage.get("output", 0)
    
    def get_model_performance(self, model_name: str) -> Dict[str, Any]:
        """Get performance metrics for a specific model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary of performance metrics
        """
        try:
            if model_name not in self.current_metrics:
                return {}
            
            current = self.current_metrics[model_name]
            history = self.metrics_history[model_name]
            
            # Calculate statistics
            latencies = [m.latency for m in history]
            costs = [m.cost_per_request for m in history]
            
            return {
                "current": {
                    "latency": current.latency,
                    "throughput": current.throughput,
                    "error_rate": current.error_rate,
                    "success_rate": current.success_rate,
                    "resource_usage": current.resource_usage,
                    "cost_per_request": current.cost_per_request,
                    "token_usage": current.token_usage
                },
                "statistics": {
                    "avg_latency": statistics.mean(latencies) if latencies else 0,
                    "p95_latency": statistics.quantiles(latencies, n=20)[-1] if latencies else 0,
                    "avg_cost": statistics.mean(costs) if costs else 0,
                    "total_requests": len(history),
                    "error_rate": self.metrics["error_rate"][model_name] / len(history) if history else 0,
                    "success_rate": self.metrics["success_rate"][model_name] / len(history) if history else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get model performance: {str(e)}")
            return {}
    
    def get_performance_alerts(self, model_name: str) -> List[Dict[str, Any]]:
        """Get performance alerts for a model
        
        Args:
            model_name: Name of the model
            
        Returns:
            List of performance alerts
        """
        alerts = []
        try:
            performance = self.get_model_performance(model_name)
            if not performance:
                return alerts
            
            current = performance["current"]
            stats = performance["statistics"]
            
            # Check latency
            if current["latency"] > stats["p95_latency"] * 1.5:
                alerts.append({
                    "type": "high_latency",
                    "severity": "warning",
                    "message": f"High latency detected: {current['latency']:.2f}s"
                })
            
            # Check error rate
            if current["error_rate"] > 0.05:  # 5% threshold
                alerts.append({
                    "type": "high_error_rate",
                    "severity": "error",
                    "message": f"High error rate detected: {current['error_rate']:.2%}"
                })
            
            # Check resource usage
            for resource, usage in current["resource_usage"].items():
                if usage > 0.9:  # 90% threshold
                    alerts.append({
                        "type": "high_resource_usage",
                        "severity": "warning",
                        "message": f"High {resource} usage: {usage:.2%}"
                    })
            
            # Check cost
            if current["cost_per_request"] > stats["avg_cost"] * 2:
                alerts.append({
                    "type": "high_cost",
                    "severity": "warning",
                    "message": f"High cost per request: ${current['cost_per_request']:.4f}"
                })
            
        except Exception as e:
            logger.error(f"Failed to get performance alerts: {str(e)}")
        
        return alerts
    
    def get_performance_summary(self, time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Get performance summary for all models
        
        Args:
            time_window: Time window for summary
            
        Returns:
            Dictionary of performance summaries
        """
        summary = {}
        try:
            cutoff_time = datetime.now() - time_window
            
            for model_name, history in self.metrics_history.items():
                recent_metrics = [m for m in history if m.timestamp >= cutoff_time]
                if not recent_metrics:
                    continue
                
                latencies = [m.latency for m in recent_metrics]
                costs = [m.cost_per_request for m in recent_metrics]
                
                summary[model_name] = {
                    "total_requests": len(recent_metrics),
                    "avg_latency": statistics.mean(latencies),
                    "p95_latency": statistics.quantiles(latencies, n=20)[-1],
                    "avg_cost": statistics.mean(costs),
                    "total_cost": sum(costs),
                    "error_rate": sum(1 for m in recent_metrics if m.error_rate > 0) / len(recent_metrics),
                    "success_rate": sum(1 for m in recent_metrics if m.success_rate > 0) / len(recent_metrics)
                }
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {str(e)}")
        
        return summary 