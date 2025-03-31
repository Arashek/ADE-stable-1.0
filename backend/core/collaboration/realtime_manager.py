from typing import Dict, Set, Any, Optional
import asyncio
from fastapi import WebSocket
from datetime import datetime
import json
from ..security.rbac import rbac_manager
from ..monitoring.telemetry import TelemetryManager

class CollaborationSession:
    def __init__(self, session_id: str, resource_id: str):
        self.session_id = session_id
        self.resource_id = resource_id
        self.users: Dict[str, WebSocket] = {}
        self.cursors: Dict[str, Dict[str, int]] = {}  # user_id -> {line, column}
        self.lock = asyncio.Lock()
        self.last_update = datetime.utcnow()

class RealtimeManager:
    def __init__(self, telemetry: TelemetryManager):
        self.sessions: Dict[str, CollaborationSession] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> set of session_ids
        self.telemetry = telemetry

    async def join_session(
        self,
        session_id: str,
        resource_id: str,
        user_id: str,
        websocket: WebSocket
    ):
        """Join a collaboration session"""
        with self.telemetry.create_span(
            "join_session",
            {"session_id": session_id, "user_id": user_id}
        ):
            # Create session if it doesn't exist
            if session_id not in self.sessions:
                self.sessions[session_id] = CollaborationSession(
                    session_id=session_id,
                    resource_id=resource_id
                )

            session = self.sessions[session_id]

            # Add user to session
            async with session.lock:
                session.users[user_id] = websocket
                session.cursors[user_id] = {"line": 0, "column": 0}

            # Track user's sessions
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = set()
            self.user_sessions[user_id].add(session_id)

            # Notify other users
            await self.broadcast_message(
                session_id,
                {
                    "type": "user_joined",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                exclude_user=user_id
            )

    async def leave_session(self, session_id: str, user_id: str):
        """Leave a collaboration session"""
        session = self.sessions.get(session_id)
        if not session:
            return

        async with session.lock:
            session.users.pop(user_id, None)
            session.cursors.pop(user_id, None)

            # Remove session if empty
            if not session.users:
                self.sessions.pop(session_id)

        # Update user's sessions
        if user_id in self.user_sessions:
            self.user_sessions[user_id].discard(session_id)
            if not self.user_sessions[user_id]:
                self.user_sessions.pop(user_id)

        # Notify other users
        await self.broadcast_message(
            session_id,
            {
                "type": "user_left",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )

    async def update_cursor(
        self,
        session_id: str,
        user_id: str,
        line: int,
        column: int
    ):
        """Update user's cursor position"""
        session = self.sessions.get(session_id)
        if not session:
            return

        async with session.lock:
            session.cursors[user_id] = {"line": line, "column": column}
            session.last_update = datetime.utcnow()

        # Broadcast cursor update
        await self.broadcast_message(
            session_id,
            {
                "type": "cursor_update",
                "user_id": user_id,
                "position": {"line": line, "column": column},
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )

    async def send_edit(
        self,
        session_id: str,
        user_id: str,
        edit: Dict[str, Any]
    ):
        """Send an edit to all users in session"""
        session = self.sessions.get(session_id)
        if not session:
            return

        # Check permissions
        if not rbac_manager.check_permission(user_id, "code", "write"):
            return

        async with session.lock:
            session.last_update = datetime.utcnow()

        # Broadcast edit
        await self.broadcast_message(
            session_id,
            {
                "type": "edit",
                "user_id": user_id,
                "edit": edit,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def broadcast_message(
        self,
        session_id: str,
        message: Dict[str, Any],
        exclude_user: Optional[str] = None
    ):
        """Broadcast message to all users in session"""
        session = self.sessions.get(session_id)
        if not session:
            return

        message_json = json.dumps(message)
        async with session.lock:
            for user_id, websocket in session.users.items():
                if user_id != exclude_user:
                    try:
                        await websocket.send_text(message_json)
                    except Exception as e:
                        # Handle disconnected users
                        await self.leave_session(session_id, user_id)
