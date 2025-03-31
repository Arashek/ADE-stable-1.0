from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass
import json
import psutil
import prometheus_client as prom

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    timestamp: datetime
    category: str
    name: str
    value: float
    tags: Dict[str, str]
    
@dataclass
class ErrorEvent:
    timestamp: datetime
    error_type: str
    message: str
    context: Dict[str, Any]
    severity: str
    
@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]

class MonitoringService:
    """Service for monitoring system performance and health"""
    
    def __init__(self):
        # Initialize Prometheus metrics
        self.request_counter = prom.Counter(
            'ade_requests_total',
            'Total requests processed',
            ['type', 'status']
        )
        self.request_duration = prom.Histogram(
            'ade_request_duration_seconds',
            'Request duration in seconds',
            ['type']
        )
        self.error_counter = prom.Counter(
            'ade_errors_total',
            'Total errors encountered',
            ['type', 'severity']
        )
        
        # Performance metrics storage
        self.metrics: List[PerformanceMetric] = []
        self.errors: List[ErrorEvent] = []
        self.system_metrics: List[SystemMetrics] = []
        
        # Start background monitoring
        asyncio.create_task(self._monitor_system())
        
    def start_request_tracking(self, request_id: str) -> None:
        """Start tracking a request"""
        self.request_counter.labels(type='total', status='started').inc()
        
    def record_request_completion(
        self,
        request_id: str,
        duration: float,
        success: bool
    ) -> None:
        """Record request completion"""
        status = 'success' if success else 'failure'
        self.request_counter.labels(type='total', status=status).inc()
        self.request_duration.labels(type='request').observe(duration)
        
    def record_error(
        self,
        error_id: str,
        error: str,
        severity: str = 'error',
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record an error event"""
        self.error_counter.labels(
            type=error_id,
            severity=severity
        ).inc()
        
        self.errors.append(ErrorEvent(
            timestamp=datetime.now(),
            error_type=error_id,
            message=error,
            context=context or {},
            severity=severity
        ))
        
    def record_performance_metric(
        self,
        category: str,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a performance metric"""
        self.metrics.append(PerformanceMetric(
            timestamp=datetime.now(),
            category=category,
            name=name,
            value=value,
            tags=tags or {}
        ))
        
    def start_workflow_tracking(
        self,
        workflow_id: str,
        workflow_type: str
    ) -> None:
        """Start tracking a workflow"""
        self.request_counter.labels(
            type=f'workflow_{workflow_type}',
            status='started'
        ).inc()
        
    def record_workflow_completion(
        self,
        workflow_id: str,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> None:
        """Record workflow completion"""
        status = 'success' if success else 'failure'
        self.request_counter.labels(
            type='workflow',
            status=status
        ).inc()
        
        if not success and error:
            self.record_error(
                error_id=f'workflow_{workflow_id}',
                error=error,
                context=metadata
            )
            
    def get_recent_metrics(
        self,
        category: Optional[str] = None,
        minutes: int = 60
    ) -> List[PerformanceMetric]:
        """Get recent performance metrics"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        metrics = [m for m in self.metrics if m.timestamp >= cutoff]
        
        if category:
            metrics = [m for m in metrics if m.category == category]
            
        return metrics
        
    def get_recent_errors(
        self,
        severity: Optional[str] = None,
        minutes: int = 60
    ) -> List[ErrorEvent]:
        """Get recent error events"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        errors = [e for e in self.errors if e.timestamp >= cutoff]
        
        if severity:
            errors = [e for e in errors if e.severity == severity]
            
        return errors
        
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics"""
        if not self.system_metrics:
            return {}
            
        latest = self.system_metrics[-1]
        return {
            'cpu_percent': latest.cpu_percent,
            'memory_usage': latest.memory_usage,
            'disk_usage': latest.disk_usage,
            'network_io': latest.network_io,
            'timestamp': datetime.now().isoformat()
        }
        
    async def _monitor_system(self) -> None:
        """Background task to monitor system metrics"""
        while True:
            try:
                # Collect system metrics
                cpu = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                net_io = psutil.net_io_counters()._asdict()
                
                # Store metrics
                self.system_metrics.append(SystemMetrics(
                    cpu_percent=cpu,
                    memory_usage=memory,
                    disk_usage=disk,
                    network_io=net_io
                ))
                
                # Keep only last hour of metrics
                cutoff = datetime.now() - timedelta(hours=1)
                self.metrics = [m for m in self.metrics
                              if m.timestamp >= cutoff]
                self.errors = [e for e in self.errors
                             if e.timestamp >= cutoff]
                self.system_metrics = self.system_metrics[-3600:]  # Keep last hour
                
                await asyncio.sleep(1)  # Collect every second
                
            except Exception as e:
                logger.error(f"Error monitoring system: {str(e)}")
                await asyncio.sleep(5)  # Back off on error
                
    def export_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        return prom.generate_latest().decode('utf-8')
