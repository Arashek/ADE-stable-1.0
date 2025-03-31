from typing import Dict, Any, List, Optional, Set
import logging
import asyncio
import aiohttp
from dataclasses import dataclass
from datetime import datetime, timedelta
from src.core.distributed.executor import NodeInfo, TaskInfo

logger = logging.getLogger(__name__)

@dataclass
class NodeState:
    """State information for a worker node"""
    info: NodeInfo
    tasks: Set[str]
    last_heartbeat: datetime
    health_status: str

class Coordinator:
    """Coordinates distributed script execution across multiple nodes"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        logger: Optional[logging.Logger] = None
    ):
        self.host = host
        self.port = port
        self.logger = logger or logging.getLogger("coordinator")
        
        # Node management
        self.nodes: Dict[str, NodeState] = {}
        self.node_timeout = timedelta(seconds=30)
        
        # Task management
        self.tasks: Dict[str, TaskInfo] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        
        # Scheduling
        self.scheduling_task: Optional[asyncio.Task] = None
        self.health_check_task: Optional[asyncio.Task] = None
        
        # HTTP server
        self.app = aiohttp.web.Application()
        self._setup_routes()
        self.runner: Optional[aiohttp.web.AppRunner] = None
    
    def _setup_routes(self):
        """Set up HTTP routes"""
        # Node management routes
        self.app.router.add_post("/nodes/register", self._handle_node_register)
        self.app.router.add_post("/nodes/deregister", self._handle_node_deregister)
        self.app.router.add_post("/nodes/heartbeat", self._handle_node_heartbeat)
        
        # Task management routes
        self.app.router.add_post("/tasks/submit", self._handle_task_submit)
        self.app.router.add_post("/tasks/update", self._handle_task_update)
        self.app.router.add_get("/tasks/{task_id}", self._handle_task_status)
        
        # Node management routes
        self.app.router.add_get("/nodes", self._handle_list_nodes)
        self.app.router.add_get("/nodes/{node_id}", self._handle_node_status)
    
    async def start(self):
        """Start the coordinator service"""
        try:
            # Start background tasks
            self.scheduling_task = asyncio.create_task(self._schedule_tasks())
            self.health_check_task = asyncio.create_task(self._check_node_health())
            
            # Start HTTP server
            self.runner = aiohttp.web.AppRunner(self.app)
            await self.runner.setup()
            site = aiohttp.web.TCPSite(self.runner, self.host, self.port)
            await site.start()
            
            self.logger.info(f"Coordinator started on {self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start coordinator: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the coordinator service"""
        try:
            # Cancel background tasks
            if self.scheduling_task:
                self.scheduling_task.cancel()
            if self.health_check_task:
                self.health_check_task.cancel()
            
            # Stop HTTP server
            if self.runner:
                await self.runner.cleanup()
            
            self.logger.info("Coordinator stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop coordinator: {str(e)}")
            raise
    
    async def _handle_node_register(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Handle node registration"""
        try:
            data = await request.json()
            node_id = data["node_id"]
            
            # Create node info
            node_info = NodeInfo(
                id=node_id,
                host=data["host"],
                port=data["port"],
                capabilities=data["capabilities"],
                load=0.0,
                available_memory=0.0,
                status="registered",
                last_heartbeat=datetime.now()
            )
            
            # Register node
            self.nodes[node_id] = NodeState(
                info=node_info,
                tasks=set(),
                last_heartbeat=datetime.now(),
                health_status="healthy"
            )
            
            self.logger.info(f"Node registered: {node_id}")
            return aiohttp.web.json_response({"status": "success"})
            
        except Exception as e:
            self.logger.error(f"Node registration failed: {str(e)}")
            return aiohttp.web.json_response(
                {"error": str(e)},
                status=400
            )
    
    async def _handle_node_deregister(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Handle node deregistration"""
        try:
            data = await request.json()
            node_id = data["node_id"]
            
            if node_id in self.nodes:
                # Reassign tasks if needed
                await self._reassign_node_tasks(node_id)
                
                # Remove node
                del self.nodes[node_id]
                self.logger.info(f"Node deregistered: {node_id}")
                
            return aiohttp.web.json_response({"status": "success"})
            
        except Exception as e:
            self.logger.error(f"Node deregistration failed: {str(e)}")
            return aiohttp.web.json_response(
                {"error": str(e)},
                status=400
            )
    
    async def _handle_node_heartbeat(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Handle node heartbeat"""
        try:
            data = await request.json()
            node_id = data["node_id"]
            
            if node_id in self.nodes:
                # Update node state
                node_state = self.nodes[node_id]
                node_state.info.load = data["load"]
                node_state.info.available_memory = data["available_memory"]
                node_state.info.status = data["status"]
                node_state.last_heartbeat = datetime.now()
                
                return aiohttp.web.json_response({"status": "success"})
            else:
                return aiohttp.web.json_response(
                    {"error": "Node not found"},
                    status=404
                )
            
        except Exception as e:
            self.logger.error(f"Heartbeat processing failed: {str(e)}")
            return aiohttp.web.json_response(
                {"error": str(e)},
                status=400
            )
    
    async def _handle_task_submit(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Handle task submission"""
        try:
            data = await request.json()
            task_id = data["task_id"]
            
            # Create task info
            task = TaskInfo(
                task_id=task_id,
                script_id=data["script_id"],
                node_id=None,
                status="pending",
                priority=data["priority"],
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                result=None,
                error=None
            )
            
            # Add to task queue
            await self.task_queue.put((-task.priority, task_id, task))
            self.tasks[task_id] = task
            
            return aiohttp.web.json_response({"status": "success"})
            
        except Exception as e:
            self.logger.error(f"Task submission failed: {str(e)}")
            return aiohttp.web.json_response(
                {"error": str(e)},
                status=400
            )
    
    async def _handle_task_update(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Handle task status update"""
        try:
            data = await request.json()
            task_id = data["task_id"]
            
            if task_id in self.tasks:
                # Update task info
                task = self.tasks[task_id]
                task.status = data["status"]
                task.result = data.get("result")
                task.error = data.get("error")
                
                if task.status in ["completed", "failed"]:
                    task.completed_at = datetime.now()
                
                return aiohttp.web.json_response({"status": "success"})
            else:
                return aiohttp.web.json_response(
                    {"error": "Task not found"},
                    status=404
                )
            
        except Exception as e:
            self.logger.error(f"Task update failed: {str(e)}")
            return aiohttp.web.json_response(
                {"error": str(e)},
                status=400
            )
    
    async def _handle_task_status(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Handle task status request"""
        try:
            task_id = request.match_info["task_id"]
            
            if task_id in self.tasks:
                task = self.tasks[task_id]
                return aiohttp.web.json_response({
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
                })
            else:
                return aiohttp.web.json_response(
                    {"error": "Task not found"},
                    status=404
                )
            
        except Exception as e:
            self.logger.error(f"Task status request failed: {str(e)}")
            return aiohttp.web.json_response(
                {"error": str(e)},
                status=400
            )
    
    async def _handle_list_nodes(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Handle node list request"""
        try:
            nodes = [
                {
                    "id": node_id,
                    "host": state.info.host,
                    "port": state.info.port,
                    "capabilities": state.info.capabilities,
                    "load": state.info.load,
                    "available_memory": state.info.available_memory,
                    "status": state.info.status,
                    "health_status": state.health_status
                }
                for node_id, state in self.nodes.items()
            ]
            
            return aiohttp.web.json_response({"nodes": nodes})
            
        except Exception as e:
            self.logger.error(f"Node list request failed: {str(e)}")
            return aiohttp.web.json_response(
                {"error": str(e)},
                status=400
            )
    
    async def _handle_node_status(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Handle node status request"""
        try:
            node_id = request.match_info["node_id"]
            
            if node_id in self.nodes:
                state = self.nodes[node_id]
                return aiohttp.web.json_response({
                    "id": state.info.id,
                    "host": state.info.host,
                    "port": state.info.port,
                    "capabilities": state.info.capabilities,
                    "load": state.info.load,
                    "available_memory": state.info.available_memory,
                    "status": state.info.status,
                    "health_status": state.health_status,
                    "tasks": list(state.tasks)
                })
            else:
                return aiohttp.web.json_response(
                    {"error": "Node not found"},
                    status=404
                )
            
        except Exception as e:
            self.logger.error(f"Node status request failed: {str(e)}")
            return aiohttp.web.json_response(
                {"error": str(e)},
                status=400
            )
    
    async def _schedule_tasks(self):
        """Schedule tasks to available nodes"""
        while True:
            try:
                # Get next task from queue
                _, task_id, task = await self.task_queue.get()
                
                # Find suitable node
                node_id = await self._find_suitable_node(task)
                if node_id:
                    # Assign task to node
                    task.node_id = node_id
                    self.nodes[node_id].tasks.add(task_id)
                    
                    # Notify node
                    await self._notify_node(node_id, task)
                    
                else:
                    # No suitable node found, requeue task
                    await self.task_queue.put((-task.priority, task_id, task))
                
                await asyncio.sleep(0.1)  # Prevent CPU spinning
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Task scheduling error: {str(e)}")
    
    async def _check_node_health(self):
        """Check health of registered nodes"""
        while True:
            try:
                current_time = datetime.now()
                
                for node_id, state in list(self.nodes.items()):
                    # Check heartbeat timeout
                    if current_time - state.last_heartbeat > self.node_timeout:
                        self.logger.warning(f"Node {node_id} heartbeat timeout")
                        state.health_status = "unhealthy"
                        
                        # Reassign tasks if needed
                        await self._reassign_node_tasks(node_id)
                    
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check error: {str(e)}")
    
    async def _find_suitable_node(self, task: TaskInfo) -> Optional[str]:
        """Find a suitable node for a task"""
        suitable_nodes = []
        
        for node_id, state in self.nodes.items():
            if state.health_status != "healthy":
                continue
                
            # Check if node has required capabilities
            if task.requirements and not all(
                cap in state.info.capabilities
                for cap in task.requirements.get("capabilities", [])
            ):
                continue
            
            # Check resource availability
            if state.info.load >= state.info.capabilities.get("max_load", 10):
                continue
                
            if state.info.available_memory < task.requirements.get("memory", 512):
                continue
            
            suitable_nodes.append((node_id, state))
        
        if not suitable_nodes:
            return None
        
        # Select node with lowest load
        return min(suitable_nodes, key=lambda x: x[1].info.load)[0]
    
    async def _notify_node(self, node_id: str, task: TaskInfo):
        """Notify node about assigned task"""
        try:
            state = self.nodes[node_id]
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{state.info.host}:{state.info.port}/tasks/assign",
                    json={
                        "task_id": task.task_id,
                        "script_id": task.script_id,
                        "requirements": task.requirements
                    }
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Failed to notify node: {await response.text()}")
                        
        except Exception as e:
            self.logger.error(f"Node notification failed: {str(e)}")
            # Requeue task
            await self.task_queue.put((-task.priority, task.task_id, task))
    
    async def _reassign_node_tasks(self, node_id: str):
        """Reassign tasks from a node"""
        try:
            state = self.nodes[node_id]
            
            for task_id in state.tasks:
                task = self.tasks[task_id]
                if task.status not in ["completed", "failed"]:
                    # Reset task state
                    task.node_id = None
                    task.status = "pending"
                    task.started_at = None
                    
                    # Requeue task
                    await self.task_queue.put((-task.priority, task_id, task))
            
            # Clear node tasks
            state.tasks.clear()
            
        except Exception as e:
            self.logger.error(f"Task reassignment failed: {str(e)}") 