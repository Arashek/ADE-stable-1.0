import unittest
import threading
import time
from datetime import datetime
from production.src.core.error_handling_agent import ErrorHandlingAgent
from production.src.core.agent_communication import Message, MessageType

class TestErrorHandlingAgent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.agent = ErrorHandlingAgent()
        
        # Track received messages
        self.received_messages = []
        
        # Register message handler for testing
        self.agent.comm_system.register_handler(
            self.agent.agent_id,
            MessageType.NOTIFICATION,
            self._handle_notification
        )

    def tearDown(self):
        """Clean up test fixtures."""
        if self.agent.is_active:
            self.agent.stop()
        self.agent.comm_system.unregister_agent(self.agent.agent_id)

    def _handle_notification(self, message: Message):
        """Handle notification messages for testing."""
        self.received_messages.append(message)

    def test_agent_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.agent_id, "error_handler")
        self.assertEqual(self.agent.name, "Error Handling Agent")
        self.assertTrue("error_detection" in self.agent.capabilities)
        self.assertTrue("error_analysis" in self.agent.capabilities)
        self.assertFalse(self.agent.is_active)
        self.assertEqual(self.agent.state.status, "initialized")

    def test_error_handling(self):
        """Test error handling functionality."""
        # Start agent
        self.agent.start()
        
        # Submit error handling task
        task_data = {
            "task_type": "handle_error",
            "error": {
                "error_id": "test_error_1",
                "error_type": "ValueError",
                "message": "Test error message",
                "stack_trace": "Traceback (most recent call last):\n  File \"test.py\", line 1, in <module>\n    raise ValueError('Test error message')",
                "context": {"source": "test_agent", "operation": "test_operation"},
                "timestamp": datetime.now().isoformat(),
                "severity": "high"
            }
        }
        self.agent.assign_task("handle_error_task", task_data)
        
        # Wait for error handling
        time.sleep(0.2)
        
        # Check for error handling message
        handling_messages = [
            msg for msg in self.received_messages
            if msg.message_type == MessageType.NOTIFICATION
            and msg.content["type"] == "error_handled"
        ]
        self.assertTrue(len(handling_messages) > 0)
        
        # Verify error handling data
        handling_data = handling_messages[-1].content["data"]
        self.assertEqual(handling_data["error_id"], "test_error_1")
        self.assertEqual(handling_data["status"], "resolved")

    def test_error_pattern_analysis(self):
        """Test error pattern analysis functionality."""
        # Start agent
        self.agent.start()
        
        # Submit pattern analysis task
        task_data = {
            "task_type": "analyze_patterns",
            "time_window": 3600  # 1 hour
        }
        self.agent.assign_task("analyze_patterns_task", task_data)
        
        # Wait for pattern analysis
        time.sleep(0.2)
        
        # Check for pattern analysis message
        pattern_messages = [
            msg for msg in self.received_messages
            if msg.message_type == MessageType.NOTIFICATION
            and msg.content["type"] == "error_patterns"
        ]
        self.assertTrue(len(pattern_messages) > 0)
        
        # Verify pattern analysis data
        pattern_data = pattern_messages[-1].content["data"]
        self.assertIn("patterns", pattern_data)
        self.assertIn("recommendations", pattern_data)

    def test_recovery_strategy_suggestion(self):
        """Test recovery strategy suggestion functionality."""
        # Start agent
        self.agent.start()
        
        # Submit strategy suggestion task
        task_data = {
            "task_type": "suggest_recovery",
            "error": {
                "error_id": "test_error_2",
                "error_type": "ConnectionError",
                "message": "Connection refused",
                "severity": "medium"
            }
        }
        self.agent.assign_task("suggest_recovery_task", task_data)
        
        # Wait for strategy suggestion
        time.sleep(0.2)
        
        # Check for strategy suggestion message
        strategy_messages = [
            msg for msg in self.received_messages
            if msg.message_type == MessageType.NOTIFICATION
            and msg.content["type"] == "recovery_strategy"
        ]
        self.assertTrue(len(strategy_messages) > 0)
        
        # Verify strategy data
        strategy_data = strategy_messages[-1].content["data"]
        self.assertEqual(strategy_data["error_id"], "test_error_2")
        self.assertIn("strategy", strategy_data)
        self.assertIn("confidence", strategy_data)

    def test_error_prevention(self):
        """Test error prevention functionality."""
        # Start agent
        self.agent.start()
        
        # Submit prevention task
        task_data = {
            "task_type": "prevent_errors",
            "target_agent": "test_agent"
        }
        self.agent.assign_task("prevent_errors_task", task_data)
        
        # Wait for prevention analysis
        time.sleep(0.2)
        
        # Check for prevention message
        prevention_messages = [
            msg for msg in self.received_messages
            if msg.message_type == MessageType.NOTIFICATION
            and msg.content["type"] == "error_prevention"
        ]
        self.assertTrue(len(prevention_messages) > 0)
        
        # Verify prevention data
        prevention_data = prevention_messages[-1].content["data"]
        self.assertEqual(prevention_data["target_agent"], "test_agent")
        self.assertIn("prevention_measures", prevention_data)

    def test_error_severity_determination(self):
        """Test error severity determination."""
        # Test high severity error
        error = {
            "error_type": "SystemError",
            "message": "Critical system failure",
            "context": {"impact": "system-wide"}
        }
        severity = self.agent._determine_severity(error)
        self.assertEqual(severity, "high")
        
        # Test medium severity error
        error = {
            "error_type": "ConnectionError",
            "message": "Connection timeout",
            "context": {"impact": "service-degradation"}
        }
        severity = self.agent._determine_severity(error)
        self.assertEqual(severity, "medium")
        
        # Test low severity error
        error = {
            "error_type": "ValueError",
            "message": "Invalid input",
            "context": {"impact": "none"}
        }
        severity = self.agent._determine_severity(error)
        self.assertEqual(severity, "low")

    def test_error_root_cause_analysis(self):
        """Test error root cause analysis."""
        # Test with stack trace
        error = {
            "stack_trace": "Traceback (most recent call last):\n  File \"main.py\", line 10, in process_data\n    result = data / 0\nZeroDivisionError: division by zero"
        }
        root_cause = self.agent._identify_root_cause(error)
        self.assertIn("division by zero", root_cause)
        
        # Test with context
        error = {
            "context": {
                "operation": "database_connection",
                "last_success": "2024-01-01T00:00:00",
                "failure_point": "connection_establishment"
            }
        }
        root_cause = self.agent._identify_root_cause(error)
        self.assertIn("connection", root_cause)

    def test_error_impact_assessment(self):
        """Test error impact assessment."""
        # Test system-wide impact
        error = {
            "error_type": "SystemError",
            "context": {"scope": "system", "affected_components": ["core", "api", "database"]}
        }
        impact = self.agent._assess_impact(error)
        self.assertEqual(impact, "high")
        
        # Test service-level impact
        error = {
            "error_type": "ServiceError",
            "context": {"scope": "service", "affected_components": ["api"]}
        }
        impact = self.agent._assess_impact(error)
        self.assertEqual(impact, "medium")
        
        # Test component-level impact
        error = {
            "error_type": "ComponentError",
            "context": {"scope": "component", "affected_components": ["logger"]}
        }
        impact = self.agent._assess_impact(error)
        self.assertEqual(impact, "low")

    def test_error_similarity_calculation(self):
        """Test error similarity calculation."""
        # Test similar errors
        error1 = {
            "error_type": "ConnectionError",
            "message": "Connection refused",
            "context": {"port": 8080}
        }
        error2 = {
            "error_type": "ConnectionError",
            "message": "Connection refused",
            "context": {"port": 8080}
        }
        similarity = self.agent._calculate_error_similarity(error1, error2)
        self.assertGreater(similarity, 0.8)
        
        # Test different errors
        error1 = {
            "error_type": "ValueError",
            "message": "Invalid input"
        }
        error2 = {
            "error_type": "TypeError",
            "message": "Type mismatch"
        }
        similarity = self.agent._calculate_error_similarity(error1, error2)
        self.assertLess(similarity, 0.5)

    def test_error_handling_settings(self):
        """Test error handling settings."""
        # Test default settings
        self.assertTrue(self.agent.settings["auto_recover"])
        self.assertTrue(self.agent.settings["pattern_analysis"])
        self.assertEqual(self.agent.settings["max_retries"], 3)
        
        # Test threshold values
        self.assertEqual(self.agent.error_thresholds["high_severity"], 5)
        self.assertEqual(self.agent.error_thresholds["medium_severity"], 10)
        self.assertEqual(self.agent.error_thresholds["low_severity"], 20)

if __name__ == '__main__':
    unittest.main() 