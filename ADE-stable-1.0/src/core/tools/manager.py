from typing import Dict, List, Optional, Any, Type, Set
from dataclasses import dataclass
from datetime import datetime
import logging
import asyncio
import importlib
import inspect
from pathlib import Path
import yaml
import psutil
import time

from .base import (
    BaseTool,
    ToolCategory,
    ToolState,
    ToolMetadata,
    ToolMetrics,
    ToolContext,
    ToolResult
)
from .discovery import ToolDiscoverySystem

logger = logging.getLogger(__name__)

@dataclass
class ToolExecution:
    """Information about a tool execution"""
    tool_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    error: Optional[str] = None
    execution_time: float = 0.0
    resource_usage: Dict[str, float] = None

class ToolManager:
    """Manager for coordinating tool execution and resource management"""
    
    def __init__(self, llm_manager, pattern_learner):
        self.llm_manager = llm_manager
        self.pattern_learner = pattern_learner
        self.discovery_system = ToolDiscoverySystem(llm_manager, pattern_learner)
        self.active_executions: Dict[str, ToolExecution] = {}
        self.execution_history: List[ToolExecution] = []
        self._lock = asyncio.Lock()
        self._resource_lock = asyncio.Lock()
        
    async def initialize(self) -> None:
        """Initialize the tool manager"""
        try:
            # Initialize discovery system
            await self.discovery_system.initialize()
            
            # Load configuration
            config_path = Path("src/core/tools/config/manager.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    self.config = yaml.safe_load(f)
            else:
                logger.warning("Manager configuration not found")
                self.config = {}
                
            # Start resource monitoring
            asyncio.create_task(self._monitor_resources())
            
        except Exception as e:
            logger.error(f"Error initializing tool manager: {str(e)}")
            raise
            
    async def execute_tool(
        self,
        tool_name: str,
        context: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> ToolResult:
        """Execute a tool with the given context"""
        try:
            # Get tool instance
            tool = await self.discovery_system.get_tool(tool_name)
            if not tool:
                raise ValueError(f"Tool {tool_name} not found")
                
            # Check resource availability
            if not await self._check_resource_availability(tool):
                raise ResourceWarning("Insufficient resources available")
                
            # Create execution record
            execution = ToolExecution(
                tool_name=tool_name,
                start_time=datetime.now(),
                resource_usage={}
            )
            
            async with self._lock:
                self.active_executions[tool_name] = execution
                
            try:
                # Initialize tool
                await tool.initialize()
                
                # Pre-execution
                await tool.pre_execute(context)
                
                # Execute tool
                start_time = time.time()
                result = await tool.execute(context)
                execution_time = time.time() - start_time
                
                # Post-execution
                await tool.post_execute(result)
                
                # Update execution record
                execution.end_time = datetime.now()
                execution.success = result.success
                execution.error = result.error
                execution.execution_time = execution_time
                execution.resource_usage = tool.get_metrics()
                
                # Update history
                self.execution_history.append(execution)
                
                # Update discovery system metrics
                await self.discovery_system.update_tool_metrics(
                    tool_name,
                    execution_time,
                    result.success
                )
                
                return result
                
            finally:
                # Cleanup
                await tool.cleanup()
                
                # Remove from active executions
                async with self._lock:
                    if tool_name in self.active_executions:
                        del self.active_executions[tool_name]
                        
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=0.0
            )
            
    async def _check_resource_availability(self, tool: BaseTool) -> bool:
        """Check if there are sufficient resources available"""
        try:
            async with self._resource_lock:
                # Get system resources
                process = psutil.Process()
                memory_info = process.memory_info()
                cpu_percent = process.cpu_percent()
                
                # Check memory
                if memory_info.rss + tool.max_memory_increase > self.config.get("max_total_memory", 1 * 1024 * 1024 * 1024):
                    logger.warning("Insufficient memory available")
                    return False
                    
                # Check CPU
                if cpu_percent > self.config.get("max_total_cpu", 80):
                    logger.warning("Insufficient CPU available")
                    return False
                    
                # Check concurrent tools
                if len(self.active_executions) >= self.config.get("max_concurrent_tools", 10):
                    logger.warning("Maximum concurrent tools reached")
                    return False
                    
                return True
                
        except Exception as e:
            logger.error(f"Error checking resource availability: {str(e)}")
            return False
            
    async def _monitor_resources(self) -> None:
        """Monitor system resources"""
        try:
            while True:
                async with self._resource_lock:
                    # Get system resources
                    process = psutil.Process()
                    memory_info = process.memory_info()
                    cpu_percent = process.cpu_percent()
                    
                    # Check thresholds
                    if memory_info.rss > self.config.get("max_total_memory", 1 * 1024 * 1024 * 1024):
                        logger.warning("Memory usage exceeded threshold")
                        await self._handle_resource_exceeded("memory")
                        
                    if cpu_percent > self.config.get("max_total_cpu", 80):
                        logger.warning("CPU usage exceeded threshold")
                        await self._handle_resource_exceeded("cpu")
                        
                await asyncio.sleep(1)  # Check every second
                
        except Exception as e:
            logger.error(f"Error monitoring resources: {str(e)}")
            
    async def _handle_resource_exceeded(self, resource_type: str) -> None:
        """Handle resource limit exceeded"""
        try:
            # Get active executions sorted by resource usage
            sorted_executions = sorted(
                self.active_executions.items(),
                key=lambda x: x[1].resource_usage.get(resource_type, 0),
                reverse=True
            )
            
            # Stop high-resource tools
            for tool_name, execution in sorted_executions:
                if execution.resource_usage.get(resource_type, 0) > self.config.get(f"max_{resource_type}_per_tool", 0):
                    logger.warning(f"Stopping tool {tool_name} due to high {resource_type} usage")
                    # TODO: Implement graceful tool stopping
                    
        except Exception as e:
            logger.error(f"Error handling resource exceeded: {str(e)}")
            
    async def get_tool_metrics(self, tool_name: str) -> Dict[str, float]:
        """Get metrics for a tool"""
        return await self.discovery_system.get_tool_metrics(tool_name)
        
    async def get_tool_dependencies(self, tool_name: str) -> Set[str]:
        """Get dependencies for a tool"""
        return await self.discovery_system.get_tool_dependencies(tool_name)
        
    async def get_active_executions(self) -> Dict[str, ToolExecution]:
        """Get currently active tool executions"""
        return self.active_executions.copy()
        
    async def get_execution_history(self) -> List[ToolExecution]:
        """Get tool execution history"""
        return self.execution_history.copy()
        
    async def optimize_tool_usage(self, tool_name: str) -> Dict[str, Any]:
        """Get optimization suggestions for a tool"""
        return await self.discovery_system.optimize_tool_usage(tool_name)

    async def register_tool(self, tool: BaseTool) -> bool:
        """Register a new tool"""
        async with self._lock:
            try:
                # Check if tool already exists
                if tool.name in self.tools:
                    logger.warning(f"Tool {tool.name} already registered")
                    return False
                    
                # Validate tool
                if not await self._validate_tool(tool):
                    return False
                    
                # Register tool
                self.tools[tool.name] = tool
                self.tool_categories[tool.category].append(tool.name)
                self.tool_dependencies[tool.name] = tool.dependencies
                self.tool_metrics[tool.name] = tool.metrics
                self.tool_contexts[tool.name] = tool.context
                
                logger.info(f"Successfully registered tool: {tool.name}")
                return True
                
            except Exception as e:
                logger.error(f"Error registering tool {tool.name}: {str(e)}")
                return False
                
    async def discover_tools(self, search_paths: List[str]) -> List[str]:
        """Discover tools in the given paths"""
        discovered_tools = []
        
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
                        
                        # Find tool classes
                        for name, obj in inspect.getmembers(module):
                            if (
                                inspect.isclass(obj) and
                                issubclass(obj, BaseTool) and
                                obj != BaseTool
                            ):
                                # Create tool instance
                                tool = obj()
                                if await self.register_tool(tool):
                                    discovered_tools.append(tool.name)
                                    
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error searching path {path}: {str(e)}")
                continue
                
        return discovered_tools
        
    async def execute_tool(
        self,
        tool_name: str,
        **kwargs
    ) -> Any:
        """Execute a tool with given parameters"""
        async with self._lock:
            try:
                # Get tool
                tool = self.tools.get(tool_name)
                if not tool:
                    raise ValueError(f"Tool {tool_name} not found")
                    
                # Check tool state
                if tool.state == ToolState.DISABLED:
                    raise RuntimeError(f"Tool {tool_name} is disabled")
                    
                # Validate parameters
                if not await tool.validate_parameters(**kwargs):
                    raise ValueError(f"Invalid parameters for tool {tool_name}")
                    
                # Check dependencies
                if not await tool.check_dependencies():
                    raise RuntimeError(f"Dependencies not satisfied for tool {tool_name}")
                    
                # Update context
                tool.context.current_task = kwargs.get("task", "")
                tool.context.parameters = kwargs
                
                # Execute tool
                start_time = datetime.now()
                tool.state = ToolState.RUNNING
                
                try:
                    result = await tool.execute(**kwargs)
                    success = True
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {str(e)}")
                    success = False
                    raise
                finally:
                    # Update metrics
                    execution_time = (datetime.now() - start_time).total_seconds()
                    await tool.update_metrics({
                        "success": success,
                        "latency": execution_time,
                        "resource_usage": self._get_resource_usage()
                    })
                    
                    # Update context
                    tool.context.recent_executions.append({
                        "timestamp": datetime.now(),
                        "parameters": kwargs,
                        "success": success,
                        "latency": execution_time
                    })
                    
                    tool.state = ToolState.IDLE
                    
                return result
                
            except Exception as e:
                logger.error(f"Error in tool execution: {str(e)}")
                tool.state = ToolState.ERROR
                raise
                
    async def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a tool"""
        tool = self.tools.get(tool_name)
        if tool:
            return tool.get_metadata()
        return None
        
    def _get_resource_usage(self) -> Dict[str, float]:
        """Get current resource usage"""
        # TODO: Implement resource usage monitoring
        return {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "network_usage": 0.0
        }

    async def _validate_tool(self, tool: BaseTool) -> bool:
        """Validate a tool before registration"""
        try:
            # Check required attributes
            required_attrs = [
                "name", "version", "description", "author",
                "category", "execute"
            ]
            
            for attr in required_attrs:
                if not hasattr(tool, attr):
                    logger.error(f"Tool missing required attribute: {attr}")
                    return False
                    
            # Validate category
            if not isinstance(tool.category, ToolCategory):
                logger.error("Invalid tool category")
                return False
                
            # Validate parameters
            if not isinstance(tool.parameters, dict):
                logger.error("Invalid parameters format")
                return False
                
            # Validate dependencies
            if not isinstance(tool.dependencies, list):
                logger.error("Invalid dependencies format")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating tool: {str(e)}")
            return False
            
    def _get_resource_usage(self) -> Dict[str, float]:
        """Get current resource usage"""
        # TODO: Implement resource usage monitoring
        return {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "network_usage": 0.0
        } 