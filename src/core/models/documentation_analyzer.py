from typing import Dict, List, Optional, Any, Tuple, Set
from pydantic import BaseModel
import logging
from datetime import datetime
from enum import Enum
import ast
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class DocumentationType(Enum):
    """Types of documentation analysis"""
    DOCSTRINGS = "docstrings"
    COMMENTS = "comments"
    COVERAGE = "coverage"
    QUALITY = "quality"
    COMPLETENESS = "completeness"
    ACCESSIBILITY = "accessibility"

class DocumentationMetric(BaseModel):
    """Documentation metric"""
    name: str
    value: float
    threshold: float
    status: str
    details: Dict[str, Any] = {}
    recommendations: List[str] = []

class DocumentationResult(BaseModel):
    """Result of documentation analysis"""
    documentation_type: DocumentationType
    metrics: Dict[str, DocumentationMetric]
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = {}

@dataclass
class DocumentationElement:
    """Information about a documentation element"""
    element_type: str
    content: str
    line_number: int
    column: int
    context: Optional[Dict[str, Any]] = None

class DocumentationAnalyzer:
    """Analyzer for assessing code documentation"""
    
    def __init__(self):
        self.analysis_history: List[DocumentationResult] = []
        self.documentation_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.analysis_metrics: Dict[str, Dict[str, float]] = {}
        self._initialize_patterns()
        self._initialize_documentation_rules()
        
    def _initialize_patterns(self):
        """Initialize documentation detection patterns"""
        # Docstring patterns
        self.documentation_patterns["docstrings"] = [
            {
                "pattern": r'""".*?"""',
                "severity": "info",
                "description": "Docstring detected",
                "recommendation": "Review docstring content"
            },
            {
                "pattern": r"'''.*?'''",
                "severity": "info",
                "description": "Docstring detected",
                "recommendation": "Review docstring content"
            }
        ]
        
        # Comment patterns
        self.documentation_patterns["comments"] = [
            {
                "pattern": r"#.*$",
                "severity": "info",
                "description": "Line comment detected",
                "recommendation": "Review comment content"
            },
            {
                "pattern": r"#\s*TODO:",
                "severity": "warning",
                "description": "TODO comment detected",
                "recommendation": "Address TODO items"
            },
            {
                "pattern": r"#\s*FIXME:",
                "severity": "warning",
                "description": "FIXME comment detected",
                "recommendation": "Address FIXME items"
            }
        ]
        
        # Coverage patterns
        self.documentation_patterns["coverage"] = [
            {
                "pattern": r"def\s+\w+\s*\([^)]*\)\s*:",
                "severity": "info",
                "description": "Function definition detected",
                "recommendation": "Ensure function is documented"
            },
            {
                "pattern": r"class\s+\w+\s*:",
                "severity": "info",
                "description": "Class definition detected",
                "recommendation": "Ensure class is documented"
            }
        ]
        
        # Quality patterns
        self.documentation_patterns["quality"] = [
            {
                "pattern": r"Args:",
                "severity": "info",
                "description": "Args section detected",
                "recommendation": "Review argument documentation"
            },
            {
                "pattern": r"Returns:",
                "severity": "info",
                "description": "Returns section detected",
                "recommendation": "Review return value documentation"
            },
            {
                "pattern": r"Raises:",
                "severity": "info",
                "description": "Raises section detected",
                "recommendation": "Review exception documentation"
            }
        ]
        
        # Completeness patterns
        self.documentation_patterns["completeness"] = [
            {
                "pattern": r"@param",
                "severity": "info",
                "description": "Parameter documentation detected",
                "recommendation": "Review parameter documentation"
            },
            {
                "pattern": r"@return",
                "severity": "info",
                "description": "Return documentation detected",
                "recommendation": "Review return documentation"
            },
            {
                "pattern": r"@type",
                "severity": "info",
                "description": "Type documentation detected",
                "recommendation": "Review type documentation"
            }
        ]
        
        # Accessibility patterns
        self.documentation_patterns["accessibility"] = [
            {
                "pattern": r"@see",
                "severity": "info",
                "description": "Reference documentation detected",
                "recommendation": "Review reference documentation"
            },
            {
                "pattern": r"@example",
                "severity": "info",
                "description": "Example documentation detected",
                "recommendation": "Review example documentation"
            },
            {
                "pattern": r"@note",
                "severity": "info",
                "description": "Note documentation detected",
                "recommendation": "Review note documentation"
            }
        ]
        
    def _initialize_documentation_rules(self):
        """Initialize documentation rules"""
        self.documentation_rules = {
            DocumentationType.DOCSTRINGS: [
                {
                    "name": "docstring_coverage",
                    "threshold": 0.8,
                    "description": "Docstring coverage score"
                },
                {
                    "name": "docstring_quality",
                    "threshold": 0.7,
                    "description": "Docstring quality score"
                },
                {
                    "name": "docstring_completeness",
                    "threshold": 0.8,
                    "description": "Docstring completeness score"
                }
            ],
            DocumentationType.COMMENTS: [
                {
                    "name": "comment_coverage",
                    "threshold": 0.7,
                    "description": "Comment coverage score"
                },
                {
                    "name": "comment_quality",
                    "threshold": 0.7,
                    "description": "Comment quality score"
                },
                {
                    "name": "comment_relevance",
                    "threshold": 0.8,
                    "description": "Comment relevance score"
                }
            ],
            DocumentationType.COVERAGE: [
                {
                    "name": "overall_coverage",
                    "threshold": 0.8,
                    "description": "Overall documentation coverage"
                },
                {
                    "name": "function_coverage",
                    "threshold": 0.8,
                    "description": "Function documentation coverage"
                },
                {
                    "name": "class_coverage",
                    "threshold": 0.8,
                    "description": "Class documentation coverage"
                }
            ],
            DocumentationType.QUALITY: [
                {
                    "name": "documentation_quality",
                    "threshold": 0.7,
                    "description": "Documentation quality score"
                },
                {
                    "name": "clarity_score",
                    "threshold": 0.7,
                    "description": "Documentation clarity score"
                },
                {
                    "name": "consistency_score",
                    "threshold": 0.8,
                    "description": "Documentation consistency score"
                }
            ],
            DocumentationType.COMPLETENESS: [
                {
                    "name": "parameter_completeness",
                    "threshold": 0.8,
                    "description": "Parameter documentation completeness"
                },
                {
                    "name": "return_completeness",
                    "threshold": 0.8,
                    "description": "Return documentation completeness"
                },
                {
                    "name": "type_completeness",
                    "threshold": 0.8,
                    "description": "Type documentation completeness"
                }
            ],
            DocumentationType.ACCESSIBILITY: [
                {
                    "name": "accessibility_score",
                    "threshold": 0.7,
                    "description": "Documentation accessibility score"
                },
                {
                    "name": "example_coverage",
                    "threshold": 0.6,
                    "description": "Example documentation coverage"
                },
                {
                    "name": "reference_coverage",
                    "threshold": 0.6,
                    "description": "Reference documentation coverage"
                }
            ]
        }
        
    def analyze_documentation(
        self,
        code: str,
        file_path: str,
        documentation_type: DocumentationType,
        context: Optional[Dict[str, Any]] = None
    ) -> DocumentationResult:
        """Analyze documentation based on specified type"""
        try:
            # Initialize result
            result = DocumentationResult(
                documentation_type=documentation_type,
                metrics={},
                issues=[],
                recommendations=[],
                metadata={
                    "analyzed_at": datetime.now().isoformat(),
                    "file_path": file_path,
                    "context": context or {}
                }
            )
            
            # Get documentation rules for type
            rules = self.documentation_rules.get(documentation_type, [])
            
            # Parse code
            tree = ast.parse(code)
            
            # Perform analysis
            for rule in rules:
                metric = self._analyze_documentation_metric(
                    rule["name"],
                    code,
                    tree,
                    rule["threshold"],
                    context
                )
                result.metrics[rule["name"]] = metric
                
                # Check for issues
                if metric.status != "good":
                    result.issues.append({
                        "metric": rule["name"],
                        "value": metric.value,
                        "threshold": rule["threshold"],
                        "status": metric.status,
                        "description": rule["description"]
                    })
                    
                # Add recommendations
                result.recommendations.extend(metric.recommendations)
                
            # Generate cross-metric recommendations
            result.recommendations.extend(
                self._generate_cross_metric_recommendations(result.metrics)
            )
            
            # Store in history
            self.analysis_history.append(result)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to analyze documentation: {str(e)}")
            
    def _analyze_documentation_metric(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        threshold: float,
        context: Optional[Dict[str, Any]] = None
    ) -> DocumentationMetric:
        """Analyze specific documentation metric"""
        try:
            # Calculate metric value
            value = self._calculate_metric_value(
                metric_name,
                code,
                tree,
                context
            )
            
            # Determine status
            status = self._determine_metric_status(value, threshold)
            
            # Generate recommendations
            recommendations = self._generate_metric_recommendations(
                metric_name,
                value,
                threshold,
                status
            )
            
            return DocumentationMetric(
                name=metric_name,
                value=value,
                threshold=threshold,
                status=status,
                details={
                    "code": code,
                    "context": context
                },
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze documentation metric {metric_name}: {str(e)}")
            return DocumentationMetric(
                name=metric_name,
                value=0.0,
                threshold=threshold,
                status="error",
                details={"error": str(e)},
                recommendations=["Fix documentation analysis error"]
            )
            
    def _calculate_metric_value(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate metric value"""
        if metric_name == "docstring_coverage":
            return self._calculate_docstring_coverage(code, tree)
        elif metric_name == "docstring_quality":
            return self._calculate_docstring_quality(code, tree)
        elif metric_name == "docstring_completeness":
            return self._calculate_docstring_completeness(code, tree)
        elif metric_name == "comment_coverage":
            return self._calculate_comment_coverage(code, tree)
        elif metric_name == "comment_quality":
            return self._calculate_comment_quality(code, tree)
        elif metric_name == "comment_relevance":
            return self._calculate_comment_relevance(code, tree)
        elif metric_name == "overall_coverage":
            return self._calculate_overall_coverage(code, tree)
        elif metric_name == "function_coverage":
            return self._calculate_function_coverage(code, tree)
        elif metric_name == "class_coverage":
            return self._calculate_class_coverage(code, tree)
        elif metric_name == "documentation_quality":
            return self._calculate_documentation_quality(code, tree)
        elif metric_name == "clarity_score":
            return self._calculate_clarity_score(code, tree)
        elif metric_name == "consistency_score":
            return self._calculate_consistency_score(code, tree)
        elif metric_name == "parameter_completeness":
            return self._calculate_parameter_completeness(code, tree)
        elif metric_name == "return_completeness":
            return self._calculate_return_completeness(code, tree)
        elif metric_name == "type_completeness":
            return self._calculate_type_completeness(code, tree)
        elif metric_name == "accessibility_score":
            return self._calculate_accessibility_score(code, tree)
        elif metric_name == "example_coverage":
            return self._calculate_example_coverage(code, tree)
        elif metric_name == "reference_coverage":
            return self._calculate_reference_coverage(code, tree)
        else:
            raise ValueError(f"Unknown metric: {metric_name}")
            
    def _determine_metric_status(self, value: float, threshold: float) -> str:
        """Determine metric status based on value and threshold"""
        if value >= threshold:
            return "good"
        elif value >= threshold * 0.8:
            return "warning"
        else:
            return "critical"
            
    def _generate_metric_recommendations(
        self,
        metric_name: str,
        value: float,
        threshold: float,
        status: str
    ) -> List[str]:
        """Generate recommendations for metric"""
        recommendations = []
        
        if status == "warning":
            recommendations.append(
                f"{metric_name} is slightly below threshold. Consider improving "
                f"documentation."
            )
        elif status == "critical":
            recommendations.append(
                f"{metric_name} is significantly below threshold. Immediate "
                f"documentation improvements are recommended."
            )
            
        # Add specific recommendations based on metric
        if "docstring" in metric_name and value < threshold:
            recommendations.append(
                "Docstring issues detected. Consider improving docstring content "
                "and structure."
            )
        elif "comment" in metric_name and value < threshold:
            recommendations.append(
                "Comment issues detected. Review and improve code comments."
            )
        elif "coverage" in metric_name and value < threshold:
            recommendations.append(
                "Coverage issues detected. Add missing documentation."
            )
        elif "quality" in metric_name and value < threshold:
            recommendations.append(
                "Quality issues detected. Improve documentation clarity and "
                "completeness."
            )
        elif "completeness" in metric_name and value < threshold:
            recommendations.append(
                "Completeness issues detected. Add missing documentation elements."
            )
        elif "accessibility" in metric_name and value < threshold:
            recommendations.append(
                "Accessibility issues detected. Improve documentation "
                "accessibility."
            )
            
        return recommendations
        
    def _generate_cross_metric_recommendations(
        self,
        metrics: Dict[str, DocumentationMetric]
    ) -> List[str]:
        """Generate recommendations based on multiple metrics"""
        recommendations = []
        
        # Check for multiple docstring issues
        docstring_metrics = [
            m for n, m in metrics.items()
            if any(p in n for p in ["docstring"])
        ]
        if len(docstring_metrics) > 1 and all(m.status == "critical" for m in docstring_metrics):
            recommendations.append(
                "Multiple critical docstring issues detected. Consider comprehensive "
                "docstring improvements."
            )
            
        # Check for coverage and quality issues
        if ("overall_coverage" in metrics and "documentation_quality" in metrics and
            metrics["overall_coverage"].status == "critical" and
            metrics["documentation_quality"].status == "critical"):
            recommendations.append(
                "Critical coverage and quality issues detected. Consider improving "
                "both documentation coverage and quality."
            )
            
        # Check for completeness and accessibility issues
        if ("parameter_completeness" in metrics and "accessibility_score" in metrics and
            metrics["parameter_completeness"].status == "critical" and
            metrics["accessibility_score"].status == "critical"):
            recommendations.append(
                "Critical completeness and accessibility issues detected. Review "
                "documentation completeness and accessibility."
            )
            
        return recommendations
        
    def get_analysis_history(self) -> List[DocumentationResult]:
        """Get analysis history"""
        return self.analysis_history
        
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        if not self.analysis_history:
            return {}
            
        latest = self.analysis_history[-1]
        return {
            "documentation_type": latest.documentation_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.metrics.items()
            },
            "issue_count": len(latest.issues),
            "recommendation_count": len(latest.recommendations)
        }
        
    def get_documentation_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get registered documentation patterns"""
        return self.documentation_patterns
        
    def get_analysis_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get documentation analysis metrics"""
        return self.analysis_metrics
        
    def register_documentation_pattern(
        self,
        issue_type: str,
        pattern: str,
        severity: str,
        description: str,
        recommendation: str
    ):
        """Register a new documentation pattern"""
        if issue_type not in self.documentation_patterns:
            self.documentation_patterns[issue_type] = []
            
        self.documentation_patterns[issue_type].append({
            "pattern": pattern,
            "severity": severity,
            "description": description,
            "recommendation": recommendation
        })
        
    # Metric calculation methods
    def _calculate_docstring_coverage(self, code: str, tree: ast.AST) -> float:
        """Calculate docstring coverage score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_docstring_quality(self, code: str, tree: ast.AST) -> float:
        """Calculate docstring quality score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_docstring_completeness(self, code: str, tree: ast.AST) -> float:
        """Calculate docstring completeness score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_comment_coverage(self, code: str, tree: ast.AST) -> float:
        """Calculate comment coverage score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_comment_quality(self, code: str, tree: ast.AST) -> float:
        """Calculate comment quality score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_comment_relevance(self, code: str, tree: ast.AST) -> float:
        """Calculate comment relevance score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_overall_coverage(self, code: str, tree: ast.AST) -> float:
        """Calculate overall coverage score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_function_coverage(self, code: str, tree: ast.AST) -> float:
        """Calculate function coverage score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_class_coverage(self, code: str, tree: ast.AST) -> float:
        """Calculate class coverage score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_documentation_quality(self, code: str, tree: ast.AST) -> float:
        """Calculate documentation quality score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_clarity_score(self, code: str, tree: ast.AST) -> float:
        """Calculate clarity score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_consistency_score(self, code: str, tree: ast.AST) -> float:
        """Calculate consistency score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_parameter_completeness(self, code: str, tree: ast.AST) -> float:
        """Calculate parameter completeness score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_return_completeness(self, code: str, tree: ast.AST) -> float:
        """Calculate return completeness score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_type_completeness(self, code: str, tree: ast.AST) -> float:
        """Calculate type completeness score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_accessibility_score(self, code: str, tree: ast.AST) -> float:
        """Calculate accessibility score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_example_coverage(self, code: str, tree: ast.AST) -> float:
        """Calculate example coverage score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_reference_coverage(self, code: str, tree: ast.AST) -> float:
        """Calculate reference coverage score"""
        # Implementation depends on the specific requirements
        return 0.8 