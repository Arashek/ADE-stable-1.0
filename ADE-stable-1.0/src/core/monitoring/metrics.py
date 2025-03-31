import logging
import time
import psutil
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Metrics:
    """Metrics data structure"""
    execution_time: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    io_operations: int = 0
    network_usage: float = 0.0
    retry_count: int = 0
    error_count: int = 0
    fix_count: int = 0
    success_rate: float = 0.0
    avg_delay: float = 0.0
    circuit_breaker_state: str = "CLOSED"
    timestamp: datetime = None

class MetricsCollector:
    """Collects and monitors system metrics"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("metrics_collector")
        self.metrics_history: List[Metrics] = []
        self.alert_thresholds: Dict[str, float] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.process = psutil.Process()
        
    def start_collection(self):
        """Start collecting metrics"""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.start_cpu = self.process.cpu_percent()
        self.start_io = self.process.io_counters()
        self.start_net = self.process.connections()
        
    def stop_collection(self):
        """Stop collecting metrics and record them"""
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024
        end_cpu = self.process.cpu_percent()
        end_io = self.process.io_counters()
        end_net = self.process.connections()
        
        metrics = Metrics(
            execution_time=end_time - self.start_time,
            memory_usage=end_memory - self.start_memory,
            cpu_usage=end_cpu - self.start_cpu,
            io_operations=end_io.read_bytes + end_io.write_bytes,
            network_usage=len(end_net),
            timestamp=datetime.now()
        )
        
        self.metrics_history.append(metrics)
        self._check_alert_thresholds(metrics)
        
        return metrics
    
    def record_retry(self, delay: float):
        """Record a retry attempt"""
        if self.metrics_history:
            self.metrics_history[-1].retry_count += 1
            self.metrics_history[-1].avg_delay = (
                (self.metrics_history[-1].avg_delay * (self.metrics_history[-1].retry_count - 1) + delay)
                / self.metrics_history[-1].retry_count
            )
    
    def record_error(self):
        """Record an error occurrence"""
        if self.metrics_history:
            self.metrics_history[-1].error_count += 1
            self.metrics_history[-1].success_rate = (
                (self.metrics_history[-1].retry_count - self.metrics_history[-1].error_count)
                / max(1, self.metrics_history[-1].retry_count)
            )
    
    def record_fix(self):
        """Record a fix application"""
        if self.metrics_history:
            self.metrics_history[-1].fix_count += 1
    
    def update_circuit_breaker_state(self, state: str):
        """Update circuit breaker state"""
        if self.metrics_history:
            self.metrics_history[-1].circuit_breaker_state = state
    
    def get_metrics(self) -> Metrics:
        """Get the most recent metrics"""
        return self.metrics_history[-1] if self.metrics_history else Metrics()
    
    def get_metrics_history(self, limit: Optional[int] = None) -> List[Metrics]:
        """Get metrics history"""
        if limit:
            return self.metrics_history[-limit:]
        return self.metrics_history
    
    def set_alert_thresholds(self, thresholds: Dict[str, float]):
        """Set alert thresholds"""
        self.alert_thresholds = thresholds
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current alerts"""
        return self.alerts
    
    def clear_alerts(self):
        """Clear current alerts"""
        self.alerts = []
    
    def _check_alert_thresholds(self, metrics: Metrics):
        """Check if any metrics exceed thresholds"""
        for metric, threshold in self.alert_thresholds.items():
            value = getattr(metrics, metric, None)
            if value is not None and value > threshold:
                self.alerts.append({
                    "metric": metric,
                    "threshold": threshold,
                    "value": value,
                    "timestamp": metrics.timestamp
                })
                self.logger.warning(
                    f"Alert: {metric} exceeded threshold. "
                    f"Value: {value}, Threshold: {threshold}"
                ) 