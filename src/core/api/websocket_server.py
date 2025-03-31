import asyncio
import json
import logging
from typing import Dict, Set, Optional, List
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from ..utils.events import EventType, Event, event_emitter
from ..config import settings
from ..models.user import User
from ..models.websocket import (
    WebSocketMessage,
    WebSocketMessageType,
    WebSocketSubscription,
    WebSocketError,
    WebSocketConnectionInfo
)

class SecurityManager:
    """Manages WebSocket security features."""
    
    def __init__(self):
        self.blacklisted_ips: Set[str] = set()
        self.failed_attempts: Dict[str, int] = {}
        self.connection_attempts: Dict[str, List[datetime]] = {}
        self.max_failed_attempts = 5
        self.max_connections_per_ip = 10
        self.connection_window = timedelta(minutes=1)
        self.logger = logging.getLogger(__name__)
        
    def is_ip_blacklisted(self, ip: str) -> bool:
        """Check if an IP is blacklisted.
        
        Args:
            ip: IP address to check
            
        Returns:
            True if IP is blacklisted
        """
        return ip in self.blacklisted_ips
        
    def record_failed_attempt(self, ip: str):
        """Record a failed connection attempt.
        
        Args:
            ip: IP address of the attempt
        """
        self.failed_attempts[ip] = self.failed_attempts.get(ip, 0) + 1
        if self.failed_attempts[ip] >= self.max_failed_attempts:
            self.blacklisted_ips.add(ip)
            self.logger.warning(f"IP {ip} blacklisted due to multiple failed attempts")
            
    def can_connect(self, ip: str) -> bool:
        """Check if an IP can establish a new connection.
        
        Args:
            ip: IP address to check
            
        Returns:
            True if connection is allowed
        """
        if self.is_ip_blacklisted(ip):
            return False
            
        # Check connection rate limit
        now = datetime.now()
        if ip in self.connection_attempts:
            # Remove old attempts
            self.connection_attempts[ip] = [
                t for t in self.connection_attempts[ip]
                if now - t < self.connection_window
            ]
            
            if len(self.connection_attempts[ip]) >= self.max_connections_per_ip:
                return False
                
        return True
        
    def record_connection_attempt(self, ip: str):
        """Record a connection attempt.
        
        Args:
            ip: IP address of the attempt
        """
        now = datetime.now()
        if ip not in self.connection_attempts:
            self.connection_attempts[ip] = []
        self.connection_attempts[ip].append(now)
        
    def cleanup(self):
        """Clean up old connection attempts."""
        now = datetime.now()
        for ip in list(self.connection_attempts.keys()):
            self.connection_attempts[ip] = [
                t for t in self.connection_attempts[ip]
                if now - t < self.connection_window
            ]
            if not self.connection_attempts[ip]:
                del self.connection_attempts[ip]

class ConnectionManager:
    """Manages WebSocket connections and subscriptions."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_subscriptions: Dict[str, Set[EventType]] = {}
        self.rate_limits: Dict[str, Dict[str, int]] = {}
        self.connection_info: Dict[str, WebSocketConnectionInfo] = {}
        self.security_manager = SecurityManager()
        self.logger = logging.getLogger(__name__)
        
    async def connect(self, websocket: WebSocket, user_id: str, client_ip: str):
        """Connect a new WebSocket client.
        
        Args:
            websocket: WebSocket connection
            user_id: ID of the connected user
            client_ip: IP address of the client
        """
        # Check security
        if not self.security_manager.can_connect(client_ip):
            await websocket.close(code=4008, reason="Too many connections")
            return
            
        # Record connection attempt
        self.security_manager.record_connection_attempt(client_ip)
        
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_subscriptions[user_id] = set()
        self.rate_limits[user_id] = {
            "messages": 0,
            "last_reset": datetime.now()
        }
        
        # Store connection info
        self.connection_info[user_id] = WebSocketConnectionInfo(
            user_id=user_id,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
            subscriptions={},
            metadata={"client_ip": client_ip}
        )
        
        self.logger.info(f"User {user_id} connected from {client_ip}")
        
    def disconnect(self, user_id: str):
        """Disconnect a WebSocket client.
        
        Args:
            user_id: ID of the user to disconnect
        """
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_subscriptions:
            del self.user_subscriptions[user_id]
        if user_id in self.rate_limits:
            del self.rate_limits[user_id]
        if user_id in self.connection_info:
            del self.connection_info[user_id]
        self.logger.info(f"User {user_id} disconnected")
        
    def update_activity(self, user_id: str):
        """Update last activity timestamp for a user.
        
        Args:
            user_id: ID of the user
        """
        if user_id in self.connection_info:
            self.connection_info[user_id].last_activity = datetime.now()
            
    def get_connection_info(self, user_id: str) -> Optional[WebSocketConnectionInfo]:
        """Get connection information for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Connection information or None if not found
        """
        return self.connection_info.get(user_id)
        
    def cleanup_inactive_connections(self, timeout: timedelta = timedelta(minutes=30)):
        """Clean up inactive connections.
        
        Args:
            timeout: Timeout period for inactivity
        """
        now = datetime.now()
        for user_id in list(self.active_connections.keys()):
            info = self.connection_info.get(user_id)
            if info and now - info.last_activity > timeout:
                self.disconnect(user_id)
        
    def subscribe(self, user_id: str, event_type: EventType):
        """Subscribe a user to an event type.
        
        Args:
            user_id: ID of the user to subscribe
            event_type: Type of event to subscribe to
        """
        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].add(event_type)
            self.logger.info(f"User {user_id} subscribed to {event_type}")
            
    def unsubscribe(self, user_id: str, event_type: EventType):
        """Unsubscribe a user from an event type.
        
        Args:
            user_id: ID of the user to unsubscribe
            event_type: Type of event to unsubscribe from
        """
        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].discard(event_type)
            self.logger.info(f"User {user_id} unsubscribed from {event_type}")
            
    def is_subscribed(self, user_id: str, event_type: EventType) -> bool:
        """Check if a user is subscribed to an event type.
        
        Args:
            user_id: ID of the user to check
            event_type: Type of event to check
            
        Returns:
            True if the user is subscribed
        """
        return user_id in self.user_subscriptions and event_type in self.user_subscriptions[user_id]
        
    def check_rate_limit(self, user_id: str) -> bool:
        """Check if a user has exceeded rate limits.
        
        Args:
            user_id: ID of the user to check
            
        Returns:
            True if rate limit is exceeded
        """
        if user_id not in self.rate_limits:
            return False
            
        limits = self.rate_limits[user_id]
        now = datetime.now()
        
        # Reset counter if time window has passed
        if (now - limits["last_reset"]) > timedelta(minutes=1):
            limits["messages"] = 0
            limits["last_reset"] = now
            return False
            
        # Check if limit is exceeded
        if limits["messages"] >= 100:  # 100 messages per minute
            return True
            
        limits["messages"] += 1
        return False

class WebSocketServer:
    """WebSocket server for real-time communication."""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.logger = logging.getLogger(__name__)
        self._cleanup_task = None
        
    def _start_cleanup_task(self):
        """Start the cleanup task."""
        if self._cleanup_task is None:
            async def cleanup_task():
                while True:
                    await asyncio.sleep(300)  # Run every 5 minutes
                    self.connection_manager.cleanup_inactive_connections()
                    self.connection_manager.security_manager.cleanup()
                    
            try:
                loop = asyncio.get_running_loop()
                self._cleanup_task = loop.create_task(cleanup_task())
            except RuntimeError:
                pass  # No event loop running, skip cleanup task
        
    async def authenticate(self, websocket: WebSocket) -> Optional[str]:
        """Authenticate a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            
        Returns:
            User ID if authenticated, None otherwise
        """
        try:
            # Get token from query parameters
            token = websocket.query_params.get("token")
            if not token:
                return None
                
            # Verify token
            payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
            user_id = payload.get("sub")
            if not user_id:
                return None
                
            return user_id
            
        except JWTError:
            return None
            
    async def handle_connection(self, websocket: WebSocket):
        """Handle a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
        """
        # Start cleanup task if not running
        self._start_cleanup_task()
        
        # Authenticate user
        user_id = await self.authenticate(websocket)
        if not user_id:
            await websocket.close(code=4001, reason="Authentication failed")
            return
            
        # Get client IP
        client_ip = websocket.client.host
        
        try:
            # Connect
            await self.connection_manager.connect(websocket, user_id, client_ip)
            
            # Handle messages
            while True:
                message = await websocket.receive_text()
                await self.handle_message(user_id, message)
                
        except WebSocketDisconnect:
            self.connection_manager.disconnect(user_id)
            
    async def handle_message(self, user_id: str, message: str):
        """Handle a WebSocket message.
        
        Args:
            user_id: ID of the user sending the message
            message: Message content
        """
        try:
            # Check rate limit
            if self.connection_manager.check_rate_limit(user_id):
                await self.send_error(user_id, "Rate limit exceeded")
                return
                
            # Parse message
            data = json.loads(message)
            msg = WebSocketMessage(**data)
            
            # Update activity
            self.connection_manager.update_activity(user_id)
            
            # Handle message based on type
            if msg.type == WebSocketMessageType.PING:
                await self.handle_ping(user_id)
            elif msg.type == WebSocketMessageType.SUBSCRIBE:
                await self.handle_subscription(user_id, msg)
            elif msg.type == WebSocketMessageType.UNSUBSCRIBE:
                await self.handle_unsubscription(user_id, msg)
                
        except json.JSONDecodeError:
            await self.send_error(user_id, "Invalid message format")
        except Exception as e:
            await self.send_error(user_id, str(e))
            
    async def handle_ping(self, user_id: str):
        """Handle a ping message.
        
        Args:
            user_id: ID of the user sending the ping
        """
        await self.send_message(user_id, {"type": "pong"})
        
    async def handle_subscription(self, user_id: str, message: WebSocketMessage):
        """Handle a subscription message.
        
        Args:
            user_id: ID of the user subscribing
            message: Subscription message
        """
        try:
            subscription = WebSocketSubscription(**message.data)
            event_type = EventType(subscription.event_type)
            
            # Subscribe user
            self.connection_manager.subscribe(user_id, event_type)
            
            # Send confirmation
            await self.send_message(user_id, {
                "type": "subscription_confirmed",
                "data": {"event_type": event_type.value}
            })
            
        except (ValueError, TypeError) as e:
            await self.send_error(user_id, f"Invalid subscription: {str(e)}")
            
    async def handle_unsubscription(self, user_id: str, message: WebSocketMessage):
        """Handle an unsubscription message.
        
        Args:
            user_id: ID of the user unsubscribing
            message: Unsubscription message
        """
        try:
            subscription = WebSocketSubscription(**message.data)
            event_type = EventType(subscription.event_type)
            
            # Unsubscribe user
            self.connection_manager.unsubscribe(user_id, event_type)
            
            # Send confirmation
            await self.send_message(user_id, {
                "type": "unsubscription_confirmed",
                "data": {"event_type": event_type.value}
            })
            
        except (ValueError, TypeError) as e:
            await self.send_error(user_id, f"Invalid unsubscription: {str(e)}")
            
    async def broadcast_event(self, event: Event):
        """Broadcast an event to subscribed users.
        
        Args:
            event: Event to broadcast
        """
        message = {
            "type": "event",
            "data": {
                "type": event.type.value,
                "data": event.data
            }
        }
        
        for user_id in self.connection_manager.active_connections:
            if self.connection_manager.is_subscribed(user_id, event.type):
                await self.send_message(user_id, message)
                
    async def send_message(self, user_id: str, message: Dict):
        """Send a message to a user.
        
        Args:
            user_id: ID of the user to send to
            message: Message to send
        """
        if user_id in self.connection_manager.active_connections:
            websocket = self.connection_manager.active_connections[user_id]
            await websocket.send_json(message)
            
    async def send_error(self, user_id: str, message: str):
        """Send an error message to a user.
        
        Args:
            user_id: ID of the user to send to
            message: Error message
        """
        error = WebSocketError(message=message)
        await self.send_message(user_id, {
            "type": "error",
            "data": error.dict()
        })

# Create a global WebSocket server instance
websocket_server = None

def get_websocket_server() -> WebSocketServer:
    """Get the global WebSocket server instance."""
    global websocket_server
    if websocket_server is None:
        websocket_server = WebSocketServer()
    return websocket_server 