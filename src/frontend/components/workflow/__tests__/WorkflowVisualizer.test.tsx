import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { WorkflowVisualizer } from '../WorkflowVisualizer';
import { WorkflowStatus, WorkflowResult, WorkflowStage } from '../../../../core/models/project/DevelopmentWorkflowManager';

describe('WorkflowVisualizer', () => {
  const mockStatus: WorkflowStatus = {
    status: 'idle',
    progress: 0,
    lastUpdated: new Date(),
    currentStage: undefined,
    activeStages: []
  };

  const mockResult: WorkflowResult = {
    success: true,
    stages: [
      {
        name: 'Build',
        status: 'success',
        duration: 1000,
        output: 'Build completed successfully',
        startTime: new Date(),
        endTime: new Date()
      },
      {
        name: 'Test',
        status: 'success',
        duration: 2000,
        output: 'Tests passed',
        startTime: new Date(),
        endTime: new Date()
      }
    ],
    summary: {
      passedTests: 10,
      totalTests: 10,
      coverage: 85,
      totalDuration: 3000,
      parallelExecutions: 1
    }
  };

  const mockOnStart = jest.fn();
  const mockOnStop = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders workflow status correctly', () => {
    render(
      <WorkflowVisualizer
        containerId="test-container"
        status={mockStatus}
        result={null}
        onStart={mockOnStart}
        onStop={mockOnStop}
      />
    );

    expect(screen.getByText('Workflow Status')).toBeInTheDocument();
    expect(screen.getByText('IDLE')).toBeInTheDocument();
    expect(screen.getByText('Progress: 0%')).toBeInTheDocument();
  });

  it('shows current stage when running', () => {
    const runningStatus: WorkflowStatus = {
      ...mockStatus,
      status: 'running',
      progress: 50,
      currentStage: 'Build'
    };

    render(
      <WorkflowVisualizer
        containerId="test-container"
        status={runningStatus}
        result={null}
        onStart={mockOnStart}
        onStop={mockOnStop}
      />
    );

    expect(screen.getByText('Current Stage: Build')).toBeInTheDocument();
    expect(screen.getByText('Progress: 50%')).toBeInTheDocument();
  });

  it('calls onStart when start button is clicked', () => {
    render(
      <WorkflowVisualizer
        containerId="test-container"
        status={mockStatus}
        result={null}
        onStart={mockOnStart}
        onStop={mockOnStop}
      />
    );

    fireEvent.click(screen.getByTitle('Start Workflow'));
    expect(mockOnStart).toHaveBeenCalledTimes(1);
  });

  it('calls onStop when stop button is clicked', () => {
    const runningStatus: WorkflowStatus = {
      ...mockStatus,
      status: 'running'
    };

    render(
      <WorkflowVisualizer
        containerId="test-container"
        status={runningStatus}
        result={null}
        onStart={mockOnStart}
        onStop={mockOnStop}
      />
    );

    fireEvent.click(screen.getByTitle('Stop Workflow'));
    expect(mockOnStop).toHaveBeenCalledTimes(1);
  });

  it('displays workflow results when available', () => {
    render(
      <WorkflowVisualizer
        containerId="test-container"
        status={mockStatus}
        result={mockResult}
        onStart={mockOnStart}
        onStop={mockOnStop}
      />
    );

    expect(screen.getByText('Workflow Results')).toBeInTheDocument();
    expect(screen.getByText('3.00s')).toBeInTheDocument(); // Total Duration
    expect(screen.getByText('1')).toBeInTheDocument(); // Parallel Executions
    expect(screen.getByText('85%')).toBeInTheDocument(); // Test Coverage
  });

  it('displays stage details when expanded', async () => {
    render(
      <WorkflowVisualizer
        containerId="test-container"
        status={mockStatus}
        result={mockResult}
        onStart={mockOnStart}
        onStop={mockOnStop}
      />
    );

    const expandButtons = screen.getAllByRole('button');
    fireEvent.click(expandButtons[0]);

    await waitFor(() => {
      expect(screen.getByText('Build completed successfully')).toBeInTheDocument();
    });
  });

  it('shows correct status colors', () => {
    const statuses: WorkflowStatus[] = [
      { ...mockStatus, status: 'completed' },
      { ...mockStatus, status: 'failed' },
      { ...mockStatus, status: 'running' }
    ];

    statuses.forEach(status => {
      const { container } = render(
        <WorkflowVisualizer
          containerId="test-container"
          status={status}
          result={null}
          onStart={mockOnStart}
          onStop={mockOnStop}
        />
      );

      const chip = container.querySelector('.MuiChip-root');
      expect(chip).toHaveStyle({
        backgroundColor: status.status === 'completed'
          ? 'rgb(46, 125, 50)'
          : status.status === 'failed'
          ? 'rgb(211, 47, 47)'
          : 'rgb(25, 118, 210)'
      });
    });
  });
}); 