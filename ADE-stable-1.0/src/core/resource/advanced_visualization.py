import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from prometheus_client import start_http_server, Gauge, Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
from src.core.resource.resource_manager import ResourceManager, ResourceType, ResourceUsage

class AdvancedResourceVisualizer:
    """Provides advanced visualization capabilities including prediction and anomaly detection"""
    
    def __init__(self, resource_manager: ResourceManager):
        self.resource_manager = resource_manager
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.prediction_window = timedelta(minutes=5)
        self._setup_prometheus_metrics()
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for external monitoring"""
        # Resource usage gauges
        self.prometheus_metrics = {
            "memory_usage": Gauge("resource_memory_usage_bytes", "Memory usage in bytes"),
            "cpu_usage": Gauge("resource_cpu_usage_percent", "CPU usage percentage"),
            "disk_io": Gauge("resource_disk_io_bytes", "Disk I/O in bytes"),
            "network_io": Gauge("resource_network_io_bytes", "Network I/O in bytes"),
            "open_files": Gauge("resource_open_files", "Number of open files"),
            "thread_count": Gauge("resource_thread_count", "Number of threads"),
            "swap_usage": Gauge("resource_swap_usage_bytes", "Swap usage in bytes"),
            "iops": Gauge("resource_iops", "IOPS"),
            "gpu_memory_usage": Gauge("resource_gpu_memory_usage_bytes", "GPU memory usage in bytes"),
            
            # Anomaly detection
            "anomaly_score": Gauge("resource_anomaly_score", "Anomaly detection score"),
            "predicted_usage": Gauge("resource_predicted_usage", "Predicted resource usage"),
            
            # Violations
            "violation_count": Counter("resource_violation_total", "Total number of resource violations")
        }
    
    def start_prometheus_server(self, port: int = 9090):
        """Start Prometheus metrics server"""
        start_http_server(port)
    
    def create_prediction_timeline(self, resource_type: ResourceType) -> go.Figure:
        """Create a timeline showing actual and predicted resource usage"""
        # Get historical data
        history = self.resource_manager.get_usage_history()
        if not history:
            raise ValueError("No historical data available for prediction")
        
        # Convert to DataFrame
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Prepare data for prediction
        feature_col = self._get_feature_column(resource_type)
        if feature_col not in df.columns:
            raise ValueError(f"Resource type {resource_type} not found in data")
        
        # Create time features
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['second'] = df['timestamp'].dt.second
        
        # Train prediction model
        X = df[['hour', 'minute', 'second']].values
        y = df[feature_col].values
        
        # Make predictions for next window
        future_times = pd.date_range(
            start=df['timestamp'].max(),
            periods=12,  # 12 points in 5-minute window
            freq='25s'
        )
        
        future_df = pd.DataFrame({
            'timestamp': future_times,
            'hour': future_times.hour,
            'minute': future_times.minute,
            'second': future_times.second
        })
        
        # Create figure
        fig = go.Figure()
        
        # Add actual usage
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=y,
            name='Actual Usage',
            line=dict(color='blue')
        ))
        
        # Add prediction
        fig.add_trace(go.Scatter(
            x=future_df['timestamp'],
            y=[np.mean(y)] * len(future_df),  # Simple prediction for now
            name='Predicted Usage',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title=f"Resource Usage Prediction - {resource_type.value}",
            xaxis_title="Time",
            yaxis_title=f"{resource_type.value} Usage",
            showlegend=True
        )
        
        return fig
    
    def create_anomaly_detection_plot(self) -> go.Figure:
        """Create a plot showing resource usage anomalies"""
        # Get historical data
        history = self.resource_manager.get_usage_history()
        if not history:
            raise ValueError("No historical data available for anomaly detection")
        
        # Convert to DataFrame
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Prepare features for anomaly detection
        features = [
            'memory_used', 'cpu_percent', 'disk_read', 'disk_write',
            'network_sent', 'network_recv', 'open_files', 'thread_count',
            'swap_used', 'iops'
        ]
        
        if 'gpu_memory_used' in df.columns:
            features.append('gpu_memory_used')
        
        X = df[features].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Detect anomalies
        anomaly_scores = self.anomaly_detector.fit_predict(X_scaled)
        
        # Create figure
        fig = go.Figure()
        
        # Add normal points
        normal_mask = anomaly_scores == 1
        fig.add_trace(go.Scatter(
            x=df.loc[normal_mask, 'timestamp'],
            y=df.loc[normal_mask, 'memory_used'],
            mode='markers',
            name='Normal',
            marker=dict(color='blue', size=8)
        ))
        
        # Add anomaly points
        anomaly_mask = anomaly_scores == -1
        fig.add_trace(go.Scatter(
            x=df.loc[anomaly_mask, 'timestamp'],
            y=df.loc[anomaly_mask, 'memory_used'],
            mode='markers',
            name='Anomaly',
            marker=dict(color='red', size=12)
        ))
        
        fig.update_layout(
            title="Resource Usage Anomalies",
            xaxis_title="Time",
            yaxis_title="Memory Usage (MB)",
            showlegend=True
        )
        
        return fig
    
    def create_resource_correlation_matrix(self) -> go.Figure:
        """Create a correlation matrix of resource usage"""
        # Get historical data
        history = self.resource_manager.get_usage_history()
        if not history:
            raise ValueError("No historical data available for correlation analysis")
        
        # Convert to DataFrame
        df = pd.DataFrame(history)
        
        # Calculate correlation matrix
        features = [
            'memory_used', 'cpu_percent', 'disk_read', 'disk_write',
            'network_sent', 'network_recv', 'open_files', 'thread_count',
            'swap_used', 'iops'
        ]
        
        if 'gpu_memory_used' in df.columns:
            features.append('gpu_memory_used')
        
        corr_matrix = df[features].corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title="Resource Usage Correlation Matrix",
            xaxis_title="Resource",
            yaxis_title="Resource",
            height=800
        )
        
        return fig
    
    def create_resource_forecast(self, resource_type: ResourceType) -> go.Figure:
        """Create a forecast of resource usage using time series analysis"""
        # Get historical data
        history = self.resource_manager.get_usage_history()
        if not history:
            raise ValueError("No historical data available for forecasting")
        
        # Convert to DataFrame
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Prepare data
        feature_col = self._get_feature_column(resource_type)
        if feature_col not in df.columns:
            raise ValueError(f"Resource type {resource_type} not found in data")
        
        # Create time features
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['second'] = df['timestamp'].dt.second
        
        # Calculate rolling statistics
        window_size = 10
        df['rolling_mean'] = df[feature_col].rolling(window=window_size).mean()
        df['rolling_std'] = df[feature_col].rolling(window=window_size).std()
        
        # Create figure
        fig = go.Figure()
        
        # Add actual values
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df[feature_col],
            name='Actual',
            line=dict(color='blue')
        ))
        
        # Add rolling mean
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['rolling_mean'],
            name='Rolling Mean',
            line=dict(color='green', dash='dash')
        ))
        
        # Add confidence intervals
        fig.add_trace(go.Scatter(
            x=df['timestamp'].tolist() + df['timestamp'].tolist()[::-1],
            y=(df['rolling_mean'] + 2*df['rolling_std']).tolist() + 
               (df['rolling_mean'] - 2*df['rolling_std']).tolist()[::-1],
            fill='toself',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% Confidence Interval'
        ))
        
        fig.update_layout(
            title=f"Resource Usage Forecast - {resource_type.value}",
            xaxis_title="Time",
            yaxis_title=f"{resource_type.value} Usage",
            showlegend=True
        )
        
        return fig
    
    def _get_feature_column(self, resource_type: ResourceType) -> str:
        """Get the DataFrame column name for a resource type"""
        column_map = {
            ResourceType.MEMORY: 'memory_used',
            ResourceType.CPU: 'cpu_percent',
            ResourceType.DISK_IO: 'disk_read',
            ResourceType.NETWORK_IO: 'network_sent',
            ResourceType.OPEN_FILES: 'open_files',
            ResourceType.THREADS: 'thread_count',
            ResourceType.SWAP: 'swap_used',
            ResourceType.IOPS: 'iops',
            ResourceType.GPU: 'gpu_memory_used'
        }
        return column_map.get(resource_type)
    
    def update_prometheus_metrics(self, usage: Dict[str, Any]):
        """Update Prometheus metrics with current resource usage"""
        # Update resource usage metrics
        self.prometheus_metrics["memory_usage"].set(usage["memory_used"] * 1024 * 1024)
        self.prometheus_metrics["cpu_usage"].set(usage["cpu_percent"])
        self.prometheus_metrics["disk_io"].set(
            (usage["disk_read"] + usage["disk_write"]) * 1024 * 1024
        )
        self.prometheus_metrics["network_io"].set(
            (usage["network_sent"] + usage["network_recv"]) * 1024 * 1024
        )
        self.prometheus_metrics["open_files"].set(usage["open_files"])
        self.prometheus_metrics["thread_count"].set(usage["thread_count"])
        self.prometheus_metrics["swap_usage"].set(usage["swap_used"] * 1024 * 1024)
        self.prometheus_metrics["iops"].set(usage["iops"])
        
        if usage.get("gpu_memory_used") is not None:
            self.prometheus_metrics["gpu_memory_usage"].set(
                usage["gpu_memory_used"] * 1024 * 1024
            )
        
        # Update anomaly score
        if "anomaly_score" in usage:
            self.prometheus_metrics["anomaly_score"].set(usage["anomaly_score"])
        
        # Update predicted usage
        if "predicted_usage" in usage:
            self.prometheus_metrics["predicted_usage"].set(usage["predicted_usage"])
    
    def increment_violation_counter(self):
        """Increment the violation counter in Prometheus"""
        self.prometheus_metrics["violation_count"].inc() 