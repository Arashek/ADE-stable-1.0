# Command Center

The Command Center is a powerful interface for monitoring and managing AI agents in the IDE. It provides real-time insights into agent status, system metrics, and project progress.

## Features

### Main Interface
- Split-panel layout with resizable panels
- Real-time agent status monitoring
- System metrics visualization
- Task and conversation management
- Notification system

### Mini-View
- Compact floating window
- Quick access to essential information
- Status indicators for all agents
- Active error notifications
- System metrics summary

### Agent Management
- Individual agent status monitoring
- Detailed agent information
- Task assignment and tracking
- Performance metrics
- Error handling and recovery

## Components

### CommandCenter
The main component that integrates all other components and manages the overall state.

### LeftPanel
Displays the list of available agents and their current status.

### RightPanel
Shows detailed information about the selected agent, including:
- Conversations
- Tasks
- Metrics
- Agent information

### MiniView
Provides a compact view of essential information that can be accessed from anywhere in the IDE.

## State Management

The Command Center uses Redux for state management, with the following main slices:
- Active agent selection
- Agent status tracking
- Notifications
- Conversations
- Tasks
- System metrics

## Usage

```jsx
import CommandCenter from './components/CommandCenter/CommandCenter';

// In your main app component
function App() {
  return (
    <div>
      <CommandCenter />
      {/* Other app components */}
    </div>
  );
}
```

## Props

### CommandCenter
No props required. The component manages its own state through Redux.

### LeftPanel
- `activeAgent`: Currently selected agent ID
- `onAgentSelect`: Callback for agent selection
- `agentStatus`: Object containing status for each agent
- `notifications`: Array of current notifications

### RightPanel
- `activeAgent`: Currently selected agent ID
- `agentStatus`: Object containing status for each agent
- `conversations`: Array of agent conversations
- `tasks`: Array of agent tasks
- `metrics`: Object containing system metrics

### MiniView
- `notifications`: Array of current notifications
- `agentStatus`: Object containing status for each agent
- `metrics`: Object containing system metrics
- `onExpand`: Callback for expanding to full view
- `onNotificationClick`: Callback for notification interaction

## Styling

The Command Center uses Material-UI's styling system and theme provider. Custom styles can be applied through the theme or by modifying the styled components.

## Testing

Run the test suite:
```bash
npm test src/components/CommandCenter/__tests__/CommandCenter.test.jsx
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 