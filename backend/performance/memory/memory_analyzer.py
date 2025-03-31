from typing import Dict, Any, List, Optional
import tracemalloc
import psutil
import os
import gc
from datetime import datetime
from ...config.logging_config import logger
from ...database.redis_client import redis_client

class MemoryAnalyzer:
    """Memory analysis and leak detection tool"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.snapshots: List[tracemalloc.Snapshot] = []
        self.memory_history: List[Dict[str, Any]] = []
        self.leak_threshold = 100 * 1024 * 1024  # 100MB threshold for leak detection
        
    def start_tracking(self):
        """Start memory tracking"""
        tracemalloc.start()
        self._take_snapshot()
        
    def stop_tracking(self):
        """Stop memory tracking"""
        tracemalloc.stop()
        
    def _take_snapshot(self):
        """Take a memory snapshot"""
        snapshot = tracemalloc.take_snapshot()
        self.snapshots.append(snapshot)
        
        # Store memory usage
        memory_info = self.process.memory_info()
        self.memory_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "rss": memory_info.rss / 1024 / 1024,  # RSS in MB
            "vms": memory_info.vms / 1024 / 1024,  # VMS in MB
            "percent": self.process.memory_percent()
        })
        
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        memory_info = self.process.memory_info()
        return {
            "rss": memory_info.rss / 1024 / 1024,  # RSS in MB
            "vms": memory_info.vms / 1024 / 1024,  # VMS in MB
            "percent": self.process.memory_percent()
        }
        
    def analyze_memory_growth(self) -> List[Dict[str, Any]]:
        """Analyze memory growth patterns"""
        if len(self.memory_history) < 2:
            return []
            
        growth_patterns = []
        for i in range(1, len(self.memory_history)):
            prev = self.memory_history[i-1]
            curr = self.memory_history[i]
            
            rss_growth = curr["rss"] - prev["rss"]
            if rss_growth > 0:
                growth_patterns.append({
                    "timestamp": curr["timestamp"],
                    "rss_growth": rss_growth,
                    "vms_growth": curr["vms"] - prev["vms"],
                    "percent_growth": curr["percent"] - prev["percent"]
                })
                
        return growth_patterns
        
    def detect_memory_leaks(self) -> List[Dict[str, Any]]:
        """Detect potential memory leaks"""
        leaks = []
        
        if len(self.snapshots) < 2:
            return leaks
            
        # Compare consecutive snapshots
        for i in range(1, len(self.snapshots)):
            stats = self.snapshots[i].compare_to(self.snapshots[i-1], 'lineno')
            for stat in stats[:3]:  # Top 3 memory increases
                if stat.size_diff > self.leak_threshold:
                    leaks.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "file": stat.traceback[0].filename,
                        "line": stat.traceback[0].lineno,
                        "size_diff": stat.size_diff / 1024 / 1024,  # MB
                        "count_diff": stat.count_diff
                    })
                    
        return leaks
        
    def get_memory_objects(self) -> List[Dict[str, Any]]:
        """Get detailed information about memory objects"""
        if not self.snapshots:
            return []
            
        objects = []
        snapshot = self.snapshots[-1]
        
        for stat in snapshot.statistics('lineno')[:10]:  # Top 10 memory users
            objects.append({
                "file": stat.traceback[0].filename,
                "line": stat.traceback[0].lineno,
                "size": stat.size / 1024 / 1024,  # MB
                "count": stat.count
            })
            
        return objects
        
    async def store_memory_metrics(self):
        """Store memory metrics in Redis"""
        try:
            metrics = {
                "current_usage": self.get_memory_usage(),
                "growth_patterns": self.analyze_memory_growth(),
                "potential_leaks": self.detect_memory_leaks(),
                "top_objects": self.get_memory_objects(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in Redis with TTL of 7 days
            key = f"memory_metrics:{datetime.utcnow().strftime('%Y%m%d')}"
            await redis_client.set(key, metrics, expire=7 * 24 * 60 * 60)
            
        except Exception as e:
            logger.error(f"Error storing memory metrics: {str(e)}")
            
    def generate_memory_report(self) -> Dict[str, Any]:
        """Generate a comprehensive memory report"""
        return {
            "current_usage": self.get_memory_usage(),
            "growth_patterns": self.analyze_memory_growth(),
            "potential_leaks": self.detect_memory_leaks(),
            "top_objects": self.get_memory_objects(),
            "history": self.memory_history,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def optimize_memory(self):
        """Perform memory optimization"""
        try:
            # Force garbage collection
            gc.collect()
            
            # Clear memory history if too large
            if len(self.memory_history) > 1000:
                self.memory_history = self.memory_history[-1000:]
                
            # Clear old snapshots
            if len(self.snapshots) > 10:
                self.snapshots = self.snapshots[-10:]
                
        except Exception as e:
            logger.error(f"Error optimizing memory: {str(e)}")
            
    def get_memory_recommendations(self) -> List[str]:
        """Generate memory optimization recommendations"""
        recommendations = []
        current_usage = self.get_memory_usage()
        
        if current_usage["percent"] > 80:
            recommendations.append("High memory usage detected. Consider optimizing data structures and caching strategies.")
            
        leaks = self.detect_memory_leaks()
        if leaks:
            recommendations.append(f"Potential memory leaks detected in {len(leaks)} locations. Review object lifecycle management.")
            
        growth_patterns = self.analyze_memory_growth()
        if growth_patterns and any(p["rss_growth"] > 50 for p in growth_patterns):
            recommendations.append("Significant memory growth detected. Review resource cleanup in long-running operations.")
            
        return recommendations 