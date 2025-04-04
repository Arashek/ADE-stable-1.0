"""
Management Components Models for ADE Platform

This module defines the data models for management components of the ADE platform,
including users, roles, permissions, and other administrative-level entities.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

print("DEBUG: Loading models/management_components.py")

class Permission(BaseModel):
    """Permission model defining what users can do within the system"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    resource: str
    action: str  # "read", "write", "delete", "admin", etc.
    conditions: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)


class Role(BaseModel):
    """Role model for grouping permissions and assigning to users"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    permissions: List[str]  # List of permission IDs
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    is_system_role: bool = False  # True if this is a system-defined role


class User(BaseModel):
    """User model for platform users including administrators"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    hashed_password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str] = []  # List of role IDs
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    @validator('email')
    def email_must_be_valid(cls, v):
        # Simple validation - could be enhanced
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v


class UserSession(BaseModel):
    """User session model for tracking active sessions"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    token: str
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)


class LoginAttempt(BaseModel):
    """Login attempt model for security monitoring"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    ip_address: str
    user_agent: Optional[str] = None
    success: bool
    timestamp: datetime = Field(default_factory=datetime.now)
    failure_reason: Optional[str] = None


class UserActivity(BaseModel):
    """User activity log for audit purposes"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    activity_type: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class AdminSettings(BaseModel):
    """Admin settings for platform configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    setting_key: str
    setting_value: Any
    description: Optional[str] = None
    updated_by: str
    updated_at: datetime = Field(default_factory=datetime.now)
    is_sensitive: bool = False


class NotificationSettings(BaseModel):
    """Notification settings for platform alerts"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    notification_type: str  # "email", "in_app", "sms", etc.
    enabled: bool = True
    channels: Dict[str, bool]  # Specific channels like "security_alerts", "updates", etc.
    updated_at: datetime = Field(default_factory=datetime.now)


class TeamMember(BaseModel):
    """Team member model for collaboration features"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    team_id: str
    role: str  # "owner", "admin", "member", etc.
    joined_at: datetime = Field(default_factory=datetime.now)
    invited_by: Optional[str] = None
    status: str = "active"  # "active", "inactive", "invited"


class Team(BaseModel):
    """Team model for group collaboration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    visibility: str = "private"  # "private", "public", etc.
    settings: Optional[Dict[str, Any]] = None


class Component(BaseModel):
    """Model representing a system component"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str # e.g., 'service', 'database', 'library'
    description: Optional[str] = None
    version: str
    status: str # e.g., 'active', 'inactive', 'deprecated'
    configuration: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[Dict[str, Any]]] = None # List of dependency info
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class Model(BaseModel):
    """Data model definition"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    schema: Dict[str, Any]
    description: Optional[str] = None
    version: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class ServiceConfig(BaseModel):
    """Service configuration settings"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str
    environment: str  # dev, test, prod
    config_data: Dict[str, Any]
    version: str
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class InfrastructureSettings(BaseModel):
    """Infrastructure configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    setting_key: str
    setting_value: Any
    description: Optional[str] = None
    environment: str  # dev, test, prod
    updated_by: str
    updated_at: datetime = Field(default_factory=datetime.now)


class ExternalService(BaseModel):
    """External service integration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # API, database, messaging, etc.
    url: str
    auth_type: Optional[str] = None
    auth_data: Optional[Dict[str, Any]] = None
    status: str = "active"
    config: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class APIConfig(BaseModel):
    """API configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    base_url: str
    version: str
    auth_type: Optional[str] = None
    rate_limit: Optional[int] = None
    timeout: int = 30
    retry_policy: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class WebhookConfig(BaseModel):
    """Webhook configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: str
    events: List[str]
    secret: Optional[str] = None
    active: bool = True
    failure_count: int = 0
    last_triggered: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class MarketplaceItem(BaseModel):
    """Marketplace item for agent components and services"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    type: str  # agent, component, service, template
    price: float
    author: str
    version: str
    tags: List[str] = []
    preview_url: Optional[str] = None
    documentation_url: Optional[str] = None
    download_count: int = 0
    rating: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class MarketplaceOrder(BaseModel):
    """Marketplace order record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    item_id: str
    quantity: int = 1
    total_price: float
    status: str  # pending, completed, failed, refunded
    payment_id: Optional[str] = None
    license_key: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
