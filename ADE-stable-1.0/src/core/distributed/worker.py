import asyncio
import aiohttp
import logging
import psutil
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from src.core.script.script_manager import ScriptManager
from src.core.distributed.executor import NodeInfo, TaskInfo

logger = logging.getLogger(__name__)

class WorkerNode:
    """Worker node for executing distributed tasks"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8001,
        coordinator_host: str = "localhost",
        coordinator_port: int = 8000,
        capabilities: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.host = host
        self.port = port
        self.coordinator_host = coordinator_host
        self.coordinator_port = coordinator_port
        self.logger = logger or logging.getLogger("worker")
        
        # Node information
        self.node_id = str(uuid.uuid4())
        self.capabilities = capabilities or {
            "max_load": 10,
            "memory": psutil.virtual_memory().total,
            "features": ["python"]
        }
        
        # Task management
        self.current_tasks: Dict[str, TaskInfo] = {}
        self.script_manager = ScriptManager()
        
        # HTTP server
        self.app = aiohttp.web.Application()
        self._setup_routes()
        self.runner: Optional[aiohttp.web.AppRunner] = None
        
        # Background tasks
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.task_processor: Optional[asyncio.Task] = None
    
    def _setup_routes(self):
        """Set up HTTP routes"""
        self.app.router.add_post("/tasks/assign", self._handle_task_assignment)
        self.app.router.add_post("/tasks/stop", self._handle_task_stop)
    
    async def start(self):
        """Start the worker node"""
        try:
            # Start HTTP server
            self.runner = aiohttp.web.AppRunner(self.app)
            await self.runner.setup()
            site = aiohttp.web.TCPSite(self.runner, self.host, self.port)
            await site.start()
            
            # Start background tasks
            self.heartbeat_task = asyncio.create_task(self._send_heartbeat())
            self.task_processor = asyncio.create_task(self._process_tasks())
            
            # Register with coordinator
            await self._register_with_coordinator()
            
            self.logger.info(f"Worker node started on {self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start worker node: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the worker node"""
        try:
            # Stop background tasks
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
            if self.task_processor:
                self.task_processor.cancel()
            
            # Stop HTTP server
            if self.runner:
                await self.runner.cleanup()
            
            # Deregister from coordinator
            await self._deregister_from_coordinator()
            
            self.logger.info("Worker node stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop worker node: {str(e)}")
            raise
    
    async def _register_with_coordinator(self):
        """Register with the coordinator"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{self.coordinator_host}:{self.coordinator_port}/nodes/register",
                    json={
                        "node_id": self.node_id,
                        "host": self.host,
                        "port": self.port,
                        "capabilities": self.capabilities
                    }
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Failed to register with coordinator: {await response.text()}")
                    
        except Exception as e:
            self.logger.error(f"Registration failed: {str(e)}")
            raise
    
    async def _deregister_from_coordinator(self):
        """Deregister from the coordinator"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{self.coordinator_host}:{self.coordinator_port}/nodes/deregister",
                    json={"node_id": self.node_id}
                ) as response:
                    if response.status != 200:
                        self.logger.warning(f"Failed to deregister from coordinator: {await response.text()}")
                    
        except Exception as e:
            self.logger.error(f"Deregistration failed: {str(e)}")
    
    async def _send_heartbeat(self):
        """Send heartbeat to coordinator"""
        while True:
            try:
                # Get current metrics
                load = psutil.getloadavg()[0]
                memory = psutil.virtual_memory()
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"http://{self.coordinator_host}:{self.coordinator_port}/nodes/heartbeat",
                        json={
                            "node_id": self.node_id,
                            "load": load,
                            "available_memory": memory.available,
                            "status": "running"
                        }
                    ) as response:
                        if response.status != 200:
                            self.logger.warning(f"Heartbeat failed: {await response.text()}")
                
                await asyncio.sleep(5)  # Send heartbeat every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Heartbeat error: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_tasks(self):
        """Process assigned tasks"""
        while True:
            try:
                # Process each task
                for task_id, task in list(self.current_tasks.items()):
                    if task.status == "pending":
                        await self._execute_task(task)
                    elif task.status == "running":
                        await self._check_task_status(task)
                
                await asyncio.sleep(0.1)  # Check tasks every 0.1 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Task processing error: {str(e)}")
    
    async def _execute_task(self, task: TaskInfo):
        """Execute a task"""
        try:
            # Update task status
            task.status = "running"
            task.started_at = datetime.now()
            
            # Execute script
            result = await self.script_manager.execute_script(
                task.script_id,
                requirements=task.requirements
            )
            
            # Update task with result
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = result
            
            # Notify coordinator
            await self._update_task_status(task)
            
        except Exception as e:
            # Handle task failure
            task.status = "failed"
            task.completed_at = datetime.now()
            task.error = str(e)
            
            # Notify coordinator
            await self._update_task_status(task)
            
            self.logger.error(f"Task execution failed: {str(e)}")
    
    async def _check_task_status(self, task: TaskInfo):
        """Check status of a running task"""
        try:
            # Check if script is still running
            if not await self.script_manager.is_script_running(task.script_id):
                # Get final result
                result = await self.script_manager.get_script_result(task.script_id)
                
                # Update task
                task.status = "completed"
                task.completed_at = datetime.now()
                task.result = result
                
                # Notify coordinator
                await self._update_task_status(task)
                
        except Exception as e:
            self.logger.error(f"Task status check failed: {str(e)}")
    
    async def _update_task_status(self, task: TaskInfo):
        """Update task status with coordinator"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{self.coordinator_host}:{self.coordinator_port}/tasks/update",
                    json={
                        "task_id": task.task_id,
                        "status": task.status,
                        "result": task.result,
                        "error": task.error
                    }
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Failed to update task status: {await response.text()}")
                    
        except Exception as e:
            self.logger.error(f"Task status update failed: {str(e)}")
    
    async def _handle_task_assignment(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Handle task assignment"""
        try:
            data = await request.json()
            task_id = data["task_id"]
            
            # Create task info
            task = TaskInfo(
                task_id=task_id,
                script_id=data["script_id"],
                node_id=self.node_id,
                status="pending",
                priority=data.get("priority", 1),
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                result=None,
                error=None,
                requirements=data.get("requirements", {})
            )
            
            # Add to current tasks
            self.current_tasks[task_id] = task
            
            return aiohttp.web.json_response({"status": "success"})
            
        except Exception as e:
            self.logger.error(f"Task assignment failed: {str(e)}")
            return aiohttp.web.json_response(
                {"error": str(e)},
                status=400
            )
    
    async def _handle_task_stop(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Handle task stop request"""
        try:
            data = await request.json()
            task_id = data["task_id"]
            
            if task_id in self.current_tasks:
                task = self.current_tasks[task_id]
                
                # Stop script execution
                await self.script_manager.stop_script(task.script_id)
                
                # Update task status
                task.status = "stopped"
                task.completed_at = datetime.now()
                
                # Notify coordinator
                await self._update_task_status(task)
                
                # Remove from current tasks
                del self.current_tasks[task_id]
                
                return aiohttp.web.json_response({"status": "success"})
            else:
                return aiohttp.web.json_response(
                    {"error": "Task not found"},
                    status=404
                )
            
        except Exception as e:
            self.logger.error(f"Task stop failed: {str(e)}")
            return aiohttp.web.json_response(
                {"error": str(e)},
                status=400
            ) 