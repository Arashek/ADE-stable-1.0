from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum
import json
import time
import psutil
import prometheus_client as prom
from prometheus_client import Counter, Gauge, Histogram
import redis
import aiohttp
import asyncio
from ..auth.auth_service import User
from ..config.service_config import ServiceConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    id: str
    title: str
    description: str
    severity: AlertSeverity
    source: str
    created_at: datetime
    resolved_at: Optional[datetime]
    metadata: Dict[str, Any]

@dataclass
class MetricPoint:
    timestamp: datetime
    value: float
    labels: Dict[str, str]
    metadata: Dict[str, Any]

class TelemetryService:
    def __init__(self, redis_url: str, prometheus_url: str,
                 service_config: ServiceConfig):
        self.redis_client = redis.from_url(redis_url)
        self.prometheus_url = prometheus_url
        self.service_config = service_config
        
        # Initialize Prometheus metrics
        self.request_counter = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"]
        )
        
        self.request_latency = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration",
            ["method", "endpoint"]
        )
        
        self.error_counter = Counter(
            "http_errors_total",
            "Total HTTP errors",
            ["method", "endpoint", "error_type"]
        )
        
        self.memory_usage = Gauge(
            "memory_usage_bytes",
            "Memory usage in bytes",
            ["type"]
        )
        
        self.cpu_usage = Gauge(
            "cpu_usage_percent",
            "CPU usage percentage",
            ["cpu"]
        )
        
        self.active_connections = Gauge(
            "active_connections",
            "Number of active connections",
            ["type"]
        )
        
        # Initialize alert thresholds
        self.alert_thresholds = {
            "memory_usage": 0.9,  # 90%
            "cpu_usage": 0.8,     # 80%
            "error_rate": 0.05,   # 5%
            "response_time": 1.0   # 1 second
        }
        
        # Start monitoring tasks
        self._start_monitoring()
        
    def _start_monitoring(self):
        """Start system monitoring tasks."""
        async def monitor_system():
            while True:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Check thresholds and generate alerts
                await self._check_thresholds()
                
                # Update Prometheus metrics
                self._update_prometheus_metrics()
                
                await asyncio.sleep(15)  # Update every 15 seconds
                
        asyncio.create_task(monitor_system())
        
    def _collect_system_metrics(self):
        """Collect system metrics."""
        # Memory metrics
        memory = psutil.virtual_memory()
        self.memory_usage.labels(type="used").set(memory.used)
        self.memory_usage.labels(type="total").set(memory.total)
        
        # CPU metrics
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
            self.cpu_usage.labels(cpu=f"cpu{i}").set(percentage)
            
        # Connection metrics
        connections = psutil.net_connections()
        self.active_connections.labels(type="total").set(len(connections))
        
    async def _check_thresholds(self):
        """Check metric thresholds and generate alerts."""
        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent / 100 > self.alert_thresholds["memory_usage"]:
            await self.create_alert(
                title="High Memory Usage",
                description=f"Memory usage is at {memory.percent}%",
                severity=AlertSeverity.WARNING,
                source="system",
                metadata={"current_usage": memory.percent}
            )
            
        # Check CPU usage
        cpu_percent = psutil.cpu_percent()
        if cpu_percent / 100 > self.alert_thresholds["cpu_usage"]:
            await self.create_alert(
                title="High CPU Usage",
                description=f"CPU usage is at {cpu_percent}%",
                severity=AlertSeverity.WARNING,
                source="system",
                metadata={"current_usage": cpu_percent}
            )
            
    def _update_prometheus_metrics(self):
        """Update Prometheus metrics."""
        # Update system metrics
        self._collect_system_metrics()
        
        # Update application metrics
        self._update_application_metrics()
        
    def _update_application_metrics(self):
        """Update application-specific metrics."""
        # Get metrics from Redis
        metrics = self.redis_client.hgetall("application_metrics")
        
        # Update Prometheus metrics
        for key, value in metrics.items():
            try:
                value = float(value)
                if key.startswith("request_"):
                    self.request_counter.labels(
                        method=key.split("_")[1],
                        endpoint=key.split("_")[2],
                        status=key.split("_")[3]
                    ).inc(value)
                elif key.startswith("error_"):
                    self.error_counter.labels(
                        method=key.split("_")[1],
                        endpoint=key.split("_")[2],
                        error_type=key.split("_")[3]
                    ).inc(value)
            except (ValueError, IndexError):
                logger.warning(f"Invalid metric format: {key}={value}")
                
    async def create_alert(self, title: str, description: str,
                          severity: AlertSeverity, source: str,
                          metadata: Dict[str, Any] = None) -> Alert:
        """Create a new alert."""
        alert = Alert(
            id=str(time.time()),
            title=title,
            description=description,
            severity=severity,
            source=source,
            created_at=datetime.utcnow(),
            resolved_at=None,
            metadata=metadata or {}
        )
        
        # Store alert in Redis
        alert_key = f"alert:{alert.id}"
        self.redis_client.hmset(alert_key, {
            "title": alert.title,
            "description": alert.description,
            "severity": alert.severity.value,
            "source": alert.source,
            "created_at": alert.created_at.isoformat(),
            "metadata": json.dumps(alert.metadata)
        })
        
        # Add to alert list
        self.redis_client.lpush("alerts", alert.id)
        
        # Notify if critical
        if severity == AlertSeverity.CRITICAL:
            await self._notify_critical_alert(alert)
            
        return alert
        
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        alert_key = f"alert:{alert_id}"
        alert_data = self.redis_client.hgetall(alert_key)
        
        if not alert_data:
            return False
            
        alert_data["resolved_at"] = datetime.utcnow().isoformat()
        self.redis_client.hmset(alert_key, alert_data)
        
        return True
        
    def record_metric(self, name: str, value: float,
                     labels: Dict[str, str] = None,
                     metadata: Dict[str, Any] = None):
        """Record a metric point."""
        point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            labels=labels or {},
            metadata=metadata or {}
        )
        
        # Store metric in Redis
        metric_key = f"metric:{name}"
        self.redis_client.lpush(metric_key, json.dumps({
            "timestamp": point.timestamp.isoformat(),
            "value": point.value,
            "labels": point.labels,
            "metadata": point.metadata
        }))
        
        # Trim old metrics
        self.redis_client.ltrim(metric_key, 0, 9999)  # Keep last 10000 points
        
    async def get_metrics(self, name: str,
                         start_time: datetime = None,
                         end_time: datetime = None,
                         labels: Dict[str, str] = None) -> List[MetricPoint]:
        """Get metric points for a given metric."""
        metric_key = f"metric:{name}"
        points = []
        
        # Get all points
        raw_points = self.redis_client.lrange(metric_key, 0, -1)
        
        for raw_point in raw_points:
            point_data = json.loads(raw_point)
            point = MetricPoint(
                timestamp=datetime.fromisoformat(point_data["timestamp"]),
                value=point_data["value"],
                labels=point_data["labels"],
                metadata=point_data["metadata"]
            )
            
            # Apply filters
            if start_time and point.timestamp < start_time:
                continue
            if end_time and point.timestamp > end_time:
                continue
            if labels:
                if not all(point.labels.get(k) == v for k, v in labels.items()):
                    continue
                    
            points.append(point)
            
        return sorted(points, key=lambda x: x.timestamp)
        
    async def get_alerts(self, severity: AlertSeverity = None,
                        source: str = None,
                        resolved: bool = None) -> List[Alert]:
        """Get alerts with optional filters."""
        alerts = []
        alert_ids = self.redis_client.lrange("alerts", 0, -1)
        
        for alert_id in alert_ids:
            alert_key = f"alert:{alert_id}"
            alert_data = self.redis_client.hgetall(alert_key)
            
            if not alert_data:
                continue
                
            alert = Alert(
                id=alert_id,
                title=alert_data["title"],
                description=alert_data["description"],
                severity=AlertSeverity(alert_data["severity"]),
                source=alert_data["source"],
                created_at=datetime.fromisoformat(alert_data["created_at"]),
                resolved_at=datetime.fromisoformat(alert_data["resolved_at"]) if "resolved_at" in alert_data else None,
                metadata=json.loads(alert_data["metadata"])
            )
            
            # Apply filters
            if severity and alert.severity != severity:
                continue
            if source and alert.source != source:
                continue
            if resolved is not None:
                if resolved and not alert.resolved_at:
                    continue
                if not resolved and alert.resolved_at:
                    continue
                    
            alerts.append(alert)
            
        return sorted(alerts, key=lambda x: x.created_at, reverse=True)
        
    async def _notify_critical_alert(self, alert: Alert):
        """Send notification for critical alerts."""
        # Get notification settings from service config
        notification_url = self.service_config.get_global_setting("alert_webhook_url")
        if not notification_url:
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(notification_url, json={
                    "title": alert.title,
                    "description": alert.description,
                    "severity": alert.severity.value,
                    "source": alert.source,
                    "created_at": alert.created_at.isoformat(),
                    "metadata": alert.metadata
                })
        except Exception as e:
            logger.error(f"Failed to send alert notification: {str(e)}")
            
    def record_request(self, method: str, endpoint: str,
                      status: int, duration: float):
        """Record HTTP request metrics."""
        # Update request counter
        self.request_counter.labels(
            method=method,
            endpoint=endpoint,
            status=str(status)
        ).inc()
        
        # Update request latency
        self.request_latency.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        # Record error if applicable
        if status >= 400:
            self.error_counter.labels(
                method=method,
                endpoint=endpoint,
                error_type=str(status)
            ).inc()
            
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        return {
            "memory": {
                "total": psutil.virtual_memory().total,
                "used": psutil.virtual_memory().used,
                "percent": psutil.virtual_memory().percent
            },
            "cpu": {
                "percent": psutil.cpu_percent(),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "disk": {
                "total": psutil.disk_usage("/").total,
                "used": psutil.disk_usage("/").used,
                "percent": psutil.disk_usage("/").percent
            },
            "network": {
                "connections": len(psutil.net_connections()),
                "io": psutil.net_io_counters()._asdict()
            }
        } 