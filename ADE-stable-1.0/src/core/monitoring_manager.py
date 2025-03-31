from typing import Dict, Any, List, Optional
import psutil
import GPUtil
import torch
import wandb
import logging
from datetime import datetime
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
import time
from threading import Thread, Event

logger = logging.getLogger(__name__)

class MonitoringManager:
    """Manages system and training monitoring"""
    
    def __init__(self, logs_dir: str = "logs"):
        """Initialize the monitoring manager
        
        Args:
            logs_dir: Directory for storing logs
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize metrics history
        self.metrics_history: Dict[str, List[float]] = {
            "cpu_percent": [],
            "memory_percent": [],
            "gpu_percent": [],
            "gpu_memory_percent": [],
            "disk_io_read": [],
            "disk_io_write": [],
            "network_io_sent": [],
            "network_io_recv": [],
            "loss": [],
            "learning_rate": [],
            "epoch": [],
            "step": []
        }
        
        # Initialize timestamps
        self.timestamps: List[datetime] = []
        
        # Initialize device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize monitoring threads
        self.resource_monitor_thread: Optional[Thread] = None
        self.training_monitor_thread: Optional[Thread] = None
        self.stop_event = Event()
        
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics
        
        Returns:
            Dictionary of system metrics
        """
        try:
            metrics = {}
            
            # CPU metrics
            metrics["cpu_percent"] = psutil.cpu_percent()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics["memory_percent"] = memory.percent
            
            # GPU metrics if available
            if self.device.type == "cuda":
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]
                        metrics["gpu_percent"] = gpu.load * 100
                        metrics["gpu_memory_percent"] = gpu.memoryUtil * 100
                except Exception as e:
                    logger.warning(f"Failed to get GPU metrics: {str(e)}")
                    
            # Disk I/O metrics
            disk_io = psutil.disk_io_counters()
            metrics["disk_io_read"] = disk_io.read_bytes / 1024 / 1024  # MB
            metrics["disk_io_write"] = disk_io.write_bytes / 1024 / 1024  # MB
            
            # Network I/O metrics
            net_io = psutil.net_io_counters()
            metrics["network_io_sent"] = net_io.bytes_sent / 1024 / 1024  # MB
            metrics["network_io_recv"] = net_io.bytes_recv / 1024 / 1024  # MB
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {str(e)}")
            return {}
            
    def get_training_metrics(self, trainer: Any) -> Dict[str, float]:
        """Get current training metrics from trainer
        
        Args:
            trainer: Trainer object
            
        Returns:
            Dictionary of training metrics
        """
        try:
            metrics = {}
            
            # Get metrics from trainer state
            if hasattr(trainer, "state"):
                state = trainer.state
                metrics["loss"] = state.log_history[-1].get("loss", 0.0)
                metrics["learning_rate"] = state.log_history[-1].get("learning_rate", 0.0)
                metrics["epoch"] = state.epoch
                metrics["step"] = state.global_step
                
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get training metrics: {str(e)}")
            return {}
            
    def update_metrics(self, metrics: Dict[str, float]) -> None:
        """Update metrics history
        
        Args:
            metrics: Dictionary of metrics to update
        """
        try:
            # Add timestamp
            self.timestamps.append(datetime.now())
            
            # Update metrics history
            for metric, value in metrics.items():
                if metric in self.metrics_history:
                    self.metrics_history[metric].append(value)
                    
            # Limit history size
            max_history = 1000
            if len(self.timestamps) > max_history:
                self.timestamps = self.timestamps[-max_history:]
                for metric in self.metrics_history:
                    self.metrics_history[metric] = self.metrics_history[metric][-max_history:]
                    
        except Exception as e:
            logger.error(f"Failed to update metrics: {str(e)}")
            
    def log_metrics(self) -> None:
        """Log metrics to wandb"""
        try:
            # Get latest metrics
            latest_metrics = {
                metric: values[-1] if values else 0.0
                for metric, values in self.metrics_history.items()
            }
            
            # Log to wandb
            wandb.log(latest_metrics)
            
        except Exception as e:
            logger.error(f"Failed to log metrics: {str(e)}")
            
    def save_metrics(self) -> None:
        """Save metrics history to file"""
        try:
            # Prepare data for saving
            data = {
                "timestamps": [ts.isoformat() for ts in self.timestamps],
                "metrics": self.metrics_history
            }
            
            # Save to JSON
            metrics_file = self.logs_dir / "metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(data, f, indent=4)
                
            # Generate plots
            self._generate_plots()
            
        except Exception as e:
            logger.error(f"Failed to save metrics: {str(e)}")
            
    def _generate_plots(self) -> None:
        """Generate plots from metrics history"""
        try:
            # Create plots directory
            plots_dir = self.logs_dir / "plots"
            plots_dir.mkdir(exist_ok=True)
            
            # Generate plots for each metric
            for metric, values in self.metrics_history.items():
                if not values:
                    continue
                    
                plt.figure(figsize=(10, 6))
                plt.plot(self.timestamps, values)
                plt.title(f"{metric} over time")
                plt.xlabel("Time")
                plt.ylabel("Value")
                plt.grid(True)
                
                # Rotate x-axis labels for better readability
                plt.xticks(rotation=45)
                
                # Save plot
                plt.tight_layout()
                plt.savefig(plots_dir / f"{metric}.png")
                plt.close()
                
        except Exception as e:
            logger.error(f"Failed to generate plots: {str(e)}")
            
    def get_metric_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary statistics for each metric
        
        Returns:
            Dictionary of metric summaries
        """
        try:
            summary = {}
            
            for metric, values in self.metrics_history.items():
                if not values:
                    continue
                    
                summary[metric] = {
                    "min": min(values),
                    "max": max(values),
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "current": values[-1]
                }
                
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get metric summary: {str(e)}")
            return {}
            
    def monitor_resources(self, interval: float = 5.0) -> None:
        """Start monitoring system resources
        
        Args:
            interval: Monitoring interval in seconds
        """
        def monitor():
            while not self.stop_event.is_set():
                try:
                    # Get system metrics
                    metrics = self.get_system_metrics()
                    
                    # Update metrics history
                    self.update_metrics(metrics)
                    
                    # Log metrics
                    self.log_metrics()
                    
                    # Wait for next interval
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Error in resource monitoring: {str(e)}")
                    time.sleep(interval)
                    
        # Start monitoring thread
        self.resource_monitor_thread = Thread(target=monitor)
        self.resource_monitor_thread.daemon = True
        self.resource_monitor_thread.start()
        
    def monitor_training(self, trainer: Any, interval: float = 1.0) -> None:
        """Start monitoring training progress
        
        Args:
            trainer: Trainer object
            interval: Monitoring interval in seconds
        """
        def monitor():
            while not self.stop_event.is_set():
                try:
                    # Get training metrics
                    metrics = self.get_training_metrics(trainer)
                    
                    # Update metrics history
                    self.update_metrics(metrics)
                    
                    # Log metrics
                    self.log_metrics()
                    
                    # Wait for next interval
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Error in training monitoring: {str(e)}")
                    time.sleep(interval)
                    
        # Start monitoring thread
        self.training_monitor_thread = Thread(target=monitor)
        self.training_monitor_thread.daemon = True
        self.training_monitor_thread.start()
        
    def get_resource_usage(self) -> Dict[str, float]:
        """Get current resource usage
        
        Returns:
            Dictionary of current resource usage
        """
        try:
            return {
                metric: values[-1] if values else 0.0
                for metric, values in self.metrics_history.items()
                if metric in ["cpu_percent", "memory_percent", "gpu_percent", "gpu_memory_percent"]
            }
            
        except Exception as e:
            logger.error(f"Failed to get resource usage: {str(e)}")
            return {}
            
    def get_training_progress(self) -> Dict[str, float]:
        """Get current training progress
        
        Returns:
            Dictionary of current training progress
        """
        try:
            return {
                metric: values[-1] if values else 0.0
                for metric, values in self.metrics_history.items()
                if metric in ["loss", "learning_rate", "epoch", "step"]
            }
            
        except Exception as e:
            logger.error(f"Failed to get training progress: {str(e)}")
            return {}
            
    def stop_monitoring(self) -> None:
        """Stop all monitoring threads"""
        self.stop_event.set()
        
        if self.resource_monitor_thread:
            self.resource_monitor_thread.join()
        if self.training_monitor_thread:
            self.training_monitor_thread.join()
            
        # Save final metrics
        self.save_metrics() 