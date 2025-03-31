from typing import Dict, Any, Optional, List
from fastapi import Request, Response
from datetime import datetime, timedelta
from .base_profiler import BaseProfiler
from ...config.logging_config import logger
from ...database.redis_client import redis_client

class APIProfiler(BaseProfiler):
    """Profiler specialized for API endpoints"""
    
    def __init__(self):
        super().__init__()
        self.request: Optional[Request] = None
        self.response: Optional[Response] = None
        self.route: Optional[str] = None
        self.method: Optional[str] = None
        self.status_code: Optional[int] = None
        
    async def start_request(self, request: Request):
        """Start profiling an API request"""
        self.request = request
        self.route = request.url.path
        self.method = request.method
        self.start()
        
    async def end_request(self, response: Response):
        """End profiling an API request"""
        self.response = response
        self.status_code = response.status_code
        self.stop()
        
    async def get_request_metrics(self) -> Dict[str, Any]:
        """Get detailed request metrics"""
        if not self.request:
            return {}
            
        return {
            "route": self.route,
            "method": self.method,
            "status_code": self.status_code,
            "client_host": self.request.client.host if self.request.client else None,
            "user_agent": self.request.headers.get("user-agent"),
            "content_length": len(await self.request.body()) if self.request else 0,
            "response_size": len(self.response.body) if self.response else 0,
            "execution_time": self.get_execution_time(),
            "cpu_usage": self.get_cpu_usage(),
            "memory_usage": self.get_memory_usage(),
            "function_stats": self.get_stats(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    async def store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in Redis for historical analysis"""
        try:
            # Store in Redis with TTL of 30 days
            key = f"api_metrics:{self.route}:{datetime.utcnow().strftime('%Y%m%d')}"
            await redis_client.set(key, metrics, expire=30 * 24 * 60 * 60)
            
            # Store in daily aggregate
            aggregate_key = f"api_aggregate:{self.route}:{datetime.utcnow().strftime('%Y%m%d')}"
            await redis_client.incr(aggregate_key)
            
        except Exception as e:
            logger.error(f"Error storing API metrics: {str(e)}")
            
    async def get_route_statistics(self, route: str, days: int = 7) -> Dict[str, Any]:
        """Get historical statistics for a route"""
        try:
            stats = {
                "total_requests": 0,
                "avg_execution_time": 0,
                "success_rate": 0,
                "error_rate": 0,
                "daily_requests": {}
            }
            
            # Get daily aggregates
            for i in range(days):
                date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y%m%d')
                key = f"api_aggregate:{route}:{date}"
                count = await redis_client.get(key)
                if count:
                    stats["daily_requests"][date] = int(count)
                    stats["total_requests"] += int(count)
                    
            # Calculate success/error rates
            if stats["total_requests"] > 0:
                success_count = sum(1 for m in stats["daily_requests"].values() if m < 400)
                stats["success_rate"] = (success_count / stats["total_requests"]) * 100
                stats["error_rate"] = 100 - stats["success_rate"]
                
            return stats
            
        except Exception as e:
            logger.error(f"Error getting route statistics: {str(e)}")
            return {}
            
    async def detect_anomalies(self, route: str) -> List[Dict[str, Any]]:
        """Detect performance anomalies for a route"""
        try:
            anomalies = []
            metrics = await self.get_route_statistics(route)
            
            # Check execution time anomalies
            if self.get_execution_time() > 2.0:  # More than 2 seconds
                anomalies.append({
                    "type": "high_execution_time",
                    "value": self.get_execution_time(),
                    "threshold": 2.0,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            # Check error rate anomalies
            if metrics.get("error_rate", 0) > 5.0:  # More than 5% errors
                anomalies.append({
                    "type": "high_error_rate",
                    "value": metrics["error_rate"],
                    "threshold": 5.0,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            # Check memory usage anomalies
            memory_usage = self.get_memory_usage()
            if memory_usage["percent"] > 80.0:  # More than 80% memory usage
                anomalies.append({
                    "type": "high_memory_usage",
                    "value": memory_usage["percent"],
                    "threshold": 80.0,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return [] 