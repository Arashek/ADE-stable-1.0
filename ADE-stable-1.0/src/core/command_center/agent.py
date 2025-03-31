from typing import Dict, List, Any, Optional
import asyncio
import websockets
import json
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, agent_type: str, capabilities: List[str], command_center_url: str):
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.command_center_url = command_center_url
        self.agent_id: Optional[str] = None
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.current_task: Optional[Dict[str, Any]] = None
        
    async def connect(self):
        """Connect to the command center"""
        try:
            self.websocket = await websockets.connect(
                f"{self.command_center_url}/ws/agent/{self.agent_type}"
            )
            
            # Register with command center
            await self.websocket.send(json.dumps({
                "type": "register",
                "capabilities": self.capabilities
            }))
            
            # Wait for registration confirmation
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get("type") == "registered":
                self.agent_id = data.get("agent_id")
                logger.info(f"Agent registered with ID: {self.agent_id}")
                return True
            else:
                logger.error("Failed to register agent")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to command center: {str(e)}")
            return False
            
    async def disconnect(self):
        """Disconnect from the command center"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.agent_id = None
            
    async def start(self):
        """Start the agent's main loop"""
        if not await self.connect():
            return
            
        try:
            while True:
                message = await self.websocket.recv()
                await self.handle_message(json.loads(message))
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection to command center closed")
        except Exception as e:
            logger.error(f"Error in agent loop: {str(e)}")
        finally:
            await self.disconnect()
            
    async def handle_message(self, message: Dict[str, Any]):
        """Handle incoming messages from the command center"""
        message_type = message.get("type")
        
        if message_type == "task_assigned":
            await self.handle_task_assignment(message.get("task"))
        else:
            logger.warning(f"Unknown message type: {message_type}")
            
    async def handle_task_assignment(self, task: Dict[str, Any]):
        """Handle task assignment from command center"""
        self.current_task = task
        try:
            result = await self.execute_task(task)
            await self.send_task_completion(task["task_id"], result)
        except Exception as e:
            await self.send_task_error(task["task_id"], str(e))
            
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """Execute the assigned task"""
        pass
        
    async def send_task_completion(self, task_id: str, result: Any):
        """Send task completion message"""
        if self.websocket:
            await self.websocket.send(json.dumps({
                "type": "task_completed",
                "task_id": task_id,
                "result": result
            }))
            
    async def send_task_error(self, task_id: str, error: str):
        """Send task error message"""
        if self.websocket:
            await self.websocket.send(json.dumps({
                "type": "task_error",
                "task_id": task_id,
                "error": error
            }))
            
    async def send_status_update(self, status: str):
        """Send status update message"""
        if self.websocket:
            await self.websocket.send(json.dumps({
                "type": "status_update",
                "status": status
            }))
            
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "type": self.agent_type,
            "capabilities": self.capabilities,
            "current_task": self.current_task
        } 