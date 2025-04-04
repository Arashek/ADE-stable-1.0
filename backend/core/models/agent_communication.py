from typing import Dict, List, Optional, Any
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CoordinationPattern(Enum):
    """Enumeration of different agent coordination patterns"""
    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"
    BROADCAST = "broadcast"
    CENTRALIZED = "centralized"
    DECENTRALIZED = "decentralized"
    HYBRID = "hybrid"

class MessageType(Enum):
    """Types of messages that can be exchanged between agents"""
    TASK_ASSIGNMENT = "task_assignment"
    RESULT = "result"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    REQUEST = "request"
    RESPONSE = "response"
    COORDINATION = "coordination"
    HEARTBEAT = "heartbeat"

class AgentMessage:
    """Represents a message exchanged between agents"""
    def __init__(
        self,
        message_id: str,
        sender_id: str,
        recipient_id: str,
        message_type: MessageType,
        content: Dict[str, Any],
        timestamp: datetime = None
    ):
        self.message_id = message_id
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.message_type = message_type
        self.content = content
        self.timestamp = timestamp or datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        return cls(
            message_id=data["message_id"],
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )

class AgentCommunicationSystem:
    """Manages communication between agents in the orchestration system"""
    def __init__(self, coordination_pattern: CoordinationPattern = CoordinationPattern.HIERARCHICAL):
        self.coordination_pattern = coordination_pattern
        self.message_queue = []
        self.agent_registry = {}
        self.logger = logging.getLogger(__name__)
        
    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message to an agent"""
        try:
            self.message_queue.append(message)
            self.logger.info(f"Message {message.message_id} queued for delivery")
            # In a real implementation, this would handle the actual message delivery
            # based on the coordination pattern
            return True
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return False
            
    async def broadcast_message(self, sender_id: str, message_type: MessageType, content: Dict[str, Any]) -> bool:
        """Broadcast a message to all registered agents"""
        try:
            for agent_id in self.agent_registry:
                if agent_id != sender_id:
                    # Create a new message for each recipient
                    message = AgentMessage(
                        message_id=f"{sender_id}-broadcast-{datetime.now().isoformat()}",
                        sender_id=sender_id,
                        recipient_id=agent_id,
                        message_type=message_type,
                        content=content
                    )
                    await self.send_message(message)
            return True
        except Exception as e:
            self.logger.error(f"Error broadcasting message: {str(e)}")
            return False
            
    async def register_agent(self, agent_id: str, agent_info: Dict[str, Any]) -> bool:
        """Register an agent with the communication system"""
        try:
            self.agent_registry[agent_id] = {
                "info": agent_info,
                "last_seen": datetime.now()
            }
            self.logger.info(f"Agent {agent_id} registered successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error registering agent: {str(e)}")
            return False
            
    async def unregister_agent(self, agent_id: str) -> bool:
        """Remove an agent from the registry"""
        try:
            if agent_id in self.agent_registry:
                del self.agent_registry[agent_id]
                self.logger.info(f"Agent {agent_id} unregistered successfully")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error unregistering agent: {str(e)}")
            return False
            
    async def get_registered_agents(self) -> List[str]:
        """Get a list of all registered agent IDs"""
        return list(self.agent_registry.keys())
