from typing import Dict, Any, List, Optional, Set
import logging
from dataclasses import dataclass
from datetime import datetime
import re
from collections import defaultdict
import json
import os

logger = logging.getLogger(__name__)

@dataclass
class RootCause:
    """Identified root cause of an error"""
    cause_type: str
    description: str
    confidence: float
    evidence: List[str]
    suggested_fixes: List[str]
    related_errors: List[str]
    metadata: Dict[str, Any] = None

class RootCauseAnalyzer:
    """Analyzes errors to identify root causes"""
    
    def __init__(self, patterns_file: str = "error_patterns.json"):
        self.patterns_file = patterns_file
        self.cause_patterns = self._load_cause_patterns()
        self.error_history: List[Dict[str, Any]] = []
        self.pattern_weights = self._load_pattern_weights()
        
    def _load_pattern_weights(self) -> Dict[str, float]:
        """Load weights for different pattern matching strategies"""
        return {
            "exact_match": 1.0,
            "partial_match": 0.8,
            "keyword_match": 0.6,
            "context_match": 0.4
        }
        
    def _load_cause_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load patterns for root cause detection"""
        # Try to load from file first
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load patterns from file: {str(e)}")
                
        # Fallback to built-in patterns
        return {
            "resource_exhaustion": [
                {
                    "pattern": r"Memory limit exceeded: (\d+)MB",
                    "confidence": 0.9,
                    "description": "System memory limit exceeded",
                    "fixes": [
                        "Optimize memory usage",
                        "Increase memory limit",
                        "Implement garbage collection"
                    ],
                    "keywords": ["memory", "out of memory", "OOM", "heap"]
                },
                {
                    "pattern": r"CPU usage exceeded (\d+)%",
                    "confidence": 0.8,
                    "description": "CPU usage limit exceeded",
                    "fixes": [
                        "Optimize CPU-intensive operations",
                        "Implement rate limiting",
                        "Add caching"
                    ],
                    "keywords": ["cpu", "processor", "thread", "core"]
                },
                {
                    "pattern": r"Disk space exceeded: (\d+)GB",
                    "confidence": 0.9,
                    "description": "Disk space limit exceeded",
                    "fixes": [
                        "Clean up disk space",
                        "Increase disk quota",
                        "Implement cleanup routines"
                    ],
                    "keywords": ["disk", "storage", "space", "quota"]
                }
            ],
            "dependency_issues": [
                {
                    "pattern": r"No module named '([^']+)'",
                    "confidence": 0.9,
                    "description": "Missing Python dependency",
                    "fixes": [
                        "Install required package",
                        "Update requirements.txt",
                        "Check virtual environment"
                    ],
                    "keywords": ["import", "module", "package", "dependency"]
                },
                {
                    "pattern": r"Failed to connect to ([^:]+):(\d+)",
                    "confidence": 0.8,
                    "description": "External service connection failed",
                    "fixes": [
                        "Check service availability",
                        "Verify network connectivity",
                        "Update service endpoint"
                    ],
                    "keywords": ["connection", "network", "service", "endpoint"]
                },
                {
                    "pattern": r"Version mismatch: ([^:]+) requires ([^:]+)",
                    "confidence": 0.8,
                    "description": "Package version mismatch",
                    "fixes": [
                        "Update package versions",
                        "Check compatibility matrix",
                        "Pin dependency versions"
                    ],
                    "keywords": ["version", "compatibility", "mismatch"]
                }
            ],
            "data_validation": [
                {
                    "pattern": r"invalid literal for ([^:]+): '([^']+)'",
                    "confidence": 0.8,
                    "description": "Invalid data format",
                    "fixes": [
                        "Validate input data",
                        "Handle edge cases",
                        "Add data type conversion"
                    ],
                    "keywords": ["invalid", "format", "type", "conversion"]
                },
                {
                    "pattern": r"Value out of range: (\d+)",
                    "confidence": 0.7,
                    "description": "Value outside expected range",
                    "fixes": [
                        "Add range validation",
                        "Handle boundary conditions",
                        "Update range constraints"
                    ],
                    "keywords": ["range", "boundary", "limit", "constraint"]
                },
                {
                    "pattern": r"Invalid JSON format: ([^:]+)",
                    "confidence": 0.8,
                    "description": "Invalid JSON data",
                    "fixes": [
                        "Validate JSON structure",
                        "Check JSON syntax",
                        "Handle malformed data"
                    ],
                    "keywords": ["json", "format", "syntax", "parse"]
                }
            ],
            "concurrency": [
                {
                    "pattern": r"Deadlock detected",
                    "confidence": 0.9,
                    "description": "Resource deadlock",
                    "fixes": [
                        "Review locking order",
                        "Implement timeout",
                        "Use deadlock detection"
                    ],
                    "keywords": ["deadlock", "lock", "mutex", "synchronization"]
                },
                {
                    "pattern": r"Race condition detected",
                    "confidence": 0.8,
                    "description": "Concurrent access issue",
                    "fixes": [
                        "Add synchronization",
                        "Use atomic operations",
                        "Implement proper locking"
                    ],
                    "keywords": ["race", "concurrent", "thread", "synchronization"]
                },
                {
                    "pattern": r"Timeout waiting for lock",
                    "confidence": 0.7,
                    "description": "Lock acquisition timeout",
                    "fixes": [
                        "Review lock contention",
                        "Implement lock timeouts",
                        "Optimize locking strategy"
                    ],
                    "keywords": ["timeout", "lock", "wait", "contention"]
                }
            ],
            "configuration": [
                {
                    "pattern": r"Configuration error: ([^:]+)",
                    "confidence": 0.9,
                    "description": "Invalid configuration",
                    "fixes": [
                        "Check configuration file",
                        "Validate settings",
                        "Update configuration"
                    ],
                    "keywords": ["config", "settings", "parameter", "option"]
                },
                {
                    "pattern": r"Environment variable ([^=]+) not set",
                    "confidence": 0.8,
                    "description": "Missing environment variable",
                    "fixes": [
                        "Set required environment variable",
                        "Update environment configuration",
                        "Add default values"
                    ],
                    "keywords": ["environment", "variable", "env", "config"]
                },
                {
                    "pattern": r"Invalid configuration value: ([^:]+)",
                    "confidence": 0.8,
                    "description": "Invalid configuration value",
                    "fixes": [
                        "Validate configuration values",
                        "Check value constraints",
                        "Update configuration"
                    ],
                    "keywords": ["config", "value", "invalid", "constraint"]
                }
            ],
            "security": [
                {
                    "pattern": r"Authentication failed: ([^:]+)",
                    "confidence": 0.9,
                    "description": "Authentication failure",
                    "fixes": [
                        "Check credentials",
                        "Verify authentication method",
                        "Update security settings"
                    ],
                    "keywords": ["auth", "login", "credential", "security"]
                },
                {
                    "pattern": r"Permission denied: ([^:]+)",
                    "confidence": 0.8,
                    "description": "Permission error",
                    "fixes": [
                        "Check file permissions",
                        "Verify user rights",
                        "Update access control"
                    ],
                    "keywords": ["permission", "access", "right", "security"]
                },
                {
                    "pattern": r"SSL/TLS error: ([^:]+)",
                    "confidence": 0.8,
                    "description": "SSL/TLS error",
                    "fixes": [
                        "Check SSL certificate",
                        "Verify TLS configuration",
                        "Update security settings"
                    ],
                    "keywords": ["ssl", "tls", "certificate", "security"]
                }
            ],
            "performance": [
                {
                    "pattern": r"Query timeout: ([^:]+)",
                    "confidence": 0.8,
                    "description": "Database query timeout",
                    "fixes": [
                        "Optimize query",
                        "Add indexes",
                        "Implement caching"
                    ],
                    "keywords": ["query", "timeout", "database", "performance"]
                },
                {
                    "pattern": r"Response time exceeded: (\d+)ms",
                    "confidence": 0.7,
                    "description": "Slow response time",
                    "fixes": [
                        "Optimize code path",
                        "Add caching",
                        "Profile performance"
                    ],
                    "keywords": ["response", "time", "slow", "performance"]
                },
                {
                    "pattern": r"Cache miss rate: (\d+)%",
                    "confidence": 0.6,
                    "description": "High cache miss rate",
                    "fixes": [
                        "Optimize cache strategy",
                        "Increase cache size",
                        "Review cache patterns"
                    ],
                    "keywords": ["cache", "miss", "performance", "optimization"]
                }
            ]
        }
        
    def analyze_error(self, error: Exception, context: Dict[str, Any]) -> List[RootCause]:
        """Analyze error to identify root causes
        
        Args:
            error: Exception that occurred
            context: Additional context information
            
        Returns:
            List of identified root causes
        """
        try:
            # Record error in history
            self.error_history.append({
                "timestamp": datetime.now(),
                "error_type": type(error).__name__,
                "message": str(error),
                "context": context
            })
            
            # Analyze error message and context
            causes = []
            error_msg = str(error)
            
            # Check each cause category
            for category, patterns in self.cause_patterns.items():
                for pattern_info in patterns:
                    # Try different matching strategies
                    match = self._match_pattern(error_msg, pattern_info)
                    if match:
                        # Create root cause
                        cause = RootCause(
                            cause_type=category,
                            description=pattern_info["description"],
                            confidence=pattern_info["confidence"] * match["weight"],
                            evidence=[error_msg] + match["evidence"],
                            suggested_fixes=pattern_info["fixes"],
                            related_errors=self._find_related_errors(error_msg, category),
                            metadata={
                                "pattern_match": match["groups"],
                                "context": context,
                                "match_type": match["type"]
                            }
                        )
                        causes.append(cause)
                        
            # Analyze error context for additional evidence
            self._analyze_context(causes, context)
            
            # Sort by confidence
            causes.sort(key=lambda x: x.confidence, reverse=True)
            return causes
            
        except Exception as e:
            logger.error(f"Root cause analysis failed: {str(e)}")
            return []
            
    def _match_pattern(self, error_msg: str, pattern_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Match error message against pattern using multiple strategies
        
        Args:
            error_msg: Error message to match
            pattern_info: Pattern information
            
        Returns:
            Match information if found, None otherwise
        """
        # Try exact pattern match
        match = re.search(pattern_info["pattern"], error_msg)
        if match:
            return {
                "type": "exact_match",
                "weight": self.pattern_weights["exact_match"],
                "groups": match.groups(),
                "evidence": []
            }
            
        # Try partial match
        if any(part in error_msg for part in pattern_info.get("keywords", [])):
            return {
                "type": "partial_match",
                "weight": self.pattern_weights["partial_match"],
                "groups": (),
                "evidence": [f"Found keywords: {', '.join(k for k in pattern_info['keywords'] if k in error_msg)}"]
            }
            
        # Try keyword match
        if any(keyword in error_msg.lower() for keyword in pattern_info.get("keywords", [])):
            return {
                "type": "keyword_match",
                "weight": self.pattern_weights["keyword_match"],
                "groups": (),
                "evidence": [f"Found keywords: {', '.join(k for k in pattern_info['keywords'] if k in error_msg.lower())}"]
            }
            
        return None
        
    def _find_related_errors(self, error_msg: str, category: str) -> List[str]:
        """Find related errors in history
        
        Args:
            error_msg: Current error message
            category: Error category
            
        Returns:
            List of related error messages
        """
        related = []
        for error in self.error_history[-10:]:  # Look at last 10 errors
            if error["error_type"] == category:
                related.append(error["message"])
        return related
        
    def _analyze_context(self, causes: List[RootCause], context: Dict[str, Any]) -> None:
        """Analyze error context for additional evidence
        
        Args:
            causes: List of identified causes
            context: Error context
        """
        # Check system state
        if "system_state" in context:
            system_state = context["system_state"]
            
            # Check resource usage
            if "resource_usage" in system_state:
                usage = system_state["resource_usage"]
                if usage.get("memory", 0) > 90:  # High memory usage
                    self._add_resource_cause(causes, "memory", usage["memory"])
                if usage.get("cpu", 0) > 90:  # High CPU usage
                    self._add_resource_cause(causes, "cpu", usage["cpu"])
                if usage.get("disk", 0) > 90:  # High disk usage
                    self._add_resource_cause(causes, "disk", usage["disk"])
                    
            # Check environment
            if "environment_vars" in system_state:
                env_vars = system_state["environment_vars"]
                missing_vars = [
                    var for var in ["PYTHONPATH", "PATH", "HOME"]
                    if var not in env_vars
                ]
                if missing_vars:
                    self._add_environment_cause(causes, missing_vars)
                    
            # Check security context
            if "security_context" in system_state:
                security = system_state["security_context"]
                if security.get("ssl_errors", []):
                    self._add_security_cause(causes, "ssl", security["ssl_errors"])
                if security.get("auth_failures", []):
                    self._add_security_cause(causes, "auth", security["auth_failures"])
                    
            # Check performance metrics
            if "performance_metrics" in system_state:
                metrics = system_state["performance_metrics"]
                if metrics.get("response_time", 0) > 1000:  # Response time > 1s
                    self._add_performance_cause(causes, "response_time", metrics["response_time"])
                if metrics.get("cache_miss_rate", 0) > 50:  # Cache miss rate > 50%
                    self._add_performance_cause(causes, "cache_miss", metrics["cache_miss_rate"])
                    
        # Check variable state
        if "local_vars" in context:
            local_vars = context["local_vars"]
            null_vars = [
                name for name, value in local_vars.items()
                if value is None
            ]
            if null_vars:
                self._add_validation_cause(causes, "null_variables", null_vars)
                
        # Check database context
        if "db_context" in context:
            db_context = context["db_context"]
            if db_context.get("slow_queries", []):
                self._add_performance_cause(causes, "slow_queries", db_context["slow_queries"])
            if db_context.get("connection_errors", []):
                self._add_dependency_cause(causes, "db_connection", db_context["connection_errors"])
                
    def _add_resource_cause(self, causes: List[RootCause], resource: str, usage: float) -> None:
        """Add resource-related cause
        
        Args:
            causes: List of causes to update
            resource: Resource type
            usage: Usage percentage
        """
        cause = RootCause(
            cause_type="resource_exhaustion",
            description=f"High {resource} usage: {usage}%",
            confidence=0.7,
            evidence=[f"{resource.capitalize()} usage at {usage}%"],
            suggested_fixes=[
                f"Optimize {resource} usage",
                f"Monitor {resource} consumption",
                "Implement resource limits"
            ],
            related_errors=[],
            metadata={"resource": resource, "usage": usage}
        )
        causes.append(cause)
        
    def _add_environment_cause(self, causes: List[RootCause], missing_vars: List[str]) -> None:
        """Add environment-related cause
        
        Args:
            causes: List of causes to update
            missing_vars: List of missing environment variables
        """
        cause = RootCause(
            cause_type="configuration",
            description=f"Missing environment variables: {', '.join(missing_vars)}",
            confidence=0.8,
            evidence=[f"Missing environment variables: {', '.join(missing_vars)}"],
            suggested_fixes=[
                "Set required environment variables",
                "Update environment configuration",
                "Check environment setup"
            ],
            related_errors=[],
            metadata={"missing_vars": missing_vars}
        )
        causes.append(cause)
        
    def _add_validation_cause(self, causes: List[RootCause], issue: str, details: List[str]) -> None:
        """Add validation-related cause
        
        Args:
            causes: List of causes to update
            issue: Type of validation issue
            details: Details about the issue
        """
        cause = RootCause(
            cause_type="data_validation",
            description=f"Validation issue: {issue}",
            confidence=0.7,
            evidence=[f"Found {issue}: {', '.join(details)}"],
            suggested_fixes=[
                "Add input validation",
                "Handle null values",
                "Implement default values"
            ],
            related_errors=[],
            metadata={"issue": issue, "details": details}
        )
        causes.append(cause)
        
    def _add_security_cause(self, causes: List[RootCause], issue_type: str, details: List[str]) -> None:
        """Add security-related cause
        
        Args:
            causes: List of causes to update
            issue_type: Type of security issue
            details: Details about the issue
        """
        cause = RootCause(
            cause_type="security",
            description=f"Security issue: {issue_type}",
            confidence=0.8,
            evidence=[f"Found {issue_type} issues: {', '.join(details)}"],
            suggested_fixes=[
                "Review security settings",
                "Update security configuration",
                "Implement security best practices"
            ],
            related_errors=[],
            metadata={"issue_type": issue_type, "details": details}
        )
        causes.append(cause)
        
    def _add_performance_cause(self, causes: List[RootCause], issue_type: str, details: Any) -> None:
        """Add performance-related cause
        
        Args:
            causes: List of causes to update
            issue_type: Type of performance issue
            details: Details about the issue
        """
        cause = RootCause(
            cause_type="performance",
            description=f"Performance issue: {issue_type}",
            confidence=0.7,
            evidence=[f"Found {issue_type} issues: {str(details)}"],
            suggested_fixes=[
                "Optimize performance",
                "Implement caching",
                "Profile and optimize"
            ],
            related_errors=[],
            metadata={"issue_type": issue_type, "details": details}
        )
        causes.append(cause)
        
    def _add_dependency_cause(self, causes: List[RootCause], issue_type: str, details: List[str]) -> None:
        """Add dependency-related cause
        
        Args:
            causes: List of causes to update
            issue_type: Type of dependency issue
            details: Details about the issue
        """
        cause = RootCause(
            cause_type="dependency_issues",
            description=f"Dependency issue: {issue_type}",
            confidence=0.8,
            evidence=[f"Found {issue_type} issues: {', '.join(details)}"],
            suggested_fixes=[
                "Check service availability",
                "Verify connectivity",
                "Update dependencies"
            ],
            related_errors=[],
            metadata={"issue_type": issue_type, "details": details}
        )
        causes.append(cause)
        
    def get_error_history(self) -> List[Dict[str, Any]]:
        """Get history of analyzed errors
        
        Returns:
            List of error records
        """
        return self.error_history
        
    def clear_history(self) -> None:
        """Clear error history"""
        self.error_history.clear() 