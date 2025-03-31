from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from .monitoring.performance_monitor import PerformanceMonitor
from .profiling.api_profiler import APIProfiler
from ..config.logging_config import logger

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring"""
    
    def __init__(self, app):
        super().__init__(app)
        self.performance_monitor = PerformanceMonitor()
        self.api_profiler = APIProfiler()
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and monitor performance"""
        try:
            # Start profiling
            await self.api_profiler.start_request(request)
            
            # Process request
            response = await call_next(request)
            
            # End profiling
            await self.api_profiler.end_request(response)
            
            # Collect metrics
            metrics = await self.api_profiler.get_request_metrics()
            
            # Store metrics
            await self.api_profiler.store_metrics(metrics)
            
            # Check for anomalies
            anomalies = await self.api_profiler.detect_anomalies(request.url.path)
            if anomalies:
                logger.warning(f"Performance anomalies detected: {anomalies}")
                
            # Add performance headers
            response.headers["X-Execution-Time"] = str(metrics.get("execution_time", 0))
            response.headers["X-CPU-Usage"] = str(metrics.get("cpu_usage", 0))
            response.headers["X-Memory-Usage"] = str(metrics.get("memory_usage", {}).get("percent", 0))
            
            return response
            
        except Exception as e:
            logger.error(f"Error in performance middleware: {str(e)}")
            return await call_next(request)
            
    async def start(self):
        """Start performance monitoring"""
        await self.performance_monitor.start_monitoring()
        
    async def stop(self):
        """Stop performance monitoring"""
        await self.performance_monitor.stop_monitoring() 