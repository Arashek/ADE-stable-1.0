import unittest
import threading
import time
from datetime import datetime
from production.src.core.agent_communication import (
    AgentCommunicationSystem,
    Message,
    MessageType
)

class TestAgentCommunicationSystem(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.comm_system = AgentCommunicationSystem()
        self.agent1_id = "agent1"
        self.agent2_id = "agent2"
        self.comm_system.register_agent(self.agent1_id)
        self.comm_system.register_agent(self.agent2_id)
        
        # Track received messages
        self.received_messages = []
        
        # Register message handlers
        self.comm_system.register_handler(
            self.agent2_id,
            MessageType.REQUEST,
            self._handle_request
        )
        self.comm_system.register_handler(
            self.agent1_id,
            MessageType.RESPONSE,
            self._handle_response
        )

    def tearDown(self):
        """Clean up test fixtures."""
        self.comm_system.unregister_agent(self.agent1_id)
        self.comm_system.unregister_agent(self.agent2_id)

    def _handle_request(self, message: Message):
        """Handle request messages."""
        self.received_messages.append(message)
        # Send response
        response = Message(
            message_id=f"resp_{datetime.now().timestamp()}",
            sender_id=self.agent2_id,
            receiver_id=self.agent1_id,
            message_type=MessageType.RESPONSE,
            content={"status": "success"},
            metadata={"request_id": message.message_id}
        )
        self.comm_system.send_message(response)

    def _handle_response(self, message: Message):
        """Handle response messages."""
        self.received_messages.append(message)

    def test_agent_registration(self):
        """Test agent registration and unregistration."""
        # Test registration
        self.assertIn(self.agent1_id, self.comm_system.message_queues)
        self.assertIn(self.agent1_id, self.comm_system.message_handlers)
        
        # Test duplicate registration
        with self.assertRaises(ValueError):
            self.comm_system.register_agent(self.agent1_id)
        
        # Test unregistration
        self.comm_system.unregister_agent(self.agent1_id)
        self.assertNotIn(self.agent1_id, self.comm_system.message_queues)
        self.assertNotIn(self.agent1_id, self.comm_system.message_handlers)

    def test_message_sending(self):
        """Test message sending between agents."""
        # Send request
        request = Message(
            message_id="test_req",
            sender_id=self.agent1_id,
            receiver_id=self.agent2_id,
            message_type=MessageType.REQUEST,
            content={"action": "test"}
        )
        
        success = self.comm_system.send_message(request)
        self.assertTrue(success)
        
        # Verify message in queue
        self.assertEqual(len(self.comm_system.message_queues[self.agent2_id]), 1)
        self.assertEqual(
            self.comm_system.message_queues[self.agent2_id][0].message_id,
            "test_req"
        )

    def test_request_response(self):
        """Test request-response pattern."""
        # Send request and wait for response
        response = self.comm_system.send_request(
            self.agent1_id,
            self.agent2_id,
            {"action": "test"}
        )
        
        # Process messages
        self.comm_system.process_messages(self.agent2_id)
        self.comm_system.process_messages(self.agent1_id)
        
        # Verify response
        self.assertIsNotNone(response)
        self.assertEqual(response["status"], "success")

    def test_broadcast_notification(self):
        """Test broadcast notifications."""
        # Send broadcast notification
        self.comm_system.broadcast_notification(
            self.agent1_id,
            {"event": "test_event"}
        )
        
        # Verify notification received by other agent
        self.assertEqual(len(self.comm_system.message_queues[self.agent2_id]), 1)
        notification = self.comm_system.message_queues[self.agent2_id][0]
        self.assertEqual(notification.message_type, MessageType.NOTIFICATION)
        self.assertEqual(notification.content["event"], "test_event")

    def test_heartbeat(self):
        """Test heartbeat messages."""
        # Wait for heartbeat
        time.sleep(6)  # Wait for one heartbeat interval
        
        # Verify heartbeat received
        self.assertTrue(len(self.comm_system.message_queues[self.agent1_id]) > 0)
        heartbeat = self.comm_system.message_queues[self.agent1_id][0]
        self.assertEqual(heartbeat.message_type, MessageType.HEARTBEAT)

    def test_error_handling(self):
        """Test error handling and reporting."""
        # Register error handler
        error_received = threading.Event()
        def handle_error(message: Message):
            self.assertEqual(message.message_type, MessageType.ERROR)
            error_received.set()
        
        self.comm_system.register_handler(
            self.agent1_id,
            MessageType.ERROR,
            handle_error
        )
        
        # Send message to non-existent agent
        message = Message(
            message_id="test_err",
            sender_id=self.agent1_id,
            receiver_id="non_existent",
            message_type=MessageType.REQUEST,
            content={"action": "test"}
        )
        
        success = self.comm_system.send_message(message)
        self.assertFalse(success)
        
        # Process messages
        self.comm_system.process_messages(self.agent1_id)
        
        # Verify error handling
        self.assertTrue(error_received.is_set())

    def test_message_clearing(self):
        """Test message queue clearing."""
        # Add messages to queue
        for i in range(3):
            message = Message(
                message_id=f"test_{i}",
                sender_id=self.agent1_id,
                receiver_id=self.agent2_id,
                message_type=MessageType.REQUEST,
                content={"action": f"test_{i}"}
            )
            self.comm_system.send_message(message)
        
        # Verify messages in queue
        self.assertEqual(len(self.comm_system.message_queues[self.agent2_id]), 3)
        
        # Clear messages
        self.comm_system.clear_messages(self.agent2_id)
        
        # Verify queue is empty
        self.assertEqual(len(self.comm_system.message_queues[self.agent2_id]), 0)

    def test_agent_status(self):
        """Test agent status reporting."""
        # Get status for registered agent
        status = self.comm_system.get_agent_status(self.agent1_id)
        self.assertEqual(status["status"], "active")
        self.assertIn("pending_messages", status)
        self.assertIn("registered_handlers", status)
        
        # Get status for non-existent agent
        status = self.comm_system.get_agent_status("non_existent")
        self.assertEqual(status["status"], "not_registered")

if __name__ == '__main__':
    unittest.main() 