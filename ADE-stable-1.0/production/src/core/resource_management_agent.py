import logging
import threading
import time
import psutil
import GPUtil
from typing import Dict, Any, Optional, List
from datetime import datetime
from .agent import Agent
from .agent_communication import Message, MessageType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ResourceMetrics:
    """Represents resource usage metrics."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)

class ResourceManagementAgent(Agent):
    """Agent specialized in managing system resources."""
    
    def __init__(self, agent_id: str = "resource_manager", 
                 name: str = "Resource Management Agent",
                 config_path: Optional[str] = None):
        """Initialize the resource management agent."""
        super().__init__(
            agent_id=agent_id,
            name=name,
            capabilities=[
                "resource_monitoring",
                "resource_allocation",
                "performance_optimization",
                "load_balancing",
                "resource_prediction",
                "resource_cleanup"
            ],
            config_path=config_path
        )
        
        # Initialize resource metrics
        self.resource_metrics: Dict[str, ResourceMetrics] = {}
        self.resource_thresholds = {
            "cpu": 80.0,  # CPU usage threshold (%)
            "memory": 85.0,  # Memory usage threshold (%)
            "disk": 90.0,  # Disk usage threshold (%)
            "network": 1000.0  # Network I/O threshold (MB/s)
        }
        
        # Resource allocation tracking
        self.allocations: Dict[str, Dict[str, Any]] = {}
        
        # Performance optimization settings
        self.optimization_settings = {
            "auto_scale": True,
            "load_balance": True,
            "cleanup_threshold": 70.0  # Cleanup when resource usage exceeds this %
        }

    def _process_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """Process a resource management task."""
        try:
            task_type = task_data.get("task_type")
            
            if task_type == "monitor_resources":
                self._monitor_resources(task_data.get("target_agent"))
            elif task_type == "allocate_resources":
                self._allocate_resources(
                    task_data.get("target_agent"),
                    task_data.get("resource_requirements")
                )
            elif task_type == "optimize_resources":
                self._optimize_resources(task_data.get("target_agent"))
            elif task_type == "predict_resources":
                self._predict_resource_usage(task_data.get("target_agent"))
            elif task_type == "cleanup_resources":
                self._cleanup_resources(task_data.get("target_agent"))
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.complete_task(task_id, True, {"status": "completed"})
            
        except Exception as e:
            self._handle_error(e, task_id)
            self.complete_task(task_id, False, {"error": str(e)})

    def _monitor_resources(self, target_agent: Optional[str] = None) -> None:
        """Monitor system resources."""
        try:
            # Get system-wide metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            metrics = ResourceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                network_io={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv
                }
            )
            
            # Store metrics
            self.resource_metrics[target_agent or "system"] = metrics
            
            # Check thresholds
            self._check_resource_thresholds(metrics)
            
            # Broadcast resource status
            self._broadcast_resource_status(target_agent, metrics)
            
        except Exception as e:
            self._handle_error(e, "resource_monitoring")

    def _allocate_resources(self, target_agent: str, 
                          requirements: Dict[str, Any]) -> None:
        """Allocate resources for a task."""
        try:
            # Check resource availability
            if not self._check_resource_availability(requirements):
                raise ValueError("Insufficient resources available")
            
            # Record allocation
            self.allocations[target_agent] = {
                "requirements": requirements,
                "timestamp": datetime.now(),
                "status": "active"
            }
            
            # Broadcast allocation
            self._broadcast_allocation(target_agent, requirements)
            
        except Exception as e:
            self._handle_error(e, "resource_allocation")

    def _optimize_resources(self, target_agent: str) -> None:
        """Optimize resource allocation."""
        try:
            if target_agent not in self.resource_metrics:
                raise ValueError(f"No metrics available for agent {target_agent}")
            
            metrics = self.resource_metrics[target_agent]
            
            # Analyze resource usage patterns
            recommendations = self._analyze_resource_patterns(metrics)
            
            # Apply optimizations if enabled
            if self.optimization_settings["auto_scale"]:
                self._apply_optimizations(target_agent, recommendations)
            
            # Broadcast optimization results
            self._broadcast_optimization(target_agent, recommendations)
            
        except Exception as e:
            self._handle_error(e, "resource_optimization")

    def _predict_resource_usage(self, target_agent: str) -> None:
        """Predict future resource usage."""
        try:
            if target_agent not in self.resource_metrics:
                raise ValueError(f"No metrics available for agent {target_agent}")
            
            # Analyze historical data
            historical_data = self._get_historical_metrics(target_agent)
            
            # Generate predictions
            predictions = self._generate_predictions(historical_data)
            
            # Broadcast predictions
            self._broadcast_predictions(target_agent, predictions)
            
        except Exception as e:
            self._handle_error(e, "resource_prediction")

    def _cleanup_resources(self, target_agent: str) -> None:
        """Clean up unused resources."""
        try:
            if target_agent not in self.allocations:
                return
            
            # Check if cleanup is needed
            if not self._should_cleanup(target_agent):
                return
            
            # Perform cleanup
            self._perform_cleanup(target_agent)
            
            # Broadcast cleanup status
            self._broadcast_cleanup(target_agent)
            
        except Exception as e:
            self._handle_error(e, "resource_cleanup")

    def _check_resource_thresholds(self, metrics: ResourceMetrics) -> None:
        """Check if resource usage exceeds thresholds."""
        if metrics.cpu_percent > self.resource_thresholds["cpu"]:
            self._handle_threshold_exceeded("cpu", metrics.cpu_percent)
        
        if metrics.memory_percent > self.resource_thresholds["memory"]:
            self._handle_threshold_exceeded("memory", metrics.memory_percent)
        
        if metrics.disk_percent > self.resource_thresholds["disk"]:
            self._handle_threshold_exceeded("disk", metrics.disk_percent)
        
        network_usage = (metrics.network_io["bytes_sent"] + 
                        metrics.network_io["bytes_recv"]) / (1024 * 1024)  # MB/s
        if network_usage > self.resource_thresholds["network"]:
            self._handle_threshold_exceeded("network", network_usage)

    def _handle_threshold_exceeded(self, resource: str, value: float) -> None:
        """Handle resource threshold exceeded."""
        logger.warning(f"Resource {resource} usage ({value}%) exceeded threshold")
        
        # Broadcast warning
        warning_data = {
            "resource": resource,
            "value": value,
            "threshold": self.resource_thresholds[resource],
            "timestamp": datetime.now().isoformat()
        }
        self.comm_system.broadcast_notification(
            self.agent_id,
            {"type": "resource_warning", "data": warning_data}
        )

    def _check_resource_availability(self, requirements: Dict[str, Any]) -> bool:
        """Check if requested resources are available."""
        try:
            metrics = self.resource_metrics.get("system")
            if not metrics:
                return False
            
            # Check CPU availability
            if requirements.get("cpu", 0) > (100 - metrics.cpu_percent):
                return False
            
            # Check memory availability
            if requirements.get("memory", 0) > (100 - metrics.memory_percent):
                return False
            
            # Check disk availability
            if requirements.get("disk", 0) > (100 - metrics.disk_percent):
                return False
            
            return True
            
        except Exception as e:
            self._handle_error(e, "resource_availability_check")
            return False

    def _analyze_resource_patterns(self, metrics: ResourceMetrics) -> Dict[str, Any]:
        """Analyze resource usage patterns."""
        recommendations = {
            "cpu": [],
            "memory": [],
            "disk": [],
            "network": []
        }
        
        # Analyze CPU patterns
        if metrics.cpu_percent > 70:
            recommendations["cpu"].append("Consider scaling down CPU-intensive tasks")
        
        # Analyze memory patterns
        if metrics.memory_percent > 70:
            recommendations["memory"].append("Consider memory cleanup or optimization")
        
        # Analyze disk patterns
        if metrics.disk_percent > 70:
            recommendations["disk"].append("Consider disk cleanup or expansion")
        
        # Analyze network patterns
        network_usage = (metrics.network_io["bytes_sent"] + 
                        metrics.network_io["bytes_recv"]) / (1024 * 1024)
        if network_usage > 800:  # MB/s
            recommendations["network"].append("Consider network optimization")
        
        return recommendations

    def _apply_optimizations(self, target_agent: str, 
                           recommendations: Dict[str, Any]) -> None:
        """Apply resource optimizations."""
        try:
            # Apply CPU optimizations
            if recommendations["cpu"]:
                self._optimize_cpu(target_agent)
            
            # Apply memory optimizations
            if recommendations["memory"]:
                self._optimize_memory(target_agent)
            
            # Apply disk optimizations
            if recommendations["disk"]:
                self._optimize_disk(target_agent)
            
            # Apply network optimizations
            if recommendations["network"]:
                self._optimize_network(target_agent)
            
        except Exception as e:
            self._handle_error(e, "optimization_application")

    def _get_historical_metrics(self, target_agent: str) -> List[ResourceMetrics]:
        """Get historical resource metrics."""
        # This would typically query a database or time-series store
        # For now, return recent metrics
        return [metrics for agent, metrics in self.resource_metrics.items()
                if agent == target_agent]

    def _generate_predictions(self, historical_data: List[ResourceMetrics]) -> Dict[str, Any]:
        """Generate resource usage predictions."""
        if not historical_data:
            return {}
        
        # Simple linear prediction based on recent trend
        latest = historical_data[-1]
        predictions = {
            "cpu": {
                "current": latest.cpu_percent,
                "predicted": min(100, latest.cpu_percent * 1.1)  # 10% increase
            },
            "memory": {
                "current": latest.memory_percent,
                "predicted": min(100, latest.memory_percent * 1.1)
            },
            "disk": {
                "current": latest.disk_percent,
                "predicted": min(100, latest.disk_percent * 1.1)
            }
        }
        
        return predictions

    def _should_cleanup(self, target_agent: str) -> bool:
        """Determine if resource cleanup is needed."""
        if target_agent not in self.resource_metrics:
            return False
        
        metrics = self.resource_metrics[target_agent]
        return any([
            metrics.cpu_percent > self.optimization_settings["cleanup_threshold"],
            metrics.memory_percent > self.optimization_settings["cleanup_threshold"],
            metrics.disk_percent > self.optimization_settings["cleanup_threshold"]
        ])

    def _perform_cleanup(self, target_agent: str) -> None:
        """Perform resource cleanup."""
        try:
            # Clean up memory
            self._cleanup_memory(target_agent)
            
            # Clean up disk
            self._cleanup_disk(target_agent)
            
            # Clean up network connections
            self._cleanup_network(target_agent)
            
            # Update allocation status
            if target_agent in self.allocations:
                self.allocations[target_agent]["status"] = "cleaned"
            
        except Exception as e:
            self._handle_error(e, "resource_cleanup")

    def _cleanup_memory(self, target_agent: str) -> None:
        """Clean up memory resources."""
        # Implementation would depend on the specific memory management strategy
        pass

    def _cleanup_disk(self, target_agent: str) -> None:
        """Clean up disk resources."""
        # Implementation would depend on the specific disk management strategy
        pass

    def _cleanup_network(self, target_agent: str) -> None:
        """Clean up network resources."""
        # Implementation would depend on the specific network management strategy
        pass

    def _optimize_cpu(self, target_agent: str) -> None:
        """Optimize CPU usage."""
        # Implementation would depend on the specific CPU optimization strategy
        pass

    def _optimize_memory(self, target_agent: str) -> None:
        """Optimize memory usage."""
        # Implementation would depend on the specific memory optimization strategy
        pass

    def _optimize_disk(self, target_agent: str) -> None:
        """Optimize disk usage."""
        # Implementation would depend on the specific disk optimization strategy
        pass

    def _optimize_network(self, target_agent: str) -> None:
        """Optimize network usage."""
        # Implementation would depend on the specific network optimization strategy
        pass

    def _broadcast_resource_status(self, target_agent: str, 
                                 metrics: ResourceMetrics) -> None:
        """Broadcast resource status."""
        status_data = {
            "target_agent": target_agent,
            "metrics": {
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "disk_percent": metrics.disk_percent,
                "network_io": metrics.network_io,
                "timestamp": metrics.timestamp.isoformat()
            }
        }
        self.comm_system.broadcast_notification(
            self.agent_id,
            {"type": "resource_status", "data": status_data}
        )

    def _broadcast_allocation(self, target_agent: str, 
                            requirements: Dict[str, Any]) -> None:
        """Broadcast resource allocation."""
        allocation_data = {
            "target_agent": target_agent,
            "requirements": requirements,
            "timestamp": datetime.now().isoformat()
        }
        self.comm_system.broadcast_notification(
            self.agent_id,
            {"type": "resource_allocation", "data": allocation_data}
        )

    def _broadcast_optimization(self, target_agent: str, 
                              recommendations: Dict[str, Any]) -> None:
        """Broadcast optimization recommendations."""
        optimization_data = {
            "target_agent": target_agent,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        self.comm_system.broadcast_notification(
            self.agent_id,
            {"type": "resource_optimization", "data": optimization_data}
        )

    def _broadcast_predictions(self, target_agent: str, 
                             predictions: Dict[str, Any]) -> None:
        """Broadcast resource predictions."""
        prediction_data = {
            "target_agent": target_agent,
            "predictions": predictions,
            "timestamp": datetime.now().isoformat()
        }
        self.comm_system.broadcast_notification(
            self.agent_id,
            {"type": "resource_predictions", "data": prediction_data}
        )

    def _broadcast_cleanup(self, target_agent: str) -> None:
        """Broadcast resource cleanup status."""
        cleanup_data = {
            "target_agent": target_agent,
            "timestamp": datetime.now().isoformat()
        }
        self.comm_system.broadcast_notification(
            self.agent_id,
            {"type": "resource_cleanup", "data": cleanup_data}
        ) 