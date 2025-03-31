from datetime import datetime
from typing import Dict, Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Subscription(BaseModel):
    """MongoDB schema for user subscriptions"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    tier_name: str
    status: str  # active, canceled, past_due, etc.
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UsageRecord(BaseModel):
    """MongoDB schema for usage records"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    feature: str
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    period: str  # monthly, yearly, lifetime
    metadata: Dict = Field(default_factory=dict)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class BillingHistory(BaseModel):
    """MongoDB schema for billing history"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    subscription_id: Optional[str] = None
    amount: float
    currency: str = "usd"
    status: str  # paid, failed, refunded
    payment_method: str
    invoice_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class EarlyAccessRequest(BaseModel):
    """MongoDB schema for early access requests"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: str
    company: Optional[str] = None
    use_case: Optional[str] = None
    status: str = "pending"  # pending, approved, rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# MongoDB indexes
SUBSCRIPTION_INDEXES = [
    [("user_id", 1)],
    [("stripe_subscription_id", 1), {"unique": True}],
    [("stripe_customer_id", 1)],
    [("status", 1)],
    [("current_period_end", 1)],
]

USAGE_RECORD_INDEXES = [
    [("user_id", 1), ("feature", 1), ("timestamp", -1)],
    [("user_id", 1), ("period", 1), ("timestamp", -1)],
    [("timestamp", 1), {"expireAfterSeconds": 60 * 60 * 24 * 365}]  # TTL index for 1 year
]

BILLING_HISTORY_INDEXES = [
    [("user_id", 1), ("created_at", -1)],
    [("subscription_id", 1)],
    [("status", 1)],
    [("created_at", 1), {"expireAfterSeconds": 60 * 60 * 24 * 365 * 7}]  # TTL index for 7 years
]

EARLY_ACCESS_INDEXES = [
    [("email", 1), {"unique": True}],
    [("status", 1)],
    [("created_at", 1)],
]

def create_indexes(db):
    """Create all necessary indexes in MongoDB"""
    # Subscription indexes
    for index in SUBSCRIPTION_INDEXES:
        db.subscriptions.create_index(*index)
    
    # Usage record indexes
    for index in USAGE_RECORD_INDEXES:
        db.usage_records.create_index(*index)
    
    # Billing history indexes
    for index in BILLING_HISTORY_INDEXES:
        db.billing_history.create_index(*index)
    
    # Early access indexes
    for index in EARLY_ACCESS_INDEXES:
        db.early_access.create_index(*index) 