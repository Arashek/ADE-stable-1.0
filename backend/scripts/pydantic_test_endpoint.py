"""
Test endpoint for validating Pydantic V2 compatibility.
This module creates routes that use the model and agent service types
to verify that our Pydantic V2 compatibility fixes are working correctly.
"""

import sys
import os
from fastapi import APIRouter, HTTPException
import json

# Add backend directory to path if not already there
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the updated Pydantic models we fixed
from services.model_service.types import ModelRequest, ModelResponse
from services.agent_service.types import AgentRequest, AgentResponse

# Create a router for the test endpoints
pydantic_test_router = APIRouter(prefix="/pydantic-test", tags=["pydantic-test"])

@pydantic_test_router.get("/model-schema")
async def get_model_schema():
    """Get the JSON schema for the ModelRequest and ModelResponse models."""
    try:
        # Get the JSON schema for the models
        model_request_schema = ModelRequest.model_json_schema()
        model_response_schema = ModelResponse.model_json_schema()
        
        return {
            "model_request_schema": model_request_schema,
            "model_response_schema": model_response_schema,
            "message": "Successfully generated schemas using Pydantic V2 compatibility fixes"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate schema: {str(e)}"
        )

@pydantic_test_router.get("/agent-schema")
async def get_agent_schema():
    """Get the JSON schema for the AgentRequest and AgentResponse models."""
    try:
        # Get the JSON schema for the models
        agent_request_schema = AgentRequest.model_json_schema()
        agent_response_schema = AgentResponse.model_json_schema()
        
        return {
            "agent_request_schema": agent_request_schema,
            "agent_response_schema": agent_response_schema,
            "message": "Successfully generated schemas using Pydantic V2 compatibility fixes"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate schema: {str(e)}"
        )

@pydantic_test_router.post("/validate-model-request")
async def validate_model_request(request: ModelRequest):
    """Validate a ModelRequest object."""
    # If we get here, validation was successful
    return {
        "status": "success",
        "message": "ModelRequest validated successfully",
        "request": request.model_dump()
    }

@pydantic_test_router.post("/validate-agent-request")
async def validate_agent_request(request: AgentRequest):
    """Validate an AgentRequest object."""
    # If we get here, validation was successful
    return {
        "status": "success",
        "message": "AgentRequest validated successfully",
        "request": request.model_dump()
    }
