from typing import Dict, Optional, Any, List
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class WebSocketMessageType(str, Enum):
    """Types of WebSocket messages."""
    # Connection management
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    
    # Authentication
    AUTH = "auth"
    AUTH_SUCCESS = "auth.success"
    AUTH_ERROR = "auth.error"
    
    # Subscription management
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    
    # Event handling
    EVENT = "event"
    EVENT_BATCH = "event.batch"
    EVENT_ERROR = "event.error"
    
    # Error handling
    ERROR = "error"
    ERROR_BATCH = "error.batch"
    
    # Connection health
    PING = "ping"
    PONG = "pong"
    HEARTBEAT = "heartbeat"
    
    # System messages
    SYSTEM_STATUS = "system.status"
    SYSTEM_CONFIG = "system.config"
    SYSTEM_ALERT = "system.alert"
    
    # User messages
    USER_STATUS = "user.status"
    USER_ACTIVITY = "user.activity"
    USER_PRESENCE = "user.presence"

class WebSocketSubscription(BaseModel):
    """Model for WebSocket subscriptions."""
    event_type: str = Field(..., description="Type of event to subscribe to")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters for the subscription")
    options: Optional[Dict[str, Any]] = Field(None, description="Optional subscription options")

class WebSocketMessage(BaseModel):
    """Base model for WebSocket messages."""
    type: WebSocketMessageType = Field(..., description="Type of message")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: Optional[datetime] = Field(None, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")

class WebSocketError(BaseModel):
    """Model for WebSocket error messages."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: Optional[datetime] = Field(None, description="When the error occurred")

class WebSocketEvent(BaseModel):
    """Model for WebSocket events."""
    event_type: str = Field(..., description="Type of event")
    timestamp: datetime = Field(..., description="When the event occurred")
    data: Dict[str, Any] = Field(..., description="Event data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional event metadata")
    sequence: Optional[int] = Field(None, description="Event sequence number")
    batch_id: Optional[str] = Field(None, description="ID for batched events")

class WebSocketConnectionInfo(BaseModel):
    """Model for WebSocket connection information."""
    user_id: str = Field(..., description="ID of the connected user")
    connected_at: datetime = Field(..., description="When the connection was established")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    subscriptions: Dict[str, datetime] = Field(default_factory=dict, description="Active subscriptions")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional connection metadata")
    client_info: Optional[Dict[str, Any]] = Field(None, description="Client information")
    connection_id: Optional[str] = Field(None, description="Unique connection ID")

class WebSocketSystemStatus(BaseModel):
    """Model for system status updates."""
    status: str = Field(..., description="Current system status")
    timestamp: datetime = Field(..., description="When the status was recorded")
    metrics: Optional[Dict[str, Any]] = Field(None, description="System metrics")
    alerts: Optional[List[Dict[str, Any]]] = Field(None, description="Active system alerts")
    version: Optional[str] = Field(None, description="System version")
    uptime: Optional[float] = Field(None, description="System uptime in seconds")

class WebSocketUserStatus(BaseModel):
    """Model for user status updates."""
    user_id: str = Field(..., description="ID of the user")
    status: str = Field(..., description="Current user status")
    timestamp: datetime = Field(..., description="When the status was recorded")
    activity: Optional[Dict[str, Any]] = Field(None, description="User activity information")
    presence: Optional[Dict[str, Any]] = Field(None, description="User presence information")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional user metadata")

class WebSocketHeartbeat(BaseModel):
    """Model for connection heartbeat messages."""
    timestamp: datetime = Field(..., description="When the heartbeat was sent")
    sequence: Optional[int] = Field(None, description="Heartbeat sequence number")
    latency: Optional[float] = Field(None, description="Connection latency in milliseconds")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional heartbeat metadata") 