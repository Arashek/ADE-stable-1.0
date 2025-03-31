from typing import Dict, Any, Optional, Callable
import time
import cProfile
import pstats
import io
import psutil
import os
from functools import wraps
from datetime import datetime
from ...config.logging_config import logger

class BaseProfiler:
    """Base class for performance profiling"""
    
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.stats = None
        self.start_time = None
        self.end_time = None
        self.process = psutil.Process(os.getpid())
        
    def start(self):
        """Start profiling"""
        self.start_time = time.time()
        self.profiler.enable()
        
    def stop(self):
        """Stop profiling"""
        self.profiler.disable()
        self.end_time = time.time()
        self.stats = pstats.Stats(self.profiler)
        
    def get_execution_time(self) -> float:
        """Get total execution time in seconds"""
        if not self.start_time or not self.end_time:
            return 0.0
        return self.end_time - self.start_time
        
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        return self.process.cpu_percent()
        
    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage statistics"""
        memory_info = self.process.memory_info()
        return {
            "rss": memory_info.rss / 1024 / 1024,  # RSS in MB
            "vms": memory_info.vms / 1024 / 1024,  # VMS in MB
            "percent": self.process.memory_percent()
        }
        
    def get_stats(self) -> Dict[str, Any]:
        """Get profiling statistics"""
        if not self.stats:
            return {}
            
        # Create a string buffer to capture stats
        s = io.StringIO()
        self.stats.stream = s
        self.stats.print_stats()
        
        # Parse the stats output
        stats_lines = s.getvalue().split('\n')
        stats_data = {}
        
        for line in stats_lines[4:]:  # Skip header lines
            if line.strip():
                parts = line.split()
                if len(parts) >= 5:
                    stats_data[parts[4]] = {
                        "ncalls": parts[0],
                        "tottime": float(parts[1]),
                        "percall": float(parts[2]),
                        "cumtime": float(parts[3])
                    }
                    
        return stats_data
        
    def generate_flamegraph(self, output_file: str):
        """Generate a flamegraph visualization"""
        try:
            import flamegraph
            self.stats.dump_stats("temp.prof")
            flamegraph.generate_flamegraph("temp.prof", output_file)
            os.remove("temp.prof")
        except ImportError:
            logger.warning("flamegraph package not installed. Install with: pip install flamegraph")
            
    def profile_function(self, func: Callable) -> Callable:
        """Decorator to profile a function"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.start()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                self.stop()
        return wrapper
        
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report"""
        return {
            "execution_time": self.get_execution_time(),
            "cpu_usage": self.get_cpu_usage(),
            "memory_usage": self.get_memory_usage(),
            "function_stats": self.get_stats(),
            "timestamp": datetime.utcnow().isoformat()
        } 