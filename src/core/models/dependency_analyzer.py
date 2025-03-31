from typing import Dict, List, Optional, Any, Tuple, Set
from pydantic import BaseModel
import ast
import logging
from datetime import datetime
from enum import Enum
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class DependencyType(Enum):
    """Types of dependency analysis"""
    IMPORTS = "imports"
    MODULES = "modules"
    CYCLES = "cycles"
    VERSIONS = "versions"
    SECURITY = "security"
    PERFORMANCE = "performance"

class DependencyMetric(BaseModel):
    """Dependency metric"""
    name: str
    value: float
    threshold: float
    status: str
    details: Dict[str, Any] = {}
    recommendations: List[str] = []

class DependencyResult(BaseModel):
    """Result of dependency analysis"""
    dependency_type: DependencyType
    metrics: Dict[str, DependencyMetric]
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = {}

@dataclass
class Dependency:
    """Information about a dependency"""
    name: str
    type: str
    version: Optional[str]
    source: str
    line_number: int
    column: int
    context: Optional[Dict[str, Any]] = None

class DependencyAnalyzer:
    """Analyzer for assessing code dependencies"""
    
    def __init__(self):
        self.analysis_history: List[DependencyResult] = []
        self.dependency_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.analysis_metrics: Dict[str, Dict[str, float]] = {}
        self._initialize_patterns()
        self._initialize_dependency_rules()
        
    def _initialize_patterns(self):
        """Initialize dependency detection patterns"""
        # Import patterns
        self.dependency_patterns["imports"] = [
            {
                "pattern": r"^import\s+\w+",
                "severity": "info",
                "description": "Direct import detected",
                "recommendation": "Review import statement"
            },
            {
                "pattern": r"^from\s+\w+\s+import\s+\w+",
                "severity": "info",
                "description": "From import detected",
                "recommendation": "Review from import statement"
            }
        ]
        
        # Module patterns
        self.dependency_patterns["modules"] = [
            {
                "pattern": r"^import\s+\w+\.\w+",
                "severity": "info",
                "description": "Module import detected",
                "recommendation": "Review module import"
            },
            {
                "pattern": r"^from\s+\w+\.\w+\s+import\s+\w+",
                "severity": "info",
                "description": "Module from import detected",
                "recommendation": "Review module from import"
            }
        ]
        
        # Version patterns
        self.dependency_patterns["versions"] = [
            {
                "pattern": r"^import\s+\w+\s+as\s+\w+",
                "severity": "info",
                "description": "Aliased import detected",
                "recommendation": "Review import alias"
            },
            {
                "pattern": r"^from\s+\w+\s+import\s+\*\s*$",
                "severity": "warning",
                "description": "Wildcard import detected",
                "recommendation": "Avoid wildcard imports"
            }
        ]
        
        # Security patterns
        self.dependency_patterns["security"] = [
            {
                "pattern": r"^import\s+os\s*$",
                "severity": "warning",
                "description": "OS module import detected",
                "recommendation": "Review OS module usage"
            },
            {
                "pattern": r"^import\s+subprocess\s*$",
                "severity": "warning",
                "description": "Subprocess module import detected",
                "recommendation": "Review subprocess usage"
            }
        ]
        
        # Performance patterns
        self.dependency_patterns["performance"] = [
            {
                "pattern": r"^import\s+numpy\s*$",
                "severity": "info",
                "description": "NumPy import detected",
                "recommendation": "Review NumPy usage"
            },
            {
                "pattern": r"^import\s+pandas\s*$",
                "severity": "info",
                "description": "Pandas import detected",
                "recommendation": "Review Pandas usage"
            }
        ]
        
    def _initialize_dependency_rules(self):
        """Initialize dependency rules"""
        self.dependency_rules = {
            DependencyType.IMPORTS: [
                {
                    "name": "import_count",
                    "threshold": 20,
                    "description": "Number of imports"
                },
                {
                    "name": "import_complexity",
                    "threshold": 0.7,
                    "description": "Import complexity score"
                },
                {
                    "name": "import_organization",
                    "threshold": 0.8,
                    "description": "Import organization score"
                }
            ],
            DependencyType.MODULES: [
                {
                    "name": "module_count",
                    "threshold": 10,
                    "description": "Number of modules"
                },
                {
                    "name": "module_depth",
                    "threshold": 3,
                    "description": "Module depth"
                },
                {
                    "name": "module_cohesion",
                    "threshold": 0.8,
                    "description": "Module cohesion score"
                }
            ],
            DependencyType.CYCLES: [
                {
                    "name": "cycle_count",
                    "threshold": 0,
                    "description": "Number of dependency cycles"
                },
                {
                    "name": "cycle_complexity",
                    "threshold": 0.7,
                    "description": "Cycle complexity score"
                },
                {
                    "name": "cycle_impact",
                    "threshold": 0.7,
                    "description": "Cycle impact score"
                }
            ],
            DependencyType.VERSIONS: [
                {
                    "name": "version_compatibility",
                    "threshold": 0.8,
                    "description": "Version compatibility score"
                },
                {
                    "name": "version_stability",
                    "threshold": 0.8,
                    "description": "Version stability score"
                },
                {
                    "name": "version_security",
                    "threshold": 0.8,
                    "description": "Version security score"
                }
            ],
            DependencyType.SECURITY: [
                {
                    "name": "security_risk",
                    "threshold": 0.8,
                    "description": "Security risk score"
                },
                {
                    "name": "security_compliance",
                    "threshold": 0.8,
                    "description": "Security compliance score"
                },
                {
                    "name": "security_vulnerabilities",
                    "threshold": 0,
                    "description": "Number of security vulnerabilities"
                }
            ],
            DependencyType.PERFORMANCE: [
                {
                    "name": "performance_impact",
                    "threshold": 0.8,
                    "description": "Performance impact score"
                },
                {
                    "name": "resource_usage",
                    "threshold": 0.8,
                    "description": "Resource usage score"
                },
                {
                    "name": "optimization_potential",
                    "threshold": 0.7,
                    "description": "Optimization potential score"
                }
            ]
        }
        
    def analyze_dependencies(
        self,
        code: str,
        file_path: str,
        dependency_type: DependencyType,
        context: Optional[Dict[str, Any]] = None
    ) -> DependencyResult:
        """Analyze dependencies based on specified type"""
        try:
            # Initialize result
            result = DependencyResult(
                dependency_type=dependency_type,
                metrics={},
                issues=[],
                recommendations=[],
                metadata={
                    "analyzed_at": datetime.now().isoformat(),
                    "file_path": file_path,
                    "context": context or {}
                }
            )
            
            # Get dependency rules for type
            rules = self.dependency_rules.get(dependency_type, [])
            
            # Parse code
            tree = ast.parse(code)
            
            # Perform analysis
            for rule in rules:
                metric = self._analyze_dependency_metric(
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
            raise ValueError(f"Failed to analyze dependencies: {str(e)}")
            
    def _analyze_dependency_metric(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        threshold: float,
        context: Optional[Dict[str, Any]] = None
    ) -> DependencyMetric:
        """Analyze specific dependency metric"""
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
            
            return DependencyMetric(
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
            logger.error(f"Failed to analyze dependency metric {metric_name}: {str(e)}")
            return DependencyMetric(
                name=metric_name,
                value=0.0,
                threshold=threshold,
                status="error",
                details={"error": str(e)},
                recommendations=["Fix dependency analysis error"]
            )
            
    def _calculate_metric_value(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate metric value"""
        if metric_name == "import_count":
            return self._calculate_import_count(code, tree)
        elif metric_name == "import_complexity":
            return self._calculate_import_complexity(code, tree)
        elif metric_name == "import_organization":
            return self._calculate_import_organization(code, tree)
        elif metric_name == "module_count":
            return self._calculate_module_count(code, tree)
        elif metric_name == "module_depth":
            return self._calculate_module_depth(code, tree)
        elif metric_name == "module_cohesion":
            return self._calculate_module_cohesion(code, tree)
        elif metric_name == "cycle_count":
            return self._calculate_cycle_count(code, tree)
        elif metric_name == "cycle_complexity":
            return self._calculate_cycle_complexity(code, tree)
        elif metric_name == "cycle_impact":
            return self._calculate_cycle_impact(code, tree)
        elif metric_name == "version_compatibility":
            return self._calculate_version_compatibility(code, tree)
        elif metric_name == "version_stability":
            return self._calculate_version_stability(code, tree)
        elif metric_name == "version_security":
            return self._calculate_version_security(code, tree)
        elif metric_name == "security_risk":
            return self._calculate_security_risk(code, tree)
        elif metric_name == "security_compliance":
            return self._calculate_security_compliance(code, tree)
        elif metric_name == "security_vulnerabilities":
            return self._calculate_security_vulnerabilities(code, tree)
        elif metric_name == "performance_impact":
            return self._calculate_performance_impact(code, tree)
        elif metric_name == "resource_usage":
            return self._calculate_resource_usage(code, tree)
        elif metric_name == "optimization_potential":
            return self._calculate_optimization_potential(code, tree)
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
                f"dependency management."
            )
        elif status == "critical":
            recommendations.append(
                f"{metric_name} is significantly below threshold. Immediate "
                f"dependency improvements are recommended."
            )
            
        # Add specific recommendations based on metric
        if "import" in metric_name and value < threshold:
            recommendations.append(
                "Import issues detected. Consider organizing and optimizing imports."
            )
        elif "module" in metric_name and value < threshold:
            recommendations.append(
                "Module issues detected. Review module organization and structure."
            )
        elif "cycle" in metric_name and value < threshold:
            recommendations.append(
                "Dependency cycle issues detected. Consider breaking circular "
                "dependencies."
            )
        elif "version" in metric_name and value < threshold:
            recommendations.append(
                "Version issues detected. Review dependency versions and compatibility."
            )
        elif "security" in metric_name and value < threshold:
            recommendations.append(
                "Security issues detected. Review dependency security and compliance."
            )
        elif "performance" in metric_name and value < threshold:
            recommendations.append(
                "Performance issues detected. Consider optimizing dependency usage."
            )
            
        return recommendations
        
    def _generate_cross_metric_recommendations(
        self,
        metrics: Dict[str, DependencyMetric]
    ) -> List[str]:
        """Generate recommendations based on multiple metrics"""
        recommendations = []
        
        # Check for multiple import issues
        import_metrics = [
            m for n, m in metrics.items()
            if any(p in n for p in ["import"])
        ]
        if len(import_metrics) > 1 and all(m.status == "critical" for m in import_metrics):
            recommendations.append(
                "Multiple critical import issues detected. Consider comprehensive "
                "import optimization."
            )
            
        # Check for module and cycle issues
        if ("module_cohesion" in metrics and "cycle_count" in metrics and
            metrics["module_cohesion"].status == "critical" and
            metrics["cycle_count"].status == "critical"):
            recommendations.append(
                "Critical module and cycle issues detected. Consider improving "
                "module organization and breaking cycles."
            )
            
        # Check for version and security issues
        if ("version_compatibility" in metrics and "security_risk" in metrics and
            metrics["version_compatibility"].status == "critical" and
            metrics["security_risk"].status == "critical"):
            recommendations.append(
                "Critical version and security issues detected. Review dependency "
                "versions and security."
            )
            
        return recommendations
        
    def get_analysis_history(self) -> List[DependencyResult]:
        """Get analysis history"""
        return self.analysis_history
        
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        if not self.analysis_history:
            return {}
            
        latest = self.analysis_history[-1]
        return {
            "dependency_type": latest.dependency_type.value,
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
        
    def get_dependency_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get registered dependency patterns"""
        return self.dependency_patterns
        
    def get_analysis_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get dependency analysis metrics"""
        return self.analysis_metrics
        
    def register_dependency_pattern(
        self,
        issue_type: str,
        pattern: str,
        severity: str,
        description: str,
        recommendation: str
    ):
        """Register a new dependency pattern"""
        if issue_type not in self.dependency_patterns:
            self.dependency_patterns[issue_type] = []
            
        self.dependency_patterns[issue_type].append({
            "pattern": pattern,
            "severity": severity,
            "description": description,
            "recommendation": recommendation
        })
        
    # Metric calculation methods
    def _calculate_import_count(self, code: str, tree: ast.AST) -> float:
        """Calculate import count score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_import_complexity(self, code: str, tree: ast.AST) -> float:
        """Calculate import complexity score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_import_organization(self, code: str, tree: ast.AST) -> float:
        """Calculate import organization score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_module_count(self, code: str, tree: ast.AST) -> float:
        """Calculate module count score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_module_depth(self, code: str, tree: ast.AST) -> float:
        """Calculate module depth score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_module_cohesion(self, code: str, tree: ast.AST) -> float:
        """Calculate module cohesion score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_cycle_count(self, code: str, tree: ast.AST) -> float:
        """Calculate cycle count score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_cycle_complexity(self, code: str, tree: ast.AST) -> float:
        """Calculate cycle complexity score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_cycle_impact(self, code: str, tree: ast.AST) -> float:
        """Calculate cycle impact score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_version_compatibility(self, code: str, tree: ast.AST) -> float:
        """Calculate version compatibility score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_version_stability(self, code: str, tree: ast.AST) -> float:
        """Calculate version stability score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_version_security(self, code: str, tree: ast.AST) -> float:
        """Calculate version security score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_security_risk(self, code: str, tree: ast.AST) -> float:
        """Calculate security risk score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_security_compliance(self, code: str, tree: ast.AST) -> float:
        """Calculate security compliance score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_security_vulnerabilities(self, code: str, tree: ast.AST) -> float:
        """Calculate security vulnerabilities score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_performance_impact(self, code: str, tree: ast.AST) -> float:
        """Calculate performance impact score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_resource_usage(self, code: str, tree: ast.AST) -> float:
        """Calculate resource usage score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_optimization_potential(self, code: str, tree: ast.AST) -> float:
        """Calculate optimization potential score"""
        # Implementation depends on the specific requirements
        return 0.8 