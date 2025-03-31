from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
import asyncio
from enum import Enum

class MessageType(Enum):
    TEXT = "text"
    CODE = "code"
    DIAGRAM = "diagram"
    DECISION = "decision"
    FILE = "file"
    STATUS = "status"

@dataclass
class Agent:
    id: str
    name: str
    role: str
    capabilities: List[str]
    color: str
    role_color: str
    status: str = "idle"

@dataclass
class Message:
    id: str
    agent_id: str
    content: Any
    type: MessageType
    timestamp: datetime
    thread_id: Optional[str] = None
    reactions: List[Dict] = None
    votes: Dict[str, int] = None

class AgentCommunicationAPI:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.active_threads: Dict[str, List[Message]] = {}
        self.message_history: List[Message] = []

    async def register_agent(self, agent: Agent) -> None:
        """Register a new agent in the system."""
        self.agents[agent.id] = agent
        await self._notify_agent_status_change(agent.id, "active")

    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the system."""
        if agent_id in self.agents:
            await self._notify_agent_status_change(agent_id, "inactive")
            del self.agents[agent_id]

    async def send_message(self, message: Message) -> None:
        """Send a message to the appropriate agent(s)."""
        self.message_history.append(message)
        await self.message_queue.put(message)

        if message.thread_id:
            if message.thread_id not in self.active_threads:
                self.active_threads[message.thread_id] = []
            self.active_threads[message.thread_id].append(message)

        await self._route_message(message)

    async def _route_message(self, message: Message) -> None:
        """Route message to appropriate agent(s) based on content and type."""
        target_agents = self._determine_target_agents(message)
        for agent_id in target_agents:
            if agent_id in self.agents:
                await self._deliver_to_agent(agent_id, message)

    def _determine_target_agents(self, message: Message) -> List[str]:
        """Determine which agents should receive the message."""
        target_agents = []
        
        # Route based on message type
        if message.type == MessageType.CODE:
            target_agents.extend([
                agent_id for agent_id, agent in self.agents.items()
                if "code_review" in agent.capabilities
            ])
        elif message.type == MessageType.DECISION:
            target_agents.extend([
                agent_id for agent_id, agent in self.agents.items()
                if "decision_making" in agent.capabilities
            ])
        elif message.type == MessageType.DIAGRAM:
            target_agents.extend([
                agent_id for agent_id, agent in self.agents.items()
                if "architecture" in agent.capabilities
            ])
        
        return list(set(target_agents))  # Remove duplicates

    async def _deliver_to_agent(self, agent_id: str, message: Message) -> None:
        """Deliver message to a specific agent."""
        agent = self.agents[agent_id]
        agent.status = "processing"
        await self._notify_agent_status_change(agent_id, "processing")
        
        # Simulate message processing
        await asyncio.sleep(0.1)
        
        agent.status = "idle"
        await self._notify_agent_status_change(agent_id, "idle")

    async def _notify_agent_status_change(self, agent_id: str, status: str) -> None:
        """Notify about agent status changes."""
        status_message = Message(
            id=f"status_{datetime.now().timestamp()}",
            agent_id=agent_id,
            content={"status": status},
            type=MessageType.STATUS,
            timestamp=datetime.now()
        )
        await self.message_queue.put(status_message)

    async def get_thread_messages(self, thread_id: str) -> List[Message]:
        """Retrieve all messages in a thread."""
        return self.active_threads.get(thread_id, [])

    async def add_reaction(self, message_id: str, reaction: Dict) -> None:
        """Add a reaction to a message."""
        for message in self.message_history:
            if message.id == message_id:
                if not message.reactions:
                    message.reactions = []
                message.reactions.append(reaction)
                break

    async def add_vote(self, message_id: str, vote: str) -> None:
        """Add a vote to a decision message."""
        for message in self.message_history:
            if message.id == message_id and message.type == MessageType.DECISION:
                if not message.votes:
                    message.votes = {"approve": 0, "reject": 0}
                message.votes[vote] += 1
                break

    async def get_agent_status(self, agent_id: str) -> Optional[str]:
        """Get the current status of an agent."""
        return self.agents.get(agent_id).status if agent_id in self.agents else None

    async def get_active_agents(self) -> List[Agent]:
        """Get list of currently active agents."""
        return [agent for agent in self.agents.values() if agent.status != "inactive"]

    async def search_messages(self, query: str) -> List[Message]:
        """Search through message history."""
        query = query.lower()
        return [
            message for message in self.message_history
            if query in str(message.content).lower()
        ]

    async def export_thread(self, thread_id: str) -> str:
        """Export a thread as JSON."""
        thread_messages = await self.get_thread_messages(thread_id)
        return json.dumps(
            [message.__dict__ for message in thread_messages],
            default=str
        ) 