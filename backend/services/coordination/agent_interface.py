"""
Unified Agent Interface for ADE Platform

This module implements a unified interface for agent interactions in the ADE platform.
It provides a consistent way for agents to communicate with each other and with the
coordination system, ensuring standardized data formats and interaction patterns.
"""

import logging
from typing import Dict, List, Any, Optional, Callable, Awaitable
from enum import Enum
import json
import asyncio
import inspect
import sys
import traceback
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import error logging system
try:
    from scripts.basic_error_logging import log_error, ErrorCategory, ErrorSeverity
    error_logging_available = True
except ImportError:
    error_logging_available = False
    # Define fallback error categories and severities
    class ErrorCategory:
        AGENT = "AGENT"
        COMMUNICATION = "COMMUNICATION"
        PROCESSING = "PROCESSING"
        SYSTEM = "SYSTEM"
        API = "API"
        VALIDATION = "VALIDATION"
    
    class ErrorSeverity:
        CRITICAL = "CRITICAL"
        ERROR = "ERROR"
        WARNING = "WARNING"
        INFO = "INFO"

# Configure logging
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Enumeration of message types for agent communication"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    QUERY = "query"
    FEEDBACK = "feedback"
    CONSENSUS_VOTE = "consensus_vote"
    CONFLICT_RESOLUTION = "conflict_resolution"
    STATUS_UPDATE = "status_update"

class AgentCapability(Enum):
    """Enumeration of agent capabilities"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DESIGN_CREATION = "design_creation"
    DESIGN_REVIEW = "design_review"
    ARCHITECTURE_ANALYSIS = "architecture_analysis"
    SECURITY_ANALYSIS = "security_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    VALIDATION = "validation"
    REQUIREMENTS_ANALYSIS = "requirements_analysis"

class AgentInterface:
    """
    Unified interface for agent interactions.
    
    This class provides a standardized interface for agents to interact with each other
    and with the coordination system. It handles message formatting, routing, and
    processing, ensuring consistent communication patterns across the platform.
    """
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str]):
        """
        Initialize the agent interface.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent (e.g., validation, design)
            capabilities: List of agent capabilities
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        
        # Initialize message handlers
        self.message_handlers = {
            MessageType.REQUEST.value: self._handle_request,
            MessageType.RESPONSE.value: self._handle_response,
            MessageType.NOTIFICATION.value: self._handle_notification,
            MessageType.QUERY.value: self._handle_query,
            MessageType.FEEDBACK.value: self._handle_feedback,
            MessageType.CONSENSUS_VOTE.value: self._handle_consensus_vote,
            MessageType.CONFLICT_RESOLUTION.value: self._handle_conflict_resolution,
            MessageType.STATUS_UPDATE.value: self._handle_status_update
        }
        
        # Initialize custom message handlers
        self.custom_message_handlers = {}
        
        # Initialize message queue
        self.message_queue = asyncio.Queue()
        
        # Initialize message history
        self.message_history = []
        
        # Initialize agent registry
        self.agent_registry = {}
        
        # Initialize error tracking
        self.errors = []
        
        logger.info("Agent interface initialized for %s agent with ID %s", 
                   agent_type, agent_id)
    
    def log_error(self, error: Any, category: str = ErrorCategory.AGENT, 
                 severity: str = ErrorSeverity.ERROR, context: Dict[str, Any] = None):
        """
        Log an error using the error logging system
        
        Args:
            error: The error object or message
            category: Category of the error
            severity: Severity level of the error
            context: Additional context information
        """
        error_message = str(error)
        
        # Log to console
        logger.error("Error [%s][%s]: %s", category, severity, error_message)
        
        # Add agent context
        if context is None:
            context = {}
        
        context.update({
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities
        })
        
        # Log to error logging system if available
        if error_logging_available:
            try:
                error_id = log_error(
                    error=error,
                    category=category,
                    severity=severity,
                    component=f"agent_{self.agent_type}",
                    source=f"backend.services.coordination.agent_interface.{self.agent_id}",
                    context=context
                )
                self.errors.append({
                    "id": error_id,
                    "message": error_message,
                    "category": category,
                    "severity": severity,
                    "context": context
                })
            except Exception as e:
                logger.error("Failed to log error: %s", str(e))
    
    async def send_message(self, target_agent_id: str, message_type: str, 
                         content: Dict[str, Any], metadata: Dict[str, Any] = None) -> str:
        """
        Send a message to another agent.
        
        Args:
            target_agent_id: ID of the target agent
            message_type: Type of message
            content: Message content
            metadata: Additional metadata
            
        Returns:
            Message ID
        """
        try:
            # Create message
            message_id = self._generate_message_id()
            message = {
                "message_id": message_id,
                "sender_id": self.agent_id,
                "sender_type": self.agent_type,
                "target_id": target_agent_id,
                "message_type": message_type,
                "content": content,
                "metadata": metadata or {},
                "timestamp": self._get_timestamp()
            }
            
            # Log message
            logger.info("Sending %s message from %s to %s", 
                       message_type, self.agent_id, target_agent_id)
            
            # Add to history
            self.message_history.append(message)
            
            # Send message to target agent
            if target_agent_id in self.agent_registry:
                target_interface = self.agent_registry[target_agent_id]
                await target_interface.receive_message(message)
            else:
                error_msg = f"Target agent {target_agent_id} not found in registry"
                logger.warning(error_msg)
                self.log_error(
                    error=error_msg,
                    category=ErrorCategory.COMMUNICATION,
                    severity=ErrorSeverity.WARNING,
                    context={
                        "message_type": message_type,
                        "target_id": target_agent_id,
                        "message_id": message_id
                    }
                )
            
            return message_id
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.COMMUNICATION,
                severity=ErrorSeverity.ERROR,
                context={
                    "action": "send_message",
                    "target_id": target_agent_id,
                    "message_type": message_type
                }
            )
            # Return a generated error message ID
            return f"error_{self._get_timestamp()}"
    
    async def broadcast_message(self, message_type: str, content: Dict[str, Any], 
                              metadata: Dict[str, Any] = None,
                              target_types: List[str] = None) -> List[str]:
        """
        Broadcast a message to multiple agents.
        
        Args:
            message_type: Type of message
            content: Message content
            metadata: Additional metadata
            target_types: List of agent types to target (None for all)
            
        Returns:
            List of message IDs
        """
        try:
            message_ids = []
            
            # Filter target agents
            target_agents = []
            for agent_id, interface in self.agent_registry.items():
                if target_types is None or interface.agent_type in target_types:
                    target_agents.append(agent_id)
            
            # Send message to each target agent
            for target_id in target_agents:
                message_id = await self.send_message(
                    target_id, message_type, content, metadata)
                message_ids.append(message_id)
            
            logger.info("Broadcasted %s message to %d agents", 
                       message_type, len(target_agents))
            
            return message_ids
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.COMMUNICATION,
                severity=ErrorSeverity.ERROR,
                context={
                    "action": "broadcast_message",
                    "message_type": message_type,
                    "target_types": target_types
                }
            )
            return []
    
    async def receive_message(self, message: Dict[str, Any]) -> None:
        """
        Receive a message from another agent.
        
        Args:
            message: The received message
        """
        try:
            # Log message
            logger.info("Received %s message from %s", 
                       message["message_type"], message["sender_id"])
            
            # Add to history
            self.message_history.append(message)
            
            # Add to queue for processing
            await self.message_queue.put(message)
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.COMMUNICATION,
                severity=ErrorSeverity.ERROR,
                context={
                    "action": "receive_message",
                    "message": message
                }
            )
    
    async def process_messages(self) -> None:
        """
        Process messages in the queue.
        """
        while True:
            try:
                # Get message from queue
                message = await self.message_queue.get()
                
                # Process message
                await self._process_message(message)
                
                # Mark as done
                self.message_queue.task_done()
            except Exception as e:
                self.log_error(
                    error=e,
                    category=ErrorCategory.PROCESSING,
                    severity=ErrorSeverity.ERROR,
                    context={
                        "action": "process_messages"
                    }
                )
                # Continue processing other messages even if one fails
                self.message_queue.task_done()
    
    async def _process_message(self, message: Dict[str, Any]) -> None:
        """
        Process a received message.
        
        Args:
            message: The message to process
        """
        try:
            message_type = message["message_type"]
            
            # Check if we have a handler for this message type
            if message_type in self.message_handlers:
                # Call the handler
                await self.message_handlers[message_type](message)
            elif message_type in self.custom_message_handlers:
                # Call the custom handler
                await self.custom_message_handlers[message_type](message)
            else:
                # Log unknown message type
                error_msg = f"Unknown message type: {message_type}"
                logger.warning(error_msg)
                self.log_error(
                    error=error_msg,
                    category=ErrorCategory.PROCESSING,
                    severity=ErrorSeverity.WARNING,
                    context={
                        "message": message
                    }
                )
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.ERROR,
                context={
                    "action": "_process_message",
                    "message": message
                }
            )
    
    async def _handle_request(self, message: Dict[str, Any]) -> None:
        """
        Handle a request message.
        
        Args:
            message: The request message
        """
        try:
            # Extract request details
            request_type = message["content"].get("request_type")
            request_data = message["content"].get("request_data", {})
            
            # Process request based on type
            if request_type == "capability_check":
                # Check if agent has requested capability
                capability = request_data.get("capability")
                has_capability = capability in self.capabilities
                
                # Send response
                await self.send_message(
                    message["sender_id"],
                    MessageType.RESPONSE.value,
                    {
                        "response_type": "capability_check",
                        "response_data": {
                            "capability": capability,
                            "has_capability": has_capability
                        },
                        "request_id": message["message_id"]
                    }
                )
            
            elif request_type == "process_task":
                # Process task request
                task_data = request_data.get("task_data", {})
                
                # This would call into the agent's task processing logic
                # For now, just send a placeholder response
                await self.send_message(
                    message["sender_id"],
                    MessageType.RESPONSE.value,
                    {
                        "response_type": "process_task",
                        "response_data": {
                            "task_id": task_data.get("task_id"),
                            "status": "completed",
                            "result": {"message": "Task processed by agent"}
                        },
                        "request_id": message["message_id"]
                    }
                )
            
            else:
                logger.warning("Unknown request type: %s", request_type)
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.ERROR,
                context={
                    "action": "_handle_request",
                    "message": message
                }
            )
    
    async def _handle_response(self, message: Dict[str, Any]) -> None:
        """
        Handle a response message.
        
        Args:
            message: The response message
        """
        try:
            # Extract response details
            response_type = message["content"].get("response_type")
            response_data = message["content"].get("response_data", {})
            request_id = message["content"].get("request_id")
            
            # Log response
            logger.info("Received %s response for request %s", 
                       response_type, request_id)
            
            # Process response based on type
            # This would typically update some internal state or trigger a callback
            # For now, just log the response
            logger.info("Response data: %s", json.dumps(response_data))
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.ERROR,
                context={
                    "action": "_handle_response",
                    "message": message
                }
            )
    
    async def _handle_notification(self, message: Dict[str, Any]) -> None:
        """
        Handle a notification message.
        
        Args:
            message: The notification message
        """
        try:
            # Extract notification details
            notification_type = message["content"].get("notification_type")
            notification_data = message["content"].get("notification_data", {})
            
            # Log notification
            logger.info("Received %s notification from %s", 
                       notification_type, message["sender_id"])
            
            # Process notification based on type
            if notification_type == "task_status_change":
                # Update task status
                task_id = notification_data.get("task_id")
                new_status = notification_data.get("new_status")
                
                logger.info("Task %s status changed to %s", task_id, new_status)
            
            elif notification_type == "agent_status_change":
                # Update agent status
                agent_id = notification_data.get("agent_id")
                new_status = notification_data.get("new_status")
                
                logger.info("Agent %s status changed to %s", agent_id, new_status)
            
            else:
                logger.info("Received notification: %s", json.dumps(notification_data))
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.ERROR,
                context={
                    "action": "_handle_notification",
                    "message": message
                }
            )
    
    async def _handle_query(self, message: Dict[str, Any]) -> None:
        """
        Handle a query message.
        
        Args:
            message: The query message
        """
        try:
            # Extract query details
            query_type = message["content"].get("query_type")
            query_data = message["content"].get("query_data", {})
            
            # Process query based on type
            if query_type == "capability_query":
                # Return agent capabilities
                await self.send_message(
                    message["sender_id"],
                    MessageType.RESPONSE.value,
                    {
                        "response_type": "capability_query",
                        "response_data": {
                            "agent_id": self.agent_id,
                            "agent_type": self.agent_type,
                            "capabilities": self.capabilities
                        },
                        "request_id": message["message_id"]
                    }
                )
            
            elif query_type == "status_query":
                # Return agent status
                await self.send_message(
                    message["sender_id"],
                    MessageType.RESPONSE.value,
                    {
                        "response_type": "status_query",
                        "response_data": {
                            "agent_id": self.agent_id,
                            "status": "active",
                            "current_tasks": []
                        },
                        "request_id": message["message_id"]
                    }
                )
            
            else:
                logger.warning("Unknown query type: %s", query_type)
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.ERROR,
                context={
                    "action": "_handle_query",
                    "message": message
                }
            )
    
    async def _handle_feedback(self, message: Dict[str, Any]) -> None:
        """
        Handle a feedback message.
        
        Args:
            message: The feedback message
        """
        try:
            # Extract feedback details
            feedback_type = message["content"].get("feedback_type")
            feedback_data = message["content"].get("feedback_data", {})
            
            # Log feedback
            logger.info("Received %s feedback from %s", 
                       feedback_type, message["sender_id"])
            
            # Process feedback based on type
            if feedback_type == "task_result_feedback":
                # Process feedback on task result
                task_id = feedback_data.get("task_id")
                rating = feedback_data.get("rating")
                comments = feedback_data.get("comments")
                
                logger.info("Received feedback for task %s: rating=%s, comments=%s", 
                           task_id, rating, comments)
            
            else:
                logger.info("Received feedback: %s", json.dumps(feedback_data))
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.ERROR,
                context={
                    "action": "_handle_feedback",
                    "message": message
                }
            )
    
    async def _handle_consensus_vote(self, message: Dict[str, Any]) -> None:
        """
        Handle a consensus vote message.
        
        Args:
            message: The consensus vote message
        """
        try:
            # Extract vote details
            decision_id = message["content"].get("decision_id")
            vote = message["content"].get("vote")
            confidence = message["content"].get("confidence")
            
            # Log vote
            logger.info("Received consensus vote from %s for decision %s: %s (confidence: %s)", 
                       message["sender_id"], decision_id, vote, confidence)
            
            # This would typically be handled by a consensus mechanism
            # For now, just acknowledge the vote
            await self.send_message(
                message["sender_id"],
                MessageType.NOTIFICATION.value,
                {
                    "notification_type": "vote_acknowledged",
                    "notification_data": {
                        "decision_id": decision_id,
                        "vote_received": True
                    }
                }
            )
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.ERROR,
                context={
                    "action": "_handle_consensus_vote",
                    "message": message
                }
            )
    
    async def _handle_conflict_resolution(self, message: Dict[str, Any]) -> None:
        """
        Handle a conflict resolution message.
        
        Args:
            message: The conflict resolution message
        """
        try:
            # Extract conflict details
            conflict_id = message["content"].get("conflict_id")
            resolution = message["content"].get("resolution")
            
            # Log resolution
            logger.info("Received conflict resolution from %s for conflict %s: %s", 
                       message["sender_id"], conflict_id, resolution)
            
            # This would typically update the agent's understanding of a conflict
            # For now, just acknowledge the resolution
            await self.send_message(
                message["sender_id"],
                MessageType.NOTIFICATION.value,
                {
                    "notification_type": "resolution_acknowledged",
                    "notification_data": {
                        "conflict_id": conflict_id,
                        "acknowledged": True
                    }
                }
            )
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.ERROR,
                context={
                    "action": "_handle_conflict_resolution",
                    "message": message
                }
            )
    
    async def _handle_status_update(self, message: Dict[str, Any]) -> None:
        """
        Handle a status update message.
        
        Args:
            message: The status update message
        """
        try:
            # Extract status details
            status_type = message["content"].get("status_type")
            status_data = message["content"].get("status_data", {})
            
            # Log status update
            logger.info("Received %s status update from %s", 
                       status_type, message["sender_id"])
            
            # Process status update based on type
            if status_type == "agent_status":
                # Update agent status in registry
                agent_id = message["sender_id"]
                status = status_data.get("status")
                
                if agent_id in self.agent_registry:
                    # This would update some status tracking
                    logger.info("Agent %s status updated to %s", agent_id, status)
            
            elif status_type == "task_status":
                # Update task status
                task_id = status_data.get("task_id")
                status = status_data.get("status")
                
                logger.info("Task %s status updated to %s", task_id, status)
            
            else:
                logger.info("Received status update: %s", json.dumps(status_data))
        except Exception as e:
            self.log_error(
                error=e,
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.ERROR,
                context={
                    "action": "_handle_status_update",
                    "message": message
                }
            )
    
    def register_message_handler(self, message_type: str, 
                               handler: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """
        Register a custom message handler.
        
        Args:
            message_type: Type of message to handle
            handler: Async function to handle the message
        """
        # Verify handler is an async function
        if not inspect.iscoroutinefunction(handler):
            raise ValueError("Message handler must be an async function")
        
        self.custom_message_handlers[message_type] = handler
        logger.info("Registered custom handler for message type %s", message_type)
    
    def register_agent(self, agent_id: str, interface) -> None:
        """
        Register another agent's interface.
        
        Args:
            agent_id: ID of the agent to register
            interface: The agent's interface instance
        """
        self.agent_registry[agent_id] = interface
        logger.info("Registered agent %s in registry", agent_id)
    
    def get_message_history(self, limit: int = None, 
                          message_types: List[str] = None,
                          sender_id: str = None,
                          target_id: str = None) -> List[Dict[str, Any]]:
        """
        Get message history with optional filtering.
        
        Args:
            limit: Maximum number of messages to return
            message_types: Filter by message types
            sender_id: Filter by sender ID
            target_id: Filter by target ID
            
        Returns:
            Filtered message history
        """
        # Apply filters
        filtered_history = self.message_history
        
        if message_types:
            filtered_history = [m for m in filtered_history if m["message_type"] in message_types]
        
        if sender_id:
            filtered_history = [m for m in filtered_history if m["sender_id"] == sender_id]
        
        if target_id:
            filtered_history = [m for m in filtered_history if m["target_id"] == target_id]
        
        # Apply limit
        if limit:
            filtered_history = filtered_history[-limit:]
        
        return filtered_history
    
    def _generate_message_id(self) -> str:
        """
        Generate a unique message ID.
        
        Returns:
            Unique message ID
        """
        import uuid
        return f"msg_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.
        
        Returns:
            Current timestamp
        """
        from datetime import datetime
        return datetime.now().isoformat()

class AgentInterfaceFactory:
    """
    Factory for creating agent interfaces.
    
    This class provides methods for creating and configuring agent interfaces
    for different types of agents.
    """
    
    @staticmethod
    def create_interface(agent_id: str, agent_type: str, 
                        capabilities: List[str] = None) -> AgentInterface:
        """
        Create an agent interface.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent
            capabilities: List of agent capabilities
            
        Returns:
            Configured agent interface
        """
        # Set default capabilities based on agent type
        if capabilities is None:
            capabilities = AgentInterfaceFactory._get_default_capabilities(agent_type)
        
        # Create interface
        interface = AgentInterface(agent_id, agent_type, capabilities)
        
        # Configure interface based on agent type
        AgentInterfaceFactory._configure_interface(interface, agent_type)
        
        return interface
    
    @staticmethod
    def _get_default_capabilities(agent_type: str) -> List[str]:
        """
        Get default capabilities for an agent type.
        
        Args:
            agent_type: Type of agent
            
        Returns:
            List of default capabilities
        """
        # Define default capabilities by agent type
        default_capabilities = {
            "validation": [
                AgentCapability.CODE_REVIEW.value,
                AgentCapability.VALIDATION.value
            ],
            "design": [
                AgentCapability.DESIGN_CREATION.value,
                AgentCapability.DESIGN_REVIEW.value
            ],
            "architecture": [
                AgentCapability.ARCHITECTURE_ANALYSIS.value,
                AgentCapability.CODE_REVIEW.value
            ],
            "security": [
                AgentCapability.SECURITY_ANALYSIS.value,
                AgentCapability.CODE_REVIEW.value
            ],
            "performance": [
                AgentCapability.PERFORMANCE_ANALYSIS.value,
                AgentCapability.CODE_REVIEW.value
            ],
            "coordinator": [
                AgentCapability.REQUIREMENTS_ANALYSIS.value
            ]
        }
        
        return default_capabilities.get(agent_type, [])
    
    @staticmethod
    def _configure_interface(interface: AgentInterface, agent_type: str) -> None:
        """
        Configure an interface based on agent type.
        
        Args:
            interface: The interface to configure
            agent_type: Type of agent
        """
        # This would add agent-specific configurations
        # For now, just log the configuration
        logger.info("Configured interface for %s agent", agent_type)

class AgentMessage:
    """
    Helper class for creating standardized agent messages.
    
    This class provides factory methods for creating different types of messages
    with consistent structure and required fields.
    """
    
    @staticmethod
    def create_request(request_type: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a request message content.
        
        Args:
            request_type: Type of request
            request_data: Request data
            
        Returns:
            Request message content
        """
        return {
            "request_type": request_type,
            "request_data": request_data
        }
    
    @staticmethod
    def create_response(response_type: str, response_data: Dict[str, Any], 
                      request_id: str) -> Dict[str, Any]:
        """
        Create a response message content.
        
        Args:
            response_type: Type of response
            response_data: Response data
            request_id: ID of the request being responded to
            
        Returns:
            Response message content
        """
        return {
            "response_type": response_type,
            "response_data": response_data,
            "request_id": request_id
        }
    
    @staticmethod
    def create_notification(notification_type: str, 
                          notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a notification message content.
        
        Args:
            notification_type: Type of notification
            notification_data: Notification data
            
        Returns:
            Notification message content
        """
        return {
            "notification_type": notification_type,
            "notification_data": notification_data
        }
    
    @staticmethod
    def create_query(query_type: str, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a query message content.
        
        Args:
            query_type: Type of query
            query_data: Query data
            
        Returns:
            Query message content
        """
        return {
            "query_type": query_type,
            "query_data": query_data
        }
    
    @staticmethod
    def create_feedback(feedback_type: str, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a feedback message content.
        
        Args:
            feedback_type: Type of feedback
            feedback_data: Feedback data
            
        Returns:
            Feedback message content
        """
        return {
            "feedback_type": feedback_type,
            "feedback_data": feedback_data
        }
    
    @staticmethod
    def create_consensus_vote(decision_id: str, vote: Any, 
                            confidence: float) -> Dict[str, Any]:
        """
        Create a consensus vote message content.
        
        Args:
            decision_id: ID of the decision
            vote: The vote value
            confidence: Confidence in the vote (0-1)
            
        Returns:
            Consensus vote message content
        """
        return {
            "decision_id": decision_id,
            "vote": vote,
            "confidence": confidence
        }
    
    @staticmethod
    def create_conflict_resolution(conflict_id: str, resolution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a conflict resolution message content.
        
        Args:
            conflict_id: ID of the conflict
            resolution: Resolution details
            
        Returns:
            Conflict resolution message content
        """
        return {
            "conflict_id": conflict_id,
            "resolution": resolution
        }
    
    @staticmethod
    def create_status_update(status_type: str, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a status update message content.
        
        Args:
            status_type: Type of status update
            status_data: Status data
            
        Returns:
            Status update message content
        """
        return {
            "status_type": status_type,
            "status_data": status_data
        }
