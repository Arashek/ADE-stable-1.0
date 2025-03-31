from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path
import yaml
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

from .monitor import ResourceMonitor, ResourceMetrics, ResourcePrediction
from .optimizer import ResourceOptimizer, OptimizationAction

logger = logging.getLogger(__name__)

@dataclass
class ResourceAnalytics:
    """Resource usage analytics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_usage: float
    gpu_usage: Optional[float]
    cost: float
    efficiency_score: float

class ResourceAnalyticsManager:
    """Manager for resource usage analytics and reporting"""
    
    def __init__(self, monitor: ResourceMonitor, optimizer: ResourceOptimizer):
        self.monitor = monitor
        self.optimizer = optimizer
        self._load_config()
        self._setup_analytics()
        self.analytics_history = defaultdict(list)
        
    def _load_config(self) -> None:
        """Load analytics configuration"""
        try:
            config_path = Path("src/core/resources/config/monitoring.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    self.config = yaml.safe_load(f)
            else:
                logger.warning("Analytics configuration not found")
                self.config = {}
                
        except Exception as e:
            logger.error(f"Error loading analytics configuration: {str(e)}")
            self.config = {}
            
    def _setup_analytics(self) -> None:
        """Setup analytics parameters"""
        try:
            # Initialize analytics settings
            self.analytics_settings = self.config.get("analytics", {
                "enabled": True,
                "metrics": [
                    "cpu_usage",
                    "memory_usage",
                    "disk_usage",
                    "network_usage",
                    "gpu_usage"
                ],
                "aggregation": [
                    "hourly",
                    "daily",
                    "weekly"
                ],
                "retention": {
                    "hourly": 24,
                    "daily": 30,
                    "weekly": 12
                }
            })
            
            # Initialize visualization settings
            self.viz_settings = {
                "style": "seaborn",
                "figsize": (12, 6),
                "dpi": 100
            }
            
        except Exception as e:
            logger.error(f"Error setting up analytics: {str(e)}")
            
    async def generate_analytics(self) -> ResourceAnalytics:
        """Generate current resource analytics"""
        try:
            # Get current metrics
            metrics = await self.monitor.get_current_metrics()
            if not metrics:
                return None
                
            # Get optimization actions
            actions = await self.optimizer.get_optimization_history()
            
            # Calculate resource usage
            cpu_usage = metrics.cpu_percent
            memory_usage = metrics.memory_percent
            disk_usage = metrics.disk_percent
            network_usage = sum(metrics.network_io) / (1024 * 1024)  # Convert to MB
            gpu_usage = metrics.gpu_percent if metrics.gpu_percent is not None else None
            
            # Calculate cost
            cost = self._calculate_cost(actions)
            
            # Calculate efficiency score
            efficiency_score = self._calculate_efficiency_score(metrics, actions)
            
            analytics = ResourceAnalytics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_usage=network_usage,
                gpu_usage=gpu_usage,
                cost=cost,
                efficiency_score=efficiency_score
            )
            
            # Store analytics
            self._store_analytics(analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            return None
            
    def _calculate_cost(self, actions: List[OptimizationAction]) -> float:
        """Calculate resource cost"""
        try:
            cost = 0.0
            
            # Calculate scaling costs
            for action in actions:
                if action.action_type == "scale_up":
                    # Add cost based on resource type and target value
                    if action.resource_type == "cpu":
                        cost += action.target_value * 0.1  # Example cost per CPU unit
                    elif action.resource_type == "memory":
                        cost += action.target_value * 0.05  # Example cost per memory unit
                    elif action.resource_type == "disk":
                        cost += action.target_value * 0.02  # Example cost per disk unit
                        
            return cost
            
        except Exception as e:
            logger.error(f"Error calculating cost: {str(e)}")
            return 0.0
            
    def _calculate_efficiency_score(self, metrics: ResourceMetrics, actions: List[OptimizationAction]) -> float:
        """Calculate resource efficiency score"""
        try:
            # Calculate individual scores
            cpu_score = 1 - (metrics.cpu_percent / 100)
            memory_score = 1 - (metrics.memory_percent / 100)
            disk_score = 1 - (metrics.disk_percent / 100)
            
            # Calculate network efficiency
            network_total = sum(metrics.network_io)
            network_score = 1 - (network_total / (1024 * 1024 * 1024))  # Normalize to GB
            
            # Calculate action efficiency
            action_score = 1 - (len(actions) / 100)  # Normalize number of actions
            
            # Calculate weighted average
            weights = [0.3, 0.3, 0.2, 0.1, 0.1]  # Weights for different components
            scores = [cpu_score, memory_score, disk_score, network_score, action_score]
            
            efficiency_score = sum(w * s for w, s in zip(weights, scores))
            
            # Normalize to [0, 1]
            efficiency_score = max(min(efficiency_score, 1), 0)
            
            return efficiency_score
            
        except Exception as e:
            logger.error(f"Error calculating efficiency score: {str(e)}")
            return 0.0
            
    def _store_analytics(self, analytics: ResourceAnalytics) -> None:
        """Store analytics data"""
        try:
            # Store in memory
            self.analytics_history["timestamp"].append(analytics.timestamp)
            self.analytics_history["cpu_usage"].append(analytics.cpu_usage)
            self.analytics_history["memory_usage"].append(analytics.memory_usage)
            self.analytics_history["disk_usage"].append(analytics.disk_usage)
            self.analytics_history["network_usage"].append(analytics.network_usage)
            self.analytics_history["gpu_usage"].append(analytics.gpu_usage)
            self.analytics_history["cost"].append(analytics.cost)
            self.analytics_history["efficiency_score"].append(analytics.efficiency_score)
            
            # Apply retention policies
            self._apply_retention_policies()
            
        except Exception as e:
            logger.error(f"Error storing analytics: {str(e)}")
            
    def _apply_retention_policies(self) -> None:
        """Apply data retention policies"""
        try:
            current_time = datetime.now()
            
            # Apply hourly retention
            hourly_data = self._filter_data_by_timeframe(
                current_time - timedelta(hours=self.analytics_settings["retention"]["hourly"])
            )
            
            # Apply daily retention
            daily_data = self._filter_data_by_timeframe(
                current_time - timedelta(days=self.analytics_settings["retention"]["daily"])
            )
            
            # Apply weekly retention
            weekly_data = self._filter_data_by_timeframe(
                current_time - timedelta(weeks=self.analytics_settings["retention"]["weekly"])
            )
            
            # Update analytics history
            self.analytics_history = {
                "hourly": hourly_data,
                "daily": daily_data,
                "weekly": weekly_data
            }
            
        except Exception as e:
            logger.error(f"Error applying retention policies: {str(e)}")
            
    def _filter_data_by_timeframe(self, cutoff_time: datetime) -> Dict[str, List]:
        """Filter data by timeframe"""
        try:
            filtered_data = defaultdict(list)
            
            for i, timestamp in enumerate(self.analytics_history["timestamp"]):
                if timestamp >= cutoff_time:
                    for key in self.analytics_history:
                        filtered_data[key].append(self.analytics_history[key][i])
                        
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error filtering data by timeframe: {str(e)}")
            return defaultdict(list)
            
    async def generate_report(self, timeframe: str = "daily") -> Dict:
        """Generate resource usage report"""
        try:
            # Get data for timeframe
            data = self.analytics_history.get(timeframe, {})
            if not data:
                return None
                
            # Calculate statistics
            stats = {
                "cpu": {
                    "mean": np.mean(data["cpu_usage"]),
                    "std": np.std(data["cpu_usage"]),
                    "max": np.max(data["cpu_usage"]),
                    "min": np.min(data["cpu_usage"])
                },
                "memory": {
                    "mean": np.mean(data["memory_usage"]),
                    "std": np.std(data["memory_usage"]),
                    "max": np.max(data["memory_usage"]),
                    "min": np.min(data["memory_usage"])
                },
                "disk": {
                    "mean": np.mean(data["disk_usage"]),
                    "std": np.std(data["disk_usage"]),
                    "max": np.max(data["disk_usage"]),
                    "min": np.min(data["disk_usage"])
                },
                "network": {
                    "mean": np.mean(data["network_usage"]),
                    "std": np.std(data["network_usage"]),
                    "max": np.max(data["network_usage"]),
                    "min": np.min(data["network_usage"])
                },
                "cost": {
                    "total": np.sum(data["cost"]),
                    "mean": np.mean(data["cost"]),
                    "max": np.max(data["cost"])
                },
                "efficiency": {
                    "mean": np.mean(data["efficiency_score"]),
                    "min": np.min(data["efficiency_score"])
                }
            }
            
            return {
                "timeframe": timeframe,
                "timestamp": datetime.now().isoformat(),
                "statistics": stats
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return None
            
    async def generate_visualizations(self, output_dir: str) -> None:
        """Generate resource usage visualizations"""
        try:
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Set visualization style
            plt.style.use(self.viz_settings["style"])
            
            # Generate CPU usage plot
            self._plot_resource_usage(
                "CPU Usage",
                self.analytics_history["cpu_usage"],
                self.analytics_history["timestamp"],
                output_path / "cpu_usage.png"
            )
            
            # Generate memory usage plot
            self._plot_resource_usage(
                "Memory Usage",
                self.analytics_history["memory_usage"],
                self.analytics_history["timestamp"],
                output_path / "memory_usage.png"
            )
            
            # Generate disk usage plot
            self._plot_resource_usage(
                "Disk Usage",
                self.analytics_history["disk_usage"],
                self.analytics_history["timestamp"],
                output_path / "disk_usage.png"
            )
            
            # Generate network usage plot
            self._plot_resource_usage(
                "Network Usage",
                self.analytics_history["network_usage"],
                self.analytics_history["timestamp"],
                output_path / "network_usage.png"
            )
            
            # Generate cost plot
            self._plot_resource_usage(
                "Resource Cost",
                self.analytics_history["cost"],
                self.analytics_history["timestamp"],
                output_path / "resource_cost.png"
            )
            
            # Generate efficiency score plot
            self._plot_resource_usage(
                "Efficiency Score",
                self.analytics_history["efficiency_score"],
                self.analytics_history["timestamp"],
                output_path / "efficiency_score.png"
            )
            
            # Generate correlation heatmap
            self._plot_correlation_heatmap(output_path / "correlation_heatmap.png")
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            
    def _plot_resource_usage(self, title: str, values: List[float], timestamps: List[datetime], output_path: Path) -> None:
        """Plot resource usage over time"""
        try:
            plt.figure(figsize=self.viz_settings["figsize"], dpi=self.viz_settings["dpi"])
            plt.plot(timestamps, values)
            plt.title(title)
            plt.xlabel("Time")
            plt.ylabel("Usage")
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            
        except Exception as e:
            logger.error(f"Error plotting resource usage: {str(e)}")
            
    def _plot_correlation_heatmap(self, output_path: Path) -> None:
        """Plot correlation heatmap of resource metrics"""
        try:
            # Create DataFrame
            df = pd.DataFrame({
                "cpu": self.analytics_history["cpu_usage"],
                "memory": self.analytics_history["memory_usage"],
                "disk": self.analytics_history["disk_usage"],
                "network": self.analytics_history["network_usage"],
                "cost": self.analytics_history["cost"],
                "efficiency": self.analytics_history["efficiency_score"]
            })
            
            # Calculate correlation matrix
            corr_matrix = df.corr()
            
            # Create heatmap
            plt.figure(figsize=self.viz_settings["figsize"], dpi=self.viz_settings["dpi"])
            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", center=0)
            plt.title("Resource Metrics Correlation")
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            
        except Exception as e:
            logger.error(f"Error plotting correlation heatmap: {str(e)}")
            
    async def export_analytics(self, filepath: str) -> None:
        """Export analytics data to file"""
        try:
            analytics_data = {
                "timestamp": datetime.now().isoformat(),
                "hourly": {
                    k: v for k, v in self.analytics_history["hourly"].items()
                },
                "daily": {
                    k: v for k, v in self.analytics_history["daily"].items()
                },
                "weekly": {
                    k: v for k, v in self.analytics_history["weekly"].items()
                }
            }
            
            with open(filepath, "w") as f:
                json.dump(analytics_data, f, indent=2)
                
            logger.info(f"Analytics data exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Error exporting analytics data: {str(e)}") 