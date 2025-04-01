"""
Decision Memory Models

This module defines the data models for storing and retrieving decision memory data,
enabling the platform to track design decisions, architectural choices, and technical debt
across the project lifecycle.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from enum import Enum

class DecisionCategory(str, Enum):
    """Enumeration of decision categories"""
    DESIGN = "design"
    ARCHITECTURE = "architecture"
    TECHNOLOGY = "technology"
    IMPLEMENTATION = "implementation"
    PROCESS = "process"
    SECURITY = "security"
    PERFORMANCE = "performance"
    USABILITY = "usability"
    ACCESSIBILITY = "accessibility"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"
    TECHNICAL_DEBT = "technical_debt"
    CUSTOM = "custom"

class DecisionStatus(str, Enum):
    """Enumeration of decision statuses"""
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"
    IMPLEMENTED = "implemented"
    DEFERRED = "deferred"

class DecisionImpact(str, Enum):
    """Enumeration of decision impact levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Decision(BaseModel):
    """Model for a decision in the decision memory"""
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    title: str
    description: str
    category: DecisionCategory
    status: DecisionStatus
    impact: DecisionImpact
    rationale: str
    alternatives: List[str] = Field(default_factory=list)
    consequences: List[str] = Field(default_factory=list)
    related_decisions: List[UUID] = Field(default_factory=list)
    related_entities: List[UUID] = Field(default_factory=list)
    created_by: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    implemented_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TechnicalDebt(BaseModel):
    """Model for technical debt in the decision memory"""
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    title: str
    description: str
    category: DecisionCategory
    severity: DecisionImpact
    estimated_effort: str  # e.g., "2 days", "1 week"
    rationale: str
    mitigation_plan: Optional[str] = None
    related_decisions: List[UUID] = Field(default_factory=list)
    related_entities: List[UUID] = Field(default_factory=list)
    created_by: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DecisionQuery(BaseModel):
    """Model for a query to the decision memory"""
    project_id: UUID
    categories: Optional[List[DecisionCategory]] = None
    statuses: Optional[List[DecisionStatus]] = None
    impacts: Optional[List[DecisionImpact]] = None
    tags: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_metadata: bool = False
