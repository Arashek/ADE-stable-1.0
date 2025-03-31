"""Task executor for running tasks in parallel."""
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class TaskResult:
    """Result of a task execution."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskExecutor:
    """Executes tasks in parallel using a thread pool."""
    
    def __init__(self, max_workers: int = 5):
        """
        Initialize the task executor
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self.executor: Optional[ThreadPoolExecutor] = None
        self._lock = threading.Lock()
        self._running = False
        
    def start(self):
        """Start the task executor"""
        with self._lock:
            if not self._running:
                self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
                self._running = True
                logger.info(f"Started task executor with {self.max_workers} workers")
    
    def stop(self):
        """Stop the task executor"""
        with self._lock:
            if self._running and self.executor:
                self.executor.shutdown(wait=True)
                self.executor = None
                self._running = False
                logger.info("Stopped task executor")
    
    def submit(self, fn: Callable, *args, **kwargs) -> Any:
        """
        Submit a task for execution
        
        Args:
            fn: The function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Future: A future representing the task execution
            
        Raises:
            RuntimeError: If the executor is not running
        """
        if not self._running or not self.executor:
            raise RuntimeError("Task executor is not running")
        
        return self.executor.submit(fn, *args, **kwargs)
    
    def is_running(self) -> bool:
        """Check if the executor is running"""
        return self._running
    
    def get_stats(self) -> Dict[str, Any]:
        """Get executor statistics"""
        with self._lock:
            if not self._running or not self.executor:
                return {
                    "running": False,
                    "max_workers": self.max_workers,
                    "active_threads": 0
                }
            
            return {
                "running": True,
                "max_workers": self.max_workers,
                "active_threads": len(self.executor._threads)
            } 