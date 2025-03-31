from typing import Dict, List, Optional, Any, Tuple, Set
from pydantic import BaseModel
import ast
import re
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
import radon
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze
import pycodestyle
import coverage
import time

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of code metrics"""
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"
    TESTABILITY = "testability"
    DOCUMENTATION = "documentation"
    STYLE = "style"
    COVERAGE = "coverage"
    PERFORMANCE = "performance"
    SECURITY = "security"
    RELIABILITY = "reliability"
    SIZE = "size"

class MetricResult(BaseModel):
    """Result of a metric calculation"""
    metric_type: MetricType
    value: float
    details: Dict[str, Any]
    thresholds: Dict[str, float]
    status: str
    recommendations: List[str]
    metadata: Dict[str, Any] = {}

class CodeMetricsResult(BaseModel):
    """Result of code metrics analysis"""
    file_path: str
    metrics: Dict[MetricType, MetricResult]
    summary: Dict[str, Any]
    metadata: Dict[str, Any] = {}

class CodeMetricsManager:
    """Manager for code metrics operations"""
    
    def __init__(self):
        self.metrics_history: List[CodeMetricsResult] = []
        self.metric_calculators: Dict[MetricType, callable] = {}
        self._initialize_calculators()
        
    def _initialize_calculators(self):
        """Initialize metric calculators"""
        # Complexity metrics
        self.metric_calculators[MetricType.COMPLEXITY] = self._calculate_complexity_metrics
        
        # Maintainability metrics
        self.metric_calculators[MetricType.MAINTAINABILITY] = self._calculate_maintainability_metrics
        
        # Testability metrics
        self.metric_calculators[MetricType.TESTABILITY] = self._calculate_testability_metrics
        
        # Documentation metrics
        self.metric_calculators[MetricType.DOCUMENTATION] = self._calculate_documentation_metrics
        
        # Style metrics
        self.metric_calculators[MetricType.STYLE] = self._calculate_style_metrics
        
        # Coverage metrics
        self.metric_calculators[MetricType.COVERAGE] = self._calculate_coverage_metrics
        
        # Performance metrics
        self.metric_calculators[MetricType.PERFORMANCE] = self._calculate_performance_metrics
        
        # Security metrics
        self.metric_calculators[MetricType.SECURITY] = self._calculate_security_metrics
        
        # Reliability metrics
        self.metric_calculators[MetricType.RELIABILITY] = self._calculate_reliability_metrics
        
        # Size metrics
        self.metric_calculators[MetricType.SIZE] = self._calculate_size_metrics
        
    async def analyze_code(
        self,
        code: str,
        file_path: str,
        metric_types: Optional[List[MetricType]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> CodeMetricsResult:
        """Analyze code metrics based on specified types"""
        try:
            # Initialize result
            result = CodeMetricsResult(
                file_path=file_path,
                metrics={},
                summary={},
                metadata={
                    "analyzed_at": datetime.now().isoformat(),
                    "context": context or {}
                }
            )
            
            # Analyze metrics
            if metric_types is None:
                metric_types = list(MetricType)
                
            for metric_type in metric_types:
                if metric_type in self.metric_calculators:
                    try:
                        metric_result = await self.metric_calculators[metric_type](
                            code,
                            file_path,
                            context
                        )
                        result.metrics[metric_type] = metric_result
                    except Exception as e:
                        logger.error(f"Failed to calculate {metric_type} metrics: {str(e)}")
                        
            # Generate summary
            result.summary = self._generate_summary(result)
            
            # Store in history
            self.metrics_history.append(result)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to analyze code metrics: {str(e)}")
            
    async def _calculate_complexity_metrics(
        self,
        code: str,
        file_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MetricResult:
        """Calculate complexity metrics"""
        try:
            tree = ast.parse(code)
            
            # Calculate cyclomatic complexity
            complexity_results = cc_visit(code)
            avg_complexity = sum(item.complexity for item in complexity_results) / len(complexity_results) if complexity_results else 0
            
            # Calculate cognitive complexity
            cognitive_complexity = self._calculate_cognitive_complexity(tree)
            
            # Calculate essential complexity
            essential_complexity = self._calculate_essential_complexity(tree)
            
            return MetricResult(
                metric_type=MetricType.COMPLEXITY,
                value=avg_complexity,
                details={
                    "cyclomatic_complexity": avg_complexity,
                    "cognitive_complexity": cognitive_complexity,
                    "essential_complexity": essential_complexity,
                    "complex_functions": [
                        item.name for item in complexity_results
                        if item.complexity > 10
                    ]
                },
                thresholds={
                    "warning": 10,
                    "critical": 20
                },
                status="warning" if avg_complexity > 10 else "good",
                recommendations=[
                    "Break down complex functions into smaller ones",
                    "Use early returns to reduce nesting",
                    "Extract complex logic into separate functions"
                ]
            )
        except Exception as e:
            logger.error(f"Failed to calculate complexity metrics: {str(e)}")
            return MetricResult(
                metric_type=MetricType.COMPLEXITY,
                value=0,
                details={},
                thresholds={},
                status="error",
                recommendations=["Fix syntax errors before calculating complexity"]
            )
            
    async def _calculate_maintainability_metrics(
        self,
        code: str,
        file_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MetricResult:
        """Calculate maintainability metrics"""
        try:
            # Calculate maintainability index
            maintainability_index = mi_visit(code, multi=True)
            
            # Calculate code duplication
            duplication = self._calculate_code_duplication(code)
            
            # Calculate dependency complexity
            dependency_complexity = self._calculate_dependency_complexity(code)
            
            return MetricResult(
                metric_type=MetricType.MAINTAINABILITY,
                value=maintainability_index,
                details={
                    "maintainability_index": maintainability_index,
                    "code_duplication": duplication,
                    "dependency_complexity": dependency_complexity
                },
                thresholds={
                    "warning": 65,
                    "critical": 45
                },
                status="warning" if maintainability_index < 65 else "good",
                recommendations=[
                    "Reduce code duplication",
                    "Simplify dependencies",
                    "Improve code organization"
                ]
            )
        except Exception as e:
            logger.error(f"Failed to calculate maintainability metrics: {str(e)}")
            return MetricResult(
                metric_type=MetricType.MAINTAINABILITY,
                value=0,
                details={},
                thresholds={},
                status="error",
                recommendations=["Fix syntax errors before calculating maintainability"]
            )
            
    async def _calculate_testability_metrics(
        self,
        code: str,
        file_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MetricResult:
        """Calculate testability metrics"""
        try:
            tree = ast.parse(code)
            
            # Calculate testability score
            testability_score = self._calculate_testability_score(tree)
            
            # Calculate coupling
            coupling = self._calculate_coupling(tree)
            
            # Calculate cohesion
            cohesion = self._calculate_cohesion(tree)
            
            return MetricResult(
                metric_type=MetricType.TESTABILITY,
                value=testability_score,
                details={
                    "testability_score": testability_score,
                    "coupling": coupling,
                    "cohesion": cohesion
                },
                thresholds={
                    "warning": 0.7,
                    "critical": 0.5
                },
                status="warning" if testability_score < 0.7 else "good",
                recommendations=[
                    "Reduce dependencies between components",
                    "Increase code cohesion",
                    "Add more unit tests"
                ]
            )
        except Exception as e:
            logger.error(f"Failed to calculate testability metrics: {str(e)}")
            return MetricResult(
                metric_type=MetricType.TESTABILITY,
                value=0,
                details={},
                thresholds={},
                status="error",
                recommendations=["Fix syntax errors before calculating testability"]
            )
            
    async def _calculate_documentation_metrics(
        self,
        code: str,
        file_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MetricResult:
        """Calculate documentation metrics"""
        try:
            tree = ast.parse(code)
            
            # Calculate documentation coverage
            doc_coverage = self._calculate_doc_coverage(tree)
            
            # Calculate comment density
            comment_density = self._calculate_comment_density(code)
            
            # Calculate docstring quality
            docstring_quality = self._calculate_docstring_quality(tree)
            
            return MetricResult(
                metric_type=MetricType.DOCUMENTATION,
                value=doc_coverage,
                details={
                    "documentation_coverage": doc_coverage,
                    "comment_density": comment_density,
                    "docstring_quality": docstring_quality
                },
                thresholds={
                    "warning": 0.7,
                    "critical": 0.5
                },
                status="warning" if doc_coverage < 0.7 else "good",
                recommendations=[
                    "Add missing docstrings",
                    "Improve comment quality",
                    "Document complex logic"
                ]
            )
        except Exception as e:
            logger.error(f"Failed to calculate documentation metrics: {str(e)}")
            return MetricResult(
                metric_type=MetricType.DOCUMENTATION,
                value=0,
                details={},
                thresholds={},
                status="error",
                recommendations=["Fix syntax errors before calculating documentation"]
            )
            
    async def _calculate_style_metrics(
        self,
        code: str,
        file_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MetricResult:
        """Calculate style metrics"""
        try:
            # Check PEP8 compliance
            style_guide = pycodestyle.StyleGuide()
            result = style_guide.check_files([file_path])
            
            # Calculate style score
            style_score = 1 - (result.total_errors / (result.total_errors + 1))
            
            # Calculate naming conventions
            naming_score = self._calculate_naming_score(code)
            
            # Calculate formatting consistency
            formatting_score = self._calculate_formatting_score(code)
            
            return MetricResult(
                metric_type=MetricType.STYLE,
                value=style_score,
                details={
                    "pep8_errors": result.total_errors,
                    "naming_score": naming_score,
                    "formatting_score": formatting_score
                },
                thresholds={
                    "warning": 0.8,
                    "critical": 0.6
                },
                status="warning" if style_score < 0.8 else "good",
                recommendations=[
                    "Fix PEP8 violations",
                    "Follow naming conventions",
                    "Maintain consistent formatting"
                ]
            )
        except Exception as e:
            logger.error(f"Failed to calculate style metrics: {str(e)}")
            return MetricResult(
                metric_type=MetricType.STYLE,
                value=0,
                details={},
                thresholds={},
                status="error",
                recommendations=["Fix syntax errors before calculating style"]
            )
            
    async def _calculate_coverage_metrics(
        self,
        code: str,
        file_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MetricResult:
        """Calculate coverage metrics"""
        try:
            # Initialize coverage
            cov = coverage.Coverage()
            
            # Start coverage measurement
            cov.start()
            
            # Execute code (if possible)
            try:
                exec(code)
            except Exception:
                pass
                
            # Stop coverage measurement
            cov.stop()
            
            # Save coverage data
            cov.save()
            
            # Get coverage report
            report = cov.report()
            
            return MetricResult(
                metric_type=MetricType.COVERAGE,
                value=report,
                details={
                    "line_coverage": report,
                    "branch_coverage": cov.report(branch=True),
                    "missing_lines": cov.analysis()[2]
                },
                thresholds={
                    "warning": 0.8,
                    "critical": 0.6
                },
                status="warning" if report < 0.8 else "good",
                recommendations=[
                    "Add more test cases",
                    "Cover edge cases",
                    "Test error conditions"
                ]
            )
        except Exception as e:
            logger.error(f"Failed to calculate coverage metrics: {str(e)}")
            return MetricResult(
                metric_type=MetricType.COVERAGE,
                value=0,
                details={},
                thresholds={},
                status="error",
                recommendations=["Fix syntax errors before calculating coverage"]
            )
            
    async def _calculate_performance_metrics(
        self,
        code: str,
        file_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MetricResult:
        """Calculate performance metrics"""
        try:
            # Measure execution time
            start_time = time.time()
            try:
                exec(code)
            except Exception:
                pass
            execution_time = time.time() - start_time
            
            # Calculate memory usage
            memory_usage = self._calculate_memory_usage(code)
            
            # Calculate CPU usage
            cpu_usage = self._calculate_cpu_usage(code)
            
            return MetricResult(
                metric_type=MetricType.PERFORMANCE,
                value=execution_time,
                details={
                    "execution_time": execution_time,
                    "memory_usage": memory_usage,
                    "cpu_usage": cpu_usage
                },
                thresholds={
                    "warning": 1.0,  # seconds
                    "critical": 5.0
                },
                status="warning" if execution_time > 1.0 else "good",
                recommendations=[
                    "Optimize algorithm complexity",
                    "Reduce memory allocations",
                    "Use caching where appropriate"
                ]
            )
        except Exception as e:
            logger.error(f"Failed to calculate performance metrics: {str(e)}")
            return MetricResult(
                metric_type=MetricType.PERFORMANCE,
                value=0,
                details={},
                thresholds={},
                status="error",
                recommendations=["Fix syntax errors before calculating performance"]
            )
            
    async def _calculate_security_metrics(
        self,
        code: str,
        file_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MetricResult:
        """Calculate security metrics"""
        try:
            # Calculate security score
            security_score = self._calculate_security_score(code)
            
            # Check for vulnerabilities
            vulnerabilities = self._find_vulnerabilities(code)
            
            # Calculate input validation
            input_validation = self._calculate_input_validation(code)
            
            return MetricResult(
                metric_type=MetricType.SECURITY,
                value=security_score,
                details={
                    "security_score": security_score,
                    "vulnerabilities": vulnerabilities,
                    "input_validation": input_validation
                },
                thresholds={
                    "warning": 0.7,
                    "critical": 0.5
                },
                status="warning" if security_score < 0.7 else "good",
                recommendations=[
                    "Fix security vulnerabilities",
                    "Improve input validation",
                    "Use secure coding practices"
                ]
            )
        except Exception as e:
            logger.error(f"Failed to calculate security metrics: {str(e)}")
            return MetricResult(
                metric_type=MetricType.SECURITY,
                value=0,
                details={},
                thresholds={},
                status="error",
                recommendations=["Fix syntax errors before calculating security"]
            )
            
    async def _calculate_reliability_metrics(
        self,
        code: str,
        file_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MetricResult:
        """Calculate reliability metrics"""
        try:
            # Calculate error handling
            error_handling = self._calculate_error_handling(code)
            
            # Calculate logging
            logging_score = self._calculate_logging_score(code)
            
            # Calculate exception handling
            exception_handling = self._calculate_exception_handling(code)
            
            return MetricResult(
                metric_type=MetricType.RELIABILITY,
                value=error_handling,
                details={
                    "error_handling": error_handling,
                    "logging_score": logging_score,
                    "exception_handling": exception_handling
                },
                thresholds={
                    "warning": 0.7,
                    "critical": 0.5
                },
                status="warning" if error_handling < 0.7 else "good",
                recommendations=[
                    "Improve error handling",
                    "Add more logging",
                    "Handle exceptions properly"
                ]
            )
        except Exception as e:
            logger.error(f"Failed to calculate reliability metrics: {str(e)}")
            return MetricResult(
                metric_type=MetricType.RELIABILITY,
                value=0,
                details={},
                thresholds={},
                status="error",
                recommendations=["Fix syntax errors before calculating reliability"]
            )
            
    async def _calculate_size_metrics(
        self,
        code: str,
        file_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MetricResult:
        """Calculate size metrics"""
        try:
            # Calculate raw metrics
            raw = analyze(code)
            
            # Calculate size metrics
            size_metrics = {
                "loc": raw.loc,
                "lloc": raw.lloc,
                "sloc": raw.sloc,
                "comments": raw.comments,
                "multi": raw.multi,
                "blank": raw.blank,
                "single_comments": raw.single_comments
            }
            
            return MetricResult(
                metric_type=MetricType.SIZE,
                value=raw.loc,
                details=size_metrics,
                thresholds={
                    "warning": 1000,
                    "critical": 2000
                },
                status="warning" if raw.loc > 1000 else "good",
                recommendations=[
                    "Split large files into smaller ones",
                    "Extract common functionality",
                    "Use modular design"
                ]
            )
        except Exception as e:
            logger.error(f"Failed to calculate size metrics: {str(e)}")
            return MetricResult(
                metric_type=MetricType.SIZE,
                value=0,
                details={},
                thresholds={},
                status="error",
                recommendations=["Fix syntax errors before calculating size"]
            )
            
    def _generate_summary(self, result: CodeMetricsResult) -> Dict[str, Any]:
        """Generate metrics summary"""
        summary = {
            "total_metrics": len(result.metrics),
            "metrics_by_status": {},
            "average_scores": {},
            "recommendations": []
        }
        
        # Count metrics by status
        for metric in result.metrics.values():
            if metric.status not in summary["metrics_by_status"]:
                summary["metrics_by_status"][metric.status] = 0
            summary["metrics_by_status"][metric.status] += 1
            
        # Calculate average scores
        for metric_type in MetricType:
            if metric_type in result.metrics:
                summary["average_scores"][metric_type] = result.metrics[metric_type].value
                
        # Collect recommendations
        for metric in result.metrics.values():
            summary["recommendations"].extend(metric.recommendations)
            
        return summary
        
    def get_metrics_history(self) -> List[CodeMetricsResult]:
        """Get metrics history"""
        return self.metrics_history
        
    def get_metric_calculators(self) -> Dict[MetricType, callable]:
        """Get metric calculators"""
        return self.metric_calculators
        
    def add_metric_calculator(
        self,
        metric_type: MetricType,
        calculator: callable
    ):
        """Add a new metric calculator"""
        self.metric_calculators[metric_type] = calculator 