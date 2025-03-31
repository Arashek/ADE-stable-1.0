from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from enum import Enum

class TimeRange(str, Enum):
    """Time range options for analytics queries"""
    ONE_DAY = "24h"
    SEVEN_DAYS = "7d"
    THIRTY_DAYS = "30d"
    NINETY_DAYS = "90d"

class UsageMetrics(BaseModel):
    """Model for usage metrics"""
    date: datetime
    compute_hours: float
    storage_gb: float
    api_calls: int
    active_users: int
    projects: int

class PerformanceMetrics(BaseModel):
    """Model for performance metrics"""
    endpoint: str
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    error_rate: float
    request_count: int

class TeamActivity(BaseModel):
    """Model for team activity"""
    id: str
    user: str
    action: str
    description: str
    timestamp: datetime
    metadata: Dict = Field(default_factory=dict)

class AnalyticsSummary(BaseModel):
    """Model for analytics summary"""
    total_compute_hours: float
    total_storage_gb: float
    total_api_calls: int
    avg_response_time: float
    error_rate: float
    active_users: int
    total_projects: int
    recent_activity: List[TeamActivity]
    usage_trends: Dict[str, List[float]]
    performance_trends: Dict[str, List[float]]

class UsageHistory(BaseModel):
    """Model for usage history"""
    user_id: str
    start_date: datetime
    end_date: datetime
    metrics: List[UsageMetrics]
    summary: AnalyticsSummary

class PerformanceHistory(BaseModel):
    """Model for performance history"""
    user_id: str
    start_date: datetime
    end_date: datetime
    metrics: List[PerformanceMetrics]
    summary: Dict[str, float]

class TeamActivityHistory(BaseModel):
    """Model for team activity history"""
    user_id: str
    start_date: datetime
    end_date: datetime
    activities: List[TeamActivity]
    summary: Dict[str, int] 