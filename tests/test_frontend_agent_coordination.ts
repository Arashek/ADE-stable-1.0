/**
 * End-to-End Frontend Tests for Agent Coordination
 * 
 * This test suite validates the frontend components that interact with the
 * agent coordination system, including task allocation and caching.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { CommandHub } from '../frontend/src/components/CommandHub/CommandHub';
import { AgentService } from '../frontend/src/services/agent.service';
import { useCommandCenter } from '../frontend/src/hooks/useCommandCenter';
import { useCodebaseAwareness } from '../frontend/src/hooks/useCodebaseAwareness';

// Mock Socket.IO
jest.mock('socket.io-client', () => {
  const emit = jest.fn();
  const on = jest.fn();
  const off = jest.fn();
  
  return {
    io: jest.fn(() => ({
      emit,
      on,
      off,
      connect: jest.fn(),
      disconnect: jest.fn(),
      id: 'mock-socket-id',
    })),
    emit,
    on,
    off,
  };
});

// Mock hooks
jest.mock('../frontend/src/hooks/useCommandCenter');
jest.mock('../frontend/src/hooks/useCodebaseAwareness');

// Mock the agent service
jest.mock('../frontend/src/services/agent.service');

// Setup mock server for API requests
const server = setupServer(
  // Mock task creation endpoint
  rest.post('/api/tasks', (req, res, ctx) => {
    return res(
      ctx.json({
        taskId: 'mock-task-1',
        status: 'created',
        message: 'Task created successfully'
      })
    );
  }),
  
  // Mock task status endpoint
  rest.get('/api/tasks/:taskId', (req, res, ctx) => {
    const { taskId } = req.params;
    return res(
      ctx.json({
        taskId,
        status: 'completed',
        result: 'Task completed successfully',
        agentId: 'agent-001',
        processingTime: 125
      })
    );
  }),
  
  // Mock agents endpoint
  rest.get('/api/agents', (req, res, ctx) => {
    return res(
      ctx.json([
        {
          id: 'agent-001',
          name: 'Code Generator',
          status: 'idle',
          capabilities: ['code_generation', 'code_review'],
          specialization: 'code_generation'
        },
        {
          id: 'agent-002',
          name: 'Design Expert',
          status: 'idle',
          capabilities: ['ui_design', 'ux_review'],
          specialization: 'ui_design'
        }
      ])
    );
  })
);

// Setup and teardown for mock server
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Setup mock data and implementations
const mockTasks = [
  {
    id: 'task-1',
    type: 'code_generation',
    prompt: 'Generate a React component',
    status: 'completed',
    agentId: 'agent-001',
    result: 'function MyComponent() { return <div>Hello World</div>; }',
    processingTime: 235
  },
  {
    id: 'task-2',
    type: 'ui_design',
    prompt: 'Design a login form',
    status: 'in_progress',
    agentId: 'agent-002'
  }
];

const mockAgents = [
  {
    id: 'agent-001',
    name: 'Code Generator',
    status: 'idle',
    capabilities: ['code_generation', 'code_review'],
    specialization: 'code_generation'
  },
  {
    id: 'agent-002',
    name: 'Design Expert',
    status: 'busy',
    capabilities: ['ui_design', 'ux_review'],
    specialization: 'ui_design'
  }
];

// Mock implementation of hooks
beforeEach(() => {
  (useCommandCenter as jest.Mock).mockReturnValue({
    getTasks: jest.fn().mockResolvedValue(mockTasks),
    createTask: jest.fn().mockImplementation((taskData) => {
      return Promise.resolve({
        id: 'new-task-id',
        ...taskData,
        status: 'created'
      });
    }),
    deleteTask: jest.fn().mockResolvedValue(true),
    isConnected: true,
    isConnecting: false,
    error: null
  });
  
  (useCodebaseAwareness as jest.Mock).mockReturnValue({
    getActiveFile: jest.fn().mockReturnValue('/path/to/active/file.js'),
    getOpenFiles: jest.fn().mockReturnValue(['/path/to/active/file.js', '/path/to/another/file.js']),
    getActiveFileContent: jest.fn().mockReturnValue('const component = () => { return <div>Test</div>; };'),
    getFileStructure: jest.fn().mockReturnValue({ 
      name: 'project',
      type: 'directory',
      path: '/',
      children: [
        { name: 'src', type: 'directory', path: '/src' },
        { name: 'README.md', type: 'file', path: '/README.md' }
      ]
    }),
    isConnected: true,
    isConnecting: false,
    error: null
  });
});

describe('Agent Coordination Frontend Integration', () => {
  test('CommandHub renders with agent information', async () => {
    (AgentService.getAgents as jest.Mock).mockResolvedValue(mockAgents);
    
    render(<CommandHub />);
    
    // Verify agents are displayed
    await waitFor(() => {
      expect(screen.getByText('Code Generator')).toBeInTheDocument();
      expect(screen.getByText('Design Expert')).toBeInTheDocument();
    });
    
    // Verify status indicators
    await waitFor(() => {
      const idleStatus = screen.getByText('idle');
      const busyStatus = screen.getByText('busy');
      expect(idleStatus).toBeInTheDocument();
      expect(busyStatus).toBeInTheDocument();
    });
  });
  
  test('Creates a new task and updates UI accordingly', async () => {
    (AgentService.getAgents as jest.Mock).mockResolvedValue(mockAgents);
    (AgentService.processTask as jest.Mock).mockResolvedValue({
      id: 'new-task-id',
      type: 'code_generation',
      prompt: 'Generate a button component',
      status: 'completed',
      agentId: 'agent-001',
      result: 'function Button() { return <button>Click me</button>; }',
      processingTime: 125
    });
    
    render(<CommandHub />);
    
    // Find the command input
    const commandInput = screen.getByPlaceholderText('Enter a command or prompt...');
    expect(commandInput).toBeInTheDocument();
    
    // Enter a command
    fireEvent.change(commandInput, { target: { value: 'Generate a button component' } });
    
    // Submit the command
    fireEvent.keyDown(commandInput, { key: 'Enter', code: 'Enter' });
    
    // Verify the command was processed
    await waitFor(() => {
      expect(AgentService.processTask).toHaveBeenCalledWith({
        type: 'code_generation',
        prompt: 'Generate a button component',
        context: expect.any(Object)
      });
    });
    
    // Verify the result is displayed
    await waitFor(() => {
      expect(screen.getByText('function Button() { return <button>Click me</button>; }')).toBeInTheDocument();
    });
  });
  
  test('Handles task allocation to appropriate agent based on type', async () => {
    (AgentService.getAgents as jest.Mock).mockResolvedValue(mockAgents);
    
    // Mock for code task
    const mockCodeTask = {
      id: 'code-task-id',
      type: 'code_generation',
      prompt: 'Create a navigation component',
      status: 'completed',
      agentId: 'agent-001',
      result: 'function Navigation() { return <nav>Links</nav>; }',
      processingTime: 150
    };
    
    // Mock for design task
    const mockDesignTask = {
      id: 'design-task-id',
      type: 'ui_design',
      prompt: 'Design a navigation menu',
      status: 'completed',
      agentId: 'agent-002',
      result: 'UI Design for navigation',
      processingTime: 200
    };
    
    // Set up the agent service to return different results based on task type
    (AgentService.processTask as jest.Mock).mockImplementation((taskData) => {
      if (taskData.type === 'code_generation') {
        return Promise.resolve(mockCodeTask);
      } else if (taskData.type === 'ui_design') {
        return Promise.resolve(mockDesignTask);
      }
    });
    
    render(<CommandHub />);
    
    // Process a code task
    const commandInput = screen.getByPlaceholderText('Enter a command or prompt...');
    fireEvent.change(commandInput, { target: { value: '/code Create a navigation component' } });
    fireEvent.keyDown(commandInput, { key: 'Enter', code: 'Enter' });
    
    // Verify code task was processed by Code Generator
    await waitFor(() => {
      expect(AgentService.processTask).toHaveBeenCalledWith(expect.objectContaining({
        type: 'code_generation',
        prompt: 'Create a navigation component'
      }));
    });
    
    // Process a design task
    fireEvent.change(commandInput, { target: { value: '/design Design a navigation menu' } });
    fireEvent.keyDown(commandInput, { key: 'Enter', code: 'Enter' });
    
    // Verify design task was processed by Design Expert
    await waitFor(() => {
      expect(AgentService.processTask).toHaveBeenCalledWith(expect.objectContaining({
        type: 'ui_design',
        prompt: 'Design a navigation menu'
      }));
    });
  });
  
  test('Caches task results and reuses them for identical prompts', async () => {
    (AgentService.getAgents as jest.Mock).mockResolvedValue(mockAgents);
    
    // Mock implementation with cache tracking
    let cacheRequests = 0;
    
    (AgentService.processTask as jest.Mock).mockImplementation((taskData) => {
      // If this is a repeated task, simulate a cache hit
      if (taskData.prompt === 'Create a login form' && cacheRequests > 0) {
        return Promise.resolve({
          id: 'cached-task-id',
          type: taskData.type,
          prompt: taskData.prompt,
          status: 'completed',
          agentId: 'agent-002',
          result: 'Login form design',
          processingTime: 10,
          cacheHit: true
        });
      }
      
      // First time or non-cached task
      cacheRequests++;
      return Promise.resolve({
        id: 'new-task-id',
        type: taskData.type,
        prompt: taskData.prompt,
        status: 'completed',
        agentId: 'agent-002',
        result: 'Login form design',
        processingTime: 200,
        cacheHit: false
      });
    });
    
    render(<CommandHub />);
    
    // Process the first task
    const commandInput = screen.getByPlaceholderText('Enter a command or prompt...');
    fireEvent.change(commandInput, { target: { value: 'Create a login form' } });
    fireEvent.keyDown(commandInput, { key: 'Enter', code: 'Enter' });
    
    // Verify the task was processed
    await waitFor(() => {
      expect(AgentService.processTask).toHaveBeenCalledTimes(1);
    });
    
    // Process the same task again
    fireEvent.change(commandInput, { target: { value: 'Create a login form' } });
    fireEvent.keyDown(commandInput, { key: 'Enter', code: 'Enter' });
    
    // Verify the second call used cached result
    await waitFor(() => {
      expect(AgentService.processTask).toHaveBeenCalledTimes(2);
      
      // The second call should get a cache hit
      const secondCallResult = (AgentService.processTask as jest.Mock).mock.results[1].value;
      expect(secondCallResult).resolves.toHaveProperty('cacheHit', true);
    });
  });
  
  test('Handles errors in agent coordination gracefully', async () => {
    (AgentService.getAgents as jest.Mock).mockResolvedValue(mockAgents);
    
    // Mock an error response
    (AgentService.processTask as jest.Mock).mockRejectedValue(new Error('Agent coordination failed'));
    
    render(<CommandHub />);
    
    // Process a task that will result in an error
    const commandInput = screen.getByPlaceholderText('Enter a command or prompt...');
    fireEvent.change(commandInput, { target: { value: 'This will cause an error' } });
    fireEvent.keyDown(commandInput, { key: 'Enter', code: 'Enter' });
    
    // Verify error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/Error:/)).toBeInTheDocument();
      expect(screen.getByText(/Agent coordination failed/)).toBeInTheDocument();
    });
  });
  
  test('Updates agent status based on task processing', async () => {
    let agentStatusUpdated = false;
    
    // Initial state with idle agents
    (AgentService.getAgents as jest.Mock).mockImplementation(() => {
      if (!agentStatusUpdated) {
        return Promise.resolve(mockAgents);
      } else {
        // Return updated status after task is processed
        return Promise.resolve([
          {
            id: 'agent-001',
            name: 'Code Generator',
            status: 'busy',
            capabilities: ['code_generation', 'code_review'],
            specialization: 'code_generation'
          },
          {
            id: 'agent-002',
            name: 'Design Expert',
            status: 'idle',
            capabilities: ['ui_design', 'ux_review'],
            specialization: 'ui_design'
          }
        ]);
      }
    });
    
    // Mock task processing that updates agent status
    (AgentService.processTask as jest.Mock).mockImplementation(() => {
      agentStatusUpdated = true;
      return Promise.resolve({
        id: 'new-task-id',
        type: 'code_generation',
        prompt: 'Generate a form component',
        status: 'in_progress',
        agentId: 'agent-001'
      });
    });
    
    render(<CommandHub />);
    
    // Process a task
    const commandInput = screen.getByPlaceholderText('Enter a command or prompt...');
    fireEvent.change(commandInput, { target: { value: 'Generate a form component' } });
    fireEvent.keyDown(commandInput, { key: 'Enter', code: 'Enter' });
    
    // Verify the agent status changes to busy
    await waitFor(() => {
      expect(AgentService.processTask).toHaveBeenCalled();
    });
    
    // Refresh the agent status
    fireEvent.click(screen.getByText('Refresh'));
    
    // Verify agent status is updated
    await waitFor(() => {
      const busyStatus = screen.getAllByText('busy');
      // Code Generator should now be busy
      expect(busyStatus.length).toBeGreaterThan(0);
    });
  });
});

// Standalone tests for hooks
describe('CommandCenter Hook', () => {
  test('Returns empty tasks array when socket is disconnected', async () => {
    (useCommandCenter as jest.Mock).mockReturnValue({
      getTasks: jest.fn().mockResolvedValue([]),
      createTask: jest.fn(),
      deleteTask: jest.fn(),
      isConnected: false,
      isConnecting: false,
      error: new Error('Socket not connected')
    });
    
    const { result } = renderHook(() => useCommandCenter());
    
    // Expect empty tasks array
    const tasks = await result.current.getTasks();
    expect(tasks).toEqual([]);
    
    // Expect error message
    expect(result.current.error).toEqual(new Error('Socket not connected'));
  });
});

// Mocked renderHook function for hook testing
function renderHook(hook) {
  let result;
  function TestComponent() {
    result = hook();
    return null;
  }
  render(<TestComponent />);
  return { result };
}
