from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import logging
import importlib
import inspect
import asyncio
from pathlib import Path
import yaml
import json

logger = logging.getLogger(__name__)

@dataclass
class ToolMetadata:
    """Metadata for a discovered tool"""
    name: str
    description: str
    version: str
    author: str
    dependencies: List[str]
    capabilities: List[str]
    safety_level: str
    performance_metrics: Dict[str, float]
    last_used: datetime
    usage_count: int
    success_rate: float

class ToolDiscoverySystem:
    """System for discovering, validating, and managing tools"""
    
    def __init__(self, llm_manager, pattern_learner):
        self.llm_manager = llm_manager
        self.pattern_learner = pattern_learner
        self.tool_registry: Dict[str, ToolMetadata] = {}
        self.tool_instances: Dict[str, Any] = {}
        self.tool_dependencies: Dict[str, Set[str]] = {}
        self.tool_metrics: Dict[str, Dict[str, float]] = {}
        self.discovery_paths: List[Path] = []
        self._lock = asyncio.Lock()
        
    async def initialize(self) -> None:
        """Initialize the tool discovery system"""
        try:
            # Load configuration
            config_path = Path("src/core/tools/config/discovery.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
                    self.discovery_paths = [Path(p) for p in config.get("discovery_paths", [])]
            else:
                logger.warning("Discovery configuration not found")
                
            # Initialize discovery paths
            if not self.discovery_paths:
                self.discovery_paths = [
                    Path("src/core/tools/providers"),
                    Path("src/core/tools/patterns"),
                    Path("src/core/tools/optimization")
                ]
                
            # Create discovery paths if they don't exist
            for path in self.discovery_paths:
                path.mkdir(parents=True, exist_ok=True)
                
            # Start discovery process
            await self.discover_tools()
            
        except Exception as e:
            logger.error(f"Error initializing tool discovery system: {str(e)}")
            
    async def discover_tools(self) -> None:
        """Discover available tools in the configured paths"""
        try:
            async with self._lock:
                for path in self.discovery_paths:
                    # Find Python files
                    for file_path in path.glob("**/*.py"):
                        if file_path.name.startswith("_"):
                            continue
                            
                        # Import module
                        try:
                            module_name = str(file_path.relative_to(Path("src"))).replace("/", ".").replace(".py", "")
                            module = importlib.import_module(module_name)
                            
                            # Find tool classes
                            for name, obj in inspect.getmembers(module):
                                if (inspect.isclass(obj) and 
                                    hasattr(obj, "is_tool") and 
                                    obj.is_tool):
                                    await self.register_tool(obj)
                                    
                        except Exception as e:
                            logger.error(f"Error discovering tools in {file_path}: {str(e)}")
                            
        except Exception as e:
            logger.error(f"Error in tool discovery: {str(e)}")
            
    async def register_tool(self, tool_class: type) -> None:
        """Register a discovered tool"""
        try:
            # Create tool instance
            tool = tool_class()
            
            # Extract metadata
            metadata = await self._extract_tool_metadata(tool)
            
            # Check compatibility
            if not await self._check_tool_compatibility(tool):
                logger.warning(f"Tool {metadata.name} is not compatible")
                return
                
            # Validate tool
            if not await self._validate_tool(tool):
                logger.warning(f"Tool {metadata.name} failed validation")
                return
                
            # Register tool
            self.tool_registry[metadata.name] = metadata
            self.tool_instances[metadata.name] = tool
            
            # Update dependencies
            self.tool_dependencies[metadata.name] = set(metadata.dependencies)
            
            # Initialize metrics
            self.tool_metrics[metadata.name] = {
                "execution_time": 0.0,
                "success_rate": 1.0,
                "error_rate": 0.0,
                "usage_count": 0
            }
            
            logger.info(f"Registered tool: {metadata.name}")
            
        except Exception as e:
            logger.error(f"Error registering tool {tool_class.__name__}: {str(e)}")
            
    async def _extract_tool_metadata(self, tool: Any) -> ToolMetadata:
        """Extract metadata from a tool"""
        try:
            # Get tool information
            name = getattr(tool, "name", tool.__class__.__name__)
            description = getattr(tool, "description", "")
            version = getattr(tool, "version", "1.0.0")
            author = getattr(tool, "author", "Unknown")
            dependencies = getattr(tool, "dependencies", [])
            capabilities = getattr(tool, "capabilities", [])
            safety_level = getattr(tool, "safety_level", "medium")
            
            return ToolMetadata(
                name=name,
                description=description,
                version=version,
                author=author,
                dependencies=dependencies,
                capabilities=capabilities,
                safety_level=safety_level,
                performance_metrics={},
                last_used=datetime.now(),
                usage_count=0,
                success_rate=1.0
            )
            
        except Exception as e:
            logger.error(f"Error extracting tool metadata: {str(e)}")
            raise
            
    async def _check_tool_compatibility(self, tool: Any) -> bool:
        """Check if a tool is compatible with the system"""
        try:
            # Check required methods
            required_methods = ["execute", "validate", "cleanup"]
            for method in required_methods:
                if not hasattr(tool, method):
                    logger.warning(f"Tool missing required method: {method}")
                    return False
                    
            # Check dependencies
            dependencies = getattr(tool, "dependencies", [])
            for dep in dependencies:
                try:
                    importlib.import_module(dep)
                except ImportError:
                    logger.warning(f"Missing dependency: {dep}")
                    return False
                    
            # Check LLM compatibility
            if hasattr(tool, "requires_llm"):
                if not self.llm_manager:
                    logger.warning("Tool requires LLM but LLM manager not available")
                    return False
                    
            # Check pattern learner compatibility
            if hasattr(tool, "requires_pattern_learner"):
                if not self.pattern_learner:
                    logger.warning("Tool requires pattern learner but not available")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error checking tool compatibility: {str(e)}")
            return False
            
    async def _validate_tool(self, tool: Any) -> bool:
        """Validate a tool's implementation"""
        try:
            # Check safety
            if not await self._check_tool_safety(tool):
                return False
                
            # Check performance
            if not await self._check_tool_performance(tool):
                return False
                
            # Check resource usage
            if not await self._check_tool_resources(tool):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating tool: {str(e)}")
            return False
            
    async def _check_tool_safety(self, tool: Any) -> bool:
        """Check if a tool is safe to use"""
        try:
            # Check safety level
            safety_level = getattr(tool, "safety_level", "medium")
            if safety_level == "high":
                # Additional safety checks for high-risk tools
                if not hasattr(tool, "safety_checks"):
                    return False
                    
            # Check for dangerous operations
            code = inspect.getsource(tool.__class__)
            dangerous_patterns = [
                r"os\.system\(",
                r"subprocess\.call\(",
                r"eval\(",
                r"exec\("
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, code):
                    logger.warning(f"Tool contains dangerous operation: {pattern}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error checking tool safety: {str(e)}")
            return False
            
    async def _check_tool_performance(self, tool: Any) -> bool:
        """Check if a tool meets performance requirements"""
        try:
            # Run performance test
            start_time = datetime.now()
            await tool.execute({"test": True})
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Check against thresholds
            max_execution_time = getattr(tool, "max_execution_time", 5.0)
            if execution_time > max_execution_time:
                logger.warning(f"Tool execution time {execution_time}s exceeds threshold {max_execution_time}s")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking tool performance: {str(e)}")
            return False
            
    async def _check_tool_resources(self, tool: Any) -> bool:
        """Check if a tool uses resources appropriately"""
        try:
            # Check memory usage
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss
            
            # Run resource test
            await tool.execute({"test": True})
            
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # Check against thresholds
            max_memory_increase = getattr(tool, "max_memory_increase", 100 * 1024 * 1024)  # 100MB
            if memory_increase > max_memory_increase:
                logger.warning(f"Tool memory increase {memory_increase} exceeds threshold {max_memory_increase}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking tool resources: {str(e)}")
            return False
            
    async def get_tool(self, name: str) -> Optional[Any]:
        """Get a tool by name"""
        return self.tool_instances.get(name)
        
    async def get_tool_metadata(self, name: str) -> Optional[ToolMetadata]:
        """Get metadata for a tool"""
        return self.tool_registry.get(name)
        
    async def get_tool_dependencies(self, name: str) -> Set[str]:
        """Get dependencies for a tool"""
        return self.tool_dependencies.get(name, set())
        
    async def get_tool_metrics(self, name: str) -> Dict[str, float]:
        """Get performance metrics for a tool"""
        return self.tool_metrics.get(name, {})
        
    async def update_tool_metrics(self, name: str, execution_time: float, success: bool) -> None:
        """Update performance metrics for a tool"""
        try:
            if name not in self.tool_metrics:
                return
                
            metrics = self.tool_metrics[name]
            metrics["execution_time"] = (metrics["execution_time"] * metrics["usage_count"] + execution_time) / (metrics["usage_count"] + 1)
            metrics["usage_count"] += 1
            
            if success:
                metrics["success_rate"] = (metrics["success_rate"] * (metrics["usage_count"] - 1) + 1) / metrics["usage_count"]
                metrics["error_rate"] = 1 - metrics["success_rate"]
            else:
                metrics["success_rate"] = (metrics["success_rate"] * (metrics["usage_count"] - 1)) / metrics["usage_count"]
                metrics["error_rate"] = 1 - metrics["success_rate"]
                
        except Exception as e:
            logger.error(f"Error updating tool metrics: {str(e)}")
            
    async def optimize_tool_usage(self, name: str) -> Dict[str, Any]:
        """Optimize usage of a tool"""
        try:
            tool = await self.get_tool(name)
            if not tool:
                return {}
                
            # Get current metrics
            metrics = await self.get_tool_metrics(name)
            
            # Generate optimization suggestions
            suggestions = []
            
            # Check execution time
            if metrics["execution_time"] > 1.0:  # More than 1 second
                suggestions.append({
                    "type": "performance",
                    "message": "Consider caching results or optimizing algorithm",
                    "impact": "high"
                })
                
            # Check success rate
            if metrics["success_rate"] < 0.8:  # Less than 80% success rate
                suggestions.append({
                    "type": "reliability",
                    "message": "Review error handling and input validation",
                    "impact": "high"
                })
                
            # Check resource usage
            if metrics.get("memory_usage", 0) > 100 * 1024 * 1024:  # More than 100MB
                suggestions.append({
                    "type": "resource",
                    "message": "Consider implementing memory cleanup",
                    "impact": "medium"
                })
                
            return {
                "suggestions": suggestions,
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Error optimizing tool usage: {str(e)}")
            return {} 