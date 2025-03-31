import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { WorkflowContainer } from '../WorkflowContainer';
import { WorkflowStatus, WorkflowResult } from '../../../../core/models/project/DevelopmentWorkflowManager';

// Mock fetch
global.fetch = jest.fn();

describe('WorkflowContainer', () => {
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
      }
    ],
    summary: {
      passedTests: 10,
      totalTests: 10,
      coverage: 85,
      totalDuration: 1000,
      parallelExecutions: 0
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.setItem('token', 'test-token');
  });

  it('fetches initial data on mount', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockStatus) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockResult) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({}) });

    render(<WorkflowContainer containerId="test-container" />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(3);
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/workflow/test-container/status',
        expect.any(Object)
      );
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/workflow/test-container/result',
        expect.any(Object)
      );
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/workflow/test-container/config',
        expect.any(Object)
      );
    });
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: false })
      .mockResolvedValueOnce({ ok: false })
      .mockResolvedValueOnce({ ok: false });

    render(<WorkflowContainer containerId="test-container" />);

    await waitFor(() => {
      expect(screen.getByText('Failed to fetch workflow status')).toBeInTheDocument();
    });
  });

  it('starts workflow when start button is clicked', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockStatus) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockResult) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({}) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ message: 'Workflow started successfully' }) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ ...mockStatus, status: 'running' }) });

    render(<WorkflowContainer containerId="test-container" />);

    await waitFor(() => {
      expect(screen.getByTitle('Start Workflow')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTitle('Start Workflow'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/workflow/test-container/start',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token'
          })
        })
      );
    });
  });

  it('stops workflow when stop button is clicked', async () => {
    const runningStatus = { ...mockStatus, status: 'running' };
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(runningStatus) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockResult) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({}) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ message: 'Workflow stopped successfully' }) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ ...mockStatus, status: 'idle' }) });

    render(<WorkflowContainer containerId="test-container" />);

    await waitFor(() => {
      expect(screen.getByTitle('Stop Workflow')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTitle('Stop Workflow'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/workflow/test-container/stop',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token'
          })
        })
      );
    });
  });

  it('polls for updates when workflow is running', async () => {
    jest.useFakeTimers();

    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ ...mockStatus, status: 'running' }) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockResult) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({}) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ ...mockStatus, status: 'running' }) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockResult) });

    render(<WorkflowContainer containerId="test-container" />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });

    // Fast-forward timers
    jest.advanceTimersByTime(5000);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(5);
    });

    jest.useRealTimers();
  });

  it('stops polling when workflow is not running', async () => {
    jest.useFakeTimers();

    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ ...mockStatus, status: 'idle' }) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockResult) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({}) });

    render(<WorkflowContainer containerId="test-container" />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });

    // Fast-forward timers
    jest.advanceTimersByTime(5000);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(3); // No additional calls
    });

    jest.useRealTimers();
  });
}); 