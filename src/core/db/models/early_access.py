from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class WaitlistStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    INVITED = "invited"
    REGISTERED = "registered"

class UseCase(str, Enum):
    PERSONAL = "personal"
    STARTUP = "startup"
    ENTERPRISE = "enterprise"
    RESEARCH = "research"
    EDUCATION = "education"
    OTHER = "other"

class ReferralSource(str, Enum):
    GOOGLE = "google"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FRIEND = "friend"
    BLOG = "blog"
    OTHER = "other"

class EarlyAccessRequest(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None
    use_case: Optional[UseCase] = None
    referral_source: Optional[ReferralSource] = None
    position: int
    status: WaitlistStatus = WaitlistStatus.PENDING
    invitation_code: Optional[str] = None
    privacy_policy_accepted: bool
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    invited_at: Optional[datetime] = None
    registered_at: Optional[datetime] = None

    class Config:
        use_enum_values = True 