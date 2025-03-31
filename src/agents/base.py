from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
from datetime import datetime

from src.core.providers import ProviderRegistry
from .core.task_processor import AITaskProcessor
from .core.context_manager import ContextManager
from .core.reasoning_engine import ReasoningEngine
from .core.response_interpreter import ResponseInterpreter

logger = logging.getLogger(__name__)

@dataclass
class AgentState:
    """State of an agent"""
    agent_id: str
    role: str
    capabilities: List[str]
    status: str  # 'idle', 'busy', 'error'
    current_task: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = datetime.now()
    last_active: datetime = datetime.now()

class BaseAgent(ABC):
    """Base interface for all specialized agents"""
    
    def __init__(
        self,
        agent_id: str,
        role: str,
        provider_registry: ProviderRegistry,
        capabilities: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities
        self.metadata = metadata or {}
        
        # Initialize core components
        self.provider_registry = provider_registry
        self.context_manager = ContextManager()
        self.task_processor = AITaskProcessor(provider_registry)
        self.reasoning_engine = ReasoningEngine(provider_registry, self.context_manager)
        self.response_interpreter = ResponseInterpreter(provider_registry)
        
        # Initialize state
        self.state = AgentState(
            agent_id=agent_id,
            role=role,
            capabilities=capabilities,
            status="idle",
            metadata=self.metadata
        )
        
        # Initialize session
        self.session_id = self.context_manager.create_session(
            metadata={"agent_id": agent_id, "role": role}
        )
    
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task assigned to the agent
        
        Args:
            task: Task description and parameters
            
        Returns:
            Task result
        """
        pass
    
    @abstractmethod
    async def collaborate(self, other_agent: 'BaseAgent', task: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with another agent on a task
        
        Args:
            other_agent: Agent to collaborate with
            task: Task to collaborate on
            
        Returns:
            Collaboration result
        """
        pass
    
    async def think(self, problem: str) -> Dict[str, Any]:
        """Think about a problem using the reasoning engine
        
        Args:
            problem: Problem to think about
            
        Returns:
            Reasoning result
        """
        try:
            self.state.status = "busy"
            self.state.current_task = "thinking"
            self.state.last_active = datetime.now()
            
            result = await self.reasoning_engine.solve_problem(
                problem=problem,
                session_id=self.session_id
            )
            
            return {
                "success": result.success,
                "steps": [
                    {
                        "id": step.step_id,
                        "description": step.description,
                        "status": step.status,
                        "result": step.result,
                        "error": step.error
                    }
                    for step in result.steps
                ],
                "final_decision": result.final_decision,
                "error": result.error
            }
            
        except Exception as e:
            logger.error(f"Thinking failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            self.state.status = "idle"
            self.state.current_task = None
    
    async def generate_code(
        self,
        requirements: str,
        language: str,
        framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate code using the code generation engine
        
        Args:
            requirements: Code requirements
            language: Target programming language
            framework: Optional framework to use
            
        Returns:
            Generated code and metadata
        """
        try:
            self.state.status = "busy"
            self.state.current_task = "code_generation"
            self.state.last_active = datetime.now()
            
            result = await self.task_processor.process_task(
                task_description=requirements,
                required_capabilities=["code_generation"],
                context={
                    "language": language,
                    "framework": framework,
                    "agent_id": self.agent_id,
                    "role": self.role
                }
            )
            
            if not result.success:
                return {
                    "success": False,
                    "error": result.error
                }
            
            # Interpret the response
            interpreted = await self.response_interpreter.interpret_response(
                response=result.output,
                expected_type="code",
                context={
                    "language": language,
                    "framework": framework
                }
            )
            
            return {
                "success": True,
                "code": interpreted.content,
                "documentation": interpreted.metadata.get("documentation", ""),
                "confidence": interpreted.confidence,
                "metadata": interpreted.metadata
            }
            
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            self.state.status = "idle"
            self.state.current_task = None
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state"""
        return {
            "agent_id": self.state.agent_id,
            "role": self.state.role,
            "capabilities": self.state.capabilities,
            "status": self.state.status,
            "current_task": self.state.current_task,
            "metadata": self.state.metadata,
            "created_at": self.state.created_at.isoformat(),
            "last_active": self.state.last_active.isoformat()
        }
    
    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update agent state
        
        Args:
            updates: State updates to apply
        """
        for key, value in updates.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
        self.state.last_active = datetime.now()
    
    def get_session_id(self) -> str:
        """Get the current session ID"""
        return self.session_id
    
    def clear_session(self) -> None:
        """Clear the current session"""
        self.context_manager.clear_session(self.session_id)
        self.session_id = self.context_manager.create_session(
            metadata={"agent_id": self.agent_id, "role": self.role}
        )
