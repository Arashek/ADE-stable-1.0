import logging
import threading
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
from .agent_communication import AgentCommunicationSystem, Message, MessageType, MessageCategory, MessagePriority
import asyncio
from .chain_of_thought import ChainOfThought
from .memory.memory_manager import MemoryManager, MemoryEntry, MemoryType, MemoryAccess
from .memory.shared_knowledge import SharedKnowledgeRepository, KnowledgeEntry, KnowledgeDomain
from .time_management import TimeManager, Task, TaskPriority, TaskStatus, TaskMetrics
import time
from .reasoning import (
    AdvancedReasoning, ReasoningType, ReasoningOutput,
    Plan, Subgoal, PlanStatus
)
from .collaboration import (
    CollaborativePlanning, Collaboration, AgentRole,
    CollaborationStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentState:
    """Represents the current state of an agent."""
    agent_id: str
    name: str
    capabilities: List[str]
    status: str
    current_task: Optional[str] = None
    last_active: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    success_count: int = 0
    total_tasks: int = 0

@dataclass
class AgentMetrics:
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_task_time: float = 0.0
    message_processing_times: List[float] = field(default_factory=list)
    memory_usage: Dict[MemoryType, int] = field(default_factory=dict)
    last_heartbeat: float = field(default_factory=time.time)
    stall_count: int = 0

class Agent:
    """Base class for all agents in the system."""
    
    def __init__(self, agent_id: str, name: str, capabilities: List[str], 
                 config_path: Optional[str] = None,
                 max_concurrent_tasks: int = 3,
                 heartbeat_interval: float = 60.0):
        """Initialize the agent."""
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.config_path = config_path
        self.state_lock = threading.Lock()
        self.is_active = False
        self.monitoring_thread = None
        self.max_concurrent_tasks = max_concurrent_tasks
        self.heartbeat_interval = heartbeat_interval
        
        # Initialize metrics
        self.metrics = AgentMetrics()
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize state
        self.state = AgentState(
            agent_id=agent_id,
            name=name,
            capabilities=capabilities,
            status="initialized"
        )
        
        # Initialize communication system
        self.comm_system = AgentCommunicationSystem()
        self.comm_system.register_agent(agent_id)
        
        # Initialize memory system
        self.memory_manager = MemoryManager(f"memory_{agent_id}.db")
        
        # Initialize shared knowledge repository
        self.shared_knowledge = SharedKnowledgeRepository()
        
        # Initialize time manager
        self.time_manager = TimeManager()
        
        # Initialize advanced reasoning
        self.reasoning = AdvancedReasoning()
        
        # Initialize collaborative planning
        self.collaboration = CollaborativePlanning()
        
        # Initialize active plans
        self.active_plans: Dict[str, Plan] = {}
        
        # Initialize collaboration tracking
        self.active_collaborations: Dict[str, Collaboration] = {}
        
        # Register message handlers
        self._register_message_handlers()
        
        # Subscribe to relevant message categories
        self._setup_subscriptions()

    def _setup_subscriptions(self) -> None:
        """Set up message subscriptions for monitoring and debugging."""
        self.comm_system.subscribe(MessageCategory.ERROR, self._handle_error_subscription)
        self.comm_system.subscribe(MessageCategory.THINKING, self._handle_thinking_subscription)
        self.comm_system.subscribe(MessageCategory.STATUS, self._handle_status_subscription)

    async def _handle_error_subscription(self, message: Message) -> None:
        """Handle error message subscriptions."""
        if message.receiver_id == self.agent_id:
            logger.error(f"Received error message: {message.content}")
            self.metrics.tasks_failed += 1
            self.metrics.last_heartbeat = time.time()

    async def _handle_thinking_subscription(self, message: Message) -> None:
        """Handle thinking message subscriptions."""
        if message.receiver_id == self.agent_id and message.reasoning:
            logger.info(f"Agent {message.sender_id} reasoning: {message.reasoning.final_decision}")
            # Store reasoning for analysis
            self.metrics.active_threads = {
                "reasoning": message.reasoning,
                "start_time": message.timestamp
            }

    async def _handle_status_subscription(self, message: Message) -> None:
        """Handle status message subscriptions."""
        if message.receiver_id == self.agent_id:
            logger.info(f"Status update from {message.sender_id}: {message.content}")
            self.metrics.last_heartbeat = time.time()

    def _register_message_handlers(self) -> None:
        """Register message handlers for the agent."""
        # Handle task assignments
        self.comm_system.register_handler(
            self.agent_id,
            MessageCategory.QUERY,
            self._handle_task_request
        )
        
        # Handle status updates
        self.comm_system.register_handler(
            self.agent_id,
            MessageCategory.NOTIFICATION,
            self._handle_status_update
        )
        
        # Handle error messages
        self.comm_system.register_handler(
            self.agent_id,
            MessageCategory.ERROR,
            self._handle_error_message
        )
        
        # Add collaboration request handler
        self.comm_system.register_handler(
            self.agent_id,
            MessageCategory.COLLABORATION_REQUEST,
            self._handle_collaboration_request
        )

    async def send_message_async(self, message: Message) -> bool:
        """Send a message asynchronously."""
        message.processing_start = datetime.now()
        success = await self.comm_system.send_message_async(message)
        if success:
            message.processing_end = datetime.now()
            processing_time = (message.processing_end - message.processing_start).total_seconds()
            self.metrics.message_processing_times.append(processing_time)
        return success

    def get_communication_metrics(self) -> Dict[str, Any]:
        """Get communication metrics for this agent."""
        return self.comm_system.get_communication_metrics(self.agent_id)

    def store_memory(self, content: Dict[str, Any], 
                    memory_type: MemoryType,
                    importance: float = 0.5,
                    tags: Optional[List[str]] = None,
                    context: Optional[Dict[str, Any]] = None,
                    access_level: MemoryAccess = MemoryAccess.PRIVATE) -> Optional[str]:
        """Store a new memory entry."""
        try:
            entry = MemoryEntry(
                type=memory_type,
                content=content,
                importance=importance,
                owner_id=self.agent_id,
                tags=tags or [],
                context=context or {},
                access_level=access_level
            )
            
            if self.memory_manager.add_memory(entry):
                self._update_memory_stats()
                return entry.id
            return None
            
        except Exception as e:
            self._handle_error(e, "memory_storage")
            return None

    def retrieve_memories(self, 
                         memory_type: Optional[MemoryType] = None,
                         tags: Optional[List[str]] = None,
                         context: Optional[Dict[str, Any]] = None,
                         limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memories based on criteria."""
        try:
            return self.memory_manager.retrieve_memories(
                memory_type=memory_type,
                tags=tags,
                context=context,
                agent_id=self.agent_id,
                limit=limit
            )
        except Exception as e:
            self._handle_error(e, "memory_retrieval")
            return []

    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory entry."""
        try:
            return self.memory_manager.update_memory(memory_id, updates)
        except Exception as e:
            self._handle_error(e, "memory_update")
            return False

    def _update_memory_stats(self) -> None:
        """Update memory statistics."""
        try:
            with self.state_lock:
                # Get counts for each memory type
                for mem_type in MemoryType:
                    count = len(self.memory_manager.retrieve_memories(
                        memory_type=mem_type,
                        agent_id=self.agent_id,
                        limit=1000  # High limit to get all memories
                    ))
                    self.metrics.memory_usage[mem_type] = count
        except Exception as e:
            self._handle_error(e, "memory_stats_update")

    async def share_knowledge(self, domain: KnowledgeDomain, content: Dict[str, Any], 
                            confidence: float = 0.5, tags: List[str] = None) -> Optional[str]:
        """Share knowledge with other agents."""
        try:
            entry = KnowledgeEntry(
                domain=domain,
                content=content,
                created_by=self.agent_id,
                confidence=confidence,
                tags=tags or []
            )
            
            knowledge_id = self.shared_knowledge.add_knowledge(entry)
            if knowledge_id:
                # Broadcast knowledge update
                await self.send_message_async(
                    Message(
                        category=MessageCategory.NOTIFICATION,
                        priority=MessagePriority.NORMAL,
                        content={
                            "type": "knowledge_update",
                            "knowledge_id": knowledge_id,
                            "domain": domain.value,
                            "tags": tags
                        }
                    )
                )
                return knowledge_id
            return None
            
        except Exception as e:
            logger.error(f"Error sharing knowledge: {e}")
            return None

    async def retrieve_shared_knowledge(self, domain: Optional[KnowledgeDomain] = None,
                                      tags: Optional[List[str]] = None,
                                      confidence_threshold: float = 0.0) -> List[KnowledgeEntry]:
        """Retrieve shared knowledge from the repository."""
        try:
            return self.shared_knowledge.retrieve_knowledge(
                domain=domain,
                tags=tags,
                confidence_threshold=confidence_threshold
            )
        except Exception as e:
            logger.error(f"Error retrieving shared knowledge: {e}")
            return []

    async def update_shared_knowledge(self, knowledge_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing shared knowledge."""
        try:
            success = self.shared_knowledge.update_knowledge(knowledge_id, updates)
            if success:
                # Broadcast knowledge update
                await self.send_message_async(
                    Message(
                        category=MessageCategory.NOTIFICATION,
                        priority=MessagePriority.NORMAL,
                        content={
                            "type": "knowledge_update",
                            "knowledge_id": knowledge_id,
                            "updates": updates
                        }
                    )
                )
            return success
            
        except Exception as e:
            logger.error(f"Error updating shared knowledge: {e}")
            return False

    async def _handle_knowledge_update(self, message: Message) -> None:
        """Handle knowledge update notifications."""
        try:
            content = message.content
            if content["type"] == "knowledge_update":
                knowledge_id = content.get("knowledge_id")
                if knowledge_id:
                    # Retrieve updated knowledge
                    knowledge = self.shared_knowledge.retrieve_knowledge(
                        knowledge_id=knowledge_id,
                        limit=1
                    )
                    if knowledge:
                        # Update local memory if relevant
                        await self._update_local_memory(knowledge[0])
                        
        except Exception as e:
            logger.error(f"Error handling knowledge update: {e}")

    async def _update_local_memory(self, knowledge: KnowledgeEntry) -> None:
        """Update local memory based on shared knowledge."""
        try:
            # Convert shared knowledge to memory entry
            memory_entry = MemoryEntry(
                type=MemoryType.SEMANTIC,
                content=knowledge.content,
                importance=knowledge.confidence,
                access_level=MemoryAccess.SHARED,
                tags=knowledge.tags,
                metadata={
                    "knowledge_id": knowledge.id,
                    "domain": knowledge.domain.value,
                    "version": knowledge.version
                }
            )
            
            # Store in memory manager
            await self.memory_manager.add_memory(memory_entry)
            
        except Exception as e:
            logger.error(f"Error updating local memory: {e}")

    async def _handle_task_request(self, message: Message) -> None:
        """Handle incoming task requests with advanced reasoning."""
        try:
            task = message.content
            logger.info(f"Received task request: {task}")
            
            # Perform reasoning about task handling
            reasoning_output = await self.perform_reasoning(
                query=f"Should I accept task: {task}",
                reasoning_type=ReasoningType.ANALYTICAL,
                context={
                    "task": task,
                    "capabilities": self.capabilities,
                    "current_workload": len(self.active_plans)
                }
            )
            
            if not reasoning_output:
                await self.send_message_async(
                    Message(
                        category=MessageCategory.RESPONSE,
                        priority=MessagePriority.HIGH,
                        content={"error": "Failed to reason about task"},
                        sender_id=self.agent_id,
                        receiver_id=message.sender_id
                    )
                )
                return
            
            # Create plan if task is accepted
            if reasoning_output.conclusion.lower() == "accept":
                plan = await self.create_plan(
                    goal=task.get("description", ""),
                    context={"task": task}
                )
                
                if plan:
                    # Share task knowledge
                    await self.share_knowledge(
                        domain=KnowledgeDomain.TASK,
                        content={
                            "task_id": task.get("task_id"),
                            "plan_id": plan.plan_id,
                            "status": "accepted"
                        },
                        confidence=reasoning_output.confidence,
                        tags=["task", "accepted"]
                    )
            
            # Send response
            await self.send_message_async(
                Message(
                    category=MessageCategory.RESPONSE,
                    priority=MessagePriority.NORMAL,
                    content={
                        "task_id": task.get("task_id"),
                        "decision": reasoning_output.conclusion,
                        "reasoning": reasoning_output.__dict__
                    },
                    sender_id=self.agent_id,
                    receiver_id=message.sender_id
                )
            )
            
        except Exception as e:
            logger.error(f"Error handling task request: {e}")
            await self.send_message_async(
                Message(
                    category=MessageCategory.ERROR,
                    priority=MessagePriority.URGENT,
                    content={"error": str(e)},
                    sender_id=self.agent_id,
                    receiver_id=message.sender_id
                )
            )

    async def complete_task(self, task_id: str, result: Dict[str, Any]) -> None:
        """Complete a task and update shared knowledge."""
        try:
            # Store completion in episodic memory
            memory_entry = MemoryEntry(
                type=MemoryType.EPISODIC,
                content={
                    "task_id": task_id,
                    "result": result,
                    "completion_time": datetime.now().isoformat()
                },
                importance=0.8,
                access_level=MemoryAccess.PRIVATE,
                tags=["task", "completion"]
            )
            await self.memory_manager.add_memory(memory_entry)
            
            # Share task completion knowledge
            await self.share_knowledge(
                domain=KnowledgeDomain.TASK,
                content={
                    "task_id": task_id,
                    "result": result,
                    "completion_time": datetime.now().isoformat(),
                    "status": "completed"
                },
                confidence=0.9,
                tags=["task", "completed"]
            )
            
            # Update metrics
            self.metrics.tasks_completed += 1
            
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            self.metrics.tasks_failed += 1

    def start(self) -> bool:
        """Start the agent."""
        try:
            with self.state_lock:
                if self.is_active:
                    return False
                
                self.is_active = True
                self.state.status = "active"
                self.state.last_active = datetime.now()
                
                # Start monitoring thread
                self.monitoring_thread = threading.Thread(
                    target=self._monitor_health,
                    daemon=True
                )
                self.monitoring_thread.start()
                
                # Broadcast agent status
                self._broadcast_status()
                
                # Start heartbeat monitoring
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                
                return True
                
        except Exception as e:
            self._handle_error(e, "agent_start")
            return False

    def stop(self) -> bool:
        """Stop the agent."""
        try:
            with self.state_lock:
                if not self.is_active:
                    return False
                
                self.is_active = False
                self.state.status = "stopped"
                
                # Stop monitoring thread
                if self.monitoring_thread:
                    self.monitoring_thread.join(timeout=1.0)
                
                # Broadcast agent status
                self._broadcast_status()
                
                # Cancel heartbeat monitoring
                if self._heartbeat_task:
                    self._heartbeat_task.cancel()
                
                return True
                
        except Exception as e:
            self._handle_error(e, "agent_stop")
            return False

    def assign_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Assign a task to the agent."""
        try:
            with self.state_lock:
                if not self.is_active:
                    return False
                
                # Check if agent has required capabilities
                required_capabilities = task_data.get("required_capabilities", [])
                if not all(cap in self.capabilities for cap in required_capabilities):
                    return False
                
                # Update state
                self.state.current_task = task_id
                self.state.total_tasks += 1
                
                # Process task
                self._process_task(task_id, task_data)
                
                return True
                
        except Exception as e:
            self._handle_error(e, task_id)
            return False

    def complete_task(self, task_id: str, success: bool, result: Optional[Dict[str, Any]] = None) -> None:
        """Complete a task and update metrics."""
        try:
            with self.state_lock:
                if self.state.current_task != task_id:
                    return
                
                # Update metrics
                if success:
                    self.metrics.tasks_completed += 1
                    self.metrics.last_heartbeat = time.time()
                    self.state.success_count += 1
                    
                    # Store successful task completion in episodic memory
                    self.store_memory(
                        content={"task_id": task_id, "result": result, "status": "completed"},
                        memory_type=MemoryType.EPISODIC,
                        importance=0.8,
                        tags=["task", "completed", "success"],
                        context={"task_id": task_id}
                    )
                    
                    # If this is a recurring task, store in procedural memory
                    if result and result.get("is_recurring"):
                        self.store_memory(
                            content={"task_id": task_id, "procedure": result.get("procedure")},
                            memory_type=MemoryType.PROCEDURAL,
                            importance=0.7,
                            tags=["procedure", "task"],
                            context={"task_id": task_id}
                        )
                else:
                    self.metrics.tasks_failed += 1
                    self.metrics.last_heartbeat = time.time()
                    self.state.error_count += 1
                    
                    # Store failed task in episodic memory
                    self.store_memory(
                        content={"task_id": task_id, "status": "failed"},
                        memory_type=MemoryType.EPISODIC,
                        importance=0.6,
                        tags=["task", "failed"],
                        context={"task_id": task_id}
                    )
                
                # Update state
                self.state.current_task = None
                self.state.last_active = datetime.now()
                
                # Broadcast task completion
                self._broadcast_task_completion(task_id, success, result)
                
        except Exception as e:
            self._handle_error(e, task_id)

    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the agent."""
        with self.state_lock:
            return {
                "agent_id": self.state.agent_id,
                "name": self.state.name,
                "capabilities": self.state.capabilities,
                "status": self.state.status,
                "current_task": self.state.current_task,
                "last_active": self.state.last_active,
                "metrics": self.metrics,
                "error_count": self.state.error_count,
                "success_count": self.state.success_count,
                "total_tasks": self.state.total_tasks
            }

    def get_metrics(self) -> Dict[str, Any]:
        """Get the current metrics of the agent."""
        with self.state_lock:
            return self.metrics.copy()

    def update_capabilities(self, new_capabilities: List[str]) -> bool:
        """Update the agent's capabilities."""
        try:
            with self.state_lock:
                self.state.capabilities = new_capabilities
                self._broadcast_status()
                return True
        except Exception as e:
            self._handle_error(e, "capability_update")
            return False

    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration from file."""
        if not self.config_path:
            return {}
        
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config from {self.config_path}: {e}")
            return {}

    def _monitor_health(self) -> None:
        """Monitor agent health in a separate thread."""
        while self.is_active:
            try:
                with self.state_lock:
                    self.state.last_active = datetime.now()
                
                # Process pending messages
                self.comm_system.process_messages(self.agent_id)
                
                # Sleep for a short interval
                threading.Event().wait(1.0)
                
            except Exception as e:
                self._handle_error(e, "health_monitoring")

    def _handle_status_update(self, message: Message) -> None:
        """Handle status update notifications."""
        try:
            status_data = message.content
            # Update agent state based on status update
            with self.state_lock:
                if "status" in status_data:
                    self.state.status = status_data["status"]
                if "capabilities" in status_data:
                    self.state.capabilities = status_data["capabilities"]
        except Exception as e:
            self._handle_error(e, "status_update_handling")

    def _handle_error_message(self, message: Message) -> None:
        """Handle error messages."""
        try:
            error_data = message.content
            logger.error(f"Received error message: {error_data}")
            # Handle error message based on content
        except Exception as e:
            logger.error(f"Error handling error message: {e}")

    def _broadcast_status(self) -> None:
        """Broadcast agent status to other agents."""
        try:
            status_data = {
                "agent_id": self.agent_id,
                "status": self.state.status,
                "capabilities": self.state.capabilities,
                "current_task": self.state.current_task,
                "last_active": self.state.last_active.isoformat()
            }
            self.comm_system.broadcast_notification(self.agent_id, status_data)
        except Exception as e:
            self._handle_error(e, "status_broadcast")

    def _broadcast_task_completion(self, task_id: str, success: bool, 
                                 result: Optional[Dict[str, Any]] = None) -> None:
        """Broadcast task completion status."""
        try:
            completion_data = {
                "task_id": task_id,
                "success": success,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            self.comm_system.broadcast_notification(self.agent_id, completion_data)
        except Exception as e:
            self._handle_error(e, "task_completion_broadcast")

    def _process_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """Process an assigned task."""
        # This method should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement _process_task")

    def _handle_error(self, error: Exception, context: str) -> None:
        """Handle errors in the agent."""
        try:
            logger.error(f"Error in {context}: {str(error)}")
            
            with self.state_lock:
                self.metrics.last_heartbeat = time.time()
                self.state.error_count += 1
            
            # Broadcast error
            error_data = {
                "error": str(error),
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            self.comm_system.broadcast_notification(self.agent_id, error_data)
            
        except Exception as e:
            logger.error(f"Error in error handler: {str(e)}")

    async def _heartbeat_loop(self) -> None:
        """Maintain agent heartbeat and check for stalls."""
        while self.is_active:
            try:
                # Update heartbeat
                await self.time_manager.update_heartbeat(self.agent_id)
                
                # Check for stalled tasks
                stalled_tasks = [
                    task_id for task_id, task in self.active_tasks.items()
                    if task.status == TaskStatus.STALLED
                ]
                
                if stalled_tasks:
                    self.metrics.stall_count += 1
                    logger.warning(f"Agent {self.agent_id} has {len(stalled_tasks)} stalled tasks")
                    
                    # Handle stalled tasks
                    for task_id in stalled_tasks:
                        await self._handle_stalled_task(task_id)
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                await asyncio.sleep(self.heartbeat_interval)

    async def _handle_stalled_task(self, task_id: str) -> None:
        """Handle a stalled task with recovery strategies."""
        if task_id not in self.active_tasks:
            return
            
        task = self.active_tasks[task_id]
        
        # Get task metrics
        metrics = await self.time_manager.get_task_metrics(task_id)
        if not metrics:
            return
            
        # Implement recovery strategies based on stall count
        if metrics["stall_count"] <= 3:
            # Retry with different strategy
            task.status = TaskStatus.PENDING
            await self._retry_task(task)
        else:
            # Escalate to error state
            task.status = TaskStatus.FAILED
            await self._cleanup_task(task_id)
            logger.error(f"Task {task_id} failed after {metrics['stall_count']} stalls")

    async def _retry_task(self, task: Task) -> None:
        """Retry a task with a different strategy."""
        # Implement retry logic here
        # This could involve:
        # 1. Using different resources
        # 2. Breaking down the task into smaller steps
        # 3. Using a different execution strategy
        pass

    async def _cleanup_task(self, task_id: str) -> None:
        """Clean up resources and state for a task."""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            await self.time_manager.release_resources(task_id)
            del self.active_tasks[task_id]

    async def _store_task_memory(self, task: Task, result: Dict) -> None:
        """Store task execution memory."""
        # Store in working memory
        working_memory = MemoryEntry(
            type=MemoryType.WORKING,
            content={
                "task_id": task.task_id,
                "result": result,
                "execution_time": time.time() - task.metrics.start_time
            },
            importance=0.8,
            owner_id=self.agent_id,
            tags=["task_execution"]
        )
        await self.memory_manager.add_memory(working_memory)
        
        # Store in episodic memory if successful
        if result.get("success"):
            episodic_memory = MemoryEntry(
                type=MemoryType.EPISODIC,
                content={
                    "task_id": task.task_id,
                    "result": result,
                    "execution_time": time.time() - task.metrics.start_time
                },
                importance=0.6,
                owner_id=self.agent_id,
                tags=["task_completed"]
            )
            await self.memory_manager.add_memory(episodic_memory)
            
            # Share task knowledge
            await self._share_task_knowledge(task, result)

    async def _share_task_knowledge(self, task: Task, result: Dict) -> None:
        """Share task-related knowledge with other agents."""
        knowledge = KnowledgeEntry(
            domain=KnowledgeDomain.TASK,
            content={
                "task_type": task.content.get("type"),
                "success_patterns": result.get("success_patterns", []),
                "failure_patterns": result.get("failure_patterns", []),
                "execution_time": time.time() - task.metrics.start_time
            },
            created_by=self.agent_id,
            confidence=0.8,
            tags=["task_execution"]
        )
        await self.shared_knowledge.add_knowledge(knowledge)

    async def _handle_collaboration_request(self, message: Message) -> None:
        """Handle requests to join collaborations."""
        try:
            request = message.content
            collaboration_id = request.get("collaboration_id")
            plan_id = request.get("plan_id")
            
            if not collaboration_id or not plan_id:
                await self.send_message_async(
                    Message(
                        category=MessageCategory.RESPONSE,
                        priority=MessagePriority.HIGH,
                        content={"error": "Missing required fields"},
                        sender_id=self.agent_id,
                        receiver_id=message.sender_id
                    )
                )
                return
            
            # Perform reasoning about collaboration
            reasoning_output = await self.perform_reasoning(
                query=f"Should I join collaboration {collaboration_id}",
                reasoning_type=ReasoningType.ANALYTICAL,
                context={
                    "request": request,
                    "capabilities": self.capabilities,
                    "current_workload": len(self.active_collaborations)
                }
            )
            
            if not reasoning_output or reasoning_output.conclusion.lower() != "accept":
                await self.send_message_async(
                    Message(
                        category=MessageCategory.RESPONSE,
                        priority=MessagePriority.NORMAL,
                        content={
                            "collaboration_id": collaboration_id,
                            "decision": "reject",
                            "reasoning": reasoning_output.__dict__ if reasoning_output else None
                        },
                        sender_id=self.agent_id,
                        receiver_id=message.sender_id
                    )
                )
                return
            
            # Join collaboration
            collaboration = await self.collaboration.initiate_collaboration(
                plan_id=plan_id,
                agents={self.agent_id: set(self.capabilities)}
            )
            
            if collaboration:
                self.active_collaborations[collaboration_id] = collaboration
                
                # Send acceptance response
                await self.send_message_async(
                    Message(
                        category=MessageCategory.RESPONSE,
                        priority=MessagePriority.NORMAL,
                        content={
                            "collaboration_id": collaboration_id,
                            "decision": "accept",
                            "role": collaboration.agents[self.agent_id].role
                        },
                        sender_id=self.agent_id,
                        receiver_id=message.sender_id
                    )
                )
            else:
                await self.send_message_async(
                    Message(
                        category=MessageCategory.RESPONSE,
                        priority=MessagePriority.HIGH,
                        content={"error": "Failed to join collaboration"},
                        sender_id=self.agent_id,
                        receiver_id=message.sender_id
                    )
                )
            
        except Exception as e:
            logger.error(f"Error handling collaboration request: {e}")
            await self.send_message_async(
                Message(
                    category=MessageCategory.ERROR,
                    priority=MessagePriority.URGENT,
                    content={"error": str(e)},
                    sender_id=self.agent_id,
                    receiver_id=message.sender_id
                )
            )

    async def create_plan(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Optional[Plan]:
        """Create a detailed plan for achieving a goal."""
        try:
            # Create plan using advanced reasoning
            plan = await self.reasoning.create_plan(
                goal=goal,
                agent_id=self.agent_id,
                capabilities=set(self.capabilities),
                context=context
            )
            
            # Validate plan
            if await self.reasoning.validate_plan(plan.plan_id):
                self.active_plans[plan.plan_id] = plan
                return plan
            return None
            
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return None

    async def initiate_collaboration(self,
                                   plan_id: str,
                                   agents: Dict[str, Set[str]]) -> Optional[Collaboration]:
        """Initiate a collaborative planning session with other agents."""
        try:
            # Create collaboration
            collaboration = await self.collaboration.initiate_collaboration(
                plan_id=plan_id,
                agents=agents
            )
            
            if collaboration:
                # Get the plan
                plan = self.active_plans.get(plan_id)
                if plan:
                    # Assign roles and subgoals
                    if await self.collaboration.assign_roles(collaboration.collaboration_id, plan):
                        self.active_collaborations[collaboration.collaboration_id] = collaboration
                        return collaboration
            
            return None
            
        except Exception as e:
            logger.error(f"Error initiating collaboration: {e}")
            return None

    async def update_collaboration_progress(self,
                                          collaboration_id: str,
                                          subgoal_id: str,
                                          progress: float) -> bool:
        """Update progress in a collaborative task."""
        try:
            return await self.collaboration.update_progress(
                collaboration_id=collaboration_id,
                agent_id=self.agent_id,
                subgoal_id=subgoal_id,
                progress=progress
            )
        except Exception as e:
            logger.error(f"Error updating collaboration progress: {e}")
            return False

    async def resolve_collaboration_conflict(self,
                                           collaboration_id: str,
                                           conflict_id: str,
                                           resolution: Dict[str, Any]) -> bool:
        """Resolve a conflict in a collaboration."""
        try:
            return await self.collaboration.resolve_conflict(
                collaboration_id=collaboration_id,
                conflict_id=conflict_id,
                resolution=resolution
            )
        except Exception as e:
            logger.error(f"Error resolving collaboration conflict: {e}")
            return False

    async def perform_reasoning(self,
                              query: str,
                              reasoning_type: ReasoningType,
                              context: Optional[Dict[str, Any]] = None) -> Optional[ReasoningOutput]:
        """Perform structured reasoning on a query."""
        try:
            return await self.reasoning.perform_reasoning(
                query=query,
                reasoning_type=reasoning_type,
                context=context
            )
        except Exception as e:
            logger.error(f"Error performing reasoning: {e}")
            return None

    async def adapt_plan(self,
                        plan_id: str,
                        changes: Dict[str, Any]) -> Optional[Plan]:
        """Adapt a plan based on changing requirements or failures."""
        try:
            return await self.reasoning.adapt_plan(plan_id, changes)
        except Exception as e:
            logger.error(f"Error adapting plan: {e}")
            return None

    async def create_recovery_plan(self,
                                 plan_id: str,
                                 failed_subgoal_id: str) -> Optional[List[Subgoal]]:
        """Create a recovery plan for a failed subgoal."""
        try:
            return await self.reasoning.create_recovery_plan(plan_id, failed_subgoal_id)
        except Exception as e:
            logger.error(f"Error creating recovery plan: {e}")
            return None

    async def evaluate_performance(self,
                                 time_period: Optional[datetime] = None) -> Dict[str, Any]:
        """Evaluate agent performance and identify areas for improvement."""
        try:
            return await self.reasoning.evaluate_performance(
                agent_id=self.agent_id,
                time_period=time_period
            )
        except Exception as e:
            logger.error(f"Error evaluating performance: {e}")
            return {}

    async def synchronize_collaboration(self,
                                      collaboration_id: str) -> Dict[str, Any]:
        """Synchronize progress in a collaboration."""
        try:
            return await self.collaboration.synchronize_progress(collaboration_id)
        except Exception as e:
            logger.error(f"Error synchronizing collaboration: {e}")
            return {} 