from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import ast
from pathlib import Path

from .base import (
    BaseAgent,
    AgentCapability,
    AgentContext,
    AgentMetrics
)
from ..llm.base import LLMRequest, LLMResponse, TaskType

logger = logging.getLogger(__name__)

class CodeAnalysisAgent(BaseAgent):
    """Specialized agent for code analysis tasks"""
    
    def __init__(
        self,
        name: str = "code_analysis_agent",
        llm_manager: Optional[Any] = None,
        max_retries: int = 3,
        learning_rate: float = 0.1
    ):
        capabilities = [
            AgentCapability.CODE_ANALYSIS,
            AgentCapability.PATTERN_RECOGNITION,
            AgentCapability.ERROR_HANDLING,
            AgentCapability.LEARNING
        ]
        
        super().__init__(
            name=name,
            capabilities=capabilities,
            llm_manager=llm_manager,
            max_retries=max_retries,
            learning_rate=learning_rate
        )
        
    async def analyze_code(
        self,
        code: str,
        file_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze code and provide insights"""
        try:
            # Prepare analysis task
            task = self._prepare_analysis_task(code, file_path, context)
            
            # Think phase
            plan = await self.think(task)
            
            # Act phase
            results = await self.act(plan)
            
            # Learn from experience
            await self.learn({
                "success": True,
                "latency": results.get("latency", 0),
                "resource_usage": results.get("resource_usage", {}),
                "resource_efficiency": results.get("resource_efficiency", 1.0)
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in code analysis: {str(e)}")
            self.context.error_history.append({
                "error": str(e),
                "timestamp": datetime.now(),
                "file_path": file_path
            })
            raise
            
    def _prepare_analysis_task(
        self,
        code: str,
        file_path: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Prepare task description for code analysis"""
        task_parts = [
            f"Analyze the following code:",
            f"```python\n{code}\n```"
        ]
        
        if file_path:
            task_parts.append(f"File path: {file_path}")
            
        if context:
            task_parts.append("Context:")
            for key, value in context.items():
                task_parts.append(f"- {key}: {value}")
                
        return "\n".join(task_parts)
        
    def _parse_llm_response(self, response: LLMResponse) -> Dict[str, Any]:
        """Parse and validate LLM response for code analysis"""
        try:
            # Parse the response content
            content = response.content.strip()
            
            # Extract analysis sections
            sections = self._extract_sections(content)
            
            # Validate the analysis
            validated_sections = self._validate_sections(sections)
            
            return {
                "sections": validated_sections,
                "metadata": {
                    "model": response.model,
                    "latency": response.latency,
                    "cost": response.cost
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return {}
            
    def _extract_sections(self, content: str) -> Dict[str, Any]:
        """Extract analysis sections from LLM response"""
        sections = {
            "complexity": {},
            "patterns": [],
            "issues": [],
            "suggestions": [],
            "metrics": {}
        }
        
        # TODO: Implement section extraction logic
        # This should parse the LLM response and organize it into sections
        
        return sections
        
    def _validate_sections(self, sections: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean up analysis sections"""
        validated = {}
        
        # Validate complexity metrics
        if "complexity" in sections:
            validated["complexity"] = self._validate_complexity(
                sections["complexity"]
            )
            
        # Validate patterns
        if "patterns" in sections:
            validated["patterns"] = self._validate_patterns(
                sections["patterns"]
            )
            
        # Validate issues
        if "issues" in sections:
            validated["issues"] = self._validate_issues(
                sections["issues"]
            )
            
        # Validate suggestions
        if "suggestions" in sections:
            validated["suggestions"] = self._validate_suggestions(
                sections["suggestions"]
            )
            
        # Validate metrics
        if "metrics" in sections:
            validated["metrics"] = self._validate_metrics(
                sections["metrics"]
            )
            
        return validated
        
    def _validate_complexity(self, complexity: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complexity metrics"""
        validated = {}
        
        # Cyclomatic complexity
        if "cyclomatic" in complexity:
            try:
                validated["cyclomatic"] = int(complexity["cyclomatic"])
            except (ValueError, TypeError):
                validated["cyclomatic"] = 0
                
        # Cognitive complexity
        if "cognitive" in complexity:
            try:
                validated["cognitive"] = int(complexity["cognitive"])
            except (ValueError, TypeError):
                validated["cognitive"] = 0
                
        return validated
        
    def _validate_patterns(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate design patterns"""
        validated = []
        
        for pattern in patterns:
            if not isinstance(pattern, dict):
                continue
                
            if "name" not in pattern or "confidence" not in pattern:
                continue
                
            try:
                confidence = float(pattern["confidence"])
                if 0 <= confidence <= 1:
                    validated.append({
                        "name": str(pattern["name"]),
                        "confidence": confidence,
                        "description": str(pattern.get("description", "")),
                        "location": str(pattern.get("location", ""))
                    })
            except (ValueError, TypeError):
                continue
                
        return validated
        
    def _validate_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate code issues"""
        validated = []
        
        for issue in issues:
            if not isinstance(issue, dict):
                continue
                
            if "type" not in issue or "severity" not in issue:
                continue
                
            try:
                severity = float(issue["severity"])
                if 0 <= severity <= 1:
                    validated.append({
                        "type": str(issue["type"]),
                        "severity": severity,
                        "description": str(issue.get("description", "")),
                        "location": str(issue.get("location", "")),
                        "suggestion": str(issue.get("suggestion", ""))
                    })
            except (ValueError, TypeError):
                continue
                
        return validated
        
    def _validate_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate improvement suggestions"""
        validated = []
        
        for suggestion in suggestions:
            if not isinstance(suggestion, dict):
                continue
                
            if "type" not in suggestion or "priority" not in suggestion:
                continue
                
            try:
                priority = float(suggestion["priority"])
                if 0 <= priority <= 1:
                    validated.append({
                        "type": str(suggestion["type"]),
                        "priority": priority,
                        "description": str(suggestion.get("description", "")),
                        "impact": str(suggestion.get("impact", "")),
                        "implementation": str(suggestion.get("implementation", ""))
                    })
            except (ValueError, TypeError):
                continue
                
        return validated
        
    def _validate_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Validate code metrics"""
        validated = {}
        
        # Lines of code
        if "loc" in metrics:
            try:
                validated["loc"] = int(metrics["loc"])
            except (ValueError, TypeError):
                validated["loc"] = 0
                
        # Number of functions
        if "functions" in metrics:
            try:
                validated["functions"] = int(metrics["functions"])
            except (ValueError, TypeError):
                validated["functions"] = 0
                
        # Number of classes
        if "classes" in metrics:
            try:
                validated["classes"] = int(metrics["classes"])
            except (ValueError, TypeError):
                validated["classes"] = 0
                
        return validated 