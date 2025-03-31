from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
from .model_router import ModelRouter
from .ast_parser import ASTParser, ASTAnalysisResult
from .security_analyzer import SecurityAnalyzer, SecurityAnalysisResult
from .code_quality_analyzer import CodeQualityAnalyzer, CodeQualityResult
from .code_generation_model import CodeGenerationModel, CodeGenerationResult
from .tool_use_model import ToolUseModel, ToolExecutionResult
from .planning_model import PlanningModel, TaskPlan

class ModelIntegrationResult(BaseModel):
    """Result of integrated model analysis"""
    ast_analysis: Optional[ASTAnalysisResult] = None
    security_analysis: Optional[SecurityAnalysisResult] = None
    quality_analysis: Optional[CodeQualityResult] = None
    code_generation: Optional[CodeGenerationResult] = None
    tool_execution: Optional[ToolExecutionResult] = None
    task_plan: Optional[TaskPlan] = None
    metrics: Dict[str, float]
    recommendations: List[str]
    metadata: Dict[str, Any] = {}

class ModelIntegrationManager:
    """Manager for coordinating between different model components"""
    
    def __init__(self, model_router: ModelRouter):
        self.model_router = model_router
        self.ast_parser = ASTParser()
        self.security_analyzer = SecurityAnalyzer()
        self.quality_analyzer = CodeQualityAnalyzer()
        self.code_generator = CodeGenerationModel(model_router)
        self.tool_use_model = ToolUseModel(model_router)
        self.planning_model = PlanningModel(model_router)
        self.integration_metrics: Dict[str, Dict[str, float]] = {}
        
    async def analyze_code(
        self,
        code: str,
        task_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ModelIntegrationResult:
        """Perform integrated code analysis"""
        try:
            # Initialize result
            result = ModelIntegrationResult(
                metrics={},
                recommendations=[],
                metadata={
                    "task_type": task_type,
                    "analyzed_at": datetime.now().isoformat()
                }
            )
            
            # Perform AST analysis
            result.ast_analysis = self.ast_parser.parse_code(code)
            
            # Perform security analysis
            result.security_analysis = self.security_analyzer.analyze_code(code)
            
            # Perform quality analysis
            result.quality_analysis = self.quality_analyzer.analyze_code(code)
            
            # Generate code if needed
            if task_type == "code_generation":
                result.code_generation = await self.code_generator.generate_code(
                    requirements=context.get("requirements", ""),
                    language=context.get("language", "python"),
                    framework=context.get("framework"),
                    context=context
                )
                
            # Execute tools if needed
            if task_type == "tool_execution":
                tool_name = context.get("tool_name")
                parameters = context.get("parameters", {})
                result.tool_execution = await self.tool_use_model.execute_tool(
                    tool_name=tool_name,
                    parameters=parameters,
                    context=context
                )
                
            # Create task plan if needed
            if task_type == "planning":
                result.task_plan = await self.planning_model.create_plan(
                    task_description=context.get("task_description", ""),
                    context=context
                )
                
            # Calculate integrated metrics
            result.metrics = self._calculate_integrated_metrics(result)
            
            # Generate integrated recommendations
            result.recommendations = self._generate_integrated_recommendations(result)
            
            # Update integration metrics
            self._update_integration_metrics(result)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to perform integrated analysis: {str(e)}")
            
    def _calculate_integrated_metrics(self, result: ModelIntegrationResult) -> Dict[str, float]:
        """Calculate integrated metrics from all analyses"""
        metrics = {}
        
        # AST metrics
        if result.ast_analysis:
            metrics.update({
                f"ast_{k}": v
                for k, v in result.ast_analysis.metrics.items()
            })
            
        # Security metrics
        if result.security_analysis:
            metrics.update({
                f"security_{k}": v
                for k, v in result.security_analysis.metrics.items()
            })
            metrics["security_risk_score"] = result.security_analysis.risk_score
            
        # Quality metrics
        if result.quality_analysis:
            metrics.update({
                f"quality_{k}": v
                for k, v in result.quality_analysis.metrics.items()
            })
            metrics["quality_overall_score"] = result.quality_analysis.overall_score
            
        # Code generation metrics
        if result.code_generation:
            metrics.update({
                f"generation_{k}": v
                for k, v in result.code_generation.quality_metrics.dict().items()
            })
            
        # Tool execution metrics
        if result.tool_execution:
            metrics.update({
                "tool_success": float(result.tool_execution.success),
                "tool_execution_time": result.tool_execution.execution_time,
                "tool_cost": result.tool_execution.cost
            })
            
        # Planning metrics
        if result.task_plan:
            metrics.update({
                "plan_steps": len(result.task_plan.steps),
                "plan_resources": len(result.task_plan.resources),
                "plan_cost": result.task_plan.total_cost or 0.0
            })
            
        return metrics
        
    def _generate_integrated_recommendations(self, result: ModelIntegrationResult) -> List[str]:
        """Generate integrated recommendations from all analyses"""
        recommendations = []
        
        # Security recommendations
        if result.security_analysis:
            recommendations.extend(result.security_analysis.recommendations)
            
        # Quality recommendations
        if result.quality_analysis:
            recommendations.extend(result.quality_analysis.suggestions)
            
        # Code quality recommendations
        if result.ast_analysis:
            recommendations.extend(result.ast_analysis.suggestions)
            
        # Code generation recommendations
        if result.code_generation:
            quality_metrics = result.code_generation.quality_metrics
            if quality_metrics.complexity < 0.7:
                recommendations.append("Consider reducing code complexity")
            if quality_metrics.maintainability < 0.7:
                recommendations.append("Improve code maintainability")
            if quality_metrics.testability < 0.7:
                recommendations.append("Add more test coverage")
                
        # Tool execution recommendations
        if result.tool_execution and not result.tool_execution.success:
            recommendations.append(f"Tool execution failed: {result.tool_execution.error}")
            
        # Planning recommendations
        if result.task_plan:
            if result.task_plan.total_cost and result.task_plan.total_cost > 1000:
                recommendations.append("Consider optimizing resource allocation to reduce costs")
                
        # Cross-component recommendations
        if result.quality_analysis and result.security_analysis:
            if result.quality_analysis.overall_score < 0.7 and result.security_analysis.risk_score > 0.7:
                recommendations.append("Code quality and security issues detected. Consider comprehensive refactoring.")
                
        return list(set(recommendations))  # Remove duplicates
        
    def _update_integration_metrics(self, result: ModelIntegrationResult):
        """Update integration performance metrics"""
        task_type = result.metadata.get("task_type", "unknown")
        
        if task_type not in self.integration_metrics:
            self.integration_metrics[task_type] = {
                "total_analyses": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
                "avg_cost": 0.0,
                "avg_quality_score": 0.0,
                "avg_security_score": 0.0,
                "avg_maintainability_score": 0.0
            }
            
        metrics = self.integration_metrics[task_type]
        metrics["total_analyses"] += 1
        
        # Update success rate
        success = all([
            result.ast_analysis is not None,
            result.security_analysis is not None,
            result.quality_analysis is not None,
            result.code_generation is not None if task_type == "code_generation" else True,
            result.tool_execution is not None if task_type == "tool_execution" else True,
            result.task_plan is not None if task_type == "planning" else True
        ])
        metrics["success_rate"] = 0.9 * metrics["success_rate"] + 0.1 * float(success)
        
        # Update average execution time
        execution_time = sum([
            result.ast_analysis.metrics.get("execution_time", 0),
            result.security_analysis.metrics.get("execution_time", 0),
            result.quality_analysis.metrics.get("execution_time", 0),
            result.code_generation.quality_metrics.complexity if result.code_generation else 0,
            result.tool_execution.execution_time if result.tool_execution else 0,
            sum(step.actual_duration or 0 for step in result.task_plan.steps) if result.task_plan else 0
        ])
        metrics["avg_execution_time"] = 0.9 * metrics["avg_execution_time"] + 0.1 * execution_time
        
        # Update average cost
        cost = sum([
            result.tool_execution.cost if result.tool_execution else 0,
            result.task_plan.total_cost or 0 if result.task_plan else 0
        ])
        metrics["avg_cost"] = 0.9 * metrics["avg_cost"] + 0.1 * cost
        
        # Update quality scores
        if result.quality_analysis:
            metrics["avg_quality_score"] = 0.9 * metrics["avg_quality_score"] + 0.1 * result.quality_analysis.overall_score
            
        if result.security_analysis:
            metrics["avg_security_score"] = 0.9 * metrics["avg_security_score"] + 0.1 * (1 - result.security_analysis.risk_score)
            
        if result.quality_analysis:
            maintainability_metric = next(
                (m for m in result.quality_analysis.metrics if m.name == "maintainability"),
                None
            )
            if maintainability_metric:
                metrics["avg_maintainability_score"] = 0.9 * metrics["avg_maintainability_score"] + 0.1 * maintainability_metric.value
                
    def get_integration_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get integration performance metrics"""
        return self.integration_metrics 