from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import json
from ...config.logging_config import logger

class PerformanceVisualizer:
    """Service for visualizing performance data"""
    
    def __init__(self):
        self.colors = {
            'cpu': '#1f77b4',
            'memory': '#ff7f0e',
            'disk': '#2ca02c',
            'network': '#d62728',
            'error': '#ff0000',
            'warning': '#ffa500',
            'success': '#00ff00'
        }
        
    def create_system_metrics_dashboard(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a dashboard of system metrics"""
        try:
            # Convert metrics to DataFrame
            df = pd.DataFrame(metrics)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('CPU Usage', 'Memory Usage', 'Disk Usage', 'Network I/O')
            )
            
            # CPU Usage
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['system.cpu.percent'],
                    name='CPU %',
                    line=dict(color=self.colors['cpu'])
                ),
                row=1, col=1
            )
            
            # Memory Usage
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['system.memory.percent'],
                    name='Memory %',
                    line=dict(color=self.colors['memory'])
                ),
                row=1, col=2
            )
            
            # Disk Usage
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['system.disk.percent'],
                    name='Disk %',
                    line=dict(color=self.colors['disk'])
                ),
                row=2, col=1
            )
            
            # Network I/O
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['network.io.bytes_sent'],
                    name='Bytes Sent',
                    line=dict(color=self.colors['network'])
                ),
                row=2, col=2
            )
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['network.io.bytes_recv'],
                    name='Bytes Received',
                    line=dict(color=self.colors['network'], dash='dash')
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                height=800,
                showlegend=True,
                title_text="System Performance Dashboard"
            )
            
            return {
                "dashboard": fig.to_json(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating system metrics dashboard: {str(e)}")
            return {}
            
    def create_memory_analysis_visualization(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create memory analysis visualization"""
        try:
            # Create memory usage plot
            fig = go.Figure()
            
            # Add memory usage trace
            fig.add_trace(go.Scatter(
                x=[d['timestamp'] for d in memory_data['history']],
                y=[d['rss'] for d in memory_data['history']],
                name='RSS',
                line=dict(color=self.colors['memory'])
            ))
            
            # Add VMS trace
            fig.add_trace(go.Scatter(
                x=[d['timestamp'] for d in memory_data['history']],
                y=[d['vms'] for d in memory_data['history']],
                name='VMS',
                line=dict(color=self.colors['memory'], dash='dash')
            ))
            
            # Update layout
            fig.update_layout(
                title="Memory Usage Over Time",
                xaxis_title="Time",
                yaxis_title="Memory (MB)",
                showlegend=True
            )
            
            return {
                "visualization": fig.to_json(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating memory analysis visualization: {str(e)}")
            return {}
            
    def create_api_metrics_visualization(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create API metrics visualization"""
        try:
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Response Time', 'Error Rate', 'Request Rate', 'Memory Usage')
            )
            
            # Response Time
            fig.add_trace(
                go.Scatter(
                    x=api_data['timestamps'],
                    y=api_data['response_times'],
                    name='Response Time',
                    line=dict(color=self.colors['cpu'])
                ),
                row=1, col=1
            )
            
            # Error Rate
            fig.add_trace(
                go.Scatter(
                    x=api_data['timestamps'],
                    y=api_data['error_rates'],
                    name='Error Rate',
                    line=dict(color=self.colors['error'])
                ),
                row=1, col=2
            )
            
            # Request Rate
            fig.add_trace(
                go.Scatter(
                    x=api_data['timestamps'],
                    y=api_data['request_rates'],
                    name='Request Rate',
                    line=dict(color=self.colors['network'])
                ),
                row=2, col=1
            )
            
            # Memory Usage
            fig.add_trace(
                go.Scatter(
                    x=api_data['timestamps'],
                    y=api_data['memory_usage'],
                    name='Memory Usage',
                    line=dict(color=self.colors['memory'])
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                height=800,
                showlegend=True,
                title_text="API Performance Metrics"
            )
            
            return {
                "visualization": fig.to_json(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating API metrics visualization: {str(e)}")
            return {}
            
    def create_performance_trends_visualization(self, trends: Dict[str, Any]) -> Dict[str, Any]:
        """Create performance trends visualization"""
        try:
            fig = go.Figure()
            
            # Add CPU trend
            fig.add_trace(go.Scatter(
                x=[d['timestamp'] for d in trends['cpu_trend']],
                y=[d['value'] for d in trends['cpu_trend']],
                name='CPU Usage',
                line=dict(color=self.colors['cpu'])
            ))
            
            # Add memory trend
            fig.add_trace(go.Scatter(
                x=[d['timestamp'] for d in trends['memory_trend']],
                y=[d['value'] for d in trends['memory_trend']],
                name='Memory Usage',
                line=dict(color=self.colors['memory'])
            ))
            
            # Add disk trend
            fig.add_trace(go.Scatter(
                x=[d['timestamp'] for d in trends['disk_trend']],
                y=[d['value'] for d in trends['disk_trend']],
                name='Disk Usage',
                line=dict(color=self.colors['disk'])
            ))
            
            # Update layout
            fig.update_layout(
                title="Performance Trends",
                xaxis_title="Time",
                yaxis_title="Usage (%)",
                showlegend=True
            )
            
            return {
                "visualization": fig.to_json(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating performance trends visualization: {str(e)}")
            return {} 