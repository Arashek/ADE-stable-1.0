"""
Extended metrics collection capabilities with additional metric types,
enhanced ML models, more visualization types, and advanced alert conditions.
"""

from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from enum import Enum
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from scipy import stats

class ExtendedMetricType2(Enum):
    """Additional types of metrics that can be collected."""
    DATABASE = "database"
    NETWORK = "network"
    INFRASTRUCTURE = "infrastructure"
    CUSTOM = "custom"

@dataclass
class DatabaseMetric:
    """Database-specific metrics."""
    name: str
    value: Any
    timestamp: datetime
    tags: Dict[str, str]
    metadata: Dict[str, Any]
    type: ExtendedMetricType2

class ExtendedMetricsCollector2:
    """Collector for additional metric types."""
    
    def __init__(self):
        self.metrics: List[DatabaseMetric] = []
        self.logger = logging.getLogger(__name__)
        
    def collect_database_metrics(self) -> List[DatabaseMetric]:
        """Collect database-specific metrics."""
        metrics = []
        
        # Query performance metrics
        metrics.append(DatabaseMetric(
            name="query_execution_time",
            value=self._measure_query_execution_time(),
            timestamp=datetime.now(),
            tags={"component": "database"},
            metadata={"query_type": "select"},
            type=ExtendedMetricType2.DATABASE
        ))
        
        # Connection pool metrics
        metrics.append(DatabaseMetric(
            name="connection_pool_usage",
            value=self._calculate_connection_pool_usage(),
            timestamp=datetime.now(),
            tags={"component": "database"},
            metadata={"pool_name": "main_pool"},
            type=ExtendedMetricType2.DATABASE
        ))
        
        # Transaction metrics
        metrics.append(DatabaseMetric(
            name="transaction_count",
            value=self._count_transactions(),
            timestamp=datetime.now(),
            tags={"component": "database"},
            metadata={"transaction_type": "all"},
            type=ExtendedMetricType2.DATABASE
        ))
        
        return metrics
        
    def collect_network_metrics(self) -> List[DatabaseMetric]:
        """Collect network-related metrics."""
        metrics = []
        
        # Latency metrics
        metrics.append(DatabaseMetric(
            name="network_latency",
            value=self._measure_network_latency(),
            timestamp=datetime.now(),
            tags={"component": "network"},
            metadata={"target": "api_endpoint"},
            type=ExtendedMetricType2.NETWORK
        ))
        
        # Bandwidth metrics
        metrics.append(DatabaseMetric(
            name="bandwidth_usage",
            value=self._calculate_bandwidth_usage(),
            timestamp=datetime.now(),
            tags={"component": "network"},
            metadata={"direction": "outbound"},
            type=ExtendedMetricType2.NETWORK
        ))
        
        # Connection metrics
        metrics.append(DatabaseMetric(
            name="active_connections",
            value=self._count_active_connections(),
            timestamp=datetime.now(),
            tags={"component": "network"},
            metadata={"protocol": "tcp"},
            type=ExtendedMetricType2.NETWORK
        ))
        
        return metrics
        
    def collect_infrastructure_metrics(self) -> List[DatabaseMetric]:
        """Collect infrastructure-related metrics."""
        metrics = []
        
        # Container metrics
        metrics.append(DatabaseMetric(
            name="container_cpu_usage",
            value=self._measure_container_cpu_usage(),
            timestamp=datetime.now(),
            tags={"component": "container"},
            metadata={"container_id": "app_container"},
            type=ExtendedMetricType2.INFRASTRUCTURE
        ))
        
        # Kubernetes metrics
        metrics.append(DatabaseMetric(
            name="pod_count",
            value=self._count_pods(),
            timestamp=datetime.now(),
            tags={"component": "kubernetes"},
            metadata={"namespace": "production"},
            type=ExtendedMetricType2.INFRASTRUCTURE
        ))
        
        # Storage metrics
        metrics.append(DatabaseMetric(
            name="disk_usage",
            value=self._calculate_disk_usage(),
            timestamp=datetime.now(),
            tags={"component": "storage"},
            metadata={"mount_point": "/data"},
            type=ExtendedMetricType2.INFRASTRUCTURE
        ))
        
        return metrics
        
    def _measure_query_execution_time(self) -> float:
        """Measure database query execution time."""
        # Implementation would measure actual query execution time
        return 0.05
        
    def _calculate_connection_pool_usage(self) -> float:
        """Calculate database connection pool usage."""
        # Implementation would calculate actual pool usage
        return 0.6
        
    def _count_transactions(self) -> int:
        """Count database transactions."""
        # Implementation would count actual transactions
        return 1000
        
    def _measure_network_latency(self) -> float:
        """Measure network latency."""
        # Implementation would measure actual network latency
        return 0.1
        
    def _calculate_bandwidth_usage(self) -> float:
        """Calculate network bandwidth usage."""
        # Implementation would calculate actual bandwidth usage
        return 500.0
        
    def _count_active_connections(self) -> int:
        """Count active network connections."""
        # Implementation would count actual connections
        return 100
        
    def _measure_container_cpu_usage(self) -> float:
        """Measure container CPU usage."""
        # Implementation would measure actual container CPU usage
        return 0.7
        
    def _count_pods(self) -> int:
        """Count Kubernetes pods."""
        # Implementation would count actual pods
        return 5
        
    def _calculate_disk_usage(self) -> float:
        """Calculate disk usage."""
        # Implementation would calculate actual disk usage
        return 0.8

class EnhancedPredictiveAnalyzer:
    """Enhanced analyzer with additional ML models."""
    
    def __init__(self, collector: ExtendedMetricsCollector2):
        self.collector = collector
        self.isolation_forest = IsolationForest(contamination=0.1)
        self.random_forest = RandomForestRegressor()
        self.dbscan = DBSCAN(eps=0.3, min_samples=2)
        self.pca = PCA(n_components=2)
        self.scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)
        
    def predict_trends_advanced(self, metric_name: str, 
                              time_window: timedelta = timedelta(days=7)) -> Dict[str, Any]:
        """Predict future trends using multiple ML models."""
        # Get historical data
        historical_data = self._get_historical_data(metric_name, time_window)
        
        # Prepare data
        X = np.array(historical_data).reshape(-1, 1)
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit and predict with Random Forest
        self.random_forest.fit(X_scaled[:-1], X_scaled[1:].ravel())
        rf_predictions = self.random_forest.predict(X_scaled)
        
        # Perform PCA for dimensionality reduction
        X_pca = self.pca.fit_transform(X_scaled)
        
        # Cluster data with DBSCAN
        clusters = self.dbscan.fit_predict(X_pca)
        
        # Calculate trend
        trend = self._calculate_trend(historical_data)
        
        # Calculate confidence
        confidence = self._calculate_confidence(rf_predictions)
        
        return {
            "trend": trend,
            "confidence": confidence,
            "predictions": rf_predictions.tolist(),
            "historical_data": historical_data,
            "clusters": clusters.tolist(),
            "pca_components": self.pca.components_.tolist()
        }
        
    def detect_anomalies_advanced(self, metric_name: str, 
                                time_window: timedelta = timedelta(days=7)) -> List[Dict[str, Any]]:
        """Detect anomalies using multiple ML models."""
        # Get historical data
        historical_data = self._get_historical_data(metric_name, time_window)
        
        # Prepare data
        X = np.array(historical_data).reshape(-1, 1)
        X_scaled = self.scaler.fit_transform(X)
        
        # Detect anomalies with Isolation Forest
        self.isolation_forest.fit(X_scaled)
        if_predictions = self.isolation_forest.predict(X_scaled)
        
        # Perform PCA
        X_pca = self.pca.fit_transform(X_scaled)
        
        # Detect clusters with DBSCAN
        clusters = self.dbscan.fit_predict(X_pca)
        
        # Find anomalies
        anomalies = []
        for i, (if_pred, cluster) in enumerate(zip(if_predictions, clusters)):
            if if_pred == -1 or cluster == -1:  # Anomaly detected
                anomalies.append({
                    "timestamp": datetime.now() - time_window + timedelta(hours=i),
                    "value": historical_data[i],
                    "severity": self._calculate_anomaly_severity(historical_data[i]),
                    "detection_method": "isolation_forest" if if_pred == -1 else "dbscan",
                    "cluster": int(cluster)
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

class AdvancedAlertManager2:
    """Enhanced manager for advanced alert conditions."""
    
    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
        self.alert_rules: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        
    def add_pattern_matching_alert(self, metric_name: str, pattern: str,
                                 time_window: timedelta) -> None:
        """Add a pattern matching alert rule."""
        self.alert_rules.append({
            "type": "pattern_matching",
            "metric": metric_name,
            "pattern": pattern,
            "time_window": time_window
        })
        
    def add_statistical_alert(self, metric_name: str, threshold: float,
                            method: str = "zscore") -> None:
        """Add a statistical analysis alert rule."""
        self.alert_rules.append({
            "type": "statistical",
            "metric": metric_name,
            "threshold": threshold,
            "method": method
        })
        
    def add_correlation_alert(self, metric1: str, metric2: str,
                            threshold: float) -> None:
        """Add a correlation-based alert rule."""
        self.alert_rules.append({
            "type": "correlation",
            "metric1": metric1,
            "metric2": metric2,
            "threshold": threshold
        })
        
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check all alert conditions."""
        new_alerts = []
        
        for rule in self.alert_rules:
            if rule["type"] == "pattern_matching":
                alert = self._check_pattern_matching(rule, metrics)
                if alert:
                    new_alerts.append(alert)
                    
            elif rule["type"] == "statistical":
                alert = self._check_statistical(rule, metrics)
                if alert:
                    new_alerts.append(alert)
                    
            elif rule["type"] == "correlation":
                alert = self._check_correlation(rule, metrics)
                if alert:
                    new_alerts.append(alert)
                    
        self.alerts.extend(new_alerts)
        return new_alerts
        
    def _check_pattern_matching(self, rule: Dict[str, Any], 
                              metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check pattern matching alert condition."""
        # Implementation would check actual pattern matching
        return None
        
    def _check_statistical(self, rule: Dict[str, Any], 
                          metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check statistical alert condition."""
        # Implementation would check actual statistical analysis
        return None
        
    def _check_correlation(self, rule: Dict[str, Any], 
                          metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check correlation alert condition."""
        # Implementation would check actual correlation
        return None

class MetricsVisualizer2:
    """Enhanced visualizer with additional plot types."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def create_pie_chart(self, data: List[Dict[str, Any]], 
                        metric_name: str) -> go.Figure:
        """Create a pie chart for a metric."""
        fig = go.Figure()
        
        # Extract values and labels
        values = [d["value"] for d in data]
        labels = [d.get("label", str(i)) for i in range(len(data))]
        
        # Add trace
        fig.add_trace(go.Pie(
            values=values,
            labels=labels,
            name=metric_name
        ))
        
        # Update layout
        fig.update_layout(
            title=f"Pie Chart for {metric_name}",
            showlegend=True
        )
        
        return fig
        
    def create_scatter_plot(self, data: List[Dict[str, Any]], 
                          x_metric: str, y_metric: str) -> go.Figure:
        """Create a scatter plot for two metrics."""
        fig = go.Figure()
        
        # Extract values
        x_values = [d[x_metric] for d in data]
        y_values = [d[y_metric] for d in data]
        
        # Add trace
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode="markers",
            name=f"{y_metric} vs {x_metric}"
        ))
        
        # Update layout
        fig.update_layout(
            title=f"Scatter Plot: {y_metric} vs {x_metric}",
            xaxis_title=x_metric,
            yaxis_title=y_metric,
            showlegend=True
        )
        
        return fig
        
    def create_network_graph(self, data: List[Dict[str, Any]]) -> go.Figure:
        """Create a network graph visualization."""
        fig = go.Figure()
        
        # Create network graph
        G = nx.Graph()
        
        # Add nodes and edges
        for item in data:
            G.add_node(item["name"], value=item["value"])
            if "connections" in item:
                for conn in item["connections"]:
                    G.add_edge(item["name"], conn)
                    
        # Get node positions
        pos = nx.spring_layout(G)
        
        # Add nodes
        node_trace = go.Scatter(
            x=[pos[node][0] for node in G.nodes()],
            y=[pos[node][1] for node in G.nodes()],
            mode="markers+text",
            marker=dict(size=20),
            text=[f"{node}<br>Value: {G.nodes[node]['value']}" for node in G.nodes()],
            name="Nodes"
        )
        fig.add_trace(node_trace)
        
        # Add edges
        edge_trace = go.Scatter(
            x=[pos[edge[0]][0] for edge in G.edges()],
            y=[pos[edge[1]][1] for edge in G.edges()],
            mode="lines",
            line=dict(width=1),
            name="Edges"
        )
        fig.add_trace(edge_trace)
        
        # Update layout
        fig.update_layout(
            title="Network Graph",
            showlegend=True,
            hovermode="closest"
        )
        
        return fig
        
    def create_advanced_dashboard(self, metrics: Dict[str, List[Dict[str, Any]]]) -> go.Figure:
        """Create an advanced dashboard with multiple plot types."""
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Time Series", "Scatter Plot", "Pie Chart", "Network Graph")
        )
        
        # Add time series plot
        for metric_name, data in metrics.items():
            times = [d["timestamp"] for d in data]
            values = [d["value"] for d in data]
            fig.add_trace(
                go.Scatter(x=times, y=values, name=metric_name),
                row=1, col=1
            )
            
        # Add scatter plot
        if len(metrics) >= 2:
            metric_names = list(metrics.keys())
            x_data = [d["value"] for d in metrics[metric_names[0]]]
            y_data = [d["value"] for d in metrics[metric_names[1]]]
            fig.add_trace(
                go.Scatter(x=x_data, y=y_data, mode="markers", name="Scatter"),
                row=1, col=2
            )
            
        # Add pie chart
        if metrics:
            metric_name = list(metrics.keys())[0]
            values = [d["value"] for d in metrics[metric_name]]
            labels = [f"Value {i}" for i in range(len(values))]
            fig.add_trace(
                go.Pie(values=values, labels=labels, name="Pie"),
                row=2, col=1
            )
            
        # Add network graph
        if metrics:
            network_data = [
                {"name": name, "value": sum(d["value"] for d in data) / len(data)}
                for name, data in metrics.items()
            ]
            fig.add_trace(
                go.Scatter(x=[0], y=[0], mode="markers", name="Network"),
                row=2, col=2
            )
            
        # Update layout
        fig.update_layout(
            height=800,
            width=1200,
            title_text="Advanced Metrics Dashboard",
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