import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import json
import time
import psutil
import GPUtil
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
import pandas as pd
from threading import Thread, Event, Lock
import requests
from prometheus_client import start_http_server, Counter, Gauge, Histogram
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    timestamp: str
    model_name: str
    version: str
    latency: float
    throughput: float
    error_rate: float
    resource_usage: Dict
    custom_metrics: Dict = field(default_factory=dict)

class PerformanceMonitor:
    """Monitors and analyzes model performance metrics"""
    
    def __init__(self, metrics_dir: str = "metrics", prometheus_port: int = 9090):
        """Initialize the performance monitor
        
        Args:
            metrics_dir: Directory for storing metrics
            prometheus_port: Port for Prometheus metrics server
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Prometheus metrics
        self.latency_histogram = Histogram(
            'model_latency_seconds',
            'Model prediction latency in seconds',
            ['model_name', 'version']
        )
        
        self.throughput_counter = Counter(
            'model_requests_total',
            'Total number of model requests',
            ['model_name', 'version']
        )
        
        self.error_counter = Counter(
            'model_errors_total',
            'Total number of model errors',
            ['model_name', 'version']
        )
        
        self.resource_gauge = Gauge(
            'model_resource_usage',
            'Model resource usage',
            ['model_name', 'version', 'resource_type']
        )
        
        # Start Prometheus server
        try:
            start_http_server(prometheus_port)
            logger.info(f"Started Prometheus metrics server on port {prometheus_port}")
        except Exception as e:
            logger.error(f"Failed to start Prometheus server: {str(e)}")
            
        # Initialize monitoring state
        self.monitoring_thread = None
        self.stop_event = Event()
        self.metrics_lock = Lock()
        self.active_models = {}
        
    def start_monitoring(self, model_name: str, version: str, endpoint: str) -> bool:
        """Start monitoring a model's performance
        
        Args:
            model_name: Name of the model
            version: Model version
            endpoint: Model API endpoint
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if model_name in self.active_models:
                logger.warning(f"Model {model_name} is already being monitored")
                return False
                
            self.active_models[model_name] = {
                "version": version,
                "endpoint": endpoint,
                "start_time": datetime.now().isoformat()
            }
            
            # Start monitoring thread if not already running
            if not self.monitoring_thread or not self.monitoring_thread.is_alive():
                self.stop_event.clear()
                self.monitoring_thread = Thread(target=self._monitor_loop)
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()
                
            logger.info(f"Started monitoring model {model_name} version {version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {str(e)}")
            return False
            
    def stop_monitoring(self, model_name: str) -> bool:
        """Stop monitoring a model's performance
        
        Args:
            model_name: Name of the model
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if model_name not in self.active_models:
                logger.warning(f"Model {model_name} is not being monitored")
                return False
                
            del self.active_models[model_name]
            
            # Stop monitoring thread if no active models
            if not self.active_models:
                self.stop_event.set()
                if self.monitoring_thread:
                    self.monitoring_thread.join()
                    
            logger.info(f"Stopped monitoring model {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {str(e)}")
            return False
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self.stop_event.is_set():
            try:
                for model_name, model_info in self.active_models.items():
                    metrics = self._collect_metrics(model_name, model_info)
                    if metrics:
                        self._save_metrics(metrics)
                        
                time.sleep(5)  # Collect metrics every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(5)  # Wait before retrying
                
    def _collect_metrics(self, model_name: str, model_info: Dict) -> Optional[PerformanceMetrics]:
        """Collect performance metrics for a model
        
        Args:
            model_name: Name of the model
            model_info: Model information
            
        Returns:
            Optional[PerformanceMetrics]: Collected metrics if successful, None otherwise
        """
        try:
            # Collect resource usage
            resource_usage = self._collect_resource_usage()
            
            # Collect API metrics
            api_metrics = self._collect_api_metrics(model_info["endpoint"])
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now().isoformat(),
                model_name=model_name,
                version=model_info["version"],
                latency=api_metrics["latency"],
                throughput=api_metrics["throughput"],
                error_rate=api_metrics["error_rate"],
                resource_usage=resource_usage,
                custom_metrics=api_metrics.get("custom_metrics", {})
            )
            
            # Update Prometheus metrics
            self._update_prometheus_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {str(e)}")
            return None
            
    def _collect_resource_usage(self) -> Dict:
        """Collect system resource usage
        
        Returns:
            Dict: Resource usage metrics
        """
        try:
            metrics = {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
            
            # Try to get GPU metrics if available
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    metrics["gpu_usage"] = [gpu.load * 100 for gpu in gpus]
                    metrics["gpu_memory"] = [gpu.memoryUtil * 100 for gpu in gpus]
            except:
                pass
                
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect resource usage: {str(e)}")
            return {}
            
    def _collect_api_metrics(self, endpoint: str) -> Dict:
        """Collect API performance metrics
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Dict: API metrics
        """
        try:
            # Send test request
            start_time = time.time()
            response = requests.get(f"{endpoint}/health")
            latency = time.time() - start_time
            
            metrics = {
                "latency": latency,
                "throughput": 1,  # Will be updated by actual request count
                "error_rate": 0.0,  # Will be updated by actual error count
                "custom_metrics": {}
            }
            
            # Parse response for custom metrics
            if response.status_code == 200:
                try:
                    custom_metrics = response.json()
                    metrics["custom_metrics"] = custom_metrics
                except:
                    pass
                    
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect API metrics: {str(e)}")
            return {
                "latency": 0.0,
                "throughput": 0,
                "error_rate": 1.0,
                "custom_metrics": {}
            }
            
    def _update_prometheus_metrics(self, metrics: PerformanceMetrics):
        """Update Prometheus metrics
        
        Args:
            metrics: Performance metrics
        """
        try:
            # Update latency histogram
            self.latency_histogram.labels(
                model_name=metrics.model_name,
                version=metrics.version
            ).observe(metrics.latency)
            
            # Update throughput counter
            self.throughput_counter.labels(
                model_name=metrics.model_name,
                version=metrics.version
            ).inc(metrics.throughput)
            
            # Update error counter
            if metrics.error_rate > 0:
                self.error_counter.labels(
                    model_name=metrics.model_name,
                    version=metrics.version
                ).inc(metrics.error_rate)
                
            # Update resource gauges
            for resource_type, value in metrics.resource_usage.items():
                if isinstance(value, list):
                    for i, v in enumerate(value):
                        self.resource_gauge.labels(
                            model_name=metrics.model_name,
                            version=metrics.version,
                            resource_type=f"{resource_type}_{i}"
                        ).set(v)
                else:
                    self.resource_gauge.labels(
                        model_name=metrics.model_name,
                        version=metrics.version,
                        resource_type=resource_type
                    ).set(value)
                    
        except Exception as e:
            logger.error(f"Failed to update Prometheus metrics: {str(e)}")
            
    def _save_metrics(self, metrics: PerformanceMetrics):
        """Save collected metrics to file
        
        Args:
            metrics: Performance metrics to save
        """
        try:
            metrics_file = self.metrics_dir / f"{metrics.model_name}_{metrics.version}.json"
            
            with self.metrics_lock:
                if metrics_file.exists():
                    with open(metrics_file, 'r') as f:
                        existing_metrics = json.load(f)
                else:
                    existing_metrics = []
                    
                existing_metrics.append(metrics.__dict__)
                
                with open(metrics_file, 'w') as f:
                    json.dump(existing_metrics, f, indent=4)
                    
        except Exception as e:
            logger.error(f"Failed to save metrics: {str(e)}")
            
    def get_metrics(self, model_name: str, version: Optional[str] = None) -> List[Dict]:
        """Get performance metrics for a model
        
        Args:
            model_name: Name of the model
            version: Optional model version
            
        Returns:
            List[Dict]: List of performance metrics
        """
        try:
            metrics_file = self.metrics_dir / f"{model_name}_{version}.json" if version else None
            
            if metrics_file and metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    return json.load(f)
                    
            # If no specific version requested, return all versions
            metrics = []
            for file in self.metrics_dir.glob(f"{model_name}_*.json"):
                with open(file, 'r') as f:
                    metrics.extend(json.load(f))
                    
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {str(e)}")
            return []
            
    def generate_performance_report(self, model_name: str, version: Optional[str] = None) -> Dict:
        """Generate performance report for a model
        
        Args:
            model_name: Name of the model
            version: Optional model version
            
        Returns:
            Dict: Performance report
        """
        try:
            metrics = self.get_metrics(model_name, version)
            if not metrics:
                return {}
                
            # Convert metrics to DataFrame for analysis
            df = pd.DataFrame(metrics)
            
            report = {
                "model_name": model_name,
                "version": version or "all",
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_requests": len(metrics),
                    "avg_latency": df["latency"].mean(),
                    "avg_throughput": df["throughput"].mean(),
                    "avg_error_rate": df["error_rate"].mean(),
                    "resource_usage": {
                        "avg_cpu": df["resource_usage"].apply(lambda x: x.get("cpu_percent", 0)).mean(),
                        "avg_memory": df["resource_usage"].apply(lambda x: x.get("memory_percent", 0)).mean(),
                        "avg_disk": df["resource_usage"].apply(lambda x: x.get("disk_usage", 0)).mean()
                    }
                },
                "trends": {
                    "latency": self._calculate_trend(df["latency"]),
                    "throughput": self._calculate_trend(df["throughput"]),
                    "error_rate": self._calculate_trend(df["error_rate"])
                }
            }
            
            # Add custom metrics if available
            if "custom_metrics" in df.columns:
                report["custom_metrics"] = self._analyze_custom_metrics(df["custom_metrics"])
                
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {str(e)}")
            return {}
            
    def _calculate_trend(self, series: pd.Series) -> Dict:
        """Calculate trend for a metric series
        
        Args:
            series: Metric series
            
        Returns:
            Dict: Trend information
        """
        try:
            if len(series) < 2:
                return {"direction": "stable", "magnitude": 0.0}
                
            # Calculate linear regression
            x = np.arange(len(series))
            slope = np.polyfit(x, series, 1)[0]
            
            # Determine trend direction and magnitude
            if abs(slope) < 0.01:
                direction = "stable"
            elif slope > 0:
                direction = "increasing"
            else:
                direction = "decreasing"
                
            magnitude = abs(slope) / series.mean() if series.mean() != 0 else 0.0
            
            return {
                "direction": direction,
                "magnitude": magnitude
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate trend: {str(e)}")
            return {"direction": "unknown", "magnitude": 0.0}
            
    def _analyze_custom_metrics(self, custom_metrics: pd.Series) -> Dict:
        """Analyze custom metrics
        
        Args:
            custom_metrics: Series of custom metrics
            
        Returns:
            Dict: Analysis results
        """
        try:
            analysis = {}
            
            # Extract all custom metric keys
            metric_keys = set()
            for metrics in custom_metrics:
                if isinstance(metrics, dict):
                    metric_keys.update(metrics.keys())
                    
            # Analyze each metric
            for key in metric_keys:
                values = []
                for metrics in custom_metrics:
                    if isinstance(metrics, dict) and key in metrics:
                        values.append(metrics[key])
                        
                if values:
                    analysis[key] = {
                        "mean": np.mean(values),
                        "std": np.std(values),
                        "min": np.min(values),
                        "max": np.max(values)
                    }
                    
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze custom metrics: {str(e)}")
            return {}
            
    def plot_performance_metrics(self, model_name: str, version: Optional[str] = None) -> bool:
        """Generate performance visualization plots
        
        Args:
            model_name: Name of the model
            version: Optional model version
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            metrics = self.get_metrics(model_name, version)
            if not metrics:
                return False
                
            # Convert metrics to DataFrame
            df = pd.DataFrame(metrics)
            
            # Create plots directory
            plots_dir = self.metrics_dir / "plots"
            plots_dir.mkdir(exist_ok=True)
            
            # Set style
            plt.style.use('seaborn')
            
            # Plot latency over time
            plt.figure(figsize=(12, 6))
            plt.plot(df["timestamp"], df["latency"])
            plt.title(f"Latency Over Time - {model_name}")
            plt.xlabel("Time")
            plt.ylabel("Latency (seconds)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(plots_dir / f"{model_name}_latency.png")
            plt.close()
            
            # Plot resource usage
            plt.figure(figsize=(12, 6))
            resource_data = pd.DataFrame([
                {
                    "timestamp": row["timestamp"],
                    "cpu": row["resource_usage"].get("cpu_percent", 0),
                    "memory": row["resource_usage"].get("memory_percent", 0),
                    "disk": row["resource_usage"].get("disk_usage", 0)
                }
                for row in metrics
            ])
            
            plt.plot(resource_data["timestamp"], resource_data["cpu"], label="CPU")
            plt.plot(resource_data["timestamp"], resource_data["memory"], label="Memory")
            plt.plot(resource_data["timestamp"], resource_data["disk"], label="Disk")
            
            plt.title(f"Resource Usage Over Time - {model_name}")
            plt.xlabel("Time")
            plt.ylabel("Usage (%)")
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(plots_dir / f"{model_name}_resources.png")
            plt.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to plot performance metrics: {str(e)}")
            return False
            
    def clean_metrics(self, model_name: str, version: Optional[str] = None) -> bool:
        """Clean up metrics data
        
        Args:
            model_name: Name of the model
            version: Optional model version
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if version:
                # Clean specific version
                metrics_file = self.metrics_dir / f"{model_name}_{version}.json"
                if metrics_file.exists():
                    metrics_file.unlink()
                    
                plot_file = self.metrics_dir / "plots" / f"{model_name}_{version}.png"
                if plot_file.exists():
                    plot_file.unlink()
            else:
                # Clean all versions
                for file in self.metrics_dir.glob(f"{model_name}_*.json"):
                    file.unlink()
                    
                for file in (self.metrics_dir / "plots").glob(f"{model_name}_*.png"):
                    file.unlink()
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to clean metrics: {str(e)}")
            return False 