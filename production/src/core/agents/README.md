# Specialized Agents

This directory contains specialized AI agents that handle specific aspects of the development environment. Each agent is designed to work in conjunction with the Agent Communication System to provide focused functionality.

## Available Agents

### Resource Management Agent
Manages system resources and optimization.

#### Features
- Resource monitoring (CPU, memory, disk, network)
- Resource allocation
- Performance optimization
- Resource prediction
- Cleanup management

#### Usage
```python
from core.agents.resource_management_agent import ResourceManagementAgent

agent = ResourceManagementAgent(
    agent_id="resource_manager",
    name="Resource Manager",
    capabilities=["monitor", "allocate", "optimize", "predict", "cleanup"]
)
```

### Error Handling Agent
Manages error detection, analysis, and recovery.

#### Features
- Error detection and analysis
- Pattern recognition
- Recovery strategy suggestion
- Error prevention
- Error reporting

#### Usage
```python
from core.agents.error_handling_agent import ErrorHandlingAgent

agent = ErrorHandlingAgent(
    agent_id="error_handler",
    name="Error Handler",
    capabilities=["detect", "analyze", "recover", "prevent", "report"]
)
```

### Code Analysis Agent
Analyzes code quality and complexity.

#### Features
- Code quality assessment
- Complexity analysis
- Dependency tracking
- Best practices enforcement
- Performance analysis

#### Usage
```python
from core.agents.code_analysis_agent import CodeAnalysisAgent

agent = CodeAnalysisAgent(
    agent_id="code_analyzer",
    name="Code Analyzer",
    capabilities=["analyze", "assess", "track", "enforce", "optimize"]
)
```

### Task Planning Agent
Manages development tasks and coordination.

#### Features
- Task decomposition
- Dependency management
- Resource allocation
- Progress tracking
- Timeline estimation

#### Usage
```python
from core.agents.task_planning_agent import TaskPlanningAgent

agent = TaskPlanningAgent(
    agent_id="task_planner",
    name="Task Planner",
    capabilities=["plan", "coordinate", "track", "estimate", "optimize"]
)
```

## Agent Communication

All agents communicate through the Agent Communication System using standardized message types:

```python
# Example: Resource Management Agent sending a warning
message = Message(
    message_id="warn1",
    sender_id="resource_manager",
    receiver_id="error_handler",
    message_type=MessageType.NOTIFICATION,
    content={
        "type": "resource_warning",
        "resource": "memory",
        "usage": 85,
        "threshold": 80
    },
    timestamp=time.time()
)
```

## Agent State Management

Each agent maintains its own state using the `AgentState` dataclass:

```python
@dataclass
class AgentState:
    agent_id: str
    name: str
    capabilities: List[str]
    status: str
    current_task: Optional[str]
    last_active: float
    metadata: Dict[str, Any]
    error_count: int
    success_count: int
    total_tasks: int
```

## Testing

Run the test suite for all agents:
```bash
python -m pytest tests/test_agents/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your agent
4. Add tests
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 