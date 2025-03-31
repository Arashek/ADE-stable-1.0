from fastapi import APIRouter, WebSocket, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..services.llm_service import llm_service
import json
import asyncio
from fastapi.responses import StreamingResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class GenerateRequest(BaseModel):
    prompt: str
    model: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    top_p: Optional[float] = 0.9
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0

@router.post("/generate")
async def generate_completion(request: GenerateRequest):
    """Generate text completion using the specified model."""
    try:
        result = await llm_service.generate_completion(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            presence_penalty=request.presence_penalty,
            frequency_penalty=request.frequency_penalty
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating completion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming completions."""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            request = json.loads(data)
            
            if request.get("type") == "generate":
                # Start streaming completion
                async for token in llm_service.stream_completion(
                    prompt=request["prompt"],
                    model=request["model"],
                    temperature=request.get("temperature", 0.7),
                    max_tokens=request.get("max_tokens", 1000),
                    top_p=request.get("top_p", 0.9)
                ):
                    # Send token to client
                    await websocket.send_json({
                        "type": "token",
                        "token": token
                    })
                
                # Send completion message
                await websocket.send_json({
                    "type": "complete"
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid request type"
                })
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()

@router.get("/models/{model}")
async def get_model_info(model: str):
    """Get information about the specified model."""
    try:
        info = llm_service.get_model_info(model)
        return info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/models")
async def list_models():
    """List all available models."""
    try:
        models = ["llama2", "mistral"]
        return {
            "models": [
                llm_service.get_model_info(model)
                for model in models
            ]
        }
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 