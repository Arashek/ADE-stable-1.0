from typing import Dict, List, Optional, Any, Tuple, Set
from pydantic import BaseModel
import ast
import re
from dataclasses import dataclass
from enum import Enum
import radon.complexity as radon_complexity
import radon.metrics as radon_metrics
from radon.visitors import ComplexityVisitor
import mccabe
import pycodestyle
import pylint.lint
import black
import isort
import logging
from core.models.context_aware_fix import ContextAwareFixSystem
from core.models.safe_code_modifier import SafeCodeModifier
from core.models.code_suggestions import CodeSuggestion, SuggestionType, SuggestionPriority

logger = logging.getLogger(__name__)

class CodeQualityMetric(BaseModel):
    """Code quality metric with value and threshold"""
    name: str
    value: float
    threshold: float
    unit: str
    description: str
    impact: str

class CodeQualityResult(BaseModel):
    """Result of code quality analysis"""
    metrics: List[CodeQualityMetric]
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    overall_score: float
    metadata: Dict[str, Any] = {}

class CodeQualityAnalyzer:
    """Specialized analyzer for code quality metrics"""
    
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.suggestions: Dict[str, List[CodeSuggestion]] = {}
        
        # Initialize new components
        self.context_aware_fix = ContextAwareFixSystem(project_dir)
        self.safe_code_modifier = SafeCodeModifier(project_dir)
        
        self.quality_thresholds: Dict[str, float] = {
            "complexity": 10.0,
            "maintainability": 0.7,
            "testability": 0.7,
            "readability": 0.7,
            "reliability": 0.7,
            "security": 0.7,
            "performance": 0.7,
            "documentation": 0.7
        }
        self.analysis_history: List[CodeQualityResult] = []
        
    async def analyze_code(self, file_path: str, content: str) -> List[CodeSuggestion]:
        """Analyze code quality and generate suggestions using context-aware system"""
        try:
            # Get code context
            context = await self.context_aware_fix.get_code_context(file_path)
            if not context:
                return []
                
            # Calculate metrics
            metrics = self._calculate_metrics(content)
            self.metrics[file_path] = metrics
            
            # Generate suggestions based on metrics and context
            suggestions = []
            
            # Generate suggestions for each metric
            for metric_name, metric_value in metrics.items():
                metric_suggestions = await self._generate_metric_suggestions(
                    metric_name,
                    metric_value,
                    context
                )
                suggestions.extend(metric_suggestions)
                
            # Generate context-aware suggestions
            context_suggestions = await self._generate_context_suggestions(context)
            suggestions.extend(context_suggestions)
            
            # Filter and prioritize suggestions
            filtered_suggestions = self._filter_suggestions(suggestions)
            prioritized_suggestions = self._prioritize_suggestions(filtered_suggestions)
            
            # Store suggestions
            self.suggestions[file_path] = prioritized_suggestions
            
            return prioritized_suggestions
            
        except Exception as e:
            logger.error(f"Failed to analyze code quality: {e}")
            return []
            
    async def _generate_context_suggestions(self, context: Any) -> List[CodeSuggestion]:
        """Generate suggestions using context-aware system"""
        suggestions = []
        
        try:
            # Analyze code context for improvements
            analysis_result = await self.context_aware_fix.analyze_code_context(context)
            
            for improvement in analysis_result:
                # Convert improvement to suggestion
                suggestion = CodeSuggestion(
                    type=self._map_improvement_to_suggestion_type(improvement.category),
                    priority=self._determine_priority_from_improvement(improvement),
                    file_path=context.file_path,
                    line_number=improvement.line_numbers[0] if improvement.line_numbers else None,
                    description=improvement.description,
                    suggestion=improvement.fix_code,
                    impact=improvement.impact,
                    effort=improvement.effort,
                    confidence=improvement.confidence,
                    context={
                        "improvement_metadata": improvement.metadata,
                        "context_analysis": improvement.context_analysis
                    }
                )
                suggestions.append(suggestion)
                
        except Exception as e:
            logger.error(f"Failed to generate context suggestions: {e}")
            
        return suggestions
        
    def _map_improvement_to_suggestion_type(self, category: str) -> SuggestionType:
        """Map improvement category to suggestion type"""
        mapping = {
            "complexity": SuggestionType.MAINTAINABILITY,
            "duplication": SuggestionType.CODE_QUALITY,
            "documentation": SuggestionType.DOCUMENTATION,
            "testing": SuggestionType.TESTING,
            "security": SuggestionType.SECURITY,
            "performance": SuggestionType.PERFORMANCE
        }
        return mapping.get(category, SuggestionType.CODE_QUALITY)
        
    def _determine_priority_from_improvement(self, improvement: Any) -> SuggestionPriority:
        """Determine suggestion priority from improvement data"""
        # Calculate weighted score
        weighted_score = (
            improvement.impact * 0.4 +
            improvement.confidence * 0.3 +
            (1 - improvement.effort) * 0.3
        )
        
        # Map score to priority
        if weighted_score >= 0.8:
            return SuggestionPriority.CRITICAL
        elif weighted_score >= 0.6:
            return SuggestionPriority.HIGH
        elif weighted_score >= 0.4:
            return SuggestionPriority.MEDIUM
        else:
            return SuggestionPriority.LOW
        
    def _calculate_metrics(self, code: str) -> Dict[str, float]:
        """Calculate code quality metrics"""
        metrics = {}
        
        # Complexity metrics
        complexity = self._calculate_complexity(code)
        metrics["complexity"] = complexity
        
        # Maintainability metrics
        maintainability = self._calculate_maintainability(code)
        metrics["maintainability"] = maintainability
        
        # Testability metrics
        testability = self._calculate_testability(code)
        metrics["testability"] = testability
        
        # Readability metrics
        readability = self._calculate_readability(code)
        metrics["readability"] = readability
        
        # Reliability metrics
        reliability = self._calculate_reliability(code)
        metrics["reliability"] = reliability
        
        # Security metrics
        security = self._calculate_security(code)
        metrics["security"] = security
        
        # Performance metrics
        performance = self._calculate_performance(code)
        metrics["performance"] = performance
        
        # Documentation metrics
        documentation = self._calculate_documentation(code)
        metrics["documentation"] = documentation
        
        return metrics
        
    def _calculate_complexity(self, code: str) -> float:
        """Calculate cyclomatic complexity"""
        try:
            complexity = radon_complexity.cc_visit(code)
            return sum(item.complexity for item in complexity)
        except Exception as e:
            logger.error(f"Failed to calculate complexity: {str(e)}")
            return 0.0
            
    def _calculate_maintainability(self, code: str) -> float:
        """Calculate maintainability index"""
        try:
            mi = radon_metrics.mi_visit(code, multi=True)
            return mi / 100.0  # Normalize to 0-1 range
        except Exception as e:
            logger.error(f"Failed to calculate maintainability: {str(e)}")
            return 0.0
            
    def _calculate_testability(self, code: str) -> float:
        """Calculate testability score"""
        try:
            # Count testable components
            testable_components = 0
            total_components = 0
            
            class TestabilityVisitor(ast.NodeVisitor):
                def visit_FunctionDef(self, node):
                    nonlocal testable_components, total_components
                    total_components += 1
                    if len(node.args.args) <= 5 and len(node.body) <= 20:
                        testable_components += 1
                        
            visitor = TestabilityVisitor()
            visitor.visit(ast.parse(code))
            
            return testable_components / total_components if total_components > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate testability: {str(e)}")
            return 0.0
            
    def _calculate_readability(self, code: str) -> float:
        """Calculate readability score"""
        try:
            # Use pycodestyle to check code style
            style_guide = pycodestyle.StyleGuide()
            result = style_guide.check_files([code])
            
            # Calculate score based on style errors
            max_errors = 100  # Arbitrary maximum
            errors = result.total_errors
            return max(0.0, 1.0 - (errors / max_errors))
            
        except Exception as e:
            logger.error(f"Failed to calculate readability: {str(e)}")
            return 0.0
            
    def _calculate_reliability(self, code: str) -> float:
        """Calculate reliability score"""
        try:
            # Check for common reliability issues
            issues = 0
            total_checks = 0
            
            class ReliabilityVisitor(ast.NodeVisitor):
                def visit_Try(self, node):
                    nonlocal issues, total_checks
                    total_checks += 1
                    if not node.handlers:
                        issues += 1
                        
                def visit_Assert(self, node):
                    nonlocal total_checks
                    total_checks += 1
                    
            visitor = ReliabilityVisitor()
            visitor.visit(ast.parse(code))
            
            return 1.0 - (issues / total_checks) if total_checks > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate reliability: {str(e)}")
            return 0.0
            
    def _calculate_security(self, code: str) -> float:
        """Calculate security score"""
        try:
            # Check for common security issues
            issues = 0
            total_checks = 0
            
            class SecurityVisitor(ast.NodeVisitor):
                def visit_Call(self, node):
                    nonlocal issues, total_checks
                    total_checks += 1
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec']:
                            issues += 1
                            
            visitor = SecurityVisitor()
            visitor.visit(ast.parse(code))
            
            return 1.0 - (issues / total_checks) if total_checks > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate security: {str(e)}")
            return 0.0
            
    def _calculate_performance(self, code: str) -> float:
        """Calculate performance score"""
        try:
            # Check for common performance issues
            issues = 0
            total_checks = 0
            
            class PerformanceVisitor(ast.NodeVisitor):
                def visit_For(self, node):
                    nonlocal issues, total_checks
                    total_checks += 1
                    if isinstance(node.iter, ast.Call):
                        if isinstance(node.iter.func, ast.Name):
                            if node.iter.func.id == 'range':
                                issues += 1
                                
            visitor = PerformanceVisitor()
            visitor.visit(ast.parse(code))
            
            return 1.0 - (issues / total_checks) if total_checks > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate performance: {str(e)}")
            return 0.0
            
    def _calculate_documentation(self, code: str) -> float:
        """Calculate documentation score"""
        try:
            # Count documented components
            documented_components = 0
            total_components = 0
            
            class DocumentationVisitor(ast.NodeVisitor):
                def visit_FunctionDef(self, node):
                    nonlocal documented_components, total_components
                    total_components += 1
                    if ast.get_docstring(node):
                        documented_components += 1
                        
                def visit_ClassDef(self, node):
                    nonlocal documented_components, total_components
                    total_components += 1
                    if ast.get_docstring(node):
                        documented_components += 1
                        
            visitor = DocumentationVisitor()
            visitor.visit(ast.parse(code))
            
            return documented_components / total_components if total_components > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate documentation: {str(e)}")
            return 0.0
        
    def get_analysis_history(self) -> List[CodeQualityResult]:
        """Get code quality analysis history"""
        return self.analysis_history
        
    def get_quality_thresholds(self) -> Dict[str, float]:
        """Get quality thresholds"""
        return self.quality_thresholds
        
    def set_quality_threshold(self, metric: str, threshold: float):
        """Set quality threshold for a metric"""
        if metric in self.quality_thresholds:
            self.quality_thresholds[metric] = threshold
        else:
            raise ValueError(f"Unknown metric: {metric}") 