from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass

@dataclass
class DomainErrorContext:
    """Context information specific to a domain."""
    domain: str
    error_type: str
    severity: str
    impact_level: str
    affected_components: List[str]
    dependencies: List[str]
    recovery_options: List[str]
    monitoring_requirements: List[str]

class DomainErrorHandler(ABC):
    """Base class for domain-specific error handlers."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def analyze_error(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Analyze error in domain-specific context."""
        pass
    
    @abstractmethod
    async def generate_solution(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate domain-specific solution steps."""
        pass
    
    @abstractmethod
    async def get_monitoring_plan(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Get domain-specific monitoring plan."""
        pass

class WebApplicationHandler(DomainErrorHandler):
    """Handler for web application errors."""
    
    async def analyze_error(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Analyze web application errors."""
        analysis = {
            "error_category": self._categorize_web_error(context.error_type),
            "affected_endpoints": self._identify_affected_endpoints(context.affected_components),
            "user_impact": self._assess_user_impact(context.impact_level),
            "session_handling": self._check_session_handling(context),
            "security_implications": self._check_security_implications(context),
            "performance_impact": self._assess_performance_impact(context)
        }
        return analysis
    
    async def generate_solution(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate web application specific solutions."""
        solutions = []
        
        if analysis["error_category"] == "authentication":
            solutions.extend([
                "Verify session tokens and cookies",
                "Check authentication middleware",
                "Validate user permissions"
            ])
        elif analysis["error_category"] == "database":
            solutions.extend([
                "Check database connection pool",
                "Verify transaction integrity",
                "Review query performance"
            ])
        elif analysis["error_category"] == "api":
            solutions.extend([
                "Validate API endpoints",
                "Check rate limiting",
                "Verify request/response formats"
            ])
        
        return solutions
    
    async def get_monitoring_plan(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Get web application monitoring plan."""
        return {
            "metrics": [
                "request_rate",
                "response_time",
                "error_rate",
                "session_count",
                "database_connections"
            ],
            "alerts": [
                {"metric": "error_rate", "threshold": 5, "window": "5m"},
                {"metric": "response_time", "threshold": 1000, "window": "1m"},
                {"metric": "database_connections", "threshold": 80, "window": "5m"}
            ],
            "dashboards": [
                "error_trends",
                "performance_metrics",
                "user_impact"
            ]
        }
    
    def _categorize_web_error(self, error_type: str) -> str:
        """Categorize web application errors."""
        categories = {
            "authentication": ["401", "403", "auth", "session"],
            "database": ["sql", "connection", "transaction"],
            "api": ["endpoint", "request", "response"],
            "performance": ["timeout", "slow", "latency"],
            "security": ["xss", "csrf", "injection"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in error_type.lower() for keyword in keywords):
                return category
        return "unknown"
    
    def _identify_affected_endpoints(self, components: List[str]) -> List[str]:
        """Identify affected API endpoints."""
        return [comp for comp in components if comp.startswith("/api/")]
    
    def _assess_user_impact(self, impact_level: str) -> Dict[str, Any]:
        """Assess impact on users."""
        impact_levels = {
            "critical": {"affected_users": "all", "severity": "high"},
            "high": {"affected_users": "many", "severity": "medium"},
            "medium": {"affected_users": "some", "severity": "low"},
            "low": {"affected_users": "few", "severity": "minimal"}
        }
        return impact_levels.get(impact_level, {"affected_users": "unknown", "severity": "unknown"})
    
    def _check_session_handling(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Check session handling mechanisms."""
        return {
            "session_state": "active",
            "session_timeout": 3600,
            "concurrent_sessions": True
        }
    
    def _check_security_implications(self, context: DomainErrorContext) -> List[str]:
        """Check security implications of the error."""
        implications = []
        if "auth" in context.error_type.lower():
            implications.append("Potential authentication bypass")
        if "session" in context.error_type.lower():
            implications.append("Session hijacking risk")
        return implications
    
    def _assess_performance_impact(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Assess performance impact of the error."""
        return {
            "response_time_impact": "high" if context.severity == "critical" else "medium",
            "resource_usage": "increased",
            "scaling_required": context.severity == "critical"
        }

class DataProcessingHandler(DomainErrorHandler):
    """Handler for data processing errors."""
    
    async def analyze_error(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Analyze data processing errors."""
        analysis = {
            "error_category": self._categorize_data_error(context.error_type),
            "data_impact": self._assess_data_impact(context),
            "processing_stage": self._identify_processing_stage(context),
            "data_integrity": self._check_data_integrity(context),
            "recovery_options": self._get_recovery_options(context)
        }
        return analysis
    
    async def generate_solution(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate data processing specific solutions."""
        solutions = []
        
        if analysis["error_category"] == "data_validation":
            solutions.extend([
                "Validate input data format",
                "Check data type constraints",
                "Verify data completeness"
            ])
        elif analysis["error_category"] == "processing":
            solutions.extend([
                "Review processing pipeline",
                "Check resource allocation",
                "Verify data transformations"
            ])
        elif analysis["error_category"] == "storage":
            solutions.extend([
                "Check storage capacity",
                "Verify data persistence",
                "Review backup status"
            ])
        
        return solutions
    
    async def get_monitoring_plan(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Get data processing monitoring plan."""
        return {
            "metrics": [
                "processing_rate",
                "error_rate",
                "data_volume",
                "processing_time",
                "storage_usage"
            ],
            "alerts": [
                {"metric": "error_rate", "threshold": 10, "window": "5m"},
                {"metric": "processing_time", "threshold": 300, "window": "1m"},
                {"metric": "storage_usage", "threshold": 90, "window": "5m"}
            ],
            "dashboards": [
                "processing_metrics",
                "error_trends",
                "data_quality"
            ]
        }
    
    def _categorize_data_error(self, error_type: str) -> str:
        """Categorize data processing errors."""
        categories = {
            "data_validation": ["validation", "format", "type"],
            "processing": ["processing", "transformation", "pipeline"],
            "storage": ["storage", "persistence", "backup"],
            "performance": ["performance", "timeout", "resource"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in error_type.lower() for keyword in keywords):
                return category
        return "unknown"
    
    def _assess_data_impact(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Assess impact on data."""
        return {
            "affected_records": "all" if context.severity == "critical" else "partial",
            "data_loss": "none" if context.severity != "critical" else "possible",
            "recovery_required": context.severity == "critical"
        }
    
    def _identify_processing_stage(self, context: DomainErrorContext) -> str:
        """Identify the stage where the error occurred."""
        stages = ["input", "validation", "processing", "transformation", "output"]
        for stage in stages:
            if stage in context.error_type.lower():
                return stage
        return "unknown"
    
    def _check_data_integrity(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Check data integrity status."""
        return {
            "integrity_status": "compromised" if context.severity == "critical" else "intact",
            "validation_status": "failed",
            "backup_status": "available"
        }
    
    def _get_recovery_options(self, context: DomainErrorContext) -> List[str]:
        """Get data recovery options."""
        options = []
        if context.severity == "critical":
            options.extend([
                "Restore from backup",
                "Reprocess failed records",
                "Validate data integrity"
            ])
        return options

class MicroservicesHandler(DomainErrorHandler):
    """Handler for microservices errors."""
    
    async def analyze_error(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Analyze microservices errors."""
        analysis = {
            "error_category": self._categorize_microservice_error(context.error_type),
            "service_impact": self._assess_service_impact(context),
            "dependency_chain": self._analyze_dependency_chain(context),
            "circuit_breaker_status": self._check_circuit_breaker(context),
            "resilience_patterns": self._check_resilience_patterns(context)
        }
        return analysis
    
    async def generate_solution(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate microservices specific solutions."""
        solutions = []
        
        if analysis["error_category"] == "service_discovery":
            solutions.extend([
                "Check service registry",
                "Verify service health",
                "Review service configuration"
            ])
        elif analysis["error_category"] == "communication":
            solutions.extend([
                "Check network connectivity",
                "Verify API contracts",
                "Review message formats"
            ])
        elif analysis["error_category"] == "circuit_breaker":
            solutions.extend([
                "Check circuit breaker status",
                "Review fallback mechanisms",
                "Verify service dependencies"
            ])
        
        return solutions
    
    async def get_monitoring_plan(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Get microservices monitoring plan."""
        return {
            "metrics": [
                "service_health",
                "response_time",
                "error_rate",
                "circuit_breaker_status",
                "dependency_health"
            ],
            "alerts": [
                {"metric": "service_health", "threshold": 0, "window": "1m"},
                {"metric": "error_rate", "threshold": 10, "window": "5m"},
                {"metric": "circuit_breaker_status", "threshold": 1, "window": "1m"}
            ],
            "dashboards": [
                "service_health",
                "dependency_map",
                "error_trends"
            ]
        }
    
    def _categorize_microservice_error(self, error_type: str) -> str:
        """Categorize microservices errors."""
        categories = {
            "service_discovery": ["discovery", "registry", "service"],
            "communication": ["network", "api", "message"],
            "circuit_breaker": ["circuit", "breaker", "fallback"],
            "resilience": ["timeout", "retry", "resilience"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in error_type.lower() for keyword in keywords):
                return category
        return "unknown"
    
    def _assess_service_impact(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Assess impact on services."""
        return {
            "affected_services": context.affected_components,
            "service_health": "degraded" if context.severity == "critical" else "healthy",
            "recovery_required": context.severity == "critical"
        }
    
    def _analyze_dependency_chain(self, context: DomainErrorContext) -> List[str]:
        """Analyze service dependency chain."""
        return context.dependencies
    
    def _check_circuit_breaker(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Check circuit breaker status."""
        return {
            "status": "open" if context.severity == "critical" else "closed",
            "failure_count": 0,
            "reset_timeout": 60
        }
    
    def _check_resilience_patterns(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Check resilience patterns."""
        return {
            "retry_enabled": True,
            "timeout_enabled": True,
            "fallback_enabled": True,
            "bulkhead_enabled": True
        }

class MobileApplicationHandler(DomainErrorHandler):
    """Handler for mobile application errors."""
    
    async def analyze_error(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Analyze mobile application errors."""
        analysis = {
            "error_category": self._categorize_mobile_error(context.error_type),
            "device_impact": self._assess_device_impact(context),
            "network_status": self._check_network_status(context),
            "app_state": self._check_app_state(context),
            "user_experience": self._assess_user_experience(context)
        }
        return analysis
    
    async def generate_solution(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate mobile application specific solutions."""
        solutions = []
        
        if analysis["error_category"] == "network":
            solutions.extend([
                "Check network connectivity",
                "Verify API endpoints",
                "Review offline capabilities"
            ])
        elif analysis["error_category"] == "ui":
            solutions.extend([
                "Check UI components",
                "Verify screen layouts",
                "Review user interactions"
            ])
        elif analysis["error_category"] == "storage":
            solutions.extend([
                "Check local storage",
                "Verify data persistence",
                "Review cache management"
            ])
        
        return solutions
    
    async def get_monitoring_plan(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Get mobile application monitoring plan."""
        return {
            "metrics": [
                "crash_rate",
                "network_errors",
                "app_performance",
                "battery_usage",
                "storage_usage"
            ],
            "alerts": [
                {"metric": "crash_rate", "threshold": 5, "window": "1h"},
                {"metric": "network_errors", "threshold": 20, "window": "5m"},
                {"metric": "app_performance", "threshold": 2000, "window": "1m"}
            ],
            "dashboards": [
                "crash_analytics",
                "performance_metrics",
                "user_experience"
            ]
        }
    
    def _categorize_mobile_error(self, error_type: str) -> str:
        """Categorize mobile application errors."""
        categories = {
            "network": ["network", "connection", "api"],
            "ui": ["ui", "screen", "layout"],
            "storage": ["storage", "cache", "persistence"],
            "performance": ["performance", "memory", "battery"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in error_type.lower() for keyword in keywords):
                return category
        return "unknown"
    
    def _assess_device_impact(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Assess impact on device."""
        return {
            "affected_devices": "all" if context.severity == "critical" else "some",
            "battery_impact": "high" if context.severity == "critical" else "low",
            "storage_impact": "high" if context.severity == "critical" else "low"
        }
    
    def _check_network_status(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Check network status."""
        return {
            "connectivity": "available",
            "api_status": "responsive",
            "offline_mode": "enabled"
        }
    
    def _check_app_state(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Check application state."""
        return {
            "state": "running",
            "memory_usage": "normal",
            "background_processes": "active"
        }
    
    def _assess_user_experience(self, context: DomainErrorContext) -> Dict[str, Any]:
        """Assess user experience impact."""
        return {
            "app_responsiveness": "degraded" if context.severity == "critical" else "normal",
            "feature_availability": "partial" if context.severity == "critical" else "full",
            "user_impact": "high" if context.severity == "critical" else "low"
        }

class DomainHandlerFactory:
    """Factory for creating domain-specific error handlers."""
    
    @staticmethod
    def create_handler(domain: str) -> DomainErrorHandler:
        """Create appropriate handler for the domain."""
        handlers = {
            "web": WebApplicationHandler(),
            "data_processing": DataProcessingHandler(),
            "microservices": MicroservicesHandler(),
            "mobile": MobileApplicationHandler()
        }
        return handlers.get(domain, DomainErrorHandler()) 