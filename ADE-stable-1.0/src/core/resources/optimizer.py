from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import asyncio
import psutil
import time
from datetime import datetime
import yaml
from pathlib import Path
import json
import numpy as np
from collections import deque

from .monitor import ResourceMonitor, ResourceMetrics, ResourcePrediction

logger = logging.getLogger(__name__)

@dataclass
class OptimizationAction:
    """Resource optimization action"""
    action_type: str
    resource_type: str
    target_value: float
    priority: str
    timestamp: datetime
    reason: str

class ResourceOptimizer:
    """Optimize resource usage and handle dynamic scaling"""
    
    def __init__(self, monitor: ResourceMonitor):
        self.monitor = monitor
        self._load_config()
        self._setup_optimization()
        self.action_history = deque(maxlen=1000)
        self._optimization_task = None
        self._stop_optimization = False
        
    def _load_config(self) -> None:
        """Load optimization configuration"""
        try:
            config_path = Path("src/core/resources/config/monitoring.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    self.config = yaml.safe_load(f)
            else:
                logger.warning("Optimization configuration not found")
                self.config = {}
                
        except Exception as e:
            logger.error(f"Error loading optimization configuration: {str(e)}")
            self.config = {}
            
    def _setup_optimization(self) -> None:
        """Setup optimization parameters"""
        try:
            # Initialize optimization settings
            self.optimization_settings = self.config.get("optimization", {
                "batch_size": 100,
                "max_workers": 4,
                "cache_size": 1000,
                "compression": True
            })
            
            # Initialize cost optimization settings
            self.cost_settings = self.config.get("cost_optimization", {
                "enabled": True,
                "llm": {
                    "max_tokens_per_request": 1000,
                    "max_requests_per_minute": 60,
                    "cost_threshold": 100
                },
                "cloud": {
                    "max_instances": 3,
                    "auto_scale": True,
                    "scale_up_threshold": 80,
                    "scale_down_threshold": 20
                }
            })
            
            # Initialize resource allocation settings
            self.allocation_settings = self.config.get("allocation", {
                "strategy": "dynamic",
                "priorities": {
                    "high": {"cpu": 50, "memory": 50, "disk": 50},
                    "medium": {"cpu": 30, "memory": 30, "disk": 30},
                    "low": {"cpu": 20, "memory": 20, "disk": 20}
                }
            })
            
        except Exception as e:
            logger.error(f"Error setting up optimization: {str(e)}")
            
    async def start_optimization(self) -> None:
        """Start resource optimization"""
        try:
            self._optimization_task = asyncio.create_task(self._optimize_resources())
            logger.info("Resource optimization started")
            
        except Exception as e:
            logger.error(f"Error starting optimization: {str(e)}")
            
    async def stop_optimization(self) -> None:
        """Stop resource optimization"""
        try:
            self._stop_optimization = True
            if self._optimization_task:
                await self._optimization_task
            logger.info("Resource optimization stopped")
            
        except Exception as e:
            logger.error(f"Error stopping optimization: {str(e)}")
            
    async def _optimize_resources(self) -> None:
        """Main optimization loop"""
        while not self._stop_optimization:
            try:
                # Get current metrics and predictions
                metrics = await self.monitor.get_current_metrics()
                predictions = await self.monitor.get_predictions()
                
                if metrics and predictions:
                    # Generate optimization actions
                    actions = self._generate_optimization_actions(metrics, predictions)
                    
                    # Execute optimization actions
                    for action in actions:
                        await self._execute_optimization_action(action)
                        
                # Sleep for optimization interval
                await asyncio.sleep(60)  # Adjust based on configuration
                
            except Exception as e:
                logger.error(f"Error in optimization loop: {str(e)}")
                await asyncio.sleep(60)
                
    def _generate_optimization_actions(self, metrics: ResourceMetrics, predictions: ResourcePrediction) -> List[OptimizationAction]:
        """Generate optimization actions based on metrics and predictions"""
        actions = []
        
        try:
            # Check CPU usage
            if metrics.cpu_percent > self.cost_settings["cloud"]["scale_up_threshold"]:
                actions.append(OptimizationAction(
                    action_type="scale_up",
                    resource_type="cpu",
                    target_value=self.cost_settings["cloud"]["scale_up_threshold"],
                    priority="high",
                    timestamp=datetime.now(),
                    reason=f"High CPU usage: {metrics.cpu_percent}%"
                ))
            elif metrics.cpu_percent < self.cost_settings["cloud"]["scale_down_threshold"]:
                actions.append(OptimizationAction(
                    action_type="scale_down",
                    resource_type="cpu",
                    target_value=self.cost_settings["cloud"]["scale_down_threshold"],
                    priority="low",
                    timestamp=datetime.now(),
                    reason=f"Low CPU usage: {metrics.cpu_percent}%"
                ))
                
            # Check memory usage
            if metrics.memory_percent > self.cost_settings["cloud"]["scale_up_threshold"]:
                actions.append(OptimizationAction(
                    action_type="scale_up",
                    resource_type="memory",
                    target_value=self.cost_settings["cloud"]["scale_up_threshold"],
                    priority="high",
                    timestamp=datetime.now(),
                    reason=f"High memory usage: {metrics.memory_percent}%"
                ))
            elif metrics.memory_percent < self.cost_settings["cloud"]["scale_down_threshold"]:
                actions.append(OptimizationAction(
                    action_type="scale_down",
                    resource_type="memory",
                    target_value=self.cost_settings["cloud"]["scale_down_threshold"],
                    priority="low",
                    timestamp=datetime.now(),
                    reason=f"Low memory usage: {metrics.memory_percent}%"
                ))
                
            # Check disk usage
            if metrics.disk_percent > self.cost_settings["cloud"]["scale_up_threshold"]:
                actions.append(OptimizationAction(
                    action_type="scale_up",
                    resource_type="disk",
                    target_value=self.cost_settings["cloud"]["scale_up_threshold"],
                    priority="high",
                    timestamp=datetime.now(),
                    reason=f"High disk usage: {metrics.disk_percent}%"
                ))
                
            # Check predictions for proactive scaling
            if predictions.confidence > 0.8:
                if predictions.cpu_prediction > self.cost_settings["cloud"]["scale_up_threshold"]:
                    actions.append(OptimizationAction(
                        action_type="scale_up",
                        resource_type="cpu",
                        target_value=self.cost_settings["cloud"]["scale_up_threshold"],
                        priority="medium",
                        timestamp=datetime.now(),
                        reason=f"Predicted high CPU usage: {predictions.cpu_prediction}%"
                    ))
                    
                if predictions.memory_prediction > self.cost_settings["cloud"]["scale_up_threshold"]:
                    actions.append(OptimizationAction(
                        action_type="scale_up",
                        resource_type="memory",
                        target_value=self.cost_settings["cloud"]["scale_up_threshold"],
                        priority="medium",
                        timestamp=datetime.now(),
                        reason=f"Predicted high memory usage: {predictions.memory_prediction}%"
                    ))
                    
        except Exception as e:
            logger.error(f"Error generating optimization actions: {str(e)}")
            
        return actions
        
    async def _execute_optimization_action(self, action: OptimizationAction) -> None:
        """Execute an optimization action"""
        try:
            # Log the action
            logger.info(f"Executing optimization action: {action.action_type} for {action.resource_type}")
            
            # Record action in history
            self.action_history.append(action)
            
            # Execute the action based on type
            if action.action_type == "scale_up":
                await self._scale_up_resource(action)
            elif action.action_type == "scale_down":
                await self._scale_down_resource(action)
                
        except Exception as e:
            logger.error(f"Error executing optimization action: {str(e)}")
            
    async def _scale_up_resource(self, action: OptimizationAction) -> None:
        """Scale up a resource"""
        try:
            if action.resource_type == "cpu":
                # Implement CPU scaling logic
                pass
            elif action.resource_type == "memory":
                # Implement memory scaling logic
                pass
            elif action.resource_type == "disk":
                # Implement disk scaling logic
                pass
                
        except Exception as e:
            logger.error(f"Error scaling up resource: {str(e)}")
            
    async def _scale_down_resource(self, action: OptimizationAction) -> None:
        """Scale down a resource"""
        try:
            if action.resource_type == "cpu":
                # Implement CPU scaling logic
                pass
            elif action.resource_type == "memory":
                # Implement memory scaling logic
                pass
            elif action.resource_type == "disk":
                # Implement disk scaling logic
                pass
                
        except Exception as e:
            logger.error(f"Error scaling down resource: {str(e)}")
            
    async def optimize_llm_usage(self, token_count: int, cost_per_token: float) -> bool:
        """Optimize LLM usage based on cost"""
        try:
            # Check if cost optimization is enabled
            if not self.cost_settings["enabled"]:
                return True
                
            # Calculate estimated cost
            estimated_cost = token_count * cost_per_token
            
            # Check against daily threshold
            if estimated_cost > self.cost_settings["llm"]["cost_threshold"]:
                logger.warning(f"LLM usage would exceed cost threshold: {estimated_cost:.2f} USD")
                return False
                
            # Check rate limits
            if token_count > self.cost_settings["llm"]["max_tokens_per_request"]:
                logger.warning(f"Token count exceeds maximum: {token_count}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing LLM usage: {str(e)}")
            return False
            
    async def get_optimization_history(self, limit: Optional[int] = None) -> List[OptimizationAction]:
        """Get optimization action history"""
        if limit:
            return list(self.action_history)[-limit:]
        return list(self.action_history)
        
    async def export_optimization_data(self, filepath: str) -> None:
        """Export optimization data to file"""
        try:
            optimization_data = {
                "actions": [
                    {
                        "action_type": a.action_type,
                        "resource_type": a.resource_type,
                        "target_value": a.target_value,
                        "priority": a.priority,
                        "timestamp": a.timestamp.isoformat(),
                        "reason": a.reason
                    }
                    for a in self.action_history
                ]
            }
            
            with open(filepath, "w") as f:
                json.dump(optimization_data, f, indent=2)
                
            logger.info(f"Optimization data exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Error exporting optimization data: {str(e)}") 