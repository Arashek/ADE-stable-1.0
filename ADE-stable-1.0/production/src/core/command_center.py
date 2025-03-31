import logging
import threading
import queue
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentInfo:
    agent_id: str
    name: str
    capabilities: List[str]
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    last_active: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskInfo:
    task_id: str
    name: str
    description: str
    required_capabilities: List[str]
    priority: int = 0
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandCenter:
    def __init__(self, config_path: str = "config/command_center.json"):
        """Initialize the Command Center with configuration."""
        self.agents: Dict[str, AgentInfo] = {}
        self.tasks: Dict[str, TaskInfo] = {}
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.agent_locks: Dict[str, threading.Lock] = {}
        self.task_locks: Dict[str, threading.Lock] = {}
        self.state_lock = threading.Lock()
        self.running = False
        self.config_path = config_path
        self.load_config()
        
        # Initialize monitoring
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_task_duration": 0,
            "active_agents": 0
        }
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_agents, daemon=True)
        self.monitor_thread.start()

    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Apply configuration
                    self.max_retries = config.get('max_retries', 3)
                    self.task_timeout = config.get('task_timeout', 300)
                    self.agent_timeout = config.get('agent_timeout', 60)
            else:
                # Default configuration
                self.max_retries = 3
                self.task_timeout = 300
                self.agent_timeout = 60
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def register_agent(self, agent_id: str, name: str, capabilities: List[str]) -> None:
        """Register a new agent with the command center."""
        with self.state_lock:
            if agent_id in self.agents:
                raise ValueError(f"Agent {agent_id} already registered")
            
            self.agents[agent_id] = AgentInfo(
                agent_id=agent_id,
                name=name,
                capabilities=capabilities,
                status=AgentStatus.IDLE
            )
            self.agent_locks[agent_id] = threading.Lock()
            logger.info(f"Registered agent {agent_id} ({name}) with capabilities: {capabilities}")

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the command center."""
        with self.state_lock:
            if agent_id not in self.agents:
                raise ValueError(f"Agent {agent_id} not found")
            
            # Cancel any running tasks
            self._cancel_agent_tasks(agent_id)
            
            # Remove agent
            del self.agents[agent_id]
            del self.agent_locks[agent_id]
            logger.info(f"Unregistered agent {agent_id}")

    def submit_task(self, name: str, description: str, required_capabilities: List[str], 
                   priority: int = 0, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Submit a new task to the command center."""
        task_id = f"task_{len(self.tasks) + 1}"
        
        task = TaskInfo(
            task_id=task_id,
            name=name,
            description=description,
            required_capabilities=required_capabilities,
            priority=priority,
            metadata=metadata or {}
        )
        
        with self.state_lock:
            self.tasks[task_id] = task
            self.task_locks[task_id] = threading.Lock()
            self.task_queue.put((-priority, task_id))  # Negative priority for max heap
        
        logger.info(f"Submitted task {task_id}: {name}")
        return task_id

    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """Assign a task to an agent."""
        with self.state_lock:
            if task_id not in self.tasks or agent_id not in self.agents:
                return False
            
            task = self.tasks[task_id]
            agent = self.agents[agent_id]
            
            # Check if agent has required capabilities
            if not all(cap in agent.capabilities for cap in task.required_capabilities):
                return False
            
            # Check if agent is available
            if agent.status != AgentStatus.IDLE:
                return False
            
            # Assign task
            task.assigned_agent = agent_id
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            
            agent.status = AgentStatus.BUSY
            agent.current_task = task_id
            agent.last_active = datetime.now()
            
            logger.info(f"Assigned task {task_id} to agent {agent_id}")
            return True

    def complete_task(self, task_id: str, success: bool = True, error: Optional[str] = None) -> None:
        """Mark a task as completed or failed."""
        with self.state_lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            agent_id = task.assigned_agent
            
            if agent_id and agent_id in self.agents:
                agent = self.agents[agent_id]
                agent.status = AgentStatus.IDLE
                agent.current_task = None
                agent.last_active = datetime.now()
            
            task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error = error
            
            # Update metrics
            if success:
                self.metrics["tasks_completed"] += 1
            else:
                self.metrics["tasks_failed"] += 1
            
            logger.info(f"Task {task_id} {'completed' if success else 'failed'}")

    def _cancel_agent_tasks(self, agent_id: str) -> None:
        """Cancel all tasks assigned to an agent."""
        for task_id, task in self.tasks.items():
            if task.assigned_agent == agent_id and task.status == TaskStatus.IN_PROGRESS:
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.now()
                task.error = "Agent unregistered"
                logger.info(f"Cancelled task {task_id} due to agent unregistration")

    def _monitor_agents(self) -> None:
        """Monitor agent health and task timeouts."""
        while self.running:
            with self.state_lock:
                current_time = datetime.now()
                
                # Check agent timeouts
                for agent_id, agent in self.agents.items():
                    if agent.status == AgentStatus.BUSY:
                        time_diff = (current_time - agent.last_active).total_seconds()
                        if time_diff > self.agent_timeout:
                            logger.warning(f"Agent {agent_id} timeout detected")
                            agent.status = AgentStatus.ERROR
                            if agent.current_task:
                                self.complete_task(agent.current_task, False, "Agent timeout")
                
                # Check task timeouts
                for task_id, task in self.tasks.items():
                    if task.status == TaskStatus.IN_PROGRESS:
                        time_diff = (current_time - task.started_at).total_seconds()
                        if time_diff > self.task_timeout:
                            logger.warning(f"Task {task_id} timeout detected")
                            self.complete_task(task_id, False, "Task timeout")
                
                # Update active agents count
                self.metrics["active_agents"] = sum(
                    1 for agent in self.agents.values() 
                    if agent.status != AgentStatus.OFFLINE
                )
            
            time.sleep(1)  # Check every second

    def get_agent_status(self, agent_id: str) -> Optional[AgentInfo]:
        """Get the current status of an agent."""
        return self.agents.get(agent_id)

    def get_task_status(self, task_id: str) -> Optional[TaskInfo]:
        """Get the current status of a task."""
        return self.tasks.get(task_id)

    def get_metrics(self) -> Dict[str, Any]:
        """Get current command center metrics."""
        return self.metrics.copy()

    def start(self) -> None:
        """Start the command center."""
        self.running = True
        logger.info("Command Center started")

    def stop(self) -> None:
        """Stop the command center."""
        self.running = False
        logger.info("Command Center stopped") 