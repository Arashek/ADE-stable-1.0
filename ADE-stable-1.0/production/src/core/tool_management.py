from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Callable, Union
from enum import Enum
from datetime import datetime
import logging
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import traceback

logger = logging.getLogger(__name__)

class ToolType(Enum):
    CODE_ANALYSIS = "code_analysis"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    UTILITY = "utility"
    API = "api"

class ToolStatus(Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    FAILED = "failed"
    DEPRECATED = "deprecated"

@dataclass
class ToolMetrics:
    success_count: int = 0
    failure_count: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    error_patterns: Dict[str, int] = field(default_factory=dict)
    cost_tracking: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ToolSpec:
    tool_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    type: ToolType = ToolType.UTILITY
    version: str = "1.0.0"
    capabilities: Set[str] = field(default_factory=set)
    required_inputs: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    error_schema: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    cost_per_call: float = 0.0
    rate_limit: Optional[int] = None
    rate_limit_period: Optional[float] = None
    status: ToolStatus = ToolStatus.AVAILABLE
    metrics: ToolMetrics = field(default_factory=ToolMetrics)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolResult:
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class ToolManager:
    def __init__(self):
        self.tools: Dict[str, ToolSpec] = {}
        self.tool_implementations: Dict[str, Callable] = {}
        self.tool_usage_history: List[Dict[str, Any]] = []
        self.tool_performance_data: Dict[str, List[Dict[str, Any]]] = {}
        self.tool_dependencies: Dict[str, Set[str]] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    async def register_tool(self, spec: ToolSpec, implementation: Callable) -> bool:
        """Register a new tool with its specification and implementation."""
        try:
            self.tools[spec.tool_id] = spec
            self.tool_implementations[spec.tool_id] = implementation
            self.tool_performance_data[spec.tool_id] = []
            return True
        except Exception as e:
            logger.error(f"Failed to register tool {spec.name}: {str(e)}")
            return False
    
    async def execute_tool(self, tool_id: str, inputs: Dict[str, Any],
                          context: Dict[str, Any] = None) -> ToolResult:
        """Execute a tool with the given inputs and context."""
        if tool_id not in self.tools or tool_id not in self.tool_implementations:
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool {tool_id} not found"
            )
        
        tool = self.tools[tool_id]
        start_time = datetime.now()
        
        # Check rate limits
        if not await self._check_rate_limit(tool):
            return ToolResult(
                success=False,
                output=None,
                error="Rate limit exceeded"
            )
        
        # Validate inputs
        if not await self._validate_inputs(tool, inputs):
            return ToolResult(
                success=False,
                output=None,
                error="Invalid inputs"
            )
        
        # Execute tool with retries
        for attempt in range(tool.retry_count):
            try:
                # Run tool in thread pool to handle blocking operations
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    self.tool_implementations[tool_id],
                    inputs,
                    context
                )
                
                # Update metrics
                execution_time = (datetime.now() - start_time).total_seconds()
                await self._update_tool_metrics(tool, True, execution_time)
                
                return ToolResult(
                    success=True,
                    output=result,
                    execution_time=execution_time,
                    cost=tool.cost_per_call
                )
            
            except Exception as e:
                if attempt < tool.retry_count - 1:
                    await asyncio.sleep(tool.retry_delay)
                    continue
                
                # Update metrics for failure
                execution_time = (datetime.now() - start_time).total_seconds()
                await self._update_tool_metrics(tool, False, execution_time)
                
                return ToolResult(
                    success=False,
                    output=None,
                    error=str(e),
                    execution_time=execution_time,
                    cost=tool.cost_per_call
                )
    
    async def execute_tool_pipeline(self, pipeline: List[Dict[str, Any]],
                                  context: Dict[str, Any] = None) -> List[ToolResult]:
        """Execute a sequence of tools in a pipeline."""
        results = []
        for step in pipeline:
            tool_id = step["tool_id"]
            inputs = step["inputs"]
            condition = step.get("condition")
            
            # Check condition if specified
            if condition and not self._evaluate_condition(condition, results):
                continue
            
            result = await self.execute_tool(tool_id, inputs, context)
            results.append(result)
            
            if not result.success:
                # Handle pipeline failure
                if step.get("fail_fast", True):
                    break
        
        return results
    
    async def execute_parallel_tools(self, tools: List[Dict[str, Any]],
                                   context: Dict[str, Any] = None) -> List[ToolResult]:
        """Execute multiple tools in parallel."""
        tasks = []
        for tool_spec in tools:
            task = self.execute_tool(
                tool_spec["tool_id"],
                tool_spec["inputs"],
                context
            )
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    async def recommend_tools(self, task_description: str,
                            context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Recommend tools based on task description and context."""
        recommendations = []
        
        # Analyze task description to identify required capabilities
        required_capabilities = await self._analyze_task_capabilities(task_description)
        
        # Find matching tools
        for tool_id, tool in self.tools.items():
            if tool.status != ToolStatus.AVAILABLE:
                continue
            
            # Calculate match score
            match_score = await self._calculate_tool_match_score(
                tool, required_capabilities, context
            )
            
            if match_score > 0.5:  # Minimum match threshold
                recommendations.append({
                    "tool_id": tool_id,
                    "name": tool.name,
                    "description": tool.description,
                    "match_score": match_score,
                    "capabilities": list(tool.capabilities),
                    "performance_metrics": {
                        "success_rate": tool.metrics.success_count /
                                      (tool.metrics.success_count + tool.metrics.failure_count)
                        if (tool.metrics.success_count + tool.metrics.failure_count) > 0
                        else 0.0,
                        "average_execution_time": tool.metrics.average_execution_time
                    }
                })
        
        # Sort by match score
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        return recommendations
    
    async def _analyze_task_capabilities(self, task_description: str) -> Set[str]:
        """Analyze task description to identify required capabilities."""
        # This is a simplified version - in practice, you'd use NLP or similar
        capabilities = set()
        
        # Map keywords to capabilities
        capability_keywords = {
            "test": "testing",
            "deploy": "deployment",
            "document": "documentation",
            "analyze": "code_analysis",
            "optimize": "performance_optimization",
            "security": "security_analysis"
        }
        
        for keyword, capability in capability_keywords.items():
            if keyword in task_description.lower():
                capabilities.add(capability)
        
        return capabilities
    
    async def _calculate_tool_match_score(self, tool: ToolSpec,
                                        required_capabilities: Set[str],
                                        context: Dict[str, Any] = None) -> float:
        """Calculate how well a tool matches the required capabilities."""
        # Calculate capability match
        capability_match = len(tool.capabilities.intersection(required_capabilities)) / \
                         len(required_capabilities) if required_capabilities else 0.0
        
        # Calculate performance score
        total_calls = tool.metrics.success_count + tool.metrics.failure_count
        performance_score = tool.metrics.success_count / total_calls if total_calls > 0 else 0.0
        
        # Calculate cost efficiency
        cost_score = 1.0 - min(tool.cost_per_call / 100.0, 1.0)  # Normalize cost
        
        # Combine scores with weights
        return (0.4 * capability_match +
                0.4 * performance_score +
                0.2 * cost_score)
    
    async def _check_rate_limit(self, tool: ToolSpec) -> bool:
        """Check if tool is within rate limits."""
        if not tool.rate_limit or not tool.rate_limit_period:
            return True
        
        # Count recent calls
        recent_calls = sum(
            1 for usage in self.tool_usage_history
            if usage["tool_id"] == tool.tool_id and
            (datetime.now() - usage["timestamp"]).total_seconds() <= tool.rate_limit_period
        )
        
        return recent_calls < tool.rate_limit
    
    async def _validate_inputs(self, tool: ToolSpec, inputs: Dict[str, Any]) -> bool:
        """Validate tool inputs against required schema."""
        for key, schema in tool.required_inputs.items():
            if key not in inputs:
                return False
            
            # Validate type
            if "type" in schema:
                if not isinstance(inputs[key], eval(schema["type"])):
                    return False
            
            # Validate format
            if "format" in schema:
                if not self._validate_format(inputs[key], schema["format"]):
                    return False
        
        return True
    
    def _validate_format(self, value: Any, format_spec: str) -> bool:
        """Validate value against format specification."""
        # Implement format validation logic
        return True
    
    async def _update_tool_metrics(self, tool: ToolSpec, success: bool,
                                 execution_time: float) -> None:
        """Update tool performance metrics."""
        if success:
            tool.metrics.success_count += 1
            tool.metrics.last_success = datetime.now()
        else:
            tool.metrics.failure_count += 1
            tool.metrics.last_failure = datetime.now()
        
        tool.metrics.total_execution_time += execution_time
        tool.metrics.average_execution_time = (
            tool.metrics.total_execution_time /
            (tool.metrics.success_count + tool.metrics.failure_count)
        )
        tool.metrics.last_updated = datetime.now()
        
        # Record usage
        self.tool_usage_history.append({
            "tool_id": tool.tool_id,
            "timestamp": datetime.now(),
            "success": success,
            "execution_time": execution_time,
            "cost": tool.cost_per_call
        })
    
    def _evaluate_condition(self, condition: Dict[str, Any],
                          previous_results: List[ToolResult]) -> bool:
        """Evaluate condition for pipeline execution."""
        if not condition:
            return True
        
        # Implement condition evaluation logic
        return True
    
    async def get_tool_performance_report(self) -> Dict[str, Any]:
        """Generate a performance report for all tools."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "tools": {}
        }
        
        for tool_id, tool in self.tools.items():
            report["tools"][tool_id] = {
                "name": tool.name,
                "type": tool.type.value,
                "status": tool.status.value,
                "metrics": {
                    "success_rate": tool.metrics.success_count /
                                  (tool.metrics.success_count + tool.metrics.failure_count)
                    if (tool.metrics.success_count + tool.metrics.failure_count) > 0
                    else 0.0,
                    "average_execution_time": tool.metrics.average_execution_time,
                    "total_cost": sum(tool.metrics.cost_tracking.values()),
                    "error_patterns": tool.metrics.error_patterns
                },
                "usage_history": self.tool_usage_history[-10:]  # Last 10 uses
            }
        
        return report 