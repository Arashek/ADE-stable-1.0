from typing import Dict, List, Optional, Set, Union, Any, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta
import json
import threading
from pathlib import Path
import yaml
from collections import defaultdict
import secrets
import ipaddress
from functools import lru_cache
import subprocess
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import io
import base64
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import asyncio
import websockets
import apscheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.combining import AndTrigger, OrTrigger
import jinja2
import markdown
from websockets.server import serve

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComponentType(Enum):
    """Types of code components."""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    FILE = "file"
    DIRECTORY = "directory"

class ReviewStatus(Enum):
    """Status of code reviews."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"

@dataclass
class CodeComponent:
    """Represents a code component with access controls."""
    id: str
    name: str
    type: ComponentType
    path: str
    description: str
    critical_level: int  # 0-5, higher means more critical
    required_reviewers: int
    allowed_roles: Set[str]
    metadata: Dict[str, Any] = None

@dataclass
class CodeReview:
    """Represents a code review."""
    id: str
    component_id: str
    reviewer_id: str
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime
    comments: List[Dict[str, Any]]
    metadata: Dict[str, Any] = None

@dataclass
class AccessViolation:
    """Represents an access violation."""
    id: str
    component_id: str
    user_id: str
    timestamp: datetime
    action: str
    details: str
    metadata: Dict[str, Any] = None

@dataclass
class ReviewChecklist:
    """Checklist items for code review."""
    id: str
    review_id: str
    items: List[Dict[str, Any]]
    status: str
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

@dataclass
class SecurityScan:
    """Security scan results."""
    id: str
    component_id: str
    scan_type: str
    findings: List[Dict[str, Any]]
    severity: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class AccessAudit:
    """Access audit log entry."""
    id: str
    user_id: str
    component_id: str
    action: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    metadata: Dict[str, Any] = None

@dataclass
class RateLimit:
    """Rate limit configuration."""
    requests_per_minute: int
    burst_size: int
    window_seconds: int = 60

@dataclass
class IPWhitelist:
    """IP whitelist configuration."""
    name: str
    description: str
    ip_ranges: List[str]
    allowed_actions: Set[str]
    metadata: Dict[str, Any] = None

@dataclass
class AutomatedCheck:
    """Automated check configuration."""
    id: str
    name: str
    description: str
    check_type: str  # "lint", "test", "security", "build", "custom"
    command: str
    required: bool
    timeout: int
    metadata: Dict[str, Any] = None

@dataclass
class CheckResult:
    """Result of an automated check."""
    check_id: str
    review_id: str
    status: str  # "passed", "failed", "error", "skipped"
    output: str
    duration: float
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class CICDIntegration:
    """CI/CD integration configuration."""
    id: str
    name: str
    provider: str  # "jenkins", "github", "gitlab", "custom"
    webhook_url: str
    secret: str
    triggers: List[str]
    metadata: Dict[str, Any] = None

@dataclass
class VisualizationConfig:
    """Configuration for data visualization."""
    type: str  # "line", "bar", "pie", "heatmap", "scatter", "box"
    title: str
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    color_scheme: Optional[str] = None
    layout: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None

@dataclass
class AnalyticsSchedule:
    """Schedule configuration for analytics."""
    id: str
    analytics_id: str
    cron_expression: str
    timezone: str
    enabled: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    metadata: Dict[str, Any] = None

@dataclass
class AnalyticsStream:
    """Real-time analytics stream configuration."""
    id: str
    analytics_id: str
    update_interval: int  # seconds
    max_points: int
    subscribers: Set[str]
    enabled: bool
    metadata: Dict[str, Any] = None

@dataclass
class WebSocketConnection:
    """WebSocket connection information."""
    id: str
    websocket: websockets.WebSocketServerProtocol
    stream_id: str
    created_at: datetime
    last_active: datetime
    metadata: Dict[str, Any] = None

@dataclass
class AnalyticsTrigger:
    """Base class for analytics triggers."""
    id: str
    analytics_id: str
    enabled: bool
    metadata: Dict[str, Any] = None

@dataclass
class CronTrigger(AnalyticsTrigger):
    """Cron-based trigger."""
    cron_expression: str
    timezone: str

@dataclass
class IntervalTrigger(AnalyticsTrigger):
    """Interval-based trigger."""
    interval_seconds: int

@dataclass
class DateTrigger(AnalyticsTrigger):
    """Date-based trigger."""
    run_date: datetime

@dataclass
class CombinedTrigger(AnalyticsTrigger):
    """Combined trigger with multiple conditions."""
    trigger_ids: List[str]
    combination_type: str  # "and" or "or"

class CodeAccessError(Exception):
    """Base class for code access errors."""
    pass

class CodeAccessControl:
    """Manages code access controls and reviews."""
    
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self._lock = threading.Lock()
        self._components: Dict[str, CodeComponent] = {}
        self._reviews: Dict[str, CodeReview] = {}
        self._violations: Dict[str, AccessViolation] = {}
        self._component_dependencies: Dict[str, Set[str]] = {}
        self._review_checklists: Dict[str, ReviewChecklist] = {}
        self._security_scans: Dict[str, SecurityScan] = {}
        self._access_audits: Dict[str, AccessAudit] = {}
        self._failed_attempts: Dict[str, List[datetime]] = {}
        self._lockout_threshold = 5
        self._lockout_duration = timedelta(minutes=15)
        self._rate_limits: Dict[str, RateLimit] = {}
        self._ip_whitelists: Dict[str, IPWhitelist] = {}
        self._request_counts: Dict[str, List[datetime]] = {}
        self._automated_checks: Dict[str, AutomatedCheck] = {}
        self._check_results: Dict[str, List[CheckResult]] = {}
        self._cicd_integrations: Dict[str, CICDIntegration] = {}
        self._visualization_configs: Dict[str, VisualizationConfig] = {}
        self._analytics_schedules: Dict[str, AnalyticsSchedule] = {}
        self._analytics_streams: Dict[str, AnalyticsStream] = {}
        self._ws_connections: Dict[str, WebSocketConnection] = {}
        self._ws_server: Optional[websockets.Server] = None
        self._ws_server_task: Optional[asyncio.Task] = None
        self._analytics_triggers: Dict[str, AnalyticsTrigger] = {}
        self._scheduler = AsyncIOScheduler()
        
        self._load_components()
        self._load_reviews()
        self._load_violations()
        self._load_dependencies()
        self._load_checklists()
        self._load_security_scans()
        self._load_access_audits()
        self._load_rate_limits()
        self._load_ip_whitelists()
        self._load_automated_checks()
        self._load_check_results()
        self._load_cicd_integrations()
        self._load_visualization_configs()
        self._load_analytics_schedules()
        self._load_analytics_streams()
        self._load_analytics_triggers()
        self._start_scheduler()
        self._start_websocket_server()
        
    def _start_scheduler(self) -> None:
        """Start the analytics scheduler."""
        self._scheduler.start()
        
    def _stop_scheduler(self) -> None:
        """Stop the analytics scheduler."""
        self._scheduler.shutdown()
        
    def _load_components(self) -> None:
        """Load code components from file."""
        components_file = self.config_dir / "code_components.yaml"
        if not components_file.exists():
            return
            
        try:
            with open(components_file) as f:
                data = yaml.safe_load(f)
                for component_data in data:
                    component = CodeComponent(
                        id=component_data["id"],
                        name=component_data["name"],
                        type=ComponentType(component_data["type"]),
                        path=component_data["path"],
                        description=component_data.get("description", ""),
                        critical_level=component_data["critical_level"],
                        required_reviewers=component_data["required_reviewers"],
                        allowed_roles=set(component_data["allowed_roles"]),
                        metadata=component_data.get("metadata", {})
                    )
                    self._components[component.id] = component
        except Exception as e:
            logger.error(f"Failed to load code components: {str(e)}")
            
    def _save_components(self) -> None:
        """Save code components to file."""
        components_file = self.config_dir / "code_components.yaml"
        with open(components_file, "w") as f:
            yaml.dump([
                {
                    "id": component.id,
                    "name": component.name,
                    "type": component.type.value,
                    "path": component.path,
                    "description": component.description,
                    "critical_level": component.critical_level,
                    "required_reviewers": component.required_reviewers,
                    "allowed_roles": list(component.allowed_roles),
                    "metadata": component.metadata
                }
                for component in self._components.values()
            ], f)
            
    def register_component(self, component_data: Dict[str, Any]) -> CodeComponent:
        """Register new code component."""
        with self._lock:
            component = CodeComponent(
                id=component_data["id"],
                name=component_data["name"],
                type=ComponentType(component_data["type"]),
                path=component_data["path"],
                description=component_data.get("description", ""),
                critical_level=component_data["critical_level"],
                required_reviewers=component_data["required_reviewers"],
                allowed_roles=set(component_data["allowed_roles"]),
                metadata=component_data.get("metadata", {})
            )
            
            if component.id in self._components:
                raise CodeAccessError(f"Component already exists: {component.id}")
                
            self._components[component.id] = component
            self._save_components()
            return component
            
    def request_code_review(
        self,
        component_id: str,
        reviewer_id: str,
        description: str
    ) -> CodeReview:
        """Create new code review request."""
        with self._lock:
            component = self._components.get(component_id)
            if not component:
                raise CodeAccessError(f"Component not found: {component_id}")
                
            review = CodeReview(
                id=f"rev_{len(self._reviews) + 1}",
                component_id=component_id,
                reviewer_id=reviewer_id,
                status=ReviewStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                comments=[],
                metadata={"description": description}
            )
            
            self._reviews[review.id] = review
            self._save_reviews()
            return review
            
    def update_review_status(
        self,
        review_id: str,
        status: ReviewStatus,
        comment: str = ""
    ) -> None:
        """Update code review status."""
        with self._lock:
            review = self._reviews.get(review_id)
            if not review:
                raise CodeAccessError(f"Review not found: {review_id}")
                
            review.status = status
            review.updated_at = datetime.now()
            if comment:
                review.comments.append({
                    "timestamp": datetime.now(),
                    "status": status.value,
                    "comment": comment
                })
                
            self._save_reviews()
            
    def add_rate_limit(
        self,
        component_id: str,
        requests_per_minute: int,
        burst_size: int = 10
    ) -> RateLimit:
        """Add rate limit for component."""
        with self._lock:
            rate_limit = RateLimit(
                requests_per_minute=requests_per_minute,
                burst_size=burst_size
            )
            self._rate_limits[component_id] = rate_limit
            self._save_rate_limits()
            return rate_limit
            
    def add_ip_whitelist(
        self,
        name: str,
        description: str,
        ip_ranges: List[str],
        allowed_actions: Set[str]
    ) -> IPWhitelist:
        """Add IP whitelist."""
        with self._lock:
            # Validate IP ranges
            for ip_range in ip_ranges:
                try:
                    ipaddress.ip_network(ip_range)
                except ValueError:
                    raise CodeAccessError(f"Invalid IP range: {ip_range}")
                    
            whitelist = IPWhitelist(
                name=name,
                description=description,
                ip_ranges=ip_ranges,
                allowed_actions=allowed_actions,
                metadata={"created_at": datetime.now().isoformat()}
            )
            
            self._ip_whitelists[name] = whitelist
            self._save_ip_whitelists()
            return whitelist
            
    @lru_cache(maxsize=1000)
    def _is_ip_whitelisted(
        self,
        ip_address: str,
        action: str
    ) -> bool:
        """Check if IP is whitelisted for action."""
        try:
            ip = ipaddress.ip_address(ip_address)
            for whitelist in self._ip_whitelists.values():
                if action in whitelist.allowed_actions:
                    for ip_range in whitelist.ip_ranges:
                        if ip in ipaddress.ip_network(ip_range):
                            return True
        except ValueError:
            return False
        return False
        
    def _check_rate_limit(
        self,
        component_id: str,
        ip_address: str
    ) -> Tuple[bool, Optional[str]]:
        """Check rate limit for component and IP."""
        rate_limit = self._rate_limits.get(component_id)
        if not rate_limit:
            return True, None
            
        key = f"{component_id}:{ip_address}"
        now = datetime.now()
        window_start = now - timedelta(seconds=rate_limit.window_seconds)
        
        # Get request counts in window
        requests = [
            t for t in self._request_counts.get(key, [])
            if t > window_start
        ]
        
        # Check burst limit
        if len(requests) >= rate_limit.burst_size:
            return False, "Burst limit exceeded"
            
        # Check rate limit
        if len(requests) >= rate_limit.requests_per_minute:
            return False, "Rate limit exceeded"
            
        # Update request counts
        if key not in self._request_counts:
            self._request_counts[key] = []
        self._request_counts[key].append(now)
        
        # Clean up old requests
        self._request_counts[key] = [
            t for t in self._request_counts[key]
            if t > window_start
        ]
        
        return True, None
        
    def check_access(
        self,
        user_id: str,
        component_id: str,
        user_roles: Set[str],
        ip_address: str,
        user_agent: str,
        action: str = "access"
    ) -> bool:
        """Check if user has access to component with enhanced security."""
        # Check IP whitelist
        if self._is_ip_whitelisted(ip_address, action):
            return True
            
        # Check rate limit
        allowed, reason = self._check_rate_limit(component_id, ip_address)
        if not allowed:
            self._record_violation(
                component_id,
                user_id,
                "rate_limit_exceeded",
                reason
            )
            return False
            
        # Check for lockout
        if self._is_user_locked_out(user_id):
            self._record_violation(
                component_id,
                user_id,
                "access_denied",
                "User is temporarily locked out"
            )
            return False
            
        # Check basic access
        if not super().check_access(user_id, component_id, user_roles):
            self._record_failed_attempt(user_id)
            return False
            
        # Record successful access
        self._record_access_audit(
            user_id,
            component_id,
            "access_granted",
            ip_address,
            user_agent
        )
        
        # Reset failed attempts on successful access
        if user_id in self._failed_attempts:
            del self._failed_attempts[user_id]
            
        return True
        
    def _is_user_locked_out(self, user_id: str) -> bool:
        """Check if user is temporarily locked out."""
        if user_id not in self._failed_attempts:
            return False
            
        attempts = self._failed_attempts[user_id]
        cutoff = datetime.now() - self._lockout_duration
        
        # Remove old attempts
        attempts = [t for t in attempts if t > cutoff]
        self._failed_attempts[user_id] = attempts
        
        # Check if user is locked out
        if len(attempts) >= self._lockout_threshold:
            return True
            
        return False
        
    def _record_failed_attempt(self, user_id: str) -> None:
        """Record failed access attempt."""
        if user_id not in self._failed_attempts:
            self._failed_attempts[user_id] = []
            
        self._failed_attempts[user_id].append(datetime.now())
        
    def get_component_reviews(self, component_id: str) -> List[CodeReview]:
        """Get all reviews for component."""
        return [
            review for review in self._reviews.values()
            if review.component_id == component_id
        ]
        
    def get_active_reviews(self) -> List[CodeReview]:
        """Get all active reviews."""
        return [
            review for review in self._reviews.values()
            if review.status in [ReviewStatus.PENDING, ReviewStatus.IN_PROGRESS]
        ]
        
    def get_critical_components(self) -> List[CodeComponent]:
        """Get all critical components."""
        return [
            component for component in self._components.values()
            if component.critical_level >= 4
        ]
        
    def get_violations(
        self,
        component_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[AccessViolation]:
        """Get access violations with optional filtering."""
        violations = self._violations.values()
        
        if component_id:
            violations = [
                v for v in violations
                if v.component_id == component_id
            ]
            
        if user_id:
            violations = [
                v for v in violations
                if v.user_id == user_id
            ]
            
        return list(violations)
        
    def _record_violation(
        self,
        component_id: str,
        user_id: str,
        action: str,
        details: str
    ) -> None:
        """Record access violation."""
        violation = AccessViolation(
            id=f"viol_{len(self._violations) + 1}",
            component_id=component_id,
            user_id=user_id,
            timestamp=datetime.now(),
            action=action,
            details=details
        )
        
        self._violations[violation.id] = violation
        self._save_violations()
        
    def _load_reviews(self) -> None:
        """Load code reviews from file."""
        reviews_file = self.config_dir / "code_reviews.yaml"
        if not reviews_file.exists():
            return
            
        try:
            with open(reviews_file) as f:
                data = yaml.safe_load(f)
                for review_data in data:
                    review = CodeReview(
                        id=review_data["id"],
                        component_id=review_data["component_id"],
                        reviewer_id=review_data["reviewer_id"],
                        status=ReviewStatus(review_data["status"]),
                        created_at=datetime.fromisoformat(review_data["created_at"]),
                        updated_at=datetime.fromisoformat(review_data["updated_at"]),
                        comments=review_data["comments"],
                        metadata=review_data.get("metadata", {})
                    )
                    self._reviews[review.id] = review
        except Exception as e:
            logger.error(f"Failed to load code reviews: {str(e)}")
            
    def _save_reviews(self) -> None:
        """Save code reviews to file."""
        reviews_file = self.config_dir / "code_reviews.yaml"
        with open(reviews_file, "w") as f:
            yaml.dump([
                {
                    "id": review.id,
                    "component_id": review.component_id,
                    "reviewer_id": review.reviewer_id,
                    "status": review.status.value,
                    "created_at": review.created_at.isoformat(),
                    "updated_at": review.updated_at.isoformat(),
                    "comments": review.comments,
                    "metadata": review.metadata
                }
                for review in self._reviews.values()
            ], f)
            
    def _load_violations(self) -> None:
        """Load access violations from file."""
        violations_file = self.config_dir / "access_violations.yaml"
        if not violations_file.exists():
            return
            
        try:
            with open(violations_file) as f:
                data = yaml.safe_load(f)
                for violation_data in data:
                    violation = AccessViolation(
                        id=violation_data["id"],
                        component_id=violation_data["component_id"],
                        user_id=violation_data["user_id"],
                        timestamp=datetime.fromisoformat(violation_data["timestamp"]),
                        action=violation_data["action"],
                        details=violation_data["details"],
                        metadata=violation_data.get("metadata", {})
                    )
                    self._violations[violation.id] = violation
        except Exception as e:
            logger.error(f"Failed to load access violations: {str(e)}")
            
    def _save_violations(self) -> None:
        """Save access violations to file."""
        violations_file = self.config_dir / "access_violations.yaml"
        with open(violations_file, "w") as f:
            yaml.dump([
                {
                    "id": violation.id,
                    "component_id": violation.component_id,
                    "user_id": violation.user_id,
                    "timestamp": violation.timestamp.isoformat(),
                    "action": violation.action,
                    "details": violation.details,
                    "metadata": violation.metadata
                }
                for violation in self._violations.values()
            ], f)
            
    def _load_dependencies(self) -> None:
        """Load component dependencies from file."""
        deps_file = self.config_dir / "component_dependencies.yaml"
        if not deps_file.exists():
            return
            
        try:
            with open(deps_file) as f:
                data = yaml.safe_load(f)
                for component_id, deps in data.items():
                    self._component_dependencies[component_id] = set(deps)
        except Exception as e:
            logger.error(f"Failed to load component dependencies: {str(e)}")
            
    def _save_dependencies(self) -> None:
        """Save component dependencies to file."""
        deps_file = self.config_dir / "component_dependencies.yaml"
        with open(deps_file, "w") as f:
            yaml.dump(
                {
                    component_id: list(deps)
                    for component_id, deps in self._component_dependencies.items()
                },
                f
            )
            
    def create_review_checklist(
        self,
        review_id: str,
        items: List[Dict[str, Any]]
    ) -> ReviewChecklist:
        """Create checklist for code review."""
        with self._lock:
            review = self._reviews.get(review_id)
            if not review:
                raise CodeAccessError(f"Review not found: {review_id}")
                
            checklist = ReviewChecklist(
                id=f"check_{len(self._review_checklists) + 1}",
                review_id=review_id,
                items=items,
                status="pending",
                metadata={"created_at": datetime.now().isoformat()}
            )
            
            self._review_checklists[checklist.id] = checklist
            self._save_checklists()
            return checklist
            
    def update_checklist_item(
        self,
        checklist_id: str,
        item_index: int,
        status: str,
        comment: str = ""
    ) -> None:
        """Update checklist item status."""
        with self._lock:
            checklist = self._review_checklists.get(checklist_id)
            if not checklist:
                raise CodeAccessError(f"Checklist not found: {checklist_id}")
                
            if item_index >= len(checklist.items):
                raise CodeAccessError("Invalid item index")
                
            checklist.items[item_index].update({
                "status": status,
                "completed_at": datetime.now().isoformat(),
                "comment": comment
            })
            
            # Check if all items are completed
            if all(item["status"] == "completed" for item in checklist.items):
                checklist.status = "completed"
                checklist.completed_at = datetime.now()
                
            self._save_checklists()
            
    def record_security_scan(
        self,
        component_id: str,
        scan_type: str,
        findings: List[Dict[str, Any]],
        severity: str
    ) -> SecurityScan:
        """Record security scan results."""
        with self._lock:
            component = self._components.get(component_id)
            if not component:
                raise CodeAccessError(f"Component not found: {component_id}")
                
            scan = SecurityScan(
                id=f"scan_{len(self._security_scans) + 1}",
                component_id=component_id,
                scan_type=scan_type,
                findings=findings,
                severity=severity,
                timestamp=datetime.now(),
                metadata={"scan_version": "1.0"}
            )
            
            self._security_scans[scan.id] = scan
            self._save_security_scans()
            return scan
            
    def record_access_audit(
        self,
        user_id: str,
        component_id: str,
        action: str,
        ip_address: str,
        user_agent: str
    ) -> AccessAudit:
        """Record access audit log entry."""
        with self._lock:
            audit = AccessAudit(
                id=f"audit_{len(self._access_audits) + 1}",
                user_id=user_id,
                component_id=component_id,
                action=action,
                timestamp=datetime.now(),
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={"session_id": secrets.token_urlsafe(16)}
            )
            
            self._access_audits[audit.id] = audit
            self._save_access_audits()
            return audit
            
    def get_security_findings(
        self,
        component_id: str,
        severity: Optional[str] = None
    ) -> List[SecurityScan]:
        """Get security scan findings for component."""
        findings = [
            scan for scan in self._security_scans.values()
            if scan.component_id == component_id
        ]
        
        if severity:
            findings = [
                scan for scan in findings
                if scan.severity == severity
            ]
            
        return findings
        
    def get_access_audits(
        self,
        user_id: Optional[str] = None,
        component_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AccessAudit]:
        """Get access audit logs with filtering."""
        audits = self._access_audits.values()
        
        if user_id:
            audits = [a for a in audits if a.user_id == user_id]
            
        if component_id:
            audits = [a for a in audits if a.component_id == component_id]
            
        if start_time:
            audits = [a for a in audits if a.timestamp >= start_time]
            
        if end_time:
            audits = [a for a in audits if a.timestamp <= end_time]
            
        return list(audits)
        
    def _load_checklists(self) -> None:
        """Load review checklists from file."""
        checklists_file = self.config_dir / "review_checklists.yaml"
        if not checklists_file.exists():
            return
            
        try:
            with open(checklists_file) as f:
                data = yaml.safe_load(f)
                for checklist_data in data:
                    checklist = ReviewChecklist(
                        id=checklist_data["id"],
                        review_id=checklist_data["review_id"],
                        items=checklist_data["items"],
                        status=checklist_data["status"],
                        completed_at=datetime.fromisoformat(checklist_data["completed_at"]) if checklist_data.get("completed_at") else None,
                        metadata=checklist_data.get("metadata", {})
                    )
                    self._review_checklists[checklist.id] = checklist
        except Exception as e:
            logger.error(f"Failed to load review checklists: {str(e)}")
            
    def _save_checklists(self) -> None:
        """Save review checklists to file."""
        checklists_file = self.config_dir / "review_checklists.yaml"
        with open(checklists_file, "w") as f:
            yaml.dump([
                {
                    "id": checklist.id,
                    "review_id": checklist.review_id,
                    "items": checklist.items,
                    "status": checklist.status,
                    "completed_at": checklist.completed_at.isoformat() if checklist.completed_at else None,
                    "metadata": checklist.metadata
                }
                for checklist in self._review_checklists.values()
            ], f)
            
    def _load_security_scans(self) -> None:
        """Load security scans from file."""
        scans_file = self.config_dir / "security_scans.yaml"
        if not scans_file.exists():
            return
            
        try:
            with open(scans_file) as f:
                data = yaml.safe_load(f)
                for scan_data in data:
                    scan = SecurityScan(
                        id=scan_data["id"],
                        component_id=scan_data["component_id"],
                        scan_type=scan_data["scan_type"],
                        findings=scan_data["findings"],
                        severity=scan_data["severity"],
                        timestamp=datetime.fromisoformat(scan_data["timestamp"]),
                        metadata=scan_data.get("metadata", {})
                    )
                    self._security_scans[scan.id] = scan
        except Exception as e:
            logger.error(f"Failed to load security scans: {str(e)}")
            
    def _save_security_scans(self) -> None:
        """Save security scans to file."""
        scans_file = self.config_dir / "security_scans.yaml"
        with open(scans_file, "w") as f:
            yaml.dump([
                {
                    "id": scan.id,
                    "component_id": scan.component_id,
                    "scan_type": scan.scan_type,
                    "findings": scan.findings,
                    "severity": scan.severity,
                    "timestamp": scan.timestamp.isoformat(),
                    "metadata": scan.metadata
                }
                for scan in self._security_scans.values()
            ], f)
            
    def _load_access_audits(self) -> None:
        """Load access audits from file."""
        audits_file = self.config_dir / "access_audits.yaml"
        if not audits_file.exists():
            return
            
        try:
            with open(audits_file) as f:
                data = yaml.safe_load(f)
                for audit_data in data:
                    audit = AccessAudit(
                        id=audit_data["id"],
                        user_id=audit_data["user_id"],
                        component_id=audit_data["component_id"],
                        action=audit_data["action"],
                        timestamp=datetime.fromisoformat(audit_data["timestamp"]),
                        ip_address=audit_data["ip_address"],
                        user_agent=audit_data["user_agent"],
                        metadata=audit_data.get("metadata", {})
                    )
                    self._access_audits[audit.id] = audit
        except Exception as e:
            logger.error(f"Failed to load access audits: {str(e)}")
            
    def _save_access_audits(self) -> None:
        """Save access audits to file."""
        audits_file = self.config_dir / "access_audits.yaml"
        with open(audits_file, "w") as f:
            yaml.dump([
                {
                    "id": audit.id,
                    "user_id": audit.user_id,
                    "component_id": audit.component_id,
                    "action": audit.action,
                    "timestamp": audit.timestamp.isoformat(),
                    "ip_address": audit.ip_address,
                    "user_agent": audit.user_agent,
                    "metadata": audit.metadata
                }
                for audit in self._access_audits.values()
            ], f)
            
    def _load_rate_limits(self) -> None:
        """Load rate limits from file."""
        limits_file = self.config_dir / "rate_limits.yaml"
        if not limits_file.exists():
            return
            
        try:
            with open(limits_file) as f:
                data = yaml.safe_load(f)
                for component_id, limit_data in data.items():
                    rate_limit = RateLimit(
                        requests_per_minute=limit_data["requests_per_minute"],
                        burst_size=limit_data["burst_size"],
                        window_seconds=limit_data.get("window_seconds", 60)
                    )
                    self._rate_limits[component_id] = rate_limit
        except Exception as e:
            logger.error(f"Failed to load rate limits: {str(e)}")
            
    def _save_rate_limits(self) -> None:
        """Save rate limits to file."""
        limits_file = self.config_dir / "rate_limits.yaml"
        with open(limits_file, "w") as f:
            yaml.dump(
                {
                    component_id: {
                        "requests_per_minute": limit.requests_per_minute,
                        "burst_size": limit.burst_size,
                        "window_seconds": limit.window_seconds
                    }
                    for component_id, limit in self._rate_limits.items()
                },
                f
            )
            
    def _load_ip_whitelists(self) -> None:
        """Load IP whitelists from file."""
        whitelists_file = self.config_dir / "ip_whitelists.yaml"
        if not whitelists_file.exists():
            return
            
        try:
            with open(whitelists_file) as f:
                data = yaml.safe_load(f)
                for name, whitelist_data in data.items():
                    whitelist = IPWhitelist(
                        name=name,
                        description=whitelist_data["description"],
                        ip_ranges=whitelist_data["ip_ranges"],
                        allowed_actions=set(whitelist_data["allowed_actions"]),
                        metadata=whitelist_data.get("metadata", {})
                    )
                    self._ip_whitelists[name] = whitelist
        except Exception as e:
            logger.error(f"Failed to load IP whitelists: {str(e)}")
            
    def _save_ip_whitelists(self) -> None:
        """Save IP whitelists to file."""
        whitelists_file = self.config_dir / "ip_whitelists.yaml"
        with open(whitelists_file, "w") as f:
            yaml.dump(
                {
                    name: {
                        "description": whitelist.description,
                        "ip_ranges": whitelist.ip_ranges,
                        "allowed_actions": list(whitelist.allowed_actions),
                        "metadata": whitelist.metadata
                    }
                    for name, whitelist in self._ip_whitelists.items()
                },
                f
            )
            
    def _load_automated_checks(self) -> None:
        """Load automated checks from file."""
        checks_file = self.config_dir / "automated_checks.yaml"
        if not checks_file.exists():
            return
            
        try:
            with open(checks_file) as f:
                data = yaml.safe_load(f)
                for check_data in data:
                    check = AutomatedCheck(
                        id=check_data["id"],
                        name=check_data["name"],
                        description=check_data["description"],
                        check_type=check_data["check_type"],
                        command=check_data["command"],
                        required=check_data["required"],
                        timeout=check_data["timeout"],
                        metadata=check_data.get("metadata", {})
                    )
                    self._automated_checks[check.id] = check
        except Exception as e:
            logger.error(f"Failed to load automated checks: {str(e)}")
            
    def _save_automated_checks(self) -> None:
        """Save automated checks to file."""
        checks_file = self.config_dir / "automated_checks.yaml"
        with open(checks_file, "w") as f:
            yaml.dump([
                {
                    "id": check.id,
                    "name": check.name,
                    "description": check.description,
                    "check_type": check.check_type,
                    "command": check.command,
                    "required": check.required,
                    "timeout": check.timeout,
                    "metadata": check.metadata
                }
                for check in self._automated_checks.values()
            ], f)
            
    def _load_check_results(self) -> None:
        """Load check results from file."""
        results_file = self.config_dir / "check_results.yaml"
        if not results_file.exists():
            return
            
        try:
            with open(results_file) as f:
                data = yaml.safe_load(f)
                for review_id, results_data in data.items():
                    results = []
                    for result_data in results_data:
                        result = CheckResult(
                            check_id=result_data["check_id"],
                            review_id=review_id,
                            status=result_data["status"],
                            output=result_data["output"],
                            duration=result_data["duration"],
                            timestamp=datetime.fromisoformat(result_data["timestamp"]),
                            metadata=result_data.get("metadata", {})
                        )
                        results.append(result)
                    self._check_results[review_id] = results
        except Exception as e:
            logger.error(f"Failed to load check results: {str(e)}")
            
    def _save_check_results(self) -> None:
        """Save check results to file."""
        results_file = self.config_dir / "check_results.yaml"
        with open(results_file, "w") as f:
            yaml.dump(
                {
                    review_id: [
                        {
                            "check_id": result.check_id,
                            "status": result.status,
                            "output": result.output,
                            "duration": result.duration,
                            "timestamp": result.timestamp.isoformat(),
                            "metadata": result.metadata
                        }
                        for result in results
                    ]
                    for review_id, results in self._check_results.items()
                },
                f
            )
            
    def _load_cicd_integrations(self) -> None:
        """Load CI/CD integrations from file."""
        integrations_file = self.config_dir / "cicd_integrations.yaml"
        if not integrations_file.exists():
            return
            
        try:
            with open(integrations_file) as f:
                data = yaml.safe_load(f)
                for integration_data in data:
                    integration = CICDIntegration(
                        id=integration_data["id"],
                        name=integration_data["name"],
                        provider=integration_data["provider"],
                        webhook_url=integration_data["webhook_url"],
                        secret=integration_data["secret"],
                        triggers=integration_data["triggers"],
                        metadata=integration_data.get("metadata", {})
                    )
                    self._cicd_integrations[integration.id] = integration
        except Exception as e:
            logger.error(f"Failed to load CI/CD integrations: {str(e)}")
            
    def _save_cicd_integrations(self) -> None:
        """Save CI/CD integrations to file."""
        integrations_file = self.config_dir / "cicd_integrations.yaml"
        with open(integrations_file, "w") as f:
            yaml.dump([
                {
                    "id": integration.id,
                    "name": integration.name,
                    "provider": integration.provider,
                    "webhook_url": integration.webhook_url,
                    "secret": integration.secret,
                    "triggers": integration.triggers,
                    "metadata": integration.metadata
                }
                for integration in self._cicd_integrations.values()
            ], f)
            
    def add_automated_check(
        self,
        name: str,
        description: str,
        check_type: str,
        command: str,
        required: bool = True,
        timeout: int = 300
    ) -> AutomatedCheck:
        """Add automated check."""
        with self._lock:
            check = AutomatedCheck(
                id=f"check_{len(self._automated_checks) + 1}",
                name=name,
                description=description,
                check_type=check_type,
                command=command,
                required=required,
                timeout=timeout,
                metadata={"created_at": datetime.now().isoformat()}
            )
            
            self._automated_checks[check.id] = check
            self._save_automated_checks()
            return check
            
    def add_cicd_integration(
        self,
        name: str,
        provider: str,
        webhook_url: str,
        secret: str,
        triggers: List[str]
    ) -> CICDIntegration:
        """Add CI/CD integration."""
        with self._lock:
            integration = CICDIntegration(
                id=f"cicd_{len(self._cicd_integrations) + 1}",
                name=name,
                provider=provider,
                webhook_url=webhook_url,
                secret=secret,
                triggers=triggers,
                metadata={"created_at": datetime.now().isoformat()}
            )
            
            self._cicd_integrations[integration.id] = integration
            self._save_cicd_integrations()
            return integration
            
    def run_automated_checks(
        self,
        review_id: str,
        component_id: str,
        working_dir: str
    ) -> List[CheckResult]:
        """Run automated checks for review."""
        results = []
        review = self._reviews.get(review_id)
        if not review:
            raise CodeAccessError(f"Review not found: {review_id}")
            
        component = self._components.get(component_id)
        if not component:
            raise CodeAccessError(f"Component not found: {component_id}")
            
        # Get relevant checks based on component type
        relevant_checks = [
            check for check in self._automated_checks.values()
            if self._is_check_relevant(check, component)
        ]
        
        for check in relevant_checks:
            try:
                result = self._run_check(check, working_dir)
                result.review_id = review_id
                results.append(result)
                
                # Update review status based on check results
                if check.required and result.status != "passed":
                    review.status = ReviewStatus.REJECTED
                    review.comments.append({
                        "timestamp": datetime.now(),
                        "type": "automated_check",
                        "check_id": check.id,
                        "status": result.status,
                        "message": f"Required check failed: {check.name}"
                    })
                    
            except Exception as e:
                logger.error(f"Failed to run check {check.name}: {str(e)}")
                result = CheckResult(
                    check_id=check.id,
                    review_id=review_id,
                    status="error",
                    output=str(e),
                    duration=0,
                    timestamp=datetime.now()
                )
                results.append(result)
                
        self._save_check_results()
        self._save_reviews()
        return results
        
    def _run_check(
        self,
        check: AutomatedCheck,
        working_dir: str
    ) -> CheckResult:
        """Run a single automated check."""
        start_time = datetime.now()
        
        try:
            # Execute check command
            process = subprocess.Popen(
                check.command,
                shell=True,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for completion with timeout
            stdout, stderr = process.communicate(timeout=check.timeout)
            
            # Determine status
            if process.returncode == 0:
                status = "passed"
            else:
                status = "failed"
                
            duration = (datetime.now() - start_time).total_seconds()
            
            return CheckResult(
                check_id=check.id,
                review_id="",  # Will be set by caller
                status=status,
                output=stdout + stderr,
                duration=duration,
                timestamp=datetime.now(),
                metadata={
                    "return_code": process.returncode,
                    "command": check.command
                }
            )
            
        except subprocess.TimeoutExpired:
            process.kill()
            return CheckResult(
                check_id=check.id,
                review_id="",  # Will be set by caller
                status="error",
                output="Check timed out",
                duration=check.timeout,
                timestamp=datetime.now()
            )
            
    def _is_check_relevant(
        self,
        check: AutomatedCheck,
        component: CodeComponent
    ) -> bool:
        """Determine if check is relevant for component."""
        # Check component type specific rules
        if check.check_type == "lint":
            return component.type in [ComponentType.MODULE, ComponentType.FILE]
        elif check.check_type == "test":
            return component.type in [ComponentType.MODULE, ComponentType.CLASS]
        elif check.check_type == "security":
            return component.critical_level >= 3
        elif check.check_type == "build":
            return component.type in [ComponentType.MODULE, ComponentType.FILE]
        elif check.check_type == "custom":
            return True
            
        return False
        
    def trigger_cicd_pipeline(
        self,
        integration_id: str,
        review_id: str,
        component_id: str,
        trigger_type: str
    ) -> bool:
        """Trigger CI/CD pipeline for review."""
        integration = self._cicd_integrations.get(integration_id)
        if not integration:
            raise CodeAccessError(f"Integration not found: {integration_id}")
            
        if trigger_type not in integration.triggers:
            raise CodeAccessError(f"Invalid trigger type: {trigger_type}")
            
        # Prepare webhook payload
        payload = {
            "review_id": review_id,
            "component_id": component_id,
            "trigger_type": trigger_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add provider-specific headers
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Secret": integration.secret
        }
        
        try:
            # Send webhook request
            response = requests.post(
                integration.webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # Record successful trigger
                self._record_cicd_trigger(
                    integration_id,
                    review_id,
                    trigger_type,
                    response.json()
                )
                return True
            else:
                logger.error(
                    f"Failed to trigger CI/CD pipeline: {response.status_code}"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error triggering CI/CD pipeline: {str(e)}")
            return False
            
    def _record_cicd_trigger(
        self,
        integration_id: str,
        review_id: str,
        trigger_type: str,
        response_data: Dict[str, Any]
    ) -> None:
        """Record CI/CD trigger result."""
        integration = self._cicd_integrations[integration_id]
        if "triggers" not in integration.metadata:
            integration.metadata["triggers"] = []
            
        integration.metadata["triggers"].append({
            "review_id": review_id,
            "trigger_type": trigger_type,
            "timestamp": datetime.now().isoformat(),
            "response": response_data
        })
        
        self._save_cicd_integrations()
        
    def add_visualization_config(
        self,
        analytics_id: str,
        config: VisualizationConfig
    ) -> None:
        """Add visualization configuration."""
        with self._lock:
            self._visualization_configs[analytics_id] = config
            self._save_visualization_configs()
            
    def create_analytics_schedule(
        self,
        analytics_id: str,
        cron_expression: str,
        timezone: str = "UTC"
    ) -> AnalyticsSchedule:
        """Create analytics schedule."""
        with self._lock:
            schedule = AnalyticsSchedule(
                id=f"schedule_{len(self._analytics_schedules) + 1}",
                analytics_id=analytics_id,
                cron_expression=cron_expression,
                timezone=timezone,
                enabled=True,
                metadata={"created_at": datetime.now().isoformat()}
            )
            
            self._analytics_schedules[schedule.id] = schedule
            self._save_analytics_schedules()
            
            # Add job to scheduler
            self._scheduler.add_job(
                self._run_scheduled_analytics,
                CronTrigger.from_crontab(cron_expression, timezone=timezone),
                id=schedule.id,
                args=[schedule.id]
            )
            
            return schedule
            
    def create_analytics_stream(
        self,
        analytics_id: str,
        update_interval: int,
        max_points: int = 100
    ) -> AnalyticsStream:
        """Create real-time analytics stream."""
        with self._lock:
            stream = AnalyticsStream(
                id=f"stream_{len(self._analytics_streams) + 1}",
                analytics_id=analytics_id,
                update_interval=update_interval,
                max_points=max_points,
                subscribers=set(),
                enabled=True,
                metadata={"created_at": datetime.now().isoformat()}
            )
            
            self._analytics_streams[stream.id] = stream
            self._save_analytics_streams()
            
            # Start stream task
            asyncio.create_task(self._run_analytics_stream(stream.id))
            
            return stream
            
    async def _run_analytics_stream(self, stream_id: str) -> None:
        """Run real-time analytics stream."""
        stream = self._analytics_streams.get(stream_id)
        if not stream or not stream.enabled:
            return
            
        while stream.enabled:
            try:
                # Run analytics
                result = self.run_analytics(
                    stream.analytics_id,
                    datetime.now() - timedelta(hours=1),
                    datetime.now()
                )
                
                # Update stream data
                if stream_id in self._analytics_results:
                    results = self._analytics_results[stream_id]
                    results.append(result)
                    
                    # Trim old results
                    if len(results) > stream.max_points:
                        results = results[-stream.max_points:]
                        self._analytics_results[stream_id] = results
                        
                    # Notify subscribers
                    await self._notify_stream_subscribers(stream_id, result)
                    
            except Exception as e:
                logger.error(f"Error in analytics stream {stream_id}: {str(e)}")
                
            await asyncio.sleep(stream.update_interval)
            
    async def _notify_stream_subscribers(
        self,
        stream_id: str,
        result: AnalyticsResult
    ) -> None:
        """Notify stream subscribers of new data."""
        stream = self._analytics_streams.get(stream_id)
        if not stream:
            return
            
        message = {
            "type": "analytics_update",
            "stream_id": stream_id,
            "data": result.data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to all subscribers
        for subscriber_id in stream.subscribers:
            connection = self._ws_connections.get(subscriber_id)
            if connection and connection.stream_id == stream_id:
                try:
                    await connection.websocket.send(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending to subscriber {subscriber_id}: {str(e)}")
                    
    async def _run_scheduled_analytics(self, schedule_id: str) -> None:
        """Run scheduled analytics."""
        schedule = self._analytics_schedules.get(schedule_id)
        if not schedule or not schedule.enabled:
            return
            
        try:
            # Run analytics
            result = self.run_analytics(schedule.analytics_id)
            
            # Update schedule metadata
            schedule.last_run = datetime.now()
            schedule.next_run = self._scheduler.get_job(schedule_id).next_run_time
            self._save_analytics_schedules()
            
            # Export results if configured
            if schedule.metadata.get("export_enabled", False):
                self.export_analytics_results(
                    schedule.analytics_id,
                    format=schedule.metadata.get("export_format", "csv")
                )
                
        except Exception as e:
            logger.error(f"Error in scheduled analytics {schedule_id}: {str(e)}")
            
    def _generate_visualization(
        self,
        data: Dict[str, Any],
        config: VisualizationConfig
    ) -> str:
        """Generate visualization based on configuration."""
        if config.type == "radar":
            return self._create_radar_chart(data, config)
        elif config.type == "bubble":
            return self._create_bubble_plot(data, config)
        elif config.type == "violin":
            return self._create_violin_plot(data, config)
        elif config.type == "sunburst":
            return self._create_sunburst_chart(data, config)
        else:
            return super()._generate_visualization(data, config)
            
    def _create_radar_chart(
        self,
        data: Dict[str, Any],
        config: VisualizationConfig
    ) -> str:
        """Create radar chart."""
        if "categories" in data and "values" in data:
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=data["values"],
                theta=data["categories"],
                fill='toself',
                name=config.title
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(data["values"])]
                    )
                ),
                showlegend=False,
                title=config.title
            )
            
            return fig.to_image(format="png")
            
    def _create_bubble_plot(
        self,
        data: Dict[str, Any],
        config: VisualizationConfig
    ) -> str:
        """Create bubble plot."""
        if "points" in data:
            df = pd.DataFrame(data["points"])
            fig = px.scatter(
                df,
                x="x",
                y="y",
                size="size",
                color="color",
                hover_data=["label"],
                title=config.title
            )
            
            return fig.to_image(format="png")
            
    def _create_violin_plot(
        self,
        data: Dict[str, Any],
        config: VisualizationConfig
    ) -> str:
        """Create violin plot."""
        if "groups" in data:
            df = pd.DataFrame(data["groups"])
            fig = px.violin(
                df,
                y="values",
                x="group",
                title=config.title
            )
            
            return fig.to_image(format="png")
            
    def _create_sunburst_chart(
        self,
        data: Dict[str, Any],
        config: VisualizationConfig
    ) -> str:
        """Create sunburst chart."""
        if "hierarchy" in data:
            fig = px.sunburst(
                data["hierarchy"],
                path=["level1", "level2", "level3"],
                values="value",
                title=config.title
            )
            
            return fig.to_image(format="png")
            
    def export_analytics_results(
        self,
        analytics_id: str,
        format: str = "csv",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> str:
        """Export analytics results in specified format."""
        results = self._analytics_results.get(analytics_id, [])
        
        if start_time:
            results = [r for r in results if r.timestamp >= start_time]
        if end_time:
            results = [r for r in results if r.timestamp <= end_time]
            
        if format == "html":
            return self._export_html(results)
        elif format == "markdown":
            return self._export_markdown(results)
        else:
            return super().export_analytics_results(analytics_id, format, start_time, end_time)
            
    def _export_html(self, results: List[AnalyticsResult]) -> str:
        """Export results to HTML."""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Analytics Results</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
            <h1>Analytics Results</h1>
            <table>
                <tr>
                    <th>Timestamp</th>
                    <th>Data</th>
                </tr>
                {% for result in results %}
                <tr>
                    <td>{{ result.timestamp }}</td>
                    <td>{{ result.data | tojson }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """
        
        return jinja2.Template(template).render(
            results=results
        )
        
    def _export_markdown(self, results: List[AnalyticsResult]) -> str:
        """Export results to Markdown."""
        markdown_content = "# Analytics Results\n\n"
        markdown_content += "| Timestamp | Data |\n"
        markdown_content += "|-----------|------|\n"
        
        for result in results:
            markdown_content += f"| {result.timestamp} | {json.dumps(result.data)} |\n"
            
        return markdown_content
        
    def create_analytics_trigger(
        self,
        analytics_id: str,
        trigger_type: str,
        **kwargs
    ) -> AnalyticsTrigger:
        """Create analytics trigger."""
        with self._lock:
            trigger_id = f"trigger_{len(self._analytics_triggers) + 1}"
            
            if trigger_type == "cron":
                trigger = CronTrigger(
                    id=trigger_id,
                    analytics_id=analytics_id,
                    enabled=True,
                    cron_expression=kwargs["cron_expression"],
                    timezone=kwargs.get("timezone", "UTC")
                )
            elif trigger_type == "interval":
                trigger = IntervalTrigger(
                    id=trigger_id,
                    analytics_id=analytics_id,
                    enabled=True,
                    interval_seconds=kwargs["interval_seconds"]
                )
            elif trigger_type == "date":
                trigger = DateTrigger(
                    id=trigger_id,
                    analytics_id=analytics_id,
                    enabled=True,
                    run_date=kwargs["run_date"]
                )
            elif trigger_type == "combined":
                trigger = CombinedTrigger(
                    id=trigger_id,
                    analytics_id=analytics_id,
                    enabled=True,
                    trigger_ids=kwargs["trigger_ids"],
                    combination_type=kwargs["combination_type"]
                )
            else:
                raise CodeAccessError(f"Invalid trigger type: {trigger_type}")
                
            self._analytics_triggers[trigger.id] = trigger
            self._save_analytics_triggers()
            
            # Add job to scheduler
            self._add_trigger_to_scheduler(trigger)
            
            return trigger
            
    def _add_trigger_to_scheduler(self, trigger: AnalyticsTrigger) -> None:
        """Add trigger to scheduler."""
        if isinstance(trigger, CronTrigger):
            self._scheduler.add_job(
                self._run_scheduled_analytics,
                CronTrigger.from_crontab(trigger.cron_expression, timezone=trigger.timezone),
                id=trigger.id,
                args=[trigger.id]
            )
        elif isinstance(trigger, IntervalTrigger):
            self._scheduler.add_job(
                self._run_scheduled_analytics,
                IntervalTrigger(seconds=trigger.interval_seconds),
                id=trigger.id,
                args=[trigger.id]
            )
        elif isinstance(trigger, DateTrigger):
            self._scheduler.add_job(
                self._run_scheduled_analytics,
                DateTrigger(run_date=trigger.run_date),
                id=trigger.id,
                args=[trigger.id]
            )
        elif isinstance(trigger, CombinedTrigger):
            # Create combined trigger
            triggers = []
            for trigger_id in trigger.trigger_ids:
                base_trigger = self._analytics_triggers.get(trigger_id)
                if base_trigger:
                    triggers.append(self._get_scheduler_trigger(base_trigger))
                    
            if trigger.combination_type == "and":
                combined_trigger = AndTrigger(triggers)
            else:
                combined_trigger = OrTrigger(triggers)
                
            self._scheduler.add_job(
                self._run_scheduled_analytics,
                combined_trigger,
                id=trigger.id,
                args=[trigger.id]
            )
            
    def _get_scheduler_trigger(self, trigger: AnalyticsTrigger) -> Any:
        """Convert analytics trigger to scheduler trigger."""
        if isinstance(trigger, CronTrigger):
            return CronTrigger.from_crontab(trigger.cron_expression, timezone=trigger.timezone)
        elif isinstance(trigger, IntervalTrigger):
            return IntervalTrigger(seconds=trigger.interval_seconds)
        elif isinstance(trigger, DateTrigger):
            return DateTrigger(run_date=trigger.run_date)
        else:
            raise CodeAccessError(f"Unsupported trigger type: {type(trigger)}")
            
    def _load_analytics_triggers(self) -> None:
        """Load analytics triggers from file."""
        triggers_file = self.config_dir / "analytics_triggers.yaml"
        if not triggers_file.exists():
            return
            
        try:
            with open(triggers_file) as f:
                data = yaml.safe_load(f)
                for trigger_data in data:
                    trigger_type = trigger_data["type"]
                    
                    if trigger_type == "cron":
                        trigger = CronTrigger(
                            id=trigger_data["id"],
                            analytics_id=trigger_data["analytics_id"],
                            enabled=trigger_data["enabled"],
                            cron_expression=trigger_data["cron_expression"],
                            timezone=trigger_data["timezone"],
                            metadata=trigger_data.get("metadata", {})
                        )
                    elif trigger_type == "interval":
                        trigger = IntervalTrigger(
                            id=trigger_data["id"],
                            analytics_id=trigger_data["analytics_id"],
                            enabled=trigger_data["enabled"],
                            interval_seconds=trigger_data["interval_seconds"],
                            metadata=trigger_data.get("metadata", {})
                        )
                    elif trigger_type == "date":
                        trigger = DateTrigger(
                            id=trigger_data["id"],
                            analytics_id=trigger_data["analytics_id"],
                            enabled=trigger_data["enabled"],
                            run_date=datetime.fromisoformat(trigger_data["run_date"]),
                            metadata=trigger_data.get("metadata", {})
                        )
                    elif trigger_type == "combined":
                        trigger = CombinedTrigger(
                            id=trigger_data["id"],
                            analytics_id=trigger_data["analytics_id"],
                            enabled=trigger_data["enabled"],
                            trigger_ids=trigger_data["trigger_ids"],
                            combination_type=trigger_data["combination_type"],
                            metadata=trigger_data.get("metadata", {})
                        )
                    else:
                        continue
                        
                    self._analytics_triggers[trigger.id] = trigger
                    
                    # Add job to scheduler if enabled
                    if trigger.enabled:
                        self._add_trigger_to_scheduler(trigger)
                        
        except Exception as e:
            logger.error(f"Failed to load analytics triggers: {str(e)}")
            
    def _save_analytics_triggers(self) -> None:
        """Save analytics triggers to file."""
        triggers_file = self.config_dir / "analytics_triggers.yaml"
        with open(triggers_file, "w") as f:
            yaml.dump([
                {
                    "id": trigger.id,
                    "type": trigger.__class__.__name__.lower(),
                    "analytics_id": trigger.analytics_id,
                    "enabled": trigger.enabled,
                    **{
                        "cron_expression": trigger.cron_expression,
                        "timezone": trigger.timezone
                    } if isinstance(trigger, CronTrigger) else {},
                    **{
                        "interval_seconds": trigger.interval_seconds
                    } if isinstance(trigger, IntervalTrigger) else {},
                    **{
                        "run_date": trigger.run_date.isoformat()
                    } if isinstance(trigger, DateTrigger) else {},
                    **{
                        "trigger_ids": trigger.trigger_ids,
                        "combination_type": trigger.combination_type
                    } if isinstance(trigger, CombinedTrigger) else {},
                    "metadata": trigger.metadata
                }
                for trigger in self._analytics_triggers.values()
            ], f)
            
    async def _start_websocket_server(self) -> None:
        """Start WebSocket server for real-time streaming."""
        self._ws_server = await serve(
            self._handle_websocket_connection,
            "localhost",
            8765
        )
        self._ws_server_task = asyncio.create_task(self._ws_server.wait_closed())
        
    async def _handle_websocket_connection(
        self,
        websocket: websockets.WebSocketServerProtocol,
        path: str
    ) -> None:
        """Handle new WebSocket connection."""
        try:
            # Parse connection parameters
            params = dict(param.split('=') for param in path.split('?')[1].split('&'))
            stream_id = params.get('stream_id')
            
            if not stream_id:
                await websocket.close(1008, "Missing stream_id parameter")
                return
                
            # Create connection record
            connection = WebSocketConnection(
                id=secrets.token_urlsafe(16),
                websocket=websocket,
                stream_id=stream_id,
                created_at=datetime.now(),
                last_active=datetime.now(),
                metadata={"path": path}
            )
            
            self._ws_connections[connection.id] = connection
            
            try:
                async for message in websocket:
                    # Update last active time
                    connection.last_active = datetime.now()
                    
                    # Handle incoming messages
                    await self._handle_websocket_message(connection, message)
                    
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"WebSocket connection closed: {connection.id}")
            finally:
                # Clean up connection
                if connection.id in self._ws_connections:
                    del self._ws_connections[connection.id]
                    
        except Exception as e:
            logger.error(f"Error handling WebSocket connection: {str(e)}")
            await websocket.close(1011, str(e))
            
    async def _handle_websocket_message(
        self,
        connection: WebSocketConnection,
        message: str
    ) -> None:
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe":
                # Add subscriber to stream
                stream = self._analytics_streams.get(connection.stream_id)
                if stream:
                    stream.subscribers.add(connection.id)
                    self._save_analytics_streams()
                    
            elif message_type == "unsubscribe":
                # Remove subscriber from stream
                stream = self._analytics_streams.get(connection.stream_id)
                if stream:
                    stream.subscribers.discard(connection.id)
                    self._save_analytics_streams()
                    
            elif message_type == "ping":
                # Send pong response
                await connection.websocket.send(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
            await connection.websocket.send(json.dumps({
                "type": "error",
                "message": str(e)
            })) 