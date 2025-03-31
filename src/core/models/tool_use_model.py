from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
from .model_router import ModelRouter
from .providers.base import BaseModelProvider

class ToolDefinition(BaseModel):
    """Definition of a tool that can be used by the model"""
    name: str
    description: str
    parameters: Dict[str, Any]
    required_capabilities: List[str]
    cost_per_use: float
    timeout: float
    retry_count: int
    fallback_tools: List[str]

class ToolExecutionResult(BaseModel):
    """Result of executing a tool"""
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float
    cost: float
    metadata: Dict[str, Any] = {}

class ToolUseModel:
    """Specialized model for tool selection and execution"""
    
    def __init__(self, model_router: ModelRouter):
        self.model_router = model_router
        self.tools: Dict[str, ToolDefinition] = {}
        self.tool_execution_history: List[Dict[str, Any]] = []
        self.tool_performance_metrics: Dict[str, Dict[str, float]] = {}
        
    def register_tool(self, tool: ToolDefinition):
        """Register a new tool"""
        self.tools[tool.name] = tool
        self.tool_performance_metrics[tool.name] = {
            "success_rate": 0.0,
            "avg_execution_time": 0.0,
            "error_rate": 0.0,
            "cost_efficiency": 0.0
        }
        
    async def select_tool(self, task: str, context: Optional[Dict[str, Any]] = None) -> Tuple[str, str]:
        """Select the best tool for a given task"""
        # Prepare tool descriptions for the model
        tool_descriptions = []
        for name, tool in self.tools.items():
            desc = f"Tool: {name}\nDescription: {tool.description}\n"
            desc += f"Required capabilities: {', '.join(tool.required_capabilities)}\n"
            desc += f"Cost per use: {tool.cost_per_use}\n"
            desc += f"Timeout: {tool.timeout}s\n"
            desc += f"Retry count: {tool.retry_count}\n"
            desc += f"Fallback tools: {', '.join(tool.fallback_tools)}\n"
            tool_descriptions.append(desc)
            
        # Create prompt for tool selection
        prompt = f"""Given the following task and available tools, select the most appropriate tool to use.
        Consider the tool's capabilities, cost, and performance history.

        Task: {task}

        Available Tools:
        {'\n'.join(tool_descriptions)}

        Please provide:
        1. The name of the selected tool
        2. A brief explanation of why this tool is the best choice
        """
        
        # Get model response
        response = await self.model_router.route_task({
            "task_type": "tool_selection",
            "content": prompt,
            "context": context
        })
        
        # Parse response to get tool name and explanation
        lines = response.content.split('\n')
        tool_name = lines[0].strip()
        explanation = lines[1].strip() if len(lines) > 1 else ""
        
        return tool_name, explanation
        
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolExecutionResult:
        """Execute a tool with the given parameters"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
            
        tool = self.tools[tool_name]
        start_time = time.time()
        
        try:
            # Validate parameters
            self._validate_parameters(tool, parameters)
            
            # Execute tool with retries
            for attempt in range(tool.retry_count):
                try:
                    result = await self._execute_with_timeout(tool, parameters, context)
                    execution_time = time.time() - start_time
                    
                    # Update performance metrics
                    self._update_tool_metrics(tool_name, True, execution_time, result.get("cost", 0))
                    
                    return ToolExecutionResult(
                        success=True,
                        output=result.get("output"),
                        execution_time=execution_time,
                        cost=result.get("cost", 0),
                        metadata=result.get("metadata", {})
                    )
                    
                except TimeoutError:
                    if attempt == tool.retry_count - 1:
                        raise
                    await asyncio.sleep(1)  # Wait before retry
                    
        except Exception as e:
            execution_time = time.time() - start_time
            self._update_tool_metrics(tool_name, False, execution_time, 0)
            
            # Try fallback tools if available
            for fallback_name in tool.fallback_tools:
                if fallback_name in self.tools:
                    try:
                        return await self.execute_tool(fallback_name, parameters, context)
                    except Exception:
                        continue
                        
            return ToolExecutionResult(
                success=False,
                output=None,
                error=str(e),
                execution_time=execution_time,
                cost=0
            )
            
    def _validate_parameters(self, tool: ToolDefinition, parameters: Dict[str, Any]):
        """Validate tool parameters"""
        for param_name, param_spec in tool.parameters.items():
            if param_name not in parameters:
                raise ValueError(f"Missing required parameter: {param_name}")
                
            param_value = parameters[param_name]
            param_type = param_spec.get("type")
            
            if param_type == "string" and not isinstance(param_value, str):
                raise ValueError(f"Parameter {param_name} must be a string")
            elif param_type == "number" and not isinstance(param_value, (int, float)):
                raise ValueError(f"Parameter {param_name} must be a number")
            elif param_type == "boolean" and not isinstance(param_value, bool):
                raise ValueError(f"Parameter {param_name} must be a boolean")
                
    async def _execute_with_timeout(self, tool: ToolDefinition, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute tool with timeout"""
        async with asyncio.timeout(tool.timeout):
            # Get the appropriate model for tool execution
            model = await self.model_router.get_model_for_capability(tool.required_capabilities[0])
            
            # Execute tool using the model
            result = await model.execute_tool(tool.name, parameters, context)
            
            return result
            
    def _update_tool_metrics(self, tool_name: str, success: bool, execution_time: float, cost: float):
        """Update tool performance metrics"""
        metrics = self.tool_performance_metrics[tool_name]
        
        # Update success rate
        metrics["success_rate"] = 0.9 * metrics["success_rate"] + 0.1 * (1 if success else 0)
        
        # Update average execution time
        metrics["avg_execution_time"] = 0.9 * metrics["avg_execution_time"] + 0.1 * execution_time
        
        # Update error rate
        metrics["error_rate"] = 0.9 * metrics["error_rate"] + 0.1 * (0 if success else 1)
        
        # Update cost efficiency
        metrics["cost_efficiency"] = 0.9 * metrics["cost_efficiency"] + 0.1 * (1 / (cost + 1))
        
    def get_tool_metrics(self, tool_name: str) -> Dict[str, float]:
        """Get performance metrics for a tool"""
        return self.tool_performance_metrics.get(tool_name, {})
        
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get tool execution history"""
        return self.tool_execution_history 