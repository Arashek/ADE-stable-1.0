from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass

from ..analysis.context_analyzer import ContextAnalyzer
from ..analysis.pattern_matcher import PatternMatcher
from ..analysis.llm_reasoning import LLMReasoning
from ..analysis.domain_knowledge import DomainKnowledge
from ..analysis.error_knowledge_base import ErrorKnowledgeBase
from ..agent_communication import AgentCommunication
from ..agents.error_handling_agent import ErrorHandlingAgent
from ..agents.resource_management_agent import ResourceManagementAgent

@dataclass
class ErrorAnalysisResult:
    """Represents the result of error analysis with ADE platform integration."""
    error_analysis: str
    root_cause: str
    solution_steps: List[str]
    confidence_score: float
    reasoning_chain: List[str]
    related_patterns: List[str]
    impact_analysis: Optional[Dict[str, Any]]
    prevention_strategies: Optional[List[str]]
    monitoring_suggestions: Optional[List[str]]
    resource_requirements: Optional[Dict[str, Any]]
    agent_recommendations: Optional[Dict[str, List[str]]]
    timestamp: datetime

class ErrorAnalysisService:
    """Service for integrating error analysis with ADE platform components."""
    
    def __init__(self):
        self.context_analyzer = ContextAnalyzer()
        self.pattern_matcher = PatternMatcher()
        self.llm_reasoning = LLMReasoning()
        self.domain_knowledge = DomainKnowledge()
        self.knowledge_base = ErrorKnowledgeBase()
        self.agent_communication = AgentCommunication()
        self.error_handling_agent = ErrorHandlingAgent()
        self.resource_management_agent = ResourceManagementAgent()
        self.logger = logging.getLogger(__name__)
    
    async def analyze_error(self, 
                          error_message: str,
                          stack_trace: Optional[List[str]] = None,
                          code_context: Optional[Dict[str, Any]] = None,
                          environment_info: Optional[Dict[str, Any]] = None,
                          domain: Optional[str] = None,
                          agent_context: Optional[Dict[str, Any]] = None) -> ErrorAnalysisResult:
        """Analyze an error and integrate with ADE platform components."""
        try:
            # Analyze context
            context = self.context_analyzer.analyze(
                error_message=error_message,
                stack_trace=stack_trace,
                code_context=code_context,
                environment_info=environment_info
            )
            
            # Match patterns
            matches = self.pattern_matcher.match(
                error_message=error_message,
                context=context
            )
            
            # Get domain-specific context
            domain_prompt = ""
            if domain:
                domain_prompt = self.domain_knowledge.get_domain_prompt(domain)
            
            # Perform LLM reasoning
            result = self.llm_reasoning.analyze_error(context, matches)
            
            # Get resource requirements
            resource_requirements = await self._get_resource_requirements(
                result, context, environment_info
            )
            
            # Get agent recommendations
            agent_recommendations = await self._get_agent_recommendations(
                result, context, agent_context
            )
            
            return ErrorAnalysisResult(
                error_analysis=result.error_analysis,
                root_cause=result.root_cause,
                solution_steps=result.solution_steps,
                confidence_score=result.confidence_score,
                reasoning_chain=result.reasoning_chain,
                related_patterns=result.related_patterns,
                impact_analysis=result.impact_analysis,
                prevention_strategies=result.prevention_strategies,
                monitoring_suggestions=result.monitoring_suggestions,
                resource_requirements=resource_requirements,
                agent_recommendations=agent_recommendations,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in analysis: {str(e)}")
            raise
    
    async def _get_resource_requirements(self,
                                       result: Any,
                                       context: Any,
                                       environment_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get resource requirements for error resolution."""
        try:
            # Analyze resource needs based on error impact
            resource_analysis = await self.resource_management_agent.analyze_resource_needs(
                error_impact=result.impact_analysis,
                context=context,
                environment_info=environment_info
            )
            
            return {
                "cpu_requirements": resource_analysis.get("cpu_requirements"),
                "memory_requirements": resource_analysis.get("memory_requirements"),
                "storage_requirements": resource_analysis.get("storage_requirements"),
                "network_requirements": resource_analysis.get("network_requirements"),
                "priority_level": resource_analysis.get("priority_level"),
                "estimated_duration": resource_analysis.get("estimated_duration")
            }
            
        except Exception as e:
            self.logger.error(f"Error getting resource requirements: {str(e)}")
            return {}
    
    async def _get_agent_recommendations(self,
                                       result: Any,
                                       context: Any,
                                       agent_context: Optional[Dict[str, Any]] = None) -> Dict[str, List[str]]:
        """Get recommendations from ADE platform agents."""
        try:
            recommendations = {}
            
            # Get error handling agent recommendations
            error_handling_recs = await self.error_handling_agent.get_recommendations(
                error_analysis=result.error_analysis,
                root_cause=result.root_cause,
                context=context,
                agent_context=agent_context
            )
            recommendations["error_handling"] = error_handling_recs
            
            # Get resource management agent recommendations
            resource_recs = await self.resource_management_agent.get_recommendations(
                resource_requirements=result.resource_requirements,
                context=context,
                agent_context=agent_context
            )
            recommendations["resource_management"] = resource_recs
            
            # Get recommendations from other agents through agent communication
            other_agent_recs = await self.agent_communication.get_agent_recommendations(
                error_analysis=result.error_analysis,
                context=context,
                agent_context=agent_context
            )
            recommendations.update(other_agent_recs)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting agent recommendations: {str(e)}")
            return {}
    
    async def handle_error(self, error_analysis_result: ErrorAnalysisResult) -> Dict[str, Any]:
        """Handle error resolution using ADE platform components."""
        try:
            # Allocate resources
            resource_allocation = await self.resource_management_agent.allocate_resources(
                requirements=error_analysis_result.resource_requirements
            )
            
            # Execute error handling steps
            handling_result = await self.error_handling_agent.execute_handling_steps(
                solution_steps=error_analysis_result.solution_steps,
                recommendations=error_analysis_result.agent_recommendations.get("error_handling", []),
                resource_allocation=resource_allocation
            )
            
            # Monitor resolution
            monitoring_result = await self._monitor_resolution(
                error_analysis_result,
                handling_result,
                resource_allocation
            )
            
            return {
                "handling_result": handling_result,
                "monitoring_result": monitoring_result,
                "resource_allocation": resource_allocation
            }
            
        except Exception as e:
            self.logger.error(f"Error handling error: {str(e)}")
            raise
    
    async def _monitor_resolution(self,
                                error_analysis_result: ErrorAnalysisResult,
                                handling_result: Dict[str, Any],
                                resource_allocation: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor error resolution progress."""
        try:
            monitoring_plan = error_analysis_result.monitoring_suggestions or []
            
            # Set up monitoring metrics
            metrics = await self.resource_management_agent.setup_monitoring(
                monitoring_plan=monitoring_plan,
                resource_allocation=resource_allocation
            )
            
            # Monitor resolution progress
            progress = await self.error_handling_agent.monitor_progress(
                handling_result=handling_result,
                metrics=metrics
            )
            
            return {
                "metrics": metrics,
                "progress": progress,
                "status": "completed" if progress.get("completion_percentage", 0) >= 100 else "in_progress"
            }
            
        except Exception as e:
            self.logger.error(f"Error monitoring resolution: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about error analysis and handling."""
        return {
            "total_analyses": self.llm_reasoning.get_statistics()["total_analyses"],
            "average_confidence": self.llm_reasoning.get_statistics()["average_confidence"],
            "patterns_matched": len(self.pattern_matcher.get_statistics()["patterns"]),
            "domains_supported": len(self.domain_knowledge.domains),
            "agent_recommendations": len(self.agent_communication.get_statistics()["recommendations"])
        } 