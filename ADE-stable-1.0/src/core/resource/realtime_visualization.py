import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import threading
import queue
import asyncio
from src.core.resource.resource_manager import ResourceManager, ResourceType, ResourceUsage
from src.core.resource.visualization import ResourceVisualizer

class RealTimeResourceVisualizer:
    """Provides real-time visualization capabilities for resource monitoring"""
    
    def __init__(self, resource_manager: ResourceManager, update_interval: float = 1.0):
        self.resource_manager = resource_manager
        self.update_interval = update_interval
        self.data_queue = queue.Queue()
        self.is_running = False
        self.update_thread = None
        
        # Initialize Dash app
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Setup the Dash application layout"""
        self.app.layout = html.Div([
            html.H1("Real-Time Resource Monitoring", className="header"),
            
            # Resource utilization gauges
            html.Div([
                html.H2("Current Resource Utilization"),
                html.Div(id="utilization-gauges", className="gauges-container")
            ], className="section"),
            
            # Resource usage timeline
            html.Div([
                html.H2("Resource Usage Timeline"),
                dcc.Graph(id="usage-timeline"),
                dcc.Interval(
                    id='timeline-interval',
                    interval=self.update_interval * 1000,  # Convert to milliseconds
                    n_intervals=0
                )
            ], className="section"),
            
            # Resource distribution
            html.Div([
                html.H2("Resource Distribution"),
                dcc.Graph(id="resource-distribution"),
                dcc.Interval(
                    id='distribution-interval',
                    interval=self.update_interval * 1000,
                    n_intervals=0
                )
            ], className="section"),
            
            # Resource correlation heatmap
            html.Div([
                html.H2("Resource Correlation"),
                dcc.Graph(id="correlation-heatmap"),
                dcc.Interval(
                    id='heatmap-interval',
                    interval=self.update_interval * 1000,
                    n_intervals=0
                )
            ], className="section"),
            
            # Resource violations
            html.Div([
                html.H2("Resource Violations"),
                dcc.Graph(id="violation-timeline"),
                dcc.Interval(
                    id='violation-interval',
                    interval=self.update_interval * 1000,
                    n_intervals=0
                )
            ], className="section"),
            
            # Resource trends
            html.Div([
                html.H2("Resource Trends"),
                dcc.Graph(id="trend-analysis"),
                dcc.Interval(
                    id='trend-interval',
                    interval=self.update_interval * 1000,
                    n_intervals=0
                )
            ], className="section"),
            
            # Resource alerts
            html.Div([
                html.H2("Resource Alerts"),
                html.Div(id="alert-container", className="alert-container")
            ], className="section")
        ])
        
        # Add custom CSS
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>Resource Monitoring Dashboard</title>
                {%favicon%}
                {%css%}
                <style>
                    .header {
                        text-align: center;
                        color: #2c3e50;
                        margin-bottom: 30px;
                    }
                    .section {
                        margin-bottom: 40px;
                        padding: 20px;
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .gauges-container {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 20px;
                        padding: 20px;
                    }
                    .alert-container {
                        max-height: 300px;
                        overflow-y: auto;
                        padding: 10px;
                        background-color: #fff;
                        border-radius: 4px;
                        border: 1px solid #ddd;
                    }
                    .alert {
                        padding: 10px;
                        margin: 5px 0;
                        border-radius: 4px;
                        border-left: 4px solid;
                    }
                    .alert-error {
                        background-color: #fee2e2;
                        border-left-color: #ef4444;
                    }
                    .alert-warning {
                        background-color: #fef3c7;
                        border-left-color: #f59e0b;
                    }
                    .alert-info {
                        background-color: #dbeafe;
                        border-left-color: #3b82f6;
                    }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
    
    def setup_callbacks(self):
        """Setup Dash callbacks for real-time updates"""
        
        @self.app.callback(
            Output("utilization-gauges", "children"),
            Input("timeline-interval", "n_intervals")
        )
        def update_gauges(n):
            current_usage = self.resource_manager.get_current_usage()
            if current_usage is None:
                return []
            
            gauges = []
            for resource, value in current_usage["utilization"].items():
                color = "green"
                if value > 0.9:
                    color = "red"
                elif value > 0.8:
                    color = "yellow"
                
                gauges.append(
                    html.Div([
                        html.H3(resource.replace("_", " ").title()),
                        dcc.Graph(
                            figure=go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=value * 100,
                                title={'text': f"{value * 100:.1f}%"},
                                gauge={
                                    'axis': {'range': [0, 100]},
                                    'bar': {'color': color},
                                    'steps': [
                                        {'range': [0, 80], 'color': "lightgray"},
                                        {'range': [80, 90], 'color': "yellow"},
                                        {'range': [90, 100], 'color': "red"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 4},
                                        'thickness': 0.75,
                                        'value': value * 100
                                    }
                                }
                            )),
                            style={'height': '200px'}
                        )
                    ])
                )
            return gauges
        
        @self.app.callback(
            Output("usage-timeline", "figure"),
            Input("timeline-interval", "n_intervals")
        )
        def update_timeline(n):
            return self.resource_manager.create_usage_timeline()
        
        @self.app.callback(
            Output("resource-distribution", "figure"),
            Input("distribution-interval", "n_intervals")
        )
        def update_distribution(n):
            return self.resource_manager.create_resource_distribution()
        
        @self.app.callback(
            Output("correlation-heatmap", "figure"),
            Input("heatmap-interval", "n_intervals")
        )
        def update_heatmap(n):
            return self.resource_manager.create_heatmap()
        
        @self.app.callback(
            Output("violation-timeline", "figure"),
            Input("violation-interval", "n_intervals")
        )
        def update_violations(n):
            return self.resource_manager.create_violation_timeline()
        
        @self.app.callback(
            Output("trend-analysis", "figure"),
            Input("trend-interval", "n_intervals")
        )
        def update_trends(n):
            trends = self.resource_manager.get_resource_trends()
            
            fig = make_subplots(rows=2, cols=2, subplot_titles=(
                "Memory Usage Trend",
                "CPU Usage Trend",
                "Disk I/O Trend",
                "Network I/O Trend"
            ))
            
            # Memory trend
            if "memory" in trends:
                memory_data = trends["memory"]
                fig.add_trace(
                    go.Scatter(
                        x=[d["timestamp"] for d in memory_data],
                        y=[d["value"] for d in memory_data],
                        name="Memory",
                        line=dict(color="#FF6B6B")
                    ),
                    row=1, col=1
                )
            
            # CPU trend
            if "cpu" in trends:
                cpu_data = trends["cpu"]
                fig.add_trace(
                    go.Scatter(
                        x=[d["timestamp"] for d in cpu_data],
                        y=[d["value"] for d in cpu_data],
                        name="CPU",
                        line=dict(color="#4ECDC4")
                    ),
                    row=1, col=2
                )
            
            # Disk I/O trend
            if "disk_io" in trends:
                disk_data = trends["disk_io"]
                fig.add_trace(
                    go.Scatter(
                        x=[d["timestamp"] for d in disk_data],
                        y=[d["value"] for d in disk_data],
                        name="Disk I/O",
                        line=dict(color="#45B7D1")
                    ),
                    row=2, col=1
                )
            
            # Network I/O trend
            if "network_io" in trends:
                network_data = trends["network_io"]
                fig.add_trace(
                    go.Scatter(
                        x=[d["timestamp"] for d in network_data],
                        y=[d["value"] for d in network_data],
                        name="Network I/O",
                        line=dict(color="#96CEB4")
                    ),
                    row=2, col=2
                )
            
            fig.update_layout(height=800, showlegend=True)
            return fig
        
        @self.app.callback(
            Output("alert-container", "children"),
            Input("violation-interval", "n_intervals")
        )
        def update_alerts(n):
            violations = self.resource_manager.get_violation_history()
            alerts = []
            
            for violation in violations[-10:]:  # Show last 10 violations
                severity_class = {
                    "error": "alert-error",
                    "warning": "alert-warning",
                    "info": "alert-info"
                }.get(violation["severity"], "alert-info")
                
                alerts.append(
                    html.Div([
                        html.Div(
                            f"{violation['type'].replace('_', ' ').title()} - "
                            f"Current: {violation['current_value']:.1f}, "
                            f"Limit: {violation['limit']:.1f}",
                            className=f"alert {severity_class}"
                        )
                    ])
                )
            
            return alerts
    
    def start(self, host: str = "0.0.0.0", port: int = 8050):
        """Start the real-time visualization server"""
        self.is_running = True
        self.update_thread = threading.Thread(
            target=self._run_server,
            args=(host, port),
            daemon=True
        )
        self.update_thread.start()
    
    def stop(self):
        """Stop the real-time visualization server"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join()
    
    def _run_server(self, host: str, port: int):
        """Run the Dash server"""
        self.app.run_server(host=host, port=port, debug=False) 