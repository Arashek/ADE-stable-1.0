# Agent Communication System

The Agent Communication System is a robust framework for facilitating communication between AI agents in the platform. It provides a structured way for agents to exchange messages, handle tasks, and maintain system state.

## Features

### Message Types
- `REQUEST`: For task assignments and queries
- `RESPONSE`: For task results and query responses
- `NOTIFICATION`: For system-wide announcements
- `ERROR`: For error reporting and handling
- `HEARTBEAT`: For agent status monitoring

### Core Functionality
- Thread-safe message queues
- Request-response pattern
- Broadcast notifications
- Error handling and recovery
- Agent status monitoring
- Message persistence

### Message Structure
```python
@dataclass
class Message:
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: float
```

## Components

### AgentCommunicationSystem
The main class that manages all agent communications.

#### Key Methods
- `register_agent(agent_id: str)`: Register a new agent
- `unregister_agent(agent_id: str)`: Remove an agent from the system
- `send_message(message: Message)`: Send a message between agents
- `process_messages(agent_id: str)`: Process messages for a specific agent
- `broadcast_notification(message: Message)`: Send a message to all agents
- `get_agent_status(agent_id: str)`: Get the current status of an agent

## Usage

```python
# Initialize the communication system
comm_system = AgentCommunicationSystem()

# Register agents
comm_system.register_agent("agent1")
comm_system.register_agent("agent2")

# Send a message
message = Message(
    message_id="msg1",
    sender_id="agent1",
    receiver_id="agent2",
    message_type=MessageType.REQUEST,
    content={"task": "analyze_code"},
    timestamp=time.time()
)
comm_system.send_message(message)

# Process messages
comm_system.process_messages("agent2")
```

## Error Handling

The system includes comprehensive error handling:
- Message validation
- Queue management
- Agent status tracking
- Error broadcasting
- Recovery mechanisms

## Thread Safety

All operations are thread-safe using:
- Message queue locks
- Agent registration locks
- Status update locks
- Error handling locks

## Testing

Run the test suite:
```bash
python -m pytest tests/test_agent_communication.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 