from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import psutil
import time
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path
import yaml
from collections import deque
import threading
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class ResourceMetrics:
    """Resource usage metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Tuple[float, float]  # (bytes_sent, bytes_recv)
    gpu_percent: Optional[float] = None
    gpu_memory_percent: Optional[float] = None

@dataclass
class ResourcePrediction:
    """Resource usage prediction"""
    timestamp: datetime
    cpu_prediction: float
    memory_prediction: float
    disk_prediction: float
    network_prediction: Tuple[float, float]
    confidence: float

class ResourceMonitor:
    """Monitor and predict resource usage"""
    
    def __init__(self, history_size: int = 1000, prediction_window: int = 60):
        self.history_size = history_size
        self.prediction_window = prediction_window
        self.metrics_history = deque(maxlen=history_size)
        self.predictions_history = deque(maxlen=history_size)
        self._load_config()
        self._setup_monitoring()
        self._monitoring_thread = None
        self._stop_monitoring = False
        
    def _load_config(self) -> None:
        """Load monitoring configuration"""
        try:
            config_path = Path("src/core/resources/config/monitoring.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    self.config = yaml.safe_load(f)
            else:
                logger.warning("Monitoring configuration not found")
                self.config = {}
                
        except Exception as e:
            logger.error(f"Error loading monitoring configuration: {str(e)}")
            self.config = {}
            
    def _setup_monitoring(self) -> None:
        """Setup resource monitoring"""
        try:
            # Initialize monitoring thresholds
            self.thresholds = self.config.get("thresholds", {
                "cpu": {"warning": 80, "critical": 90},
                "memory": {"warning": 80, "critical": 90},
                "disk": {"warning": 80, "critical": 90},
                "network": {"warning": 80, "critical": 90}
            })
            
            # Initialize monitoring intervals
            self.intervals = self.config.get("intervals", {
                "metrics": 1,  # seconds
                "prediction": 60,  # seconds
                "alert": 300  # seconds
            })
            
            # Initialize prediction parameters
            self.prediction_params = self.config.get("prediction", {
                "window_size": 60,
                "min_samples": 30,
                "confidence_threshold": 0.8
            })
            
        except Exception as e:
            logger.error(f"Error setting up monitoring: {str(e)}")
            
    async def start_monitoring(self) -> None:
        """Start resource monitoring"""
        try:
            self._monitoring_thread = threading.Thread(target=self._monitor_resources)
            self._monitoring_thread.daemon = True
            self._monitoring_thread.start()
            logger.info("Resource monitoring started")
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {str(e)}")
            
    async def stop_monitoring(self) -> None:
        """Stop resource monitoring"""
        try:
            self._stop_monitoring = True
            if self._monitoring_thread:
                self._monitoring_thread.join()
            logger.info("Resource monitoring stopped")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring: {str(e)}")
            
    def _monitor_resources(self) -> None:
        """Monitor system resources"""
        while not self._stop_monitoring:
            try:
                # Collect current metrics
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Generate predictions
                if len(self.metrics_history) >= self.prediction_params["min_samples"]:
                    prediction = self._generate_prediction()
                    self.predictions_history.append(prediction)
                    
                # Check for alerts
                self._check_alerts(metrics)
                
                # Sleep for the metrics interval
                time.sleep(self.intervals["metrics"])
                
            except Exception as e:
                logger.error(f"Error in resource monitoring: {str(e)}")
                time.sleep(self.intervals["metrics"])
                
    def _collect_metrics(self) -> ResourceMetrics:
        """Collect current resource metrics"""
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Get network I/O
            net_io = psutil.net_io_counters()
            network_io = (net_io.bytes_sent, net_io.bytes_recv)
            
            # Get GPU metrics if available
            gpu_percent = None
            gpu_memory_percent = None
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    gpu_percent = gpu.load * 100
                    gpu_memory_percent = gpu.memoryUtil * 100
            except ImportError:
                pass
                
            return ResourceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_io=network_io,
                gpu_percent=gpu_percent,
                gpu_memory_percent=gpu_memory_percent
            )
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
            return None
            
    def _generate_prediction(self) -> ResourcePrediction:
        """Generate resource usage predictions"""
        try:
            # Convert history to numpy arrays
            history = list(self.metrics_history)
            timestamps = np.array([m.timestamp for m in history])
            cpu_values = np.array([m.cpu_percent for m in history])
            memory_values = np.array([m.memory_percent for m in history])
            disk_values = np.array([m.disk_percent for m in history])
            network_values = np.array([sum(m.network_io) for m in history])
            
            # Calculate prediction window
            window_size = self.prediction_params["window_size"]
            future_timestamps = np.array([
                timestamps[-1] + timedelta(seconds=i)
                for i in range(1, window_size + 1)
            ])
            
            # Generate predictions using simple linear regression
            cpu_pred = self._predict_linear(timestamps, cpu_values, future_timestamps)
            memory_pred = self._predict_linear(timestamps, memory_values, future_timestamps)
            disk_pred = self._predict_linear(timestamps, disk_values, future_timestamps)
            network_pred = self._predict_linear(timestamps, network_values, future_timestamps)
            
            # Calculate confidence based on historical variance
            confidence = self._calculate_confidence(history)
            
            return ResourcePrediction(
                timestamp=datetime.now(),
                cpu_prediction=cpu_pred[-1],
                memory_prediction=memory_pred[-1],
                disk_prediction=disk_pred[-1],
                network_prediction=(network_pred[-1], network_pred[-1]),
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error generating predictions: {str(e)}")
            return None
            
    def _predict_linear(self, x: np.ndarray, y: np.ndarray, x_future: np.ndarray) -> np.ndarray:
        """Generate linear predictions"""
        try:
            # Convert timestamps to seconds since epoch
            x_seconds = np.array([t.timestamp() for t in x])
            x_future_seconds = np.array([t.timestamp() for t in x_future])
            
            # Fit linear regression
            coeffs = np.polyfit(x_seconds, y, 1)
            
            # Generate predictions
            predictions = np.polyval(coeffs, x_future_seconds)
            
            # Ensure predictions are within reasonable bounds
            predictions = np.clip(predictions, 0, 100)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in linear prediction: {str(e)}")
            return np.zeros_like(x_future)
            
    def _calculate_confidence(self, history: List[ResourceMetrics]) -> float:
        """Calculate prediction confidence"""
        try:
            # Calculate variance of recent metrics
            recent_metrics = history[-self.prediction_params["min_samples"]:]
            cpu_variance = np.var([m.cpu_percent for m in recent_metrics])
            memory_variance = np.var([m.memory_percent for m in recent_metrics])
            disk_variance = np.var([m.disk_percent for m in recent_metrics])
            
            # Calculate overall confidence (inverse of average variance)
            avg_variance = (cpu_variance + memory_variance + disk_variance) / 3
            confidence = 1 / (1 + avg_variance)
            
            # Normalize confidence to [0, 1]
            confidence = min(max(confidence, 0), 1)
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 0.0
            
    def _check_alerts(self, metrics: ResourceMetrics) -> None:
        """Check for resource usage alerts"""
        try:
            # Check CPU usage
            if metrics.cpu_percent >= self.thresholds["cpu"]["critical"]:
                logger.critical(f"Critical CPU usage: {metrics.cpu_percent}%")
            elif metrics.cpu_percent >= self.thresholds["cpu"]["warning"]:
                logger.warning(f"High CPU usage: {metrics.cpu_percent}%")
                
            # Check memory usage
            if metrics.memory_percent >= self.thresholds["memory"]["critical"]:
                logger.critical(f"Critical memory usage: {metrics.memory_percent}%")
            elif metrics.memory_percent >= self.thresholds["memory"]["warning"]:
                logger.warning(f"High memory usage: {metrics.memory_percent}%")
                
            # Check disk usage
            if metrics.disk_percent >= self.thresholds["disk"]["critical"]:
                logger.critical(f"Critical disk usage: {metrics.disk_percent}%")
            elif metrics.disk_percent >= self.thresholds["disk"]["warning"]:
                logger.warning(f"High disk usage: {metrics.disk_percent}%")
                
            # Check GPU usage if available
            if metrics.gpu_percent is not None:
                if metrics.gpu_percent >= self.thresholds.get("gpu", {}).get("critical", 90):
                    logger.critical(f"Critical GPU usage: {metrics.gpu_percent}%")
                elif metrics.gpu_percent >= self.thresholds.get("gpu", {}).get("warning", 80):
                    logger.warning(f"High GPU usage: {metrics.gpu_percent}%")
                    
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
            
    async def get_current_metrics(self) -> ResourceMetrics:
        """Get current resource metrics"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return self._collect_metrics()
        
    async def get_predictions(self) -> ResourcePrediction:
        """Get current resource predictions"""
        if self.predictions_history:
            return self.predictions_history[-1]
        return self._generate_prediction()
        
    async def get_metrics_history(self, limit: Optional[int] = None) -> List[ResourceMetrics]:
        """Get historical metrics"""
        if limit:
            return list(self.metrics_history)[-limit:]
        return list(self.metrics_history)
        
    async def get_predictions_history(self, limit: Optional[int] = None) -> List[ResourcePrediction]:
        """Get historical predictions"""
        if limit:
            return list(self.predictions_history)[-limit:]
        return list(self.predictions_history)
        
    async def export_metrics(self, filepath: str) -> None:
        """Export metrics to file"""
        try:
            metrics_data = {
                "metrics": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "cpu_percent": m.cpu_percent,
                        "memory_percent": m.memory_percent,
                        "disk_percent": m.disk_percent,
                        "network_io": m.network_io,
                        "gpu_percent": m.gpu_percent,
                        "gpu_memory_percent": m.gpu_memory_percent
                    }
                    for m in self.metrics_history
                ],
                "predictions": [
                    {
                        "timestamp": p.timestamp.isoformat(),
                        "cpu_prediction": p.cpu_prediction,
                        "memory_prediction": p.memory_prediction,
                        "disk_prediction": p.disk_prediction,
                        "network_prediction": p.network_prediction,
                        "confidence": p.confidence
                    }
                    for p in self.predictions_history
                ]
            }
            
            with open(filepath, "w") as f:
                json.dump(metrics_data, f, indent=2)
                
            logger.info(f"Metrics exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {str(e)}") 