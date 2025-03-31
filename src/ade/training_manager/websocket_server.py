import asyncio
import json
import logging
import websockets
from typing import Dict, Set, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class TrainingSession:
    """Represents an active training session."""
    session_id: str
    model_name: str
    start_time: datetime
    status: str
    metrics: Dict[str, float]
    hyperparameters: Dict[str, any]
    gpu_utilization: Dict[str, float]
    connected_clients: Set[websockets.WebSocketServerProtocol]

class TrainingWebSocketServer:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.active_sessions: Dict[str, TrainingSession] = {}
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        handler = logging.FileHandler(log_dir / "websocket_server.log")
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    async def register(self, websocket: websockets.WebSocketServerProtocol):
        """Register a new client connection."""
        self.clients.add(websocket)
        logger.info(f"New client connected. Total clients: {len(self.clients)}")

    async def unregister(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister a client connection."""
        self.clients.remove(websocket)
        # Remove client from all training sessions
        for session in self.active_sessions.values():
            session.connected_clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "auth":
                await self._handle_auth(websocket, data)
            elif message_type == "training_update":
                await self._handle_training_update(data)
            elif message_type == "control_command":
                await self._handle_control_command(data)
            elif message_type == "subscribe":
                await self._handle_subscribe(websocket, data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON message received")
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Invalid JSON format"
            }))
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e)
            }))

    async def _handle_auth(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """Handle authentication requests."""
        token = data.get("token")
        if not token or not self._verify_token(token):
            await websocket.send(json.dumps({
                "type": "auth_error",
                "message": "Invalid authentication token"
            }))
            await websocket.close()
            return
        
        await websocket.send(json.dumps({
            "type": "auth_success",
            "message": "Authentication successful"
        }))

    async def _handle_training_update(self, data: dict):
        """Handle training progress updates."""
        session_id = data.get("session_id")
        if not session_id or session_id not in self.active_sessions:
            logger.error(f"Invalid session ID: {session_id}")
            return

        session = self.active_sessions[session_id]
        session.metrics.update(data.get("metrics", {}))
        session.gpu_utilization.update(data.get("gpu_utilization", {}))
        
        # Broadcast update to all subscribed clients
        await self._broadcast_to_session(session_id, {
            "type": "training_update",
            "session_id": session_id,
            "data": asdict(session)
        })

    async def _handle_control_command(self, data: dict):
        """Handle training control commands."""
        session_id = data.get("session_id")
        command = data.get("command")
        params = data.get("params", {})
        
        if not session_id or session_id not in self.active_sessions:
            logger.error(f"Invalid session ID: {session_id}")
            return

        session = self.active_sessions[session_id]
        
        if command == "stop":
            session.status = "stopping"
            await self._broadcast_to_session(session_id, {
                "type": "control_update",
                "session_id": session_id,
                "command": "stop",
                "status": "stopping"
            })
        elif command == "pause":
            session.status = "paused"
            await self._broadcast_to_session(session_id, {
                "type": "control_update",
                "session_id": session_id,
                "command": "pause",
                "status": "paused"
            })
        elif command == "resume":
            session.status = "training"
            await self._broadcast_to_session(session_id, {
                "type": "control_update",
                "session_id": session_id,
                "command": "resume",
                "status": "training"
            })
        elif command == "update_hyperparameters":
            session.hyperparameters.update(params)
            await self._broadcast_to_session(session_id, {
                "type": "control_update",
                "session_id": session_id,
                "command": "update_hyperparameters",
                "hyperparameters": params
            })

    async def _handle_subscribe(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """Handle client subscription to training sessions."""
        session_id = data.get("session_id")
        if not session_id or session_id not in self.active_sessions:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Invalid session ID: {session_id}"
            }))
            return

        session = self.active_sessions[session_id]
        session.connected_clients.add(websocket)
        
        # Send current session state to new subscriber
        await websocket.send(json.dumps({
            "type": "session_state",
            "session_id": session_id,
            "data": asdict(session)
        }))

    async def _broadcast_to_session(self, session_id: str, message: dict):
        """Broadcast message to all clients subscribed to a session."""
        session = self.active_sessions[session_id]
        if not session.connected_clients:
            return

        message_str = json.dumps(message)
        await asyncio.gather(
            *[client.send(message_str) for client in session.connected_clients]
        )

    def _verify_token(self, token: str) -> bool:
        """Verify authentication token."""
        # TODO: Implement proper token verification
        return True

    async def start(self):
        """Start the WebSocket server."""
        async with websockets.serve(self._handle_connection, self.host, self.port):
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            await asyncio.Future()  # run forever

    async def _handle_connection(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle new WebSocket connections."""
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed")
        finally:
            await self.unregister(websocket)

    def create_training_session(self, session_id: str, model_name: str, hyperparameters: dict) -> TrainingSession:
        """Create a new training session."""
        session = TrainingSession(
            session_id=session_id,
            model_name=model_name,
            start_time=datetime.now(),
            status="initializing",
            metrics={},
            hyperparameters=hyperparameters,
            gpu_utilization={},
            connected_clients=set()
        )
        self.active_sessions[session_id] = session
        logger.info(f"Created new training session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[TrainingSession]:
        """Get a training session by ID."""
        return self.active_sessions.get(session_id)

    def list_sessions(self) -> list:
        """List all active training sessions."""
        return [asdict(session) for session in self.active_sessions.values()] 