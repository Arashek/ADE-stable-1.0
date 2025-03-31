from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import logging
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)

class ToolCategory(Enum):
    """Categories of tools available in the system"""
    CODE_ANALYSIS = "code_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"
    TOOL_SELECTION = "tool_selection"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    ERROR_HANDLING = "error_handling"
    LEARNING = "learning"

class ToolState(Enum):
    """Possible states of a tool"""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    DISABLED = "disabled"

@dataclass
class ToolMetadata:
    """Metadata for a tool"""
    name: str
    version: str
    description: str
    author: str
    category: ToolCategory
    dependencies: List[str]
    requirements: List[str]
    capabilities: List[str]
    parameters: Dict[str, Any]
    return_type: str
    compatibility: Dict[str, str]
    last_updated: datetime

@dataclass
class ToolMetrics:
    """Metrics for tracking tool performance"""
    success_rate: float
    average_latency: float
    error_rate: float
    resource_usage: Dict[str, float]
    last_update: datetime

@dataclass
class ToolContext:
    """Context information for tool execution"""
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class ToolResult:
    """Result of tool execution"""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

class BaseTool(ABC):
    """Base class for all tools"""
    
    # Tool metadata
    name: str = "base_tool"
    description: str = "Base tool implementation"
    version: str = "1.0.0"
    author: str = "System"
    dependencies: List[str] = []
    capabilities: List[str] = []
    safety_level: str = "medium"
    
    # Performance limits
    max_execution_time: float = 5.0
    max_memory_increase: int = 100 * 1024 * 1024  # 100MB
    
    # Tool state
    is_tool: bool = True
    requires_llm: bool = False
    requires_pattern_learner: bool = False
    
    def __init__(self):
        self._context: Optional[ToolContext] = None
        self._metrics: Dict[str, float] = {}
        self._last_execution: Optional[datetime] = None
        
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> ToolResult:
        """Execute the tool with the given context"""
        pass
        
    @abstractmethod
    async def validate(self, context: Dict[str, Any]) -> bool:
        """Validate the tool's input context"""
        pass
        
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up any resources used by the tool"""
        pass
        
    async def initialize(self) -> None:
        """Initialize the tool"""
        try:
            # Check dependencies
            for dep in self.dependencies:
                try:
                    __import__(dep)
                except ImportError:
                    logger.error(f"Missing dependency: {dep}")
                    raise
                    
            # Initialize metrics
            self._metrics = {
                "execution_time": 0.0,
                "memory_usage": 0.0,
                "cpu_usage": 0.0,
                "success_rate": 1.0,
                "error_rate": 0.0,
                "usage_count": 0
            }
            
        except Exception as e:
            logger.error(f"Error initializing tool {self.name}: {str(e)}")
            raise
            
    async def pre_execute(self, context: Dict[str, Any]) -> None:
        """Pre-execution hook"""
        try:
            # Create tool context
            self._context = ToolContext(
                parameters=context,
                metadata={},
                timestamp=datetime.now()
            )
            
            # Validate context
            if not await self.validate(context):
                raise ValueError("Invalid context")
                
            # Check resource limits
            if not await self._check_resource_limits():
                raise ResourceWarning("Resource limits exceeded")
                
        except Exception as e:
            logger.error(f"Error in pre-execution: {str(e)}")
            raise
            
    async def post_execute(self, result: ToolResult) -> None:
        """Post-execution hook"""
        try:
            # Update metrics
            self._metrics["execution_time"] = result.execution_time
            self._metrics["usage_count"] += 1
            
            if result.success:
                self._metrics["success_rate"] = (
                    (self._metrics["success_rate"] * (self._metrics["usage_count"] - 1) + 1) 
                    / self._metrics["usage_count"]
                )
                self._metrics["error_rate"] = 1 - self._metrics["success_rate"]
            else:
                self._metrics["success_rate"] = (
                    (self._metrics["success_rate"] * (self._metrics["usage_count"] - 1)) 
                    / self._metrics["usage_count"]
                )
                self._metrics["error_rate"] = 1 - self._metrics["success_rate"]
                
            # Update last execution time
            self._last_execution = datetime.now()
            
        except Exception as e:
            logger.error(f"Error in post-execution: {str(e)}")
            
    async def _check_resource_limits(self) -> bool:
        """Check if resource usage is within limits"""
        try:
            import psutil
            process = psutil.Process()
            
            # Check memory usage
            memory_info = process.memory_info()
            if memory_info.rss > self.max_memory_increase:
                logger.warning(f"Memory usage {memory_info.rss} exceeds limit {self.max_memory_increase}")
                return False
                
            # Check CPU usage
            cpu_percent = process.cpu_percent()
            if cpu_percent > 80:  # 80% CPU usage limit
                logger.warning(f"CPU usage {cpu_percent}% exceeds limit 80%")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking resource limits: {str(e)}")
            return False
            
    def get_metrics(self) -> Dict[str, float]:
        """Get current tool metrics"""
        return self._metrics.copy()
        
    def get_context(self) -> Optional[ToolContext]:
        """Get current tool context"""
        return self._context
        
    def get_last_execution(self) -> Optional[datetime]:
        """Get last execution time"""
        return self._last_execution
        
    async def validate_parameters(self, **kwargs) -> bool:
        """Validate tool parameters"""
        try:
            # Check required parameters
            for param, spec in self.parameters.items():
                if spec.get("required", False) and param not in kwargs:
                    logger.error(f"Missing required parameter: {param}")
                    return False
                    
            # Validate parameter types
            for param, value in kwargs.items():
                if param in self.parameters:
                    spec = self.parameters[param]
                    expected_type = spec.get("type", "any")
                    
                    if expected_type != "any":
                        if not isinstance(value, eval(expected_type)):
                            logger.error(
                                f"Invalid type for parameter {param}: "
                                f"expected {expected_type}, got {type(value)}"
                            )
                            return False
                            
            return True
            
        except Exception as e:
            logger.error(f"Error validating parameters: {str(e)}")
            return False
            
    async def check_dependencies(self) -> bool:
        """Check if all dependencies are satisfied"""
        try:
            for dep in self.dependencies:
                # TODO: Implement dependency checking logic
                pass
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking dependencies: {str(e)}")
            return False
            
    async def update_metrics(self, execution_result: Dict[str, Any]) -> None:
        """Update tool metrics based on execution result"""
        try:
            # Update success rate
            if execution_result.get("success", False):
                self._metrics["success_rate"] = (
                    self._metrics["success_rate"] * 0.9 +
                    0.1
                )
            else:
                self._metrics["error_rate"] = (
                    self._metrics["error_rate"] * 0.9 +
                    0.1
                )
                
            # Update latency
            if "latency" in execution_result:
                self._metrics["execution_time"] = (
                    self._metrics["execution_time"] * 0.9 +
                    execution_result["latency"] * 0.1
                )
                
            # Update resource usage
            if "resource_usage" in execution_result:
                for resource, usage in execution_result["resource_usage"].items():
                    if resource not in self._metrics:
                        self._metrics[resource] = usage
                    else:
                        self._metrics[resource] = (
                            self._metrics[resource] * 0.9 +
                            usage * 0.1
                        )
                        
            self._metrics["last_update"] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}")
            
    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata"""
        return ToolMetadata(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            category=self.category,
            dependencies=self.dependencies,
            requirements=[],
            capabilities=self.capabilities,
            parameters={},
            return_type="dict",
            compatibility={},
            last_updated=datetime.now()
        )
        
    def get_metrics(self) -> ToolMetrics:
        """Get tool metrics"""
        return ToolMetrics(
            success_rate=self._metrics["success_rate"],
            average_latency=self._metrics["execution_time"],
            error_rate=self._metrics["error_rate"],
            resource_usage=self._metrics,
            last_update=self._metrics["last_update"]
        )
        
    def get_context(self) -> ToolContext:
        """Get tool context"""
        return self._context 