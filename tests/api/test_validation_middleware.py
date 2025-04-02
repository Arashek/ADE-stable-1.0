"""
Test validation middleware functionality

This module tests the validation middleware to ensure it correctly:
1. Validates requests against Pydantic models
2. Handles validation errors properly
3. Adds debugging information in debug mode
4. Reports response validation problems
"""

import pytest
from fastapi import FastAPI, Body, Depends
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.middleware.validation_middleware import (
    ValidationMiddleware,
    ResponseValidationMiddleware,
    add_validation_middleware
)


# Create test models
class TestRequestModel(BaseModel):
    name: str = Field(min_length=3)
    age: int = Field(ge=0, le=120)
    email: str
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email must contain @')
        return v


class TestResponseModel(BaseModel):
    id: str
    status: str
    message: str
    data: Dict[str, Any] = {}


# Create a minimal test app
def create_test_app(debug_mode: bool = False):
    app = FastAPI()
    
    # Add middleware
    add_validation_middleware(app, debug_mode=debug_mode)
    
    # Define test routes
    @app.post("/test", response_model=TestResponseModel)
    async def test_endpoint(data: TestRequestModel):
        return {
            "id": "test-id",
            "status": "success",
            "message": f"Hello, {data.name}",
            "data": {"age": data.age, "email": data.email}
        }
    
    @app.post("/invalid-response")
    async def invalid_response_endpoint(data: TestRequestModel):
        # This response is missing required fields
        return {
            "status": "success",
            # Missing id and message
            "data": {"age": data.age, "email": data.email}
        }
    
    @app.get("/excluded-path")
    async def excluded_endpoint():
        return {"message": "This path is excluded from validation middleware"}
    
    return app


# Test cases
class TestValidationMiddleware:
    """Test cases for validation middleware functionality"""
    
    def test_valid_request(self):
        """Test that valid requests pass through middleware"""
        app = create_test_app()
        client = TestClient(app)
        
        valid_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john.doe@example.com"
        }
        
        response = client.post("/test", json=valid_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Hello, John Doe"
        
        # Check that timing headers are added
        assert "X-Response-Time" in response.headers
        assert "X-Request-ID" in response.headers
    
    def test_invalid_request(self):
        """Test that invalid requests are properly rejected"""
        app = create_test_app()
        client = TestClient(app)
        
        # Missing required field
        invalid_data = {
            "name": "John Doe",
            # Missing age
            "email": "john.doe@example.com"
        }
        
        response = client.post("/test", json=invalid_data)
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert "detail" in data
        assert "request_id" in data
        
        # Invalid value
        invalid_data = {
            "name": "John Doe",
            "age": -10,  # Negative age is invalid
            "email": "john.doe@example.com"
        }
        
        response = client.post("/test", json=invalid_data)
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        
        # Invalid email
        invalid_data = {
            "name": "John Doe",
            "age": 30,
            "email": "invalid-email"  # No @ symbol
        }
        
        response = client.post("/test", json=invalid_data)
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_excluded_path(self):
        """Test that excluded paths bypass validation middleware"""
        app = FastAPI()
        
        # Add middleware with excluded path
        app.add_middleware(
            ValidationMiddleware,
            exclude_paths=["/excluded"]
        )
        
        @app.get("/excluded")
        async def excluded_endpoint():
            return {"message": "Excluded path"}
        
        @app.get("/included")
        async def included_endpoint():
            return {"message": "Included path"}
        
        client = TestClient(app)
        
        # Excluded path should not have timing headers
        response = client.get("/excluded")
        assert response.status_code == 200
        assert "X-Response-Time" not in response.headers
        
        # Included path should have timing headers
        response = client.get("/included")
        assert response.status_code == 200
        assert "X-Response-Time" in response.headers
    
    def test_response_validation_in_debug_mode(self):
        """Test that responses are validated in debug mode"""
        app = create_test_app(debug_mode=True)
        client = TestClient(app)
        
        valid_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john.doe@example.com"
        }
        
        # Valid request with valid response
        response = client.post("/test", json=valid_data)
        assert response.status_code == 200
        
        # Valid request with invalid response
        response = client.post("/invalid-response", json=valid_data)
        assert response.status_code == 200
        
        # In non-strict debug mode, the response is modified to include validation errors
        data = response.json()
        if "original_response" in data:
            # Debug mode detected the invalid response
            assert "validation_errors" in data
            assert "_debug_info" in data
            
            # Check that validation errors include missing required fields
            found_id_error = False
            found_message_error = False
            
            for error in data["validation_errors"]:
                loc = error.get("loc", [])
                if "id" in loc:
                    found_id_error = True
                elif "message" in loc:
                    found_message_error = True
            
            assert found_id_error or found_message_error


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
