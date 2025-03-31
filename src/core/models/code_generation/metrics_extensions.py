"""
Extended metrics collection capabilities including application-specific metrics,
predictive analysis, advanced alerts, and visualization.
"""

from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from enum import Enum
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ExtendedMetricType(Enum):
    """Extended types of metrics that can be collected."""
    APPLICATION = "application"
    BUSINESS = "business"
    USER = "user"
    SECURITY = "security"
    CUSTOM = "custom"

@dataclass
class ApplicationMetric:
    """Application-specific metrics."""
    name: str
    value: Any
    timestamp: datetime
    tags: Dict[str, str]
    metadata: Dict[str, Any]
    type: ExtendedMetricType

class ExtendedMetricsCollector:
    """Collector for extended metrics types."""
    
    def __init__(self):
        self.metrics: List[ApplicationMetric] = []
        self.logger = logging.getLogger(__name__)
        
    def collect_application_metrics(self) -> List[ApplicationMetric]:
        """Collect application-specific metrics."""
        metrics = []
        
        # Response time metrics
        metrics.append(ApplicationMetric(
            name="response_time",
            value=self._measure_response_time(),
            timestamp=datetime.now(),
            tags={"component": "api"},
            metadata={"endpoint": "/api/v1/endpoint"},
            type=ExtendedMetricType.APPLICATION
        ))
        
        # Error rate metrics
        metrics.append(ApplicationMetric(
            name="error_rate",
            value=self._calculate_error_rate(),
            timestamp=datetime.now(),
            tags={"component": "api"},
            metadata={"endpoint": "/api/v1/endpoint"},
            type=ExtendedMetricType.APPLICATION
        ))
        
        # Cache hit rate
        metrics.append(ApplicationMetric(
            name="cache_hit_rate",
            value=self._calculate_cache_hit_rate(),
            timestamp=datetime.now(),
            tags={"component": "cache"},
            metadata={"cache_type": "redis"},
            type=ExtendedMetricType.APPLICATION
        ))
        
        return metrics
        
    def collect_business_metrics(self) -> List[ApplicationMetric]:
        """Collect business-related metrics."""
        metrics = []
        
        # User engagement metrics
        metrics.append(ApplicationMetric(
            name="user_engagement",
            value=self._calculate_user_engagement(),
            timestamp=datetime.now(),
            tags={"component": "user"},
            metadata={"period": "daily"},
            type=ExtendedMetricType.BUSINESS
        ))
        
        # Revenue metrics
        metrics.append(ApplicationMetric(
            name="revenue",
            value=self._calculate_revenue(),
            timestamp=datetime.now(),
            tags={"component": "business"},
            metadata={"period": "daily"},
            type=ExtendedMetricType.BUSINESS
        ))
        
        # Customer satisfaction
        metrics.append(ApplicationMetric(
            name="customer_satisfaction",
            value=self._calculate_customer_satisfaction(),
            timestamp=datetime.now(),
            tags={"component": "customer"},
            metadata={"period": "daily"},
            type=ExtendedMetricType.BUSINESS
        ))
        
        return metrics
        
    def collect_user_metrics(self) -> List[ApplicationMetric]:
        """Collect user-related metrics."""
        metrics = []
        
        # Active users
        metrics.append(ApplicationMetric(
            name="active_users",
            value=self._count_active_users(),
            timestamp=datetime.now(),
            tags={"component": "user"},
            metadata={"period": "hourly"},
            type=ExtendedMetricType.USER
        ))
        
        # User retention
        metrics.append(ApplicationMetric(
            name="user_retention",
            value=self._calculate_user_retention(),
            timestamp=datetime.now(),
            tags={"component": "user"},
            metadata={"period": "daily"},
            type=ExtendedMetricType.USER
        ))
        
        # User session duration
        metrics.append(ApplicationMetric(
            name="session_duration",
            value=self._calculate_session_duration(),
            timestamp=datetime.now(),
            tags={"component": "user"},
            metadata={"period": "daily"},
            type=ExtendedMetricType.USER
        ))
        
        return metrics
        
    def collect_security_metrics(self) -> List[ApplicationMetric]:
        """Collect security-related metrics."""
        metrics = []
        
        # Failed login attempts
        metrics.append(ApplicationMetric(
            name="failed_logins",
            value=self._count_failed_logins(),
            timestamp=datetime.now(),
            tags={"component": "security"},
            metadata={"period": "hourly"},
            type=ExtendedMetricType.SECURITY
        ))
        
        # Security incidents
        metrics.append(ApplicationMetric(
            name="security_incidents",
            value=self._count_security_incidents(),
            timestamp=datetime.now(),
            tags={"component": "security"},
            metadata={"period": "daily"},
            type=ExtendedMetricType.SECURITY
        ))
        
        # API abuse attempts
        metrics.append(ApplicationMetric(
            name="api_abuse",
            value=self._count_api_abuse(),
            timestamp=datetime.now(),
            tags={"component": "security"},
            metadata={"period": "hourly"},
            type=ExtendedMetricType.SECURITY
        ))
        
        return metrics
        
    def _measure_response_time(self) -> float:
        """Measure API response time."""
        # Implementation would measure actual API response time
        return 0.1
        
    def _calculate_error_rate(self) -> float:
        """Calculate API error rate."""
        # Implementation would calculate actual error rate
        return 0.01
        
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        # Implementation would calculate actual cache hit rate
        return 0.8
        
    def _calculate_user_engagement(self) -> float:
        """Calculate user engagement score."""
        # Implementation would calculate actual engagement score
        return 0.75
        
    def _calculate_revenue(self) -> float:
        """Calculate daily revenue."""
        # Implementation would calculate actual revenue
        return 1000.0
        
    def _calculate_customer_satisfaction(self) -> float:
        """Calculate customer satisfaction score."""
        # Implementation would calculate actual satisfaction score
        return 4.5
        
    def _count_active_users(self) -> int:
        """Count active users."""
        # Implementation would count actual active users
        return 1000
        
    def _calculate_user_retention(self) -> float:
        """Calculate user retention rate."""
        # Implementation would calculate actual retention rate
        return 0.85
        
    def _calculate_session_duration(self) -> float:
        """Calculate average session duration."""
        # Implementation would calculate actual session duration
        return 15.0
        
    def _count_failed_logins(self) -> int:
        """Count failed login attempts."""
        # Implementation would count actual failed logins
        return 5
        
    def _count_security_incidents(self) -> int:
        """Count security incidents."""
        # Implementation would count actual security incidents
        return 2
        
    def _count_api_abuse(self) -> int:
        """Count API abuse attempts."""
        # Implementation would count actual API abuse attempts
        return 10

class PredictiveAnalyzer:
    """Analyzer for predictive analysis and anomaly detection."""
    
    def __init__(self, collector: ExtendedMetricsCollector):
        self.collector = collector
        self.model = IsolationForest(contamination=0.1)
        self.scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)
        
    def predict_trends(self, metric_name: str, 
                      time_window: timedelta = timedelta(days=7)) -> Dict[str, Any]:
        """Predict future trends for a metric."""
        # Get historical data
        historical_data = self._get_historical_data(metric_name, time_window)
        
        # Prepare data for prediction
        X = np.array(historical_data).reshape(-1, 1)
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit model and predict
        self.model.fit(X_scaled)
        predictions = self.model.predict(X_scaled)
        
        # Calculate trend
        trend = self._calculate_trend(historical_data)
        
        # Calculate confidence
        confidence = self._calculate_confidence(predictions)
        
        return {
            "trend": trend,
            "confidence": confidence,
            "predictions": predictions.tolist(),
            "historical_data": historical_data
        }
        
    def detect_anomalies(self, metric_name: str, 
                        time_window: timedelta = timedelta(days=7)) -> List[Dict[str, Any]]:
        """Detect anomalies in metric data."""
        # Get historical data
        historical_data = self._get_historical_data(metric_name, time_window)
        
        # Prepare data for anomaly detection
        X = np.array(historical_data).reshape(-1, 1)
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit model and predict
        self.model.fit(X_scaled)
        predictions = self.model.predict(X_scaled)
        
        # Find anomalies
        anomalies = []
        for i, pred in enumerate(predictions):
            if pred == -1:  # Anomaly detected
                anomalies.append({
                    "timestamp": datetime.now() - time_window + timedelta(hours=i),
                    "value": historical_data[i],
                    "severity": self._calculate_anomaly_severity(historical_data[i])
                })
                
        return anomalies
        
    def _get_historical_data(self, metric_name: str, 
                           time_window: timedelta) -> List[float]:
        """Get historical data for a metric."""
        # Implementation would get actual historical data
        return [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        
    def _calculate_trend(self, data: List[float]) -> str:
        """Calculate trend direction from data."""
        if len(data) < 2:
            return "insufficient_data"
            
        first_half = sum(data[:len(data)//2]) / (len(data)//2)
        second_half = sum(data[len(data)//2:]) / (len(data) - len(data)//2)
        
        if second_half > first_half * 1.1:
            return "increasing"
        elif second_half < first_half * 0.9:
            return "decreasing"
        else:
            return "stable"
            
    def _calculate_confidence(self, predictions: np.ndarray) -> float:
        """Calculate prediction confidence."""
        return 0.85  # Implementation would calculate actual confidence
        
    def _calculate_anomaly_severity(self, value: float) -> str:
        """Calculate anomaly severity."""
        if value > 2.0:
            return "high"
        elif value > 1.5:
            return "medium"
        else:
            return "low"

class AdvancedAlertManager:
    """Manager for advanced alert conditions."""
    
    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
        self.alert_rules: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        
    def add_rate_of_change_alert(self, metric_name: str, threshold: float,
                               time_window: timedelta) -> None:
        """Add a rate of change alert rule."""
        self.alert_rules.append({
            "type": "rate_of_change",
            "metric": metric_name,
            "threshold": threshold,
            "time_window": time_window
        })
        
    def add_composite_alert(self, conditions: List[Dict[str, Any]], 
                          operator: str = "AND") -> None:
        """Add a composite alert rule."""
        self.alert_rules.append({
            "type": "composite",
            "conditions": conditions,
            "operator": operator
        })
        
    def add_threshold_alert(self, metric_name: str, threshold: float,
                          comparison: str = ">") -> None:
        """Add a threshold alert rule."""
        self.alert_rules.append({
            "type": "threshold",
            "metric": metric_name,
            "threshold": threshold,
            "comparison": comparison
        })
        
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check all alert conditions."""
        new_alerts = []
        
        for rule in self.alert_rules:
            if rule["type"] == "rate_of_change":
                alert = self._check_rate_of_change(rule, metrics)
                if alert:
                    new_alerts.append(alert)
                    
            elif rule["type"] == "composite":
                alert = self._check_composite(rule, metrics)
                if alert:
                    new_alerts.append(alert)
                    
            elif rule["type"] == "threshold":
                alert = self._check_threshold(rule, metrics)
                if alert:
                    new_alerts.append(alert)
                    
        self.alerts.extend(new_alerts)
        return new_alerts
        
    def _check_rate_of_change(self, rule: Dict[str, Any], 
                            metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check rate of change alert condition."""
        # Implementation would check actual rate of change
        return None
        
    def _check_composite(self, rule: Dict[str, Any], 
                        metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check composite alert condition."""
        # Implementation would check actual composite conditions
        return None
        
    def _check_threshold(self, rule: Dict[str, Any], 
                        metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check threshold alert condition."""
        # Implementation would check actual threshold
        return None

class MetricsVisualizer:
    """Visualizer for metrics data."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def create_time_series_plot(self, data: List[Dict[str, Any]], 
                              metric_name: str) -> go.Figure:
        """Create a time series plot for a metric."""
        fig = go.Figure()
        
        # Extract time and values
        times = [d["timestamp"] for d in data]
        values = [d["value"] for d in data]
        
        # Add trace
        fig.add_trace(go.Scatter(
            x=times,
            y=values,
            mode="lines+markers",
            name=metric_name
        ))
        
        # Update layout
        fig.update_layout(
            title=f"Time Series Plot for {metric_name}",
            xaxis_title="Time",
            yaxis_title="Value",
            showlegend=True
        )
        
        return fig
        
    def create_heatmap(self, data: List[Dict[str, Any]], 
                      x_metric: str, y_metric: str) -> go.Figure:
        """Create a heatmap for two metrics."""
        fig = go.Figure()
        
        # Extract values
        x_values = [d[x_metric] for d in data]
        y_values = [d[y_metric] for d in data]
        
        # Create heatmap
        fig.add_trace(go.Heatmap(
            z=np.corrcoef(x_values, y_values),
            x=[x_metric, y_metric],
            y=[x_metric, y_metric],
            colorscale="RdBu"
        ))
        
        # Update layout
        fig.update_layout(
            title=f"Heatmap: {x_metric} vs {y_metric}",
            xaxis_title=x_metric,
            yaxis_title=y_metric
        )
        
        return fig
        
    def create_dashboard(self, metrics: Dict[str, List[Dict[str, Any]]]) -> go.Figure:
        """Create a dashboard with multiple plots."""
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Time Series", "Heatmap", "Distribution", "Box Plot")
        )
        
        # Add time series plot
        for metric_name, data in metrics.items():
            times = [d["timestamp"] for d in data]
            values = [d["value"] for d in data]
            fig.add_trace(
                go.Scatter(x=times, y=values, name=metric_name),
                row=1, col=1
            )
            
        # Add heatmap
        values = np.array([[d["value"] for d in data] for data in metrics.values()])
        fig.add_trace(
            go.Heatmap(z=np.corrcoef(values), colorscale="RdBu"),
            row=1, col=2
        )
        
        # Add distribution plot
        for metric_name, data in metrics.items():
            values = [d["value"] for d in data]
            fig.add_trace(
                go.Histogram(x=values, name=metric_name),
                row=2, col=1
            )
            
        # Add box plot
        for metric_name, data in metrics.items():
            values = [d["value"] for d in data]
            fig.add_trace(
                go.Box(y=values, name=metric_name),
                row=2, col=2
            )
            
        # Update layout
        fig.update_layout(
            height=800,
            width=1200,
            title_text="Metrics Dashboard",
            showlegend=True
        )
        
        return fig
        
    def save_plot(self, fig: go.Figure, filename: str) -> None:
        """Save a plot to a file."""
        fig.write_html(filename)
        
    def export_dashboard(self, dashboard: go.Figure, 
                        filename: str, format: str = "html") -> None:
        """Export a dashboard to a file."""
        if format == "html":
            dashboard.write_html(filename)
        elif format == "json":
            dashboard_json = dashboard.to_json()
            with open(filename, "w") as f:
                json.dump(dashboard_json, f)
        else:
            raise ValueError(f"Unsupported format: {format}") 