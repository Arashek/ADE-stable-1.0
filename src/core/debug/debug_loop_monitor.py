from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import threading
import time
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DebugStatus(Enum):
    """Status of a debug operation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    STALLED = "stalled"

@dataclass
class DebugMetrics:
    """Metrics for a debug operation"""
    start_time: datetime
    end_time: Optional[datetime] = None
    status: DebugStatus = DebugStatus.PENDING
    error_count: int = 0
    warning_count: int = 0
    step_count: int = 0
    resource_usage: Dict[str, float] = None
    completion_percentage: float = 0.0

class DebugLoopMonitor:
    """Monitors and tracks debug operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics: Dict[str, DebugMetrics] = {}
        self.stop_event = threading.Event()
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
    def start_monitoring(self, debug_id: str) -> bool:
        """Start monitoring a debug operation
        
        Args:
            debug_id: Unique identifier for the debug operation
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.lock:
                if debug_id in self.metrics:
                    logger.warning(f"Debug operation {debug_id} is already being monitored")
                    return False
                    
                self.metrics[debug_id] = DebugMetrics(
                    start_time=datetime.now(),
                    resource_usage={}
                )
                
                # Start monitoring thread if not already running
                if not self.monitor_thread or not self.monitor_thread.is_alive():
                    self.stop_event.clear()
                    self.monitor_thread = threading.Thread(target=self._monitor_loop)
                    self.monitor_thread.daemon = True
                    self.monitor_thread.start()
                    
                logger.info(f"Started monitoring debug operation {debug_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to start monitoring: {str(e)}")
            return False
            
    def stop_monitoring(self, debug_id: str) -> bool:
        """Stop monitoring a debug operation
        
        Args:
            debug_id: Unique identifier for the debug operation
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.lock:
                if debug_id not in self.metrics:
                    logger.warning(f"Debug operation {debug_id} is not being monitored")
                    return False
                    
                metrics = self.metrics[debug_id]
                metrics.end_time = datetime.now()
                metrics.status = DebugStatus.COMPLETED
                
                # Stop monitoring thread if no active operations
                if not any(m.status == DebugStatus.IN_PROGRESS for m in self.metrics.values()):
                    self.stop_event.set()
                    if self.monitor_thread:
                        self.monitor_thread.join()
                        
                logger.info(f"Stopped monitoring debug operation {debug_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {str(e)}")
            return False
            
    def update_progress(self, debug_id: str, 
                       step_count: Optional[int] = None,
                       error_count: Optional[int] = None,
                       warning_count: Optional[int] = None,
                       resource_usage: Optional[Dict[str, float]] = None,
                       completion_percentage: Optional[float] = None) -> None:
        """Update progress of a debug operation
        
        Args:
            debug_id: Unique identifier for the debug operation
            step_count: Number of steps completed
            error_count: Number of errors encountered
            warning_count: Number of warnings encountered
            resource_usage: Current resource usage metrics
            completion_percentage: Overall completion percentage
        """
        try:
            with self.lock:
                if debug_id not in self.metrics:
                    logger.warning(f"Debug operation {debug_id} not found")
                    return
                    
                metrics = self.metrics[debug_id]
                metrics.status = DebugStatus.IN_PROGRESS
                
                if step_count is not None:
                    metrics.step_count = step_count
                if error_count is not None:
                    metrics.error_count = error_count
                if warning_count is not None:
                    metrics.warning_count = warning_count
                if resource_usage is not None:
                    metrics.resource_usage = resource_usage
                if completion_percentage is not None:
                    metrics.completion_percentage = completion_percentage
                    
        except Exception as e:
            logger.error(f"Failed to update progress: {str(e)}")
            
    def get_progress(self, debug_id: str) -> Dict[str, Any]:
        """Get current progress of a debug operation
        
        Args:
            debug_id: Unique identifier for the debug operation
            
        Returns:
            Dictionary containing progress metrics
        """
        try:
            with self.lock:
                if debug_id not in self.metrics:
                    return {}
                    
                metrics = self.metrics[debug_id]
                return {
                    "status": metrics.status.value,
                    "start_time": metrics.start_time.isoformat(),
                    "end_time": metrics.end_time.isoformat() if metrics.end_time else None,
                    "step_count": metrics.step_count,
                    "error_count": metrics.error_count,
                    "warning_count": metrics.warning_count,
                    "resource_usage": metrics.resource_usage,
                    "completion_percentage": metrics.completion_percentage
                }
                
        except Exception as e:
            logger.error(f"Failed to get progress: {str(e)}")
            return {}
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self.stop_event.is_set():
            try:
                with self.lock:
                    for debug_id, metrics in self.metrics.items():
                        # Check for stalled operations
                        if metrics.status == DebugStatus.IN_PROGRESS:
                            elapsed = (datetime.now() - metrics.start_time).total_seconds()
                            if elapsed > self.config.get("stall_threshold", 300):  # 5 minutes default
                                metrics.status = DebugStatus.STALLED
                                logger.warning(f"Debug operation {debug_id} stalled after {elapsed:.1f} seconds")
                                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(5)  # Wait before retrying 