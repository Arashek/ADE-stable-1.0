from typing import Dict, List, Optional, Tuple
import logging
import asyncio
from datetime import datetime
import json
from pathlib import Path
import yaml
from collections import defaultdict

from .monitor import ResourceMonitor, ResourceMetrics, ResourcePrediction
from .optimizer import ResourceOptimizer, OptimizationAction
from .analytics import ResourceAnalyticsManager, ResourceAnalytics

logger = logging.getLogger(__name__)

class ResourceManager:
    """Manager for coordinating resource monitoring, optimization, and analytics"""
    
    def __init__(self):
        self.monitor = ResourceMonitor()
        self.optimizer = ResourceOptimizer(self.monitor)
        self.analytics = ResourceAnalyticsManager(self.monitor, self.optimizer)
        self._load_config()
        self._setup_manager()
        self._manager_task = None
        self._stop_manager = False
        self.resource_stats = defaultdict(dict)
        
    def _load_config(self) -> None:
        """Load manager configuration"""
        try:
            config_path = Path("src/core/resources/config/monitoring.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    self.config = yaml.safe_load(f)
            else:
                logger.warning("Manager configuration not found")
                self.config = {}
                
        except Exception as e:
            logger.error(f"Error loading manager configuration: {str(e)}")
            self.config = {}
            
    def _setup_manager(self) -> None:
        """Setup manager parameters"""
        try:
            # Initialize manager settings
            self.manager_settings = self.config.get("manager", {
                "enabled": True,
                "update_interval": 60,  # seconds
                "export_interval": 3600,  # seconds
                "max_history": 1000,
                "auto_optimize": True,
                "auto_export": True
            })
            
            # Initialize resource policies
            self.resource_policies = self.config.get("resource_policies", {
                "cpu": {
                    "min_cores": 1,
                    "max_cores": 8,
                    "scale_factor": 1.5
                },
                "memory": {
                    "min_gb": 2,
                    "max_gb": 32,
                    "scale_factor": 1.5
                },
                "disk": {
                    "min_gb": 10,
                    "max_gb": 500,
                    "scale_factor": 1.5
                }
            })
            
        except Exception as e:
            logger.error(f"Error setting up manager: {str(e)}")
            
    async def start(self) -> None:
        """Start resource management"""
        try:
            # Start monitoring
            await self.monitor.start_monitoring()
            
            # Start optimization
            await self.optimizer.start_optimization()
            
            # Start manager task
            self._manager_task = asyncio.create_task(self._manage_resources())
            logger.info("Resource management started")
            
        except Exception as e:
            logger.error(f"Error starting resource management: {str(e)}")
            
    async def stop(self) -> None:
        """Stop resource management"""
        try:
            # Stop manager task
            self._stop_manager = True
            if self._manager_task:
                await self._manager_task
                
            # Stop optimization
            await self.optimizer.stop_optimization()
            
            # Stop monitoring
            await self.monitor.stop_monitoring()
            
            logger.info("Resource management stopped")
            
        except Exception as e:
            logger.error(f"Error stopping resource management: {str(e)}")
            
    async def _manage_resources(self) -> None:
        """Main resource management loop"""
        while not self._stop_manager:
            try:
                # Get current metrics and predictions
                metrics = await self.monitor.get_current_metrics()
                predictions = await self.monitor.get_predictions()
                
                if metrics and predictions:
                    # Update resource statistics
                    self._update_resource_stats(metrics, predictions)
                    
                    # Generate analytics
                    analytics = await self.analytics.generate_analytics()
                    
                    if analytics:
                        # Check for resource constraints
                        constraints = self._check_resource_constraints(analytics)
                        
                        if constraints:
                            # Generate optimization actions
                            actions = self._generate_optimization_actions(analytics, constraints)
                            
                            # Execute optimization actions
                            for action in actions:
                                await self.optimizer._execute_optimization_action(action)
                                
                        # Export data if enabled
                        if self.manager_settings["auto_export"]:
                            await self._export_data()
                            
                # Sleep for update interval
                await asyncio.sleep(self.manager_settings["update_interval"])
                
            except Exception as e:
                logger.error(f"Error in resource management loop: {str(e)}")
                await asyncio.sleep(self.manager_settings["update_interval"])
                
    def _update_resource_stats(self, metrics: ResourceMetrics, predictions: ResourcePrediction) -> None:
        """Update resource statistics"""
        try:
            # Update current metrics
            self.resource_stats["current"] = {
                "cpu": metrics.cpu_percent,
                "memory": metrics.memory_percent,
                "disk": metrics.disk_percent,
                "network": sum(metrics.network_io),
                "gpu": metrics.gpu_percent,
                "gpu_memory": metrics.gpu_memory_percent
            }
            
            # Update predictions
            self.resource_stats["predictions"] = {
                "cpu": predictions.cpu_prediction,
                "memory": predictions.memory_prediction,
                "disk": predictions.disk_prediction,
                "network": sum(predictions.network_prediction),
                "confidence": predictions.confidence
            }
            
            # Update historical data
            self.resource_stats["history"] = {
                "timestamps": [m.timestamp for m in self.monitor.metrics_history],
                "cpu": [m.cpu_percent for m in self.monitor.metrics_history],
                "memory": [m.memory_percent for m in self.monitor.metrics_history],
                "disk": [m.disk_percent for m in self.monitor.metrics_history],
                "network": [sum(m.network_io) for m in self.monitor.metrics_history]
            }
            
        except Exception as e:
            logger.error(f"Error updating resource stats: {str(e)}")
            
    def _check_resource_constraints(self, analytics: ResourceAnalytics) -> List[str]:
        """Check for resource constraints"""
        constraints = []
        
        try:
            # Check CPU constraints
            if analytics.cpu_usage > self.resource_policies["cpu"]["max_cores"] * 100:
                constraints.append("cpu_overload")
            elif analytics.cpu_usage < self.resource_policies["cpu"]["min_cores"] * 100:
                constraints.append("cpu_underutilized")
                
            # Check memory constraints
            if analytics.memory_usage > self.resource_policies["memory"]["max_gb"] * 100:
                constraints.append("memory_overload")
            elif analytics.memory_usage < self.resource_policies["memory"]["min_gb"] * 100:
                constraints.append("memory_underutilized")
                
            # Check disk constraints
            if analytics.disk_usage > self.resource_policies["disk"]["max_gb"] * 100:
                constraints.append("disk_overload")
            elif analytics.disk_usage < self.resource_policies["disk"]["min_gb"] * 100:
                constraints.append("disk_underutilized")
                
            # Check efficiency constraints
            if analytics.efficiency_score < 0.5:
                constraints.append("low_efficiency")
                
        except Exception as e:
            logger.error(f"Error checking resource constraints: {str(e)}")
            
        return constraints
        
    def _generate_optimization_actions(self, analytics: ResourceAnalytics, constraints: List[str]) -> List[OptimizationAction]:
        """Generate optimization actions based on constraints"""
        actions = []
        
        try:
            for constraint in constraints:
                if constraint == "cpu_overload":
                    actions.append(OptimizationAction(
                        action_type="scale_up",
                        resource_type="cpu",
                        target_value=self.resource_policies["cpu"]["scale_factor"] * analytics.cpu_usage,
                        priority="high",
                        timestamp=datetime.now(),
                        reason="CPU overload detected"
                    ))
                elif constraint == "cpu_underutilized":
                    actions.append(OptimizationAction(
                        action_type="scale_down",
                        resource_type="cpu",
                        target_value=self.resource_policies["cpu"]["min_cores"] * 100,
                        priority="low",
                        timestamp=datetime.now(),
                        reason="CPU underutilized"
                    ))
                    
                elif constraint == "memory_overload":
                    actions.append(OptimizationAction(
                        action_type="scale_up",
                        resource_type="memory",
                        target_value=self.resource_policies["memory"]["scale_factor"] * analytics.memory_usage,
                        priority="high",
                        timestamp=datetime.now(),
                        reason="Memory overload detected"
                    ))
                elif constraint == "memory_underutilized":
                    actions.append(OptimizationAction(
                        action_type="scale_down",
                        resource_type="memory",
                        target_value=self.resource_policies["memory"]["min_gb"] * 100,
                        priority="low",
                        timestamp=datetime.now(),
                        reason="Memory underutilized"
                    ))
                    
                elif constraint == "disk_overload":
                    actions.append(OptimizationAction(
                        action_type="scale_up",
                        resource_type="disk",
                        target_value=self.resource_policies["disk"]["scale_factor"] * analytics.disk_usage,
                        priority="high",
                        timestamp=datetime.now(),
                        reason="Disk overload detected"
                    ))
                elif constraint == "disk_underutilized":
                    actions.append(OptimizationAction(
                        action_type="scale_down",
                        resource_type="disk",
                        target_value=self.resource_policies["disk"]["min_gb"] * 100,
                        priority="low",
                        timestamp=datetime.now(),
                        reason="Disk underutilized"
                    ))
                    
                elif constraint == "low_efficiency":
                    # Generate efficiency optimization actions
                    actions.extend(self._generate_efficiency_actions(analytics))
                    
        except Exception as e:
            logger.error(f"Error generating optimization actions: {str(e)}")
            
        return actions
        
    def _generate_efficiency_actions(self, analytics: ResourceAnalytics) -> List[OptimizationAction]:
        """Generate actions to improve resource efficiency"""
        actions = []
        
        try:
            # Identify least efficient resource
            resource_scores = {
                "cpu": analytics.cpu_usage / 100,
                "memory": analytics.memory_usage / 100,
                "disk": analytics.disk_usage / 100,
                "network": analytics.network_usage / (1024 * 1024 * 1024)  # Normalize to GB
            }
            
            least_efficient = max(resource_scores.items(), key=lambda x: x[1])
            
            # Generate optimization action for least efficient resource
            if least_efficient[1] > 0.8:  # If usage is above 80%
                actions.append(OptimizationAction(
                    action_type="optimize",
                    resource_type=least_efficient[0],
                    target_value=least_efficient[1] * 0.8,  # Target 80% of current usage
                    priority="medium",
                    timestamp=datetime.now(),
                    reason=f"Optimizing {least_efficient[0]} for better efficiency"
                ))
                
        except Exception as e:
            logger.error(f"Error generating efficiency actions: {str(e)}")
            
        return actions
        
    async def _export_data(self) -> None:
        """Export resource management data"""
        try:
            # Create export directory
            export_dir = Path("exports/resources")
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Export metrics
            await self.monitor.export_metrics(export_dir / "metrics.json")
            
            # Export optimization data
            await self.optimizer.export_optimization_data(export_dir / "optimization.json")
            
            # Export analytics
            await self.analytics.export_analytics(export_dir / "analytics.json")
            
            # Export resource stats
            with open(export_dir / "resource_stats.json", "w") as f:
                json.dump(self.resource_stats, f, indent=2, default=str)
                
            # Generate visualizations
            await self.analytics.generate_visualizations(str(export_dir / "visualizations"))
            
            logger.info("Resource data exported successfully")
            
        except Exception as e:
            logger.error(f"Error exporting resource data: {str(e)}")
            
    async def get_resource_status(self) -> Dict:
        """Get current resource status"""
        try:
            return {
                "current": self.resource_stats.get("current", {}),
                "predictions": self.resource_stats.get("predictions", {}),
                "constraints": self._check_resource_constraints(
                    await self.analytics.generate_analytics()
                ) if self.analytics else [],
                "efficiency": self.resource_stats.get("efficiency", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error getting resource status: {str(e)}")
            return {}
            
    async def get_resource_history(self, timeframe: str = "daily") -> Dict:
        """Get resource usage history"""
        try:
            return {
                "timestamps": self.resource_stats.get("history", {}).get("timestamps", []),
                "metrics": {
                    "cpu": self.resource_stats.get("history", {}).get("cpu", []),
                    "memory": self.resource_stats.get("history", {}).get("memory", []),
                    "disk": self.resource_stats.get("history", {}).get("disk", []),
                    "network": self.resource_stats.get("history", {}).get("network", [])
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting resource history: {str(e)}")
            return {} 