import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from src.core.resource.resource_manager import ResourceType, ResourceUsage
import numpy as np

class ResourceVisualizer:
    """Provides visualization capabilities for resource usage data"""
    
    def __init__(self):
        # Set default style
        plt.style.use('seaborn')
        
        # Color scheme for different resource types
        self.color_scheme = {
            ResourceType.MEMORY: '#FF6B6B',
            ResourceType.CPU: '#4ECDC4',
            ResourceType.DISK_IO: '#45B7D1',
            ResourceType.NETWORK_IO: '#96CEB4',
            ResourceType.OPEN_FILES: '#FFEEAD',
            ResourceType.THREADS: '#D4A5A5',
            ResourceType.SWAP: '#9B59B6',
            ResourceType.IOPS: '#3498DB',
            ResourceType.GPU: '#E67E22'
        }
    
    def create_usage_timeline(self, usage_history: List[ResourceUsage], 
                            resource_types: Optional[List[ResourceType]] = None) -> go.Figure:
        """Create an interactive timeline of resource usage"""
        if not resource_types:
            resource_types = list(ResourceType)
        
        # Convert usage history to DataFrame
        df = pd.DataFrame([
            {
                'timestamp': usage.timestamp,
                'memory': usage.memory_used,
                'cpu': usage.cpu_percent,
                'disk_io': usage.disk_read + usage.disk_write,
                'network_io': usage.network_sent + usage.network_recv,
                'open_files': usage.open_files,
                'threads': usage.thread_count,
                'swap': usage.swap_used,
                'iops': usage.iops,
                'gpu': usage.gpu_memory_used or 0
            }
            for usage in usage_history
        ])
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add traces for each resource type
        for resource_type in resource_types:
            if resource_type == ResourceType.MEMORY:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['memory'],
                        name='Memory (MB)',
                        line=dict(color=self.color_scheme[resource_type])
                    ),
                    secondary_y=False
                )
            elif resource_type == ResourceType.CPU:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['cpu'],
                        name='CPU (%)',
                        line=dict(color=self.color_scheme[resource_type])
                    ),
                    secondary_y=True
                )
            elif resource_type == ResourceType.DISK_IO:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['disk_io'],
                        name='Disk I/O (MB/s)',
                        line=dict(color=self.color_scheme[resource_type])
                    ),
                    secondary_y=True
                )
            elif resource_type == ResourceType.NETWORK_IO:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['network_io'],
                        name='Network I/O (MB/s)',
                        line=dict(color=self.color_scheme[resource_type])
                    ),
                    secondary_y=True
                )
            elif resource_type == ResourceType.OPEN_FILES:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['open_files'],
                        name='Open Files',
                        line=dict(color=self.color_scheme[resource_type])
                    ),
                    secondary_y=True
                )
            elif resource_type == ResourceType.THREADS:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['threads'],
                        name='Threads',
                        line=dict(color=self.color_scheme[resource_type])
                    ),
                    secondary_y=True
                )
            elif resource_type == ResourceType.SWAP:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['swap'],
                        name='Swap (MB)',
                        line=dict(color=self.color_scheme[resource_type])
                    ),
                    secondary_y=False
                )
            elif resource_type == ResourceType.IOPS:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['iops'],
                        name='IOPS',
                        line=dict(color=self.color_scheme[resource_type])
                    ),
                    secondary_y=True
                )
            elif resource_type == ResourceType.GPU:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['gpu'],
                        name='GPU Memory (MB)',
                        line=dict(color=self.color_scheme[resource_type])
                    ),
                    secondary_y=False
                )
        
        # Update layout
        fig.update_layout(
            title='Resource Usage Timeline',
            xaxis_title='Time',
            yaxis_title='Memory/GPU/Swap (MB)',
            yaxis2_title='CPU/Disk/Network/Threads/IOPS',
            hovermode='x unified'
        )
        
        return fig
    
    def create_resource_distribution(self, usage_history: List[ResourceUsage]) -> go.Figure:
        """Create a distribution plot of resource usage"""
        # Convert usage history to DataFrame
        df = pd.DataFrame([
            {
                'memory': usage.memory_used,
                'cpu': usage.cpu_percent,
                'disk_io': usage.disk_read + usage.disk_write,
                'network_io': usage.network_sent + usage.network_recv,
                'open_files': usage.open_files,
                'threads': usage.thread_count,
                'swap': usage.swap_used,
                'iops': usage.iops,
                'gpu': usage.gpu_memory_used or 0
            }
            for usage in usage_history
        ])
        
        # Create figure
        fig = go.Figure()
        
        # Add box plots for each resource
        for column in df.columns:
            fig.add_trace(
                go.Box(
                    y=df[column],
                    name=column.replace('_', ' ').title(),
                    boxpoints='outliers',
                    jitter=0.3,
                    pointpos=-1.8
                )
            )
        
        # Update layout
        fig.update_layout(
            title='Resource Usage Distribution',
            yaxis_title='Value',
            showlegend=False
        )
        
        return fig
    
    def create_heatmap(self, usage_history: List[ResourceUsage]) -> go.Figure:
        """Create a heatmap of resource usage patterns"""
        # Convert usage history to DataFrame
        df = pd.DataFrame([
            {
                'memory': usage.memory_used,
                'cpu': usage.cpu_percent,
                'disk_io': usage.disk_read + usage.disk_write,
                'network_io': usage.network_sent + usage.network_recv,
                'open_files': usage.open_files,
                'threads': usage.thread_count,
                'swap': usage.swap_used,
                'iops': usage.iops,
                'gpu': usage.gpu_memory_used or 0
            }
            for usage in usage_history
        ])
        
        # Calculate correlation matrix
        corr_matrix = df.corr()
        
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
        
        # Update layout
        fig.update_layout(
            title='Resource Usage Correlation Heatmap',
            xaxis_title='Resource',
            yaxis_title='Resource'
        )
        
        return fig
    
    def create_violation_timeline(self, violation_history: List[Dict[str, Any]]) -> go.Figure:
        """Create a timeline of resource violations"""
        # Convert violation history to DataFrame
        df = pd.DataFrame(violation_history)
        
        # Create figure
        fig = go.Figure()
        
        # Add scatter plot for each violation type
        for violation_type in df['type'].unique():
            mask = df['type'] == violation_type
            fig.add_trace(
                go.Scatter(
                    x=df[mask]['timestamp'],
                    y=df[mask]['current_value'],
                    mode='markers',
                    name=violation_type.replace('_', ' ').title(),
                    marker=dict(
                        size=10,
                        color='red' if df[mask]['severity'].iloc[0] == 'error' else 'yellow'
                    )
                )
            )
        
        # Update layout
        fig.update_layout(
            title='Resource Violations Timeline',
            xaxis_title='Time',
            yaxis_title='Value',
            hovermode='closest'
        )
        
        return fig
    
    def create_utilization_gauge(self, current_usage: Dict[str, Any]) -> go.Figure:
        """Create a gauge chart showing current resource utilization"""
        # Extract utilization values
        utilization = current_usage['utilization']
        
        # Create figure with subplots
        fig = make_subplots(
            rows=2, cols=4,
            specs=[[{"type": "indicator"}, {"type": "indicator"},
                   {"type": "indicator"}, {"type": "indicator"}],
                  [{"type": "indicator"}, {"type": "indicator"},
                   {"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # Add gauge for each resource
        resources = [
            ('memory', 'Memory'),
            ('cpu', 'CPU'),
            ('disk_io', 'Disk I/O'),
            ('network_io', 'Network I/O'),
            ('open_files', 'Open Files'),
            ('threads', 'Threads'),
            ('swap', 'Swap'),
            ('iops', 'IOPS')
        ]
        
        for idx, (key, name) in enumerate(resources, 1):
            row = (idx - 1) // 4 + 1
            col = (idx - 1) % 4 + 1
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=utilization[key] * 100,
                    title={'text': name},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 80], 'color': "lightgray"},
                            {'range': [80, 90], 'color': "yellow"},
                            {'range': [90, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': utilization[key] * 100
                        }
                    }
                ),
                row=row, col=col
            )
        
        # Update layout
        fig.update_layout(
            title='Current Resource Utilization',
            height=600,
            showlegend=False
        )
        
        return fig
    
    def save_visualization(self, fig: go.Figure, filename: str):
        """Save a visualization to a file"""
        fig.write_html(filename)
    
    def show_visualization(self, fig: go.Figure):
        """Display a visualization in the browser"""
        fig.show() 