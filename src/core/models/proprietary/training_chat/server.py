import asyncio
import json
import logging
from typing import Dict, Set, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

class TrainingSession:
    def __init__(self, session_id: str, training_id: str):
        self.session_id = session_id
        self.training_id = training_id
        self.websocket: Optional[WebSocket] = None
        self.connected = False
        self.last_activity = datetime.now()
        self.metrics: Dict = {}
        self.status: str = "initializing"
        self.checkpoints: list = []
        self.resources: Dict = {}

class TrainingChatServer:
    def __init__(self):
        self.app = FastAPI()
        self.active_sessions: Dict[str, TrainingSession] = {}
        self.training_connections: Dict[str, Set[str]] = {}  # training_id -> set of session_ids
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self.app.websocket("/ws/{session_id}/{training_id}")
        self.app.websocket("/ws/{session_id}/{training_id}")(self.handle_websocket)
        
        # Add REST endpoints
        self.app.get("/sessions")(self.list_sessions)
        self.app.get("/sessions/{training_id}")(self.get_session)
        self.app.post("/sessions/{training_id}/control")(self.control_training)
        
    async def handle_websocket(self, websocket: WebSocket, session_id: str, training_id: str):
        """Handle WebSocket connections for training sessions"""
        await websocket.accept()
        
        # Create or get session
        if training_id not in self.training_connections:
            self.training_connections[training_id] = set()
            
        session = TrainingSession(session_id, training_id)
        session.websocket = websocket
        session.connected = True
        self.active_sessions[session_id] = session
        self.training_connections[training_id].add(session_id)
        
        try:
            while True:
                data = await websocket.receive_text()
                await self.handle_message(session, data)
        except WebSocketDisconnect:
            await self.handle_disconnect(session)
            
    async def handle_message(self, session: TrainingSession, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "metrics":
                session.metrics = data.get("metrics", {})
                await self.broadcast_to_training(session.training_id, {
                    "type": "metrics_update",
                    "session_id": session.session_id,
                    "metrics": session.metrics
                })
                
            elif message_type == "checkpoint":
                checkpoint = data.get("checkpoint")
                session.checkpoints.append(checkpoint)
                await self.broadcast_to_training(session.training_id, {
                    "type": "checkpoint_created",
                    "session_id": session.session_id,
                    "checkpoint": checkpoint
                })
                
            elif message_type == "status":
                session.status = data.get("status")
                await self.broadcast_to_training(session.training_id, {
                    "type": "status_update",
                    "session_id": session.session_id,
                    "status": session.status
                })
                
            elif message_type == "resources":
                session.resources = data.get("resources", {})
                await self.broadcast_to_training(session.training_id, {
                    "type": "resources_update",
                    "session_id": session.session_id,
                    "resources": session.resources
                })
                
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            await session.websocket.send_json({
                "type": "error",
                "message": str(e)
            })
            
    async def handle_disconnect(self, session: TrainingSession):
        """Handle WebSocket disconnections"""
        session.connected = False
        if session.training_id in self.training_connections:
            self.training_connections[session.training_id].remove(session.session_id)
        if session.session_id in self.active_sessions:
            del self.active_sessions[session.session_id]
            
    async def broadcast_to_training(self, training_id: str, message: dict):
        """Broadcast message to all sessions connected to a training process"""
        if training_id in self.training_connections:
            for session_id in self.training_connections[training_id]:
                if session_id in self.active_sessions:
                    session = self.active_sessions[session_id]
                    if session.connected:
                        await session.websocket.send_json(message)
                        
    async def list_sessions(self):
        """List all active training sessions"""
        return {
            "sessions": [
                {
                    "session_id": session_id,
                    "training_id": session.training_id,
                    "status": session.status,
                    "last_activity": session.last_activity.isoformat()
                }
                for session_id, session in self.active_sessions.items()
            ]
        }
        
    async def get_session(self, training_id: str):
        """Get details for a specific training session"""
        if training_id not in self.training_connections:
            raise HTTPException(status_code=404, detail="Training session not found")
            
        sessions = [
            {
                "session_id": session_id,
                "status": self.active_sessions[session_id].status,
                "metrics": self.active_sessions[session_id].metrics,
                "checkpoints": self.active_sessions[session_id].checkpoints,
                "resources": self.active_sessions[session_id].resources
            }
            for session_id in self.training_connections[training_id]
        ]
        
        return {
            "training_id": training_id,
            "sessions": sessions
        }
        
    async def control_training(self, training_id: str, command: dict):
        """Send control command to training process"""
        if training_id not in self.training_connections:
            raise HTTPException(status_code=404, detail="Training session not found")
            
        # Broadcast control command to all sessions
        await self.broadcast_to_training(training_id, {
            "type": "control",
            "command": command
        })
        
        return {"status": "command sent"}

# Create global server instance
server = TrainingChatServer()
app = server.app 