# AIScriptExecutor Component

The `AIScriptExecutor` component provides a user interface for executing AI scripts with real-time feedback, command history, and environment variable management.

## Features

- Command execution with real-time output
- Command history with search and replay
- Command templates for quick execution
- Environment variable management
- Resource usage monitoring
- Error handling and display
- Responsive design

## Props

```typescript
interface AIScriptExecutorProps {
  onExecute: (command: string, env: Record<string, string>) => Promise<ExecutionResult>;
  onShowHistory: () => void;
  onShowTemplates: () => void;
  onShowEnvironment: () => void;
}
```

## Usage

```tsx
import { AIScriptExecutor } from './AIScriptExecutor';

function App() {
  const handleExecute = async (command: string, env: Record<string, string>) => {
    try {
      const response = await fetch('/api/ai/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'your-api-key'
        },
        body: JSON.stringify({ command, env })
      });
      return await response.json();
    } catch (error) {
      console.error('Execution error:', error);
      throw error;
    }
  };

  return (
    <AIScriptExecutor
      onExecute={handleExecute}
      onShowHistory={() => console.log('Show history')}
      onShowTemplates={() => console.log('Show templates')}
      onShowEnvironment={() => console.log('Show environment')}
    />
  );
}
```

## Component Structure

```
AIScriptExecutor/
├── index.tsx           # Main component
├── styles.ts          # Styled components
├── types.ts           # TypeScript interfaces
└── README.md          # Documentation
```

## Features in Detail

### Command Execution

- Real-time command input with validation
- Environment variable support
- Execution status display
- Output and error display
- Resource usage monitoring

### Command History

- Persistent storage of executed commands
- Search functionality
- Replay capability
- Filtering by status
- Pagination

### Command Templates

- Save frequently used commands
- Template categories
- Quick execution
- Template management (edit/delete)

### Environment Variables

- Add/remove environment variables
- Variable validation
- Secure storage
- Template-specific variables

## Styling

The component uses Material-UI components and custom styling:

```typescript
// Example styled component
const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  margin: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius
}));
```

## State Management

The component uses React hooks for state management:

```typescript
const [command, setCommand] = useState('');
const [history, setHistory] = useState<ExecutionResult[]>([]);
const [templates, setTemplates] = useState<ExecutionTemplate[]>([]);
const [envVars, setEnvVars] = useState<Record<string, string>>({});
```

## Error Handling

- Input validation
- API error handling
- Resource limit warnings
- Network error handling

## Performance Considerations

- Debounced search
- Paginated history
- Lazy loading of templates
- Optimized re-renders

## Testing

```typescript
describe('AIScriptExecutor', () => {
  it('executes commands successfully', async () => {
    // Test implementation
  });

  it('handles errors appropriately', async () => {
    // Test implementation
  });

  it('manages command history', () => {
    // Test implementation
  });
});
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This component is part of the AI Script Execution system and is licensed under the MIT License. 