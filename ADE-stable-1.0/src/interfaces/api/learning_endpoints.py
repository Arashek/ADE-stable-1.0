from typing import Dict, List, Optional, Set
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from uuid import UUID

from ...core.learning.models.privacy_settings import (
    PrivacySettings,
    PrivacyLevel,
    AttributionType,
    PatternType
)
from ...core.learning.models.pattern import BasePattern
from ...core.learning.learning_manager import LearningManager
from ...core.orchestrator import Orchestrator
from ..dependencies import get_orchestrator

router = APIRouter(prefix="/learning", tags=["learning"])

class PrivacySettingsResponse(BaseModel):
    """Response model for privacy settings"""
    enabled: bool
    privacy_level: PrivacyLevel
    attribution_type: AttributionType
    shared_pattern_types: Set[PatternType]
    excluded_projects: Set[str]
    excluded_languages: Set[str]
    custom_parameters: Dict[str, float]
    created_at: datetime
    last_updated: datetime
    version: str
    modified_by: str

class PrivacySettingsUpdate(BaseModel):
    """Request model for updating privacy settings"""
    enabled: Optional[bool] = None
    privacy_level: Optional[PrivacyLevel] = None
    attribution_type: Optional[AttributionType] = None
    shared_pattern_types: Optional[Set[PatternType]] = None
    excluded_projects: Optional[Set[str]] = None
    excluded_languages: Optional[Set[str]] = None
    custom_parameters: Optional[Dict[str, float]] = None

class ActivityData(BaseModel):
    """Request model for activity data"""
    activities: List[Dict[str, any]] = Field(..., description="List of development activities")
    privacy_settings: Optional[PrivacySettingsUpdate] = None

class PatternResponse(BaseModel):
    """Response model for patterns"""
    pattern_id: str
    pattern_type: PatternType
    name: str
    description: str
    context: Dict[str, any]
    privacy: Dict[str, any]
    effectiveness: Dict[str, float]
    created_at: datetime
    last_updated: datetime

class LearningStatsResponse(BaseModel):
    """Response model for learning statistics"""
    total_patterns: int
    patterns_by_type: Dict[PatternType, int]
    last_collection: Optional[datetime]
    collection_errors: int
    anonymization_errors: int
    processing_errors: int
    total_activities_processed: int
    total_patterns_shared: int
    total_patterns_filtered: int

@router.get(
    "/privacy",
    response_model=PrivacySettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current privacy settings",
    description="Retrieve the current privacy settings for the learning infrastructure"
)
async def get_privacy_settings(
    orchestrator: Orchestrator = Depends(get_orchestrator)
) -> PrivacySettingsResponse:
    """Get current privacy settings"""
    try:
        settings = orchestrator.learning_manager.get_privacy_settings()
        metadata = orchestrator.learning_manager.privacy_manager.get_metadata()
        
        return PrivacySettingsResponse(
            enabled=settings.enabled,
            privacy_level=settings.privacy_level,
            attribution_type=settings.attribution_type,
            shared_pattern_types=settings.shared_pattern_types,
            excluded_projects=settings.excluded_projects,
            excluded_languages=settings.excluded_languages,
            custom_parameters=settings.custom_parameters,
            created_at=metadata.created_at,
            last_updated=metadata.last_updated,
            version=metadata.version,
            modified_by=metadata.modified_by
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving privacy settings: {str(e)}"
        )

@router.post(
    "/privacy",
    response_model=PrivacySettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Update privacy settings",
    description="Update the privacy settings for the learning infrastructure"
)
async def update_privacy_settings(
    settings_update: PrivacySettingsUpdate,
    orchestrator: Orchestrator = Depends(get_orchestrator)
) -> PrivacySettingsResponse:
    """Update privacy settings"""
    try:
        # Get current settings
        current_settings = orchestrator.learning_manager.get_privacy_settings()
        
        # Update settings
        update_data = settings_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(current_settings, key, value)
        
        # Apply updates
        orchestrator.learning_manager.update_privacy_settings(
            current_settings,
            modified_by="api"
        )
        
        # Get updated settings
        return await get_privacy_settings(orchestrator)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating privacy settings: {str(e)}"
        )

@router.post(
    "/privacy/reset",
    response_model=PrivacySettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset privacy settings",
    description="Reset privacy settings to default values"
)
async def reset_privacy_settings(
    orchestrator: Orchestrator = Depends(get_orchestrator)
) -> PrivacySettingsResponse:
    """Reset privacy settings to defaults"""
    try:
        orchestrator.learning_manager.privacy_manager.reset_to_defaults(
            modified_by="api"
        )
        return await get_privacy_settings(orchestrator)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting privacy settings: {str(e)}"
        )

@router.post(
    "/collect",
    response_model=List[PatternResponse],
    status_code=status.HTTP_200_OK,
    summary="Collect patterns",
    description="Collect patterns from development activities"
)
async def collect_patterns(
    activity_data: ActivityData,
    orchestrator: Orchestrator = Depends(get_orchestrator)
) -> List[PatternResponse]:
    """Collect patterns from activities"""
    try:
        # Update privacy settings if provided
        if activity_data.privacy_settings:
            await update_privacy_settings(
                activity_data.privacy_settings,
                orchestrator
            )
        
        # Collect patterns
        patterns = orchestrator.learning_manager.collect_patterns(
            activity_data.activities
        )
        
        # Convert patterns to response model
        return [
            PatternResponse(
                pattern_id=pattern.pattern_id,
                pattern_type=pattern.pattern_type,
                name=pattern.name,
                description=pattern.description,
                context=pattern.context,
                privacy=pattern.privacy.dict(),
                effectiveness=pattern.effectiveness.dict(),
                created_at=pattern.created_at,
                last_updated=pattern.last_updated
            )
            for pattern in patterns
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error collecting patterns: {str(e)}"
        )

@router.get(
    "/stats",
    response_model=LearningStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get learning statistics",
    description="Retrieve statistics about the learning infrastructure"
)
async def get_learning_stats(
    orchestrator: Orchestrator = Depends(get_orchestrator)
) -> LearningStatsResponse:
    """Get learning statistics"""
    try:
        stats = orchestrator.learning_manager.get_stats()
        return LearningStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving learning statistics: {str(e)}"
        ) 