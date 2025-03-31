from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from ...config.logging_config import logger
import torch

class LearningVisualizer:
    """Visualizes learning progress and metrics"""
    
    def __init__(self, output_dir: str = "data/learning/visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def create_reward_plot(self, rewards: List[float], episode: int) -> str:
        """Create plot of rewards over time"""
        try:
            # Create DataFrame
            df = pd.DataFrame({
                'Episode': range(1, len(rewards) + 1),
                'Reward': rewards
            })
            
            # Create plot
            fig = px.line(
                df,
                x='Episode',
                y='Reward',
                title=f'Rewards Over Time (Episode {episode})',
                labels={'Reward': 'Average Reward', 'Episode': 'Episode Number'}
            )
            
            # Add moving average
            fig.add_trace(
                go.Scatter(
                    x=df['Episode'],
                    y=df['Reward'].rolling(window=10).mean(),
                    name='Moving Average',
                    line=dict(color='red')
                )
            )
            
            # Add confidence interval
            std = df['Reward'].rolling(window=10).std()
            fig.add_trace(
                go.Scatter(
                    x=df['Episode'],
                    y=df['Reward'].rolling(window=10).mean() + std,
                    fill=None,
                    mode='lines',
                    line_color='rgba(0,100,80,0.2)',
                    name='Upper Bound'
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=df['Episode'],
                    y=df['Reward'].rolling(window=10).mean() - std,
                    fill='tonexty',
                    mode='lines',
                    line_color='rgba(0,100,80,0.2)',
                    name='Lower Bound'
                )
            )
            
            # Save plot
            filename = f'rewards_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating reward plot: {str(e)}")
            return ""
            
    def create_completion_accuracy_plot(self, accuracy_data: Dict[str, List[float]], episode: int) -> str:
        """Create plot of completion accuracy metrics"""
        try:
            # Create DataFrame
            df = pd.DataFrame(accuracy_data)
            
            # Create plot
            fig = go.Figure()
            
            for column in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[column],
                        name=column,
                        mode='lines+markers'
                    )
                )
                
            fig.update_layout(
                title=f'Completion Accuracy Metrics (Episode {episode})',
                xaxis_title='Episode',
                yaxis_title='Accuracy',
                yaxis=dict(range=[0, 1])
            )
            
            # Add confusion matrix
            if 'confusion_matrix' in accuracy_data:
                conf_matrix = accuracy_data['confusion_matrix']
                fig.add_trace(
                    go.Heatmap(
                        z=conf_matrix,
                        x=['True Neg', 'False Pos', 'False Neg', 'True Pos'],
                        y=['True Neg', 'False Pos', 'False Neg', 'True Pos'],
                        colorscale='Viridis',
                        name='Confusion Matrix'
                    )
                )
                
            # Save plot
            filename = f'accuracy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating accuracy plot: {str(e)}")
            return ""
            
    def create_exploration_plot(self, exploration_data: Dict[str, List[float]], episode: int) -> str:
        """Create plot of exploration metrics"""
        try:
            # Create DataFrame
            df = pd.DataFrame(exploration_data)
            
            # Create plot
            fig = go.Figure()
            
            for column in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[column],
                        name=column,
                        mode='lines+markers'
                    )
                )
                
            fig.update_layout(
                title=f'Exploration Metrics (Episode {episode})',
                xaxis_title='Episode',
                yaxis_title='Value'
            )
            
            # Add action distribution
            if 'action_distribution' in exploration_data:
                action_dist = exploration_data['action_distribution']
                fig.add_trace(
                    go.Bar(
                        x=list(action_dist.keys()),
                        y=list(action_dist.values()),
                        name='Action Distribution'
                    )
                )
                
            # Save plot
            filename = f'exploration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating exploration plot: {str(e)}")
            return ""
            
    def create_learning_curves(self, learning_data: Dict[str, Any], episode: int) -> str:
        """Create comprehensive learning curves"""
        try:
            # Create subplots
            fig = go.Figure()
            
            # Add reward curve
            fig.add_trace(
                go.Scatter(
                    x=range(1, len(learning_data['rewards']) + 1),
                    y=learning_data['rewards'],
                    name='Rewards',
                    mode='lines+markers'
                )
            )
            
            # Add accuracy curve
            fig.add_trace(
                go.Scatter(
                    x=range(1, len(learning_data['accuracy']) + 1),
                    y=learning_data['accuracy'],
                    name='Accuracy',
                    mode='lines+markers'
                )
            )
            
            # Add exploration curve
            fig.add_trace(
                go.Scatter(
                    x=range(1, len(learning_data['exploration']) + 1),
                    y=learning_data['exploration'],
                    name='Exploration',
                    mode='lines+markers'
                )
            )
            
            # Add loss curve if available
            if 'loss' in learning_data:
                fig.add_trace(
                    go.Scatter(
                        x=range(1, len(learning_data['loss']) + 1),
                        y=learning_data['loss'],
                        name='Loss',
                        mode='lines+markers'
                    )
                )
                
            fig.update_layout(
                title=f'Learning Curves (Episode {episode})',
                xaxis_title='Episode',
                yaxis_title='Value',
                showlegend=True
            )
            
            # Save plot
            filename = f'learning_curves_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating learning curves: {str(e)}")
            return ""
            
    def create_completion_examples(self, examples: List[Dict[str, Any]], episode: int) -> str:
        """Create visualization of completion examples"""
        try:
            # Create HTML table
            html = """
            <html>
            <head>
                <style>
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    .context { font-family: monospace; }
                    .completion { font-family: monospace; color: green; }
                    .actual { font-family: monospace; color: blue; }
                    .diff { font-family: monospace; }
                    .diff-add { color: green; }
                    .diff-remove { color: red; }
                </style>
            </head>
            <body>
                <h2>Completion Examples (Episode {episode})</h2>
                <table>
                    <tr>
                        <th>Context</th>
                        <th>Predicted</th>
                        <th>Actual</th>
                        <th>Reward</th>
                        <th>Confidence</th>
                        <th>Time</th>
                    </tr>
            """
            
            for example in examples:
                # Calculate diff
                diff = self._calculate_diff(example['predicted'], example['actual'])
                
                html += f"""
                    <tr>
                        <td class="context">{example['context']}</td>
                        <td class="completion">{example['predicted']}</td>
                        <td class="actual">{example['actual']}</td>
                        <td>{example['reward']:.2f}</td>
                        <td>{example.get('confidence', 0):.2f}</td>
                        <td>{example.get('time', 0):.2f}s</td>
                    </tr>
                    <tr>
                        <td colspan="6" class="diff">{diff}</td>
                    </tr>
                """
                
            html += """
                </table>
            </body>
            </html>
            """
            
            # Save HTML
            filename = f'examples_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            with open(filepath, 'w') as f:
                f.write(html)
                
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating completion examples: {str(e)}")
            return ""
            
    def create_dashboard(self, learning_data: Dict[str, Any], episode: int) -> str:
        """Create comprehensive learning dashboard"""
        try:
            # Create HTML dashboard
            html = """
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .container { display: flex; flex-wrap: wrap; gap: 20px; }
                    .plot { flex: 1; min-width: 400px; height: 400px; }
                    .metrics { flex: 1; min-width: 400px; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    .metric-card {
                        background-color: #f8f9fa;
                        border-radius: 5px;
                        padding: 15px;
                        margin-bottom: 15px;
                    }
                    .metric-value {
                        font-size: 24px;
                        font-weight: bold;
                        color: #007bff;
                    }
                </style>
            </head>
            <body>
                <h1>Learning Dashboard (Episode {episode})</h1>
                <div class="container">
                    <div class="plot">
                        <iframe src="{reward_plot}" width="100%" height="100%" frameborder="0"></iframe>
                    </div>
                    <div class="plot">
                        <iframe src="{accuracy_plot}" width="100%" height="100%" frameborder="0"></iframe>
                    </div>
                    <div class="plot">
                        <iframe src="{exploration_plot}" width="100%" height="100%" frameborder="0"></iframe>
                    </div>
                    <div class="metrics">
                        <h2>Current Metrics</h2>
                        <div class="metric-card">
                            <h3>Average Reward</h3>
                            <div class="metric-value">{avg_reward:.2f}</div>
                        </div>
                        <div class="metric-card">
                            <h3>Completion Accuracy</h3>
                            <div class="metric-value">{accuracy:.2f}</div>
                        </div>
                        <div class="metric-card">
                            <h3>Exploration Rate</h3>
                            <div class="metric-value">{exploration:.2f}</div>
                        </div>
                        <div class="metric-card">
                            <h3>Average Loss</h3>
                            <div class="metric-value">{loss:.2f}</div>
                        </div>
                        <div class="metric-card">
                            <h3>Average Time</h3>
                            <div class="metric-value">{avg_time:.2f}s</div>
                        </div>
                        <div class="metric-card">
                            <h3>Memory Usage</h3>
                            <div class="metric-value">{memory_usage:.1f}MB</div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Generate plots
            reward_plot = self.create_reward_plot(learning_data['rewards'], episode)
            accuracy_plot = self.create_completion_accuracy_plot(learning_data['accuracy'], episode)
            exploration_plot = self.create_exploration_plot(learning_data['exploration'], episode)
            
            # Calculate metrics
            avg_reward = np.mean(learning_data['rewards'][-10:]) if learning_data['rewards'] else 0
            accuracy = np.mean(learning_data['accuracy'][-10:]) if learning_data['accuracy'] else 0
            exploration = np.mean(learning_data['exploration'][-10:]) if learning_data['exploration'] else 0
            loss = np.mean(learning_data.get('loss', [0])[-10:])
            avg_time = np.mean(learning_data.get('completion_times', [0])[-10:])
            memory_usage = learning_data.get('memory_usage', 0)
            
            # Format HTML
            html = html.format(
                episode=episode,
                reward_plot=reward_plot,
                accuracy_plot=accuracy_plot,
                exploration_plot=exploration_plot,
                avg_reward=avg_reward,
                accuracy=accuracy,
                exploration=exploration,
                loss=loss,
                avg_time=avg_time,
                memory_usage=memory_usage
            )
            
            # Save dashboard
            filename = f'dashboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            with open(filepath, 'w') as f:
                f.write(html)
                
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            return ""
            
    def _calculate_diff(self, predicted: str, actual: str) -> str:
        """Calculate diff between predicted and actual completions"""
        try:
            from difflib import ndiff
            diff = list(ndiff(predicted.splitlines(keepends=True),
                            actual.splitlines(keepends=True)))
            
            html_diff = ""
            for line in diff:
                if line.startswith('+'):
                    html_diff += f'<span class="diff-add">{line}</span>'
                elif line.startswith('-'):
                    html_diff += f'<span class="diff-remove">{line}</span>'
                else:
                    html_diff += line
                    
            return html_diff
            
        except Exception as e:
            logger.error(f"Error calculating diff: {str(e)}")
            return ""
            
    def create_attention_map(self, attention_data: Dict[str, Any], episode: int) -> str:
        """Create visualization of attention maps"""
        try:
            # Create figure
            fig = go.Figure()
            
            # Add attention heatmap
            fig.add_trace(
                go.Heatmap(
                    z=attention_data['attention_matrix'],
                    x=attention_data['input_tokens'],
                    y=attention_data['output_tokens'],
                    colorscale='Viridis',
                    name='Attention'
                )
            )
            
            fig.update_layout(
                title=f'Attention Map (Episode {episode})',
                xaxis_title='Input Tokens',
                yaxis_title='Output Tokens'
            )
            
            # Save plot
            filename = f'attention_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating attention map: {str(e)}")
            return ""
            
    def create_gradient_flow(self, gradient_data: Dict[str, Any], episode: int) -> str:
        """Create visualization of gradient flow"""
        try:
            # Create figure
            fig = go.Figure()
            
            # Add gradient magnitude plot
            fig.add_trace(
                go.Scatter(
                    x=gradient_data['layers'],
                    y=gradient_data['gradient_magnitudes'],
                    mode='lines+markers',
                    name='Gradient Magnitude'
                )
            )
            
            # Add gradient direction plot
            fig.add_trace(
                go.Scatter(
                    x=gradient_data['layers'],
                    y=gradient_data['gradient_directions'],
                    mode='lines+markers',
                    name='Gradient Direction'
                )
            )
            
            fig.update_layout(
                title=f'Gradient Flow (Episode {episode})',
                xaxis_title='Layer',
                yaxis_title='Value'
            )
            
            # Save plot
            filename = f'gradients_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating gradient flow: {str(e)}")
            return ""
            
    def create_memory_patterns(self, memory_data: Dict[str, Any], episode: int) -> str:
        """Create visualization of memory usage patterns"""
        try:
            # Create figure
            fig = go.Figure()
            
            # Add memory usage plot
            fig.add_trace(
                go.Scatter(
                    x=memory_data['timestamps'],
                    y=memory_data['memory_usage'],
                    mode='lines+markers',
                    name='Memory Usage',
                    line=dict(color='blue')
                )
            )
            
            # Add memory allocation plot
            fig.add_trace(
                go.Scatter(
                    x=memory_data['timestamps'],
                    y=memory_data['memory_allocated'],
                    mode='lines+markers',
                    name='Memory Allocated',
                    line=dict(color='green')
                )
            )
            
            # Add memory cached plot
            fig.add_trace(
                go.Scatter(
                    x=memory_data['timestamps'],
                    y=memory_data['memory_cached'],
                    mode='lines+markers',
                    name='Memory Cached',
                    line=dict(color='red')
                )
            )
            
            # Add memory peak plot
            fig.add_trace(
                go.Scatter(
                    x=memory_data['timestamps'],
                    y=memory_data['memory_peak'],
                    mode='lines+markers',
                    name='Memory Peak',
                    line=dict(color='purple')
                )
            )
            
            fig.update_layout(
                title=f'Memory Usage Patterns (Episode {episode})',
                xaxis_title='Time',
                yaxis_title='Memory (MB)',
                showlegend=True
            )
            
            # Add memory statistics table
            table_data = {
                'Metric': ['Current Usage', 'Peak Usage', 'Allocated', 'Cached'],
                'Value (MB)': [
                    memory_data['memory_usage'][-1],
                    max(memory_data['memory_peak']),
                    memory_data['memory_allocated'][-1],
                    memory_data['memory_cached'][-1]
                ]
            }
            
            fig.add_trace(
                go.Table(
                    header=dict(values=list(table_data.keys())),
                    cells=dict(values=list(table_data.values()))
                )
            )
            
            # Save plot
            filename = f'memory_patterns_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating memory patterns visualization: {str(e)}")
            return ""
            
    def create_code_quality_metrics(self, quality_data: Dict[str, Any], episode: int) -> str:
        """Create visualization of code quality metrics"""
        try:
            # Create figure
            fig = go.Figure()
            
            # Add complexity plot
            fig.add_trace(
                go.Scatter(
                    x=quality_data['episodes'],
                    y=quality_data['complexity'],
                    mode='lines+markers',
                    name='Code Complexity',
                    line=dict(color='red')
                )
            )
            
            # Add maintainability plot
            fig.add_trace(
                go.Scatter(
                    x=quality_data['episodes'],
                    y=quality_data['maintainability'],
                    mode='lines+markers',
                    name='Maintainability',
                    line=dict(color='green')
                )
            )
            
            # Add readability plot
            fig.add_trace(
                go.Scatter(
                    x=quality_data['episodes'],
                    y=quality_data['readability'],
                    mode='lines+markers',
                    name='Readability',
                    line=dict(color='blue')
                )
            )
            
            # Add test coverage plot
            fig.add_trace(
                go.Scatter(
                    x=quality_data['episodes'],
                    y=quality_data['test_coverage'],
                    mode='lines+markers',
                    name='Test Coverage',
                    line=dict(color='purple')
                )
            )
            
            fig.update_layout(
                title=f'Code Quality Metrics (Episode {episode})',
                xaxis_title='Episode',
                yaxis_title='Score',
                showlegend=True
            )
            
            # Add quality statistics table
            table_data = {
                'Metric': ['Complexity', 'Maintainability', 'Readability', 'Test Coverage'],
                'Current': [
                    quality_data['complexity'][-1],
                    quality_data['maintainability'][-1],
                    quality_data['readability'][-1],
                    quality_data['test_coverage'][-1]
                ],
                'Average': [
                    np.mean(quality_data['complexity']),
                    np.mean(quality_data['maintainability']),
                    np.mean(quality_data['readability']),
                    np.mean(quality_data['test_coverage'])
                ]
            }
            
            fig.add_trace(
                go.Table(
                    header=dict(values=list(table_data.keys())),
                    cells=dict(values=list(table_data.values()))
                )
            )
            
            # Save plot
            filename = f'code_quality_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating code quality metrics visualization: {str(e)}")
            return ""
            
    def create_performance_metrics(self, performance_data: Dict[str, Any], episode: int) -> str:
        """Create visualization of performance metrics"""
        try:
            # Create figure
            fig = go.Figure()
            
            # Add memory usage plot
            fig.add_trace(
                go.Scatter(
                    x=performance_data['timestamps'],
                    y=performance_data['memory_usage'],
                    mode='lines+markers',
                    name='Memory Usage'
                )
            )
            
            # Add CPU usage plot
            fig.add_trace(
                go.Scatter(
                    x=performance_data['timestamps'],
                    y=performance_data['cpu_usage'],
                    mode='lines+markers',
                    name='CPU Usage'
                )
            )
            
            # Add GPU usage plot if available
            if 'gpu_usage' in performance_data:
                fig.add_trace(
                    go.Scatter(
                        x=performance_data['timestamps'],
                        y=performance_data['gpu_usage'],
                        mode='lines+markers',
                        name='GPU Usage'
                    )
                )
                
            fig.update_layout(
                title=f'Performance Metrics (Episode {episode})',
                xaxis_title='Time',
                yaxis_title='Usage (%)'
            )
            
            # Save plot
            filename = f'performance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating performance metrics: {str(e)}")
            return ""
            
    def create_model_comparison(self, comparison_data: Dict[str, Any]) -> str:
        """Create visualization comparing different models"""
        try:
            # Create figure
            fig = go.Figure()
            
            # Add metrics for each model
            for model_name, metrics in comparison_data.items():
                fig.add_trace(
                    go.Scatter(
                        x=metrics['episodes'],
                        y=metrics['rewards'],
                        mode='lines+markers',
                        name=f'{model_name} - Rewards'
                    )
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=metrics['episodes'],
                        y=metrics['accuracy'],
                        mode='lines+markers',
                        name=f'{model_name} - Accuracy'
                    )
                )
                
            fig.update_layout(
                title='Model Comparison',
                xaxis_title='Episode',
                yaxis_title='Value'
            )
            
            # Save plot
            filename = f'comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating model comparison: {str(e)}")
            return ""
            
    def create_hyperparameter_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Create visualization of hyperparameter analysis"""
        try:
            # Create figure
            fig = go.Figure()
            
            # Add parameter sweep results
            for param_name, results in analysis_data.items():
                fig.add_trace(
                    go.Scatter(
                        x=results['values'],
                        y=results['rewards'],
                        mode='lines+markers',
                        name=f'{param_name} - Rewards'
                    )
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=results['values'],
                        y=results['accuracy'],
                        mode='lines+markers',
                        name=f'{param_name} - Accuracy'
                    )
                )
                
            fig.update_layout(
                title='Hyperparameter Analysis',
                xaxis_title='Parameter Value',
                yaxis_title='Score'
            )
            
            # Save plot
            filename = f'hyperparams_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating hyperparameter analysis: {str(e)}")
            return ""
            
    def create_model_architecture(self, model: torch.nn.Module, episode: int) -> str:
        """Create visualization of model architecture"""
        try:
            # Create figure
            fig = go.Figure()
            
            # Get model structure
            layers = []
            connections = []
            current_y = 0
            
            def add_layer(name, size, layer_type):
                nonlocal current_y
                layers.append({
                    'name': name,
                    'size': size,
                    'type': layer_type,
                    'y': current_y
                })
                current_y += 1
                
            def add_connection(from_layer, to_layer):
                connections.append({
                    'from': from_layer,
                    'to': to_layer
                })
                
            # Traverse model structure
            def traverse_module(module, name=''):
                if isinstance(module, torch.nn.Linear):
                    add_layer(f"{name}Linear", module.out_features, 'linear')
                elif isinstance(module, torch.nn.Conv2d):
                    add_layer(f"{name}Conv2d", module.out_channels, 'conv')
                elif isinstance(module, torch.nn.LSTM):
                    add_layer(f"{name}LSTM", module.hidden_size, 'lstm')
                elif isinstance(module, torch.nn.Transformer):
                    add_layer(f"{name}Transformer", module.d_model, 'transformer')
                    
                for child_name, child in module.named_children():
                    traverse_module(child, f"{name}{child_name}_")
                    
            traverse_module(model)
            
            # Add layer nodes
            for layer in layers:
                fig.add_trace(
                    go.Scatter(
                        x=[0],
                        y=[layer['y']],
                        mode='markers+text',
                        name=layer['name'],
                        text=layer['name'],
                        textposition="top center",
                        marker=dict(
                            size=20,
                            color='blue' if layer['type'] == 'linear' else
                                  'red' if layer['type'] == 'conv' else
                                  'green' if layer['type'] == 'lstm' else
                                  'purple'
                        )
                    )
                )
                
            # Add connections
            for conn in connections:
                fig.add_trace(
                    go.Scatter(
                        x=[0, 0],
                        y=[conn['from']['y'], conn['to']['y']],
                        mode='lines',
                        line=dict(color='gray', width=1),
                        showlegend=False
                    )
                )
                
            fig.update_layout(
                title=f'Model Architecture (Episode {episode})',
                showlegend=True,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            
            # Save plot
            filename = f'architecture_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating model architecture visualization: {str(e)}")
            return ""
            
    def create_code_coverage_metrics(self, coverage_data: Dict[str, Any], episode: int) -> str:
        """Create visualization of code coverage metrics"""
        try:
            # Create figure
            fig = go.Figure()
            
            # Add line coverage plot
            fig.add_trace(
                go.Scatter(
                    x=coverage_data['episodes'],
                    y=coverage_data['line_coverage'],
                    mode='lines+markers',
                    name='Line Coverage'
                )
            )
            
            # Add branch coverage plot
            fig.add_trace(
                go.Scatter(
                    x=coverage_data['episodes'],
                    y=coverage_data['branch_coverage'],
                    mode='lines+markers',
                    name='Branch Coverage'
                )
            )
            
            # Add function coverage plot
            fig.add_trace(
                go.Scatter(
                    x=coverage_data['episodes'],
                    y=coverage_data['function_coverage'],
                    mode='lines+markers',
                    name='Function Coverage'
                )
            )
            
            # Add complexity plot
            fig.add_trace(
                go.Scatter(
                    x=coverage_data['episodes'],
                    y=coverage_data['complexity'],
                    mode='lines+markers',
                    name='Code Complexity'
                )
            )
            
            fig.update_layout(
                title=f'Code Coverage Metrics (Episode {episode})',
                xaxis_title='Episode',
                yaxis_title='Coverage (%)',
                yaxis=dict(range=[0, 100])
            )
            
            # Add coverage summary table
            table_data = {
                'Metric': ['Line Coverage', 'Branch Coverage', 'Function Coverage', 'Complexity'],
                'Current': [
                    coverage_data['line_coverage'][-1],
                    coverage_data['branch_coverage'][-1],
                    coverage_data['function_coverage'][-1],
                    coverage_data['complexity'][-1]
                ],
                'Average': [
                    np.mean(coverage_data['line_coverage']),
                    np.mean(coverage_data['branch_coverage']),
                    np.mean(coverage_data['function_coverage']),
                    np.mean(coverage_data['complexity'])
                ]
            }
            
            fig.add_trace(
                go.Table(
                    header=dict(values=list(table_data.keys())),
                    cells=dict(values=list(table_data.values()))
                )
            )
            
            # Save plot
            filename = f'coverage_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating code coverage visualization: {str(e)}")
            return ""
            
    def create_model_architecture_comparison(self, models: Dict[str, torch.nn.Module], episode: int) -> str:
        """Create visualization comparing different model architectures"""
        try:
            # Create figure
            fig = go.Figure()
            
            # Add architecture for each model
            for model_name, model in models.items():
                # Get model structure
                layers = []
                connections = []
                current_y = 0
                
                def add_layer(name, size, layer_type):
                    nonlocal current_y
                    layers.append({
                        'name': name,
                        'size': size,
                        'type': layer_type,
                        'y': current_y,
                        'model': model_name
                    })
                    current_y += 1
                    
                def add_connection(from_layer, to_layer):
                    connections.append({
                        'from': from_layer,
                        'to': to_layer,
                        'model': model_name
                    })
                    
                # Traverse model structure
                def traverse_module(module, name=''):
                    if isinstance(module, torch.nn.Linear):
                        add_layer(f"{name}Linear", module.out_features, 'linear')
                    elif isinstance(module, torch.nn.Conv2d):
                        add_layer(f"{name}Conv2d", module.out_channels, 'conv')
                    elif isinstance(module, torch.nn.LSTM):
                        add_layer(f"{name}LSTM", module.hidden_size, 'lstm')
                    elif isinstance(module, torch.nn.Transformer):
                        add_layer(f"{name}Transformer", module.d_model, 'transformer')
                        
                    for child_name, child in module.named_children():
                        traverse_module(child, f"{name}{child_name}_")
                        
                traverse_module(model)
                
                # Add layer nodes
                for layer in layers:
                    fig.add_trace(
                        go.Scatter(
                            x=[0],
                            y=[layer['y']],
                            mode='markers+text',
                            name=f"{model_name} - {layer['name']}",
                            text=layer['name'],
                            textposition="top center",
                            marker=dict(
                                size=20,
                                color='blue' if layer['type'] == 'linear' else
                                      'red' if layer['type'] == 'conv' else
                                      'green' if layer['type'] == 'lstm' else
                                      'purple'
                            )
                        )
                    )
                    
                # Add connections
                for conn in connections:
                    fig.add_trace(
                        go.Scatter(
                            x=[0, 0],
                            y=[conn['from']['y'], conn['to']['y']],
                            mode='lines',
                            line=dict(color='gray', width=1),
                            showlegend=False
                        )
                    )
                    
            fig.update_layout(
                title=f'Model Architecture Comparison (Episode {episode})',
                showlegend=True,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            
            # Save plot
            filename = f'architecture_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating model architecture comparison: {str(e)}")
            return "" 