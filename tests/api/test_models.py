"""
Test the validation of the Pydantic API models
"""

import pytest
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.models.api_models import (
    CreateConsensusDecisionRequest,
    ConsensusDecisionResponse,
    ErrorCategory,
    ErrorSeverity,
    ConsensusStatus,
    ConflictResolutionRequest,
    ErrorLogRequest
)

class TestPydanticModels:
    """Test the validation of Pydantic models for API requests and responses"""
    
    def test_create_consensus_decision_request(self):
        """Test CreateConsensusDecisionRequest validation"""
        # Valid model
        valid_model = CreateConsensusDecisionRequest(
            key="test_decision",
            description="Test consensus decision",
            options=["option1", "option2", "option3"],
            agents=["agent1", "agent2"],
            timeout_seconds=120
        )
        
        assert valid_model.key == "test_decision"
        assert valid_model.description == "Test consensus decision"
        assert valid_model.options == ["option1", "option2", "option3"]
        assert valid_model.agents == ["agent1", "agent2"]
        assert valid_model.timeout_seconds == 120
        
        # Test missing required fields
        with pytest.raises(ValueError):
            CreateConsensusDecisionRequest(
                key="test_decision",
                # Missing description
                options=["option1", "option2"]
            )
        
        # Test empty options
        with pytest.raises(ValueError):
            CreateConsensusDecisionRequest(
                key="test_decision",
                description="Test consensus decision",
                options=[]  # Empty options list
            )
        
        # Test invalid timeout
        with pytest.raises(ValueError):
            CreateConsensusDecisionRequest(
                key="test_decision",
                description="Test consensus decision",
                options=["option1", "option2"],
                timeout_seconds=5000  # Greater than max of 3600
            )
    
    def test_consensus_decision_response(self):
        """Test ConsensusDecisionResponse validation"""
        # Valid model
        valid_model = ConsensusDecisionResponse(
            id="test-id",
            key="test_decision",
            description="Test consensus decision",
            options=["option1", "option2"],
            status=ConsensusStatus.PENDING
        )
        
        assert valid_model.id == "test-id"
        assert valid_model.key == "test_decision"
        assert valid_model.description == "Test consensus decision"
        assert valid_model.options == ["option1", "option2"]
        assert valid_model.status == ConsensusStatus.PENDING
        
        # Test invalid status
        with pytest.raises(ValueError):
            ConsensusDecisionResponse(
                id="test-id",
                key="test_decision",
                description="Test consensus decision",
                options=["option1", "option2"],
                status="not_a_valid_status"  # Invalid status
            )
    
    def test_conflict_resolution_request(self):
        """Test ConflictResolutionRequest validation"""
        # Valid model
        valid_model = ConflictResolutionRequest(
            attribute="test_attribute",
            values={"agent1": "value1", "agent2": "value2"},
            selected_value="value1",
            selected_agent="agent1",
            confidence=0.8,
            reasoning="Test reasoning"
        )
        
        assert valid_model.attribute == "test_attribute"
        assert valid_model.values == {"agent1": "value1", "agent2": "value2"}
        assert valid_model.selected_value == "value1"
        assert valid_model.selected_agent == "agent1"
        assert valid_model.confidence == 0.8
        assert valid_model.reasoning == "Test reasoning"
        
        # Test invalid confidence
        with pytest.raises(ValueError):
            ConflictResolutionRequest(
                attribute="test_attribute",
                values={"agent1": "value1", "agent2": "value2"},
                selected_value="value1",
                selected_agent="agent1",
                confidence=1.5  # Greater than 1.0
            )
        
        # Test empty values
        with pytest.raises(ValueError):
            ConflictResolutionRequest(
                attribute="test_attribute",
                values={},  # Empty values
                selected_value="value1",
                selected_agent="agent1",
                confidence=0.8
            )
        
        # Test selected agent not in values
        with pytest.raises(ValueError):
            ConflictResolutionRequest(
                attribute="test_attribute",
                values={"agent1": "value1", "agent2": "value2"},
                selected_value="value1",
                selected_agent="agent3",  # Not in values
                confidence=0.8
            )
    
    def test_error_log_request(self):
        """Test ErrorLogRequest validation"""
        # Valid model
        valid_model = ErrorLogRequest(
            message="Test error message",
            error_type="TypeError",
            category=ErrorCategory.API,
            severity=ErrorSeverity.ERROR,
            component="test",
            source="test_models.py",
            stack_trace="Test stack trace",
            context={"test": "context"}
        )
        
        assert valid_model.message == "Test error message"
        assert valid_model.error_type == "TypeError"
        assert valid_model.category == ErrorCategory.API
        assert valid_model.severity == ErrorSeverity.ERROR
        assert valid_model.component == "test"
        assert valid_model.source == "test_models.py"
        assert valid_model.stack_trace == "Test stack trace"
        assert valid_model.context == {"test": "context"}
        
        # Test missing message
        with pytest.raises(ValueError):
            ErrorLogRequest(
                # Missing message
                error_type="TypeError",
                category=ErrorCategory.API,
                severity=ErrorSeverity.ERROR
            )
        
        # Test invalid category
        with pytest.raises(ValueError):
            ErrorLogRequest(
                message="Test error message",
                category="INVALID_CATEGORY"  # Not a valid ErrorCategory
            )
        
        # Test invalid severity
        with pytest.raises(ValueError):
            ErrorLogRequest(
                message="Test error message",
                severity="INVALID_SEVERITY"  # Not a valid ErrorSeverity
            )


# Run the tests if this file is executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
