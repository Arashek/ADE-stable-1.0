from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
from .context_analyzer import ContextInfo
from .pattern_matcher import MatchResult
from .error_knowledge_base import ErrorPattern, ErrorSolution

@dataclass
class ReasoningResult:
    """Represents the result of LLM reasoning."""
    error_analysis: str
    root_cause: str
    solution_steps: List[str]
    confidence_score: float
    reasoning_chain: List[str]
    related_patterns: List[str]
    timestamp: datetime
    impact_analysis: Optional[Dict[str, Any]] = None
    prevention_strategies: Optional[List[str]] = None
    monitoring_suggestions: Optional[List[str]] = None

class LLMReasoning:
    """Performs intelligent reasoning about errors using LLM capabilities."""
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.temperature = temperature
        self.reasoning_history: List[Dict[str, Any]] = []
        
        # Initialize prompt templates
        self.analysis_prompt = """
        Analyze the following error and provide a comprehensive analysis:
        
        Error Message: {error_message}
        Error Type: {error_type}
        Category: {category}
        Severity: {severity}
        
        Code Context:
        {code_context}
        
        Stack Trace:
        {stack_trace}
        
        Environment Info:
        {environment_info}
        
        Please provide a detailed analysis including:
        1. Error Analysis:
           - Detailed description of the error
           - Key components involved
           - Potential impact on system
        
        2. Root Cause Analysis:
           - Primary cause identification
           - Contributing factors
           - System state at time of error
        
        3. Solution Steps:
           - Immediate actions
           - Long-term fixes
           - Prevention measures
        
        4. Impact Analysis:
           - System components affected
           - Data integrity impact
           - Performance implications
        
        5. Prevention Strategies:
           - Code-level improvements
           - Process improvements
           - Monitoring recommendations
        
        6. Confidence Assessment:
           - Confidence score (0-1)
           - Reasoning chain
           - Uncertainty factors
        """
        
        self.solution_prompt = """
        Based on the following error pattern and context, provide a comprehensive solution:
        
        Pattern: {pattern_description}
        Category: {category}
        Severity: {severity}
        
        Common Causes:
        {common_causes}
        
        Examples:
        {examples}
        
        Code Context:
        {code_context}
        
        Please provide:
        1. Solution Implementation:
           - Step-by-step solution
           - Code examples
           - Testing approach
        
        2. Prerequisites:
           - Required access
           - Dependencies
           - System requirements
        
        3. Success Criteria:
           - Functional requirements
           - Performance metrics
           - Validation steps
        
        4. Risk Assessment:
           - Potential issues
           - Mitigation strategies
           - Rollback plan
        
        5. Monitoring:
           - Key metrics to track
           - Alert thresholds
           - Logging requirements
        
        6. Maintenance:
           - Regular checks
           - Update procedures
           - Documentation needs
        """
        
        self.impact_analysis_prompt = """
        Analyze the potential impact of the following error:
        
        Error Type: {error_type}
        Category: {category}
        Severity: {severity}
        
        System Context:
        {system_context}
        
        Please provide:
        1. System Impact:
           - Affected components
           - Service degradation
           - Data integrity
        
        2. Business Impact:
           - User experience
           - Operational impact
           - Financial implications
        
        3. Recovery Requirements:
           - Time to recover
           - Resource needs
           - Dependencies
        
        4. Long-term Effects:
           - System stability
           - Performance impact
           - Maintenance needs
        """
        
        self.prevention_prompt = """
        Develop prevention strategies for the following error pattern:
        
        Pattern: {pattern_description}
        Category: {category}
        Severity: {severity}
        
        Common Causes:
        {common_causes}
        
        Please provide:
        1. Code-level Prevention:
           - Best practices
           - Design patterns
           - Validation rules
        
        2. Process Improvements:
           - Development practices
           - Testing strategies
           - Deployment procedures
        
        3. Monitoring Setup:
           - Key metrics
           - Alert rules
           - Logging requirements
        
        4. Documentation:
           - Guidelines
           - Examples
           - Troubleshooting steps
        """
    
    def analyze_error(self, context: ContextInfo, matches: List[MatchResult]) -> ReasoningResult:
        """Analyze error using LLM reasoning."""
        try:
            # Prepare context for analysis
            analysis_context = {
                "error_message": context.error_message,
                "error_type": context.error_type,
                "category": context.category,
                "severity": context.severity,
                "code_context": self._format_code_context(context.code_context),
                "stack_trace": self._format_stack_trace(context.stack_trace),
                "environment_info": self._format_environment_info(context.environment_info)
            }
            
            # Generate analysis using LLM
            analysis = self._generate_analysis(analysis_context)
            
            # Generate impact analysis
            impact_analysis = self._generate_impact_analysis(analysis_context)
            
            # Generate prevention strategies
            prevention_strategies = self._generate_prevention_strategies(analysis_context)
            
            # Extract key components from analysis
            error_analysis = analysis.get("error_analysis", "")
            root_cause = analysis.get("root_cause", "")
            solution_steps = analysis.get("solution_steps", [])
            confidence_score = analysis.get("confidence_score", 0.0)
            reasoning_chain = analysis.get("reasoning_chain", [])
            
            # Get related patterns from matches
            related_patterns = [m.pattern_id for m in matches]
            
            # Create reasoning result
            result = ReasoningResult(
                error_analysis=error_analysis,
                root_cause=root_cause,
                solution_steps=solution_steps,
                confidence_score=confidence_score,
                reasoning_chain=reasoning_chain,
                related_patterns=related_patterns,
                timestamp=datetime.now(),
                impact_analysis=impact_analysis,
                prevention_strategies=prevention_strategies,
                monitoring_suggestions=analysis.get("monitoring_suggestions", [])
            )
            
            # Store in history
            self.reasoning_history.append({
                "timestamp": result.timestamp,
                "context": context,
                "matches": matches,
                "result": result
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in LLM reasoning: {str(e)}")
            return ReasoningResult(
                error_analysis="Error analysis failed",
                root_cause="Unknown",
                solution_steps=["Check system logs for more details"],
                confidence_score=0.0,
                reasoning_chain=["Error occurred during analysis"],
                related_patterns=[],
                timestamp=datetime.now()
            )
    
    def generate_solution(self, pattern: ErrorPattern, context: ContextInfo) -> Dict[str, Any]:
        """Generate detailed solution using LLM reasoning."""
        try:
            # Prepare context for solution generation
            solution_context = {
                "pattern_description": pattern.description,
                "category": pattern.category,
                "severity": pattern.severity,
                "common_causes": "\n".join(pattern.common_causes),
                "examples": "\n".join(pattern.examples),
                "code_context": self._format_code_context(context.code_context)
            }
            
            # Generate solution using LLM
            solution = self._generate_solution(solution_context)
            
            # Create solution object
            solution_obj = ErrorSolution(
                solution_id=f"sol_{datetime.now().timestamp()}",
                pattern_type=pattern.pattern_type,
                description=solution.get("description", ""),
                steps=solution.get("steps", []),
                prerequisites=solution.get("prerequisites", []),
                success_criteria=solution.get("success_criteria", []),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            return {
                "solution": solution_obj,
                "confidence_score": solution.get("confidence_score", 0.0),
                "reasoning_chain": solution.get("reasoning_chain", []),
                "risk_assessment": solution.get("risk_assessment", {}),
                "monitoring_plan": solution.get("monitoring_plan", {}),
                "maintenance_requirements": solution.get("maintenance_requirements", [])
            }
            
        except Exception as e:
            self.logger.error(f"Error generating solution: {str(e)}")
            return {
                "solution": None,
                "confidence_score": 0.0,
                "reasoning_chain": ["Error occurred during solution generation"]
            }
    
    def _format_code_context(self, context: Optional[Dict[str, Any]]) -> str:
        """Format code context for LLM input."""
        if not context:
            return "No code context available"
        
        formatted = []
        if "surrounding_lines" in context:
            formatted.append("Surrounding Code:")
            formatted.extend(context["surrounding_lines"])
        
        if "variables" in context:
            formatted.append("\nVariables:")
            formatted.extend(context["variables"])
        
        if "function_calls" in context:
            formatted.append("\nFunction Calls:")
            formatted.extend(context["function_calls"])
        
        if "imports" in context:
            formatted.append("\nImports:")
            formatted.extend(context["imports"])
        
        return "\n".join(formatted)
    
    def _format_stack_trace(self, stack_trace: Optional[List[str]]) -> str:
        """Format stack trace for LLM input."""
        if not stack_trace:
            return "No stack trace available"
        return "\n".join(stack_trace)
    
    def _format_environment_info(self, env_info: Optional[Dict[str, Any]]) -> str:
        """Format environment info for LLM input."""
        if not env_info:
            return "No environment info available"
        
        formatted = []
        for key, value in env_info.items():
            if isinstance(value, dict):
                formatted.append(f"{key}:")
                for k, v in value.items():
                    formatted.append(f"  {k}: {v}")
            else:
                formatted.append(f"{key}: {value}")
        
        return "\n".join(formatted)
    
    def _generate_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis using LLM."""
        # TODO: Implement actual LLM call
        # This is a placeholder implementation
        return {
            "error_analysis": "Detailed analysis of the error",
            "root_cause": "Identified root cause",
            "solution_steps": ["Step 1", "Step 2", "Step 3"],
            "confidence_score": 0.8,
            "reasoning_chain": ["Observation 1", "Observation 2", "Conclusion"],
            "monitoring_suggestions": ["Monitor metric 1", "Monitor metric 2"]
        }
    
    def _generate_impact_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate impact analysis using LLM."""
        # TODO: Implement actual LLM call
        # This is a placeholder implementation
        return {
            "system_impact": {
                "components": ["Component 1", "Component 2"],
                "degradation": "Service degradation description",
                "data_integrity": "Data integrity impact"
            },
            "business_impact": {
                "user_experience": "Impact on users",
                "operations": "Operational impact",
                "financial": "Financial implications"
            },
            "recovery": {
                "time": "Estimated recovery time",
                "resources": ["Resource 1", "Resource 2"],
                "dependencies": ["Dependency 1", "Dependency 2"]
            }
        }
    
    def _generate_prevention_strategies(self, context: Dict[str, Any]) -> List[str]:
        """Generate prevention strategies using LLM."""
        # TODO: Implement actual LLM call
        # This is a placeholder implementation
        return [
            "Strategy 1",
            "Strategy 2",
            "Strategy 3"
        ]
    
    def _generate_solution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate solution using LLM."""
        # TODO: Implement actual LLM call
        # This is a placeholder implementation
        return {
            "description": "Detailed solution description",
            "steps": ["Step 1", "Step 2", "Step 3"],
            "prerequisites": ["Prereq 1", "Prereq 2"],
            "success_criteria": ["Criterion 1", "Criterion 2"],
            "confidence_score": 0.8,
            "reasoning_chain": ["Observation 1", "Observation 2", "Solution"],
            "risk_assessment": {
                "risks": ["Risk 1", "Risk 2"],
                "mitigation": ["Mitigation 1", "Mitigation 2"],
                "rollback": "Rollback procedure"
            },
            "monitoring_plan": {
                "metrics": ["Metric 1", "Metric 2"],
                "alerts": ["Alert 1", "Alert 2"],
                "logging": ["Log 1", "Log 2"]
            },
            "maintenance_requirements": [
                "Requirement 1",
                "Requirement 2"
            ]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about LLM reasoning."""
        return {
            "total_analyses": len(self.reasoning_history),
            "average_confidence": sum(r["result"].confidence_score for r in self.reasoning_history) / len(self.reasoning_history) if self.reasoning_history else 0.0,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "categories_analyzed": len(set(r["context"].category for r in self.reasoning_history)),
            "patterns_matched": len(set(p for r in self.reasoning_history for p in r["result"].related_patterns))
        } 