# Code Analysis and Collaboration Components

This directory contains React components for code analysis visualization, AI-powered insights, and real-time collaboration features.

## Components Overview

### CodeVisualization

A component that provides interactive visualization of code dependencies and metrics.

```typescript
import { CodeVisualization } from './visualization/CodeVisualization';

<CodeVisualization
  code={sourceCode}
  metrics={codeMetrics}
  dependencies={dependencyGraph}
/>
```

#### Props

- `code: string` - The source code to visualize
- `metrics: CodeMetrics` - Code quality metrics including complexity, maintainability, etc.
- `dependencies: DependencyGraph` - Graph structure of code dependencies

#### Features

- Interactive force-directed graph visualization
- Color-coded nodes based on code quality metrics
- Real-time metrics display with progress indicators
- Performance metrics visualization
- Responsive layout for different screen sizes

### CodeInsight

A component that displays AI-powered code suggestions and improvements.

```typescript
import { CodeInsight } from './insights/CodeInsight';

<CodeInsight
  code={sourceCode}
  context={codeContext}
  suggestions={aiSuggestions}
  onApply={handleApplySuggestion}
/>
```

#### Props

- `code: string` - The source code to analyze
- `context: CodeContext` - Context information about the code
- `suggestions: AISuggestion[]` - Array of AI-generated suggestions
- `onApply: (suggestion: AISuggestion) => void` - Callback when applying a suggestion

#### Features

- Split view with code and suggestions
- Syntax highlighting for code snippets
- Collapsible suggestion cards
- Color-coded suggestion types
- One-click suggestion application
- Support for multiple programming languages

### CollaborationPanel

A component that enables real-time collaboration features.

```typescript
import { CollaborationPanel } from './collaboration/CollaborationPanel';

<CollaborationPanel
  projectId={projectId}
  users={activeUsers}
  changes={codeChanges}
/>
```

#### Props

- `projectId: string` - Unique identifier for the project
- `users: User[]` - Array of users currently in the project
- `changes: CodeChange[]` - Array of code changes in the project

#### Features

- Real-time user presence indicators
- Active users list with status badges
- Change history timeline
- Integrated chat panel
- File editing indicators
- Diff previews for changes

## Usage Examples

### Basic Setup

```typescript
import { CodeVisualization, CodeInsight, CollaborationPanel } from './components';

function CodeAnalysisPage() {
  return (
    <div>
      <CodeVisualization
        code={sourceCode}
        metrics={metrics}
        dependencies={dependencies}
      />
      <CodeInsight
        code={sourceCode}
        context={context}
        suggestions={suggestions}
        onApply={handleApply}
      />
      <CollaborationPanel
        projectId={projectId}
        users={users}
        changes={changes}
      />
    </div>
  );
}
```

### Theme Integration

All components support Material-UI theming:

```typescript
import { ThemeProvider, createTheme } from '@mui/material';

const theme = createTheme({
  // Your theme configuration
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CodeAnalysisPage />
    </ThemeProvider>
  );
}
```

## Best Practices

1. **Performance**
   - Use memoization for expensive computations
   - Implement virtualization for large lists
   - Optimize graph rendering for large codebases

2. **Accessibility**
   - All components include ARIA labels
   - Support keyboard navigation
   - Provide high contrast modes
   - Screen reader friendly

3. **Responsiveness**
   - Components adapt to different screen sizes
   - Mobile-friendly interactions
   - Flexible layouts

4. **Error Handling**
   - Graceful degradation when services are unavailable
   - Clear error messages
   - Fallback UI states

## Testing

Run the test suite:

```bash
npm test
```

Test files are located in `__tests__` directories alongside components.

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass
5. Submit a pull request 