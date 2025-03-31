from typing import Dict, List, Optional
import asyncio
import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config import AgentConfig
from .types import AgentRequest, AgentResponse
from ...agents.coordinator import AgentCoordinator
from ..utils.telemetry import track_event

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.coordinator = AgentCoordinator()
        self.app = FastAPI(title="ADE Agent Service")
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self._setup_routes()
        
    def _setup_routes(self):
        @self.app.post("/process", response_model=AgentResponse)
        async def process_request(request: AgentRequest):
            try:
                task_id = str(uuid4())
                
                # Create async task
                task = asyncio.create_task(
                    self._process_request(task_id, request)
                )
                self.active_tasks[task_id] = task
                
                return AgentResponse(
                    task_id=task_id,
                    status="processing"
                )
                
            except Exception as e:
                logger.error(f"Request processing failed: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/status/{task_id}")
        async def get_status(task_id: str):
            try:
                if task_id not in self.active_tasks:
                    return {
                        "status": "not_found"
                    }
                    
                task = self.active_tasks[task_id]
                if task.done():
                    try:
                        result = task.result()
                        return {
                            "status": "completed",
                            "result": result
                        }
                    except Exception as e:
                        return {
                            "status": "failed",
                            "error": str(e)
                        }
                else:
                    return {
                        "status": "processing"
                    }
                    
            except Exception as e:
                logger.error(f"Status check failed: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
    async def _process_request(self, task_id: str, request: AgentRequest) -> Dict:
        """
        Process agent request
        """
        try:
            # Track request
            track_event("agent_request_started", {
                "task_id": task_id,
                "request_type": request.request_type
            })
            
            # Process based on request type
            if request.request_type == "create_project":
                result = await self.coordinator.process_project(request.project)
            elif request.request_type == "update_project":
                result = await self.coordinator.update_project(
                    request.project_id,
                    request.changes
                )
            elif request.request_type == "analyze_code":
                result = await self.coordinator.analyze_code(request.code)
            else:
                raise ValueError(f"Unknown request type: {request.request_type}")
                
            # Track success
            track_event("agent_request_completed", {
                "task_id": task_id,
                "request_type": request.request_type
            })
            
            return result
            
        except Exception as e:
            # Track failure
            track_event("agent_request_failed", {
                "task_id": task_id,
                "request_type": request.request_type,
                "error": str(e)
            })
            raise
            
        finally:
            # Cleanup
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
                
    async def start(self):
        """
        Start the agent service
        """
        import uvicorn
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            reload=self.config.debug
        )
