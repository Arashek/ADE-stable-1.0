"""
Visualization tools for code quality metrics.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import json
import os

@dataclass
class MetricsVisualizer:
    """Visualizes code quality metrics."""
    
    output_dir: str
    
    def __init__(self, output_dir: str = "output/metrics"):
        """Initialize the visualizer."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_radar_chart(self, metrics: Dict[str, float], title: str, filename: str):
        """Plot a radar chart of metrics."""
        # Prepare data
        categories = list(metrics.keys())
        values = list(metrics.values())
        
        # Compute angles for each category
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
        
        # Close the plot by appending first value
        values = np.concatenate((values, [values[0]]))
        angles = np.concatenate((angles, [angles[0]]))
        categories = np.concatenate((categories, [categories[0]]))
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Plot data
        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.25)
        
        # Set labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories[:-1])
        
        # Add title
        plt.title(title)
        
        # Save plot
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
    
    def plot_bar_chart(self, metrics: Dict[str, float], title: str, filename: str):
        """Plot a bar chart of metrics."""
        plt.figure(figsize=(12, 6))
        
        # Create bar chart
        bars = plt.bar(metrics.keys(), metrics.values())
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom')
        
        # Customize plot
        plt.title(title)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save plot
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
    
    def plot_heatmap(self, metrics: Dict[str, Dict[str, float]], title: str, filename: str):
        """Plot a heatmap of metrics."""
        # Convert metrics to matrix
        categories = list(metrics.keys())
        subcategories = list(next(iter(metrics.values())).keys())
        
        matrix = np.array([[metrics[cat][subcat] for subcat in subcategories] 
                          for cat in categories])
        
        # Create heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(matrix, annot=True, fmt='.2f', cmap='YlOrRd',
                   xticklabels=subcategories, yticklabels=categories)
        
        # Customize plot
        plt.title(title)
        plt.tight_layout()
        
        # Save plot
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
    
    def plot_trend(self, metrics_history: List[Dict[str, float]], title: str, filename: str):
        """Plot trends of metrics over time."""
        plt.figure(figsize=(12, 6))
        
        # Prepare data
        categories = list(metrics_history[0].keys())
        x = range(len(metrics_history))
        
        # Plot lines for each category
        for category in categories:
            values = [metrics[category] for metrics in metrics_history]
            plt.plot(x, values, label=category, marker='o')
        
        # Customize plot
        plt.title(title)
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        
        # Save plot
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
    
    def plot_comparison(self, before_metrics: Dict[str, float], after_metrics: Dict[str, float],
                       title: str, filename: str):
        """Plot comparison of metrics before and after refactoring."""
        plt.figure(figsize=(12, 6))
        
        # Prepare data
        categories = list(before_metrics.keys())
        x = np.arange(len(categories))
        width = 0.35
        
        # Create bars
        plt.bar(x - width/2, list(before_metrics.values()), width, label='Before')
        plt.bar(x + width/2, list(after_metrics.values()), width, label='After')
        
        # Customize plot
        plt.title(title)
        plt.xlabel('Metrics')
        plt.ylabel('Value')
        plt.xticks(x, categories, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        
        # Save plot
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
    
    def plot_distribution(self, metrics: Dict[str, float], title: str, filename: str):
        """Plot distribution of metrics."""
        plt.figure(figsize=(12, 6))
        
        # Create box plot
        plt.boxplot(list(metrics.values()))
        
        # Customize plot
        plt.title(title)
        plt.xticks(range(1, len(metrics) + 1), list(metrics.keys()), rotation=45, ha='right')
        plt.ylabel('Value')
        plt.tight_layout()
        
        # Save plot
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
    
    def generate_report(self, metrics: Dict[str, Dict[str, float]], filename: str):
        """Generate a comprehensive HTML report of metrics."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Code Quality Metrics Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .metric-section { margin-bottom: 30px; }
                .metric-title { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }
                .metric-value { margin-left: 20px; }
                .metric-description { color: #666; font-size: 0.9em; }
                .improvement { color: green; }
                .degradation { color: red; }
            </style>
        </head>
        <body>
            <h1>Code Quality Metrics Report</h1>
        """
        
        # Add sections for each metric category
        for category, values in metrics.items():
            html += f"""
            <div class="metric-section">
                <div class="metric-title">{category}</div>
            """
            
            for metric, value in values.items():
                html += f"""
                <div class="metric-value">
                    {metric}: {value:.2f}
                    <div class="metric-description">
                        {self._get_metric_description(category, metric)}
                    </div>
                </div>
                """
            
            html += "</div>"
        
        html += """
        </body>
        </html>
        """
        
        # Save report
        with open(os.path.join(self.output_dir, filename), 'w') as f:
            f.write(html)
    
    def _get_metric_description(self, category: str, metric: str) -> str:
        """Get description for a metric."""
        descriptions = {
            'complexity': {
                'cyclomatic_complexity': 'Measures the number of linearly independent paths through a program',
                'cognitive_complexity': 'Measures how difficult code is to understand',
                'maintainability_index': 'Indicates how maintainable the code is'
            },
            'cohesion': {
                'lcom': 'Lack of Cohesion of Methods - measures how related methods are',
                'tcc': 'Tight Class Cohesion - measures how related methods are within a class',
                'lcc': 'Loose Class Cohesion - alternative measure of class cohesion'
            },
            'coupling': {
                'cbo': 'Coupling Between Objects - measures how connected classes are',
                'rfc': 'Response For Class - measures how many methods can be called',
                'cf': 'Coupling Factor - overall measure of coupling'
            },
            'inheritance': {
                'dit': 'Depth of Inheritance Tree - measures inheritance depth',
                'noc': 'Number of Children - measures number of subclasses',
                'mif': 'Method Inheritance Factor - measures inherited methods'
            },
            'maintainability': {
                'complexity': 'Overall code complexity',
                'size': 'Code size in lines',
                'duplication': 'Code duplication ratio',
                'documentation': 'Documentation quality',
                'modularity': 'Code modularity'
            },
            'readability': {
                'lines_per_function': 'Average lines per function',
                'complexity': 'Code complexity',
                'comment_ratio': 'Ratio of comments to code',
                'naming': 'Naming convention score',
                'formatting': 'Code formatting quality'
            }
        }
        
        return descriptions.get(category, {}).get(metric, 'No description available') 