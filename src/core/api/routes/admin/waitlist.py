from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from ....db.models.early_access import WaitlistStatus
from ....storage.waitlist_store import waitlist_store
from ....core.auth.auth import get_current_admin_user

router = APIRouter()

class WaitlistResponse(BaseModel):
    requests: List[dict]
    stats: dict

class InviteRequest(BaseModel):
    message: str

class BulkActionRequest(BaseModel):
    ids: List[str]

@router.get("/waitlist", response_model=WaitlistResponse)
async def list_waitlist(
    current_user: dict = Depends(get_current_admin_user)
):
    """List all early access requests with statistics"""
    try:
        requests = await waitlist_store.get_pending_requests()
        stats = await waitlist_store.get_waitlist_stats()
        return {
            "requests": requests,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/waitlist/{request_id}/approve")
async def approve_request(
    request_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """Approve an early access request"""
    try:
        request = await waitlist_store.get_request_by_email(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if request["status"] != WaitlistStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail="Request is not in pending status"
            )
        
        await waitlist_store.update_request_status(
            request_id,
            WaitlistStatus.APPROVED
        )
        return {"message": "Request approved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/waitlist/{request_id}/reject")
async def reject_request(
    request_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """Reject an early access request"""
    try:
        request = await waitlist_store.get_request_by_email(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if request["status"] != WaitlistStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail="Request is not in pending status"
            )
        
        await waitlist_store.update_request_status(
            request_id,
            WaitlistStatus.REJECTED
        )
        return {"message": "Request rejected successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/waitlist/{request_id}/invite")
async def send_invitation(
    request_id: str,
    invite_data: InviteRequest,
    current_user: dict = Depends(get_current_admin_user)
):
    """Send an invitation to an approved request"""
    try:
        request = await waitlist_store.get_request_by_email(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if request["status"] != WaitlistStatus.APPROVED:
            raise HTTPException(
                status_code=400,
                detail="Request is not in approved status"
            )
        
        invitation_code = await waitlist_store.generate_invitation_code()
        await waitlist_store.update_request_status(
            request_id,
            WaitlistStatus.INVITED,
            invitation_code
        )
        
        # TODO: Send invitation email with code and message
        # await email_service.send_invitation_email(
        #     request["email"],
        #     invitation_code,
        #     invite_data.message
        # )
        
        return {"message": "Invitation sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/waitlist/bulk-approve")
async def bulk_approve_requests(
    action_data: BulkActionRequest,
    current_user: dict = Depends(get_current_admin_user)
):
    """Approve multiple early access requests"""
    try:
        for request_id in action_data.ids:
            request = await waitlist_store.get_request_by_email(request_id)
            if request and request["status"] == WaitlistStatus.PENDING:
                await waitlist_store.update_request_status(
                    request_id,
                    WaitlistStatus.APPROVED
                )
        
        return {"message": "Requests approved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/waitlist/bulk-reject")
async def bulk_reject_requests(
    action_data: BulkActionRequest,
    current_user: dict = Depends(get_current_admin_user)
):
    """Reject multiple early access requests"""
    try:
        for request_id in action_data.ids:
            request = await waitlist_store.get_request_by_email(request_id)
            if request and request["status"] == WaitlistStatus.PENDING:
                await waitlist_store.update_request_status(
                    request_id,
                    WaitlistStatus.REJECTED
                )
        
        return {"message": "Requests rejected successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/waitlist/stats")
async def get_waitlist_stats(
    current_user: dict = Depends(get_current_admin_user)
):
    """Get detailed waitlist statistics"""
    try:
        stats = await waitlist_store.get_waitlist_stats()
        use_cases = await waitlist_store.get_use_case_distribution()
        referral_sources = await waitlist_store.get_referral_sources()
        
        return {
            "overview": stats,
            "use_cases": use_cases,
            "referral_sources": referral_sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 