from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import psutil
import numpy as np
from dataclasses import dataclass
import json
import yaml
from pathlib import Path
import threading
import time
from collections import deque
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

logger = logging.getLogger(__name__)

@dataclass
class ResourceMetrics:
    """Metrics for resource usage"""
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Tuple[float, float]  # (bytes_sent, bytes_recv)
    gpu_usage: Optional[float] = None
    timestamp: datetime = datetime.now()

@dataclass
class ResourcePrediction:
    """Prediction for future resource usage"""
    cpu_prediction: float
    memory_prediction: float
    disk_prediction: float
    network_prediction: Tuple[float, float]
    gpu_prediction: Optional[float] = None
    confidence: float = 0.0
    prediction_time: datetime = datetime.now()

class ResourceOptimizer:
    """Enhanced resource prediction and dynamic scaling"""
    
    def __init__(self, 
                 history_size: int = 1000,
                 prediction_window: int = 60,  # seconds
                 update_interval: int = 5,  # seconds
                 scaling_threshold: float = 0.8):
        self.history_size = history_size
        self.prediction_window = prediction_window
        self.update_interval = update_interval
        self.scaling_threshold = scaling_threshold
        
        # Initialize resource history
        self.cpu_history = deque(maxlen=history_size)
        self.memory_history = deque(maxlen=history_size)
        self.disk_history = deque(maxlen=history_size)
        self.network_history = deque(maxlen=history_size)
        self.gpu_history = deque(maxlen=history_size)
        
        # Initialize prediction models
        self.cpu_model = RandomForestRegressor()
        self.memory_model = RandomForestRegressor()
        self.disk_model = RandomForestRegressor()
        self.network_model = RandomForestRegressor()
        self.gpu_model = RandomForestRegressor() if self._has_gpu() else None
        
        # Initialize scalers
        self.cpu_scaler = StandardScaler()
        self.memory_scaler = StandardScaler()
        self.disk_scaler = StandardScaler()
        self.network_scaler = StandardScaler()
        self.gpu_scaler = StandardScaler() if self._has_gpu() else None
        
        # Initialize monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self.monitoring_thread.start()
        
    def _has_gpu(self) -> bool:
        """Check if GPU is available"""
        try:
            return len(tf.config.list_physical_devices('GPU')) > 0
        except:
            return False
            
    def _monitor_resources(self) -> None:
        """Monitor resource usage in background"""
        while True:
            try:
                metrics = self._collect_metrics()
                self._update_history(metrics)
                self._update_models()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error monitoring resources: {e}")
                
    def _collect_metrics(self) -> ResourceMetrics:
        """Collect current resource metrics"""
        return ResourceMetrics(
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage('/').percent,
            network_io=psutil.net_io_counters()._asdict(),
            gpu_usage=self._get_gpu_usage() if self._has_gpu() else None
        )
        
    def _get_gpu_usage(self) -> Optional[float]:
        """Get GPU usage percentage"""
        try:
            gpu = tf.config.list_physical_devices('GPU')[0]
            return tf.config.experimental.get_memory_info(gpu)['current'] / \
                   tf.config.experimental.get_memory_info(gpu)['peak'] * 100
        except:
            return None
            
    def _update_history(self, metrics: ResourceMetrics) -> None:
        """Update resource history"""
        self.cpu_history.append(metrics.cpu_percent)
        self.memory_history.append(metrics.memory_percent)
        self.disk_history.append(metrics.disk_usage)
        self.network_history.append(sum(metrics.network_io))
        if metrics.gpu_usage is not None:
            self.gpu_history.append(metrics.gpu_usage)
            
    def _update_models(self) -> None:
        """Update prediction models"""
        if len(self.cpu_history) < 100:  # Minimum samples needed
            return
            
        # Prepare training data
        X = self._prepare_training_data()
        
        # Update CPU model
        y_cpu = np.array(list(self.cpu_history)[1:])
        X_cpu = X[:-1]
        self.cpu_scaler.fit(X_cpu)
        X_cpu_scaled = self.cpu_scaler.transform(X_cpu)
        self.cpu_model.fit(X_cpu_scaled, y_cpu)
        
        # Update memory model
        y_memory = np.array(list(self.memory_history)[1:])
        X_memory = X[:-1]
        self.memory_scaler.fit(X_memory)
        X_memory_scaled = self.memory_scaler.transform(X_memory)
        self.memory_model.fit(X_memory_scaled, y_memory)
        
        # Update disk model
        y_disk = np.array(list(self.disk_history)[1:])
        X_disk = X[:-1]
        self.disk_scaler.fit(X_disk)
        X_disk_scaled = self.disk_scaler.transform(X_disk)
        self.disk_model.fit(X_disk_scaled, y_disk)
        
        # Update network model
        y_network = np.array(list(self.network_history)[1:])
        X_network = X[:-1]
        self.network_scaler.fit(X_network)
        X_network_scaled = self.network_scaler.transform(X_network)
        self.network_model.fit(X_network_scaled, y_network)
        
        # Update GPU model if available
        if self._has_gpu() and len(self.gpu_history) > 0:
            y_gpu = np.array(list(self.gpu_history)[1:])
            X_gpu = X[:-1]
            self.gpu_scaler.fit(X_gpu)
            X_gpu_scaled = self.gpu_scaler.transform(X_gpu)
            self.gpu_model.fit(X_gpu_scaled, y_gpu)
            
    def _prepare_training_data(self) -> np.ndarray:
        """Prepare training data for models"""
        data = []
        for i in range(len(self.cpu_history)):
            features = [
                self.cpu_history[i],
                self.memory_history[i],
                self.disk_history[i],
                self.network_history[i]
            ]
            if self._has_gpu() and len(self.gpu_history) > i:
                features.append(self.gpu_history[i])
            data.append(features)
        return np.array(data)
        
    def predict_resources(self, 
                         prediction_time: Optional[datetime] = None) -> ResourcePrediction:
        """Predict future resource usage"""
        if prediction_time is None:
            prediction_time = datetime.now() + timedelta(seconds=self.prediction_window)
            
        # Prepare prediction data
        X = self._prepare_training_data()
        if len(X) == 0:
            return None
            
        # Scale data
        X_cpu_scaled = self.cpu_scaler.transform(X[-1:])
        X_memory_scaled = self.memory_scaler.transform(X[-1:])
        X_disk_scaled = self.disk_scaler.transform(X[-1:])
        X_network_scaled = self.network_scaler.transform(X[-1:])
        
        # Make predictions
        cpu_pred = self.cpu_model.predict(X_cpu_scaled)[0]
        memory_pred = self.memory_model.predict(X_memory_scaled)[0]
        disk_pred = self.disk_model.predict(X_disk_scaled)[0]
        network_pred = self.network_model.predict(X_network_scaled)[0]
        
        # Calculate confidence
        confidence = self._calculate_prediction_confidence()
        
        # Get GPU prediction if available
        gpu_pred = None
        if self._has_gpu() and self.gpu_model is not None:
            X_gpu_scaled = self.gpu_scaler.transform(X[-1:])
            gpu_pred = self.gpu_model.predict(X_gpu_scaled)[0]
            
        return ResourcePrediction(
            cpu_prediction=cpu_pred,
            memory_prediction=memory_pred,
            disk_prediction=disk_pred,
            network_prediction=(network_pred, network_pred),  # Simplified network prediction
            gpu_prediction=gpu_pred,
            confidence=confidence,
            prediction_time=prediction_time
        )
        
    def _calculate_prediction_confidence(self) -> float:
        """Calculate confidence in predictions"""
        # Use model feature importance as confidence metric
        cpu_importance = np.mean(self.cpu_model.feature_importances_)
        memory_importance = np.mean(self.memory_model.feature_importances_)
        disk_importance = np.mean(self.disk_model.feature_importances_)
        network_importance = np.mean(self.network_model.feature_importances_)
        
        # Calculate average confidence
        confidences = [cpu_importance, memory_importance, disk_importance, network_importance]
        if self._has_gpu() and self.gpu_model is not None:
            confidences.append(np.mean(self.gpu_model.feature_importances_))
            
        return np.mean(confidences)
        
    def should_scale(self) -> Tuple[bool, Dict[str, Any]]:
        """Determine if resources should be scaled"""
        prediction = self.predict_resources()
        if prediction is None:
            return False, {}
            
        # Check if any resource is predicted to exceed threshold
        scaling_needed = False
        scaling_info = {}
        
        if prediction.cpu_prediction > self.scaling_threshold:
            scaling_needed = True
            scaling_info["cpu"] = {
                "current": self.cpu_history[-1],
                "predicted": prediction.cpu_prediction,
                "threshold": self.scaling_threshold
            }
            
        if prediction.memory_prediction > self.scaling_threshold:
            scaling_needed = True
            scaling_info["memory"] = {
                "current": self.memory_history[-1],
                "predicted": prediction.memory_prediction,
                "threshold": self.scaling_threshold
            }
            
        if prediction.disk_prediction > self.scaling_threshold:
            scaling_needed = True
            scaling_info["disk"] = {
                "current": self.disk_history[-1],
                "predicted": prediction.disk_prediction,
                "threshold": self.scaling_threshold
            }
            
        if sum(prediction.network_prediction) > self.scaling_threshold:
            scaling_needed = True
            scaling_info["network"] = {
                "current": self.network_history[-1],
                "predicted": sum(prediction.network_prediction),
                "threshold": self.scaling_threshold
            }
            
        if prediction.gpu_prediction and prediction.gpu_prediction > self.scaling_threshold:
            scaling_needed = True
            scaling_info["gpu"] = {
                "current": self.gpu_history[-1],
                "predicted": prediction.gpu_prediction,
                "threshold": self.scaling_threshold
            }
            
        return scaling_needed, scaling_info
        
    def get_resource_metrics(self) -> Dict[str, Any]:
        """Get current resource metrics"""
        if not self.cpu_history:
            return {}
            
        return {
            "cpu": {
                "current": self.cpu_history[-1],
                "history": list(self.cpu_history)
            },
            "memory": {
                "current": self.memory_history[-1],
                "history": list(self.memory_history)
            },
            "disk": {
                "current": self.disk_history[-1],
                "history": list(self.disk_history)
            },
            "network": {
                "current": self.network_history[-1],
                "history": list(self.network_history)
            },
            "gpu": {
                "current": self.gpu_history[-1] if self.gpu_history else None,
                "history": list(self.gpu_history) if self.gpu_history else []
            }
        }
        
    def get_prediction_metrics(self) -> Dict[str, Any]:
        """Get prediction metrics"""
        prediction = self.predict_resources()
        if prediction is None:
            return {}
            
        return {
            "cpu": {
                "predicted": prediction.cpu_prediction,
                "confidence": prediction.confidence
            },
            "memory": {
                "predicted": prediction.memory_prediction,
                "confidence": prediction.confidence
            },
            "disk": {
                "predicted": prediction.disk_prediction,
                "confidence": prediction.confidence
            },
            "network": {
                "predicted": sum(prediction.network_prediction),
                "confidence": prediction.confidence
            },
            "gpu": {
                "predicted": prediction.gpu_prediction,
                "confidence": prediction.confidence
            } if prediction.gpu_prediction is not None else None
        } 