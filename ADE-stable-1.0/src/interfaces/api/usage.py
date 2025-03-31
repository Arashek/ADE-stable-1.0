from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from src.core.services.usage_tracking import UsageTrackingService
from src.storage.document.models.usage import UsageRecord, UserUsageSummary, UsageType
from src.interfaces.api.auth import User, get_current_active_user
from src.interfaces.api.providers import provider_registry

router = APIRouter(
    prefix="/usage",
    tags=["usage"]
)

class UsageResponse(BaseModel):
    """Response model for usage data"""
    total_tokens: int
    total_cost: float
    usage_by_type: dict
    usage_by_provider: dict
    usage_by_model: dict
    quota_limits: dict
    quota_usage: dict

class UsageHistoryResponse(BaseModel):
    """Response model for historical usage data"""
    date: str
    total_tokens: int
    total_cost: float
    requests: int
    successful_requests: int

@router.get("/summary", response_model=UsageResponse)
async def get_usage_summary(
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get usage summary for the current user"""
    try:
        summary = await usage_tracking_service.get_user_usage_summary(
            current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting usage summary: {str(e)}"
        )

@router.get("/history", response_model=List[UsageHistoryResponse])
async def get_usage_history(
    current_user: User = Depends(get_current_active_user),
    days: int = Query(30, ge=1, le=365),
    group_by: str = Query("day", regex="^(day|month)$")
):
    """Get historical usage data for the current user"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        history = await usage_tracking_service.usage_repository.aggregate_usage(
            current_user.id,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )
        
        return [
            UsageHistoryResponse(
                date=item["_id"],
                total_tokens=item["total_tokens"],
                total_cost=item["total_cost"],
                requests=item["requests"],
                successful_requests=item["successful_requests"]
            )
            for item in history
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting usage history: {str(e)}"
        )

@router.get("/by-provider", response_model=List[UsageRecord])
async def get_usage_by_provider(
    provider: str,
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get usage records for a specific provider"""
    try:
        records = await usage_tracking_service.usage_repository.get_usage_by_provider(
            current_user.id,
            provider,
            start_date=start_date,
            end_date=end_date
        )
        return records
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting provider usage: {str(e)}"
        )

@router.get("/by-type", response_model=List[UsageRecord])
async def get_usage_by_type(
    usage_type: UsageType,
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get usage records for a specific usage type"""
    try:
        records = await usage_tracking_service.usage_repository.get_usage_by_type(
            current_user.id,
            usage_type,
            start_date=start_date,
            end_date=end_date
        )
        return records
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting usage by type: {str(e)}"
        )

@router.get("/project/{project_id}", response_model=List[UsageRecord])
async def get_project_usage(
    project_id: str,
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get usage records for a specific project"""
    try:
        records = await usage_tracking_service.usage_repository.get_project_usage(
            project_id,
            start_date=start_date,
            end_date=end_date
        )
        return records
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting project usage: {str(e)}"
        )

@router.get("/export")
async def export_usage_data(
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    format: str = Query("csv", regex="^(csv|json)$")
):
    """Export usage data in CSV or JSON format"""
    try:
        records = await usage_tracking_service.usage_repository.find(
            {
                "user_id": current_user.id,
                "timestamp": {
                    "$gte": start_date or datetime.min,
                    "$lte": end_date or datetime.max
                }
            },
            sort_by="timestamp"
        )
        
        if format == "csv":
            # Convert to CSV format
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "Date", "Provider", "Model", "Type", "Tokens", "Cost",
                "Status", "Project ID", "Error Message"
            ])
            
            # Write records
            for record in records:
                writer.writerow([
                    record.timestamp.isoformat(),
                    record.provider,
                    record.model,
                    record.usage_type,
                    record.tokens_used,
                    record.cost,
                    record.status,
                    record.project_id or "",
                    record.error_message or ""
                ])
            
            return {
                "content": output.getvalue(),
                "content_type": "text/csv",
                "filename": f"usage_export_{datetime.utcnow().strftime('%Y%m%d')}.csv"
            }
        else:
            # Return JSON format
            return {
                "content": [record.model_dump() for record in records],
                "content_type": "application/json",
                "filename": f"usage_export_{datetime.utcnow().strftime('%Y%m%d')}.json"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting usage data: {str(e)}"
        ) 