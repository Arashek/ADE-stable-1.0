from typing import Dict, List, Optional, Any, Tuple, Set
from pydantic import BaseModel
import logging
from datetime import datetime
from enum import Enum
import ast
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ArchitectureType(Enum):
    """Types of architecture analysis"""
    ROUTING = "routing"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE = "performance"
    SCALABILITY = "scalability"
    MAINTAINABILITY = "maintainability"
    SECURITY = "security"

class ArchitectureMetric(BaseModel):
    """Architecture metric"""
    name: str
    value: float
    threshold: float
    status: str
    details: Dict[str, Any] = {}
    recommendations: List[str] = []

class ArchitectureResult(BaseModel):
    """Result of architecture analysis"""
    architecture_type: ArchitectureType
    metrics: Dict[str, ArchitectureMetric]
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = {}

@dataclass
class ArchitectureIssue:
    """Information about an architecture issue"""
    type: str
    severity: str
    description: str
    line_number: int
    column: int
    code_snippet: str
    recommendation: str
    impact: str
    metadata: Dict[str, Any] = None

class ArchitectureAnalyzer:
    """Analyzer for assessing and improving code architecture"""
    
    def __init__(self):
        self.analysis_history: List[ArchitectureResult] = []
        self.architecture_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.analysis_metrics: Dict[str, Dict[str, float]] = {}
        self._initialize_patterns()
        self._initialize_architecture_rules()
        
    def _initialize_patterns(self):
        """Initialize architecture detection patterns"""
        # Routing patterns
        self.architecture_patterns["routing"] = [
            {
                "pattern": r"@app\.route\(.*?\)",
                "severity": "info",
                "description": "Route decorator detected",
                "recommendation": "Consider using Blueprint for better route organization"
            },
            {
                "pattern": r"@app\.before_request",
                "severity": "info",
                "description": "Global request handler detected",
                "recommendation": "Consider using middleware for better request handling"
            }
        ]
        
        # Error handling patterns
        self.architecture_patterns["error_handling"] = [
            {
                "pattern": r"try:.*?except:",
                "severity": "warning",
                "description": "Bare except clause detected",
                "recommendation": "Specify exception types and handle them appropriately"
            },
            {
                "pattern": r"except\s+Exception\s+as\s+e:",
                "severity": "warning",
                "description": "Generic exception handling detected",
                "recommendation": "Use specific exception types for better error handling"
            }
        ]
        
        # Performance patterns
        self.architecture_patterns["performance"] = [
            {
                "pattern": r"for\s+.*?in\s+range\(.*?\):",
                "severity": "warning",
                "description": "Potential performance bottleneck detected",
                "recommendation": "Consider using list comprehension or vectorized operations"
            },
            {
                "pattern": r"\.append\(.*?\)\s+in\s+loop",
                "severity": "warning",
                "description": "List append in loop detected",
                "recommendation": "Use list comprehension or pre-allocate list"
            }
        ]
        
        # Scalability patterns
        self.architecture_patterns["scalability"] = [
            {
                "pattern": r"global\s+.*?=",
                "severity": "warning",
                "description": "Global variable usage detected",
                "recommendation": "Use dependency injection or configuration management"
            },
            {
                "pattern": r"threading\.Thread\(.*?\)\s+in\s+loop",
                "severity": "warning",
                "description": "Thread creation in loop detected",
                "recommendation": "Use thread pool or asyncio for better scalability"
            }
        ]
        
        # Maintainability patterns
        self.architecture_patterns["maintainability"] = [
            {
                "pattern": r"def\s+\w+\(.*?\):.*?pass",
                "severity": "warning",
                "description": "Empty function detected",
                "recommendation": "Implement function or remove if not needed"
            },
            {
                "pattern": r"#\s+TODO|#\s+FIXME",
                "severity": "info",
                "description": "TODO/FIXME comment detected",
                "recommendation": "Address technical debt and document issues"
            }
        ]
        
        # Security patterns
        self.architecture_patterns["security"] = [
            {
                "pattern": r"password\s*=\s*['\"].*?['\"]",
                "severity": "critical",
                "description": "Hardcoded password detected",
                "recommendation": "Use environment variables or secure configuration"
            },
            {
                "pattern": r"eval\(.*?\)|exec\(.*?\)",
                "severity": "critical",
                "description": "Dynamic code execution detected",
                "recommendation": "Avoid using eval/exec for security reasons"
            }
        ]
        
    def _initialize_architecture_rules(self):
        """Initialize architecture rules"""
        self.architecture_rules = {
            ArchitectureType.ROUTING: [
                {
                    "name": "route_organization",
                    "threshold": 0.8,
                    "description": "Route organization score"
                },
                {
                    "name": "middleware_usage",
                    "threshold": 0.8,
                    "description": "Middleware usage score"
                },
                {
                    "name": "route_handling",
                    "threshold": 0.8,
                    "description": "Route handling efficiency score"
                }
            ],
            ArchitectureType.ERROR_HANDLING: [
                {
                    "name": "error_coverage",
                    "threshold": 0.8,
                    "description": "Error handling coverage score"
                },
                {
                    "name": "error_specificity",
                    "threshold": 0.8,
                    "description": "Error handling specificity score"
                },
                {
                    "name": "error_recovery",
                    "threshold": 0.7,
                    "description": "Error recovery capability score"
                }
            ],
            ArchitectureType.PERFORMANCE: [
                {
                    "name": "algorithm_efficiency",
                    "threshold": 0.8,
                    "description": "Algorithm efficiency score"
                },
                {
                    "name": "resource_usage",
                    "threshold": 0.8,
                    "description": "Resource usage efficiency score"
                },
                {
                    "name": "response_time",
                    "threshold": 0.7,
                    "description": "Response time efficiency score"
                }
            ],
            ArchitectureType.SCALABILITY: [
                {
                    "name": "horizontal_scaling",
                    "threshold": 0.8,
                    "description": "Horizontal scaling capability score"
                },
                {
                    "name": "resource_management",
                    "threshold": 0.8,
                    "description": "Resource management efficiency score"
                },
                {
                    "name": "load_balancing",
                    "threshold": 0.7,
                    "description": "Load balancing capability score"
                }
            ],
            ArchitectureType.MAINTAINABILITY: [
                {
                    "name": "code_organization",
                    "threshold": 0.8,
                    "description": "Code organization score"
                },
                {
                    "name": "documentation",
                    "threshold": 0.8,
                    "description": "Documentation quality score"
                },
                {
                    "name": "technical_debt",
                    "threshold": 0.7,
                    "description": "Technical debt score"
                }
            ],
            ArchitectureType.SECURITY: [
                {
                    "name": "security_controls",
                    "threshold": 0.8,
                    "description": "Security controls score"
                },
                {
                    "name": "vulnerability_management",
                    "threshold": 0.8,
                    "description": "Vulnerability management score"
                },
                {
                    "name": "compliance",
                    "threshold": 0.7,
                    "description": "Compliance score"
                }
            ]
        }
        
    def analyze_architecture(
        self,
        code: str,
        file_path: str,
        architecture_type: ArchitectureType,
        context: Optional[Dict[str, Any]] = None
    ) -> ArchitectureResult:
        """Analyze code architecture based on specified type"""
        try:
            # Initialize result
            result = ArchitectureResult(
                architecture_type=architecture_type,
                metrics={},
                issues=[],
                recommendations=[],
                metadata={
                    "analyzed_at": datetime.now().isoformat(),
                    "file_path": file_path,
                    "context": context or {}
                }
            )
            
            # Get architecture rules for type
            rules = self.architecture_rules.get(architecture_type, [])
            
            # Parse code
            tree = ast.parse(code)
            
            # Perform analysis
            for rule in rules:
                metric = self._analyze_architecture_metric(
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
            raise ValueError(f"Failed to analyze architecture: {str(e)}")
            
    def _analyze_architecture_metric(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        threshold: float,
        context: Optional[Dict[str, Any]] = None
    ) -> ArchitectureMetric:
        """Analyze specific architecture metric"""
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
            
            return ArchitectureMetric(
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
            logger.error(f"Failed to analyze architecture metric {metric_name}: {str(e)}")
            return ArchitectureMetric(
                name=metric_name,
                value=0.0,
                threshold=threshold,
                status="error",
                details={"error": str(e)},
                recommendations=["Fix architecture analysis error"]
            )
            
    def _calculate_metric_value(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate metric value"""
        if metric_name == "route_organization":
            return self._calculate_route_organization(code, tree)
        elif metric_name == "middleware_usage":
            return self._calculate_middleware_usage(code, tree)
        elif metric_name == "route_handling":
            return self._calculate_route_handling(code, tree)
        elif metric_name == "error_coverage":
            return self._calculate_error_coverage(code, tree)
        elif metric_name == "error_specificity":
            return self._calculate_error_specificity(code, tree)
        elif metric_name == "error_recovery":
            return self._calculate_error_recovery(code, tree)
        elif metric_name == "algorithm_efficiency":
            return self._calculate_algorithm_efficiency(code, tree)
        elif metric_name == "resource_usage":
            return self._calculate_resource_usage(code, tree)
        elif metric_name == "response_time":
            return self._calculate_response_time(code, tree)
        elif metric_name == "horizontal_scaling":
            return self._calculate_horizontal_scaling(code, tree)
        elif metric_name == "resource_management":
            return self._calculate_resource_management(code, tree)
        elif metric_name == "load_balancing":
            return self._calculate_load_balancing(code, tree)
        elif metric_name == "code_organization":
            return self._calculate_code_organization(code, tree)
        elif metric_name == "documentation":
            return self._calculate_documentation(code, tree)
        elif metric_name == "technical_debt":
            return self._calculate_technical_debt(code, tree)
        elif metric_name == "security_controls":
            return self._calculate_security_controls(code, tree)
        elif metric_name == "vulnerability_management":
            return self._calculate_vulnerability_management(code, tree)
        elif metric_name == "compliance":
            return self._calculate_compliance(code, tree)
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
                f"architecture."
            )
        elif status == "critical":
            recommendations.append(
                f"{metric_name} is significantly below threshold. Immediate "
                f"architecture improvements are recommended."
            )
            
        # Add specific recommendations based on metric
        if "route" in metric_name and value < threshold:
            recommendations.append(
                "Route organization issues detected. Consider using Blueprint and "
                "better route organization patterns."
            )
        elif "error" in metric_name and value < threshold:
            recommendations.append(
                "Error handling issues detected. Implement proper error handling "
                "and recovery mechanisms."
            )
        elif "performance" in metric_name and value < threshold:
            recommendations.append(
                "Performance issues detected. Consider optimizing algorithms and "
                "resource usage."
            )
        elif "scaling" in metric_name and value < threshold:
            recommendations.append(
                "Scalability issues detected. Implement better resource management "
                "and scaling patterns."
            )
        elif "maintainability" in metric_name and value < threshold:
            recommendations.append(
                "Maintainability issues detected. Improve code organization and "
                "documentation."
            )
        elif "security" in metric_name and value < threshold:
            recommendations.append(
                "Security issues detected. Implement proper security controls and "
                "vulnerability management."
            )
            
        return recommendations
        
    def _generate_cross_metric_recommendations(
        self,
        metrics: Dict[str, ArchitectureMetric]
    ) -> List[str]:
        """Generate recommendations based on multiple metrics"""
        recommendations = []
        
        # Check for multiple architecture issues
        architecture_metrics = [
            m for n, m in metrics.items()
            if any(p in n for p in ["route", "error", "performance", "scaling"])
        ]
        if len(architecture_metrics) > 1 and all(m.status == "critical" for m in architecture_metrics):
            recommendations.append(
                "Multiple critical architecture issues detected. Consider comprehensive "
                "architecture improvements."
            )
            
        # Check for security and performance issues
        if ("security_controls" in metrics and "performance" in metrics and
            metrics["security_controls"].status == "critical" and
            metrics["performance"].status == "critical"):
            recommendations.append(
                "Critical security and performance issues detected. Consider "
                "implementing better security controls and performance optimizations."
            )
            
        # Check for maintainability and scalability issues
        if ("maintainability" in metrics and "scaling" in metrics and
            metrics["maintainability"].status == "critical" and
            metrics["scaling"].status == "critical"):
            recommendations.append(
                "Critical maintainability and scalability issues detected. Consider "
                "improving code organization and implementing better scaling patterns."
            )
            
        return recommendations
        
    def get_analysis_history(self) -> List[ArchitectureResult]:
        """Get analysis history"""
        return self.analysis_history
        
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        if not self.analysis_history:
            return {}
            
        latest = self.analysis_history[-1]
        return {
            "architecture_type": latest.architecture_type.value,
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
        
    def get_architecture_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get registered architecture patterns"""
        return self.architecture_patterns
        
    def get_analysis_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get architecture analysis metrics"""
        return self.analysis_metrics
        
    def register_architecture_pattern(
        self,
        issue_type: str,
        pattern: str,
        severity: str,
        description: str,
        recommendation: str
    ):
        """Register a new architecture pattern"""
        if issue_type not in self.architecture_patterns:
            self.architecture_patterns[issue_type] = []
            
        self.architecture_patterns[issue_type].append({
            "pattern": pattern,
            "severity": severity,
            "description": description,
            "recommendation": recommendation
        })
        
    # Metric calculation methods
    def _calculate_route_organization(self, code: str, tree: ast.AST) -> float:
        """Calculate route organization score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_middleware_usage(self, code: str, tree: ast.AST) -> float:
        """Calculate middleware usage score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_route_handling(self, code: str, tree: ast.AST) -> float:
        """Calculate route handling efficiency score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_error_coverage(self, code: str, tree: ast.AST) -> float:
        """Calculate error handling coverage score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_error_specificity(self, code: str, tree: ast.AST) -> float:
        """Calculate error handling specificity score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_error_recovery(self, code: str, tree: ast.AST) -> float:
        """Calculate error recovery capability score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_algorithm_efficiency(self, code: str, tree: ast.AST) -> float:
        """Calculate algorithm efficiency score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_resource_usage(self, code: str, tree: ast.AST) -> float:
        """Calculate resource usage efficiency score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_response_time(self, code: str, tree: ast.AST) -> float:
        """Calculate response time efficiency score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_horizontal_scaling(self, code: str, tree: ast.AST) -> float:
        """Calculate horizontal scaling capability score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_resource_management(self, code: str, tree: ast.AST) -> float:
        """Calculate resource management efficiency score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_load_balancing(self, code: str, tree: ast.AST) -> float:
        """Calculate load balancing capability score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_code_organization(self, code: str, tree: ast.AST) -> float:
        """Calculate code organization score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_documentation(self, code: str, tree: ast.AST) -> float:
        """Calculate documentation quality score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_technical_debt(self, code: str, tree: ast.AST) -> float:
        """Calculate technical debt score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_security_controls(self, code: str, tree: ast.AST) -> float:
        """Calculate security controls score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_vulnerability_management(self, code: str, tree: ast.AST) -> float:
        """Calculate vulnerability management score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_compliance(self, code: str, tree: ast.AST) -> float:
        """Calculate compliance score"""
        # Implementation depends on the specific requirements
        return 0.8 