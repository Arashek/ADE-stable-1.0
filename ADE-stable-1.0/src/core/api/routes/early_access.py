from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import re
from ...storage.waitlist_store import waitlist_store
from ...core.email.email_service import email_service

router = APIRouter()

class EarlyAccessRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None
    use_case: Optional[str] = None
    privacy_policy: bool

def validate_email(email: str) -> bool:
    """Validate email format and domain"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    
    # Add additional domain validation if needed
    return True

async def send_confirmation_email(email: str, name: Optional[str] = None):
    """Send confirmation email to the user"""
    subject = "Welcome to CloudEV.ai Early Access"
    template = "early_access_confirmation"
    
    await email_service.send_email(
        to_email=email,
        subject=subject,
        template=template,
        template_data={
            "name": name or "there",
            "email": email,
        }
    )

@router.post("/signup")
async def signup_for_early_access(
    request: EarlyAccessRequest,
    background_tasks: BackgroundTasks
):
    """Handle early access signup requests"""
    try:
        # Validate email
        if not validate_email(request.email):
            raise HTTPException(
                status_code=400,
                detail="Invalid email format"
            )

        # Check for duplicate submissions
        existing_request = await waitlist_store.get_request_by_email(request.email)
        if existing_request:
            raise HTTPException(
                status_code=400,
                detail="Email already registered for early access"
            )

        # Create waitlist entry
        waitlist_entry = {
            "email": request.email,
            "name": request.name,
            "company": request.company,
            "use_case": request.use_case,
            "status": "pending",
            "submitted_at": datetime.utcnow(),
            "position": await waitlist_store.get_next_position(),
        }

        await waitlist_store.create_request(waitlist_entry)

        # Send confirmation email in background
        background_tasks.add_task(
            send_confirmation_email,
            request.email,
            request.name
        )

        return {
            "message": "Successfully registered for early access",
            "position": waitlist_entry["position"],
            "email": request.email
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process early access request: {str(e)}"
        )

@router.get("/status/{email}")
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
            "position": request["position"],
            "submitted_at": request["submitted_at"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check waitlist status: {str(e)}"
        ) 