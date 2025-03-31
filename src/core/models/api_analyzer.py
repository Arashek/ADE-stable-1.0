from typing import Dict, List, Optional, Any, Tuple, Set
from pydantic import BaseModel
import logging
from datetime import datetime
from enum import Enum
import ast
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class APIType(Enum):
    """Types of API analysis"""
    ENDPOINT = "endpoint"
    REQUEST = "request"
    RESPONSE = "response"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    PERFORMANCE = "performance"

class APIMetric(BaseModel):
    """API metric"""
    name: str
    value: float
    threshold: float
    status: str
    details: Dict[str, Any] = {}
    recommendations: List[str] = []

class APIResult(BaseModel):
    """Result of API analysis"""
    api_type: APIType
    metrics: Dict[str, APIMetric]
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = {}

@dataclass
class APIEndpoint:
    """Information about an API endpoint"""
    path: str
    method: str
    parameters: List[Dict[str, Any]]
    responses: List[Dict[str, Any]]
    security: List[Dict[str, Any]]
    documentation: Optional[str] = None
    performance_metrics: Optional[Dict[str, float]] = None

class APIAnalyzer:
    """Analyzer for assessing and improving API design and implementation"""
    
    def __init__(self):
        self.analysis_history: List[APIResult] = []
        self.api_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.analysis_metrics: Dict[str, Dict[str, float]] = {}
        self._initialize_patterns()
        self._initialize_api_rules()
        
    def _initialize_patterns(self):
        """Initialize API detection patterns"""
        # Endpoint patterns
        self.api_patterns["endpoint"] = [
            {
                "pattern": r"@app\.route\(.*?\)",
                "severity": "info",
                "description": "API endpoint detected",
                "recommendation": "Consider using Blueprint for better route organization"
            },
            {
                "pattern": r"@app\.before_request",
                "severity": "info",
                "description": "Global request handler detected",
                "recommendation": "Consider using middleware for better request handling"
            }
        ]
        
        # Request patterns
        self.api_patterns["request"] = [
            {
                "pattern": r"request\.json",
                "severity": "warning",
                "description": "JSON request body detected",
                "recommendation": "Implement request validation and sanitization"
            },
            {
                "pattern": r"request\.args",
                "severity": "warning",
                "description": "Query parameters detected",
                "recommendation": "Validate and sanitize query parameters"
            }
        ]
        
        # Response patterns
        self.api_patterns["response"] = [
            {
                "pattern": r"jsonify\(.*?\)",
                "severity": "info",
                "description": "JSON response detected",
                "recommendation": "Consider implementing response compression"
            },
            {
                "pattern": r"send_file\(.*?\)",
                "severity": "warning",
                "description": "File response detected",
                "recommendation": "Implement proper file type validation"
            }
        ]
        
        # Documentation patterns
        self.api_patterns["documentation"] = [
            {
                "pattern": r'"""[\s\S]*?"""',
                "severity": "info",
                "description": "Docstring detected",
                "recommendation": "Consider using OpenAPI/Swagger documentation"
            },
            {
                "pattern": r"#\s*API\s*Documentation",
                "severity": "info",
                "description": "API documentation comment detected",
                "recommendation": "Use structured documentation format"
            }
        ]
        
        # Security patterns
        self.api_patterns["security"] = [
            {
                "pattern": r"@login_required",
                "severity": "info",
                "description": "Authentication decorator detected",
                "recommendation": "Consider implementing rate limiting"
            },
            {
                "pattern": r"@admin_required",
                "severity": "info",
                "description": "Admin authorization detected",
                "recommendation": "Implement role-based access control"
            }
        ]
        
        # Performance patterns
        self.api_patterns["performance"] = [
            {
                "pattern": r"cache\.cached\(.*?\)",
                "severity": "info",
                "description": "Cache decorator detected",
                "recommendation": "Consider implementing cache invalidation"
            },
            {
                "pattern": r"db\.session\.query\(.*?\)",
                "severity": "warning",
                "description": "Database query detected",
                "recommendation": "Optimize database queries and implement caching"
            }
        ]
        
    def _initialize_api_rules(self):
        """Initialize API rules"""
        self.api_rules = {
            APIType.ENDPOINT: [
                {
                    "name": "endpoint_organization",
                    "threshold": 0.8,
                    "description": "Endpoint organization score"
                },
                {
                    "name": "route_handling",
                    "threshold": 0.8,
                    "description": "Route handling efficiency score"
                },
                {
                    "name": "versioning",
                    "threshold": 0.7,
                    "description": "API versioning score"
                }
            ],
            APIType.REQUEST: [
                {
                    "name": "request_validation",
                    "threshold": 0.8,
                    "description": "Request validation score"
                },
                {
                    "name": "parameter_handling",
                    "threshold": 0.8,
                    "description": "Parameter handling score"
                },
                {
                    "name": "input_sanitization",
                    "threshold": 0.8,
                    "description": "Input sanitization score"
                }
            ],
            APIType.RESPONSE: [
                {
                    "name": "response_format",
                    "threshold": 0.8,
                    "description": "Response format consistency score"
                },
                {
                    "name": "error_handling",
                    "threshold": 0.8,
                    "description": "Error handling score"
                },
                {
                    "name": "status_codes",
                    "threshold": 0.7,
                    "description": "HTTP status code usage score"
                }
            ],
            APIType.DOCUMENTATION: [
                {
                    "name": "doc_completeness",
                    "threshold": 0.8,
                    "description": "Documentation completeness score"
                },
                {
                    "name": "doc_quality",
                    "threshold": 0.8,
                    "description": "Documentation quality score"
                },
                {
                    "name": "examples",
                    "threshold": 0.7,
                    "description": "Example coverage score"
                }
            ],
            APIType.SECURITY: [
                {
                    "name": "authentication",
                    "threshold": 0.8,
                    "description": "Authentication implementation score"
                },
                {
                    "name": "authorization",
                    "threshold": 0.8,
                    "description": "Authorization implementation score"
                },
                {
                    "name": "rate_limiting",
                    "threshold": 0.7,
                    "description": "Rate limiting implementation score"
                }
            ],
            APIType.PERFORMANCE: [
                {
                    "name": "response_time",
                    "threshold": 0.8,
                    "description": "Response time efficiency score"
                },
                {
                    "name": "caching",
                    "threshold": 0.8,
                    "description": "Caching implementation score"
                },
                {
                    "name": "resource_usage",
                    "threshold": 0.7,
                    "description": "Resource usage efficiency score"
                }
            ]
        }
        
    def analyze_api(
        self,
        code: str,
        file_path: str,
        api_type: APIType,
        context: Optional[Dict[str, Any]] = None
    ) -> APIResult:
        """Analyze API based on specified type"""
        try:
            # Initialize result
            result = APIResult(
                api_type=api_type,
                metrics={},
                issues=[],
                recommendations=[],
                metadata={
                    "analyzed_at": datetime.now().isoformat(),
                    "file_path": file_path,
                    "context": context or {}
                }
            )
            
            # Get API rules for type
            rules = self.api_rules.get(api_type, [])
            
            # Parse code
            tree = ast.parse(code)
            
            # Perform analysis
            for rule in rules:
                metric = self._analyze_api_metric(
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
            raise ValueError(f"Failed to analyze API: {str(e)}")
            
    def _analyze_api_metric(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        threshold: float,
        context: Optional[Dict[str, Any]] = None
    ) -> APIMetric:
        """Analyze specific API metric"""
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
            
            return APIMetric(
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
            logger.error(f"Failed to analyze API metric {metric_name}: {str(e)}")
            return APIMetric(
                name=metric_name,
                value=0.0,
                threshold=threshold,
                status="error",
                details={"error": str(e)},
                recommendations=["Fix API analysis error"]
            )
            
    def _calculate_metric_value(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate metric value"""
        if metric_name == "endpoint_organization":
            return self._calculate_endpoint_organization(code, tree)
        elif metric_name == "route_handling":
            return self._calculate_route_handling(code, tree)
        elif metric_name == "versioning":
            return self._calculate_versioning(code, tree)
        elif metric_name == "request_validation":
            return self._calculate_request_validation(code, tree)
        elif metric_name == "parameter_handling":
            return self._calculate_parameter_handling(code, tree)
        elif metric_name == "input_sanitization":
            return self._calculate_input_sanitization(code, tree)
        elif metric_name == "response_format":
            return self._calculate_response_format(code, tree)
        elif metric_name == "error_handling":
            return self._calculate_error_handling(code, tree)
        elif metric_name == "status_codes":
            return self._calculate_status_codes(code, tree)
        elif metric_name == "doc_completeness":
            return self._calculate_doc_completeness(code, tree)
        elif metric_name == "doc_quality":
            return self._calculate_doc_quality(code, tree)
        elif metric_name == "examples":
            return self._calculate_examples(code, tree)
        elif metric_name == "authentication":
            return self._calculate_authentication(code, tree)
        elif metric_name == "authorization":
            return self._calculate_authorization(code, tree)
        elif metric_name == "rate_limiting":
            return self._calculate_rate_limiting(code, tree)
        elif metric_name == "response_time":
            return self._calculate_response_time(code, tree)
        elif metric_name == "caching":
            return self._calculate_caching(code, tree)
        elif metric_name == "resource_usage":
            return self._calculate_resource_usage(code, tree)
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
                f"API implementation."
            )
        elif status == "critical":
            recommendations.append(
                f"{metric_name} is significantly below threshold. Immediate "
                f"API improvements are recommended."
            )
            
        # Add specific recommendations based on metric
        if "endpoint" in metric_name and value < threshold:
            recommendations.append(
                "Endpoint organization issues detected. Consider using Blueprint and "
                "better route organization patterns."
            )
        elif "request" in metric_name and value < threshold:
            recommendations.append(
                "Request handling issues detected. Implement proper validation and "
                "sanitization mechanisms."
            )
        elif "response" in metric_name and value < threshold:
            recommendations.append(
                "Response handling issues detected. Consider optimizing response "
                "format and error handling."
            )
        elif "documentation" in metric_name and value < threshold:
            recommendations.append(
                "Documentation issues detected. Improve API documentation and "
                "example coverage."
            )
        elif "security" in metric_name and value < threshold:
            recommendations.append(
                "Security issues detected. Implement proper authentication, "
                "authorization, and rate limiting."
            )
        elif "performance" in metric_name and value < threshold:
            recommendations.append(
                "Performance issues detected. Consider implementing caching and "
                "optimizing resource usage."
            )
            
        return recommendations
        
    def _generate_cross_metric_recommendations(
        self,
        metrics: Dict[str, APIMetric]
    ) -> List[str]:
        """Generate recommendations based on multiple metrics"""
        recommendations = []
        
        # Check for multiple API issues
        api_metrics = [
            m for n, m in metrics.items()
            if any(p in n for p in ["endpoint", "request", "response"])
        ]
        if len(api_metrics) > 1 and all(m.status == "critical" for m in api_metrics):
            recommendations.append(
                "Multiple critical API issues detected. Consider comprehensive "
                "API improvements."
            )
            
        # Check for security and performance issues
        if ("authentication" in metrics and "response_time" in metrics and
            metrics["authentication"].status == "critical" and
            metrics["response_time"].status == "critical"):
            recommendations.append(
                "Critical security and performance issues detected. Consider "
                "implementing better security controls and performance optimizations."
            )
            
        # Check for documentation and error handling issues
        if ("doc_completeness" in metrics and "error_handling" in metrics and
            metrics["doc_completeness"].status == "critical" and
            metrics["error_handling"].status == "critical"):
            recommendations.append(
                "Critical documentation and error handling issues detected. Consider "
                "improving API documentation and implementing better error handling."
            )
            
        return recommendations
        
    def get_analysis_history(self) -> List[APIResult]:
        """Get analysis history"""
        return self.analysis_history
        
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        if not self.analysis_history:
            return {}
            
        latest = self.analysis_history[-1]
        return {
            "api_type": latest.api_type.value,
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
        
    def get_api_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get registered API patterns"""
        return self.api_patterns
        
    def get_analysis_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get API analysis metrics"""
        return self.analysis_metrics
        
    def register_api_pattern(
        self,
        issue_type: str,
        pattern: str,
        severity: str,
        description: str,
        recommendation: str
    ):
        """Register a new API pattern"""
        if issue_type not in self.api_patterns:
            self.api_patterns[issue_type] = []
            
        self.api_patterns[issue_type].append({
            "pattern": pattern,
            "severity": severity,
            "description": description,
            "recommendation": recommendation
        })
        
    # Metric calculation methods
    def _calculate_endpoint_organization(self, code: str, tree: ast.AST) -> float:
        """Calculate endpoint organization score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_route_handling(self, code: str, tree: ast.AST) -> float:
        """Calculate route handling efficiency score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_versioning(self, code: str, tree: ast.AST) -> float:
        """Calculate API versioning score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_request_validation(self, code: str, tree: ast.AST) -> float:
        """Calculate request validation score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_parameter_handling(self, code: str, tree: ast.AST) -> float:
        """Calculate parameter handling score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_input_sanitization(self, code: str, tree: ast.AST) -> float:
        """Calculate input sanitization score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_response_format(self, code: str, tree: ast.AST) -> float:
        """Calculate response format consistency score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_error_handling(self, code: str, tree: ast.AST) -> float:
        """Calculate error handling score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_status_codes(self, code: str, tree: ast.AST) -> float:
        """Calculate HTTP status code usage score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_doc_completeness(self, code: str, tree: ast.AST) -> float:
        """Calculate documentation completeness score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_doc_quality(self, code: str, tree: ast.AST) -> float:
        """Calculate documentation quality score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_examples(self, code: str, tree: ast.AST) -> float:
        """Calculate example coverage score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_authentication(self, code: str, tree: ast.AST) -> float:
        """Calculate authentication implementation score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_authorization(self, code: str, tree: ast.AST) -> float:
        """Calculate authorization implementation score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_rate_limiting(self, code: str, tree: ast.AST) -> float:
        """Calculate rate limiting implementation score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_response_time(self, code: str, tree: ast.AST) -> float:
        """Calculate response time efficiency score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_caching(self, code: str, tree: ast.AST) -> float:
        """Calculate caching implementation score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_resource_usage(self, code: str, tree: ast.AST) -> float:
        """Calculate resource usage efficiency score"""
        # Implementation depends on the specific requirements
        return 0.8 