from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
import psutil
import json
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ResourceMetrics:
    """Resource usage metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    gpu_percent: Optional[float] = None
    disk_usage_percent: float
    network_io: Dict[str, int]
    process_count: int
    thread_count: int
    model_name: Optional[str] = None
    task_id: Optional[str] = None

class ResourceTracker:
    """Tracks and manages resource usage across the platform"""
    
    def __init__(self, data_dir: str = "data/resource"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_history: List[ResourceMetrics] = []
        self.current_metrics: Optional[ResourceMetrics] = None
        self.resource_limits: Dict[str, float] = {}
        self._load_data()
    
    def _load_data(self):
        """Load historical resource data"""
        try:
            metrics_file = self.data_dir / "metrics.json"
            if metrics_file.exists():
                with open(metrics_file, "r") as f:
                    data = json.load(f)
                    self.metrics_history = [
                        ResourceMetrics(
                            timestamp=datetime.fromisoformat(m["timestamp"]),
                            cpu_percent=m["cpu_percent"],
                            memory_percent=m["memory_percent"],
                            gpu_percent=m.get("gpu_percent"),
                            disk_usage_percent=m["disk_usage_percent"],
                            network_io=m["network_io"],
                            process_count=m["process_count"],
                            thread_count=m["thread_count"],
                            model_name=m.get("model_name"),
                            task_id=m.get("task_id")
                        )
                        for m in data
                    ]
            
            limits_file = self.data_dir / "limits.json"
            if limits_file.exists():
                with open(limits_file, "r") as f:
                    self.resource_limits = json.load(f)
                    
        except Exception as e:
            logger.error(f"Failed to load resource data: {str(e)}")
    
    def _save_data(self):
        """Save resource data to disk"""
        try:
            # Save metrics
            metrics_data = [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "cpu_percent": m.cpu_percent,
                    "memory_percent": m.memory_percent,
                    "gpu_percent": m.gpu_percent,
                    "disk_usage_percent": m.disk_usage_percent,
                    "network_io": m.network_io,
                    "process_count": m.process_count,
                    "thread_count": m.thread_count,
                    "model_name": m.model_name,
                    "task_id": m.task_id
                }
                for m in self.metrics_history
            ]
            
            with open(self.data_dir / "metrics.json", "w") as f:
                json.dump(metrics_data, f)
            
            # Save limits
            with open(self.data_dir / "limits.json", "w") as f:
                json.dump(self.resource_limits, f)
                
        except Exception as e:
            logger.error(f"Failed to save resource data: {str(e)}")
    
    def set_resource_limit(self, resource: str, limit: float):
        """Set resource usage limit
        
        Args:
            resource: Resource name (cpu, memory, gpu, disk)
            limit: Usage limit percentage
        """
        self.resource_limits[resource] = limit
        self._save_data()
    
    def collect_metrics(self, model_name: Optional[str] = None, task_id: Optional[str] = None) -> ResourceMetrics:
        """Collect current resource metrics
        
        Args:
            model_name: Optional model name to associate with metrics
            task_id: Optional task ID to associate with metrics
            
        Returns:
            Current resource metrics
        """
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Get GPU usage if available
            gpu_percent = None
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                info = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_percent = info.gpu
                pynvml.nvmlShutdown()
            except:
                pass
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Get network I/O
            net_io = psutil.net_io_counters()
            network_io = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv
            }
            
            # Get process and thread counts
            process_count = len(psutil.pids())
            thread_count = sum(p.num_threads() for p in psutil.process_iter(['num_threads']))
            
            # Create metrics
            metrics = ResourceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                gpu_percent=gpu_percent,
                disk_usage_percent=disk_usage_percent,
                network_io=network_io,
                process_count=process_count,
                thread_count=thread_count,
                model_name=model_name,
                task_id=task_id
            )
            
            # Update current metrics
            self.current_metrics = metrics
            
            # Add to history
            self.metrics_history.append(metrics)
            
            # Trim history if needed (keep last 1000 records)
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
            # Save data
            self._save_data()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect resource metrics: {str(e)}")
            return None
    
    def get_resource_summary(self, time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Get resource usage summary
        
        Args:
            time_window: Time window for summary
            
        Returns:
            Dictionary of resource summaries
        """
        summary = {}
        try:
            cutoff_time = datetime.now() - time_window
            recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return summary
            
            # Calculate averages
            summary = {
                "cpu": {
                    "avg_percent": sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
                    "max_percent": max(m.cpu_percent for m in recent_metrics),
                    "limit": self.resource_limits.get("cpu", 100)
                },
                "memory": {
                    "avg_percent": sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
                    "max_percent": max(m.memory_percent for m in recent_metrics),
                    "limit": self.resource_limits.get("memory", 100)
                },
                "disk": {
                    "avg_percent": sum(m.disk_usage_percent for m in recent_metrics) / len(recent_metrics),
                    "max_percent": max(m.disk_usage_percent for m in recent_metrics),
                    "limit": self.resource_limits.get("disk", 100)
                },
                "network": {
                    "total_sent": sum(m.network_io["bytes_sent"] for m in recent_metrics),
                    "total_recv": sum(m.network_io["bytes_recv"] for m in recent_metrics)
                },
                "processes": {
                    "avg_count": sum(m.process_count for m in recent_metrics) / len(recent_metrics),
                    "max_count": max(m.process_count for m in recent_metrics)
                },
                "threads": {
                    "avg_count": sum(m.thread_count for m in recent_metrics) / len(recent_metrics),
                    "max_count": max(m.thread_count for m in recent_metrics)
                }
            }
            
            # Add GPU metrics if available
            gpu_metrics = [m for m in recent_metrics if m.gpu_percent is not None]
            if gpu_metrics:
                summary["gpu"] = {
                    "avg_percent": sum(m.gpu_percent for m in gpu_metrics) / len(gpu_metrics),
                    "max_percent": max(m.gpu_percent for m in gpu_metrics),
                    "limit": self.resource_limits.get("gpu", 100)
                }
            
        except Exception as e:
            logger.error(f"Failed to get resource summary: {str(e)}")
        
        return summary
    
    def get_resource_alerts(self) -> List[Dict[str, Any]]:
        """Get resource-related alerts
        
        Returns:
            List of resource alerts
        """
        alerts = []
        try:
            if not self.current_metrics:
                return alerts
            
            # Check CPU usage
            if self.current_metrics.cpu_percent > self.resource_limits.get("cpu", 90):
                alerts.append({
                    "type": "high_cpu_usage",
                    "severity": "warning",
                    "message": f"High CPU usage: {self.current_metrics.cpu_percent:.1f}%"
                })
            
            # Check memory usage
            if self.current_metrics.memory_percent > self.resource_limits.get("memory", 90):
                alerts.append({
                    "type": "high_memory_usage",
                    "severity": "warning",
                    "message": f"High memory usage: {self.current_metrics.memory_percent:.1f}%"
                })
            
            # Check GPU usage
            if self.current_metrics.gpu_percent is not None:
                if self.current_metrics.gpu_percent > self.resource_limits.get("gpu", 90):
                    alerts.append({
                        "type": "high_gpu_usage",
                        "severity": "warning",
                        "message": f"High GPU usage: {self.current_metrics.gpu_percent:.1f}%"
                    })
            
            # Check disk usage
            if self.current_metrics.disk_usage_percent > self.resource_limits.get("disk", 90):
                alerts.append({
                    "type": "high_disk_usage",
                    "severity": "warning",
                    "message": f"High disk usage: {self.current_metrics.disk_usage_percent:.1f}%"
                })
            
            # Check process count
            if self.current_metrics.process_count > 1000:  # Arbitrary threshold
                alerts.append({
                    "type": "high_process_count",
                    "severity": "warning",
                    "message": f"High process count: {self.current_metrics.process_count}"
                })
            
            # Check thread count
            if self.current_metrics.thread_count > 5000:  # Arbitrary threshold
                alerts.append({
                    "type": "high_thread_count",
                    "severity": "warning",
                    "message": f"High thread count: {self.current_metrics.thread_count}"
                })
            
        except Exception as e:
            logger.error(f"Failed to get resource alerts: {str(e)}")
        
        return alerts
    
    def get_resource_trends(self, time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Get resource usage trends
        
        Args:
            time_window: Time window for trends
            
        Returns:
            Dictionary of resource trends
        """
        trends = {}
        try:
            cutoff_time = datetime.now() - time_window
            recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return trends
            
            # Sort by timestamp
            recent_metrics.sort(key=lambda x: x.timestamp)
            
            # Calculate trends
            trends = {
                "timestamps": [m.timestamp.isoformat() for m in recent_metrics],
                "cpu_percent": [m.cpu_percent for m in recent_metrics],
                "memory_percent": [m.memory_percent for m in recent_metrics],
                "disk_usage_percent": [m.disk_usage_percent for m in recent_metrics],
                "process_count": [m.process_count for m in recent_metrics],
                "thread_count": [m.thread_count for m in recent_metrics]
            }
            
            # Add GPU trends if available
            gpu_metrics = [m for m in recent_metrics if m.gpu_percent is not None]
            if gpu_metrics:
                trends["gpu_percent"] = [m.gpu_percent for m in gpu_metrics]
            
        except Exception as e:
            logger.error(f"Failed to get resource trends: {str(e)}")
        
        return trends 