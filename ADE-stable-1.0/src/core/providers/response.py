from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ProviderResponse(BaseModel):
    """Base class for provider responses"""
    success: bool
    provider: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True

class TextResponse(ProviderResponse):
    """Response containing generated text"""
    text: str = ""
    
class ImageResponse(ProviderResponse):
    """Response containing image analysis or generation"""
    text: Optional[str] = None
    image_url: Optional[str] = None
    image_data: Optional[bytes] = None

class PlanResponse(ProviderResponse):
    """Response containing a generated plan"""
    plan: Dict[str, Any] = Field(default_factory=dict)


