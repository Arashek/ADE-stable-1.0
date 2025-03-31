from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from ..auth.auth import get_current_user
from ...storage.usage_tracking import usage_tracker
from ...db.models.analytics import (
    UsageMetrics,
    PerformanceMetrics,
    TeamActivity,
    TimeRange
)

router = APIRouter()

@router.get("/usage", response_model=List[UsageMetrics])
async def get_usage_metrics(
    range: TimeRange = Query(TimeRange.SEVEN_DAYS),
    current_user = Depends(get_current_user)
):
    """Get usage metrics for the specified time range"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=range.value)
        
        metrics = await usage_tracker.get_usage_history(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance", response_model=List[PerformanceMetrics])
async def get_performance_metrics(
    range: TimeRange = Query(TimeRange.SEVEN_DAYS),
    current_user = Depends(get_current_user)
):
    """Get performance metrics for the specified time range"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=range.value)
        
        metrics = await usage_tracker.get_performance_history(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity", response_model=List[TeamActivity])
async def get_team_activity(
    range: TimeRange = Query(TimeRange.SEVEN_DAYS),
    current_user = Depends(get_current_user)
):
    """Get team activity for the specified time range"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=range.value)
        
        activity = await usage_tracker.get_team_activity(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        return activity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary", response_model=dict)
async def get_analytics_summary(
    current_user = Depends(get_current_user)
):
    """Get a summary of all analytics data"""
    try:
        summary = await usage_tracker.get_analytics_summary(
            user_id=current_user.id
        )
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 