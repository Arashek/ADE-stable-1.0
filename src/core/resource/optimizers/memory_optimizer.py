from typing import Dict, List, Any, Optional
import logging
import psutil
import gc
import asyncio
from datetime import datetime
import weakref
import sys

from ..base import (
    BaseResourceOptimizer,
    ResourceType,
    OptimizationStrategy,
    ResourceMetrics,
    OptimizationMetrics,
    ResourceContext
)

logger = logging.getLogger(__name__)

class MemoryOptimizer(BaseResourceOptimizer):
    """Optimizer for Memory resources"""
    
    def __init__(self):
        super().__init__(
            name="memory_optimizer",
            resource_type=ResourceType.MEMORY,
            strategies=[
                OptimizationStrategy.GARBAGE_COLLECTION,
                OptimizationStrategy.CACHING,
                OptimizationStrategy.RESOURCE_POOLING
            ],
            description="Optimizes memory usage through garbage collection, caching, and resource pooling",
            author="ADE Platform",
            version="1.0.0"
        )
        
        self._process = psutil.Process()
        self._cache = {}
        self._cache_size = 0
        self._max_cache_size = 100 * 1024 * 1024  # 100MB default
        self._resource_pools = {}
        self._pool_sizes = {}
        
    async def optimize(self, **kwargs) -> Dict[str, Any]:
        """Optimize memory usage"""
        try:
            # Get current memory usage
            current_usage = kwargs.get("current_usage", {})
            memory_percent = current_usage.get("memory_percent", 0.0)
            
            # Get optimization context
            context = kwargs.get("context", self.context)
            
            # Check if optimization is needed
            if memory_percent < context.resource_limits.get("memory_percent", 80):
                return {
                    "success": True,
                    "improvement": 0.0,
                    "cost_savings": 0.0,
                    "efficiency": 1.0,
                    "message": "Memory usage within acceptable limits"
                }
                
            # Apply optimization strategies
            results = []
            
            # 1. Garbage Collection Strategy
            if OptimizationStrategy.GARBAGE_COLLECTION in self.strategies:
                gc_result = await self._apply_garbage_collection_strategy()
                results.append(gc_result)
                
            # 2. Caching Strategy
            if OptimizationStrategy.CACHING in self.strategies:
                caching_result = await self._apply_caching_strategy()
                results.append(caching_result)
                
            # 3. Resource Pooling Strategy
            if OptimizationStrategy.RESOURCE_POOLING in self.strategies:
                pooling_result = await self._apply_resource_pooling_strategy()
                results.append(pooling_result)
                
            # Calculate overall improvement
            total_improvement = sum(r.get("improvement", 0.0) for r in results)
            total_cost_savings = sum(r.get("cost_savings", 0.0) for r in results)
            avg_efficiency = sum(r.get("efficiency", 1.0) for r in results) / len(results)
            
            return {
                "success": True,
                "improvement": total_improvement,
                "cost_savings": total_cost_savings,
                "efficiency": avg_efficiency,
                "message": "Applied memory optimization strategies",
                "details": {
                    "strategies_applied": len(results),
                    "results": results
                }
            }
            
        except Exception as e:
            logger.error(f"Error optimizing memory resources: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "improvement": 0.0,
                "cost_savings": 0.0,
                "efficiency": 1.0
            }
            
    async def _get_resource_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        try:
            # Get memory info for current process
            memory_info = self._process.memory_info()
            
            # Get system-wide memory usage
            system_memory = psutil.virtual_memory()
            
            return {
                "current": memory_info.rss / 1024 / 1024,  # Convert to MB
                "system": system_memory.percent,
                "available": system_memory.available / 1024 / 1024,  # Convert to MB
                "total": system_memory.total / 1024 / 1024,  # Convert to MB
                "peak": self.resource_metrics.peak_usage,
                "average": self.resource_metrics.average_usage
            }
            
        except Exception as e:
            logger.error(f"Error getting memory usage: {str(e)}")
            return {
                "current": 0.0,
                "system": 0.0,
                "available": 0.0,
                "total": 0.0,
                "peak": 0.0,
                "average": 0.0
            }
            
    async def _apply_garbage_collection_strategy(self) -> Dict[str, Any]:
        """Apply memory garbage collection strategy"""
        try:
            # Get current memory usage before GC
            before_memory = self._process.memory_info().rss
            
            # Get GC threshold from context
            gc_threshold = self.context.resource_limits.get("gc_threshold", 0.8)
            
            # Check if GC is needed
            if before_memory / psutil.virtual_memory().total > gc_threshold:
                # Perform garbage collection
                gc.collect()
                
                # Get memory usage after GC
                after_memory = self._process.memory_info().rss
                
                # Calculate improvement
                improvement = (before_memory - after_memory) / before_memory
                cost_savings = improvement * 0.1  # Estimated cost savings
                
                return {
                    "strategy": "garbage_collection",
                    "action": "collect",
                    "improvement": improvement,
                    "cost_savings": cost_savings,
                    "efficiency": 1.0 - improvement,
                    "details": {
                        "before_memory_mb": before_memory / 1024 / 1024,
                        "after_memory_mb": after_memory / 1024 / 1024,
                        "threshold": gc_threshold
                    }
                }
                
            return {
                "strategy": "garbage_collection",
                "action": "none",
                "improvement": 0.0,
                "cost_savings": 0.0,
                "efficiency": 1.0,
                "details": {
                    "current_memory_mb": before_memory / 1024 / 1024,
                    "threshold": gc_threshold
                }
            }
            
        except Exception as e:
            logger.error(f"Error applying garbage collection strategy: {str(e)}")
            return {
                "strategy": "garbage_collection",
                "action": "error",
                "error": str(e),
                "improvement": 0.0,
                "cost_savings": 0.0,
                "efficiency": 1.0
            }
            
    async def _apply_caching_strategy(self) -> Dict[str, Any]:
        """Apply memory caching strategy"""
        try:
            # Get cache settings from context
            max_cache_size = self.context.resource_limits.get(
                "cache_size_mb",
                self._max_cache_size
            ) * 1024 * 1024  # Convert to bytes
            cache_ttl = self.context.resource_limits.get("cache_ttl_seconds", 3600)
            
            # Check if cache cleanup is needed
            if self._cache_size > max_cache_size:
                # Remove expired items
                current_time = datetime.now()
                expired_keys = []
                
                for key, (value, timestamp) in self._cache.items():
                    if (current_time - timestamp).total_seconds() > cache_ttl:
                        expired_keys.append(key)
                        self._cache_size -= sys.getsizeof(value)
                        
                for key in expired_keys:
                    del self._cache[key]
                    
                # If still too large, remove oldest items
                if self._cache_size > max_cache_size:
                    sorted_items = sorted(
                        self._cache.items(),
                        key=lambda x: x[1][1]
                    )
                    
                    while self._cache_size > max_cache_size and sorted_items:
                        key, (value, _) = sorted_items.pop(0)
                        del self._cache[key]
                        self._cache_size -= sys.getsizeof(value)
                        
                improvement = (
                    self._cache_size / max_cache_size
                    if max_cache_size > 0 else 0.0
                )
                cost_savings = improvement * 0.1  # Estimated cost savings
                
                return {
                    "strategy": "caching",
                    "action": "cleanup",
                    "improvement": improvement,
                    "cost_savings": cost_savings,
                    "efficiency": 1.0 - improvement,
                    "details": {
                        "before_size_mb": self._cache_size / 1024 / 1024,
                        "after_size_mb": self._cache_size / 1024 / 1024,
                        "max_size_mb": max_cache_size / 1024 / 1024,
                        "items_removed": len(expired_keys)
                    }
                }
                
            return {
                "strategy": "caching",
                "action": "none",
                "improvement": 0.0,
                "cost_savings": 0.0,
                "efficiency": 1.0,
                "details": {
                    "current_size_mb": self._cache_size / 1024 / 1024,
                    "max_size_mb": max_cache_size / 1024 / 1024
                }
            }
            
        except Exception as e:
            logger.error(f"Error applying caching strategy: {str(e)}")
            return {
                "strategy": "caching",
                "action": "error",
                "error": str(e),
                "improvement": 0.0,
                "cost_savings": 0.0,
                "efficiency": 1.0
            }
            
    async def _apply_resource_pooling_strategy(self) -> Dict[str, Any]:
        """Apply memory resource pooling strategy"""
        try:
            # Get pool settings from context
            max_pool_size = self.context.resource_limits.get("pool_size", 10)
            pool_timeout = self.context.resource_limits.get("pool_timeout_seconds", 30)
            
            # Check each resource pool
            total_improvement = 0.0
            total_cost_savings = 0.0
            pools_optimized = 0
            
            for pool_name, pool in self._resource_pools.items():
                current_size = self._pool_sizes.get(pool_name, 0)
                
                if current_size > max_pool_size:
                    # Remove excess resources
                    excess = current_size - max_pool_size
                    for _ in range(excess):
                        if pool:
                            resource = pool.pop()
                            self._pool_sizes[pool_name] -= 1
                            
                    improvement = excess / current_size
                    total_improvement += improvement
                    total_cost_savings += improvement * 0.1  # Estimated cost savings
                    pools_optimized += 1
                    
            if pools_optimized > 0:
                avg_improvement = total_improvement / pools_optimized
                avg_cost_savings = total_cost_savings / pools_optimized
                
                return {
                    "strategy": "resource_pooling",
                    "action": "optimize",
                    "improvement": avg_improvement,
                    "cost_savings": avg_cost_savings,
                    "efficiency": 1.0 - avg_improvement,
                    "details": {
                        "pools_optimized": pools_optimized,
                        "max_pool_size": max_pool_size,
                        "total_improvement": total_improvement
                    }
                }
                
            return {
                "strategy": "resource_pooling",
                "action": "none",
                "improvement": 0.0,
                "cost_savings": 0.0,
                "efficiency": 1.0,
                "details": {
                    "total_pools": len(self._resource_pools),
                    "max_pool_size": max_pool_size
                }
            }
            
        except Exception as e:
            logger.error(f"Error applying resource pooling strategy: {str(e)}")
            return {
                "strategy": "resource_pooling",
                "action": "error",
                "error": str(e),
                "improvement": 0.0,
                "cost_savings": 0.0,
                "efficiency": 1.0
            } 