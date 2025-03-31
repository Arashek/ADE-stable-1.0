"""
Comprehensive metrics collection and monitoring capabilities.
"""

from typing import Dict, List, Any, Optional, Type, Callable, Protocol
from datetime import datetime
import time
import psutil
import logging
from dataclasses import dataclass
from enum import Enum

class MetricType(Enum):
    """Types of metrics that can be collected."""
    PERFORMANCE = "performance"
    USAGE = "usage"
    HEALTH = "health"
    CUSTOM = "custom"

@dataclass
class Metric:
    """Base class for all metrics."""
    name: str
    type: MetricType
    value: Any
    timestamp: datetime
    tags: Dict[str, str]
    metadata: Dict[str, Any]

class MetricsCollector:
    """Collector for various system metrics."""
    
    def __init__(self):
        self.metrics: List[Metric] = []
        self.logger = logging.getLogger(__name__)
        
    def collect_performance_metrics(self) -> List[Metric]:
        """Collect performance-related metrics."""
        metrics = []
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append(Metric(
            name="cpu_usage",
            type=MetricType.PERFORMANCE,
            value=cpu_percent,
            timestamp=datetime.now(),
            tags={"component": "cpu"},
            metadata={"interval": 1}
        ))
        
        # Memory metrics
        memory = psutil.virtual_memory()
        metrics.append(Metric(
            name="memory_usage",
            type=MetricType.PERFORMANCE,
            value=memory.percent,
            timestamp=datetime.now(),
            tags={"component": "memory"},
            metadata={"total": memory.total, "available": memory.available}
        ))
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        metrics.append(Metric(
            name="disk_usage",
            type=MetricType.PERFORMANCE,
            value=disk.percent,
            timestamp=datetime.now(),
            tags={"component": "disk"},
            metadata={"total": disk.total, "free": disk.free}
        ))
        
        return metrics
        
    def collect_usage_metrics(self) -> List[Metric]:
        """Collect usage-related metrics."""
        metrics = []
        
        # Process metrics
        process = psutil.Process()
        metrics.append(Metric(
            name="process_usage",
            type=MetricType.USAGE,
            value={
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "num_threads": process.num_threads()
            },
            timestamp=datetime.now(),
            tags={"component": "process"},
            metadata={"pid": process.pid}
        ))
        
        # Network metrics
        net_io = psutil.net_io_counters()
        metrics.append(Metric(
            name="network_usage",
            type=MetricType.USAGE,
            value={
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            },
            timestamp=datetime.now(),
            tags={"component": "network"},
            metadata={}
        ))
        
        return metrics
        
    def collect_health_metrics(self) -> List[Metric]:
        """Collect system health metrics."""
        metrics = []
        
        # System load
        load_avg = psutil.getloadavg()
        metrics.append(Metric(
            name="system_load",
            type=MetricType.HEALTH,
            value=load_avg,
            timestamp=datetime.now(),
            tags={"component": "system"},
            metadata={"intervals": [1, 5, 15]}
        ))
        
        # Process count
        process_count = len(psutil.pids())
        metrics.append(Metric(
            name="process_count",
            type=MetricType.HEALTH,
            value=process_count,
            timestamp=datetime.now(),
            tags={"component": "system"},
            metadata={}
        ))
        
        # System uptime
        uptime = time.time() - psutil.boot_time()
        metrics.append(Metric(
            name="system_uptime",
            type=MetricType.HEALTH,
            value=uptime,
            timestamp=datetime.now(),
            tags={"component": "system"},
            metadata={}
        ))
        
        return metrics
        
    def collect_custom_metrics(self, metric_name: str, value: Any, 
                             tags: Dict[str, str], metadata: Dict[str, Any]) -> Metric:
        """Collect custom metrics."""
        metric = Metric(
            name=metric_name,
            type=MetricType.CUSTOM,
            value=value,
            timestamp=datetime.now(),
            tags=tags,
            metadata=metadata
        )
        self.metrics.append(metric)
        return metric
        
    def get_metrics(self, metric_type: Optional[MetricType] = None) -> List[Metric]:
        """Get collected metrics, optionally filtered by type."""
        if metric_type is None:
            return self.metrics
        return [m for m in self.metrics if m.type == metric_type]
        
    def clear_metrics(self) -> None:
        """Clear all collected metrics."""
        self.metrics.clear()

class MetricsAnalyzer:
    """Analyzer for collected metrics."""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.logger = logging.getLogger(__name__)
        
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance metrics."""
        performance_metrics = self.collector.get_metrics(MetricType.PERFORMANCE)
        analysis = {
            "cpu_usage": self._analyze_cpu_usage(performance_metrics),
            "memory_usage": self._analyze_memory_usage(performance_metrics),
            "disk_usage": self._analyze_disk_usage(performance_metrics)
        }
        return analysis
        
    def analyze_usage(self) -> Dict[str, Any]:
        """Analyze usage metrics."""
        usage_metrics = self.collector.get_metrics(MetricType.USAGE)
        analysis = {
            "process_usage": self._analyze_process_usage(usage_metrics),
            "network_usage": self._analyze_network_usage(usage_metrics)
        }
        return analysis
        
    def analyze_health(self) -> Dict[str, Any]:
        """Analyze system health metrics."""
        health_metrics = self.collector.get_metrics(MetricType.HEALTH)
        analysis = {
            "system_load": self._analyze_system_load(health_metrics),
            "process_count": self._analyze_process_count(health_metrics),
            "system_uptime": self._analyze_system_uptime(health_metrics)
        }
        return analysis
        
    def _analyze_cpu_usage(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze CPU usage patterns."""
        cpu_metrics = [m for m in metrics if m.name == "cpu_usage"]
        if not cpu_metrics:
            return {"status": "no_data"}
            
        values = [m.value for m in cpu_metrics]
        return {
            "current": values[-1],
            "average": sum(values) / len(values),
            "max": max(values),
            "min": min(values),
            "trend": self._calculate_trend(values)
        }
        
    def _analyze_memory_usage(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze memory usage patterns."""
        memory_metrics = [m for m in metrics if m.name == "memory_usage"]
        if not memory_metrics:
            return {"status": "no_data"}
            
        values = [m.value for m in memory_metrics]
        return {
            "current": values[-1],
            "average": sum(values) / len(values),
            "max": max(values),
            "min": min(values),
            "trend": self._calculate_trend(values)
        }
        
    def _analyze_disk_usage(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze disk usage patterns."""
        disk_metrics = [m for m in metrics if m.name == "disk_usage"]
        if not disk_metrics:
            return {"status": "no_data"}
            
        values = [m.value for m in disk_metrics]
        return {
            "current": values[-1],
            "average": sum(values) / len(values),
            "max": max(values),
            "min": min(values),
            "trend": self._calculate_trend(values)
        }
        
    def _analyze_process_usage(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze process usage patterns."""
        process_metrics = [m for m in metrics if m.name == "process_usage"]
        if not process_metrics:
            return {"status": "no_data"}
            
        values = [m.value for m in process_metrics]
        return {
            "current": values[-1],
            "average": {
                "cpu_percent": sum(v["cpu_percent"] for v in values) / len(values),
                "memory_percent": sum(v["memory_percent"] for v in values) / len(values),
                "num_threads": sum(v["num_threads"] for v in values) / len(values)
            }
        }
        
    def _analyze_network_usage(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze network usage patterns."""
        network_metrics = [m for m in metrics if m.name == "network_usage"]
        if not network_metrics:
            return {"status": "no_data"}
            
        values = [m.value for m in network_metrics]
        return {
            "current": values[-1],
            "total_bytes_sent": sum(v["bytes_sent"] for v in values),
            "total_bytes_recv": sum(v["bytes_recv"] for v in values),
            "total_packets_sent": sum(v["packets_sent"] for v in values),
            "total_packets_recv": sum(v["packets_recv"] for v in values)
        }
        
    def _analyze_system_load(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze system load patterns."""
        load_metrics = [m for m in metrics if m.name == "system_load"]
        if not load_metrics:
            return {"status": "no_data"}
            
        values = [m.value for m in load_metrics]
        return {
            "current": values[-1],
            "average": [
                sum(v[i] for v in values) / len(values)
                for i in range(3)
            ]
        }
        
    def _analyze_process_count(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze process count patterns."""
        count_metrics = [m for m in metrics if m.name == "process_count"]
        if not count_metrics:
            return {"status": "no_data"}
            
        values = [m.value for m in count_metrics]
        return {
            "current": values[-1],
            "average": sum(values) / len(values),
            "max": max(values),
            "min": min(values)
        }
        
    def _analyze_system_uptime(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze system uptime patterns."""
        uptime_metrics = [m for m in metrics if m.name == "system_uptime"]
        if not uptime_metrics:
            return {"status": "no_data"}
            
        values = [m.value for m in uptime_metrics]
        return {
            "current": values[-1],
            "start_time": datetime.fromtimestamp(time.time() - values[-1])
        }
        
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values."""
        if len(values) < 2:
            return "insufficient_data"
            
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        if second_half > first_half * 1.1:
            return "increasing"
        elif second_half < first_half * 0.9:
            return "decreasing"
        else:
            return "stable"

class MetricsMonitor:
    """Monitor for system metrics with alerts."""
    
    def __init__(self, collector: MetricsCollector, analyzer: MetricsAnalyzer):
        self.collector = collector
        self.analyzer = analyzer
        self.alerts: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        
    def start_monitoring(self, interval: float = 1.0) -> None:
        """Start monitoring metrics with the specified interval."""
        while True:
            try:
                # Collect metrics
                self.collector.collect_performance_metrics()
                self.collector.collect_usage_metrics()
                self.collector.collect_health_metrics()
                
                # Analyze metrics
                performance_analysis = self.analyzer.analyze_performance()
                usage_analysis = self.analyzer.analyze_usage()
                health_analysis = self.analyzer.analyze_health()
                
                # Check for alerts
                self._check_alerts(performance_analysis, usage_analysis, health_analysis)
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring: {str(e)}")
                time.sleep(interval)
                
    def _check_alerts(self, performance: Dict[str, Any], 
                     usage: Dict[str, Any], health: Dict[str, Any]) -> None:
        """Check for alert conditions in the analyzed metrics."""
        # CPU usage alerts
        if performance["cpu_usage"]["current"] > 90:
            self._create_alert("high_cpu_usage", "CPU usage is above 90%", 
                             performance["cpu_usage"])
            
        # Memory usage alerts
        if performance["memory_usage"]["current"] > 90:
            self._create_alert("high_memory_usage", "Memory usage is above 90%", 
                             performance["memory_usage"])
            
        # Disk usage alerts
        if performance["disk_usage"]["current"] > 90:
            self._create_alert("high_disk_usage", "Disk usage is above 90%", 
                             performance["disk_usage"])
            
        # Process count alerts
        if health["process_count"]["current"] > 1000:
            self._create_alert("high_process_count", "Process count is above 1000", 
                             health["process_count"])
            
        # System load alerts
        if any(load > 10 for load in health["system_load"]["current"]):
            self._create_alert("high_system_load", "System load is above 10", 
                             health["system_load"])
            
    def _create_alert(self, alert_type: str, message: str, 
                     details: Dict[str, Any]) -> None:
        """Create a new alert."""
        alert = {
            "type": alert_type,
            "message": message,
            "details": details,
            "timestamp": datetime.now()
        }
        self.alerts.append(alert)
        self.logger.warning(f"Alert: {message}")
        
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get all alerts."""
        return self.alerts
        
    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.alerts.clear() 