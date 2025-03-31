import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { ThemeProvider } from '@mui/material/styles';
import CommandCenter from '../CommandCenter';
import commandCenterReducer from '../../../store/commandCenterSlice';
import theme from '../../../theme';

const createTestStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      commandCenter: commandCenterReducer,
    },
    preloadedState: {
      commandCenter: {
        activeAgent: null,
        agentStatus: {
          codeAnalysis: 'active',
          errorHandling: 'active',
          resourceManagement: 'active',
          taskPlanning: 'active',
        },
        notifications: [],
        conversations: [],
        tasks: [],
        metrics: {
          cpu: 45,
          memory: 60,
          disk: 30,
        },
        ...initialState,
      },
    },
  });
};

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

describe('CommandCenter', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('renders the command center with all components', () => {
    renderWithProviders(<CommandCenter />);
    
    // Check for main components
    expect(screen.getByText('Command Center')).toBeInTheDocument();
    expect(screen.getByText('Agents')).toBeInTheDocument();
    expect(screen.getByText('Code Analysis Agent')).toBeInTheDocument();
  });

  it('handles agent selection', () => {
    renderWithProviders(<CommandCenter />);
    
    const agentButton = screen.getByText('Code Analysis Agent');
    fireEvent.click(agentButton);
    
    expect(screen.getByText('Agent Information')).toBeInTheDocument();
  });

  it('displays notifications when they occur', () => {
    renderWithProviders(<CommandCenter />, {
      notifications: [
        {
          id: '1',
          type: 'error',
          message: 'Test error notification',
          timestamp: new Date().toISOString(),
        },
      ],
    });
    
    expect(screen.getByText('Test error notification')).toBeInTheDocument();
  });

  it('handles panel resizing', () => {
    renderWithProviders(<CommandCenter />);
    
    const resizeHandle = screen.getByRole('separator');
    fireEvent.mouseDown(resizeHandle);
    fireEvent.mouseMove(resizeHandle, { clientX: 400 });
    fireEvent.mouseUp(resizeHandle);
    
    // Check if the panel width has been updated
    const leftPanel = screen.getByRole('complementary');
    expect(leftPanel).toHaveStyle({ width: expect.any(String) });
  });

  it('collapses to mini-view when minimized', () => {
    renderWithProviders(<CommandCenter />);
    
    const minimizeButton = screen.getByRole('button', { name: /minimize/i });
    fireEvent.click(minimizeButton);
    
    expect(screen.getByText('Command Center')).toBeInTheDocument();
    expect(screen.getByText('Agent Status')).toBeInTheDocument();
  });

  it('expands from mini-view when clicked', () => {
    renderWithProviders(<CommandCenter />, {
      commandCenter: {
        isCollapsed: true,
      },
    });
    
    const expandButton = screen.getByRole('button', { name: /expand/i });
    fireEvent.click(expandButton);
    
    expect(screen.getByText('Agents')).toBeInTheDocument();
  });

  it('updates agent status periodically', () => {
    renderWithProviders(<CommandCenter />);
    
    act(() => {
      jest.advanceTimersByTime(5000);
    });
    
    // Check if agent status has been updated
    const agentStatuses = screen.getAllByText(/active|error|inactive/);
    expect(agentStatuses.length).toBeGreaterThan(4); // Initial 4 agents
  });

  it('displays metrics in the right panel', () => {
    renderWithProviders(<CommandCenter />);
    
    const agentButton = screen.getByText('Resource Management Agent');
    fireEvent.click(agentButton);
    
    const metricsTab = screen.getByRole('tab', { name: /metrics/i });
    fireEvent.click(metricsTab);
    
    expect(screen.getByText('System Metrics')).toBeInTheDocument();
  });

  it('handles notification clearing', () => {
    renderWithProviders(<CommandCenter />, {
      notifications: [
        {
          id: '1',
          type: 'error',
          message: 'Test error notification',
          timestamp: new Date().toISOString(),
        },
      ],
    });
    
    const notificationButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(notificationButton);
    
    expect(screen.queryByText('Test error notification')).not.toBeInTheDocument();
  });
}); 