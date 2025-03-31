from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
import logging
import time
import psutil
import threading
from dataclasses import dataclass
from collections import deque

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data"""
    name: str
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = None

class SystemMetrics(BaseModel):
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict[str, float]
    timestamp: datetime

class AnalysisMetrics(BaseModel):
    """Analysis performance metrics"""
    duration: float
    memory_usage: float
    cpu_usage: float
    timestamp: datetime
    metadata: Dict[str, Any] = {}

class HealthStatus(BaseModel):
    """System health status"""
    status: str
    timestamp: datetime
    issues: List[Dict[str, Any]] = []
    metrics: Dict[str, float] = {}

class MonitoringSystem:
    """System for monitoring analysis performance and health"""
    
    def __init__(self, history_size: int = 1000):
        self.performance_history: Dict[str, deque] = {}
        self.analysis_history: List[AnalysisMetrics] = []
        self.health_history: List[HealthStatus] = []
        self.history_size = history_size
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_monitoring = False
        
    def start_monitoring(self):
        """Start the monitoring system"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return
            
        self._stop_monitoring = False
        self._monitoring_thread = threading.Thread(target=self._monitor_system)
        self._monitoring_thread.daemon = True
        self._monitoring_thread.start()
        
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self._stop_monitoring = True
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join()
            
    def record_analysis_metrics(self, metrics: AnalysisMetrics):
        """Record analysis performance metrics"""
        self.analysis_history.append(metrics)
        if len(self.analysis_history) > self.history_size:
            self.analysis_history.pop(0)
            
    def record_performance_metric(self, metric: PerformanceMetric):
        """Record a performance metric"""
        if metric.name not in self.performance_history:
            self.performance_history[metric.name] = deque(maxlen=self.history_size)
        self.performance_history[metric.name].append(metric)
        
    def record_health_status(self, status: HealthStatus):
        """Record system health status"""
        self.health_history.append(status)
        if len(self.health_history) > self.history_size:
            self.health_history.pop(0)
            
    def get_performance_metrics(self, metric_name: str) -> List[PerformanceMetric]:
        """Get performance metrics for a specific metric name"""
        return list(self.performance_history.get(metric_name, []))
        
    def get_analysis_metrics(self) -> List[AnalysisMetrics]:
        """Get analysis performance metrics"""
        return self.analysis_history
        
    def get_health_status(self) -> Optional[HealthStatus]:
        """Get latest health status"""
        if not self.health_history:
            return None
        return self.health_history[-1]
        
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        return SystemMetrics(
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage('/').percent,
            network_io={
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv
            },
            timestamp=datetime.now()
        )
        
    def _monitor_system(self):
        """Monitor system performance in background"""
        while not self._stop_monitoring:
            try:
                # Record system metrics
                system_metrics = self.get_system_metrics()
                self.record_performance_metric(PerformanceMetric(
                    name='system_metrics',
                    value=system_metrics.cpu_percent,
                    timestamp=system_metrics.timestamp,
                    metadata=system_metrics.dict()
                ))
                
                # Check system health
                health_status = self._check_system_health(system_metrics)
                self.record_health_status(health_status)
                
                # Sleep for monitoring interval
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in monitoring thread: {str(e)}")
                time.sleep(5)  # Wait before retrying
                
    def _check_system_health(self, metrics: SystemMetrics) -> HealthStatus:
        """Check system health based on metrics"""
        issues = []
        
        # Check CPU usage
        if metrics.cpu_percent > 90:
            issues.append({
                'type': 'high_cpu',
                'value': metrics.cpu_percent,
                'threshold': 90
            })
            
        # Check memory usage
        if metrics.memory_percent > 90:
            issues.append({
                'type': 'high_memory',
                'value': metrics.memory_percent,
                'threshold': 90
            })
            
        # Check disk usage
        if metrics.disk_usage > 90:
            issues.append({
                'type': 'high_disk',
                'value': metrics.disk_usage,
                'threshold': 90
            })
            
        # Determine overall status
        status = 'healthy'
        if issues:
            status = 'warning' if len(issues) == 1 else 'critical'
            
        return HealthStatus(
            status=status,
            timestamp=datetime.now(),
            issues=issues,
            metrics=metrics.dict()
        ) 