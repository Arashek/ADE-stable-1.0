"""
Test API validation middleware and Pydantic models

This test module verifies that the API validation middleware correctly validates
requests and responses according to the specified Pydantic models.
"""

import pytest
import json
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.main import app
from backend.models.api_models import (
    CreateConsensusDecisionRequest,
    ConsensusDecisionResponse,
    ErrorCategory,
    ErrorSeverity,
    ConsensusStatus
)

# Create test client
client = TestClient(app)


# Helper functions
def get_auth_header():
    """Get a mock authentication header for testing"""
    return {"Authorization": "Bearer test_token"}


# Test API validation
class TestAPIValidation:
    """Test cases for API validation middleware and Pydantic models"""
    
    def test_valid_consensus_request(self):
        """Test that a valid request passes validation"""
        valid_data = {
            "key": "test_decision",
            "description": "Test consensus decision",
            "options": ["option1", "option2", "option3"],
            "agents": ["agent1", "agent2"],
            "timeout_seconds": 120
        }
        
        # Parse with Pydantic model to ensure it's valid
        model = CreateConsensusDecisionRequest(**valid_data)
        assert model.key == valid_data["key"]
        assert model.description == valid_data["description"]
        assert model.options == valid_data["options"]
        assert model.agents == valid_data["agents"]
        assert model.timeout_seconds == valid_data["timeout_seconds"]
        
        # Test API endpoint with valid data
        response = client.post(
            "/api/coordination/consensus",
            json=valid_data,
            headers=get_auth_header()
        )
        
        # Even though the request is valid, the coordination system might not be active
        # So we just make sure it's not a validation error (422)
        assert response.status_code != 422
    
    def test_invalid_consensus_request_missing_required(self):
        """Test that a request missing required fields fails validation"""
        invalid_data = {
            "key": "test_decision",
            # Missing description
            "options": ["option1", "option2"]
        }
        
        # Test with Pydantic model
        with pytest.raises(Exception):
            CreateConsensusDecisionRequest(**invalid_data)
        
        # Test API endpoint with invalid data
        response = client.post(
            "/api/coordination/consensus",
            json=invalid_data,
            headers=get_auth_header()
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert "detail" in data
        
        # Check that the validation error details contain the missing field
        found_missing_field = False
        for error in data["detail"]:
            if error.get("loc", [""])[0] == "description":
                found_missing_field = True
                break
        
        assert found_missing_field, "Validation error should report missing 'description' field"
    
    def test_invalid_consensus_request_empty_options(self):
        """Test that a request with empty options list fails validation"""
        invalid_data = {
            "key": "test_decision",
            "description": "Test consensus decision",
            "options": [],  # Empty options list
            "agents": ["agent1", "agent2"]
        }
        
        # Test with Pydantic model
        with pytest.raises(Exception):
            CreateConsensusDecisionRequest(**invalid_data)
        
        # Test API endpoint with invalid data
        response = client.post(
            "/api/coordination/consensus",
            json=invalid_data,
            headers=get_auth_header()
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        
        # Check that the validation error details contain the empty options error
        found_error = False
        for error in data["detail"]:
            if "options" in str(error.get("loc")):
                found_error = True
                break
        
        assert found_error, "Validation error should report empty 'options' field"
    
    def test_invalid_timeout_value(self):
        """Test that a request with invalid timeout value fails validation"""
        invalid_data = {
            "key": "test_decision",
            "description": "Test consensus decision",
            "options": ["option1", "option2"],
            "timeout_seconds": 5000  # Greater than max of 3600
        }
        
        # Test with Pydantic model
        with pytest.raises(Exception):
            CreateConsensusDecisionRequest(**invalid_data)
        
        # Test API endpoint with invalid data
        response = client.post(
            "/api/coordination/consensus",
            json=invalid_data,
            headers=get_auth_header()
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_error_logging_request(self):
        """Test that error logging validation works correctly"""
        valid_data = {
            "message": "Test error message",
            "category": "API",
            "severity": "ERROR",
            "component": "test",
            "source": "test_validation.py",
            "context": {"test": "context"}
        }
        
        # Test API endpoint
        response = client.post(
            "/api/error-logging/log",
            json=valid_data
        )
        
        # Error logging should work without authentication
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "recorded"
        assert "error_id" in data
    
    def test_invalid_error_category(self):
        """Test that invalid error category fails validation"""
        invalid_data = {
            "message": "Test error message",
            "category": "INVALID_CATEGORY",  # Not a valid ErrorCategory
            "severity": "ERROR",
            "component": "test"
        }
        
        # Test API endpoint
        response = client.post(
            "/api/error-logging/log",
            json=invalid_data
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        
        # Check that the error is about the invalid category
        found_error = False
        for error in data["detail"]:
            if "category" in str(error.get("loc")) and "enum" in str(error.get("type", "")):
                found_error = True
                break
        
        assert found_error, "Validation error should report invalid category"


# Test response validation
class TestResponseValidation:
    """Test cases for response validation using Pydantic models"""
    
    def test_consensus_decision_response(self):
        """Test that a consensus decision response validates correctly"""
        valid_response = {
            "id": "test-id",
            "key": "test_decision",
            "description": "Test consensus decision",
            "options": ["option1", "option2"],
            "status": "pending"
        }
        
        # Test with Pydantic model
        model = ConsensusDecisionResponse(**valid_response)
        assert model.id == valid_response["id"]
        assert model.key == valid_response["key"]
        assert model.description == valid_response["description"]
        assert model.options == valid_response["options"]
        assert model.status == ConsensusStatus.PENDING
    
    def test_invalid_status_value(self):
        """Test that invalid status value fails validation"""
        invalid_response = {
            "id": "test-id",
            "key": "test_decision",
            "description": "Test consensus decision",
            "options": ["option1", "option2"],
            "status": "not_a_valid_status"  # Invalid status
        }
        
        # Test with Pydantic model
        with pytest.raises(Exception):
            ConsensusDecisionResponse(**invalid_response)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
