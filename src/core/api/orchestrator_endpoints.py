from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import logging
from datetime import datetime

from src.core.api.middleware.auth import require_permissions
from src.core.api.models.orchestrator import (
    PlanCreate,
    PlanUpdate,
    PlanResponse,
    PlanListResponse,
    PlanFilter,
    ErrorResponse,
    PlanStatus
)
from src.core.services.orchestrator_service import OrchestratorService
from src.core.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/plans", tags=["plans"])

@router.get(
    "",
    response_model=PlanListResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def list_plans(
    status: Optional[PlanStatus] = None,
    type: Optional[str] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user: User = Depends(require_permissions("plans:read")),
    orchestrator: OrchestratorService = Depends()
):
    """
    List all plans with optional filtering and pagination.
    """
    try:
        filter_params = PlanFilter(
            status=status,
            type=type,
            created_after=created_after,
            created_before=created_before,
            search=search
        )
        
        plans, total = await orchestrator.list_plans(
            user_id=user.id,
            filter_params=filter_params,
            page=page,
            page_size=page_size
        )
        
        return PlanListResponse(
            plans=plans,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"Error listing plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def create_plan(
    plan: PlanCreate,
    user: User = Depends(require_permissions("plans:create")),
    orchestrator: OrchestratorService = Depends()
):
    """
    Create a new plan.
    """
    try:
        created_plan = await orchestrator.create_plan(
            user_id=user.id,
            name=plan.name,
            description=plan.description,
            type=plan.type,
            steps=plan.steps,
            parameters=plan.parameters,
            timeout=plan.timeout,
            retry_count=plan.retry_count,
            retry_delay=plan.retry_delay
        )
        
        logger.info(f"Plan created successfully: {created_plan.id}")
        return created_plan
    except ValueError as e:
        logger.warning(f"Invalid plan data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/{plan_id}",
    response_model=PlanResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_plan(
    plan_id: str,
    user: User = Depends(require_permissions("plans:read")),
    orchestrator: OrchestratorService = Depends()
):
    """
    Get details of a specific plan.
    """
    try:
        plan = await orchestrator.get_plan(plan_id, user.id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        return plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plan {plan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/{plan_id}/execute",
    response_model=PlanResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def execute_plan(
    plan_id: str,
    user: User = Depends(require_permissions("plans:execute")),
    orchestrator: OrchestratorService = Depends()
):
    """
    Execute a plan.
    """
    try:
        plan = await orchestrator.get_plan(plan_id, user.id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        if plan.status in [PlanStatus.RUNNING, PlanStatus.COMPLETED]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Plan is already {plan.status.value}"
            )
        
        executed_plan = await orchestrator.execute_plan(plan_id, user.id)
        logger.info(f"Plan {plan_id} execution started")
        return executed_plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing plan {plan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete(
    "/{plan_id}",
    response_model=PlanResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def cancel_plan(
    plan_id: str,
    user: User = Depends(require_permissions("plans:delete")),
    orchestrator: OrchestratorService = Depends()
):
    """
    Cancel a plan.
    """
    try:
        plan = await orchestrator.get_plan(plan_id, user.id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        if plan.status not in [PlanStatus.PENDING, PlanStatus.RUNNING]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot cancel plan in {plan.status.value} status"
            )
        
        cancelled_plan = await orchestrator.cancel_plan(plan_id, user.id)
        logger.info(f"Plan {plan_id} cancelled successfully")
        return cancelled_plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling plan {plan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 