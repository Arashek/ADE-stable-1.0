from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import logging
import asyncio
from enum import Enum

from ..llm.base import (
    LLMRequest,
    LLMResponse,
    TaskType,
    LLMError
)
from ..llm.manager import LLMManager

logger = logging.getLogger(__name__)

class AgentState(Enum):
    """Possible states of an agent"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    LEARNING = "learning"
    ERROR = "error"

class AgentCapability(Enum):
    """Capabilities that an agent can have"""
    CODE_ANALYSIS = "code_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"
    TOOL_SELECTION = "tool_selection"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    ERROR_HANDLING = "error_handling"
    LEARNING = "learning"
    
    # Workflow capabilities
    GIT_OPERATIONS = "git_operations"
    CODE_REVIEW = "code_review"
    CICD_PIPELINE = "cicd_pipeline"
    PROJECT_MANAGEMENT = "project_management"
    WORKFLOW_COORDINATION = "workflow_coordination"
    STATUS_MONITORING = "status_monitoring"

@dataclass
class AgentContext:
    """Context information for agent decision making"""
    current_task: str
    available_tools: List[str]
    recent_actions: List[Dict[str, Any]]
    error_history: List[Dict[str, Any]]
    resource_usage: Dict[str, Any]
    learning_data: Dict[str, Any]

@dataclass
class AgentMetrics:
    """Metrics for tracking agent performance"""
    success_rate: float
    average_latency: float
    error_rate: float
    learning_rate: float
    resource_efficiency: float
    last_update: datetime

class BaseAgent(ABC):
    """Base class for autonomous agents"""
    
    def __init__(
        self,
        name: str,
        capabilities: List[AgentCapability],
        llm_manager: LLMManager,
        max_retries: int = 3,
        learning_rate: float = 0.1
    ):
        self.name = name
        self.capabilities = capabilities
        self.llm_manager = llm_manager
        self.max_retries = max_retries
        self.learning_rate = learning_rate
        
        self.state = AgentState.IDLE
        self.context = AgentContext(
            current_task="",
            available_tools=[],
            recent_actions=[],
            error_history=[],
            resource_usage={},
            learning_data={}
        )
        self.metrics = AgentMetrics(
            success_rate=1.0,
            average_latency=0.0,
            error_rate=0.0,
            learning_rate=0.0,
            resource_efficiency=1.0,
            last_update=datetime.now()
        )
        
        self._lock = asyncio.Lock()
        
    async def think(self, task: str) -> Dict[str, Any]:
        """Think about how to approach a task"""
        async with self._lock:
            self.state = AgentState.THINKING
            
            try:
                # Prepare context for LLM
                context_prompt = self._prepare_context_prompt(task)
                
                # Get LLM response
                request = LLMRequest(
                    prompt=context_prompt,
                    task_type=TaskType.CODE_ANALYSIS,
                    metadata={"agent": self.name, "task": task}
                )
                
                response = await self.llm_manager.generate(request)
                
                # Parse and validate response
                plan = self._parse_llm_response(response)
                
                # Update context
                self.context.current_task = task
                self.context.recent_actions.append({
                    "type": "think",
                    "task": task,
                    "plan": plan,
                    "timestamp": datetime.now()
                })
                
                return plan
                
            except Exception as e:
                logger.error(f"Error in think phase: {str(e)}")
                self.state = AgentState.ERROR
                raise
                
    async def act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute actions based on plan"""
        async with self._lock:
            self.state = AgentState.ACTING
            
            try:
                results = []
                for action in plan.get("actions", []):
                    # Execute action
                    result = await self._execute_action(action)
                    results.append(result)
                    
                    # Update context
                    self.context.recent_actions.append({
                        "type": "act",
                        "action": action,
                        "result": result,
                        "timestamp": datetime.now()
                    })
                    
                return {"results": results}
                
            except Exception as e:
                logger.error(f"Error in act phase: {str(e)}")
                self.state = AgentState.ERROR
                raise
                
    async def learn(self, experience: Dict[str, Any]) -> None:
        """Learn from experience"""
        async with self._lock:
            self.state = AgentState.LEARNING
            
            try:
                # Update learning data
                self.context.learning_data.update(experience)
                
                # Update metrics
                self._update_metrics(experience)
                
                # Update learning rate
                self.learning_rate = self._calculate_learning_rate()
                
                self.state = AgentState.IDLE
                
            except Exception as e:
                logger.error(f"Error in learn phase: {str(e)}")
                self.state = AgentState.ERROR
                raise
                
    def _prepare_context_prompt(self, task: str) -> str:
        """Prepare context prompt for LLM"""
        return f"""
        Agent: {self.name}
        Capabilities: {[c.value for c in self.capabilities]}
        Current Task: {task}
        Recent Actions: {self.context.recent_actions[-5:]}
        Error History: {self.context.error_history[-3:]}
        Resource Usage: {self.context.resource_usage}
        
        Please analyze this task and provide a plan of action.
        """
        
    def _parse_llm_response(self, response: LLMResponse) -> Dict[str, Any]:
        """Parse and validate LLM response"""
        # TODO: Implement response parsing and validation
        return {}
        
    async def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action"""
        # TODO: Implement action execution
        return {}
        
    def _update_metrics(self, experience: Dict[str, Any]) -> None:
        """Update agent metrics based on experience"""
        # Update success rate
        if experience.get("success", False):
            self.metrics.success_rate = (
                self.metrics.success_rate * (1 - self.learning_rate) +
                self.learning_rate
            )
        else:
            self.metrics.error_rate = (
                self.metrics.error_rate * (1 - self.learning_rate) +
                self.learning_rate
            )
            
        # Update latency
        if "latency" in experience:
            self.metrics.average_latency = (
                self.metrics.average_latency * (1 - self.learning_rate) +
                experience["latency"] * self.learning_rate
            )
            
        # Update resource efficiency
        if "resource_usage" in experience:
            self.metrics.resource_efficiency = (
                self.metrics.resource_efficiency * (1 - self.learning_rate) +
                experience.get("resource_efficiency", 1.0) * self.learning_rate
            )
            
        self.metrics.last_update = datetime.now()
        
    def _calculate_learning_rate(self) -> float:
        """Calculate adaptive learning rate based on performance"""
        base_rate = 0.1
        success_factor = self.metrics.success_rate
        error_factor = 1 - self.metrics.error_rate
        
        return base_rate * success_factor * error_factor
        
    def get_metrics(self) -> AgentMetrics:
        """Get current agent metrics"""
        return self.metrics
        
    def get_context(self) -> AgentContext:
        """Get current agent context"""
        return self.context 