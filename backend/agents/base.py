from typing import Dict, Any, List, Optional
import logging
import asyncio
from datetime import datetime
import uuid
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class AgentContext:
    """Context information for agent execution"""
    def __init__(
        self,
        task_id: str,
        project_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.task_id = task_id
        self.project_id = project_id
        self.user_id = user_id
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            "task_id": self.task_id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentContext':
        """Create context from dictionary"""
        return cls(
            task_id=data["task_id"],
            project_id=data["project_id"],
            user_id=data.get("user_id"),
            metadata=data.get("metadata", {})
        )

class AgentRequest:
    """Request to an agent"""
    def __init__(
        self,
        request_id: str,
        agent_id: str,
        action: str,
        input_data: Dict[str, Any],
        context: AgentContext
    ):
        self.request_id = request_id
        self.agent_id = agent_id
        self.action = action
        self.input_data = input_data
        self.context = context
        self.created_at = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary"""
        return {
            "request_id": self.request_id,
            "agent_id": self.agent_id,
            "action": self.action,
            "input_data": self.input_data,
            "context": self.context.to_dict() if self.context else None,
            "created_at": self.created_at.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentRequest':
        """Create request from dictionary"""
        return cls(
            request_id=data["request_id"],
            agent_id=data["agent_id"],
            action=data["action"],
            input_data=data["input_data"],
            context=AgentContext.from_dict(data["context"]) if data.get("context") else None
        )

class AgentResponse:
    """Response from an agent"""
    def __init__(
        self,
        request_id: str,
        agent_id: str,
        success: bool,
        output_data: Dict[str, Any],
        error: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None
    ):
        self.request_id = request_id
        self.agent_id = agent_id
        self.success = success
        self.output_data = output_data
        self.error = error
        self.metrics = metrics or {}
        self.created_at = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "request_id": self.request_id,
            "agent_id": self.agent_id,
            "success": self.success,
            "output_data": self.output_data,
            "error": self.error,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentResponse':
        """Create response from dictionary"""
        return cls(
            request_id=data["request_id"],
            agent_id=data["agent_id"],
            success=data["success"],
            output_data=data["output_data"],
            error=data.get("error"),
            metrics=data.get("metrics", {})
        )

class BaseAgent(ABC):
    """Base class for all agents in the ADE platform"""
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.config = config or {}
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.metrics = {
            "requests_processed": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time_ms": 0
        }
        
    @abstractmethod
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process a request and generate a response
        
        This is the main method that needs to be implemented by all agent subclasses.
        """
        pass
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming request
        
        This method handles request conversion, logging, metrics tracking, and error handling.
        Agent-specific logic should be implemented in the process() method.
        """
        try:
            # Convert dict to AgentRequest
            if isinstance(request, dict):
                # Generate request_id if not provided
                if "request_id" not in request:
                    request["request_id"] = str(uuid.uuid4())
                
                # Set agent_id if not specified
                if "agent_id" not in request:
                    request["agent_id"] = self.agent_id
                    
                # Create context if not provided
                if "context" not in request:
                    request["context"] = {
                        "task_id": str(uuid.uuid4()),
                        "project_id": "default",
                        "user_id": None,
                        "metadata": {}
                    }
                    
                agent_request = AgentRequest.from_dict(request)
            else:
                agent_request = request
                
            self.logger.info(f"Processing request {agent_request.request_id} for action: {agent_request.action}")
            
            # Track metrics
            start_time = datetime.now()
            self.metrics["requests_processed"] += 1
            
            # Process the request
            response = await self.process(agent_request)
            
            # Update metrics
            end_time = datetime.now()
            processing_time_ms = (end_time - start_time).total_seconds() * 1000
            self._update_metrics(True, processing_time_ms)
            
            self.logger.info(f"Request {agent_request.request_id} processed successfully in {processing_time_ms:.2f}ms")
            
            # Return the response
            return response.to_dict()
            
        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}", exc_info=True)
            
            # Update metrics
            self._update_metrics(False, 0)
            
            # Create error response
            error_response = AgentResponse(
                request_id=request.get("request_id", str(uuid.uuid4())),
                agent_id=self.agent_id,
                success=False,
                output_data={},
                error=str(e)
            )
            
            return error_response.to_dict()
            
    def _update_metrics(self, success: bool, response_time_ms: float):
        """Update agent metrics"""
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
            
        # Update average response time
        current_avg = self.metrics["avg_response_time_ms"]
        total_requests = self.metrics["requests_processed"]
        
        if response_time_ms > 0:
            self.metrics["avg_response_time_ms"] = (
                (current_avg * (total_requests - 1) + response_time_ms) / total_requests
            )
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        return self.metrics.copy()
        
    def reset_metrics(self):
        """Reset agent metrics"""
        self.metrics = {
            "requests_processed": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time_ms": 0
        }
