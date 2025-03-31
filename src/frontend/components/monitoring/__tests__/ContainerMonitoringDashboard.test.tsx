import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ContainerMonitoringDashboard } from '../ContainerMonitoringDashboard';
import { ContainerMetrics, HealthStatus, Alert } from '../../../../core/monitoring/types';

describe('ContainerMonitoringDashboard', () => {
  const mockMetrics: ContainerMetrics = {
    cpu: {
      usage: 75,
      limit: 100,
      cores: 2
    },
    memory: {
      usage: 60,
      limit: 1024 * 1024 * 1024,
      swap: 0
    },
    network: {
      rxBytes: 1024 * 1024,
      txBytes: 1024 * 1024,
      rxPackets: 1000,
      txPackets: 1000
    },
    disk: {
      usage: 85,
      limit: 1024 * 1024 * 1024 * 10,
      iops: {
        read: 100,
        write: 100
      }
    }
  };

  const mockHealthStatus: HealthStatus = {
    status: 'healthy',
    checks: {
      'liveness': {
        status: 'pass',
        lastCheck: new Date(),
        consecutiveFailures: 0,
        consecutiveSuccesses: 5
      },
      'readiness': {
        status: 'pass',
        lastCheck: new Date(),
        consecutiveFailures: 0,
        consecutiveSuccesses: 5
      }
    },
    lastUpdated: new Date()
  };

  const mockAlerts: Alert[] = [
    {
      id: '1',
      type: 'resource',
      severity: 'high',
      title: 'High CPU Usage',
      message: 'CPU usage is above 80%',
      timestamp: new Date(),
      source: 'cpu',
      metadata: { value: 85, threshold: 80 }
    },
    {
      id: '2',
      type: 'health',
      severity: 'critical',
      title: 'Health Check Failed',
      message: 'Liveness check failed',
      timestamp: new Date(),
      source: 'liveness',
      metadata: { check: 'liveness', error: 'Connection timeout' }
    }
  ];

  const mockOnRefresh = jest.fn();
  const mockOnResolveAlert = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders container monitoring dashboard', () => {
    render(
      <ContainerMonitoringDashboard
        containerId="test-container"
        metrics={mockMetrics}
        healthStatus={mockHealthStatus}
        alerts={mockAlerts}
        onRefresh={mockOnRefresh}
        onResolveAlert={mockOnResolveAlert}
      />
    );

    expect(screen.getByText('Container Monitoring')).toBeInTheDocument();
    expect(screen.getByText('Health Status')).toBeInTheDocument();
    expect(screen.getByText('Active Alerts')).toBeInTheDocument();
  });

  it('displays health status correctly', () => {
    render(
      <ContainerMonitoringDashboard
        containerId="test-container"
        metrics={mockMetrics}
        healthStatus={mockHealthStatus}
        alerts={mockAlerts}
        onRefresh={mockOnRefresh}
        onResolveAlert={mockOnResolveAlert}
      />
    );

    expect(screen.getByText('HEALTHY')).toBeInTheDocument();
    expect(screen.getByText('liveness')).toBeInTheDocument();
    expect(screen.getByText('readiness')).toBeInTheDocument();
  });

  it('displays metrics correctly', () => {
    render(
      <ContainerMonitoringDashboard
        containerId="test-container"
        metrics={mockMetrics}
        healthStatus={mockHealthStatus}
        alerts={mockAlerts}
        onRefresh={mockOnRefresh}
        onResolveAlert={mockOnResolveAlert}
      />
    );

    expect(screen.getByText('75.0 %')).toBeInTheDocument(); // CPU Usage
    expect(screen.getByText('60.0 %')).toBeInTheDocument(); // Memory Usage
    expect(screen.getByText('85.0 %')).toBeInTheDocument(); // Disk Usage
    expect(screen.getByText('2.0 MB/s')).toBeInTheDocument(); // Network I/O
  });

  it('displays alerts correctly', () => {
    render(
      <ContainerMonitoringDashboard
        containerId="test-container"
        metrics={mockMetrics}
        healthStatus={mockHealthStatus}
        alerts={mockAlerts}
        onRefresh={mockOnRefresh}
        onResolveAlert={mockOnResolveAlert}
      />
    );

    expect(screen.getByText('High CPU Usage')).toBeInTheDocument();
    expect(screen.getByText('Health Check Failed')).toBeInTheDocument();
  });

  it('calls onResolveAlert when alert is resolved', () => {
    render(
      <ContainerMonitoringDashboard
        containerId="test-container"
        metrics={mockMetrics}
        healthStatus={mockHealthStatus}
        alerts={mockAlerts}
        onRefresh={mockOnRefresh}
        onResolveAlert={mockOnResolveAlert}
      />
    );

    const resolveButtons = screen.getAllByRole('button', { name: /resolve/i });
    fireEvent.click(resolveButtons[0]);

    expect(mockOnResolveAlert).toHaveBeenCalledWith('1');
  });

  it('toggles auto-refresh when refresh button is clicked', () => {
    jest.useFakeTimers();

    render(
      <ContainerMonitoringDashboard
        containerId="test-container"
        metrics={mockMetrics}
        healthStatus={mockHealthStatus}
        alerts={mockAlerts}
        onRefresh={mockOnRefresh}
        onResolveAlert={mockOnResolveAlert}
      />
    );

    const refreshButton = screen.getByRole('button', { name: /auto-refresh enabled/i });
    fireEvent.click(refreshButton);

    expect(screen.getByRole('button', { name: /auto-refresh disabled/i })).toBeInTheDocument();

    // Fast-forward timers
    jest.advanceTimersByTime(30000);

    expect(mockOnRefresh).not.toHaveBeenCalled();

    jest.useRealTimers();
  });

  it('refreshes data automatically when auto-refresh is enabled', () => {
    jest.useFakeTimers();

    render(
      <ContainerMonitoringDashboard
        containerId="test-container"
        metrics={mockMetrics}
        healthStatus={mockHealthStatus}
        alerts={mockAlerts}
        onRefresh={mockOnRefresh}
        onResolveAlert={mockOnResolveAlert}
      />
    );

    // Fast-forward timers
    jest.advanceTimersByTime(30000);

    expect(mockOnRefresh).toHaveBeenCalled();

    jest.useRealTimers();
  });

  it('displays "No active alerts" when there are no unresolved alerts', () => {
    const resolvedAlerts = mockAlerts.map(alert => ({ ...alert, resolved: true }));

    render(
      <ContainerMonitoringDashboard
        containerId="test-container"
        metrics={mockMetrics}
        healthStatus={mockHealthStatus}
        alerts={resolvedAlerts}
        onRefresh={mockOnRefresh}
        onResolveAlert={mockOnResolveAlert}
      />
    );

    expect(screen.getByText('No active alerts')).toBeInTheDocument();
  });
}); 