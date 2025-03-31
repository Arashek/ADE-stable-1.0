import unittest
import threading
import time
from datetime import datetime
from production.src.core.resource_management_agent import ResourceManagementAgent
from production.src.core.agent_communication import Message, MessageType

class TestResourceManagementAgent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.agent = ResourceManagementAgent()
        
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
        self.assertEqual(self.agent.agent_id, "resource_manager")
        self.assertEqual(self.agent.name, "Resource Management Agent")
        self.assertTrue("resource_monitoring" in self.agent.capabilities)
        self.assertTrue("resource_allocation" in self.agent.capabilities)
        self.assertFalse(self.agent.is_active)
        self.assertEqual(self.agent.state.status, "initialized")

    def test_resource_monitoring(self):
        """Test resource monitoring functionality."""
        # Start agent
        self.agent.start()
        
        # Submit monitoring task
        task_data = {
            "task_type": "monitor_resources",
            "target_agent": "test_agent"
        }
        self.agent.assign_task("monitor_task", task_data)
        
        # Wait for monitoring
        time.sleep(0.2)
        
        # Check for resource status message
        status_messages = [
            msg for msg in self.received_messages
            if msg.message_type == MessageType.NOTIFICATION
            and msg.content["type"] == "resource_status"
        ]
        self.assertTrue(len(status_messages) > 0)
        
        # Verify metrics
        metrics = status_messages[-1].content["data"]["metrics"]
        self.assertIn("cpu_percent", metrics)
        self.assertIn("memory_percent", metrics)
        self.assertIn("disk_percent", metrics)
        self.assertIn("network_io", metrics)

    def test_resource_allocation(self):
        """Test resource allocation functionality."""
        # Start agent
        self.agent.start()
        
        # Submit allocation task
        task_data = {
            "task_type": "allocate_resources",
            "target_agent": "test_agent",
            "resource_requirements": {
                "cpu": 20,
                "memory": 30,
                "disk": 10
            }
        }
        self.agent.assign_task("allocate_task", task_data)
        
        # Wait for allocation
        time.sleep(0.2)
        
        # Check for allocation message
        allocation_messages = [
            msg for msg in self.received_messages
            if msg.message_type == MessageType.NOTIFICATION
            and msg.content["type"] == "resource_allocation"
        ]
        self.assertTrue(len(allocation_messages) > 0)
        
        # Verify allocation data
        allocation_data = allocation_messages[-1].content["data"]
        self.assertEqual(allocation_data["target_agent"], "test_agent")
        self.assertEqual(allocation_data["requirements"]["cpu"], 20)

    def test_resource_optimization(self):
        """Test resource optimization functionality."""
        # Start agent
        self.agent.start()
        
        # Submit optimization task
        task_data = {
            "task_type": "optimize_resources",
            "target_agent": "test_agent"
        }
        self.agent.assign_task("optimize_task", task_data)
        
        # Wait for optimization
        time.sleep(0.2)
        
        # Check for optimization message
        optimization_messages = [
            msg for msg in self.received_messages
            if msg.message_type == MessageType.NOTIFICATION
            and msg.content["type"] == "resource_optimization"
        ]
        self.assertTrue(len(optimization_messages) > 0)
        
        # Verify optimization data
        optimization_data = optimization_messages[-1].content["data"]
        self.assertEqual(optimization_data["target_agent"], "test_agent")
        self.assertIn("recommendations", optimization_data)

    def test_resource_prediction(self):
        """Test resource usage prediction functionality."""
        # Start agent
        self.agent.start()
        
        # Submit prediction task
        task_data = {
            "task_type": "predict_resources",
            "target_agent": "test_agent"
        }
        self.agent.assign_task("predict_task", task_data)
        
        # Wait for prediction
        time.sleep(0.2)
        
        # Check for prediction message
        prediction_messages = [
            msg for msg in self.received_messages
            if msg.message_type == MessageType.NOTIFICATION
            and msg.content["type"] == "resource_predictions"
        ]
        self.assertTrue(len(prediction_messages) > 0)
        
        # Verify prediction data
        prediction_data = prediction_messages[-1].content["data"]
        self.assertEqual(prediction_data["target_agent"], "test_agent")
        self.assertIn("predictions", prediction_data)

    def test_resource_cleanup(self):
        """Test resource cleanup functionality."""
        # Start agent
        self.agent.start()
        
        # Submit cleanup task
        task_data = {
            "task_type": "cleanup_resources",
            "target_agent": "test_agent"
        }
        self.agent.assign_task("cleanup_task", task_data)
        
        # Wait for cleanup
        time.sleep(0.2)
        
        # Check for cleanup message
        cleanup_messages = [
            msg for msg in self.received_messages
            if msg.message_type == MessageType.NOTIFICATION
            and msg.content["type"] == "resource_cleanup"
        ]
        self.assertTrue(len(cleanup_messages) > 0)
        
        # Verify cleanup data
        cleanup_data = cleanup_messages[-1].content["data"]
        self.assertEqual(cleanup_data["target_agent"], "test_agent")

    def test_resource_thresholds(self):
        """Test resource threshold monitoring."""
        # Start agent
        self.agent.start()
        
        # Simulate high resource usage
        self.agent.resource_metrics["test_agent"] = self.agent.ResourceMetrics(
            cpu_percent=85.0,
            memory_percent=90.0,
            disk_percent=95.0,
            network_io={"bytes_sent": 2000000, "bytes_recv": 2000000}
        )
        
        # Trigger threshold check
        self.agent._check_resource_thresholds(
            self.agent.resource_metrics["test_agent"]
        )
        
        # Check for warning messages
        warning_messages = [
            msg for msg in self.received_messages
            if msg.message_type == MessageType.NOTIFICATION
            and msg.content["type"] == "resource_warning"
        ]
        self.assertTrue(len(warning_messages) > 0)
        
        # Verify warning data
        warning_data = warning_messages[-1].content["data"]
        self.assertIn("resource", warning_data)
        self.assertIn("value", warning_data)
        self.assertIn("threshold", warning_data)

    def test_resource_availability(self):
        """Test resource availability checking."""
        # Set up test metrics
        self.agent.resource_metrics["system"] = self.agent.ResourceMetrics(
            cpu_percent=50.0,
            memory_percent=60.0,
            disk_percent=70.0,
            network_io={"bytes_sent": 0, "bytes_recv": 0}
        )
        
        # Test available resources
        requirements = {
            "cpu": 20,
            "memory": 30,
            "disk": 10
        }
        self.assertTrue(self.agent._check_resource_availability(requirements))
        
        # Test unavailable resources
        requirements = {
            "cpu": 60,
            "memory": 50,
            "disk": 30
        }
        self.assertFalse(self.agent._check_resource_availability(requirements))

    def test_resource_pattern_analysis(self):
        """Test resource pattern analysis."""
        # Add test metrics
        for i in range(5):
            self.agent.resource_metrics[f"test_agent_{i}"] = self.agent.ResourceMetrics(
                cpu_percent=70.0 + i,
                memory_percent=75.0 + i,
                disk_percent=80.0 + i,
                network_io={"bytes_sent": 1000000, "bytes_recv": 1000000}
            )
        
        # Analyze patterns
        patterns = self.agent._analyze_resource_patterns(
            self.agent.resource_metrics["test_agent_0"]
        )
        
        # Verify pattern analysis
        self.assertIn("cpu", patterns)
        self.assertIn("memory", patterns)
        self.assertIn("disk", patterns)
        self.assertIn("network", patterns)

    def test_resource_optimization_settings(self):
        """Test resource optimization settings."""
        # Test default settings
        self.assertTrue(self.agent.settings["auto_scale"])
        self.assertTrue(self.agent.settings["load_balance"])
        self.assertEqual(self.agent.settings["cleanup_threshold"], 70.0)
        
        # Test threshold values
        self.assertEqual(self.agent.resource_thresholds["cpu"], 80.0)
        self.assertEqual(self.agent.resource_thresholds["memory"], 85.0)
        self.assertEqual(self.agent.resource_thresholds["disk"], 90.0)
        self.assertEqual(self.agent.resource_thresholds["network"], 1000.0)

if __name__ == '__main__':
    unittest.main() 