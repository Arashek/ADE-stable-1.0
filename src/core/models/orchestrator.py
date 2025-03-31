from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
from .model_router import ModelRouter
from .ast_parser import ASTParser
from .security_analyzer import SecurityAnalyzer
from .code_generation_model import CodeGenerationModel
from .tool_use_model import ToolUseModel
from .planning_model import PlanningModel
from .integration_manager import ModelIntegrationManager
from .optimization_manager import OptimizationManager
from .performance_analyzer import PerformanceAnalyzer

class OrchestrationResult(BaseModel):
    """Result of orchestrated model operations"""
    task_id: str
    task_type: str
    status: str
    result: Any
    metrics: Dict[str, float]
    recommendations: List[str]
    metadata: Dict[str, Any] = {}

class ModelOrchestrator:
    """Main orchestrator for coordinating model components"""
    
    def __init__(self):
        self.model_router = ModelRouter()
        self.integration_manager = ModelIntegrationManager(self.model_router)
        self.optimization_manager = OptimizationManager()
        self.performance_analyzer = PerformanceAnalyzer()
        self.task_history: List[OrchestrationResult] = []
        
    async def execute_task(
        self,
        task_id: str,
        task_type: str,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> OrchestrationResult:
        """Execute a task using appropriate model components"""
        try:
            # Initialize result
            result = OrchestrationResult(
                task_id=task_id,
                task_type=task_type,
                status="PENDING",
                result=None,
                metrics={},
                recommendations=[],
                metadata={
                    "started_at": datetime.now().isoformat(),
                    "context": context or {}
                }
            )
            
            # Collect initial performance metrics
            initial_metrics = self.performance_analyzer.collect_metrics()
            
            # Execute task based on type
            if task_type == "code_analysis":
                result.result = await self._execute_code_analysis(task_data, context)
            elif task_type == "code_generation":
                result.result = await self._execute_code_generation(task_data, context)
            elif task_type == "tool_execution":
                result.result = await self._execute_tool(task_data, context)
            elif task_type == "planning":
                result.result = await self._execute_planning(task_data, context)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
            # Collect final performance metrics
            final_metrics = self.performance_analyzer.collect_metrics()
            
            # Calculate task metrics
            result.metrics = self._calculate_task_metrics(
                initial_metrics,
                final_metrics,
                result.result
            )
            
            # Generate recommendations
            result.recommendations = self._generate_recommendations(
                result.result,
                result.metrics
            )
            
            # Update status
            result.status = "COMPLETED"
            result.metadata["completed_at"] = datetime.now().isoformat()
            
            # Store in history
            self.task_history.append(result)
            
            return result
            
        except Exception as e:
            # Update status and store error
            result.status = "FAILED"
            result.metadata["error"] = str(e)
            result.metadata["completed_at"] = datetime.now().isoformat()
            self.task_history.append(result)
            raise
            
    async def _execute_code_analysis(
        self,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute code analysis task"""
        code = task_data.get("code")
        if not code:
            raise ValueError("Code is required for code analysis")
            
        # Perform integrated analysis
        analysis_result = await self.integration_manager.analyze_code(
            code=code,
            task_type="code_analysis",
            context=context
        )
        
        # Optimize code if needed
        if analysis_result.metrics.get("quality_score", 0) < 0.7:
            optimization_result = await self.optimization_manager.optimize_code(
                code=code,
                optimization_level="balanced",
                context=context
            )
            analysis_result.optimized_code = optimization_result.optimized_code
            analysis_result.improvements.extend(optimization_result.improvements)
            
        return analysis_result
        
    async def _execute_code_generation(
        self,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute code generation task"""
        requirements = task_data.get("requirements")
        language = task_data.get("language", "python")
        framework = task_data.get("framework")
        
        if not requirements:
            raise ValueError("Requirements are required for code generation")
            
        # Generate code
        generation_result = await self.integration_manager.analyze_code(
            code="",  # Empty code for generation
            task_type="code_generation",
            context={
                "requirements": requirements,
                "language": language,
                "framework": framework,
                **(context or {})
            }
        )
        
        # Optimize generated code
        if generation_result.code_generation:
            optimization_result = await self.optimization_manager.optimize_code(
                code=generation_result.code_generation.code,
                optimization_level="balanced",
                context=context
            )
            generation_result.code_generation.code = optimization_result.optimized_code
            generation_result.improvements.extend(optimization_result.improvements)
            
        return generation_result
        
    async def _execute_tool(
        self,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute tool task"""
        tool_name = task_data.get("tool_name")
        parameters = task_data.get("parameters", {})
        
        if not tool_name:
            raise ValueError("Tool name is required for tool execution")
            
        # Execute tool
        return await self.integration_manager.analyze_code(
            code="",  # Empty code for tool execution
            task_type="tool_execution",
            context={
                "tool_name": tool_name,
                "parameters": parameters,
                **(context or {})
            }
        )
        
    async def _execute_planning(
        self,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute planning task"""
        task_description = task_data.get("task_description")
        
        if not task_description:
            raise ValueError("Task description is required for planning")
            
        # Create plan
        return await self.integration_manager.analyze_code(
            code="",  # Empty code for planning
            task_type="planning",
            context={
                "task_description": task_description,
                **(context or {})
            }
        )
        
    def _calculate_task_metrics(
        self,
        initial_metrics: Any,
        final_metrics: Any,
        result: Any
    ) -> Dict[str, float]:
        """Calculate task-specific metrics"""
        metrics = {
            "execution_time": (
                final_metrics.timestamp - initial_metrics.timestamp
            ).total_seconds(),
            "cpu_usage": final_metrics.cpu_usage - initial_metrics.cpu_usage,
            "memory_usage": final_metrics.memory_usage - initial_metrics.memory_usage,
            "disk_usage": final_metrics.disk_usage - initial_metrics.disk_usage
        }
        
        # Add result-specific metrics
        if hasattr(result, "metrics"):
            metrics.update(result.metrics)
            
        return metrics
        
    def _generate_recommendations(
        self,
        result: Any,
        metrics: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations based on results and metrics"""
        recommendations = []
        
        # Add result-specific recommendations
        if hasattr(result, "recommendations"):
            recommendations.extend(result.recommendations)
            
        # Add performance-based recommendations
        if metrics.get("cpu_usage", 0) > 80:
            recommendations.append("High CPU usage detected. Consider optimizing resource usage.")
        if metrics.get("memory_usage", 0) > 80:
            recommendations.append("High memory usage detected. Consider optimizing memory allocation.")
        if metrics.get("disk_usage", 0) > 80:
            recommendations.append("High disk usage detected. Consider cleaning up unused resources.")
            
        return list(set(recommendations))  # Remove duplicates
        
    def get_task_history(
        self,
        task_type: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[OrchestrationResult]:
        """Get task history with filters"""
        filtered_tasks = self.task_history
        
        if task_type:
            filtered_tasks = [
                t for t in filtered_tasks
                if t.task_type == task_type
            ]
            
        if status:
            filtered_tasks = [
                t for t in filtered_tasks
                if t.status == status
            ]
            
        if start_time:
            filtered_tasks = [
                t for t in filtered_tasks
                if datetime.fromisoformat(t.metadata["started_at"]) >= start_time
            ]
            
        if end_time:
            filtered_tasks = [
                t for t in filtered_tasks
                if datetime.fromisoformat(t.metadata["completed_at"]) <= end_time
            ]
            
        return filtered_tasks
        
    def get_performance_stats(
        self,
        window: int = 3600  # 1 hour in seconds
    ) -> Dict[str, float]:
        """Get performance statistics"""
        return self.performance_analyzer.get_performance_stats(window)
        
    def get_optimization_stats(self) -> Dict[str, float]:
        """Get optimization statistics"""
        return self.optimization_manager.get_optimization_stats() 