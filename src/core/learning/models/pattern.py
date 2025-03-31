from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid

class PatternType(str, Enum):
    """Enumeration of supported pattern types"""
    SOLUTION = "solution"
    ERROR_RECOVERY = "error_recovery"
    WORKFLOW = "workflow"
    TOOL_USAGE = "tool_usage"

class PrivacyLevel(str, Enum):
    """Enumeration of privacy levels for pattern data"""
    PUBLIC = "public"  # Fully anonymized, safe for sharing
    AGGREGATED = "aggregated"  # Contains aggregated statistics only
    PRIVATE = "private"  # Contains instance-specific data
    SENSITIVE = "sensitive"  # Contains potentially sensitive data

class EnvironmentContext(BaseModel):
    """Context information about the environment where the pattern was observed"""
    instance_id: str = Field(..., description="Unique identifier of the ADE instance")
    environment: str = Field(..., description="Environment type (e.g., development, staging, production)")
    version: str = Field(..., description="ADE platform version")
    region: Optional[str] = Field(None, description="Geographic region of the instance")
    component: str = Field(..., description="Component or module where the pattern was observed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the pattern was observed")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PrivacyMetadata(BaseModel):
    """Metadata about privacy and data handling"""
    privacy_level: PrivacyLevel = Field(..., description="Privacy level of the pattern data")
    anonymization_method: Optional[str] = Field(None, description="Method used for anonymization")
    contributor_count: int = Field(default=1, description="Number of instances that contributed to this pattern")
    last_anonymized: datetime = Field(default_factory=datetime.utcnow, description="Last time the data was anonymized")
    retention_period: Optional[int] = Field(None, description="Data retention period in days")
    data_scope: List[str] = Field(default_factory=list, description="Scope of data included in the pattern")

    @validator('contributor_count')
    def validate_contributor_count(cls, v):
        if v < 1:
            raise ValueError("Contributor count must be at least 1")
        return v

class EffectivenessMetrics(BaseModel):
    """Metrics for measuring pattern effectiveness"""
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Rate of successful pattern application")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in pattern effectiveness")
    usage_count: int = Field(default=0, ge=0, description="Number of times the pattern has been used")
    average_duration: Optional[float] = Field(None, ge=0, description="Average duration of pattern application")
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Rate of errors during pattern application")
    last_success: Optional[datetime] = Field(None, description="Timestamp of last successful application")
    last_failure: Optional[datetime] = Field(None, description="Timestamp of last failed application")

    @validator('success_rate', 'confidence_score', 'error_rate')
    def validate_probability(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Probability values must be between 0 and 1")
        return v

class BasePattern(BaseModel):
    """Base model for all learning patterns"""
    pattern_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique pattern identifier")
    pattern_type: PatternType = Field(..., description="Type of the pattern")
    name: str = Field(..., description="Human-readable name of the pattern")
    description: str = Field(..., description="Detailed description of the pattern")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Pattern creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    context: EnvironmentContext = Field(..., description="Environment context")
    privacy: PrivacyMetadata = Field(..., description="Privacy metadata")
    effectiveness: EffectivenessMetrics = Field(..., description="Effectiveness metrics")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SolutionPattern(BasePattern):
    """Model for solution patterns"""
    pattern_type: PatternType = Field(default=PatternType.SOLUTION, description="Type of the pattern")
    steps: List[str] = Field(..., description="Step-by-step solution instructions")
    prerequisites: List[str] = Field(default_factory=list, description="Required conditions or prerequisites")
    alternatives: List[str] = Field(default_factory=list, description="Alternative solution approaches")
    validation_rules: List[str] = Field(default_factory=list, description="Rules for validating solution success")
    estimated_duration: Optional[float] = Field(None, ge=0, description="Estimated duration in seconds")

class ErrorRecoveryPattern(BasePattern):
    """Model for error recovery patterns"""
    pattern_type: PatternType = Field(default=PatternType.ERROR_RECOVERY, description="Type of the pattern")
    error_type: str = Field(..., description="Type of error this pattern addresses")
    error_signature: str = Field(..., description="Pattern matching signature for error identification")
    recovery_steps: List[str] = Field(..., description="Step-by-step recovery instructions")
    prevention_measures: List[str] = Field(default_factory=list, description="Measures to prevent error recurrence")
    error_context: Dict[str, Any] = Field(default_factory=dict, description="Contextual information about the error")
    severity_level: str = Field(..., description="Severity level of the error")

class WorkflowPattern(BasePattern):
    """Model for workflow patterns"""
    pattern_type: PatternType = Field(default=PatternType.WORKFLOW, description="Type of the pattern")
    sequence: List[str] = Field(..., description="Sequence of actions in the workflow")
    dependencies: Dict[str, List[str]] = Field(default_factory=dict, description="Action dependencies")
    checkpoints: List[str] = Field(default_factory=list, description="Validation checkpoints")
    rollback_steps: List[str] = Field(default_factory=list, description="Steps for workflow rollback")
    parallel_actions: List[List[str]] = Field(default_factory=list, description="Actions that can be executed in parallel")

class ToolUsagePattern(BasePattern):
    """Model for tool usage patterns"""
    pattern_type: PatternType = Field(default=PatternType.TOOL_USAGE, description="Type of the pattern")
    tool_name: str = Field(..., description="Name of the tool")
    command_sequence: List[str] = Field(..., description="Sequence of commands or operations")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters and configuration")
    output_format: Optional[str] = Field(None, description="Expected output format")
    common_issues: List[str] = Field(default_factory=list, description="Common issues and their solutions")
    optimization_tips: List[str] = Field(default_factory=list, description="Tips for optimal tool usage")

def create_pattern(
    pattern_type: PatternType,
    name: str,
    description: str,
    context: EnvironmentContext,
    privacy: PrivacyMetadata,
    effectiveness: EffectivenessMetrics,
    **kwargs: Any
) -> Union[SolutionPattern, ErrorRecoveryPattern, WorkflowPattern, ToolUsagePattern]:
    """
    Factory function to create pattern instances based on type.
    
    Args:
        pattern_type: Type of pattern to create
        name: Pattern name
        description: Pattern description
        context: Environment context
        privacy: Privacy metadata
        effectiveness: Effectiveness metrics
        **kwargs: Additional arguments specific to pattern type
        
    Returns:
        Instance of the appropriate pattern type
    """
    pattern_classes = {
        PatternType.SOLUTION: SolutionPattern,
        PatternType.ERROR_RECOVERY: ErrorRecoveryPattern,
        PatternType.WORKFLOW: WorkflowPattern,
        PatternType.TOOL_USAGE: ToolUsagePattern
    }
    
    if pattern_type not in pattern_classes:
        raise ValueError(f"Unsupported pattern type: {pattern_type}")
    
    pattern_class = pattern_classes[pattern_type]
    return pattern_class(
        pattern_type=pattern_type,
        name=name,
        description=description,
        context=context,
        privacy=privacy,
        effectiveness=effectiveness,
        **kwargs
    ) 