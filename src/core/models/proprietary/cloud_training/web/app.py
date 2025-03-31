import os
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="ADE Training Monitor")

# Mount static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Serve index.html
@app.get("/")
async def read_root():
    return FileResponse(str(static_dir / "index.html"))

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
            
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages
            try:
                message = json.loads(data)
                if message.get('type') == 'subscribe':
                    # Subscribe to job updates
                    job_name = message.get('job_name')
                    if job_name:
                        # Start monitoring job
                        await manager.send_personal_message(
                            json.dumps({
                                'type': 'status',
                                'job_name': job_name,
                                'status': 'subscribed'
                            }),
                            websocket
                        )
                elif message.get('type') == 'command':
                    # Handle training commands
                    command = message.get('command')
                    job_name = message.get('job_name')
                    if command == 'stop' and job_name:
                        # Stop training job
                        await manager.send_personal_message(
                            json.dumps({
                                'type': 'status',
                                'job_name': job_name,
                                'status': 'stopping'
                            }),
                            websocket
                        )
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({
                        'type': 'error',
                        'message': 'Invalid message format'
                    }),
                    websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# API endpoints
class JobStatus(BaseModel):
    job_name: str
    status: str
    metrics: Optional[Dict] = None
    cost: Optional[Dict] = None
    logs: Optional[List[str]] = None

@app.post("/api/jobs/{job_name}/status")
async def update_job_status(job_name: str, status: JobStatus):
    """Update job status and broadcast to connected clients"""
    try:
        await manager.broadcast(json.dumps({
            'type': 'status',
            'job_name': job_name,
            'status': status.dict()
        }))
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to update job status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs/{job_name}/metrics")
async def update_job_metrics(job_name: str, metrics: Dict):
    """Update job metrics and broadcast to connected clients"""
    try:
        await manager.broadcast(json.dumps({
            'type': 'metrics',
            'job_name': job_name,
            'metrics': metrics
        }))
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to update job metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs/{job_name}/cost")
async def update_job_cost(job_name: str, cost: Dict):
    """Update job cost and broadcast to connected clients"""
    try:
        await manager.broadcast(json.dumps({
            'type': 'cost',
            'job_name': job_name,
            'cost': cost
        }))
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to update job cost: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs/{job_name}/logs")
async def update_job_logs(job_name: str, logs: List[str]):
    """Update job logs and broadcast to connected clients"""
    try:
        await manager.broadcast(json.dumps({
            'type': 'logs',
            'job_name': job_name,
            'logs': logs
        }))
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to update job logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs")
async def list_jobs():
    """List all training jobs"""
    try:
        # Import here to avoid circular imports
        from ..manage_jobs import TrainingJobManager
        job_manager = TrainingJobManager()
        jobs = job_manager.list_jobs()
        return {"jobs": jobs}
    except Exception as e:
        logger.error(f"Failed to list jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_name}")
async def get_job_details(job_name: str):
    """Get detailed information about a training job"""
    try:
        # Import here to avoid circular imports
        from ..manage_jobs import TrainingJobManager
        job_manager = TrainingJobManager()
        details = job_manager.get_job_details(job_name)
        if not details:
            raise HTTPException(status_code=404, detail="Job not found")
        return details
    except Exception as e:
        logger.error(f"Failed to get job details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs/{job_name}/stop")
async def stop_job(job_name: str):
    """Stop a running training job"""
    try:
        # Import here to avoid circular imports
        from ..manage_jobs import TrainingJobManager
        job_manager = TrainingJobManager()
        if job_manager.stop_job(job_name):
            return {"status": "success"}
        raise HTTPException(status_code=500, detail="Failed to stop job")
    except Exception as e:
        logger.error(f"Failed to stop job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/jobs/{job_name}")
async def delete_job(job_name: str):
    """Delete a completed training job"""
    try:
        # Import here to avoid circular imports
        from ..manage_jobs import TrainingJobManager
        job_manager = TrainingJobManager()
        if job_manager.delete_job(job_name):
            return {"status": "success"}
        raise HTTPException(status_code=500, detail="Failed to delete job")
    except Exception as e:
        logger.error(f"Failed to delete job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 