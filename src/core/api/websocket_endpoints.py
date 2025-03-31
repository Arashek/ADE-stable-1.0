from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Optional
from ..api.websocket_server import websocket_server
from ..auth import get_current_user
from ..models.user import User

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    current_user: Optional[User] = Depends(get_current_user)
):
    """WebSocket endpoint for real-time updates.
    
    Args:
        websocket: WebSocket connection
        current_user: Current authenticated user
    """
    if not current_user:
        await websocket.close(code=4001, reason="Authentication required")
        return
        
    await websocket_server.handle_connection(websocket)

@router.get("/ws/status")
async def websocket_status(current_user: User = Depends(get_current_user)):
    """Get WebSocket connection status.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict containing connection status
    """
    return {
        "connected": websocket_server.manager.is_watching(current_user.id),
        "subscriptions": list(websocket_server.manager.user_subscriptions.get(current_user.id, [])),
        "last_activity": websocket_server.manager.rate_limits.get(current_user.id, {}).get("last_reset")
    } 