import asyncio
import json
import logging
import uuid
from typing import Dict, Optional, Callable, Any
from websockets import connect, WebSocketClientProtocol
from datetime import datetime

logger = logging.getLogger(__name__)

class TrainingChatClient:
    def __init__(self, server_url: str = "ws://localhost:8000"):
        self.server_url = server_url
        self.session_id = str(uuid.uuid4())
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.connected = False
        self.message_handlers: Dict[str, Callable] = {}
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1.0
        
    async def connect(self, training_id: str):
        """Connect to the training chat server"""
        try:
            self.websocket = await connect(
                f"{self.server_url}/ws/{self.session_id}/{training_id}"
            )
            self.connected = True
            self.reconnect_attempts = 0
            
            # Start message handler
            asyncio.create_task(self._handle_messages())
            
        except Exception as e:
            logger.error(f"Failed to connect to server: {str(e)}")
            await self._handle_reconnect(training_id)
            
    async def _handle_reconnect(self, training_id: str):
        """Handle reconnection attempts"""
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            delay = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))
            logger.info(f"Attempting to reconnect in {delay} seconds...")
            await asyncio.sleep(delay)
            await self.connect(training_id)
        else:
            logger.error("Max reconnection attempts reached")
            self.connected = False
            
    async def _handle_messages(self):
        """Handle incoming WebSocket messages"""
        try:
            while self.connected:
                message = await self.websocket.recv()
                data = json.loads(message)
                message_type = data.get("type")
                
                if message_type in self.message_handlers:
                    await self.message_handlers[message_type](data)
                    
        except Exception as e:
            logger.error(f"Error handling messages: {str(e)}")
            self.connected = False
            
    def register_handler(self, message_type: str, handler: Callable):
        """Register a handler for a specific message type"""
        self.message_handlers[message_type] = handler
        
    async def send_message(self, message_type: str, data: Dict[str, Any]):
        """Send a message to the server"""
        if not self.connected:
            raise ConnectionError("Not connected to server")
            
        message = {
            "type": message_type,
            **data
        }
        
        await self.websocket.send(json.dumps(message))
        
    async def update_metrics(self, metrics: Dict[str, Any]):
        """Update training metrics"""
        await self.send_message("metrics", {"metrics": metrics})
        
    async def report_checkpoint(self, checkpoint: Dict[str, Any]):
        """Report a new checkpoint"""
        await self.send_message("checkpoint", {"checkpoint": checkpoint})
        
    async def update_status(self, status: str):
        """Update training status"""
        await self.send_message("status", {"status": status})
        
    async def report_resources(self, resources: Dict[str, Any]):
        """Report resource utilization"""
        await self.send_message("resources", {"resources": resources})
        
    async def send_control_command(self, command: Dict[str, Any]):
        """Send a control command to the training process"""
        await self.send_message("control", {"command": command})
        
    async def close(self):
        """Close the WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            
    def __del__(self):
        """Cleanup on deletion"""
        if self.websocket:
            asyncio.create_task(self.close()) 