import logging
import json
import threading
from typing import Dict, Any, Optional, List, Callable, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from uuid import uuid4
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessagePriority(Enum):
    URGENT = "urgent"
    NORMAL = "normal"
    BACKGROUND = "background"

class MessageCategory(Enum):
    QUERY = "query"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    THINKING = "thinking"
    STATUS = "status"
    HEARTBEAT = "heartbeat"

@dataclass
class ChainOfThought:
    """Represents the reasoning process for a decision."""
    steps: List[Dict[str, Any]]
    final_decision: str
    confidence: float
    alternatives: List[str] = field(default_factory=list)

@dataclass
class Message:
    """Enhanced message structure with advanced features."""
    category: MessageCategory
    priority: MessagePriority
    content: Dict[str, Any]
    sender_id: str
    receiver_id: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(uuid4()))
    reply_to: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    thread_id: Optional[str] = None
    parent_message_id: Optional[str] = None
    reasoning: Optional[ChainOfThought] = None
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    is_processed: bool = False
    processing_start: Optional[datetime] = None
    processing_end: Optional[datetime] = None

class AgentCommunicationSystem:
    """Enhanced system for managing communication between agents."""
    
    def __init__(self):
        """Initialize the communication system."""
        self.registered_agents: Set[str] = set()
        self.message_queues: Dict[str, asyncio.Queue] = {}
        self.message_handlers: Dict[MessageCategory, List[Callable]] = defaultdict(list)
        self.context_manager = ContextManager()
        self.message_history: Dict[str, List[Message]] = defaultdict(list)
        self.conversation_threads: Dict[str, List[Message]] = defaultdict(list)
        self.agent_contexts: Dict[str, Dict[str, Any]] = {}
        self.heartbeat_interval = 5  # seconds
        self.message_timeout = 30  # seconds
        self.lock = threading.Lock()
        self.monitoring_lock = threading.Lock()
        
        # Monitoring metrics
        self.metrics = {
            "message_counts": {},  # Agent ID -> Message counts by category
            "processing_times": {},  # Agent ID -> List of processing times
            "error_counts": {},  # Agent ID -> Error counts
            "bottleneck_threshold": 100,  # Messages in queue before bottleneck warning
            "response_time_threshold": 10.0,  # Seconds before response time warning
        }
        
        # Message bus subscribers
        self.subscribers: Dict[MessageCategory, List[Callable]] = {
            category: [] for category in MessageCategory
        }
        
        # Start monitoring and heartbeat threads
        self.heartbeat_thread = threading.Thread(target=self._send_heartbeats, daemon=True)
        self.monitoring_thread = threading.Thread(target=self._monitor_communication, daemon=True)
        self.heartbeat_thread.start()
        self.monitoring_thread.start()

    async def register_agent(self, agent_id: str) -> bool:
        """Register an agent in the communication system."""
        try:
            self.registered_agents.add(agent_id)
            self.message_queues[agent_id] = asyncio.Queue()
            self.agent_contexts[agent_id] = {
                "active_conversations": set(),
                "message_count": 0,
                "last_active": datetime.now(),
                "context": {}
            }
            return True
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {str(e)}")
            return False

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the communication system."""
        with self.lock:
            if agent_id not in self.message_queues:
                raise ValueError(f"Agent {agent_id} not found")
            
            del self.message_queues[agent_id]
            del self.message_handlers[agent_id]
            logger.info(f"Unregistered agent {agent_id}")

    def register_handler(self, agent_id: str, category: MessageCategory, 
                        handler: Callable[[Message], None]) -> None:
        """Register a message handler for an agent."""
        with self.lock:
            if agent_id not in self.message_handlers:
                raise ValueError(f"Agent {agent_id} not found")
            
            self.message_handlers[category].append(handler)
            logger.info(f"Registered handler for {category} messages from agent {agent_id}")

    def subscribe(self, category: MessageCategory, callback: Callable[[Message], None]) -> None:
        """Subscribe to messages of a specific category."""
        with self.lock:
            self.subscribers[category].append(callback)
            logger.info(f"New subscriber added for {category} messages")

    def unsubscribe(self, category: MessageCategory, callback: Callable[[Message], None]) -> None:
        """Unsubscribe from messages of a specific category."""
        with self.lock:
            if callback in self.subscribers[category]:
                self.subscribers[category].remove(callback)
                logger.info(f"Subscriber removed for {category} messages")

    async def send_message(self, message: Message) -> bool:
        """Send a message between agents with context awareness."""
        try:
            # Validate sender and receiver
            if message.sender_id not in self.registered_agents or \
               message.receiver_id not in self.registered_agents:
                return False
            
            # Add context to message
            message.context.update(self._get_relevant_context(message))
            
            # Update conversation thread
            if message.reply_to:
                thread_id = self._get_thread_id(message.reply_to)
                self.conversation_threads[thread_id].append(message)
            else:
                thread_id = message.message_id
                self.conversation_threads[thread_id] = [message]
            
            # Update agent contexts
            self._update_agent_contexts(message)
            
            # Add to message history
            self.message_history[message.sender_id].append(message)
            self.message_history[message.receiver_id].append(message)
            
            # Queue message for receiver
            await self.message_queues[message.receiver_id].put(message)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return False

    def _update_metrics(self, message: Message) -> None:
        """Update monitoring metrics for a message."""
        with self.monitoring_lock:
            # Update message counts
            if message.receiver_id not in self.metrics["message_counts"]:
                self.metrics["message_counts"][message.receiver_id] = {}
            if message.category not in self.metrics["message_counts"][message.receiver_id]:
                self.metrics["message_counts"][message.receiver_id][message.category] = 0
            self.metrics["message_counts"][message.receiver_id][message.category] += 1
            
            # Initialize processing times list if needed
            if message.receiver_id not in self.metrics["processing_times"]:
                self.metrics["processing_times"][message.receiver_id] = []
            
            # Initialize error counts if needed
            if message.receiver_id not in self.metrics["error_counts"]:
                self.metrics["error_counts"][message.receiver_id] = 0

    def _monitor_communication(self) -> None:
        """Monitor communication patterns and detect issues."""
        while True:
            try:
                with self.monitoring_lock:
                    for agent_id, queue in self.message_queues.items():
                        # Check for bottlenecks
                        if len(queue) > self.metrics["bottleneck_threshold"]:
                            logger.warning(f"Bottleneck detected for agent {agent_id}: {len(queue)} messages in queue")
                        
                        # Check for unresponsive agents
                        for message in queue:
                            if message.processing_start and not message.is_processed:
                                processing_time = (datetime.now() - message.processing_start).total_seconds()
                                if processing_time > self.metrics["response_time_threshold"]:
                                    logger.warning(
                                        f"Agent {agent_id} not responding to message {message.message_id} "
                                        f"for {processing_time:.1f} seconds"
                                    )
                        
                        # Check for communication loops
                        if len(self.metrics["processing_times"][agent_id]) > 10:
                            recent_times = self.metrics["processing_times"][agent_id][-10:]
                            if all(t > self.metrics["response_time_threshold"] for t in recent_times):
                                logger.warning(f"Possible communication loop detected for agent {agent_id}")
                
                threading.Event().wait(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring thread: {e}")
                threading.Event().wait(5)  # Wait before retrying

    def get_communication_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get communication metrics for an agent."""
        with self.monitoring_lock:
            if agent_id not in self.metrics["message_counts"]:
                return {"status": "not_found"}
            
            return {
                "message_counts": self.metrics["message_counts"][agent_id],
                "average_processing_time": (
                    sum(self.metrics["processing_times"][agent_id]) / 
                    len(self.metrics["processing_times"][agent_id])
                ) if self.metrics["processing_times"][agent_id] else 0,
                "error_count": self.metrics["error_counts"][agent_id],
                "queue_size": len(self.message_queues.get(agent_id, [])),
                "is_responsive": all(
                    t <= self.metrics["response_time_threshold"]
                    for t in self.metrics["processing_times"][agent_id][-5:]
                ) if self.metrics["processing_times"][agent_id] else True
            }

    def send_request(self, sender_id: str, receiver_id: str, 
                    content: Dict[str, Any], timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Send a request and wait for a response."""
        # Create request message
        request = Message(
            message_id=f"req_{datetime.now().timestamp()}",
            sender_id=sender_id,
            receiver_id=receiver_id,
            category=MessageCategory.QUERY,
            content=content
        )
        
        # Send request
        if not self.send_message(request):
            return None
        
        # Wait for response
        response = self._wait_for_response(request.message_id, timeout)
        return response.content if response else None

    def broadcast_notification(self, sender_id: str, content: Dict[str, Any]) -> None:
        """Broadcast a notification to all registered agents."""
        notification = Message(
            message_id=f"notif_{datetime.now().timestamp()}",
            sender_id=sender_id,
            receiver_id="broadcast",
            category=MessageCategory.NOTIFICATION,
            content=content
        )
        
        with self.lock:
            for agent_id in self.message_queues:
                if agent_id != sender_id:
                    notification.receiver_id = agent_id
                    self.message_queues[agent_id].put(notification)
        
        logger.info(f"Broadcast notification {notification.message_id} from {sender_id}")

    def process_messages(self, agent_id: str) -> None:
        """Process all pending messages for an agent."""
        with self.lock:
            if agent_id not in self.message_queues:
                return
            
            while not self.message_queues[agent_id].empty():
                message = self.message_queues[agent_id].get()
                self._handle_message(message)

    def _handle_message(self, message: Message) -> None:
        """Handle a message by calling appropriate handlers."""
        if message.receiver_id not in self.message_handlers:
            return
        
        handlers = self.message_handlers[message.category]
        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"Error handling message {message.message_id}: {e}")
                self._send_error_response(message, str(e))

    def _wait_for_response(self, request_id: str, timeout: float) -> Optional[Message]:
        """Wait for a response to a request."""
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < timeout:
            with self.lock:
                for agent_id, queue in self.message_queues.items():
                    for message in queue:
                        if (message.category == MessageCategory.RESPONSE and 
                            message.metadata.get("request_id") == request_id):
                            queue.remove(message)
                            return message
            
            threading.Event().wait(0.1)  # Wait 100ms before checking again
        
        return None

    def _send_error_response(self, original_message: Message, error: str) -> None:
        """Send an error response to a message."""
        error_message = Message(
            message_id=f"err_{datetime.now().timestamp()}",
            sender_id=original_message.receiver_id,
            receiver_id=original_message.sender_id,
            category=MessageCategory.ERROR,
            content={"error": error},
            metadata={"original_message_id": original_message.message_id}
        )
        
        self.send_message(error_message)

    def _send_heartbeats(self) -> None:
        """Send periodic heartbeats to all agents."""
        while True:
            with self.lock:
                for agent_id in self.message_queues:
                    heartbeat = Message(
                        message_id=f"hb_{datetime.now().timestamp()}",
                        sender_id="system",
                        receiver_id=agent_id,
                        category=MessageCategory.HEARTBEAT,
                        content={"timestamp": datetime.now().isoformat()}
                    )
                    self.message_queues[agent_id].put(heartbeat)
            
            threading.Event().wait(self.heartbeat_interval)

    def get_message_count(self, agent_id: str) -> int:
        """Get the number of pending messages for an agent."""
        with self.lock:
            return self.message_queues[agent_id].qsize()

    def clear_messages(self, agent_id: str) -> None:
        """Clear all pending messages for an agent."""
        with self.lock:
            if agent_id in self.message_queues:
                while not self.message_queues[agent_id].empty():
                    self.message_queues[agent_id].get()

    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get the communication status of an agent."""
        with self.lock:
            if agent_id not in self.message_queues:
                return {"status": "not_registered"}
            
            return {
                "status": "active",
                "pending_messages": self.get_message_count(agent_id),
                "registered_handlers": {
                    msg_type: len(handlers)
                    for msg_type, handlers in self.message_handlers.items()
                }
            }

    def _get_relevant_context(self, message: Message) -> Dict[str, Any]:
        """Get relevant context for a message based on conversation history."""
        context = {}
        
        # Get conversation thread context
        if message.reply_to:
            thread_id = self._get_thread_id(message.reply_to)
            thread_messages = self.conversation_threads.get(thread_id, [])
            context["conversation_history"] = [
                {"sender": m.sender_id, "content": m.content}
                for m in thread_messages[-5:]  # Last 5 messages
            ]
        
        # Get agent-specific context
        sender_context = self.agent_contexts.get(message.sender_id, {}).get("context", {})
        receiver_context = self.agent_contexts.get(message.receiver_id, {}).get("context", {})
        
        context.update({
            "sender_context": sender_context,
            "receiver_context": receiver_context
        })
        
        return context

    def _update_agent_contexts(self, message: Message) -> None:
        """Update agent contexts based on message content."""
        # Update sender context
        sender_context = self.agent_contexts[message.sender_id]
        sender_context["last_active"] = datetime.now()
        sender_context["message_count"] += 1
        
        # Update receiver context
        receiver_context = self.agent_contexts[message.receiver_id]
        receiver_context["last_active"] = datetime.now()
        
        # Update active conversations
        thread_id = self._get_thread_id(message)
        sender_context["active_conversations"].add(thread_id)
        receiver_context["active_conversations"].add(thread_id)
    
    def _get_thread_id(self, message: Message) -> str:
        """Get the thread ID for a message."""
        if message.reply_to:
            return message.reply_to
        return message.message_id
    
    def _context_matches(self, message_context: Dict[str, Any],
                        required_context: Dict[str, Any]) -> bool:
        """Check if message context matches required context."""
        for key, value in required_context.items():
            if key not in message_context or message_context[key] != value:
                return False
        return True
    
    async def get_conversation_thread(self, thread_id: str) -> List[Message]:
        """Get the complete conversation thread for a given thread ID."""
        return self.conversation_threads.get(thread_id, [])
    
    async def get_agent_context(self, agent_id: str) -> Dict[str, Any]:
        """Get the current context for an agent."""
        return self.agent_contexts.get(agent_id, {}).get("context", {})
    
    async def update_agent_context(self, agent_id: str, 
                                 context_updates: Dict[str, Any]) -> bool:
        """Update the context for an agent."""
        try:
            if agent_id not in self.agent_contexts:
                return False
            
            self.agent_contexts[agent_id]["context"].update(context_updates)
            return True
        except Exception as e:
            logger.error(f"Failed to update agent context: {str(e)}")
            return False 