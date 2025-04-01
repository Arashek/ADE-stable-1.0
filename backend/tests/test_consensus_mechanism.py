import unittest
import asyncio
import json
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.coordination.consensus_mechanism import (
    ConsensusMechanism, 
    ConflictDetector, 
    ConflictResolutionStrategy,
    ConsensusVote
)
from services.coordination.agent_interface import AgentInterface, MessageType
from services.coordination.agent_coordinator import AgentCoordinator


class MockAgentInterface(AgentInterface):
    """Mock implementation of AgentInterface for testing"""
    
    def __init__(self, agent_id, agent_type):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.messages = []
        self.responses = {}
    
    def send_message(self, target_agent_id, message_type, content):
        message_id = f"msg_{len(self.messages)}"
        self.messages.append({
            "id": message_id,
            "target": target_agent_id,
            "type": message_type,
            "content": content
        })
        return message_id
    
    def set_response(self, message_id, response):
        """Set a predefined response for a message ID"""
        self.responses[message_id] = response
    
    async def receive_message(self, message_id, timeout=5.0):
        """Mock receive_message to return predefined responses"""
        if message_id in self.responses:
            return self.responses[message_id]
        return {"success": False, "error": "No response defined"}


class TestConflictDetector(unittest.TestCase):
    """Test cases for the ConflictDetector class"""
    
    def test_detect_conflicts_simple(self):
        """Test conflict detection with simple conflicting values"""
        agent_recommendations = {
            "security": {
                "result": {
                    "authentication": {
                        "method": "oauth2"
                    }
                }
            },
            "architecture": {
                "result": {
                    "authentication": {
                        "method": "jwt"
                    }
                }
            }
        }
        
        conflicts = ConflictDetector.detect_conflicts(agent_recommendations)
        
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["attribute"], "authentication.method")
        self.assertEqual(conflicts[0]["values"]["security"], "oauth2")
        self.assertEqual(conflicts[0]["values"]["architecture"], "jwt")
    
    def test_detect_conflicts_nested(self):
        """Test conflict detection with nested conflicting values"""
        agent_recommendations = {
            "security": {
                "result": {
                    "database": {
                        "encryption": {
                            "enabled": True
                        }
                    }
                }
            },
            "performance": {
                "result": {
                    "database": {
                        "encryption": {
                            "enabled": False
                        }
                    }
                }
            }
        }
        
        conflicts = ConflictDetector.detect_conflicts(agent_recommendations)
        
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["attribute"], "database.encryption.enabled")
        self.assertEqual(conflicts[0]["values"]["security"], True)
        self.assertEqual(conflicts[0]["values"]["performance"], False)
    
    def test_no_conflicts(self):
        """Test when there are no conflicts"""
        agent_recommendations = {
            "security": {
                "result": {
                    "authentication": {
                        "method": "oauth2"
                    }
                }
            },
            "architecture": {
                "result": {
                    "database": {
                        "type": "postgresql"
                    }
                }
            }
        }
        
        conflicts = ConflictDetector.detect_conflicts(agent_recommendations)
        
        self.assertEqual(len(conflicts), 0)


class TestConsensusMechanism(unittest.IsolatedAsyncioTestCase):
    """Test cases for the ConsensusMechanism class"""
    
    async def asyncSetUp(self):
        """Set up test fixtures"""
        self.consensus_mechanism = ConsensusMechanism()
        
        # Set agent priorities
        self.consensus_mechanism.agent_priorities = {
            "security": 5,
            "architecture": 4,
            "validation": 3,
            "performance": 2,
            "design": 1
        }
        
        # Create mock agent interfaces
        self.security_agent = MockAgentInterface("security-1", "security")
        self.architecture_agent = MockAgentInterface("architecture-1", "architecture")
        self.design_agent = MockAgentInterface("design-1", "design")
        
        self.agent_interfaces = {
            "security": self.security_agent,
            "architecture": self.architecture_agent,
            "design": self.design_agent
        }
    
    async def test_resolve_conflict_priority_based(self):
        """Test priority-based conflict resolution"""
        conflict = {
            "attribute": "authentication.method",
            "values": {
                "security": "oauth2",
                "architecture": "jwt"
            }
        }
        
        agent_recommendations = {
            "security": {
                "agent_type": "security",
                "result": {
                    "authentication": {
                        "method": "oauth2"
                    }
                }
            },
            "architecture": {
                "agent_type": "architecture",
                "result": {
                    "authentication": {
                        "method": "jwt"
                    }
                }
            }
        }
        
        resolution = await self.consensus_mechanism.resolve_conflict(
            conflict=conflict,
            agent_recommendations=agent_recommendations,
            strategy=ConflictResolutionStrategy.PRIORITY_BASED.value,
            context={"task_type": "authentication_setup"}
        )
        
        self.assertEqual(resolution["selected_agent"], "security")
        self.assertEqual(resolution["recommendation"]["method"], "oauth2")
        self.assertGreater(resolution["confidence"], 0.7)
    
    async def test_build_consensus(self):
        """Test building consensus among agents"""
        decision_point = {
            "id": "decision_123",
            "key": "database_type",
            "description": "Choose database type for the application",
            "options": ["postgresql", "mongodb", "mysql"]
        }
        
        # Set up mock responses
        self.security_agent.set_response("msg_0", {
            "success": True,
            "vote": {
                "option": "postgresql",
                "confidence": 0.8,
                "reasoning": "PostgreSQL has better security features"
            }
        })
        
        self.architecture_agent.set_response("msg_0", {
            "success": True,
            "vote": {
                "option": "postgresql",
                "confidence": 0.9,
                "reasoning": "PostgreSQL is better for complex data models"
            }
        })
        
        self.design_agent.set_response("msg_0", {
            "success": True,
            "vote": {
                "option": "mongodb",
                "confidence": 0.7,
                "reasoning": "MongoDB is more flexible for UI data"
            }
        })
        
        result = await self.consensus_mechanism.build_consensus(
            decision_point=decision_point,
            agent_interfaces=self.agent_interfaces,
            context={"task_type": "database_selection"},
            threshold=0.7
        )
        
        self.assertEqual(result["selected_option"], "postgresql")
        self.assertGreater(result["confidence"], 0.8)
        self.assertEqual(len(result["votes"]), 3)
    
    async def test_integration_with_agent_coordinator(self):
        """Test integration with the AgentCoordinator"""
        with patch('backend.services.coordination.agent_registry.AgentRegistry') as mock_registry:
            # Set up mock registry
            mock_registry_instance = MagicMock()
            mock_registry.return_value = mock_registry_instance
            
            # Mock get_agents_by_type to return our agent IDs
            mock_registry_instance.get_agents_by_type.side_effect = lambda agent_type: {
                "security": ["security-1"],
                "architecture": ["architecture-1"],
                "design": ["design-1"]
            }.get(agent_type, [])
            
            # Mock get_agent_interface to return our mock interfaces
            mock_registry_instance.get_agent_interface.side_effect = lambda agent_id: {
                "security-1": self.security_agent,
                "architecture-1": self.architecture_agent,
                "design-1": self.design_agent
            }.get(agent_id)
            
            # Create agent coordinator
            coordinator = AgentCoordinator()
            coordinator.registry = mock_registry_instance
            coordinator.consensus_mechanism = self.consensus_mechanism
            
            # Test resolve_conflicts
            results = [
                {
                    "agent_type": "security",
                    "success": True,
                    "result": {
                        "authentication": {
                            "method": "oauth2"
                        }
                    }
                },
                {
                    "agent_type": "architecture",
                    "success": True,
                    "result": {
                        "authentication": {
                            "method": "jwt"
                        }
                    }
                }
            ]
            
            resolved = await coordinator.resolve_conflicts(results)
            
            self.assertTrue("authentication" in resolved)
            self.assertTrue("method" in resolved["authentication"])
            self.assertTrue("conflict_resolutions" in resolved)


if __name__ == '__main__':
    unittest.main()
