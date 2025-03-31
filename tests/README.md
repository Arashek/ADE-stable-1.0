# Test Suite

This directory contains comprehensive test suites for all components of the platform, including the Agent Communication System, specialized agents, and the Command Center interface.

## Test Structure

```
tests/
├── test_agent_communication.py
├── test_agents/
│   ├── test_resource_management_agent.py
│   ├── test_error_handling_agent.py
│   ├── test_code_analysis_agent.py
│   └── test_task_planning_agent.py
├── test_command_center/
│   ├── test_components/
│   │   ├── test_input_controls.jsx
│   │   ├── test_voice_recognition.jsx
│   │   ├── test_image_handler.jsx
│   │   └── test_clipboard_manager.jsx
│   └── test_integration/
│       └── test_multimodal_input.jsx
└── test_api/
    ├── test_command_center_api.py
    ├── test_voice_processing.py
    ├── test_ocr_service.py
    └── test_context_management.py
```

## Running Tests

### Python Tests
```bash
# Run all Python tests
python -m pytest

# Run specific test file
python -m pytest tests/test_agent_communication.py

# Run tests with coverage
python -m pytest --cov=src tests/
```

### JavaScript Tests
```bash
# Run all JavaScript tests
npm test

# Run specific test file
npm test src/components/CommandCenter/__tests__/CommandCenter.test.jsx

# Run tests with coverage
npm test -- --coverage
```

## Test Categories

### Agent Communication Tests
- Message passing
- Queue management
- Error handling
- Thread safety
- Performance metrics

### Agent Tests
- Resource management
- Error handling
- Code analysis
- Task planning
- State management

### Command Center Tests
- Component rendering
- User interactions
- State management
- Input handling
- Accessibility

### API Tests
- Endpoint functionality
- Data processing
- Error handling
- Integration
- Performance

## Test Utilities

### Mock Store
```javascript
const createTestStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      commandCenter: commandCenterReducer,
    },
    preloadedState: {
      commandCenter: {
        ...initialState,
      },
    },
  });
};
```

### Test Renderer
```javascript
const renderWithProviders = (component, initialState = {}) => {
  const store = createTestStore(initialState);
  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        {component}
      </ThemeProvider>
    </Provider>
  );
};
```

### Mock API
```python
@pytest.fixture
def mock_api():
    with patch('core.api.command_center.CommandCenterAPI') as mock:
        yield mock
```

## Writing Tests

### Python Tests
```python
def test_message_passing():
    comm_system = AgentCommunicationSystem()
    message = Message(
        message_id="test1",
        sender_id="agent1",
        receiver_id="agent2",
        message_type=MessageType.REQUEST,
        content={"test": "data"},
        timestamp=time.time()
    )
    comm_system.send_message(message)
    assert comm_system.get_message_count() == 1
```

### JavaScript Tests
```javascript
it('handles voice input', () => {
  renderWithProviders(<InputControls />);
  const voiceButton = screen.getByRole('button', { name: /voice input/i });
  fireEvent.click(voiceButton);
  expect(screen.getByText(/recording/i)).toBeInTheDocument();
});
```

## Test Coverage

The test suite aims for:
- 90% code coverage
- 100% critical path coverage
- Edge case testing
- Performance testing
- Integration testing

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Merges to main
- Nightly builds
- Release candidates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for your feature
4. Ensure all tests pass
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 