import psutil
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from pathlib import Path

@dataclass
class ResourceMetrics:
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    process_count: int
    network_io: Dict[str, float]
    terminal_sessions: int

class ResourceMonitor:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        self.logger = logging.getLogger("resource_monitor")
        self.logger.setLevel(logging.INFO)
        
        # File handler for resource metrics
        metrics_handler = logging.FileHandler(self.log_dir / "resource_metrics.log")
        metrics_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(metrics_handler)
        
        # File handler for alerts
        alerts_handler = logging.FileHandler(self.log_dir / "resource_alerts.log")
        alerts_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.alerts_logger = logging.getLogger("resource_alerts")
        self.alerts_logger.setLevel(logging.WARNING)
        self.alerts_logger.addHandler(alerts_handler)
        
        # Resource thresholds
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_usage_percent": 90.0,
            "process_count": 1000
        }
        
        # Initialize metrics history
        self.metrics_history: List[ResourceMetrics] = []
        self.max_history_size = 1000
        
        # Network IO counters
        self.last_net_io = psutil.net_io_counters()
        self.last_net_io_time = time.time()

    def collect_metrics(self, terminal_sessions: int = 0) -> ResourceMetrics:
        """Collect current system resource metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Process count
            process_count = len(psutil.pids())
            
            # Network IO
            current_net_io = psutil.net_io_counters()
            current_time = time.time()
            time_diff = current_time - self.last_net_io_time
            
            network_io = {
                "bytes_sent": (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff,
                "bytes_recv": (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff,
                "packets_sent": (current_net_io.packets_sent - self.last_net_io.packets_sent) / time_diff,
                "packets_recv": (current_net_io.packets_recv - self.last_net_io.packets_recv) / time_diff
            }
            
            # Update network IO counters
            self.last_net_io = current_net_io
            self.last_net_io_time = current_time
            
            # Create metrics object
            metrics = ResourceMetrics(
                timestamp=datetime.utcnow().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage_percent=disk_usage_percent,
                process_count=process_count,
                network_io=network_io,
                terminal_sessions=terminal_sessions
            )
            
            # Log metrics
            self.logger.info(json.dumps({
                "type": "metrics",
                "data": metrics.__dict__
            }))
            
            # Check thresholds and log alerts
            self._check_thresholds(metrics)
            
            # Update history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {str(e)}")
            raise

    def _check_thresholds(self, metrics: ResourceMetrics) -> None:
        """Check if any metrics exceed thresholds and log alerts."""
        alerts = []
        
        if metrics.cpu_percent > self.thresholds["cpu_percent"]:
            alerts.append(f"High CPU usage: {metrics.cpu_percent}%")
            
        if metrics.memory_percent > self.thresholds["memory_percent"]:
            alerts.append(f"High memory usage: {metrics.memory_percent}%")
            
        if metrics.disk_usage_percent > self.thresholds["disk_usage_percent"]:
            alerts.append(f"High disk usage: {metrics.disk_usage_percent}%")
            
        if metrics.process_count > self.thresholds["process_count"]:
            alerts.append(f"High process count: {metrics.process_count}")
        
        for alert in alerts:
            self.alerts_logger.warning(alert)

    def get_metrics_history(self, limit: Optional[int] = None) -> List[ResourceMetrics]:
        """Get historical metrics, optionally limited to the most recent N entries."""
        if limit is None:
            return self.metrics_history
        return self.metrics_history[-limit:]

    def get_current_metrics(self) -> Optional[ResourceMetrics]:
        """Get the most recent metrics."""
        if not self.metrics_history:
            return None
        return self.metrics_history[-1]

    def get_metrics_summary(self, time_window: int = 3600) -> Dict:
        """Get a summary of metrics over a time window (in seconds)."""
        current_time = time.time()
        recent_metrics = [
            m for m in self.metrics_history
            if (current_time - datetime.fromisoformat(m.timestamp).timestamp()) <= time_window
        ]
        
        if not recent_metrics:
            return {}
        
        return {
            "avg_cpu_percent": sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            "avg_memory_percent": sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            "avg_disk_usage_percent": sum(m.disk_usage_percent for m in recent_metrics) / len(recent_metrics),
            "max_process_count": max(m.process_count for m in recent_metrics),
            "total_network_io": {
                "bytes_sent": sum(m.network_io["bytes_sent"] for m in recent_metrics),
                "bytes_recv": sum(m.network_io["bytes_recv"] for m in recent_metrics),
                "packets_sent": sum(m.network_io["packets_sent"] for m in recent_metrics),
                "packets_recv": sum(m.network_io["packets_recv"] for m in recent_metrics)
            },
            "terminal_sessions": recent_metrics[-1].terminal_sessions
        }

resource_monitor = ResourceMonitor() 