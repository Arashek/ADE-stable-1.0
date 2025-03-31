from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import asyncio
from collections import defaultdict

@dataclass
class Metric:
    """Represents a metric with its value and metadata."""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    unit: str
    type: str

@dataclass
class Alert:
    """Represents an alert with its configuration and state."""
    name: str
    metric: str
    condition: str
    threshold: float
    window: str
    severity: str
    status: str
    last_triggered: Optional[datetime]
    notification_channels: List[str]

@dataclass
class Dashboard:
    """Represents a dashboard with its configuration."""
    name: str
    metrics: List[str]
    layout: Dict[str, Any]
    refresh_interval: int
    time_range: str

class MonitoringService:
    """Service for monitoring and alerting in the ADE platform."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.alerts: Dict[str, Alert] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.notification_channels: Dict[str, Any] = {}
        self.monitoring_tasks: List[asyncio.Task] = []
    
    async def start_monitoring(self):
        """Start the monitoring service."""
        try:
            # Start metric collection tasks
            self.monitoring_tasks.extend([
                asyncio.create_task(self._collect_metrics()),
                asyncio.create_task(self._evaluate_alerts()),
                asyncio.create_task(self._update_dashboards())
            ])
            
            self.logger.info("Monitoring service started")
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring service: {str(e)}")
            raise
    
    async def stop_monitoring(self):
        """Stop the monitoring service."""
        try:
            # Cancel all monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
            self.monitoring_tasks.clear()
            
            self.logger.info("Monitoring service stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring service: {str(e)}")
            raise
    
    async def add_metric(self, metric: Metric):
        """Add a new metric."""
        try:
            self.metrics[metric.name].append(metric)
            
            # Keep only last 24 hours of metrics
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.metrics[metric.name] = [
                m for m in self.metrics[metric.name]
                if m.timestamp > cutoff_time
            ]
            
            self.logger.debug(f"Added metric: {metric.name}")
            
        except Exception as e:
            self.logger.error(f"Error adding metric: {str(e)}")
            raise
    
    async def create_alert(self, alert: Alert):
        """Create a new alert."""
        try:
            self.alerts[alert.name] = alert
            self.logger.info(f"Created alert: {alert.name}")
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {str(e)}")
            raise
    
    async def update_alert(self, alert_name: str, updates: Dict[str, Any]):
        """Update an existing alert."""
        try:
            if alert_name not in self.alerts:
                raise ValueError(f"Alert not found: {alert_name}")
            
            alert = self.alerts[alert_name]
            for key, value in updates.items():
                setattr(alert, key, value)
            
            self.logger.info(f"Updated alert: {alert_name}")
            
        except Exception as e:
            self.logger.error(f"Error updating alert: {str(e)}")
            raise
    
    async def create_dashboard(self, dashboard: Dashboard):
        """Create a new dashboard."""
        try:
            self.dashboards[dashboard.name] = dashboard
            self.logger.info(f"Created dashboard: {dashboard.name}")
            
        except Exception as e:
            self.logger.error(f"Error creating dashboard: {str(e)}")
            raise
    
    async def get_metric_history(self,
                               metric_name: str,
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> List[Metric]:
        """Get metric history within a time range."""
        try:
            if metric_name not in self.metrics:
                return []
            
            metrics = self.metrics[metric_name]
            if start_time:
                metrics = [m for m in metrics if m.timestamp >= start_time]
            if end_time:
                metrics = [m for m in metrics if m.timestamp <= end_time]
            
            return sorted(metrics, key=lambda x: x.timestamp)
            
        except Exception as e:
            self.logger.error(f"Error getting metric history: {str(e)}")
            return []
    
    async def get_alert_status(self, alert_name: str) -> Dict[str, Any]:
        """Get current status of an alert."""
        try:
            if alert_name not in self.alerts:
                raise ValueError(f"Alert not found: {alert_name}")
            
            alert = self.alerts[alert_name]
            return {
                "name": alert.name,
                "status": alert.status,
                "last_triggered": alert.last_triggered,
                "severity": alert.severity
            }
            
        except Exception as e:
            self.logger.error(f"Error getting alert status: {str(e)}")
            raise
    
    async def get_dashboard_data(self, dashboard_name: str) -> Dict[str, Any]:
        """Get current data for a dashboard."""
        try:
            if dashboard_name not in self.dashboards:
                raise ValueError(f"Dashboard not found: {dashboard_name}")
            
            dashboard = self.dashboards[dashboard_name]
            data = {}
            
            for metric_name in dashboard.metrics:
                data[metric_name] = await self.get_metric_history(
                    metric_name,
                    start_time=datetime.now() - self._parse_time_range(dashboard.time_range)
                )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {str(e)}")
            raise
    
    async def _collect_metrics(self):
        """Collect metrics from various sources."""
        while True:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect application metrics
                await self._collect_application_metrics()
                
                # Collect custom metrics
                await self._collect_custom_metrics()
                
                await asyncio.sleep(60)  # Collect every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {str(e)}")
                await asyncio.sleep(60)
    
    async def _evaluate_alerts(self):
        """Evaluate alerts based on metric values."""
        while True:
            try:
                for alert_name, alert in self.alerts.items():
                    if alert.status == "disabled":
                        continue
                    
                    # Get metric values for the alert window
                    metrics = await self.get_metric_history(
                        alert.metric,
                        start_time=datetime.now() - self._parse_time_range(alert.window)
                    )
                    
                    if not metrics:
                        continue
                    
                    # Evaluate alert condition
                    triggered = self._evaluate_condition(
                        alert.condition,
                        [m.value for m in metrics],
                        alert.threshold
                    )
                    
                    if triggered and alert.status != "triggered":
                        await self._trigger_alert(alert)
                    elif not triggered and alert.status == "triggered":
                        await self._resolve_alert(alert)
                
                await asyncio.sleep(30)  # Evaluate every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error evaluating alerts: {str(e)}")
                await asyncio.sleep(30)
    
    async def _update_dashboards(self):
        """Update dashboard data."""
        while True:
            try:
                for dashboard_name, dashboard in self.dashboards.items():
                    # Update dashboard data
                    await self.get_dashboard_data(dashboard_name)
                
                await asyncio.sleep(dashboard.refresh_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error updating dashboards: {str(e)}")
                await asyncio.sleep(60)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        # This is a placeholder for actual system metric collection
        # In a real implementation, this would collect CPU, memory, disk, etc.
        pass
    
    async def _collect_application_metrics(self):
        """Collect application-level metrics."""
        # This is a placeholder for application metric collection
        # In a real implementation, this would collect request rates, response times, etc.
        pass
    
    async def _collect_custom_metrics(self):
        """Collect custom metrics."""
        # This is a placeholder for custom metric collection
        # In a real implementation, this would collect user-defined metrics
        pass
    
    async def _trigger_alert(self, alert: Alert):
        """Trigger an alert and send notifications."""
        try:
            alert.status = "triggered"
            alert.last_triggered = datetime.now()
            
            # Send notifications through configured channels
            for channel in alert.notification_channels:
                await self._send_notification(
                    channel=channel,
                    alert=alert,
                    message=f"Alert {alert.name} triggered: {alert.metric} {alert.condition} {alert.threshold}"
                )
            
            self.logger.info(f"Alert triggered: {alert.name}")
            
        except Exception as e:
            self.logger.error(f"Error triggering alert: {str(e)}")
    
    async def _resolve_alert(self, alert: Alert):
        """Resolve a triggered alert."""
        try:
            alert.status = "resolved"
            
            # Send resolution notifications
            for channel in alert.notification_channels:
                await self._send_notification(
                    channel=channel,
                    alert=alert,
                    message=f"Alert {alert.name} resolved"
                )
            
            self.logger.info(f"Alert resolved: {alert.name}")
            
        except Exception as e:
            self.logger.error(f"Error resolving alert: {str(e)}")
    
    async def _send_notification(self,
                               channel: str,
                               alert: Alert,
                               message: str):
        """Send notification through a specific channel."""
        try:
            if channel not in self.notification_channels:
                self.logger.warning(f"Notification channel not configured: {channel}")
                return
            
            # Send notification using the configured channel
            await self.notification_channels[channel].send(
                message=message,
                severity=alert.severity
            )
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {str(e)}")
    
    def _evaluate_condition(self,
                          condition: str,
                          values: List[float],
                          threshold: float) -> bool:
        """Evaluate an alert condition."""
        if not values:
            return False
        
        if condition == ">":
            return max(values) > threshold
        elif condition == ">=":
            return max(values) >= threshold
        elif condition == "<":
            return min(values) < threshold
        elif condition == "<=":
            return min(values) <= threshold
        elif condition == "==":
            return any(abs(v - threshold) < 0.001 for v in values)
        else:
            return False
    
    def _parse_time_range(self, time_range: str) -> timedelta:
        """Parse a time range string into a timedelta."""
        try:
            value = float(time_range[:-1])
            unit = time_range[-1]
            
            if unit == "s":
                return timedelta(seconds=value)
            elif unit == "m":
                return timedelta(minutes=value)
            elif unit == "h":
                return timedelta(hours=value)
            elif unit == "d":
                return timedelta(days=value)
            else:
                raise ValueError(f"Invalid time unit: {unit}")
                
        except Exception as e:
            self.logger.error(f"Error parsing time range: {str(e)}")
            return timedelta(hours=1)  # Default to 1 hour 