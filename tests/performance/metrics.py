import time
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Data class for storing performance metrics."""
    timestamp: float
    metric_type: str
    value: float
    unit: str
    metadata: Dict[str, Any]

class MetricsCollector:
    """Collects and stores performance metrics."""
    
    def __init__(self, baseline_file: Optional[str] = None):
        self.metrics: List[PerformanceMetric] = []
        self.baseline = self._load_baseline(baseline_file) if baseline_file else None
        self._lock = asyncio.Lock()
        
    def _load_baseline(self, baseline_file: str) -> Dict[str, Any]:
        """Load baseline metrics from file."""
        try:
            with open(baseline_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Baseline file {baseline_file} not found")
            return {}
            
    async def record_metric(
        self,
        metric_type: str,
        value: float,
        unit: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a new metric with thread safety."""
        async with self._lock:
            metric = PerformanceMetric(
                timestamp=time.time(),
                metric_type=metric_type,
                value=value,
                unit=unit,
                metadata=metadata or {}
            )
            self.metrics.append(metric)
            
    def get_metrics_by_type(self, metric_type: str) -> List[PerformanceMetric]:
        """Get all metrics of a specific type."""
        return [m for m in self.metrics if m.metric_type == metric_type]
        
    def get_metrics_df(self) -> pd.DataFrame:
        """Convert metrics to pandas DataFrame for analysis."""
        return pd.DataFrame([asdict(m) for m in self.metrics])
        
    def save_metrics(self, filename: str) -> None:
        """Save metrics to JSON file."""
        with open(filename, 'w') as f:
            json.dump([asdict(m) for m in self.metrics], f, indent=2)
            
    def compare_with_baseline(self) -> Dict[str, Any]:
        """Compare current metrics with baseline."""
        if not self.baseline:
            return {}
            
        current_df = self.get_metrics_df()
        baseline_df = pd.DataFrame(self.baseline)
        
        comparison = {}
        for metric_type in current_df['metric_type'].unique():
            current = current_df[current_df['metric_type'] == metric_type]['value']
            baseline = baseline_df[baseline_df['metric_type'] == metric_type]['value']
            
            if not baseline.empty:
                comparison[metric_type] = {
                    'current_mean': current.mean(),
                    'baseline_mean': baseline.mean(),
                    'difference_percent': ((current.mean() - baseline.mean()) / baseline.mean()) * 100
                }
                
        return comparison

class MetricsVisualizer:
    """Generates visualizations for performance metrics."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def generate_plots(self, output_dir: str) -> None:
        """Generate various performance plots."""
        df = self.collector.get_metrics_df()
        
        # Create plots in a thread pool to avoid blocking
        await asyncio.get_event_loop().run_in_executor(
            self.executor,
            self._generate_plots_internal,
            df,
            output_dir
        )
        
    def _generate_plots_internal(self, df: pd.DataFrame, output_dir: str) -> None:
        """Internal method to generate plots."""
        # Response time over time
        plt.figure(figsize=(12, 6))
        response_times = df[df['metric_type'] == 'response_time']
        plt.plot(response_times['timestamp'], response_times['value'])
        plt.title('Response Time Over Time')
        plt.xlabel('Time')
        plt.ylabel('Response Time (ms)')
        plt.savefig(f"{output_dir}/response_time.png")
        plt.close()
        
        # Error rate
        plt.figure(figsize=(12, 6))
        error_rates = df[df['metric_type'] == 'error_rate']
        plt.plot(error_rates['timestamp'], error_rates['value'])
        plt.title('Error Rate Over Time')
        plt.xlabel('Time')
        plt.ylabel('Error Rate (%)')
        plt.savefig(f"{output_dir}/error_rate.png")
        plt.close()
        
        # Resource usage
        plt.figure(figsize=(12, 6))
        memory_usage = df[df['metric_type'] == 'memory_usage']
        plt.plot(memory_usage['timestamp'], memory_usage['value'])
        plt.title('Memory Usage Over Time')
        plt.xlabel('Time')
        plt.ylabel('Memory Usage (MB)')
        plt.savefig(f"{output_dir}/memory_usage.png")
        plt.close()
        
        # Concurrent users
        plt.figure(figsize=(12, 6))
        users = df[df['metric_type'] == 'concurrent_users']
        plt.plot(users['timestamp'], users['value'])
        plt.title('Concurrent Users Over Time')
        plt.xlabel('Time')
        plt.ylabel('Number of Users')
        plt.savefig(f"{output_dir}/concurrent_users.png")
        plt.close()

class PerformanceReporter:
    """Generates performance test reports."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector
        self.visualizer = MetricsVisualizer(metrics_collector)
        
    async def generate_report(self, output_dir: str) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        # Generate visualizations
        await self.visualizer.generate_plots(output_dir)
        
        # Calculate statistics
        df = self.collector.get_metrics_df()
        stats = {}
        
        for metric_type in df['metric_type'].unique():
            metric_data = df[df['metric_type'] == metric_type]['value']
            stats[metric_type] = {
                'mean': metric_data.mean(),
                'median': metric_data.median(),
                'p95': metric_data.quantile(0.95),
                'p99': metric_data.quantile(0.99),
                'min': metric_data.min(),
                'max': metric_data.max()
            }
            
        # Compare with baseline
        baseline_comparison = self.collector.compare_with_baseline()
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'baseline_comparison': baseline_comparison,
            'issues': self._identify_issues(stats, baseline_comparison)
        }
        
        # Save report
        with open(f"{output_dir}/report.json", 'w') as f:
            json.dump(report, f, indent=2)
            
        return report
        
    def _identify_issues(self, stats: Dict[str, Any], baseline_comparison: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential performance issues."""
        issues = []
        
        # Check response times
        if 'response_time' in stats:
            response_time = stats['response_time']
            if response_time['p95'] > 1000:  # 1 second
                issues.append({
                    'type': 'high_response_time',
                    'metric': 'response_time',
                    'value': response_time['p95'],
                    'threshold': 1000,
                    'severity': 'high'
                })
                
        # Check error rates
        if 'error_rate' in stats:
            error_rate = stats['error_rate']
            if error_rate['mean'] > 5:  # 5%
                issues.append({
                    'type': 'high_error_rate',
                    'metric': 'error_rate',
                    'value': error_rate['mean'],
                    'threshold': 5,
                    'severity': 'high'
                })
                
        # Check memory usage
        if 'memory_usage' in stats:
            memory_usage = stats['memory_usage']
            if memory_usage['max'] > 1000:  # 1GB
                issues.append({
                    'type': 'high_memory_usage',
                    'metric': 'memory_usage',
                    'value': memory_usage['max'],
                    'threshold': 1000,
                    'severity': 'medium'
                })
                
        # Check baseline deviations
        for metric, comparison in baseline_comparison.items():
            if abs(comparison['difference_percent']) > 20:  # 20% deviation
                issues.append({
                    'type': 'baseline_deviation',
                    'metric': metric,
                    'deviation': comparison['difference_percent'],
                    'threshold': 20,
                    'severity': 'medium'
                })
                
        return issues 