import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from prometheus_client import Counter, Gauge, Histogram, start_http_server
import json

logger = logging.getLogger(__name__)

class TrainingMonitor:
    """Monitors and visualizes training metrics."""
    
    def __init__(self, output_dir: str = "monitoring"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Prometheus metrics
        self.training_counter = Counter(
            'training_iterations_total',
            'Total number of training iterations'
        )
        self.loss_gauge = Gauge(
            'training_loss',
            'Current training loss'
        )
        self.accuracy_gauge = Gauge(
            'training_accuracy',
            'Current training accuracy'
        )
        self.memory_usage = Gauge(
            'memory_usage_bytes',
            'Current memory usage in bytes'
        )
        self.training_duration = Histogram(
            'training_duration_seconds',
            'Duration of training iterations'
        )
        
        # Start Prometheus server
        start_http_server(8000)
        
    def update_metrics(self, metrics: Dict):
        """Update Prometheus metrics."""
        try:
            self.training_counter.inc()
            self.loss_gauge.set(metrics.get('loss', 0))
            self.accuracy_gauge.set(metrics.get('accuracy', 0))
            self.memory_usage.set(metrics.get('memory_usage', 0))
            self.training_duration.observe(metrics.get('duration', 0))
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            
    def save_metrics(self, metrics: Dict):
        """Save metrics to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metrics_file = self.output_dir / f"metrics_{timestamp}.json"
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            
    def create_training_plot(self, metrics_history: List[Dict]):
        """Create training visualization."""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(metrics_history)
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Loss', 'Accuracy', 'Memory Usage', 'Training Duration')
            )
            
            # Loss plot
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['loss'],
                    name='Loss'
                ),
                row=1, col=1
            )
            
            # Accuracy plot
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['accuracy'],
                    name='Accuracy'
                ),
                row=1, col=2
            )
            
            # Memory usage plot
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['memory_usage'],
                    name='Memory Usage'
                ),
                row=2, col=1
            )
            
            # Training duration plot
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['duration'],
                    name='Duration'
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                height=800,
                width=1200,
                title_text="Training Metrics",
                showlegend=True
            )
            
            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(self.output_dir / f"training_plot_{timestamp}.html")
            
        except Exception as e:
            logger.error(f"Error creating training plot: {e}")
            
    def create_performance_plot(self, data: pd.DataFrame):
        """Create performance visualization."""
        try:
            # Create correlation matrix
            corr_matrix = data.corr()
            
            # Create heatmap
            fig = px.imshow(
                corr_matrix,
                title="Feature Correlation Matrix",
                aspect="auto"
            )
            
            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(self.output_dir / f"performance_plot_{timestamp}.html")
            
        except Exception as e:
            logger.error(f"Error creating performance plot: {e}")
            
    def create_error_analysis(self, data: pd.DataFrame):
        """Create error analysis visualization."""
        try:
            # Create error distribution plot
            fig = px.histogram(
                data,
                x='error_rate',
                title="Error Rate Distribution",
                nbins=30
            )
            
            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(self.output_dir / f"error_analysis_{timestamp}.html")
            
        except Exception as e:
            logger.error(f"Error creating error analysis: {e}")
            
    def generate_report(self, metrics_history: List[Dict], data: pd.DataFrame):
        """Generate comprehensive training report."""
        try:
            # Create all visualizations
            self.create_training_plot(metrics_history)
            self.create_performance_plot(data)
            self.create_error_analysis(data)
            
            # Calculate summary statistics
            summary = {
                'total_iterations': len(metrics_history),
                'avg_loss': np.mean([m['loss'] for m in metrics_history]),
                'avg_accuracy': np.mean([m['accuracy'] for m in metrics_history]),
                'avg_memory_usage': np.mean([m['memory_usage'] for m in metrics_history]),
                'avg_duration': np.mean([m['duration'] for m in metrics_history]),
                'total_training_time': sum([m['duration'] for m in metrics_history]),
                'error_rate_stats': {
                    'mean': data['error_rate'].mean(),
                    'std': data['error_rate'].std(),
                    'min': data['error_rate'].min(),
                    'max': data['error_rate'].max()
                }
            }
            
            # Save summary
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(self.output_dir / f"summary_{timestamp}.json", 'w') as f:
                json.dump(summary, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error generating report: {e}") 