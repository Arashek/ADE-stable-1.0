from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
import json
import uuid
from ..core.terminal.websocket_handler import terminal_manager
from ..core.security.rate_limiter import RateLimiter
from fastapi.security import APIKeyHeader

router = APIRouter(prefix="/ws", tags=["websocket"])

# Security
api_key_header = APIKeyHeader(name="X-API-Key")
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

async def verify_ws_connection(
    websocket: WebSocket,
) -> None:
    """Verify WebSocket connection with API key."""
    try:
        # Get API key from headers
        headers = dict(websocket.headers)
        api_key = headers.get("x-api-key")
        
        if not api_key or api_key != "your-secure-api-key":  # Replace with secure key management
            await websocket.close(code=4001, reason="Invalid API key")
            return False
        
        # Check rate limit
        client_ip = websocket.client.host
        if not rate_limiter.is_allowed(client_ip):
            await websocket.close(code=4002, reason="Too many requests")
            return False
            
        return True
    except Exception as e:
        await websocket.close(code=4000, reason=str(e))
        return False

@router.websocket("/terminal/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: Optional[str] = None):
    """
    WebSocket endpoint for terminal sessions.
    
    Args:
        websocket: The WebSocket connection
        session_id: Optional session ID. If not provided, a new one will be generated.
    """
    # Verify connection
    if not await verify_ws_connection(websocket):
        return

    # Accept connection
    await websocket.accept()
    
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    try:
        # Create terminal session
        session = await terminal_manager.create_terminal(websocket, session_id)
        
        # Send session info
        await websocket.send_json({
            "type": "session_created",
            "session_id": session_id
        })
        
        # Start terminal communication tasks
        read_task = asyncio.create_task(handle_terminal_output(session))
        write_task = asyncio.create_task(handle_terminal_input(session))
        
        # Wait for tasks to complete
        await asyncio.gather(read_task, write_task)
        
    except WebSocketDisconnect:
        await terminal_manager.close_terminal(session_id)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "data": f"Terminal error: {str(e)}"
        })
    finally:
        await terminal_manager.close_terminal(session_id)

async def handle_terminal_output(session: 'TerminalSession'):
    """Handle terminal output and send it to the WebSocket."""
    try:
        async for output in terminal_manager.read_terminal_output(session):
            await session.ws.send_json({
                "type": "output",
                "data": output
            })
    except WebSocketDisconnect:
        raise
    except Exception as e:
        await session.ws.send_json({
            "type": "error",
            "data": f"Output error: {str(e)}"
        })

async def handle_terminal_input(session: 'TerminalSession'):
    """Handle input from WebSocket and write it to the terminal."""
    try:
        while True:
            message = await session.ws.receive_json()
            
            if message["type"] == "input":
                await terminal_manager.handle_terminal_input(session, message["data"])
            elif message["type"] == "resize":
                await terminal_manager.resize_terminal(
                    session,
                    rows=message["rows"],
                    cols=message["cols"]
                )
    except WebSocketDisconnect:
        raise
    except Exception as e:
        await session.ws.send_json({
            "type": "error",
            "data": f"Input error: {str(e)}"
        }) 