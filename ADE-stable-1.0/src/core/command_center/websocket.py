from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Dict, Any
import json
import logging
from uuid import uuid4

from .command_center import CommandCenter

logger = logging.getLogger(__name__)
router = APIRouter()
command_center = CommandCenter()

@router.websocket("/ws/agent/{agent_type}")
async def agent_websocket(websocket: WebSocket, agent_type: str):
    """WebSocket endpoint for agent connections"""
    agent_id = str(uuid4())
    
    try:
        await websocket.accept()
        
        # Wait for agent registration
        registration = await websocket.receive_json()
        if registration.get("type") != "register":
            await websocket.close(code=4000, reason="Invalid registration message")
            return
            
        capabilities = registration.get("capabilities", [])
        await command_center.register_agent(agent_id, agent_type, capabilities, websocket)
        
        # Send registration confirmation
        await websocket.send_json({
            "type": "registered",
            "agent_id": agent_id
        })
        
        # Main message loop
        while True:
            message = await websocket.receive_json()
            await command_center.handle_agent_message(agent_id, message)
            
    except WebSocketDisconnect:
        logger.info(f"Agent {agent_id} disconnected")
        await command_center.unregister_agent(agent_id)
    except Exception as e:
        logger.error(f"Error in agent websocket: {str(e)}")
        await websocket.close(code=1011, reason=str(e))
        
@router.post("/tasks")
async def create_task(task: Dict[str, Any]):
    """Create a new task"""
    task_id = await command_center.assign_task(task)
    return {"task_id": task_id}
    
@router.get("/agents")
async def get_agents():
    """Get list of active agents"""
    return await command_center.get_active_agents()
    
@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a specific task"""
    return await command_center.get_task_status(task_id)
    
@router.get("/agents/{agent_id}")
async def get_agent_status(agent_id: str):
    """Get status of a specific agent"""
    return await command_center.get_agent_status(agent_id) 