from typing import Dict, List, Any, Optional
import json
import os
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass
from datetime import datetime

@dataclass
class VisualizationConfig:
    width: int = 1200
    height: int = 800
    theme: str = 'dark'
    font_size: int = 12
    node_size: int = 20
    edge_width: float = 1.0
    show_labels: bool = True
    interactive: bool = True

class CodeVisualizer:
    def __init__(self, config: Optional[VisualizationConfig] = None):
        self.config = config or VisualizationConfig()
        self.graph = nx.DiGraph()
        self.metrics_data: Dict[str, Any] = {}
        
    def generate_dependency_graph(self, project_root: str, 
                                language_analyzers: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an interactive dependency graph visualization."""
        self.graph.clear()
        
        # Add nodes and edges for each file
        for root, _, files in os.walk(project_root):
            for file in files:
                file_path = os.path.join(root, file)
                language = self._get_language(file)
                
                if language in language_analyzers:
                    analyzer = language_analyzers[language]
                    analysis = analyzer.analyze_code(file_path)
                    
                    # Add file node
                    self.graph.add_node(file_path, 
                                      type='file',
                                      language=language,
                                      metrics=analysis.get('metrics', {}))
                    
                    # Add dependency edges
                    for dep in analysis.get('dependencies', []):
                        self.graph.add_edge(file_path, dep)
                        
        # Generate visualization data
        pos = nx.spring_layout(self.graph)
        
        # Create nodes
        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers+text',
            hoverinfo='text',
            marker=dict(
                size=[],
                color=[],
                colorscale='Viridis',
                line_width=2
            )
        )
        
        # Add node positions
        for node in self.graph.nodes():
            x, y = pos[node]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['text'] += tuple([f"{os.path.basename(node)}<br>Language: {self.graph.nodes[node]['language']}"])
            node_trace['marker']['size'] += tuple([self.config.node_size])
            node_trace['marker']['color'] += tuple([self._get_node_color(node)])
            
        # Create edges
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=self.config.edge_width, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Add edge positions
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += tuple([x0, x1, None])
            edge_trace['y'] += tuple([y0, y1, None])
            
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[
                               dict(
                                   text="",
                                   showarrow=False,
                                   xref="paper",
                                   yref="paper",
                                   x=0,
                                   y=0
                               )
                           ],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           plot_bgcolor='rgba(0,0,0,0)',
                           paper_bgcolor='rgba(0,0,0,0)',
                           width=self.config.width,
                           height=self.config.height
                       ))
        
        return {
            'type': 'graph',
            'data': fig.to_dict(),
            'metrics': self._calculate_graph_metrics()
        }
        
    def generate_complexity_heatmap(self, project_root: str, 
                                  language_analyzers: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complexity heatmap visualization."""
        complexity_data = []
        
        for root, _, files in os.walk(project_root):
            for file in files:
                file_path = os.path.join(root, file)
                language = self._get_language(file)
                
                if language in language_analyzers:
                    analyzer = language_analyzers[language]
                    analysis = analyzer.analyze_code(file_path)
                    metrics = analysis.get('metrics', {})
                    
                    complexity_data.append({
                        'file': os.path.relpath(file_path, project_root),
                        'language': language,
                        'complexity': metrics.get('complexity', 0),
                        'lines': metrics.get('lines', 0),
                        'statements': metrics.get('statements', 0)
                    })
                    
        # Create heatmap
        fig = px.treemap(complexity_data,
                        path=['language', 'file'],
                        values='complexity',
                        color='complexity',
                        color_continuous_scale='Viridis',
                        title='Code Complexity Heatmap',
                        width=self.config.width,
                        height=self.config.height)
        
        return {
            'type': 'heatmap',
            'data': fig.to_dict()
        }
        
    def generate_metrics_dashboard(self, project_root: str, 
                                 language_analyzers: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a metrics dashboard visualization."""
        metrics_data = {
            'languages': {},
            'total_files': 0,
            'total_lines': 0,
            'total_complexity': 0,
            'total_statements': 0
        }
        
        for root, _, files in os.walk(project_root):
            for file in files:
                file_path = os.path.join(root, file)
                language = self._get_language(file)
                
                if language in language_analyzers:
                    analyzer = language_analyzers[language]
                    analysis = analyzer.analyze_code(file_path)
                    metrics = analysis.get('metrics', {})
                    
                    if language not in metrics_data['languages']:
                        metrics_data['languages'][language] = {
                            'files': 0,
                            'lines': 0,
                            'complexity': 0,
                            'statements': 0
                        }
                        
                    metrics_data['languages'][language]['files'] += 1
                    metrics_data['languages'][language]['lines'] += metrics.get('lines', 0)
                    metrics_data['languages'][language]['complexity'] += metrics.get('complexity', 0)
                    metrics_data['languages'][language]['statements'] += metrics.get('statements', 0)
                    
                    metrics_data['total_files'] += 1
                    metrics_data['total_lines'] += metrics.get('lines', 0)
                    metrics_data['total_complexity'] += metrics.get('complexity', 0)
                    metrics_data['total_statements'] += metrics.get('statements', 0)
                    
        # Create dashboard
        fig = go.Figure()
        
        # Add language distribution pie chart
        fig.add_trace(go.Pie(
            labels=list(metrics_data['languages'].keys()),
            values=[data['files'] for data in metrics_data['languages'].values()],
            name='Files by Language',
            domain={'x': [0, 0.5], 'y': [0.5, 1]}
        ))
        
        # Add complexity bar chart
        fig.add_trace(go.Bar(
            x=list(metrics_data['languages'].keys()),
            y=[data['complexity'] for data in metrics_data['languages'].values()],
            name='Complexity by Language',
            xaxis='x2',
            yaxis='y2'
        ))
        
        # Update layout
        fig.update_layout(
            title='Code Metrics Dashboard',
            grid={'rows': 2, 'columns': 2, 'pattern': 'independent'},
            xaxis2={'domain': [0.6, 1], 'anchor': 'y2'},
            yaxis2={'domain': [0.5, 1], 'anchor': 'x2'},
            width=self.config.width,
            height=self.config.height
        )
        
        return {
            'type': 'dashboard',
            'data': fig.to_dict(),
            'metrics': metrics_data
        }
        
    def _get_language(self, file_name: str) -> str:
        """Determine programming language from file extension."""
        ext = os.path.splitext(file_name)[1].lower()
        if ext == '.py':
            return 'python'
        elif ext in ('.js', '.jsx', '.ts', '.tsx'):
            return 'javascript'
        elif ext == '.java':
            return 'java'
        else:
            return 'unknown'
            
    def _get_node_color(self, node: str) -> float:
        """Get color value for node based on metrics."""
        metrics = self.graph.nodes[node].get('metrics', {})
        complexity = metrics.get('complexity', 0)
        return min(complexity / 10, 1)  # Normalize to [0,1]
        
    def _calculate_graph_metrics(self) -> Dict[str, Any]:
        """Calculate graph-level metrics."""
        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'avg_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes(),
            'components': nx.number_weakly_connected_components(self.graph)
        } 