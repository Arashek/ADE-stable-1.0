import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { WorkflowDashboard } from '../WorkflowDashboard';
import { WorkflowConfig, WorkflowStatus, WorkflowResult } from '../../../../core/models/project/DevelopmentWorkflowManager';

const mockConfig: WorkflowConfig = {
  versionControl: {
    type: 'git',
    repository: 'https://github.com/test/repo',
    branch: 'main'
  },
  ci: {
    enabled: true,
    stages: ['build', 'test', 'lint'],
    testCommand: 'npm test',
    buildCommand: 'npm run build'
  },
  cd: {
    enabled: true,
    deploymentTargets: ['staging', 'production'],
    deploymentStrategy: 'rolling'
  },
  testing: {
    environment: 'development',
    coverageThreshold: 80,
    testSuites: ['unit', 'integration', 'e2e']
  }
};

const mockStatus: WorkflowStatus = {
  status: 'idle',
  progress: 0,
  lastUpdated: new Date()
};

const mockResult: WorkflowResult = {
  success: true,
  stages: [
    {
      name: 'Build',
      status: 'success',
      duration: 1000,
      output: 'Build completed successfully'
    },
    {
      name: 'Test',
      status: 'success',
      duration: 2000,
      output: 'All tests passed'
    }
  ],
  summary: {
    passedTests: 10,
    totalTests: 10,
    coverage: 85,
    deploymentStatus: 'completed'
  }
};

describe('WorkflowDashboard', () => {
  const mockOnStartWorkflow = jest.fn();
  const mockOnStopWorkflow = jest.fn();
  const mockOnRefresh = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the dashboard with initial state', () => {
    render(
      <WorkflowDashboard
        containerId="test-container"
        config={mockConfig}
        onStartWorkflow={mockOnStartWorkflow}
        onStopWorkflow={mockOnStopWorkflow}
        onRefresh={mockOnRefresh}
      />
    );

    // Check for main components
    expect(screen.getByText('Workflow Status')).toBeInTheDocument();
    expect(screen.getByText('Workflow Stages')).toBeInTheDocument();
    expect(screen.getByText('Workflow Summary')).toBeInTheDocument();
    expect(screen.getByText('Workflow Configuration')).toBeInTheDocument();

    // Check for action buttons
    expect(screen.getByTitle('Start Workflow')).toBeInTheDocument();
    expect(screen.getByTitle('Stop Workflow')).toBeInTheDocument();
    expect(screen.getByTitle('Refresh')).toBeInTheDocument();
  });

  it('displays workflow configuration correctly', () => {
    render(
      <WorkflowDashboard
        containerId="test-container"
        config={mockConfig}
        onStartWorkflow={mockOnStartWorkflow}
        onStopWorkflow={mockOnStopWorkflow}
        onRefresh={mockOnRefresh}
      />
    );

    // Check version control info
    expect(screen.getByText('https://github.com/test/repo')).toBeInTheDocument();
    expect(screen.getByText('main')).toBeInTheDocument();

    // Check CI/CD settings
    expect(screen.getByText('Yes')).toBeInTheDocument();
    expect(screen.getByText('rolling')).toBeInTheDocument();

    // Check testing configuration
    expect(screen.getByText('development')).toBeInTheDocument();
    expect(screen.getByText('80%')).toBeInTheDocument();
    expect(screen.getByText('unit')).toBeInTheDocument();
    expect(screen.getByText('integration')).toBeInTheDocument();
    expect(screen.getByText('e2e')).toBeInTheDocument();
  });

  it('handles workflow actions correctly', async () => {
    render(
      <WorkflowDashboard
        containerId="test-container"
        config={mockConfig}
        onStartWorkflow={mockOnStartWorkflow}
        onStopWorkflow={mockOnStopWorkflow}
        onRefresh={mockOnRefresh}
      />
    );

    // Test start workflow
    fireEvent.click(screen.getByTitle('Start Workflow'));
    await waitFor(() => {
      expect(mockOnStartWorkflow).toHaveBeenCalledTimes(1);
    });

    // Test stop workflow
    fireEvent.click(screen.getByTitle('Stop Workflow'));
    await waitFor(() => {
      expect(mockOnStopWorkflow).toHaveBeenCalledTimes(1);
    });

    // Test refresh
    fireEvent.click(screen.getByTitle('Refresh'));
    await waitFor(() => {
      expect(mockOnRefresh).toHaveBeenCalledTimes(1);
    });
  });

  it('displays workflow stages correctly', () => {
    render(
      <WorkflowDashboard
        containerId="test-container"
        config={mockConfig}
        onStartWorkflow={mockOnStartWorkflow}
        onStopWorkflow={mockOnStopWorkflow}
        onRefresh={mockOnRefresh}
      />
    );

    // Mock the result state
    const result = {
      success: true,
      stages: [
        {
          name: 'Build',
          status: 'success',
          duration: 1000,
          output: 'Build completed successfully'
        },
        {
          name: 'Test',
          status: 'failure',
          duration: 2000,
          output: 'Test failed: 5 tests failed'
        }
      ],
      summary: {
        passedTests: 5,
        totalTests: 10,
        coverage: 75,
        deploymentStatus: 'failed'
      }
    };

    // Update the component with the result
    const { rerender } = render(
      <WorkflowDashboard
        containerId="test-container"
        config={mockConfig}
        onStartWorkflow={mockOnStartWorkflow}
        onStopWorkflow={mockOnStopWorkflow}
        onRefresh={mockOnRefresh}
      />
    );

    // Check if stages are displayed
    expect(screen.getByText('Build')).toBeInTheDocument();
    expect(screen.getByText('Test')).toBeInTheDocument();
    expect(screen.getByText('1000ms')).toBeInTheDocument();
    expect(screen.getByText('2000ms')).toBeInTheDocument();
  });

  it('displays workflow summary correctly', () => {
    render(
      <WorkflowDashboard
        containerId="test-container"
        config={mockConfig}
        onStartWorkflow={mockOnStartWorkflow}
        onStopWorkflow={mockOnStopWorkflow}
        onRefresh={mockOnRefresh}
      />
    );

    // Mock the result state
    const result = {
      success: true,
      stages: [
        {
          name: 'Build',
          status: 'success',
          duration: 1000,
          output: 'Build completed successfully'
        }
      ],
      summary: {
        passedTests: 8,
        totalTests: 10,
        coverage: 85,
        deploymentStatus: 'completed'
      }
    };

    // Update the component with the result
    const { rerender } = render(
      <WorkflowDashboard
        containerId="test-container"
        config={mockConfig}
        onStartWorkflow={mockOnStartWorkflow}
        onStopWorkflow={mockOnStopWorkflow}
        onRefresh={mockOnRefresh}
      />
    );

    // Check if summary is displayed
    expect(screen.getByText('8 / 10 tests passed')).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument();
    expect(screen.getByText('COMPLETED')).toBeInTheDocument();
  });

  it('handles loading state correctly', async () => {
    render(
      <WorkflowDashboard
        containerId="test-container"
        config={mockConfig}
        onStartWorkflow={mockOnStartWorkflow}
        onStopWorkflow={mockOnStopWorkflow}
        onRefresh={mockOnRefresh}
      />
    );

    // Mock loading state
    const loading = true;

    // Update the component with loading state
    const { rerender } = render(
      <WorkflowDashboard
        containerId="test-container"
        config={mockConfig}
        onStartWorkflow={mockOnStartWorkflow}
        onStopWorkflow={mockOnStopWorkflow}
        onRefresh={mockOnRefresh}
      />
    );

    // Check if buttons are disabled during loading
    expect(screen.getByTitle('Start Workflow')).toBeDisabled();
    expect(screen.getByTitle('Stop Workflow')).toBeDisabled();
    expect(screen.getByTitle('Refresh')).toBeDisabled();
  });
}); 