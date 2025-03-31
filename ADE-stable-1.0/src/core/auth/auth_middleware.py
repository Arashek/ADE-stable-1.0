from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime, timedelta
import logging
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import json
import hashlib
import ipaddress
import re
from .auth_service import AuthService, User, UserRole
from .user_management import UserManagementService
from .two_factor import TwoFactorAuth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimitConfig:
    def __init__(
        self,
        requests_per_minute: int,
        burst_size: int = 10,
        window_size: int = 60,
        block_duration: int = 300,
        concurrent_requests: int = 5,
        per_ip_limit: int = 100
    ):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.window_size = window_size
        self.block_duration = block_duration
        self.concurrent_requests = concurrent_requests
        self.per_ip_limit = per_ip_limit

class SecurityConfig:
    def __init__(
        self,
        max_login_attempts: int = 5,
        lockout_duration: int = 300,
        require_2fa: bool = False,
        allowed_ips: List[str] = None,
        blocked_ips: List[str] = None,
        require_ssl: bool = True,
        max_request_size: int = 10485760,  # 10MB
        allowed_methods: List[str] = None,
        allowed_content_types: List[str] = None,
        require_strong_password: bool = True,
        session_timeout: int = 3600,
        max_sessions_per_user: int = 5,
        enable_ip_geolocation: bool = True,
        enable_anomaly_detection: bool = True
    ):
        self.max_login_attempts = max_login_attempts
        self.lockout_duration = lockout_duration
        self.require_2fa = require_2fa
        self.allowed_ips = allowed_ips or []
        self.blocked_ips = blocked_ips or []
        self.require_ssl = require_ssl
        self.max_request_size = max_request_size
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "PATCH"]
        self.allowed_content_types = allowed_content_types or [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data"
        ]
        self.require_strong_password = require_strong_password
        self.session_timeout = session_timeout
        self.max_sessions_per_user = max_sessions_per_user
        self.enable_ip_geolocation = enable_ip_geolocation
        self.enable_anomaly_detection = enable_anomaly_detection

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        auth_service: AuthService,
        user_management: UserManagementService,
        rate_limits: Dict[UserRole, RateLimitConfig] = None,
        security_config: SecurityConfig = None,
        two_factor_auth: TwoFactorAuth = None
    ):
        super().__init__(app)
        self.auth_service = auth_service
        self.user_management = user_management
        self.rate_limits = rate_limits or {
            UserRole.OWNER: RateLimitConfig(1000, burst_size=20),
            UserRole.ADMIN: RateLimitConfig(500, burst_size=15),
            UserRole.TECHNICAL_STAFF: RateLimitConfig(200, burst_size=10),
            UserRole.CUSTOMER: RateLimitConfig(100, burst_size=5)
        }
        self.security_config = security_config or SecurityConfig()
        self.two_factor_auth = two_factor_auth
        self._request_counts: Dict[str, List[float]] = {}
        self._login_attempts: Dict[str, Tuple[int, float]] = {}
        self._blocked_ips: Dict[str, float] = {}
        self._active_sessions: Dict[str, List[Dict[str, Any]]] = {}
        self._concurrent_requests: Dict[str, int] = {}
        self._anomaly_scores: Dict[str, float] = {}
        
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Skip auth for public endpoints
        if request.url.path.startswith("/public/"):
            return await call_next(request)
            
        # Security checks
        if not self._check_security(request):
            raise HTTPException(
                status_code=403,
                detail="Security check failed"
            )
            
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header"
            )
            
        token = auth_header.split(" ")[1]
        
        # Validate token
        payload = self.auth_service.validate_token(token)
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
            
        # Get user
        user = self.user_management.repository.get_user(payload.sub)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=401,
                detail="User not found or inactive"
            )
            
        # Check rate limit
        if not self._check_rate_limit(user, request):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
            
        # Check 2FA if required
        if self.security_config.require_2fa and self.two_factor_auth.is_2fa_enabled(user.id):
            if not self._check_2fa(request, user):
                raise HTTPException(
                    status_code=403,
                    detail="2FA required"
                )
                
        # Check concurrent requests
        if not self._check_concurrent_requests(user):
            raise HTTPException(
                status_code=429,
                detail="Too many concurrent requests"
            )
            
        # Check session limits
        if not self._check_session_limits(user):
            raise HTTPException(
                status_code=403,
                detail="Session limit exceeded"
            )
            
        # Check for anomalies
        if self.security_config.enable_anomaly_detection:
            if not self._check_anomalies(request, user):
                raise HTTPException(
                    status_code=403,
                    detail="Suspicious activity detected"
                )
                
        # Log request
        self._log_request(request, user)
        
        # Add user to request state
        request.state.user = user
        
        # Check permissions for protected routes
        if request.url.path.startswith("/protected/"):
            required_permission = self._get_required_permission(request)
            if not self.auth_service.has_permission(user, required_permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Missing permission: {required_permission}"
                )
                
        # Process request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response)
        
        return response
        
    def _check_security(self, request: Request) -> bool:
        """Perform security checks on request."""
        # Check SSL
        if self.security_config.require_ssl and not request.url.scheme == "https":
            return False
            
        # Check IP
        client_ip = request.client.host
        if client_ip in self._blocked_ips:
            if time.time() - self._blocked_ips[client_ip] < self.security_config.lockout_duration:
                return False
            else:
                del self._blocked_ips[client_ip]
                
        # Check allowed IPs
        if self.security_config.allowed_ips:
            if not any(
                ipaddress.ip_address(client_ip) in ipaddress.ip_network(allowed_ip)
                for allowed_ip in self.security_config.allowed_ips
            ):
                return False
                
        # Check blocked IPs
        if client_ip in self.security_config.blocked_ips:
            return False
            
        # Check request method
        if request.method not in self.security_config.allowed_methods:
            return False
            
        # Check content type
        content_type = request.headers.get("content-type", "")
        if not any(
            allowed_type in content_type
            for allowed_type in self.security_config.allowed_content_types
        ):
            return False
            
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.security_config.max_request_size:
            return False
            
        return True
        
    def _check_rate_limit(self, user: User, request: Request) -> bool:
        """Enhanced rate limiting with burst support and IP limits."""
        config = self.rate_limits[user.role]
        now = time.time()
        
        # Get user's request history
        user_requests = self._request_counts.get(user.id, [])
        
        # Remove old requests
        user_requests = [
            req_time for req_time in user_requests
            if now - req_time < config.window_size
        ]
        
        # Check burst limit
        if len(user_requests) >= config.burst_size:
            return False
            
        # Check rate limit
        if len(user_requests) >= config.requests_per_minute:
            return False
            
        # Check IP-based limit
        client_ip = request.client.host
        ip_requests = self._request_counts.get(f"ip:{client_ip}", [])
        ip_requests = [
            req_time for req_time in ip_requests
            if now - req_time < config.window_size
        ]
        if len(ip_requests) >= config.per_ip_limit:
            return False
            
        # Add current request
        user_requests.append(now)
        self._request_counts[user.id] = user_requests
        
        ip_requests.append(now)
        self._request_counts[f"ip:{client_ip}"] = ip_requests
        
        return True
        
    def _check_concurrent_requests(self, user: User) -> bool:
        """Check concurrent request limits."""
        config = self.rate_limits[user.role]
        current = self._concurrent_requests.get(user.id, 0)
        
        if current >= config.concurrent_requests:
            return False
            
        self._concurrent_requests[user.id] = current + 1
        return True
        
    def _check_session_limits(self, user: User) -> bool:
        """Check session limits."""
        now = time.time()
        user_sessions = self._active_sessions.get(user.id, [])
        
        # Remove expired sessions
        user_sessions = [
            session for session in user_sessions
            if now - session["created_at"] < self.security_config.session_timeout
        ]
        
        if len(user_sessions) >= self.security_config.max_sessions_per_user:
            return False
            
        # Add new session
        user_sessions.append({
            "created_at": now,
            "last_activity": now,
            "ip": request.client.host
        })
        
        self._active_sessions[user.id] = user_sessions
        return True
        
    def _check_anomalies(self, request: Request, user: User) -> bool:
        """Check for anomalous behavior."""
        client_ip = request.client.host
        now = time.time()
        
        # Get anomaly score
        score = self._anomaly_scores.get(f"{user.id}:{client_ip}", 0)
        
        # Check for suspicious patterns
        if self._is_suspicious_pattern(request):
            score += 1
            
        # Check for rapid requests
        if self._is_rapid_request(user, request):
            score += 2
            
        # Check for unusual endpoints
        if self._is_unusual_endpoint(request):
            score += 1
            
        # Update score
        self._anomaly_scores[f"{user.id}:{client_ip}"] = score
        
        # Decay score over time
        if now - self._last_anomaly_check.get(f"{user.id}:{client_ip}", 0) > 3600:
            score = max(0, score - 1)
            self._anomaly_scores[f"{user.id}:{client_ip}"] = score
            self._last_anomaly_check[f"{user.id}:{client_ip}"] = now
            
        return score < 5  # Threshold for blocking
        
    def _is_suspicious_pattern(self, request: Request) -> bool:
        """Check for suspicious request patterns."""
        # Check for SQL injection attempts
        sql_patterns = [
            r"UNION\s+SELECT",
            r"OR\s+'1'='1",
            r"OR\s+1=1",
            r"';--",
            r"DROP\s+TABLE",
            r"INSERT\s+INTO"
        ]
        
        # Check query parameters
        for param in request.query_params.values():
            if any(re.search(pattern, param, re.IGNORECASE) for pattern in sql_patterns):
                return True
                
        # Check request body
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = request.json()
                if any(
                    re.search(pattern, str(value), re.IGNORECASE)
                    for value in body.values()
                    for pattern in sql_patterns
                ):
                    return True
            except:
                pass
                
        return False
        
    def _is_rapid_request(self, user: User, request: Request) -> bool:
        """Check for rapid request patterns."""
        now = time.time()
        user_requests = self._request_counts.get(user.id, [])
        
        # Check for burst of requests
        recent_requests = [
            req_time for req_time in user_requests
            if now - req_time < 5  # 5 seconds
        ]
        
        return len(recent_requests) > 10  # More than 10 requests in 5 seconds
        
    def _is_unusual_endpoint(self, request: Request) -> bool:
        """Check for unusual endpoint access patterns."""
        # Define normal endpoints for different roles
        normal_endpoints = {
            UserRole.OWNER: ["/protected/admin", "/protected/users", "/protected/roles"],
            UserRole.ADMIN: ["/protected/users", "/protected/roles"],
            UserRole.TECHNICAL_STAFF: ["/protected/infrastructure", "/protected/logs"],
            UserRole.CUSTOMER: ["/protected/profile", "/protected/data"]
        }
        
        # Check if endpoint is unusual for user's role
        return not any(
            request.url.path.startswith(endpoint)
            for endpoint in normal_endpoints.get(request.state.user.role, [])
        )
        
    def _check_2fa(self, request: Request, user: User) -> bool:
        """Check if 2FA is valid."""
        # Get 2FA token from header
        two_factor_token = request.headers.get("X-2FA-Token")
        if not two_factor_token:
            return False
            
        # Get 2FA method from header
        two_factor_method = request.headers.get("X-2FA-Method", "totp")
        
        # Verify based on method
        if two_factor_method == "totp":
            return self.two_factor_auth.verify_totp(user.id, two_factor_token)
        elif two_factor_method in ["sms", "email"]:
            return self.two_factor_auth.verify_code(user.id, two_factor_token)
            
        return False
        
    def _log_request(self, request: Request, user: User):
        """Enhanced request logging."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user.id,
            "role": user.role.value,
            "method": request.method,
            "path": request.url.path,
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "request_id": self._generate_request_id(request),
            "session_id": request.cookies.get("session_id"),
            "content_type": request.headers.get("content-type"),
            "content_length": request.headers.get("content-length"),
            "anomaly_score": self._anomaly_scores.get(f"{user.id}:{request.client.host}", 0),
            "geolocation": self._get_ip_geolocation(request.client.host) if self.security_config.enable_ip_geolocation else None
        }
        
        # Log to security log
        logger.info(
            "Security log: %s",
            json.dumps(log_data)
        )
        
    def _generate_request_id(self, request: Request) -> str:
        """Generate unique request ID."""
        data = f"{request.client.host}{request.url.path}{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()
        
    def _get_ip_geolocation(self, ip: str) -> Dict[str, Any]:
        """Get IP geolocation information."""
        # Implementation depends on your geolocation service
        return {
            "country": "Unknown",
            "city": "Unknown",
            "latitude": 0,
            "longitude": 0,
            "isp": "Unknown"
        }
        
    def _add_security_headers(self, response: Response):
        """Add security headers to response."""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Request-ID": self._generate_request_id(request),
            "X-RateLimit-Limit": str(self.rate_limits[request.state.user.role].requests_per_minute),
            "X-RateLimit-Remaining": str(
                self.rate_limits[request.state.user.role].requests_per_minute -
                len(self._request_counts.get(request.state.user.id, []))
            ),
            "X-RateLimit-Reset": str(
                int(time.time()) + self.rate_limits[request.state.user.role].window_size
            )
        }
        
        for header, value in headers.items():
            response.headers[header] = value

def get_current_user(request: Request) -> User:
    """Dependency for getting current user."""
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )
    return request.state.user

def require_permission(permission: str):
    """Decorator for requiring specific permission."""
    async def dependency(request: Request):
        user = get_current_user(request)
        if not request.app.auth_service.has_permission(user, permission):
            raise HTTPException(
                status_code=403,
                detail=f"Missing permission: {permission}"
            )
        return user
    return Depends(dependency)

def require_role(role: UserRole):
    """Decorator for requiring specific role."""
    async def dependency(request: Request):
        user = get_current_user(request)
        if user.role != role:
            raise HTTPException(
                status_code=403,
                detail=f"Required role: {role.value}"
            )
        return user
    return Depends(dependency)

def require_2fa():
    """Decorator for requiring 2FA."""
    async def dependency(request: Request):
        user = get_current_user(request)
        if not request.app.auth_middleware._check_2fa(request, user):
            raise HTTPException(
                status_code=403,
                detail="2FA required"
            )
        return user
    return Depends(dependency) 