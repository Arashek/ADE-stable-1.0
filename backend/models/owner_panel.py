"""
Owner Panel Models for ADE Platform

This module defines the data models for the Owner Panel component of the ADE platform,
including dashboard metrics, system configurations, and admin-level operational models.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class SystemMetrics(BaseModel):
    """System performance and usage metrics"""
    active_users: int
    total_users: int
    system_load: float
    memory_usage: float
    storage_usage: float
    api_requests: int
    error_rate: float


class UserStats(BaseModel):
    """User statistics for the platform"""
    total_users: int
    active_users: int
    new_users: int
    suspended_users: int
    avg_session_time: Optional[float] = None
    conversion_rate: Optional[float] = None


class SecurityConfig(BaseModel):
    """Security configuration settings"""
    auth_method: str
    session_timeout: int
    max_login_attempts: int
    require_2fa: bool
    ip_whitelist: Optional[List[str]] = None
    password_policy: Dict[str, Any]


class FrontendConfig(BaseModel):
    """Frontend configuration settings"""
    theme: str
    custom_css: Optional[str] = None
    logo_url: Optional[str] = None
    menu_items: List[Dict[str, Any]]
    landing_page_content: Dict[str, Any]
    seo_settings: Optional[Dict[str, Any]] = None


class SupportTicket(BaseModel):
    """Support ticket model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subject: str
    description: str
    status: str
    priority: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    attachments: Optional[List[str]] = None


class AuditLog(BaseModel):
    """Audit log entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: str
    action: str
    resource: str
    ip_address: str
    details: Optional[Dict[str, Any]] = None


class SystemDiagnostics(BaseModel):
    """System diagnostics information"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_status: str
    service_statuses: Dict[str, str]
    pending_updates: int
    last_backup: Optional[datetime] = None


class APIKey(BaseModel):
    """API key model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    key_hash: str
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    permissions: List[str]
    created_by: str
    last_used: Optional[datetime] = None
    active: bool = True


class DashboardMetrics(BaseModel):
    """Dashboard metrics for the Owner Panel"""
    active_projects: int
    completed_projects: int
    user_signups: Dict[str, int]  # Period (day, week, month) to count
    revenue: Dict[str, float]  # Period to amount
    api_usage: Dict[str, int]  # Endpoint to count
    system_health: float  # 0-1 score
    average_response_time: float  # in ms


class APIConfig(BaseModel):
    """API configuration settings"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    endpoint: str
    method: str
    auth_required: bool
    rate_limit: Optional[int] = None
    cache_ttl: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None
    response_format: str


class WebhookConfig(BaseModel):
    """Webhook configuration settings"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: str
    events: List[str]
    active: bool = True
    secret: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    created_at: datetime = Field(default_factory=datetime.now)


class MarketplaceItem(BaseModel):
    """Marketplace item model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: float
    category: str
    author: str
    version: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    downloads: int = 0
    rating: Optional[float] = None
    tags: Optional[List[str]] = None


class MarketplaceOrder(BaseModel):
    """Marketplace order model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    item_id: str
    price: float
    status: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    transaction_id: Optional[str] = None


class SystemDiagnostic(BaseModel):
    """System diagnostic information"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    component: str
    status: str
    details: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class PerformanceMetric(BaseModel):
    """Performance metric model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metric_name: str
    value: float
    unit: str
    component: str
    timestamp: datetime = Field(default_factory=datetime.now)
    threshold: Optional[float] = None
    alert_triggered: bool = False


class ErrorLog(BaseModel):
    """Error log entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    error_code: str
    message: str
    stack_trace: Optional[str] = None
    component: str
    severity: str
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = None
    request_id: Optional[str] = None


class LandingPageContent(BaseModel):
    """Landing page content configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    subtitle: Optional[str] = None
    hero_image: Optional[str] = None
    sections: List[Dict[str, Any]]
    cta_button_text: Optional[str] = None
    cta_button_link: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)


class ThemeConfig(BaseModel):
    """Theme configuration settings"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    text_color: str
    font_family: str
    custom_css: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)


class UIComponent(BaseModel):
    """UI component configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    component_type: str
    position: str
    visible: bool = True
    config: Dict[str, Any]
    updated_at: datetime = Field(default_factory=datetime.now)
