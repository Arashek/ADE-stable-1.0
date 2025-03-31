from typing import Dict, List, Optional, Any
import re
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ErrorClassification:
    """Represents the classification of an error."""
    category: str
    subcategory: str
    severity: str
    impact_level: str
    confidence: float
    patterns: List[str]
    context: Dict[str, Any]
    timestamp: datetime

class ErrorClassifier:
    """Classifies errors based on their characteristics and patterns."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_categories()
        self._initialize_severity_levels()
        self._initialize_impact_levels()
    
    def _initialize_categories(self):
        """Initialize error categories and their patterns."""
        self.categories = {
            "runtime": {
                "patterns": [
                    r"TypeError:.*",
                    r"ValueError:.*",
                    r"IndexError:.*",
                    r"KeyError:.*",
                    r"AttributeError:.*",
                    r"NameError:.*",
                    r"ZeroDivisionError:.*",
                    r"OverflowError:.*",
                    r"RecursionError:.*",
                    r"StopIteration:.*",
                    r"GeneratorExit:.*",
                    r"RuntimeError:.*"
                ],
                "subcategories": {
                    "type_error": ["TypeError"],
                    "value_error": ["ValueError"],
                    "index_error": ["IndexError"],
                    "key_error": ["KeyError"],
                    "attribute_error": ["AttributeError"],
                    "name_error": ["NameError"],
                    "division_error": ["ZeroDivisionError"],
                    "overflow_error": ["OverflowError"],
                    "recursion_error": ["RecursionError"],
                    "iteration_error": ["StopIteration"],
                    "generator_error": ["GeneratorExit"],
                    "general_runtime": ["RuntimeError"]
                }
            },
            "system": {
                "patterns": [
                    r"OSError:.*",
                    r"IOError:.*",
                    r"FileNotFoundError:.*",
                    r"PermissionError:.*",
                    r"ProcessLookupError:.*",
                    r"InterruptedError:.*",
                    r"BlockingIOError:.*",
                    r"ChildProcessError:.*",
                    r"ConnectionError:.*",
                    r"BrokenPipeError:.*",
                    r"ConnectionAbortedError:.*",
                    r"ConnectionRefusedError:.*",
                    r"ConnectionResetError:.*"
                ],
                "subcategories": {
                    "os_error": ["OSError"],
                    "io_error": ["IOError"],
                    "file_error": ["FileNotFoundError"],
                    "permission_error": ["PermissionError"],
                    "process_error": ["ProcessLookupError"],
                    "interrupt_error": ["InterruptedError"],
                    "blocking_error": ["BlockingIOError"],
                    "child_process_error": ["ChildProcessError"],
                    "connection_error": ["ConnectionError"],
                    "pipe_error": ["BrokenPipeError"],
                    "connection_aborted": ["ConnectionAbortedError"],
                    "connection_refused": ["ConnectionRefusedError"],
                    "connection_reset": ["ConnectionResetError"]
                }
            },
            "database": {
                "patterns": [
                    r"DatabaseError:.*",
                    r"SQL.*Error:.*",
                    r"ConnectionError:.*",
                    r"TransactionError:.*",
                    r"IntegrityError:.*",
                    r"OperationalError:.*",
                    r"ProgrammingError:.*",
                    r"NotSupportedError:.*",
                    r"DataError:.*",
                    r"InterfaceError:.*",
                    r"InternalError:.*"
                ],
                "subcategories": {
                    "connection_error": ["ConnectionError"],
                    "query_error": ["SQL.*Error"],
                    "transaction_error": ["TransactionError"],
                    "integrity_error": ["IntegrityError"],
                    "operational_error": ["OperationalError"],
                    "programming_error": ["ProgrammingError"],
                    "not_supported_error": ["NotSupportedError"],
                    "data_error": ["DataError"],
                    "interface_error": ["InterfaceError"],
                    "internal_error": ["InternalError"]
                }
            },
            "network": {
                "patterns": [
                    r"NetworkError:.*",
                    r"ConnectionError:.*",
                    r"TimeoutError:.*",
                    r"HTTPError:.*",
                    r"URLError:.*",
                    r"SSLError:.*",
                    r"ProxyError:.*",
                    r"DNSLookupError:.*",
                    r"SocketError:.*",
                    r"WebSocketError:.*",
                    r"RESTError:.*",
                    r"APIError:.*"
                ],
                "subcategories": {
                    "connection_error": ["ConnectionError"],
                    "timeout_error": ["TimeoutError"],
                    "http_error": ["HTTPError"],
                    "url_error": ["URLError"],
                    "ssl_error": ["SSLError"],
                    "proxy_error": ["ProxyError"],
                    "dns_error": ["DNSLookupError"],
                    "socket_error": ["SocketError"],
                    "websocket_error": ["WebSocketError"],
                    "rest_error": ["RESTError"],
                    "api_error": ["APIError"]
                }
            },
            "security": {
                "patterns": [
                    r"SecurityError:.*",
                    r"AuthenticationError:.*",
                    r"AuthorizationError:.*",
                    r"ValidationError:.*",
                    r"EncryptionError:.*",
                    r"DecryptionError:.*",
                    r"HashError:.*",
                    r"CertificateError:.*",
                    r"TokenError:.*",
                    r"SignatureError:.*",
                    r"AccessControlError:.*",
                    r"AuditError:.*"
                ],
                "subcategories": {
                    "auth_error": ["AuthenticationError"],
                    "authz_error": ["AuthorizationError"],
                    "validation_error": ["ValidationError"],
                    "encryption_error": ["EncryptionError"],
                    "decryption_error": ["DecryptionError"],
                    "hash_error": ["HashError"],
                    "certificate_error": ["CertificateError"],
                    "token_error": ["TokenError"],
                    "signature_error": ["SignatureError"],
                    "access_control_error": ["AccessControlError"],
                    "audit_error": ["AuditError"]
                }
            },
            "performance": {
                "patterns": [
                    r"PerformanceError:.*",
                    r"TimeoutError:.*",
                    r"ResourceExhaustedError:.*",
                    r"MemoryError:.*",
                    r"CPUError:.*",
                    r"DiskError:.*",
                    r"NetworkLatencyError:.*",
                    r"ConcurrencyError:.*",
                    r"DeadlockError:.*",
                    r"ThrottlingError:.*",
                    r"RateLimitError:.*",
                    r"LoadError:.*"
                ],
                "subcategories": {
                    "timeout_error": ["TimeoutError"],
                    "resource_error": ["ResourceExhaustedError"],
                    "memory_error": ["MemoryError"],
                    "cpu_error": ["CPUError"],
                    "disk_error": ["DiskError"],
                    "latency_error": ["NetworkLatencyError"],
                    "concurrency_error": ["ConcurrencyError"],
                    "deadlock_error": ["DeadlockError"],
                    "throttling_error": ["ThrottlingError"],
                    "rate_limit_error": ["RateLimitError"],
                    "load_error": ["LoadError"]
                }
            },
            "data": {
                "patterns": [
                    r"DataError:.*",
                    r"FormatError:.*",
                    r"EncodingError:.*",
                    r"DecodingError:.*",
                    r"SerializationError:.*",
                    r"DeserializationError:.*",
                    r"SchemaError:.*",
                    r"ValidationError:.*",
                    r"IntegrityError:.*",
                    r"ConsistencyError:.*",
                    r"DataCorruptionError:.*",
                    r"DataLossError:.*"
                ],
                "subcategories": {
                    "format_error": ["FormatError"],
                    "encoding_error": ["EncodingError"],
                    "decoding_error": ["DecodingError"],
                    "serialization_error": ["SerializationError"],
                    "deserialization_error": ["DeserializationError"],
                    "schema_error": ["SchemaError"],
                    "validation_error": ["ValidationError"],
                    "integrity_error": ["IntegrityError"],
                    "consistency_error": ["ConsistencyError"],
                    "corruption_error": ["DataCorruptionError"],
                    "loss_error": ["DataLossError"]
                }
            },
            "infrastructure": {
                "patterns": [
                    r"InfrastructureError:.*",
                    r"DeploymentError:.*",
                    r"ConfigurationError:.*",
                    r"EnvironmentError:.*",
                    r"ServiceError:.*",
                    r"ClusterError:.*",
                    r"ContainerError:.*",
                    r"OrchestrationError:.*",
                    r"ScalingError:.*",
                    r"ProvisioningError:.*",
                    r"MaintenanceError:.*",
                    r"InfrastructureFailureError:.*"
                ],
                "subcategories": {
                    "deployment_error": ["DeploymentError"],
                    "configuration_error": ["ConfigurationError"],
                    "environment_error": ["EnvironmentError"],
                    "service_error": ["ServiceError"],
                    "cluster_error": ["ClusterError"],
                    "container_error": ["ContainerError"],
                    "orchestration_error": ["OrchestrationError"],
                    "scaling_error": ["ScalingError"],
                    "provisioning_error": ["ProvisioningError"],
                    "maintenance_error": ["MaintenanceError"],
                    "failure_error": ["InfrastructureFailureError"]
                }
            }
        }
    
    def _initialize_severity_levels(self):
        """Initialize severity levels and their criteria."""
        self.severity_levels = {
            "critical": {
                "criteria": [
                    "data_loss",
                    "security_breach",
                    "system_crash",
                    "service_outage"
                ],
                "threshold": 0.9
            },
            "high": {
                "criteria": [
                    "performance_degradation",
                    "partial_outage",
                    "data_corruption",
                    "security_vulnerability"
                ],
                "threshold": 0.7
            },
            "medium": {
                "criteria": [
                    "reduced_functionality",
                    "increased_latency",
                    "resource_warning",
                    "validation_failure"
                ],
                "threshold": 0.5
            },
            "low": {
                "criteria": [
                    "non_critical_failure",
                    "minor_issue",
                    "cosmetic_problem",
                    "informational"
                ],
                "threshold": 0.3
            }
        }
    
    def _initialize_impact_levels(self):
        """Initialize impact levels and their criteria."""
        self.impact_levels = {
            "system_wide": {
                "criteria": ["affects_all_users", "core_functionality", "data_integrity"],
                "weight": 1.0
            },
            "service_level": {
                "criteria": ["affects_specific_service", "partial_functionality", "performance_impact"],
                "weight": 0.8
            },
            "user_level": {
                "criteria": ["affects_specific_users", "non_critical_functionality", "minor_impact"],
                "weight": 0.6
            },
            "component_level": {
                "criteria": ["affects_single_component", "auxiliary_functionality", "minimal_impact"],
                "weight": 0.4
            }
        }
    
    def classify_error(self, error_message: str, stack_trace: Optional[List[str]] = None, 
                      context: Optional[Dict[str, Any]] = None) -> ErrorClassification:
        """Classify an error based on its message, stack trace, and context."""
        # Initialize context if None
        context = context or {}
        
        # Detect category and subcategory
        category, subcategory, patterns = self._detect_category(error_message)
        
        # Determine severity
        severity = self._determine_severity(error_message, stack_trace, context)
        
        # Determine impact level
        impact_level = self._determine_impact(error_message, stack_trace, context)
        
        # Calculate confidence
        confidence = self._calculate_confidence(error_message, patterns, context)
        
        return ErrorClassification(
            category=category,
            subcategory=subcategory,
            severity=severity,
            impact_level=impact_level,
            confidence=confidence,
            patterns=patterns,
            context=context,
            timestamp=datetime.now()
        )
    
    def _detect_category(self, error_message: str) -> tuple[str, str, List[str]]:
        """Detect the category and subcategory of an error."""
        matched_patterns = []
        
        for category, info in self.categories.items():
            for pattern in info["patterns"]:
                if re.match(pattern, error_message):
                    matched_patterns.append(pattern)
                    # Find matching subcategory
                    for subcategory, subpatterns in info["subcategories"].items():
                        if any(re.match(p, error_message) for p in subpatterns):
                            return category, subcategory, matched_patterns
        
        return "unknown", "unknown", matched_patterns
    
    def _determine_severity(self, error_message: str, stack_trace: Optional[List[str]], 
                          context: Dict[str, Any]) -> str:
        """Determine the severity level of an error."""
        severity_score = 0.0
        
        # Check error message against severity criteria
        for level, info in self.severity_levels.items():
            for criterion in info["criteria"]:
                if criterion in error_message.lower():
                    severity_score = max(severity_score, info["threshold"])
        
        # Adjust severity based on stack trace
        if stack_trace:
            if len(stack_trace) > 10:  # Deep stack trace
                severity_score += 0.1
            if any("main" in line.lower() for line in stack_trace):
                severity_score += 0.1
        
        # Adjust severity based on context
        if context:
            if context.get("affects_all_users", False):
                severity_score += 0.2
            if context.get("data_loss", False):
                severity_score += 0.3
        
        # Determine final severity level
        for level, info in sorted(self.severity_levels.items(), 
                                key=lambda x: x[1]["threshold"], reverse=True):
            if severity_score >= info["threshold"]:
                return level
        
        return "low"
    
    def _determine_impact(self, error_message: str, stack_trace: Optional[List[str]], 
                         context: Dict[str, Any]) -> str:
        """Determine the impact level of an error."""
        impact_score = 0.0
        
        # Check error message against impact criteria
        for level, info in self.impact_levels.items():
            for criterion in info["criteria"]:
                if criterion in error_message.lower():
                    impact_score = max(impact_score, info["weight"])
        
        # Adjust impact based on context
        if context:
            if context.get("user_count", 0) > 1000:
                impact_score += 0.2
            if context.get("revenue_impact", False):
                impact_score += 0.3
        
        # Determine final impact level
        for level, info in sorted(self.impact_levels.items(), 
                                key=lambda x: x[1]["weight"], reverse=True):
            if impact_score >= info["weight"]:
                return level
        
        return "component_level"
    
    def _calculate_confidence(self, error_message: str, patterns: List[str], 
                            context: Dict[str, Any]) -> float:
        """Calculate the confidence score for the classification."""
        confidence = 0.0
        
        # Base confidence from pattern matching
        if patterns:
            confidence += 0.4
        
        # Additional confidence from context
        if context:
            if context.get("error_count", 0) > 1:
                confidence += 0.2
            if context.get("reproducible", False):
                confidence += 0.2
            if context.get("consistent_pattern", False):
                confidence += 0.2
        
        return min(confidence, 1.0)
    
    def get_classification_statistics(self) -> Dict[str, Any]:
        """Get statistics about error classifications."""
        return {
            "categories": {
                category: {
                    "subcategories": info["subcategories"],
                    "pattern_count": len(info["patterns"])
                }
                for category, info in self.categories.items()
            },
            "severity_levels": {
                level: {
                    "criteria": info["criteria"],
                    "threshold": info["threshold"]
                }
                for level, info in self.severity_levels.items()
            },
            "impact_levels": {
                level: {
                    "criteria": info["criteria"],
                    "weight": info["weight"]
                }
                for level, info in self.impact_levels.items()
            }
        } 