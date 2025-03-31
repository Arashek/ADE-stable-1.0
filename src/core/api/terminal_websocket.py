import asyncio
import logging
import json
from typing import Dict, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
import jwt
from dataclasses import dataclass
from enum import Enum

from ..terminal.terminal_service import TerminalService, TerminalSession

logger = logging.getLogger(__name__)

class WebSocketMessageType(Enum):
    """Types of WebSocket messages"""
    CONNECT = "connect"
    COMMAND = "command"
    OUTPUT = "output"
    ERROR = "error"
    STATUS = "status"
    DISCONNECT = "disconnect"

@dataclass
class WebSocketMessage:
    """Represents a WebSocket message"""
    type: WebSocketMessageType
    data: Dict[str, Any]
    timestamp: datetime

class TerminalWebSocketManager:
    """Manages WebSocket connections for terminal sessions"""
    
    def __init__(
        self,
        terminal_service: TerminalService,
        secret_key: str,
        algorithm: str = "HS256"
    ):
        """Initialize WebSocket manager
        
        Args:
            terminal_service: Terminal service instance
            secret_key: JWT secret key
            algorithm: JWT algorithm
        """
        self.terminal_service = terminal_service
        self.secret_key = secret_key
        self.algorithm = algorithm
        
        # Active connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
        # OAuth2 scheme
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        
    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """Handle WebSocket connection
        
        Args:
            websocket: WebSocket connection
            session_id: Terminal session ID
        """
        try:
            # Accept connection
            await websocket.accept()
            
            # Add to active connections
            if session_id not in self.active_connections:
                self.active_connections[session_id] = set()
            self.active_connections[session_id].add(websocket)
            
            # Send connection success message
            await self._send_message(
                websocket,
                WebSocketMessageType.CONNECT,
                {"status": "connected", "session_id": session_id}
            )
            
        except Exception as e:
            logger.error(f"Failed to handle WebSocket connection: {str(e)}")
            raise
            
    async def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        """Handle WebSocket disconnection
        
        Args:
            websocket: WebSocket connection
            session_id: Terminal session ID
        """
        try:
            # Remove from active connections
            if session_id in self.active_connections:
                self.active_connections[session_id].remove(websocket)
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
                    
            # Close connection
            await websocket.close()
            
        except Exception as e:
            logger.error(f"Failed to handle WebSocket disconnection: {str(e)}")
            
    async def handle_message(
        self,
        websocket: WebSocket,
        session_id: str,
        message: str
    ) -> None:
        """Handle incoming WebSocket message
        
        Args:
            websocket: WebSocket connection
            session_id: Terminal session ID
            message: Message content
        """
        try:
            # Parse message
            data = json.loads(message)
            message_type = WebSocketMessageType(data.get("type"))
            
            if message_type == WebSocketMessageType.COMMAND:
                # Handle command execution
                command = data.get("command")
                if not command:
                    raise ValueError("No command provided")
                    
                # Execute command
                result = await self.terminal_service.execute_command(
                    session_id,
                    command,
                    data.get("user_id")
                )
                
                # Send result
                await self._send_message(
                    websocket,
                    WebSocketMessageType.OUTPUT,
                    result
                )
                
            elif message_type == WebSocketMessageType.DISCONNECT:
                # Handle disconnection request
                await self.disconnect(websocket, session_id)
                
            else:
                raise ValueError(f"Unsupported message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Failed to handle WebSocket message: {str(e)}")
            await self._send_message(
                websocket,
                WebSocketMessageType.ERROR,
                {"error": str(e)}
            )
            
    async def broadcast_session_status(
        self,
        session_id: str,
        status: Dict[str, Any]
    ) -> None:
        """Broadcast session status to all connected clients
        
        Args:
            session_id: Terminal session ID
            status: Status data
        """
        try:
            if session_id in self.active_connections:
                message = WebSocketMessage(
                    type=WebSocketMessageType.STATUS,
                    data=status,
                    timestamp=datetime.utcnow()
                )
                
                for websocket in self.active_connections[session_id]:
                    await self._send_message(
                        websocket,
                        message.type,
                        message.data
                    )
                    
        except Exception as e:
            logger.error(f"Failed to broadcast session status: {str(e)}")
            
    async def _send_message(
        self,
        websocket: WebSocket,
        message_type: WebSocketMessageType,
        data: Dict[str, Any]
    ) -> None:
        """Send message to WebSocket client
        
        Args:
            websocket: WebSocket connection
            message_type: Message type
            data: Message data
        """
        try:
            message = {
                "type": message_type.value,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_text(json.dumps(message))
            
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {str(e)}")
            
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token
        
        Args:
            token: JWT token
            
        Returns:
            Decoded token data
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
            
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
            
    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """Get current user from token
        
        Args:
            token: JWT token
            
        Returns:
            User data
        """
        try:
            payload = self.verify_token(token)
            return payload
            
        except Exception as e:
            logger.error(f"Failed to get current user: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials"
            ) 