import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import json
import yaml
import psutil
import GPUtil
import time
import docker
from datetime import datetime
from dataclasses import dataclass, field
from threading import Thread, Event

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System resource metrics"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_usage_percent: float = 0.0
    gpu_metrics: List[Dict] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class StageMetrics:
    """Metrics for a pipeline stage"""
    name: str
    start_time: str
    end_time: Optional[str] = None
    duration: Optional[float] = None
    cpu_usage: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    disk_usage: List[float] = field(default_factory=list)
    gpu_usage: List[List[float]] = field(default_factory=list)
    status: str = "running"
    error: Optional[str] = None

class PipelineMonitor:
    """Monitors pipeline execution and collects metrics"""
    
    def __init__(self, metrics_dir: str = "metrics", interval: float = 1.0):
        """Initialize the pipeline monitor
        
        Args:
            metrics_dir: Directory for storing metrics
            interval: Metrics collection interval in seconds
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.interval = interval
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {str(e)}")
            self.docker_client = None
            
        # Monitoring state
        self.is_monitoring = False
        self.stop_event = Event()
        self.monitor_thread = None
        self.current_pipeline: Optional[str] = None
        self.current_stage: Optional[str] = None
        self.stage_metrics: Dict[str, StageMetrics] = {}
        
    def start_monitoring(self, pipeline_name: str, stage_name: str) -> bool:
        """Start monitoring a pipeline stage
        
        Args:
            pipeline_name: Name of the pipeline
            stage_name: Name of the stage
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.is_monitoring:
                logger.warning("Monitoring is already active")
                return False
                
            self.current_pipeline = pipeline_name
            self.current_stage = stage_name
            
            # Initialize stage metrics
            self.stage_metrics[stage_name] = StageMetrics(
                name=stage_name,
                start_time=datetime.now().isoformat()
            )
            
            # Start monitoring thread
            self.stop_event.clear()
            self.is_monitoring = True
            self.monitor_thread = Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            logger.info(f"Started monitoring pipeline {pipeline_name}, stage {stage_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {str(e)}")
            return False
            
    def stop_monitoring(self) -> bool:
        """Stop monitoring the current pipeline stage
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.is_monitoring:
                return True
                
            # Stop monitoring thread
            self.stop_event.set()
            if self.monitor_thread:
                self.monitor_thread.join()
                
            self.is_monitoring = False
            
            # Update final metrics
            if self.current_stage and self.current_stage in self.stage_metrics:
                metrics = self.stage_metrics[self.current_stage]
                metrics.end_time = datetime.now().isoformat()
                metrics.duration = (
                    datetime.fromisoformat(metrics.end_time) -
                    datetime.fromisoformat(metrics.start_time)
                ).total_seconds()
                
                # Save metrics
                self._save_metrics()
                
            logger.info("Stopped monitoring")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {str(e)}")
            return False
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self.stop_event.is_set():
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                
                # Update stage metrics
                if self.current_stage and self.current_stage in self.stage_metrics:
                    metrics = self.stage_metrics[self.current_stage]
                    metrics.cpu_usage.append(system_metrics.cpu_percent)
                    metrics.memory_usage.append(system_metrics.memory_percent)
                    metrics.disk_usage.append(system_metrics.disk_usage_percent)
                    metrics.gpu_usage.append([
                        gpu["gpuLoad"] for gpu in system_metrics.gpu_metrics
                    ])
                    
                # Save metrics periodically
                self._save_metrics()
                
                # Wait for next interval
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(self.interval)
                
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system resource metrics
        
        Returns:
            SystemMetrics: Collected system metrics
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # GPU metrics
            gpu_metrics = []
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_metrics.append({
                        "id": gpu.id,
                        "name": gpu.name,
                        "gpuLoad": gpu.load * 100,
                        "memoryUsed": gpu.memoryUsed,
                        "memoryTotal": gpu.memoryTotal,
                        "temperature": gpu.temperature
                    })
            except Exception as e:
                logger.warning(f"Failed to collect GPU metrics: {str(e)}")
                
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage_percent=disk_usage_percent,
                gpu_metrics=gpu_metrics
            )
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {str(e)}")
            return SystemMetrics()
            
    def _save_metrics(self):
        """Save collected metrics to disk"""
        try:
            if not self.current_pipeline:
                return
                
            # Create metrics file path
            metrics_file = self.metrics_dir / f"{self.current_pipeline}-metrics.json"
            
            # Prepare metrics data
            metrics_data = {
                "pipeline_name": self.current_pipeline,
                "stages": {
                    name: {
                        "name": metrics.name,
                        "start_time": metrics.start_time,
                        "end_time": metrics.end_time,
                        "duration": metrics.duration,
                        "cpu_usage": metrics.cpu_usage,
                        "memory_usage": metrics.memory_usage,
                        "disk_usage": metrics.disk_usage,
                        "gpu_usage": metrics.gpu_usage,
                        "status": metrics.status,
                        "error": metrics.error
                    }
                    for name, metrics in self.stage_metrics.items()
                }
            }
            
            # Save metrics
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=4)
                
        except Exception as e:
            logger.error(f"Failed to save metrics: {str(e)}")
            
    def get_metrics(self, pipeline_name: str) -> Optional[Dict]:
        """Get metrics for a pipeline
        
        Args:
            pipeline_name: Name of the pipeline
            
        Returns:
            Dict: Pipeline metrics if found, None otherwise
        """
        try:
            metrics_file = self.metrics_dir / f"{pipeline_name}-metrics.json"
            if not metrics_file.exists():
                return None
                
            with open(metrics_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to get metrics: {str(e)}")
            return None
            
    def clean_metrics(self, pipeline_name: str) -> bool:
        """Clean up metrics for a pipeline
        
        Args:
            pipeline_name: Name of the pipeline
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            metrics_file = self.metrics_dir / f"{pipeline_name}-metrics.json"
            if metrics_file.exists():
                metrics_file.unlink()
                
            logger.info(f"Cleaned metrics for pipeline: {pipeline_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clean metrics: {str(e)}")
            return False 