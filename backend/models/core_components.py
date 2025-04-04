from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """User profile information"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class Notification(BaseModel):
    """User notification"""
    id: str
    user_id: str
    title: str
    message: str
    type: str  # 'info', 'warning', 'error', 'success'
    read: bool = False
    created_at: datetime


class DashboardMetrics(BaseModel):
    """Metrics for dashboard display"""
    active_projects: int
    total_deployments: int
    pending_tasks: int
    system_health: str  # 'healthy', 'warning', 'critical'
    resource_usage: Dict[str, float]  # CPU, memory, disk usage
    recent_activities: List[Dict[str, Any]]


class NavigationItem(BaseModel):
    """Navigation menu item"""
    id: str
    name: str
    path: str
    icon: Optional[str] = None
    parent_id: Optional[str] = None
    order: int
    required_permissions: List[str] = []


class UserSettings(BaseModel):
    """User preferences and settings"""
    user_id: str
    theme: str = "light"
    notifications_enabled: bool = True
    email_notifications: bool = True
    dashboard_widgets: List[str] = []
    language: str = "en"
    timezone: str = "UTC"


class ResourceUsage(BaseModel):
    """System resource usage metrics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent_mb: float
    network_received_mb: float
    timestamp: datetime


class SystemHealth(BaseModel):
    """System health status"""
    status: str  # 'healthy', 'warning', 'critical'
    components: Dict[str, str]  # component_name: status
    last_check: datetime
    issues: List[Dict[str, Any]] = []


class DeploymentStatus(BaseModel):
    """Deployment status information"""
    id: str
    project_id: str
    status: str  # 'pending', 'in_progress', 'success', 'failed'
    environment: str
    version: str
    deployed_at: Optional[datetime] = None
    logs: List[str] = []


class UserManagement(BaseModel):
    """User management actions and status"""
    total_users: int
    active_users: int
    locked_accounts: int
    recent_registrations: List[Dict[str, Any]]


class SystemOverview(BaseModel):
    """Overall system statistics"""
    users: int
    projects: int
    deployments: int
    components: int
    services: int
    uptime_days: float


class SystemStatus(BaseModel):
    """Current system status"""
    status: str  # 'operational', 'degraded', 'maintenance', 'outage'
    message: Optional[str] = None
    last_updated: datetime
    services: Dict[str, str]  # service_name: status
