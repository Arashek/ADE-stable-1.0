"""Metrics API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from src.core.orchestrator import Orchestrator
from src.interfaces.api.auth import User, get_current_active_user
from src.interfaces.api.dependencies import get_orchestrator

# Create router
router = APIRouter(
    prefix="/metrics",
    tags=["metrics"]
)

# Models
class MetricResponse(BaseModel):
    """Response model for metric information."""
    name: str = Field(..., description="Name of the metric")
    value: float = Field(..., description="Current value of the metric")
    unit: str = Field(..., description="Unit of measurement")
    timestamp: datetime = Field(..., description="When the metric was recorded")

class MetricHistoryResponse(BaseModel):
    """Response model for metric history."""
    metric_name: str = Field(..., description="Name of the metric")
    values: List[float] = Field(..., description="List of metric values")
    timestamps: List[datetime] = Field(..., description="List of timestamps")
    unit: str = Field(..., description="Unit of measurement")

# Routes
@router.get("/", response_model=List[MetricResponse])
async def list_metrics(
    current_user: User = Depends(get_current_active_user),
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """List all available metrics"""
    try:
        metrics = orchestrator.get_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list metrics: {str(e)}"
        )

@router.get("/{metric_name}", response_model=MetricResponse)
async def get_metric(
    metric_name: str,
    current_user: User = Depends(get_current_active_user),
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Get a specific metric"""
    try:
        metric = orchestrator.get_metric(metric_name)
        if not metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Metric {metric_name} not found"
            )
        return metric
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metric: {str(e)}"
        )

@router.get("/{metric_name}/history", response_model=MetricHistoryResponse)
async def get_metric_history(
    metric_name: str,
    current_user: User = Depends(get_current_active_user),
    orchestrator: Orchestrator = Depends(get_orchestrator),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    interval: Optional[timedelta] = None
):
    """Get historical data for a metric"""
    try:
        history = orchestrator.get_metric_history(
            metric_name,
            start_time=start_time,
            end_time=end_time,
            interval=interval
        )
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No history found for metric {metric_name}"
            )
        return history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metric history: {str(e)}"
        )

@router.get("/summary", response_model=Dict[str, Any])
async def get_metrics_summary(
    current_user: User = Depends(get_current_active_user),
    orchestrator: Orchestrator = Depends(get_orchestrator),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """Get a summary of all metrics"""
    try:
        summary = orchestrator.get_metrics_summary(
            start_time=start_time,
            end_time=end_time
        )
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics summary: {str(e)}"
        ) 