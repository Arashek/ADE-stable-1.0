#!/usr/bin/env python
"""
Simple API Test for ADE Platform

This script runs a minimal FastAPI server to test core API functionality.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="ADE Platform - API Test")

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class PromptRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None
    
class PromptResponse(BaseModel):
    task_id: str
    status: str
    message: str

# Routes
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "ADE API Test Server is running",
        "version": "1.0.0"
    }

@app.post("/api/prompt", response_model=PromptResponse)
async def process_prompt(request: PromptRequest):
    """Process a prompt request"""
    logger.info(f"Received prompt: {request.prompt[:50]}...")
    
    # Simple mock processing logic
    response = {
        "task_id": "task_123",
        "status": "accepted",
        "message": f"Processing prompt: {request.prompt[:50]}..."
    }
    
    return response

@app.get("/api/prompt/{task_id}")
async def get_prompt_status(task_id: str):
    """Get the status of a prompt processing task"""
    return {
        "task_id": task_id,
        "status": "completed",
        "result": {
            "code": "console.log('Hello from ADE platform');"
        }
    }

def main():
    """Run the API test server"""
    logger.info("Starting simple API test server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
