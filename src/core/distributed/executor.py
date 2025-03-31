from typing import Dict, Any, List, Optional, Tuple
import logging
import asyncio
import json
import aiohttp
from dataclasses import dataclass
from datetime import datetime
from src.core.script.script_manager import ScriptManager, ScriptContext, ExecutionResult
from src.core.monitoring.metrics import MetricsCollector
from src.core.monitoring.analytics import AnalyticsEngine

logger = logging.getLogger(__name__)

@dataclass
class NodeInfo:
    """Information about a worker node"""
    id: str
    host: str
    port: int
    capabilities: List[str]
    load: float
    available_memory: float
    status: str
    last_heartbeat: datetime

@dataclass
class TaskInfo:
    """Information about a distributed task"""
    task_id: str
    script_id: str
    node_id: Optional[str]
    status: str
    priority: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[Dict[str, Any]]
    error: Optional[str]

class DistributedExecutor:
    """Manages distributed script execution across multiple nodes"""
    
    def __init__(
        self,
        coordinator_host: str,
        coordinator_port: int,
        node_id: str,
        capabilities: List[str],
        script_manager: Optional[ScriptManager] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        analytics_engine: Optional[AnalyticsEngine] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.coordinator_host = coordinator_host
        self.coordinator_port = coordinator_port
        self.node_id = node_id
        self.capabilities = capabilities
        self.script_manager = script_manager or ScriptManager()
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.analytics_engine = analytics_engine or AnalyticsEngine()
        self.logger = logger or logging.getLogger("distributed_executor")
        
        # Initialize node info
        self.node_info = NodeInfo(
            id=node_id,
            host="localhost",  # Will be updated by coordinator
            port=0,  # Will be assigned by coordinator
            capabilities=capabilities,
            load=0.0,
            available_memory=0.0,
            status="initializing",
            last_heartbeat=datetime.now()
        )
        
        # Task tracking
        self.active_tasks: Dict[str, TaskInfo] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        
        # Connection management
        self.session: Optional[aiohttp.ClientSession] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.task_processor_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the distributed executor"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession()
            
            # Register with coordinator
            await self._register_with_coordinator()
            
            # Start background tasks
            self.heartbeat_task = asyncio.create_task(self._send_heartbeat())
            self.task_processor_task = asyncio.create_task(self._process_tasks())
            
            self.node_info.status = "running"
            self.logger.info("Distributed executor started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start distributed executor: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the distributed executor"""
        try:
            # Cancel background tasks
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
            if self.task_processor_task:
                self.task_processor_task.cancel()
            
            # Close HTTP session
            if self.session:
                await self.session.close()
            
            # Deregister from coordinator
            await self._deregister_from_coordinator()
            
            self.node_info.status = "stopped"
            self.logger.info("Distributed executor stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to stop distributed executor: {str(e)}")
            raise
    
    async def submit_task(
        self,
        script_id: str,
        priority: int = 0,
        requirements: Optional[Dict[str, Any]] = None
    ) -> str:
        """Submit a task for distributed execution
        
        Args:
            script_id: ID of the script to execute
            priority: Task priority (higher number = higher priority)
            requirements: Resource requirements for the task
            
        Returns:
            Task ID
        """
        try:
            # Create task info
            task_id = f"task_{len(self.active_tasks) + 1}"
            task = TaskInfo(
                task_id=task_id,
                script_id=script_id,
                node_id=None,
                status="pending",
                priority=priority,
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                result=None,
                error=None
            )
            
            # Add to task queue
            await self.task_queue.put((-priority, task_id, task))
            
            # Submit to coordinator
            await self._submit_task_to_coordinator(task, requirements)
            
            return task_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit task: {str(e)}")
            raise
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a task
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task status information
        """
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
            
        task = self.active_tasks[task_id]
        return {
            "task_id": task.task_id,
            "script_id": task.script_id,
            "node_id": task.node_id,
            "status": task.status,
            "priority": task.priority,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "result": task.result,
            "error": task.error
        }
    
    async def _register_with_coordinator(self):
        """Register this node with the coordinator"""
        try:
            async with self.session.post(
                f"http://{self.coordinator_host}:{self.coordinator_port}/nodes/register",
                json={
                    "node_id": self.node_id,
                    "capabilities": self.capabilities,
                    "host": self.node_info.host,
                    "port": self.node_info.port
                }
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to register with coordinator: {await response.text()}")
                    
                data = await response.json()
                self.node_info.host = data["host"]
                self.node_info.port = data["port"]
                
        except Exception as e:
            self.logger.error(f"Failed to register with coordinator: {str(e)}")
            raise
    
    async def _deregister_from_coordinator(self):
        """Deregister this node from the coordinator"""
        try:
            async with self.session.post(
                f"http://{self.coordinator_host}:{self.coordinator_port}/nodes/deregister",
                json={"node_id": self.node_id}
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to deregister from coordinator: {await response.text()}")
                    
        except Exception as e:
            self.logger.error(f"Failed to deregister from coordinator: {str(e)}")
            raise
    
    async def _send_heartbeat(self):
        """Send periodic heartbeat to coordinator"""
        while True:
            try:
                # Update node info
                self.node_info.load = len(self.active_tasks)
                self.node_info.available_memory = self._get_available_memory()
                self.node_info.last_heartbeat = datetime.now()
                
                # Send heartbeat
                async with self.session.post(
                    f"http://{self.coordinator_host}:{self.coordinator_port}/nodes/heartbeat",
                    json={
                        "node_id": self.node_id,
                        "load": self.node_info.load,
                        "available_memory": self.node_info.available_memory,
                        "status": self.node_info.status
                    }
                ) as response:
                    if response.status != 200:
                        self.logger.warning(f"Heartbeat failed: {await response.text()}")
                
                await asyncio.sleep(5)  # Send heartbeat every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Heartbeat error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _process_tasks(self):
        """Process tasks from the queue"""
        while True:
            try:
                # Get next task
                _, task_id, task = await self.task_queue.get()
                
                # Update task status
                task.status = "running"
                task.started_at = datetime.now()
                self.active_tasks[task_id] = task
                
                try:
                    # Execute script
                    result = await self.script_manager.execute_script(task.script_id)
                    
                    # Update task with result
                    task.status = "completed"
                    task.completed_at = datetime.now()
                    task.result = {
                        "success": result.success,
                        "output": result.output,
                        "error": result.error,
                        "execution_time": result.execution_time,
                        "memory_usage": result.memory_usage
                    }
                    
                except Exception as e:
                    # Update task with error
                    task.status = "failed"
                    task.completed_at = datetime.now()
                    task.error = str(e)
                    
                finally:
                    # Notify coordinator
                    await self._update_task_status(task)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Task processing error: {str(e)}")
    
    async def _submit_task_to_coordinator(self, task: TaskInfo, requirements: Optional[Dict[str, Any]]):
        """Submit task to coordinator for scheduling"""
        try:
            async with self.session.post(
                f"http://{self.coordinator_host}:{self.coordinator_port}/tasks/submit",
                json={
                    "task_id": task.task_id,
                    "script_id": task.script_id,
                    "priority": task.priority,
                    "requirements": requirements or {}
                }
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to submit task to coordinator: {await response.text()}")
                    
        except Exception as e:
            self.logger.error(f"Failed to submit task to coordinator: {str(e)}")
            raise
    
    async def _update_task_status(self, task: TaskInfo):
        """Update task status with coordinator"""
        try:
            async with self.session.post(
                f"http://{self.coordinator_host}:{self.coordinator_port}/tasks/update",
                json={
                    "task_id": task.task_id,
                    "status": task.status,
                    "result": task.result,
                    "error": task.error
                }
            ) as response:
                if response.status != 200:
                    self.logger.warning(f"Failed to update task status: {await response.text()}")
                    
        except Exception as e:
            self.logger.error(f"Failed to update task status: {str(e)}")
    
    def _get_available_memory(self) -> float:
        """Get available memory in MB"""
        import psutil
        return psutil.virtual_memory().available / (1024 * 1024) 