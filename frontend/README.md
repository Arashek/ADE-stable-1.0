# ADE Platform Frontend

This is the frontend implementation of the ADE Platform, featuring a 3D code visualization system that provides real-time insights into the codebase structure and relationships.

## Features

### CodeAwarenessService

The `CodeAwarenessService` provides a 3D visualization of the codebase, enabling developers and AI agents to understand the relationships between different components, services, and systems.

#### Key Features

1. **3D Code Visualization**
   - Interactive 3D graph visualization of codebase structure
   - Real-time updates as code changes
   - Color-coded nodes for different types of code entities
   - Weighted edges showing relationships between components

2. **Code Analysis**
   - Automatic code structure analysis
   - Dependency tracking
   - Complexity metrics
   - Code coverage visualization

3. **Real-time Updates**
   - Live synchronization with code changes
   - WebSocket-based communication
   - Efficient update propagation

4. **Interactive Features**
   - Node selection and highlighting
   - Dependency path visualization
   - Metrics display
   - Zoom and pan controls

#### Node Types

- Components (Green)
- Services (Red)
- Frameworks (Blue)
- Systems (Yellow)
- Files (Magenta)
- Functions (Cyan)

#### Edge Types

- Imports (Green)
- Dependencies (Red)
- Inheritance (Blue)
- Composition (Yellow)

## Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Run tests:
   ```bash
   npm test
   ```

## Usage

```typescript
import { CodeAwarenessService } from './services/CodeAwarenessService';

// Initialize the service
const codeAwareness = new CodeAwarenessService({
  ws: socket,
  editor: monacoEditor,
  container: document.getElementById('code-visualization')
});

// Listen for node selection
codeAwareness.on('nodeSelected', (node) => {
  console.log('Selected node:', node);
});

// Get node information
const nodeInfo = codeAwareness.getNodeInfo('node-id');
const dependencies = codeAwareness.getNodeDependencies('node-id');
const metrics = codeAwareness.getNodeMetrics('node-id');
```

## Architecture

The service is built using:
- Three.js for 3D visualization
- Monaco Editor for code editing
- Socket.IO for real-time communication
- TypeScript for type safety

## Testing

The service includes comprehensive tests covering:
- Initialization and configuration
- Code analysis and updates
- Node selection and highlighting
- Dependency tracking
- Metrics calculation
- Resource cleanup

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 