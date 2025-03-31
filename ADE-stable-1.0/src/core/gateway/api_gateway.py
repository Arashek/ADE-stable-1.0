from typing import Dict, List, Optional, Any, Set, Union, Callable, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import aiohttp
import asyncio
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import jwt
import time
import redis
from ..auth.auth_service import User
from ..config.service_config import ServiceConfig
import json
import secrets
import uvicorn
from pathlib import Path
import yaml
from .service_discovery import ServiceDiscovery, ServiceInstance, LoadBalanceStrategy
from .rate_limiting import RateLimiter, UserTier
import prometheus_client as prom
from prometheus_client import Counter, Histogram, Gauge
import traceback
import hashlib
import jsonpath_ng
from jinja2 import Template
import re
import opentelemetry
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from elasticsearch import AsyncElasticsearch
import numpy as np
from ..monitoring.audit_logging import (
    AuditLogger,
    AuditEvent,
    AuditEventType,
    AuditEventSeverity
)
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'gateway_requests_total',
    'Total number of requests',
    ['method', 'path', 'status']
)
REQUEST_LATENCY = Histogram(
    'gateway_request_duration_seconds',
    'Request latency in seconds',
    ['method', 'path']
)
ACTIVE_CONNECTIONS = Gauge(
    'gateway_active_connections',
    'Number of active connections',
    ['service']
)
ERROR_COUNT = Counter(
    'gateway_errors_total',
    'Total number of errors',
    ['type', 'service']
)

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"

class RequestMethod(Enum):
    """HTTP request methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

class ResponseStatus(Enum):
    """Standard response statuses."""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    BAD_REQUEST = "bad_request"
    INTERNAL_ERROR = "internal_error"

@dataclass
class ServiceInfo:
    name: str
    url: str
    status: ServiceStatus
    last_health_check: datetime
    metadata: Dict[str, Any]
    rate_limit: Dict[str, int]  # requests per minute
    circuit_breaker: Dict[str, Any]

@dataclass
class RouteConfig:
    """Route configuration."""
    path: str
    method: RequestMethod
    service: str
    path_prefix: str = ""
    auth_required: bool = True
    rate_limit: Optional[int] = None
    timeout: float = 30.0
    retry_count: int = 3
    metadata: Dict[str, Any] = None

@dataclass
class GatewayResponse:
    """Standardized gateway response."""
    status: ResponseStatus
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class JWTConfig(BaseModel):
    """JWT configuration."""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

class RateLimitConfig(BaseModel):
    """Rate limit configuration."""
    requests_per_minute: int
    burst_size: int = 10
    window_seconds: int = 60

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, redis_client: redis.Redis):
        super().__init__(app)
        self.redis_client = redis_client
        
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP or user ID)
        client_id = request.client.host
        if hasattr(request.state, "user"):
            client_id = request.state.user.id
            
        # Get endpoint path
        path = request.url.path
        
        # Check rate limit
        key = f"rate_limit:{client_id}:{path}"
        current = int(self.redis_client.get(key) or 0)
        
        # Get rate limit from service config
        service = self.get_service_from_path(path)
        rate_limit = self.get_rate_limit(service)
        
        if current >= rate_limit:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
            
        # Increment counter
        self.redis_client.incr(key)
        self.redis_client.expire(key, 60)  # Reset after 1 minute
        
        return await call_next(request)
        
    def get_service_from_path(self, path: str) -> str:
        """Extract service name from path."""
        parts = path.split("/")
        return parts[1] if len(parts) > 1 else "default"
        
    def get_rate_limit(self, service: str) -> int:
        """Get rate limit for service."""
        # Default rate limits
        limits = {
            "default": 60,
            "auth": 30,
            "api": 100,
            "admin": 20
        }
        return limits.get(service, limits["default"])

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5,
                 reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = None
        self.is_open = False
        
    def record_failure(self):
        """Record a failure and potentially open the circuit."""
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.is_open = True
            logger.warning("Circuit breaker opened")
            
    def record_success(self):
        """Record a success and reset the circuit breaker."""
        self.failures = 0
        self.is_open = False
        
    def can_execute(self) -> bool:
        """Check if request can be executed."""
        if not self.is_open:
            return True
            
        # Check if reset timeout has elapsed
        if (time.time() - self.last_failure_time) >= self.reset_timeout:
            self.is_open = False
            self.failures = 0
            return True
            
        return False

class TransformRule:
    """Request/response transformation rule."""
    def __init__(
        self,
        name: str,
        condition: Dict[str, Any],
        request_transform: Optional[Dict[str, Any]] = None,
        response_transform: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.condition = condition
        self.request_transform = request_transform or {}
        self.response_transform = response_transform or {}
        
        # Compile JSON path expressions
        self.request_paths = {}
        self.response_paths = {}
        if "jsonpath" in self.request_transform:
            for key, expr in self.request_transform["jsonpath"].items():
                self.request_paths[key] = jsonpath_ng.parse(expr)
        if "jsonpath" in self.response_transform:
            for key, expr in self.response_transform["jsonpath"].items():
                self.response_paths[key] = jsonpath_ng.parse(expr)
                
        # Compile templates
        self.request_templates = {}
        self.response_templates = {}
        if "template" in self.request_transform:
            for key, template in self.request_transform["template"].items():
                self.request_templates[key] = Template(template)
        if "template" in self.response_transform:
            for key, template in self.response_transform["template"].items():
                self.response_templates[key] = Template(template)
                
    def _apply_jsonpath(
        self,
        data: Dict[str, Any],
        paths: Dict[str, jsonpath_ng.Expression]
    ) -> Dict[str, Any]:
        """Apply JSON path transformations."""
        result = {}
        for key, expr in paths.items():
            matches = expr.find(data)
            if matches:
                result[key] = matches[0].value
        return result
        
    def _apply_template(
        self,
        data: Dict[str, Any],
        templates: Dict[str, Template]
    ) -> Dict[str, Any]:
        """Apply template transformations."""
        result = {}
        for key, template in templates.items():
            try:
                result[key] = template.render(**data)
            except Exception as e:
                logger.error(f"Template rendering failed: {str(e)}")
                result[key] = None
        return result
        
    def _apply_regex(
        self,
        data: Dict[str, Any],
        patterns: Dict[str, str]
    ) -> Dict[str, Any]:
        """Apply regex transformations."""
        result = {}
        for key, pattern in patterns.items():
            try:
                if isinstance(data.get(key), str):
                    match = re.search(pattern, data[key])
                    if match:
                        result[key] = match.group(1)
            except Exception as e:
                logger.error(f"Regex transformation failed: {str(e)}")
                result[key] = None
        return result

@dataclass
class AlertConfig:
    """Alert configuration."""
    name: str
    condition: Dict[str, Any]
    threshold: float
    duration: int  # seconds
    severity: str
    notification: Dict[str, Any]
    enabled: bool = True

class AlertManager:
    """Alert management system."""
    
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self.alerts: Dict[str, AlertConfig] = {}
        self.alert_history: Dict[str, List[Dict[str, Any]]] = {}
        self._load_alerts()
        
    def _load_alerts(self) -> None:
        """Load alert configurations."""
        alerts_file = self.config_dir / "alerts.yaml"
        if alerts_file.exists():
            with open(alerts_file) as f:
                data = yaml.safe_load(f)
                for alert_data in data:
                    alert = AlertConfig(
                        name=alert_data["name"],
                        condition=alert_data["condition"],
                        threshold=alert_data["threshold"],
                        duration=alert_data["duration"],
                        severity=alert_data["severity"],
                        notification=alert_data["notification"]
                    )
                    self.alerts[alert.name] = alert
                    self.alert_history[alert.name] = []
                    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check metrics against alert conditions."""
        triggered_alerts = []
        
        for alert in self.alerts.values():
            if not alert.enabled:
                continue
                
            # Check condition
            value = self._evaluate_condition(alert.condition, metrics)
            if value >= alert.threshold:
                # Add to history
                self.alert_history[alert.name].append({
                    "timestamp": datetime.now(),
                    "value": value,
                    "threshold": alert.threshold
                })
                
                # Keep only recent history
                cutoff = datetime.now() - timedelta(seconds=alert.duration)
                self.alert_history[alert.name] = [
                    h for h in self.alert_history[alert.name]
                    if h["timestamp"] > cutoff
                ]
                
                # Check if alert is sustained
                if len(self.alert_history[alert.name]) >= alert.duration:
                    triggered_alerts.append({
                        "name": alert.name,
                        "severity": alert.severity,
                        "value": value,
                        "threshold": alert.threshold,
                        "notification": alert.notification
                    })
                    
        return triggered_alerts
        
    def _evaluate_condition(
        self,
        condition: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> float:
        """Evaluate alert condition against metrics."""
        metric_name = condition["metric"]
        if metric_name not in metrics:
            return 0.0
            
        value = metrics[metric_name]
        
        # Apply aggregation if specified
        if "aggregation" in condition:
            if condition["aggregation"] == "avg":
                value = sum(value) / len(value)
            elif condition["aggregation"] == "max":
                value = max(value)
            elif condition["aggregation"] == "min":
                value = min(value)
                
        return float(value)
        
    async def send_notification(
        self,
        alert: Dict[str, Any]
    ) -> None:
        """Send alert notification."""
        notification = alert["notification"]
        
        if notification["type"] == "email":
            await self._send_email_notification(alert)
        elif notification["type"] == "webhook":
            await self._send_webhook_notification(alert)
        elif notification["type"] == "slack":
            await self._send_slack_notification(alert)
            
    async def _send_email_notification(self, alert: Dict[str, Any]) -> None:
        """Send email notification."""
        notification = alert["notification"]
        
        msg = MIMEMultipart()
        msg["From"] = notification["from"]
        msg["To"] = notification["to"]
        msg["Subject"] = f"Alert: {alert['name']}"
        
        body = f"""
        Alert: {alert['name']}
        Severity: {alert['severity']}
        Value: {alert['value']}
        Threshold: {alert['threshold']}
        Time: {datetime.now()}
        """
        
        msg.attach(MIMEText(body, "plain"))
        
        try:
            with smtplib.SMTP(notification["smtp_server"]) as server:
                server.starttls()
                server.login(notification["username"], notification["password"])
                server.send_message(msg)
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            
    async def _send_webhook_notification(self, alert: Dict[str, Any]) -> None:
        """Send webhook notification."""
        notification = alert["notification"]
        
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    notification["url"],
                    json={
                        "alert": alert["name"],
                        "severity": alert["severity"],
                        "value": alert["value"],
                        "threshold": alert["threshold"],
                        "timestamp": datetime.now().isoformat()
                    },
                    headers=notification.get("headers", {})
                )
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {str(e)}")
            
    async def _send_slack_notification(self, alert: Dict[str, Any]) -> None:
        """Send Slack notification."""
        notification = alert["notification"]
        
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    notification["webhook_url"],
                    json={
                        "text": f"""
                        *Alert: {alert['name']}*
                        Severity: {alert['severity']}
                        Value: {alert['value']}
                        Threshold: {alert['threshold']}
                        Time: {datetime.now()}
                        """
                    }
                )
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")

class APIGateway:
    """API Gateway with enhanced features."""
    
    def __init__(
        self,
        config_dir: str,
        elasticsearch_url: str = "http://localhost:9200",
        redis_url: str = "redis://localhost:6379",
        jwt_secret: str = "your-secret-key"
    ):
        self.config_dir = Path(config_dir)
        self.es = AsyncElasticsearch([elasticsearch_url])
        self.redis = redis.from_url(redis_url)
        self.jwt_secret = jwt_secret
        
        # Initialize audit logger
        self.audit_logger = AuditLogger(
            config_dir=config_dir,
            elasticsearch_url=elasticsearch_url
        )
        
        # Load configurations
        self.routes: Dict[str, RouteConfig] = {}
        self.services: Dict[str, ServiceConfig] = {}
        self.transform_rules: List[TransformRule] = []
        self._load_configs()
        
        # Initialize metrics
        self._init_metrics()
        
        # Track active connections and circuit breaker state
        self.active_connections = 0
        self.circuit_breaker = CircuitBreaker()
        
    async def handle_request(
        self,
        request: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle incoming request with enhanced features."""
        try:
            # Track active connections
            self.active_connections += 1
            self.active_connections_metric.inc()
            
            # Check circuit breaker
            if self.circuit_breaker.is_open():
                # Log circuit breaker event
                await self.audit_logger.log_event(
                    AuditEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=AuditEventType.SYSTEM_CHANGE,
                        severity=AuditEventSeverity.WARNING,
                        timestamp=datetime.now(),
                        user_id=context.get("user_id"),
                        action="circuit_breaker_open",
                        resource="api_gateway",
                        details={
                            "request_path": request.get("path"),
                            "request_method": request.get("method")
                        },
                        ip_address=context.get("ip_address"),
                        user_agent=context.get("user_agent"),
                        session_id=context.get("session_id"),
                        correlation_id=context.get("correlation_id"),
                        metadata={
                            "fallback_response": self.circuit_breaker.get_fallback_response()
                        }
                    )
                )
                return self.circuit_breaker.get_fallback_response()
            
            # Get route configuration
            route_key = f"{request['method']}:{request['path']}"
            route = self.routes.get(route_key)
            if not route:
                # Log invalid route access
                await self.audit_logger.log_event(
                    AuditEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=AuditEventType.DATA_ACCESS,
                        severity=AuditEventSeverity.WARNING,
                        timestamp=datetime.now(),
                        user_id=context.get("user_id"),
                        action="invalid_route_access",
                        resource="api_gateway",
                        details={
                            "request_path": request.get("path"),
                            "request_method": request.get("method")
                        },
                        ip_address=context.get("ip_address"),
                        user_agent=context.get("user_agent"),
                        session_id=context.get("session_id"),
                        correlation_id=context.get("correlation_id"),
                        metadata={}
                    )
                )
                return {"error": "Route not found"}
            
            # Apply request transformations
            transformed_request = await self._apply_transformations(
                request,
                route.request_transform
            )
            
            # Get service instance with adaptive load balancing
            service_instance = await self._get_service_instance(route.service)
            
            # Forward request to service
            start_time = datetime.now()
            try:
                response = await self._forward_request(
                    service_instance,
                    transformed_request
                )
                
                # Record success metrics
                self.request_latency_metric.observe(
                    (datetime.now() - start_time).total_seconds()
                )
                self.request_count_metric.inc()
                self.success_count_metric.inc()
                
                # Log successful request
                await self.audit_logger.log_event(
                    AuditEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=AuditEventType.DATA_ACCESS,
                        severity=AuditEventSeverity.INFO,
                        timestamp=datetime.now(),
                        user_id=context.get("user_id"),
                        action="request_forwarded",
                        resource=route.service,
                        details={
                            "request_path": request.get("path"),
                            "request_method": request.get("method"),
                            "service_instance": service_instance
                        },
                        ip_address=context.get("ip_address"),
                        user_agent=context.get("user_agent"),
                        session_id=context.get("session_id"),
                        correlation_id=context.get("correlation_id"),
                        metadata={
                            "response_status": response.get("status_code")
                        }
                    )
                )
                
                # Apply response transformations
                transformed_response = await self._apply_transformations(
                    response,
                    route.response_transform
                )
                
                return transformed_response
                
            except Exception as e:
                # Record failure metrics
                self.request_count_metric.inc()
                self.error_count_metric.inc()
                
                # Log request failure
                await self.audit_logger.log_event(
                    AuditEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=AuditEventType.DATA_ACCESS,
                        severity=AuditEventSeverity.ERROR,
                        timestamp=datetime.now(),
                        user_id=context.get("user_id"),
                        action="request_failed",
                        resource=route.service,
                        details={
                            "request_path": request.get("path"),
                            "request_method": request.get("method"),
                            "service_instance": service_instance,
                            "error": str(e)
                        },
                        ip_address=context.get("ip_address"),
                        user_agent=context.get("user_agent"),
                        session_id=context.get("session_id"),
                        correlation_id=context.get("correlation_id"),
                        metadata={}
                    )
                )
                
                # Update circuit breaker
                self.circuit_breaker.record_failure()
                
                return {"error": "Service unavailable"}
                
        finally:
            # Update active connections
            self.active_connections -= 1
            self.active_connections_metric.dec()
            
    async def _authenticate_request(
        self,
        request: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Authenticate request with JWT."""
        try:
            token = request.get("headers", {}).get("Authorization", "").split(" ")[1]
            if not token:
                # Log authentication failure
                await self.audit_logger.log_event(
                    AuditEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=AuditEventType.AUTHENTICATION,
                        severity=AuditEventSeverity.WARNING,
                        timestamp=datetime.now(),
                        user_id=None,
                        action="authentication_failed",
                        resource="api_gateway",
                        details={
                            "reason": "missing_token",
                            "request_path": request.get("path"),
                            "request_method": request.get("method")
                        },
                        ip_address=request.get("ip_address"),
                        user_agent=request.get("user_agent"),
                        session_id=request.get("session_id"),
                        correlation_id=request.get("correlation_id"),
                        metadata={}
                    )
                )
                return None
                
            # Verify token
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            
            # Log successful authentication
            await self.audit_logger.log_event(
                AuditEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=AuditEventType.AUTHENTICATION,
                    severity=AuditEventSeverity.INFO,
                    timestamp=datetime.now(),
                    user_id=payload.get("user_id"),
                    action="authentication_success",
                    resource="api_gateway",
                    details={
                        "request_path": request.get("path"),
                        "request_method": request.get("method")
                    },
                    ip_address=request.get("ip_address"),
                    user_agent=request.get("user_agent"),
                    session_id=request.get("session_id"),
                    correlation_id=request.get("correlation_id"),
                    metadata={
                        "token_exp": payload.get("exp")
                    }
                )
            )
            
            return payload
            
        except jwt.InvalidTokenError as e:
            # Log invalid token
            await self.audit_logger.log_event(
                AuditEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=AuditEventType.AUTHENTICATION,
                    severity=AuditEventSeverity.WARNING,
                    timestamp=datetime.now(),
                    user_id=None,
                    action="invalid_token",
                    resource="api_gateway",
                    details={
                        "reason": str(e),
                        "request_path": request.get("path"),
                        "request_method": request.get("method")
                    },
                    ip_address=request.get("ip_address"),
                    user_agent=request.get("user_agent"),
                    session_id=request.get("session_id"),
                    correlation_id=request.get("correlation_id"),
                    metadata={}
                )
            )
            return None
            
    async def _load_configs(self) -> None:
        """Load gateway configurations."""
        try:
            # Load routes
            routes_file = self.config_dir / "routes.yaml"
            if routes_file.exists():
                with open(routes_file) as f:
                    data = yaml.safe_load(f)
                    for route_data in data:
                        route = RouteConfig(**route_data)
                        self.routes[f"{route.method.value}:{route.path}"] = route
                        
            # Load services
            services_file = self.config_dir / "services.yaml"
            if services_file.exists():
                with open(services_file) as f:
                    data = yaml.safe_load(f)
                    for service_data in data:
                        service = ServiceConfig(
                            name=service_data["name"],
                            version=service_data["version"],
                            base_url=service_data["base_url"],
                            timeout=service_data.get("timeout", 30.0),
                            retry_count=service_data.get("retry_count", 3),
                            metadata=service_data.get("metadata", {})
                        )
                        self.services[service.name] = service
                        
            # Load transformation rules
            transforms_file = self.config_dir / "transforms.yaml"
            if transforms_file.exists():
                with open(transforms_file) as f:
                    data = yaml.safe_load(f)
                    for rule_data in data:
                        rule = TransformRule(
                            name=rule_data["name"],
                            condition=rule_data["condition"],
                            request_transform=rule_data.get("request_transform"),
                            response_transform=rule_data.get("response_transform")
                        )
                        self.transform_rules.append(rule)
                        
            # Log configuration load
            await self.audit_logger.log_event(
                AuditEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=AuditEventType.CONFIG_CHANGE,
                    severity=AuditEventSeverity.INFO,
                    timestamp=datetime.now(),
                    user_id="system",
                    action="config_loaded",
                    resource="api_gateway",
                    details={
                        "routes_count": len(self.routes),
                        "services_count": len(self.services),
                        "transformations_count": len(self.transform_rules)
                    },
                    ip_address=None,
                    user_agent=None,
                    session_id=None,
                    correlation_id=None,
                    metadata={}
                )
            )
            
        except Exception as e:
            logger.error(f"Failed to load configurations: {str(e)}")
            
    async def update_config(
        self,
        config_type: str,
        config_data: Dict[str, Any]
    ) -> bool:
        """Update gateway configuration."""
        try:
            if config_type == "routes":
                # Update routes
                for route_data in config_data:
                    route = RouteConfig(**route_data)
                    self.routes[f"{route.method.value}:{route.path}"] = route
                    
                # Save to file
                routes_file = self.config_dir / "routes.yaml"
                with open(routes_file, "w") as f:
                    yaml.dump(config_data, f)
                    
            elif config_type == "services":
                # Update services
                for service_data in config_data:
                    service = ServiceConfig(**service_data)
                    self.services[service.name] = service
                    
                # Save to file
                services_file = self.config_dir / "services.yaml"
                with open(services_file, "w") as f:
                    yaml.dump(config_data, f)
                    
            elif config_type == "transforms":
                # Update transformations
                for rule_data in config_data:
                    rule = TransformRule(
                        name=rule_data["name"],
                        condition=rule_data["condition"],
                        request_transform=rule_data.get("request_transform"),
                        response_transform=rule_data.get("response_transform")
                    )
                    self.transform_rules.append(rule)
                    
                # Save to file
                transforms_file = self.config_dir / "transforms.yaml"
                with open(transforms_file, "w") as f:
                    yaml.dump(config_data, f)
                    
            # Log configuration update
            await self.audit_logger.log_event(
                AuditEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=AuditEventType.CONFIG_CHANGE,
                    severity=AuditEventSeverity.WARNING,
                    timestamp=datetime.now(),
                    user_id="admin",
                    action="config_updated",
                    resource="api_gateway",
                    details={
                        "config_type": config_type,
                        "changes": config_data
                    },
                    ip_address=None,
                    user_agent=None,
                    session_id=None,
                    correlation_id=None,
                    metadata={}
                )
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {str(e)}")
            return False
            
    async def close(self) -> None:
        """Close connections and cleanup."""
        await self.es.close()
        await self.redis.close()
        await self.audit_logger.close()

    def generate_access_token(
        self,
        user_id: str,
        roles: List[str],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Generate JWT access token."""
        to_encode = {
            "sub": user_id,
            "roles": roles,
            "exp": datetime.utcnow() + (
                expires_delta or timedelta(minutes=self.jwt_config.access_token_expire_minutes)
            )
        }
        return jwt.encode(
            to_encode,
            self.jwt_config.secret_key,
            algorithm=self.jwt_config.algorithm
        )
        
    def validate_access_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT access token."""
        try:
            return jwt.decode(
                token,
                self.jwt_config.secret_key,
                algorithms=[self.jwt_config.algorithm]
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
            
    def revoke_access_token(self, token: str) -> None:
        """Revoke JWT access token."""
        # In a real implementation, you would add the token to a blacklist
        # and check against it during validation
        pass

    def _get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service."""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]

    def run(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Run the API gateway."""
        uvicorn.run(self.app, host=host, port=port) 