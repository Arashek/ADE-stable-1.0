from typing import Dict, List, Optional, Any, Type
from datetime import datetime
import logging
import asyncio
import importlib
import inspect
from pathlib import Path

from .base import (
    BaseResourceOptimizer,
    ResourceType,
    OptimizationStrategy,
    ResourceMetrics,
    OptimizationMetrics,
    ResourceContext
)

logger = logging.getLogger(__name__)

class ResourceManager:
    """Manager class for handling resource optimization"""
    
    def __init__(self):
        self.optimizers: Dict[str, BaseResourceOptimizer] = {}
        self.resource_types: Dict[ResourceType, List[str]] = {
            resource_type: [] for resource_type in ResourceType
        }
        self.strategies: Dict[OptimizationStrategy, List[str]] = {
            strategy: [] for strategy in OptimizationStrategy
        }
        self.resource_metrics: Dict[str, ResourceMetrics] = {}
        self.optimization_metrics: Dict[str, OptimizationMetrics] = {}
        self.resource_contexts: Dict[str, ResourceContext] = {}
        
        self._lock = asyncio.Lock()
        
    async def register_optimizer(self, optimizer: BaseResourceOptimizer) -> bool:
        """Register a new resource optimizer"""
        async with self._lock:
            try:
                # Check if optimizer already exists
                if optimizer.name in self.optimizers:
                    logger.warning(f"Optimizer {optimizer.name} already registered")
                    return False
                    
                # Validate optimizer
                if not await self._validate_optimizer(optimizer):
                    return False
                    
                # Register optimizer
                self.optimizers[optimizer.name] = optimizer
                self.resource_types[optimizer.resource_type].append(optimizer.name)
                for strategy in optimizer.strategies:
                    self.strategies[strategy].append(optimizer.name)
                self.resource_metrics[optimizer.name] = optimizer.resource_metrics
                self.optimization_metrics[optimizer.name] = optimizer.optimization_metrics
                self.resource_contexts[optimizer.name] = optimizer.context
                
                logger.info(f"Successfully registered optimizer: {optimizer.name}")
                return True
                
            except Exception as e:
                logger.error(f"Error registering optimizer {optimizer.name}: {str(e)}")
                return False
                
    async def discover_optimizers(self, search_paths: List[str]) -> List[str]:
        """Discover resource optimizers in the given paths"""
        discovered_optimizers = []
        
        for path in search_paths:
            try:
                # Convert path to Path object
                path_obj = Path(path)
                
                # Find Python files
                for file_path in path_obj.rglob("*.py"):
                    try:
                        # Import module
                        module_path = str(file_path.relative_to(path_obj))
                        module_name = module_path.replace("/", ".").replace(".py", "")
                        module = importlib.import_module(module_name)
                        
                        # Find optimizer classes
                        for name, obj in inspect.getmembers(module):
                            if (
                                inspect.isclass(obj) and
                                issubclass(obj, BaseResourceOptimizer) and
                                obj != BaseResourceOptimizer
                            ):
                                # Create optimizer instance
                                optimizer = obj()
                                if await self.register_optimizer(optimizer):
                                    discovered_optimizers.append(optimizer.name)
                                    
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error searching path {path}: {str(e)}")
                continue
                
        return discovered_optimizers
        
    async def optimize_resources(
        self,
        resource_types: Optional[List[ResourceType]] = None,
        strategies: Optional[List[OptimizationStrategy]] = None
    ) -> List[Dict[str, Any]]:
        """Optimize resources using registered optimizers"""
        async with self._lock:
            try:
                results = []
                
                # Get relevant optimizers
                optimizers = await self._get_relevant_optimizers(
                    resource_types,
                    strategies
                )
                
                # Optimize resources
                for optimizer_name in optimizers:
                    optimizer = self.optimizers[optimizer_name]
                    
                    # Monitor current resource usage
                    usage = await optimizer.monitor_resources()
                    
                    # Optimize resources
                    start_time = datetime.now()
                    
                    try:
                        result = await optimizer.optimize(
                            current_usage=usage,
                            context=optimizer.context
                        )
                        
                        # Update metrics
                        execution_time = (
                            datetime.now() - start_time
                        ).total_seconds()
                        
                        await optimizer.update_optimization_metrics({
                            "success": True,
                            "latency": execution_time,
                            "improvement": result.get("improvement", 0.0),
                            "cost_savings": result.get("cost_savings", 0.0),
                            "efficiency": result.get("efficiency", 1.0)
                        })
                        
                        # Update context
                        optimizer.context.optimization_history.append({
                            "timestamp": datetime.now(),
                            "result": result,
                            "usage": usage
                        })
                        
                        results.append(result)
                        
                    except Exception as e:
                        logger.error(
                            f"Error optimizing resources with {optimizer_name}: {str(e)}"
                        )
                        optimizer.context.error_history.append({
                            "timestamp": datetime.now(),
                            "error": str(e),
                            "usage": usage
                        })
                        continue
                        
                return results
                
            except Exception as e:
                logger.error(f"Error in resource optimization: {str(e)}")
                raise
                
    async def get_resource_metrics(self, optimizer_name: str) -> Optional[ResourceMetrics]:
        """Get resource metrics for an optimizer"""
        return self.resource_metrics.get(optimizer_name)
        
    async def get_optimization_metrics(self, optimizer_name: str) -> Optional[OptimizationMetrics]:
        """Get optimization metrics for an optimizer"""
        return self.optimization_metrics.get(optimizer_name)
        
    async def get_resource_context(self, optimizer_name: str) -> Optional[ResourceContext]:
        """Get resource context for an optimizer"""
        return self.resource_contexts.get(optimizer_name)
        
    async def get_optimizers_by_type(self, resource_type: ResourceType) -> List[str]:
        """Get all optimizers for a specific resource type"""
        return self.resource_types.get(resource_type, [])
        
    async def get_optimizers_by_strategy(self, strategy: OptimizationStrategy) -> List[str]:
        """Get all optimizers using a specific strategy"""
        return self.strategies.get(strategy, [])
        
    async def _validate_optimizer(self, optimizer: BaseResourceOptimizer) -> bool:
        """Validate an optimizer before registration"""
        try:
            # Check required attributes
            required_attrs = [
                "name", "resource_type", "strategies", "description",
                "author", "version", "optimize"
            ]
            
            for attr in required_attrs:
                if not hasattr(optimizer, attr):
                    logger.error(f"Optimizer missing required attribute: {attr}")
                    return False
                    
            # Validate resource type
            if not isinstance(optimizer.resource_type, ResourceType):
                logger.error("Invalid resource type")
                return False
                
            # Validate strategies
            if not all(isinstance(s, OptimizationStrategy) for s in optimizer.strategies):
                logger.error("Invalid optimization strategies")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating optimizer: {str(e)}")
            return False
            
    async def _get_relevant_optimizers(
        self,
        resource_types: Optional[List[ResourceType]],
        strategies: Optional[List[OptimizationStrategy]]
    ) -> List[str]:
        """Get relevant optimizers based on type and strategy filters"""
        relevant_optimizers = set()
        
        if resource_types:
            for resource_type in resource_types:
                optimizers = await self.get_optimizers_by_type(resource_type)
                relevant_optimizers.update(optimizers)
                
        if strategies:
            for strategy in strategies:
                optimizers = await self.get_optimizers_by_strategy(strategy)
                relevant_optimizers.update(optimizers)
                
        if not resource_types and not strategies:
            relevant_optimizers = set(self.optimizers.keys())
            
        return list(relevant_optimizers) 