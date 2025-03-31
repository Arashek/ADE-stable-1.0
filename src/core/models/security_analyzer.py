from typing import Dict, List, Optional, Any, Tuple, Set
from pydantic import BaseModel
import ast
import re
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class VulnerabilitySeverity(Enum):
    """Severity levels for security vulnerabilities"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class VulnerabilityType(Enum):
    """Types of security vulnerabilities"""
    INJECTION = "injection"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CRYPTOGRAPHY = "cryptography"
    INPUT_VALIDATION = "input_validation"
    CONFIGURATION = "configuration"
    SENSITIVE_DATA = "sensitive_data"
    ERROR_HANDLING = "error_handling"
    LOGGING = "logging"
    OTHER = "other"

class SecurityType(Enum):
    """Types of security analysis"""
    VULNERABILITY = "vulnerability"
    COMPLIANCE = "compliance"
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"
    ACCESS = "access"

class SecurityMetric(BaseModel):
    """Security metric"""
    name: str
    value: float
    threshold: float
    status: str
    details: Dict[str, Any] = {}
    recommendations: List[str] = []

class SecurityResult(BaseModel):
    """Result of security analysis"""
    security_type: SecurityType
    metrics: Dict[str, SecurityMetric]
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = {}

@dataclass
class Vulnerability:
    """Information about a security vulnerability"""
    type: VulnerabilityType
    severity: VulnerabilitySeverity
    description: str
    line_number: int
    column: int
    code_snippet: str
    recommendation: str
    cwe_id: Optional[str] = None
    metadata: Dict[str, Any] = None

class SecurityAnalysisResult(BaseModel):
    """Result of security analysis"""
    vulnerabilities: List[Vulnerability]
    risk_score: float
    metrics: Dict[str, float]
    recommendations: List[str]
    metadata: Dict[str, Any] = {}

class SecurityAnalyzer:
    """Analyzer for code security and compliance"""
    
    def __init__(self):
        self.vulnerability_patterns: Dict[VulnerabilityType, List[Dict[str, Any]]] = {}
        self.analysis_metrics: Dict[str, Dict[str, float]] = {}
        self.analysis_history: List[SecurityResult] = []
        self._initialize_patterns()
        self._initialize_security_rules()
        
    def _initialize_patterns(self):
        """Initialize vulnerability detection patterns"""
        # SQL Injection patterns
        self.vulnerability_patterns[VulnerabilityType.INJECTION] = [
            {
                "pattern": r"\+.*?\+.*?sql",
                "severity": VulnerabilitySeverity.CRITICAL,
                "description": "SQL injection vulnerability detected",
                "recommendation": "Use parameterized queries or an ORM"
            },
            {
                "pattern": r"execute\(.*?\+.*?\)",
                "severity": VulnerabilitySeverity.CRITICAL,
                "description": "SQL injection vulnerability in execute() call",
                "recommendation": "Use parameterized queries"
            }
        ]
        
        # Command Injection patterns
        self.vulnerability_patterns[VulnerabilityType.INJECTION].extend([
            {
                "pattern": r"os\.system|subprocess\.call",
                "severity": VulnerabilitySeverity.HIGH,
                "description": "Command injection vulnerability detected",
                "recommendation": "Use subprocess.run with shell=False and list arguments"
            }
        ])
        
        # Authentication patterns
        self.vulnerability_patterns[VulnerabilityType.AUTHENTICATION] = [
            {
                "pattern": r"password\s*=\s*[\'"][^\'"]+[\'"]",
                "severity": VulnerabilitySeverity.CRITICAL,
                "description": "Hardcoded password detected",
                "recommendation": "Use environment variables or secure secret management"
            }
        ]
        
        # Cryptography patterns
        self.vulnerability_patterns[VulnerabilityType.CRYPTOGRAPHY] = [
            {
                "pattern": r"md5\(|sha1\(",
                "severity": VulnerabilitySeverity.HIGH,
                "description": "Weak cryptographic hash function detected",
                "recommendation": "Use strong cryptographic hash functions (e.g., SHA-256)"
            }
        ]
        
        # Input Validation patterns
        self.vulnerability_patterns[VulnerabilityType.INPUT_VALIDATION] = [
            {
                "pattern": r"eval\(|exec\(",
                "severity": VulnerabilitySeverity.CRITICAL,
                "description": "Unsafe code execution detected",
                "recommendation": "Avoid using eval() or exec() with user input"
            }
        ]
        
    def _initialize_security_rules(self):
        """Initialize security rules"""
        self.security_rules = {
            SecurityType.VULNERABILITY: [
                {
                    "name": "sql_injection",
                    "threshold": 0.0,
                    "description": "SQL injection vulnerability score",
                    "pattern": r"(?i)(execute|exec|query|raw|sql)\s*\([\"'].*?[\"']\)"
                },
                {
                    "name": "xss_vulnerability",
                    "threshold": 0.0,
                    "description": "XSS vulnerability score",
                    "pattern": r"(?i)(innerHTML|outerHTML|document\.write)\s*\([\"'].*?[\"']\)"
                },
                {
                    "name": "command_injection",
                    "threshold": 0.0,
                    "description": "Command injection vulnerability score",
                    "pattern": r"(?i)(os\.system|subprocess\.call|subprocess\.Popen)\s*\([\"'].*?[\"']\)"
                }
            ],
            SecurityType.COMPLIANCE: [
                {
                    "name": "gdpr_compliance",
                    "threshold": 0.8,
                    "description": "GDPR compliance score"
                },
                {
                    "name": "hipaa_compliance",
                    "threshold": 0.8,
                    "description": "HIPAA compliance score"
                },
                {
                    "name": "pci_compliance",
                    "threshold": 0.8,
                    "description": "PCI compliance score"
                }
            ],
            SecurityType.DEPENDENCY: [
                {
                    "name": "vulnerable_dependencies",
                    "threshold": 0.0,
                    "description": "Number of vulnerable dependencies"
                },
                {
                    "name": "outdated_packages",
                    "threshold": 0.2,
                    "description": "Ratio of outdated packages"
                },
                {
                    "name": "license_compliance",
                    "threshold": 0.9,
                    "description": "License compliance score"
                }
            ],
            SecurityType.CONFIGURATION: [
                {
                    "name": "secure_config",
                    "threshold": 0.8,
                    "description": "Secure configuration score"
                },
                {
                    "name": "secret_management",
                    "threshold": 0.9,
                    "description": "Secret management score"
                },
                {
                    "name": "encryption_usage",
                    "threshold": 0.8,
                    "description": "Encryption usage score"
                }
            ],
            SecurityType.ACCESS: [
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
                    "name": "session_management",
                    "threshold": 0.8,
                    "description": "Session management score"
                }
            ]
        }
        
    def analyze_security(
        self,
        code: str,
        file_path: str,
        security_type: SecurityType,
        context: Optional[Dict[str, Any]] = None
    ) -> SecurityResult:
        """Analyze code security based on specified type"""
        try:
            # Initialize result
            result = SecurityResult(
                security_type=security_type,
                metrics={},
                issues=[],
                recommendations=[],
                metadata={
                    "analyzed_at": datetime.now().isoformat(),
                    "file_path": file_path,
                    "context": context or {}
                }
            )
            
            # Get security rules for type
            rules = self.security_rules.get(security_type, [])
            
            # Parse code
            tree = ast.parse(code)
            
            # Perform analysis
            for rule in rules:
                metric = self._analyze_security_metric(
                    rule["name"],
                    code,
                    tree,
                    rule["threshold"],
                    rule.get("pattern"),
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
            raise ValueError(f"Failed to analyze security: {str(e)}")
            
    def _analyze_security_metric(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        threshold: float,
        pattern: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> SecurityMetric:
        """Analyze specific security metric"""
        try:
            # Calculate metric value
            value = self._calculate_metric_value(
                metric_name,
                code,
                tree,
                pattern,
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
            
            return SecurityMetric(
                name=metric_name,
                value=value,
                threshold=threshold,
                status=status,
                details={
                    "code": code,
                    "pattern": pattern,
                    "context": context
                },
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze security metric {metric_name}: {str(e)}")
            return SecurityMetric(
                name=metric_name,
                value=0.0,
                threshold=threshold,
                status="error",
                details={"error": str(e)},
                recommendations=["Fix security analysis error"]
            )
            
    def _calculate_metric_value(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        pattern: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate metric value"""
        if pattern:
            # Pattern-based metrics
            matches = re.finditer(pattern, code)
            match_count = sum(1 for _ in matches)
            return 1.0 if match_count == 0 else 0.0
            
        elif metric_name == "gdpr_compliance":
            return self._calculate_gdpr_compliance(code, tree)
        elif metric_name == "hipaa_compliance":
            return self._calculate_hipaa_compliance(code, tree)
        elif metric_name == "pci_compliance":
            return self._calculate_pci_compliance(code, tree)
        elif metric_name == "vulnerable_dependencies":
            return self._calculate_vulnerable_dependencies(context)
        elif metric_name == "outdated_packages":
            return self._calculate_outdated_packages(context)
        elif metric_name == "license_compliance":
            return self._calculate_license_compliance(context)
        elif metric_name == "secure_config":
            return self._calculate_secure_config(code, tree)
        elif metric_name == "secret_management":
            return self._calculate_secret_management(code, tree)
        elif metric_name == "encryption_usage":
            return self._calculate_encryption_usage(code, tree)
        elif metric_name == "authentication":
            return self._calculate_authentication(code, tree)
        elif metric_name == "authorization":
            return self._calculate_authorization(code, tree)
        elif metric_name == "session_management":
            return self._calculate_session_management(code, tree)
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
                f"security measures."
            )
        elif status == "critical":
            recommendations.append(
                f"{metric_name} is significantly below threshold. Immediate "
                f"security improvements are recommended."
            )
            
        # Add specific recommendations based on metric
        if "injection" in metric_name and value < threshold:
            recommendations.append(
                "Potential injection vulnerability detected. Consider using "
                "parameterized queries and input validation."
            )
        elif "compliance" in metric_name and value < threshold:
            recommendations.append(
                "Compliance requirements not fully met. Review and implement "
                "necessary security controls."
            )
        elif "dependency" in metric_name and value > threshold:
            recommendations.append(
                "Security issues found in dependencies. Update packages and "
                "review third-party code."
            )
            
        return recommendations
        
    def _generate_cross_metric_recommendations(
        self,
        metrics: Dict[str, SecurityMetric]
    ) -> List[str]:
        """Generate recommendations based on multiple metrics"""
        recommendations = []
        
        # Check for multiple vulnerabilities
        vulnerability_metrics = [
            m for n, m in metrics.items()
            if any(v in n for v in ["injection", "vulnerability"])
        ]
        if len(vulnerability_metrics) > 1 and all(m.status == "critical" for m in vulnerability_metrics):
            recommendations.append(
                "Multiple critical vulnerabilities detected. Consider comprehensive "
                "security audit and remediation."
            )
            
        # Check for compliance issues
        compliance_metrics = [
            m for n, m in metrics.items()
            if "compliance" in n
        ]
        if compliance_metrics and all(m.status != "good" for m in compliance_metrics):
            recommendations.append(
                "Multiple compliance issues detected. Review and update security "
                "controls to meet requirements."
            )
            
        # Check for configuration issues
        if ("secure_config" in metrics and "secret_management" in metrics and
            metrics["secure_config"].status == "critical" and
            metrics["secret_management"].status == "critical"):
            recommendations.append(
                "Critical configuration and secret management issues detected. "
                "Review security settings and implement proper secret handling."
            )
            
        return recommendations
        
    def get_analysis_history(self) -> List[SecurityResult]:
        """Get analysis history"""
        return self.analysis_history
        
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        if not self.analysis_history:
            return {}
            
        latest = self.analysis_history[-1]
        return {
            "security_type": latest.security_type.value,
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
        
    def analyze_code(self, code: str) -> SecurityAnalysisResult:
        """Analyze code for security vulnerabilities"""
        try:
            # Parse code into AST
            tree = ast.parse(code)
            
            # Find vulnerabilities
            vulnerabilities = self._find_vulnerabilities(tree, code)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(vulnerabilities)
            
            # Calculate metrics
            metrics = self._calculate_metrics(vulnerabilities)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(vulnerabilities)
            
            return SecurityAnalysisResult(
                vulnerabilities=vulnerabilities,
                risk_score=risk_score,
                metrics=metrics,
                recommendations=recommendations,
                metadata={
                    "analyzed_at": datetime.now().isoformat(),
                    "total_vulnerabilities": len(vulnerabilities)
                }
            )
        except Exception as e:
            raise ValueError(f"Failed to analyze code: {str(e)}")
            
    def _find_vulnerabilities(self, tree: ast.AST, code: str) -> List[Vulnerability]:
        """Find security vulnerabilities in code"""
        vulnerabilities = []
        
        # Check for pattern-based vulnerabilities
        for vuln_type, patterns in self.vulnerability_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern["pattern"], code)
                for match in matches:
                    line_number = code[:match.start()].count('\n') + 1
                    column = match.start() - code.rfind('\n', 0, match.start())
                    code_snippet = self._get_code_snippet(code, line_number)
                    
                    vulnerability = Vulnerability(
                        type=vuln_type,
                        severity=pattern["severity"],
                        description=pattern["description"],
                        line_number=line_number,
                        column=column,
                        code_snippet=code_snippet,
                        recommendation=pattern["recommendation"]
                    )
                    vulnerabilities.append(vulnerability)
                    
        # Check for AST-based vulnerabilities
        vulnerabilities.extend(self._find_ast_vulnerabilities(tree, code))
        
        return vulnerabilities
        
    def _find_ast_vulnerabilities(self, tree: ast.AST, code: str) -> List[Vulnerability]:
        """Find vulnerabilities using AST analysis"""
        vulnerabilities = []
        
        class SecurityVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                # Check for unsafe function calls
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        vulnerabilities.append(Vulnerability(
                            type=VulnerabilityType.INPUT_VALIDATION,
                            severity=VulnerabilitySeverity.CRITICAL,
                            description="Unsafe code execution detected",
                            line_number=node.lineno,
                            column=node.col_offset,
                            code_snippet=self._get_code_snippet(code, node.lineno),
                            recommendation="Avoid using eval() or exec() with user input"
                        ))
                        
            def visit_Assign(self, node):
                # Check for hardcoded secrets
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id.lower().endswith(('password', 'secret', 'key')):
                            vulnerabilities.append(Vulnerability(
                                type=VulnerabilityType.SENSITIVE_DATA,
                                severity=VulnerabilitySeverity.HIGH,
                                description="Potential hardcoded secret detected",
                                line_number=node.lineno,
                                column=node.col_offset,
                                code_snippet=self._get_code_snippet(code, node.lineno),
                                recommendation="Use environment variables or secure secret management"
                            ))
                            
        visitor = SecurityVisitor()
        visitor.visit(tree)
        return vulnerabilities
        
    def _get_code_snippet(self, code: str, line_number: int, context_lines: int = 2) -> str:
        """Get code snippet around a specific line"""
        lines = code.split('\n')
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        return '\n'.join(lines[start:end])
        
    def _calculate_risk_score(self, vulnerabilities: List[Vulnerability]) -> float:
        """Calculate overall risk score"""
        if not vulnerabilities:
            return 0.0
            
        severity_weights = {
            VulnerabilitySeverity.CRITICAL: 1.0,
            VulnerabilitySeverity.HIGH: 0.8,
            VulnerabilitySeverity.MEDIUM: 0.6,
            VulnerabilitySeverity.LOW: 0.4,
            VulnerabilitySeverity.INFO: 0.2
        }
        
        total_weight = sum(severity_weights[v.severity] for v in vulnerabilities)
        return min(total_weight / len(vulnerabilities), 1.0)
        
    def _calculate_metrics(self, vulnerabilities: List[Vulnerability]) -> Dict[str, float]:
        """Calculate security metrics"""
        metrics = {
            'vulnerability_count': len(vulnerabilities),
            'critical_count': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0,
            'info_count': 0,
            'injection_count': 0,
            'auth_count': 0,
            'crypto_count': 0,
            'validation_count': 0
        }
        
        for vuln in vulnerabilities:
            metrics[f'{vuln.severity.value}_count'] += 1
            metrics[f'{vuln.type.value}_count'] += 1
            
        return metrics
        
    def _generate_recommendations(self, vulnerabilities: List[Vulnerability]) -> List[str]:
        """Generate security recommendations"""
        recommendations = set()
        
        # Add specific recommendations for each vulnerability
        for vuln in vulnerabilities:
            recommendations.add(vuln.recommendation)
            
        # Add general recommendations based on vulnerability types
        vuln_types = {v.type for v in vulnerabilities}
        
        if VulnerabilityType.INJECTION in vuln_types:
            recommendations.add("Implement proper input validation and sanitization")
            
        if VulnerabilityType.AUTHENTICATION in vuln_types:
            recommendations.add("Review authentication mechanisms and password handling")
            
        if VulnerabilityType.CRYPTOGRAPHY in vuln_types:
            recommendations.add("Use strong cryptographic algorithms and proper key management")
            
        if VulnerabilityType.INPUT_VALIDATION in vuln_types:
            recommendations.add("Implement comprehensive input validation")
            
        return list(recommendations)
        
    def register_vulnerability_pattern(
        self,
        vuln_type: VulnerabilityType,
        pattern: str,
        severity: VulnerabilitySeverity,
        description: str,
        recommendation: str
    ):
        """Register a new vulnerability pattern"""
        if vuln_type not in self.vulnerability_patterns:
            self.vulnerability_patterns[vuln_type] = []
            
        self.vulnerability_patterns[vuln_type].append({
            "pattern": pattern,
            "severity": severity,
            "description": description,
            "recommendation": recommendation
        })
        
    def get_vulnerability_patterns(self) -> Dict[VulnerabilityType, List[Dict[str, Any]]]:
        """Get registered vulnerability patterns"""
        return self.vulnerability_patterns
        
    def get_analysis_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get security analysis metrics"""
        return self.analysis_metrics 