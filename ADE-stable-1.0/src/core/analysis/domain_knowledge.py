from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class DomainContext:
    """Represents domain-specific context for error analysis."""
    domain: str
    frameworks: List[str]
    common_patterns: List[str]
    critical_components: List[str]
    monitoring_metrics: List[str]
    best_practices: List[str]
    security_considerations: List[str]
    performance_guidelines: List[str]

class DomainKnowledge:
    """Provides domain-specific knowledge for error analysis."""
    
    def __init__(self):
        self.domains: Dict[str, DomainContext] = {
            "web_application": DomainContext(
                domain="web_application",
                frameworks=["Django", "Flask", "FastAPI", "Spring Boot", "Express"],
                common_patterns=[
                    "Session management errors",
                    "Authentication failures",
                    "Database connection issues",
                    "API rate limiting",
                    "CORS configuration errors"
                ],
                critical_components=[
                    "Authentication service",
                    "Database layer",
                    "API endpoints",
                    "Session store",
                    "Cache layer"
                ],
                monitoring_metrics=[
                    "Response time",
                    "Error rate",
                    "Active users",
                    "Database query time",
                    "Cache hit ratio"
                ],
                best_practices=[
                    "Implement proper error handling",
                    "Use secure session management",
                    "Follow REST API best practices",
                    "Implement rate limiting",
                    "Use proper logging"
                ],
                security_considerations=[
                    "Input validation",
                    "XSS prevention",
                    "CSRF protection",
                    "SQL injection prevention",
                    "Authentication security"
                ],
                performance_guidelines=[
                    "Implement caching",
                    "Optimize database queries",
                    "Use connection pooling",
                    "Implement request batching",
                    "Monitor resource usage"
                ]
            ),
            "data_processing": DomainContext(
                domain="data_processing",
                frameworks=["Apache Spark", "Hadoop", "Pandas", "NumPy", "Dask"],
                common_patterns=[
                    "Memory overflow",
                    "Data type mismatches",
                    "Processing timeouts",
                    "Resource exhaustion",
                    "Data corruption"
                ],
                critical_components=[
                    "Data ingestion pipeline",
                    "Processing engine",
                    "Storage layer",
                    "Resource manager",
                    "Monitoring system"
                ],
                monitoring_metrics=[
                    "Processing time",
                    "Memory usage",
                    "CPU utilization",
                    "I/O operations",
                    "Data quality metrics"
                ],
                best_practices=[
                    "Implement data validation",
                    "Use efficient data structures",
                    "Optimize processing logic",
                    "Implement proper error handling",
                    "Monitor resource usage"
                ],
                security_considerations=[
                    "Data encryption",
                    "Access control",
                    "Audit logging",
                    "Data integrity checks",
                    "Secure data transfer"
                ],
                performance_guidelines=[
                    "Optimize data structures",
                    "Use parallel processing",
                    "Implement caching",
                    "Monitor resource usage",
                    "Optimize I/O operations"
                ]
            ),
            "microservices": DomainContext(
                domain="microservices",
                frameworks=["Kubernetes", "Docker", "gRPC", "RabbitMQ", "Redis"],
                common_patterns=[
                    "Service discovery issues",
                    "Network timeouts",
                    "Circuit breaker trips",
                    "Load balancing problems",
                    "Configuration errors"
                ],
                critical_components=[
                    "Service registry",
                    "Load balancer",
                    "Message broker",
                    "Configuration service",
                    "Monitoring system"
                ],
                monitoring_metrics=[
                    "Service health",
                    "Response time",
                    "Error rate",
                    "Resource usage",
                    "Network latency"
                ],
                best_practices=[
                    "Implement circuit breakers",
                    "Use service discovery",
                    "Implement proper logging",
                    "Use health checks",
                    "Implement retry logic"
                ],
                security_considerations=[
                    "Service authentication",
                    "Network security",
                    "Data encryption",
                    "Access control",
                    "Audit logging"
                ],
                performance_guidelines=[
                    "Optimize network calls",
                    "Implement caching",
                    "Use connection pooling",
                    "Monitor resource usage",
                    "Implement rate limiting"
                ]
            ),
            "mobile_application": DomainContext(
                domain="mobile_application",
                frameworks=["React Native", "Flutter", "iOS Native", "Android Native"],
                common_patterns=[
                    "Network connectivity issues",
                    "Memory leaks",
                    "UI rendering problems",
                    "Battery consumption",
                    "Storage issues"
                ],
                critical_components=[
                    "Network layer",
                    "UI components",
                    "Local storage",
                    "Background services",
                    "Push notifications"
                ],
                monitoring_metrics=[
                    "App performance",
                    "Crash rate",
                    "Battery usage",
                    "Network usage",
                    "Storage usage"
                ],
                best_practices=[
                    "Implement offline support",
                    "Optimize battery usage",
                    "Handle network changes",
                    "Implement proper error handling",
                    "Use efficient data structures"
                ],
                security_considerations=[
                    "Data encryption",
                    "Secure storage",
                    "Network security",
                    "Authentication",
                    "Input validation"
                ],
                performance_guidelines=[
                    "Optimize UI rendering",
                    "Implement caching",
                    "Optimize battery usage",
                    "Monitor resource usage",
                    "Optimize network calls"
                ]
            )
        }
    
    def get_domain_context(self, domain: str) -> Optional[DomainContext]:
        """Get domain-specific context for error analysis."""
        return self.domains.get(domain)
    
    def get_domain_prompt(self, domain: str) -> str:
        """Get domain-specific prompt for LLM analysis."""
        context = self.get_domain_context(domain)
        if not context:
            return ""
        
        return f"""
        Consider the following domain-specific context for {domain}:
        
        Frameworks: {', '.join(context.frameworks)}
        Common Patterns: {', '.join(context.common_patterns)}
        Critical Components: {', '.join(context.critical_components)}
        Monitoring Metrics: {', '.join(context.monitoring_metrics)}
        Best Practices: {', '.join(context.best_practices)}
        Security Considerations: {', '.join(context.security_considerations)}
        Performance Guidelines: {', '.join(context.performance_guidelines)}
        
        Please incorporate this domain knowledge into your analysis and recommendations.
        """
    
    def get_domain_specific_metrics(self, domain: str) -> List[str]:
        """Get domain-specific metrics for monitoring."""
        context = self.get_domain_context(domain)
        return context.monitoring_metrics if context else []
    
    def get_domain_best_practices(self, domain: str) -> List[str]:
        """Get domain-specific best practices."""
        context = self.get_domain_context(domain)
        return context.best_practices if context else []
    
    def get_domain_security_considerations(self, domain: str) -> List[str]:
        """Get domain-specific security considerations."""
        context = self.get_domain_context(domain)
        return context.security_considerations if context else []
    
    def get_domain_performance_guidelines(self, domain: str) -> List[str]:
        """Get domain-specific performance guidelines."""
        context = self.get_domain_context(domain)
        return context.performance_guidelines if context else [] 