from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from ....db.models.early_access import UseCase, ReferralSource
from ....storage.waitlist_store import waitlist_store
from ....core.email.email_service import email_service

router = APIRouter()

class EarlyAccessRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None
    use_case: Optional[UseCase] = None
    referral_source: Optional[ReferralSource] = None
    privacy_policy_accepted: bool

class WaitlistStatusResponse(BaseModel):
    status: str
    position: Optional[int] = None
    invitation_code: Optional[str] = None

@router.post("/early-access/signup")
async def signup_for_early_access(request: EarlyAccessRequest):
    """Submit an early access request"""
    try:
        # Check if email already exists
        existing_request = await waitlist_store.get_request_by_email(request.email)
        if existing_request:
            raise HTTPException(
                status_code=400,
                detail="Email already registered for early access"
            )
        
        # Get next position in waitlist
        position = await waitlist_store.get_next_position()
        
        # Create request
        request_data = request.dict()
        request_data["position"] = position
        request_data["status"] = "pending"
        
        await waitlist_store.create_request(request_data)
        
        # Send confirmation email
        await email_service.send_confirmation_email(
            request.email,
            request.name,
            position
        )
        
        return {
            "message": "Early access request submitted successfully",
            "position": position
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/early-access/status/{email}", response_model=WaitlistStatusResponse)
async def check_waitlist_status(email: str):
    """Check the status of an early access request"""
    try:
        request = await waitlist_store.get_request_by_email(email)
        if not request:
            raise HTTPException(
                status_code=404,
                detail="Email not found in waitlist"
            )
        
        return {
            "status": request["status"],
            "position": request.get("position"),
            "invitation_code": request.get("invitation_code")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/early-access/verify-invitation/{code}")
async def verify_invitation_code(code: str):
    """Verify an invitation code"""
    try:
        # TODO: Implement invitation code verification
        # This will be used during the registration process
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 