from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass

from ..services.error_analysis_service import ErrorAnalysisService, ErrorAnalysisResult
from ..agent_communication import AgentCommunication
from ..agents.resource_management_agent import ResourceManagementAgent

@dataclass
class ErrorHandlingResult:
    """Represents the result of error handling."""
    success: bool
    steps_completed: List[str]
    errors_encountered: List[str]
    resolution_time: float
    resource_usage: Dict[str, Any]
    timestamp: datetime

class ErrorHandlingAgent:
    """Agent responsible for handling errors in the ADE platform."""
    
    def __init__(self):
        self.error_analysis_service = ErrorAnalysisService()
        self.agent_communication = AgentCommunication()
        self.resource_management_agent = ResourceManagementAgent()
        self.logger = logging.getLogger(__name__)
    
    async def handle_error(self,
                          error_message: str,
                          stack_trace: Optional[List[str]] = None,
                          code_context: Optional[Dict[str, Any]] = None,
                          environment_info: Optional[Dict[str, Any]] = None,
                          domain: Optional[str] = None,
                          agent_context: Optional[Dict[str, Any]] = None) -> ErrorHandlingResult:
        """Handle an error using the error analysis service and ADE platform components."""
        try:
            start_time = datetime.now()
            
            # Analyze error using the error analysis service
            analysis_result = await self.error_analysis_service.analyze_error(
                error_message=error_message,
                stack_trace=stack_trace,
                code_context=code_context,
                environment_info=environment_info,
                domain=domain,
                agent_context=agent_context
            )
            
            # Handle error resolution
            handling_result = await self.error_analysis_service.handle_error(analysis_result)
            
            # Calculate resolution time
            resolution_time = (datetime.now() - start_time).total_seconds()
            
            return ErrorHandlingResult(
                success=handling_result["monitoring_result"]["status"] == "completed",
                steps_completed=handling_result["handling_result"].get("completed_steps", []),
                errors_encountered=handling_result["handling_result"].get("errors", []),
                resolution_time=resolution_time,
                resource_usage=handling_result["resource_allocation"],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in error handling: {str(e)}")
            raise
    
    async def get_recommendations(self,
                                error_analysis: str,
                                root_cause: str,
                                context: Any,
                                agent_context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Get recommendations for error handling."""
        try:
            recommendations = []
            
            # Get recommendations from error analysis service
            analysis_recommendations = await self.error_analysis_service.analyze_error(
                error_message=error_analysis,
                code_context={"root_cause": root_cause},
                agent_context=agent_context
            )
            
            recommendations.extend(analysis_recommendations.solution_steps)
            
            # Get recommendations from other agents
            agent_recommendations = await self.agent_communication.get_agent_recommendations(
                error_analysis=error_analysis,
                context=context,
                agent_context=agent_context
            )
            
            for agent, recs in agent_recommendations.items():
                recommendations.extend(recs)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {str(e)}")
            return []
    
    async def execute_handling_steps(self,
                                   solution_steps: List[str],
                                   recommendations: List[str],
                                   resource_allocation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute error handling steps."""
        try:
            completed_steps = []
            errors = []
            
            # Combine solution steps and recommendations
            all_steps = solution_steps + recommendations
            
            for step in all_steps:
                try:
                    # Execute step with resource allocation
                    await self._execute_step(step, resource_allocation)
                    completed_steps.append(step)
                except Exception as e:
                    errors.append(f"Error executing step '{step}': {str(e)}")
            
            return {
                "completed_steps": completed_steps,
                "errors": errors,
                "total_steps": len(all_steps),
                "success_rate": len(completed_steps) / len(all_steps) if all_steps else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error executing handling steps: {str(e)}")
            raise
    
    async def _execute_step(self, step: str, resource_allocation: Dict[str, Any]) -> None:
        """Execute a single handling step."""
        try:
            # Validate resource availability
            await self.resource_management_agent.validate_resources(resource_allocation)
            
            # Execute step with proper resource allocation
            # This is a placeholder for actual step execution logic
            # In a real implementation, this would contain specific error handling logic
            await self.agent_communication.notify_agents(
                message=f"Executing step: {step}",
                context={"resource_allocation": resource_allocation}
            )
            
        except Exception as e:
            self.logger.error(f"Error executing step '{step}': {str(e)}")
            raise
    
    async def monitor_progress(self,
                             handling_result: Dict[str, Any],
                             metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor error handling progress."""
        try:
            completed_steps = handling_result.get("completed_steps", [])
            total_steps = handling_result.get("total_steps", 0)
            
            # Calculate completion percentage
            completion_percentage = (len(completed_steps) / total_steps * 100) if total_steps > 0 else 0
            
            # Monitor resource usage
            resource_usage = await self.resource_management_agent.monitor_resource_usage(metrics)
            
            return {
                "completion_percentage": completion_percentage,
                "resource_usage": resource_usage,
                "remaining_steps": total_steps - len(completed_steps),
                "errors_count": len(handling_result.get("errors", [])),
                "success_rate": handling_result.get("success_rate", 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error monitoring progress: {str(e)}")
            return {
                "completion_percentage": 0,
                "resource_usage": {},
                "remaining_steps": 0,
                "errors_count": 0,
                "success_rate": 0
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about error handling."""
        return {
            "total_handled": self.error_analysis_service.get_statistics()["total_analyses"],
            "success_rate": self.error_analysis_service.get_statistics()["average_confidence"],
            "patterns_matched": self.error_analysis_service.get_statistics()["patterns_matched"],
            "agent_recommendations": self.error_analysis_service.get_statistics()["agent_recommendations"]
        } 