import pytest
import asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from fastapi import FastAPI
from jose import jwt
from typing import Dict, Any, Optional

from src.core.api.websocket_server import WebSocketServer, ConnectionManager, SecurityManager
from src.core.models.websocket import (
    WebSocketMessage,
    WebSocketMessageType,
    WebSocketSubscription,
    WebSocketEvent
)
from src.core.utils.events import EventType, Event
from src.core.config import settings

# Test fixtures
@pytest.fixture
def app():
    """Create a test FastAPI application."""
    app = FastAPI()
    return app

@pytest.fixture
def test_client(app):
    """Create a test client."""
    return TestClient(app)

@pytest.fixture
def websocket_server():
    """Create a WebSocket server instance."""
    return WebSocketServer()

@pytest.fixture
def connection_manager():
    """Create a connection manager instance."""
    return ConnectionManager()

@pytest.fixture
def security_manager():
    """Create a security manager instance."""
    return SecurityManager()

@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket connection."""
    class MockWebSocket:
        def __init__(self):
            self.client = type('Client', (), {'host': '127.0.0.1'})()
            self.query_params = {}
            self.accepted = False
            self.closed = False
            self.close_code = None
            self.close_reason = None
            self.sent_messages = []
            
        async def accept(self):
            self.accepted = True
            
        async def close(self, code: int = 1000, reason: str = ""):
            self.closed = True
            self.close_code = code
            self.close_reason = reason
            
        async def send_json(self, data: Dict[str, Any]):
            self.sent_messages.append(data)
            
        async def receive_text(self):
            return '{"type": "ping", "data": {}}'
            
    return MockWebSocket()

@pytest.fixture
def mock_token():
    """Create a mock JWT token."""
    return jwt.encode(
        {"sub": "test_user", "exp": datetime.utcnow() + timedelta(hours=1)},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

# Security Manager Tests
def test_security_manager_initialization(security_manager):
    """Test security manager initialization."""
    assert len(security_manager.blacklisted_ips) == 0
    assert len(security_manager.failed_attempts) == 0
    assert len(security_manager.connection_attempts) == 0

def test_security_manager_ip_blacklisting(security_manager):
    """Test IP blacklisting functionality."""
    ip = "127.0.0.1"
    
    # Record failed attempts
    for _ in range(security_manager.max_failed_attempts):
        security_manager.record_failed_attempt(ip)
        
    assert security_manager.is_ip_blacklisted(ip)
    assert not security_manager.can_connect(ip)

def test_security_manager_connection_limits(security_manager):
    """Test connection rate limiting."""
    ip = "127.0.0.1"
    
    # Record connection attempts
    for _ in range(security_manager.max_connections_per_ip):
        security_manager.record_connection_attempt(ip)
        
    assert not security_manager.can_connect(ip)

def test_security_manager_cleanup(security_manager):
    """Test cleanup of old connection attempts."""
    ip = "127.0.0.1"
    security_manager.record_connection_attempt(ip)
    
    # Simulate time passing
    security_manager.connection_attempts[ip][0] = datetime.now() - timedelta(minutes=2)
    
    security_manager.cleanup()
    assert ip not in security_manager.connection_attempts

# Connection Manager Tests
def test_connection_manager_initialization(connection_manager):
    """Test connection manager initialization."""
    assert len(connection_manager.active_connections) == 0
    assert len(connection_manager.user_subscriptions) == 0
    assert len(connection_manager.rate_limits) == 0
    assert len(connection_manager.connection_info) == 0

@pytest.mark.asyncio
async def test_connection_manager_connect(connection_manager, mock_websocket):
    """Test connection establishment."""
    user_id = "test_user"
    client_ip = "127.0.0.1"
    
    await connection_manager.connect(mock_websocket, user_id, client_ip)
    
    assert user_id in connection_manager.active_connections
    assert user_id in connection_manager.user_subscriptions
    assert user_id in connection_manager.rate_limits
    assert user_id in connection_manager.connection_info
    
    info = connection_manager.connection_info[user_id]
    assert info.user_id == user_id
    assert info.metadata["client_ip"] == client_ip

def test_connection_manager_disconnect(connection_manager):
    """Test connection cleanup."""
    user_id = "test_user"
    
    # Set up test data
    connection_manager.active_connections[user_id] = None
    connection_manager.user_subscriptions[user_id] = set()
    connection_manager.rate_limits[user_id] = {}
    connection_manager.connection_info[user_id] = None
    
    connection_manager.disconnect(user_id)
    
    assert user_id not in connection_manager.active_connections
    assert user_id not in connection_manager.user_subscriptions
    assert user_id not in connection_manager.rate_limits
    assert user_id not in connection_manager.connection_info

def test_connection_manager_subscription(connection_manager):
    """Test subscription management."""
    user_id = "test_user"
    event_type = EventType.PLAN_CREATED
    
    connection_manager.subscribe(user_id, event_type)
    assert connection_manager.is_subscribed(user_id, event_type)
    
    connection_manager.unsubscribe(user_id, event_type)
    assert not connection_manager.is_subscribed(user_id, event_type)

def test_connection_manager_rate_limit(connection_manager):
    """Test rate limiting."""
    user_id = "test_user"
    
    # Set up rate limit
    connection_manager.rate_limits[user_id] = {
        "messages": 0,
        "last_reset": datetime.now()
    }
    
    # Test rate limit check
    assert not connection_manager.check_rate_limit(user_id)
    
    # Simulate exceeding rate limit
    connection_manager.rate_limits[user_id]["messages"] = 1000
    assert connection_manager.check_rate_limit(user_id)

# WebSocket Server Tests
@pytest.mark.asyncio
async def test_websocket_server_authentication(websocket_server, mock_websocket, mock_token):
    """Test WebSocket authentication."""
    mock_websocket.query_params["token"] = mock_token
    
    user_id = await websocket_server.authenticate(mock_websocket)
    assert user_id == "test_user"
    
    # Test invalid token
    mock_websocket.query_params["token"] = "invalid_token"
    user_id = await websocket_server.authenticate(mock_websocket)
    assert user_id is None

@pytest.mark.asyncio
async def test_websocket_server_connection_handling(websocket_server, mock_websocket, mock_token):
    """Test WebSocket connection handling."""
    mock_websocket.query_params["token"] = mock_token
    
    # Test successful connection
    await websocket_server.handle_connection(mock_websocket)
    assert mock_websocket.accepted
    assert not mock_websocket.closed
    
    # Test message handling
    assert len(mock_websocket.sent_messages) > 0
    assert mock_websocket.sent_messages[0]["type"] == WebSocketMessageType.PONG

@pytest.mark.asyncio
async def test_websocket_server_subscription(websocket_server, mock_websocket, mock_token):
    """Test WebSocket subscription handling."""
    mock_websocket.query_params["token"] = mock_token
    await websocket_server.handle_connection(mock_websocket)
    
    # Test subscription
    subscription = WebSocketSubscription(event_type=EventType.PLAN_CREATED.value)
    message = WebSocketMessage(
        type=WebSocketMessageType.SUBSCRIBE,
        data=subscription.dict()
    )
    
    await websocket_server.handle_message("test_user", message.json())
    
    # Verify subscription
    assert websocket_server.manager.is_subscribed("test_user", EventType.PLAN_CREATED)
    
    # Test unsubscription
    message.type = WebSocketMessageType.UNSUBSCRIBE
    await websocket_server.handle_message("test_user", message.json())
    
    # Verify unsubscription
    assert not websocket_server.manager.is_subscribed("test_user", EventType.PLAN_CREATED)

@pytest.mark.asyncio
async def test_websocket_server_event_broadcasting(websocket_server, mock_websocket, mock_token):
    """Test WebSocket event broadcasting."""
    mock_websocket.query_params["token"] = mock_token
    await websocket_server.handle_connection(mock_websocket)
    
    # Subscribe to an event type
    subscription = WebSocketSubscription(event_type=EventType.PLAN_CREATED.value)
    message = WebSocketMessage(
        type=WebSocketMessageType.SUBSCRIBE,
        data=subscription.dict()
    )
    await websocket_server.handle_message("test_user", message.json())
    
    # Create and broadcast an event
    event = Event(
        type=EventType.PLAN_CREATED,
        timestamp=datetime.now(),
        data={"plan_id": "test_plan"}
    )
    
    await websocket_server.broadcast_event(event)
    
    # Verify event was sent
    event_messages = [
        msg for msg in mock_websocket.sent_messages
        if msg["type"] == WebSocketMessageType.EVENT
    ]
    assert len(event_messages) > 0
    assert event_messages[0]["data"]["event_type"] == EventType.PLAN_CREATED.value

@pytest.mark.asyncio
async def test_websocket_server_error_handling(websocket_server, mock_websocket, mock_token):
    """Test WebSocket error handling."""
    mock_websocket.query_params["token"] = mock_token
    await websocket_server.handle_connection(mock_websocket)
    
    # Test invalid JSON
    await websocket_server.handle_message("test_user", "invalid json")
    
    # Verify error message was sent
    error_messages = [
        msg for msg in mock_websocket.sent_messages
        if msg["type"] == WebSocketMessageType.ERROR
    ]
    assert len(error_messages) > 0
    assert "Invalid JSON format" in error_messages[0]["data"]["message"]
    
    # Test invalid message type
    message = WebSocketMessage(
        type="invalid_type",
        data={}
    )
    await websocket_server.handle_message("test_user", message.json())
    
    error_messages = [
        msg for msg in mock_websocket.sent_messages
        if msg["type"] == WebSocketMessageType.ERROR
    ]
    assert len(error_messages) > 1
    assert "Invalid message type" in error_messages[1]["data"]["message"]

@pytest.mark.asyncio
async def test_websocket_server_cleanup(websocket_server, mock_websocket, mock_token):
    """Test WebSocket cleanup functionality."""
    mock_websocket.query_params["token"] = mock_token
    await websocket_server.handle_connection(mock_websocket)
    
    # Simulate inactivity
    info = websocket_server.manager.get_connection_info("test_user")
    info.last_activity = datetime.now() - timedelta(minutes=31)
    
    # Run cleanup
    websocket_server.manager.cleanup_inactive_connections()
    
    # Verify connection was cleaned up
    assert "test_user" not in websocket_server.manager.active_connections
    assert "test_user" not in websocket_server.manager.connection_info 