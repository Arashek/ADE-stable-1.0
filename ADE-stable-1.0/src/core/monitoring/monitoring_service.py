from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import json
import time
import psutil
import prometheus_client as prom
from prometheus_client import Counter, Gauge, Histogram, Summary
import redis
import aiohttp
import asyncio
import pandas as pd
import numpy as np
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
    type: str
    severity: AlertSeverity
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class MetricThreshold:
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    comparison: str  # "gt", "lt", "eq"
    window_size: int  # seconds
    aggregation: str  # "avg", "max", "min"

class MonitoringService:
    """Centralized monitoring service with comprehensive analytics and health monitoring."""
    
    def __init__(self, redis_url: str, prometheus_url: str,
                 service_config: ServiceConfig):
        self.redis_client = redis.from_url(redis_url)
        self.prometheus_url = prometheus_url
        self.service_config = service_config
        
        # Initialize Prometheus metrics
        self._initialize_prometheus_metrics()
        
        # Initialize alert thresholds
        self.alert_thresholds = self._initialize_alert_thresholds()
        
        # Initialize monitoring state
        self.alerts: List[Alert] = []
        self.metric_history: Dict[str, List[Dict[str, Any]]] = {}
        self.health_checks: Dict[str, Dict[str, Any]] = {}
        self.performance_baselines: Dict[str, Dict[str, float]] = {}
        
        # Start monitoring tasks
        self._start_monitoring()
        
    def _initialize_prometheus_metrics(self):
        """Initialize all Prometheus metrics."""
        # System metrics
        self.system_metrics = {
            "cpu_usage": Gauge("system_cpu_usage_percent", "CPU usage percentage", ["cpu"]),
            "memory_usage": Gauge("system_memory_usage_bytes", "Memory usage in bytes"),
            "disk_usage": Gauge("system_disk_usage_bytes", "Disk usage in bytes", ["mountpoint"]),
            "network_io": Counter("system_network_io_bytes", "Network I/O in bytes", ["direction"]),
            "process_count": Gauge("system_process_count", "Number of processes")
        }
        
        # Application metrics
        self.app_metrics = {
            "request_count": Counter("app_requests_total", "Total requests", ["endpoint", "method"]),
            "request_latency": Histogram("app_request_duration_seconds", "Request duration", ["endpoint"]),
            "error_count": Counter("app_errors_total", "Total errors", ["endpoint", "error_type"]),
            "active_users": Gauge("app_active_users", "Number of active users"),
            "session_count": Gauge("app_session_count", "Number of active sessions")
        }
        
        # Business metrics
        self.business_metrics = {
            "transaction_count": Counter("business_transactions_total", "Total transactions", ["type"]),
            "transaction_value": Counter("business_transaction_value", "Transaction value", ["type"]),
            "user_actions": Counter("business_user_actions_total", "User actions", ["action_type"]),
            "conversion_rate": Gauge("business_conversion_rate", "Conversion rate", ["funnel_stage"])
        }
        
        # Custom metrics
        self.custom_metrics = {}
        
    def _initialize_alert_thresholds(self) -> Dict[str, MetricThreshold]:
        """Initialize alert thresholds for various metrics."""
        return {
            "cpu_usage": MetricThreshold(
                metric_name="system_cpu_usage_percent",
                warning_threshold=80.0,
                critical_threshold=90.0,
                comparison="gt",
                window_size=300,
                aggregation="avg"
            ),
            "memory_usage": MetricThreshold(
                metric_name="system_memory_usage_bytes",
                warning_threshold=0.8,
                critical_threshold=0.9,
                comparison="gt",
                window_size=300,
                aggregation="avg"
            ),
            "request_latency": MetricThreshold(
                metric_name="app_request_duration_seconds",
                warning_threshold=1.0,
                critical_threshold=2.0,
                comparison="gt",
                window_size=60,
                aggregation="p95"
            ),
            "error_rate": MetricThreshold(
                metric_name="app_errors_total",
                warning_threshold=0.05,
                critical_threshold=0.1,
                comparison="gt",
                window_size=300,
                aggregation="rate"
            )
        }
        
    async def _start_monitoring(self):
        """Start all monitoring tasks."""
        tasks = [
            self._collect_system_metrics(),
            self._collect_application_metrics(),
            self._collect_business_metrics(),
            self._check_health(),
            self._analyze_metrics(),
            self._check_alerts()
        ]
        
        await asyncio.gather(*tasks)
        
    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        while True:
            try:
                # CPU metrics
                for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
                    self.system_metrics["cpu_usage"].labels(cpu=f"cpu{i}").set(percentage)
                    
                # Memory metrics
                memory = psutil.virtual_memory()
                self.system_metrics["memory_usage"].set(memory.used)
                
                # Disk metrics
                for partition in psutil.disk_partitions():
                    usage = psutil.disk_usage(partition.mountpoint)
                    self.system_metrics["disk_usage"].labels(mountpoint=partition.mountpoint).set(usage.used)
                    
                # Network metrics
                net_io = psutil.net_io_counters()
                self.system_metrics["network_io"].labels(direction="sent").inc(net_io.bytes_sent)
                self.system_metrics["network_io"].labels(direction="recv").inc(net_io.bytes_recv)
                
                # Process metrics
                self.system_metrics["process_count"].set(len(psutil.pids()))
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {str(e)}")
                await asyncio.sleep(1)
                
    async def _collect_application_metrics(self):
        """Collect application-level metrics."""
        while True:
            try:
                # Request metrics
                # This should be implemented based on your application's needs
                pass
                
                # User metrics
                active_users = await self._get_active_users()
                self.app_metrics["active_users"].set(active_users)
                
                # Session metrics
                session_count = await self._get_session_count()
                self.app_metrics["session_count"].set(session_count)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error collecting application metrics: {str(e)}")
                await asyncio.sleep(1)
                
    async def _collect_business_metrics(self):
        """Collect business-level metrics."""
        while True:
            try:
                # Transaction metrics
                # This should be implemented based on your business needs
                pass
                
                # User action metrics
                # This should be implemented based on your business needs
                pass
                
                # Conversion metrics
                # This should be implemented based on your business needs
                pass
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error collecting business metrics: {str(e)}")
                await asyncio.sleep(1)
                
    async def _check_health(self):
        """Perform health checks on system components."""
        while True:
            try:
                # Check system health
                system_health = await self._check_system_health()
                self.health_checks["system"] = system_health
                
                # Check application health
                app_health = await self._check_application_health()
                self.health_checks["application"] = app_health
                
                # Check database health
                db_health = await self._check_database_health()
                self.health_checks["database"] = db_health
                
                # Check external services
                external_health = await self._check_external_services()
                self.health_checks["external"] = external_health
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error checking health: {str(e)}")
                await asyncio.sleep(30)
                
    async def _analyze_metrics(self):
        """Analyze collected metrics for trends and anomalies."""
        while True:
            try:
                # Analyze system metrics
                system_analysis = self._analyze_system_metrics()
                
                # Analyze application metrics
                app_analysis = self._analyze_application_metrics()
                
                # Analyze business metrics
                business_analysis = self._analyze_business_metrics()
                
                # Store analysis results
                self._store_analysis_results({
                    "system": system_analysis,
                    "application": app_analysis,
                    "business": business_analysis
                })
                
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error analyzing metrics: {str(e)}")
                await asyncio.sleep(60)
                
    async def _check_alerts(self):
        """Check for alert conditions and create alerts."""
        while True:
            try:
                for metric_name, threshold in self.alert_thresholds.items():
                    value = await self._get_metric_value(threshold)
                    if self._check_threshold(value, threshold):
                        await self._create_alert(metric_name, value, threshold)
                        
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error checking alerts: {str(e)}")
                await asyncio.sleep(10)
                
    def _analyze_system_metrics(self) -> Dict[str, Any]:
        """Analyze system metrics for trends and anomalies."""
        analysis = {}
        
        try:
            # Get recent metrics
            cpu_metrics = self._get_recent_metrics("system_cpu_usage_percent")
            memory_metrics = self._get_recent_metrics("system_memory_usage_bytes")
            disk_metrics = self._get_recent_metrics("system_disk_usage_bytes")
            
            # Analyze CPU usage
            if cpu_metrics:
                analysis["cpu"] = {
                    "trend": self._calculate_trend(cpu_metrics),
                    "anomalies": self._detect_anomalies(cpu_metrics),
                    "forecast": self._forecast_metric(cpu_metrics)
                }
                
            # Analyze memory usage
            if memory_metrics:
                analysis["memory"] = {
                    "trend": self._calculate_trend(memory_metrics),
                    "anomalies": self._detect_anomalies(memory_metrics),
                    "forecast": self._forecast_metric(memory_metrics)
                }
                
            # Analyze disk usage
            if disk_metrics:
                analysis["disk"] = {
                    "trend": self._calculate_trend(disk_metrics),
                    "anomalies": self._detect_anomalies(disk_metrics),
                    "forecast": self._forecast_metric(disk_metrics)
                }
                
        except Exception as e:
            logger.error(f"Error analyzing system metrics: {str(e)}")
            
        return analysis
        
    def _analyze_application_metrics(self) -> Dict[str, Any]:
        """Analyze application metrics for trends and anomalies."""
        analysis = {}
        
        try:
            # Get recent metrics
            request_metrics = self._get_recent_metrics("app_request_duration_seconds")
            error_metrics = self._get_recent_metrics("app_errors_total")
            
            # Analyze request latency
            if request_metrics:
                analysis["request_latency"] = {
                    "trend": self._calculate_trend(request_metrics),
                    "anomalies": self._detect_anomalies(request_metrics),
                    "forecast": self._forecast_metric(request_metrics)
                }
                
            # Analyze error rates
            if error_metrics:
                analysis["error_rate"] = {
                    "trend": self._calculate_trend(error_metrics),
                    "anomalies": self._detect_anomalies(error_metrics),
                    "forecast": self._forecast_metric(error_metrics)
                }
                
        except Exception as e:
            logger.error(f"Error analyzing application metrics: {str(e)}")
            
        return analysis
        
    def _analyze_business_metrics(self) -> Dict[str, Any]:
        """Analyze business metrics for trends and anomalies."""
        analysis = {}
        
        try:
            # Get recent metrics
            transaction_metrics = self._get_recent_metrics("business_transactions_total")
            conversion_metrics = self._get_recent_metrics("business_conversion_rate")
            
            # Analyze transaction volume
            if transaction_metrics:
                analysis["transactions"] = {
                    "trend": self._calculate_trend(transaction_metrics),
                    "anomalies": self._detect_anomalies(transaction_metrics),
                    "forecast": self._forecast_metric(transaction_metrics)
                }
                
            # Analyze conversion rates
            if conversion_metrics:
                analysis["conversion"] = {
                    "trend": self._calculate_trend(conversion_metrics),
                    "anomalies": self._detect_anomalies(conversion_metrics),
                    "forecast": self._forecast_metric(conversion_metrics)
                }
                
        except Exception as e:
            logger.error(f"Error analyzing business metrics: {str(e)}")
            
        return analysis
        
    def _calculate_trend(self, metrics: List[float]) -> str:
        """Calculate trend direction from a list of metrics."""
        if len(metrics) < 2:
            return "insufficient_data"
            
        first_half = np.mean(metrics[:len(metrics)//2])
        second_half = np.mean(metrics[len(metrics)//2:])
        
        if second_half > first_half * 1.1:
            return "increasing"
        elif second_half < first_half * 0.9:
            return "decreasing"
        else:
            return "stable"
            
    def _detect_anomalies(self, metrics: List[float]) -> List[Dict[str, Any]]:
        """Detect anomalies in a list of metrics using statistical methods."""
        if len(metrics) < 10:
            return []
            
        anomalies = []
        mean = np.mean(metrics)
        std = np.std(metrics)
        
        for i, value in enumerate(metrics):
            if abs(value - mean) > 3 * std:  # 3 standard deviations
                anomalies.append({
                    "index": i,
                    "value": value,
                    "deviation": abs(value - mean) / std
                })
                
        return anomalies
        
    def _forecast_metric(self, metrics: List[float]) -> Dict[str, float]:
        """Forecast future values of a metric using simple linear regression."""
        if len(metrics) < 10:
            return {"forecast": None, "confidence": 0.0}
            
        x = np.arange(len(metrics))
        y = np.array(metrics)
        
        # Simple linear regression
        slope, intercept = np.polyfit(x, y, 1)
        
        # Forecast next 5 values
        next_x = np.arange(len(metrics), len(metrics) + 5)
        forecast = slope * next_x + intercept
        
        # Calculate confidence (R-squared)
        y_pred = slope * x + intercept
        r_squared = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
        
        return {
            "forecast": forecast.tolist(),
            "confidence": float(r_squared)
        }
        
    async def _create_alert(self, metric_name: str, value: float, threshold: MetricThreshold):
        """Create a new alert based on metric value and threshold."""
        severity = self._determine_alert_severity(value, threshold)
        
        alert = Alert(
            id=str(uuid.uuid4()),
            type=metric_name,
            severity=severity,
            message=f"{metric_name} threshold exceeded",
            details={
                "value": value,
                "threshold": threshold.__dict__,
                "timestamp": datetime.now().isoformat()
            },
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        await self._notify_alert(alert)
        
    def _determine_alert_severity(self, value: float, threshold: MetricThreshold) -> AlertSeverity:
        """Determine alert severity based on metric value and threshold."""
        if threshold.comparison == "gt":
            if value > threshold.critical_threshold:
                return AlertSeverity.CRITICAL
            elif value > threshold.warning_threshold:
                return AlertSeverity.WARNING
        elif threshold.comparison == "lt":
            if value < threshold.critical_threshold:
                return AlertSeverity.CRITICAL
            elif value < threshold.warning_threshold:
                return AlertSeverity.WARNING
                
        return AlertSeverity.INFO
        
    async def _notify_alert(self, alert: Alert):
        """Send alert notification through configured channels."""
        # Implement notification logic (email, SMS, Slack, etc.)
        pass
        
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected metrics."""
        try:
            summary = {
                "system": await self._get_system_metrics_summary(),
                "application": await self._get_application_metrics_summary(),
                "business": await self._get_business_metrics_summary(),
                "health": self.health_checks,
                "alerts": [alert.__dict__ for alert in self.alerts if not alert.resolved]
            }
            return summary
            
        except Exception as e:
            logger.error(f"Error getting metrics summary: {str(e)}")
            return {}
            
    async def get_metric_history(self, metric_name: str, 
                                start_time: datetime, 
                                end_time: datetime) -> List[Dict[str, Any]]:
        """Get historical data for a specific metric."""
        try:
            # Get data from Redis
            data = await self.redis_client.zrangebyscore(
                f"metric:{metric_name}",
                start_time.timestamp(),
                end_time.timestamp()
            )
            
            # Parse and return data
            return [json.loads(d) for d in data]
            
        except Exception as e:
            logger.error(f"Error getting metric history: {str(e)}")
            return []
            
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current health status of all components."""
        return self.health_checks
        
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active (unresolved) alerts."""
        return [alert.__dict__ for alert in self.alerts if not alert.resolved]
        
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False
        
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolution_time = datetime.now()
                return True
        return False 