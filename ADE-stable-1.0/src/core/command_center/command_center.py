from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from fastapi import WebSocket
import json
import logging
from uuid import uuid4

from ...memory.memory_manager import MemoryManager
from ...database.connection import DatabaseManager

logger = logging.getLogger(__name__)

class CommandCenter:
    def __init__(self):
        self.active_agents: Dict[str, Dict[str, Any]] = {}
        self.agent_connections: Dict[str, WebSocket] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.memory_manager = MemoryManager()
        self.db = DatabaseManager.get_mongodb()
        
    async def register_agent(self, agent_id: str, agent_type: str, capabilities: List[str], websocket: WebSocket):
        """Register a new agent with the command center"""
        self.active_agents[agent_id] = {
            "type": agent_type,
            "capabilities": capabilities,
            "status": "idle",
            "current_task": None,
            "last_active": datetime.utcnow()
        }
        self.agent_connections[agent_id] = websocket
        await self._update_agent_status(agent_id, "registered")
        
    async def unregister_agent(self, agent_id: str):
        """Unregister an agent from the command center"""
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]
        if agent_id in self.agent_connections:
            del self.agent_connections[agent_id]
            
    async def assign_task(self, task: Dict[str, Any]) -> str:
        """Assign a task to an appropriate agent"""
        task_id = str(uuid4())
        task["task_id"] = task_id
        task["status"] = "pending"
        task["created_at"] = datetime.utcnow()
        
        # Store task in database
        await self.db.tasks.insert_one(task)
        
        # Find suitable agent
        suitable_agent = await self._find_suitable_agent(task)
        if suitable_agent:
            await self._assign_task_to_agent(task_id, suitable_agent)
        else:
            await self.task_queue.put(task)
            
        return task_id
        
    async def _find_suitable_agent(self, task: Dict[str, Any]) -> Optional[str]:
        """Find an agent suitable for the given task"""
        required_capabilities = task.get("required_capabilities", [])
        
        for agent_id, agent_info in self.active_agents.items():
            if agent_info["status"] == "idle":
                if all(cap in agent_info["capabilities"] for cap in required_capabilities):
                    return agent_id
        return None
        
    async def _assign_task_to_agent(self, task_id: str, agent_id: str):
        """Assign a task to a specific agent"""
        task = await self.db.tasks.find_one({"task_id": task_id})
        if not task:
            return
            
        self.active_agents[agent_id]["current_task"] = task_id
        self.active_agents[agent_id]["status"] = "busy"
        
        # Send task to agent
        websocket = self.agent_connections[agent_id]
        await websocket.send_json({
            "type": "task_assigned",
            "task": task
        })
        
        # Update task status
        await self.db.tasks.update_one(
            {"task_id": task_id},
            {
                "$set": {
                    "status": "assigned",
                    "assigned_to": agent_id,
                    "assigned_at": datetime.utcnow()
                }
            }
        )
        
    async def _update_agent_status(self, agent_id: str, status: str):
        """Update the status of an agent"""
        if agent_id in self.active_agents:
            self.active_agents[agent_id]["status"] = status
            self.active_agents[agent_id]["last_active"] = datetime.utcnow()
            
    async def handle_agent_message(self, agent_id: str, message: Dict[str, Any]):
        """Handle messages from agents"""
        message_type = message.get("type")
        
        if message_type == "task_completed":
            await self._handle_task_completion(agent_id, message)
        elif message_type == "task_error":
            await self._handle_task_error(agent_id, message)
        elif message_type == "status_update":
            await self._handle_status_update(agent_id, message)
            
    async def _handle_task_completion(self, agent_id: str, message: Dict[str, Any]):
        """Handle task completion from an agent"""
        task_id = message.get("task_id")
        result = message.get("result")
        
        # Update task status
        await self.db.tasks.update_one(
            {"task_id": task_id},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.utcnow(),
                    "result": result
                }
            }
        )
        
        # Update agent status
        await self._update_agent_status(agent_id, "idle")
        self.active_agents[agent_id]["current_task"] = None
        
        # Check for new tasks
        if not self.task_queue.empty():
            next_task = await self.task_queue.get()
            await self._assign_task_to_agent(next_task["task_id"], agent_id)
            
    async def _handle_task_error(self, agent_id: str, message: Dict[str, Any]):
        """Handle task errors from an agent"""
        task_id = message.get("task_id")
        error = message.get("error")
        
        # Update task status
        await self.db.tasks.update_one(
            {"task_id": task_id},
            {
                "$set": {
                    "status": "error",
                    "error": error,
                    "error_at": datetime.utcnow()
                }
            }
        )
        
        # Update agent status
        await self._update_agent_status(agent_id, "idle")
        self.active_agents[agent_id]["current_task"] = None
        
    async def _handle_status_update(self, agent_id: str, message: Dict[str, Any]):
        """Handle status updates from an agent"""
        status = message.get("status")
        await self._update_agent_status(agent_id, status)
        
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of an agent"""
        return self.active_agents.get(agent_id)
        
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a task"""
        return await self.db.tasks.find_one({"task_id": task_id})
        
    async def get_active_agents(self) -> List[Dict[str, Any]]:
        """Get list of all active agents"""
        return [
            {
                "agent_id": agent_id,
                **agent_info
            }
            for agent_id, agent_info in self.active_agents.items()
        ] 