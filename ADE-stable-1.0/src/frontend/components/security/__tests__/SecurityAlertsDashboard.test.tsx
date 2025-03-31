import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SecurityAlertsDashboard } from '../SecurityAlertsDashboard';
import { SecurityAlert, SecurityPattern } from '../../../../core/models/project/SecurityEventCorrelator';
import { SecurityEvent } from '../../../../core/models/project/SecurityAuditLogger';

describe('SecurityAlertsDashboard', () => {
  const mockAlerts: SecurityAlert[] = [
    {
      id: '1',
      patternId: 'multiple-failed-logins',
      severity: 'high',
      timestamp: new Date(),
      events: [
        {
          timestamp: new Date().toISOString(),
          eventType: 'AUTH_FAILURE',
          severity: 'high',
          action: 'Login attempt failed',
          details: 'Invalid credentials',
        },
      ],
      description: 'Multiple failed login attempts detected',
      recommendations: [
        'Implement account lockout policies',
        'Review authentication mechanisms',
      ],
    },
    {
      id: '2',
      patternId: 'privilege-escalation',
      severity: 'critical',
      timestamp: new Date(),
      events: [
        {
          timestamp: new Date().toISOString(),
          eventType: 'PRIVILEGE_CHANGE',
          severity: 'critical',
          action: 'Privilege change attempt',
          details: 'Attempt to gain root privileges',
        },
      ],
      description: 'Suspicious privilege escalation attempt detected',
      recommendations: [
        'Review user permissions',
        'Implement principle of least privilege',
      ],
    },
  ];

  const mockPatterns: SecurityPattern[] = [
    {
      id: 'multiple-failed-logins',
      name: 'Multiple Failed Login Attempts',
      description: 'Detects multiple failed login attempts',
      severity: 'high',
      events: ['AUTH_FAILURE'],
      timeWindow: 300000,
      threshold: 5,
      correlation: () => true,
    },
    {
      id: 'privilege-escalation',
      name: 'Privilege Escalation Attempt',
      description: 'Detects privilege escalation attempts',
      severity: 'critical',
      events: ['PRIVILEGE_CHANGE'],
      timeWindow: 60000,
      threshold: 2,
      correlation: () => true,
    },
  ];

  const mockEvents: SecurityEvent[] = [
    {
      timestamp: new Date().toISOString(),
      eventType: 'AUTH_FAILURE',
      severity: 'high',
      action: 'Login attempt failed',
      details: 'Invalid credentials',
    },
    {
      timestamp: new Date().toISOString(),
      eventType: 'PRIVILEGE_CHANGE',
      severity: 'critical',
      action: 'Privilege change attempt',
      details: 'Attempt to gain root privileges',
    },
  ];

  const mockOnClearAlerts = jest.fn();
  const mockOnDismissAlert = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the dashboard with alerts and patterns', () => {
    render(
      <SecurityAlertsDashboard
        alerts={mockAlerts}
        patterns={mockPatterns}
        events={mockEvents}
        onClearAlerts={mockOnClearAlerts}
        onDismissAlert={mockOnDismissAlert}
      />
    );

    // Check for main components
    expect(screen.getByText('Security Alerts Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Alert Summary')).toBeInTheDocument();
    expect(screen.getByText('Security Patterns')).toBeInTheDocument();
    expect(screen.getByText('Recent Alerts')).toBeInTheDocument();
    expect(screen.getByText('Recent Security Events')).toBeInTheDocument();

    // Check for alert counts
    expect(screen.getByText('2')).toBeInTheDocument(); // Total alerts
    expect(screen.getByText('1')).toBeInTheDocument(); // Critical alerts
    expect(screen.getByText('1')).toBeInTheDocument(); // High alerts
  });

  it('displays alert details in dialog when clicking an alert', async () => {
    render(
      <SecurityAlertsDashboard
        alerts={mockAlerts}
        patterns={mockPatterns}
        events={mockEvents}
        onClearAlerts={mockOnClearAlerts}
        onDismissAlert={mockOnDismissAlert}
      />
    );

    // Click the first alert
    const alertItem = screen.getByText('Multiple failed login attempts detected');
    fireEvent.click(alertItem);

    // Check for dialog content
    await waitFor(() => {
      expect(screen.getByText('Details')).toBeInTheDocument();
      expect(screen.getByText('Recommendations')).toBeInTheDocument();
      expect(screen.getByText('Related Events')).toBeInTheDocument();
      expect(screen.getByText('Implement account lockout policies')).toBeInTheDocument();
    });
  });

  it('calls onDismissAlert when dismissing an alert', async () => {
    render(
      <SecurityAlertsDashboard
        alerts={mockAlerts}
        patterns={mockPatterns}
        events={mockEvents}
        onClearAlerts={mockOnClearAlerts}
        onDismissAlert={mockOnDismissAlert}
      />
    );

    // Click the first alert
    const alertItem = screen.getByText('Multiple failed login attempts detected');
    fireEvent.click(alertItem);

    // Click dismiss button
    const dismissButton = screen.getByText('Dismiss Alert');
    fireEvent.click(dismissButton);

    // Check if onDismissAlert was called with correct ID
    expect(mockOnDismissAlert).toHaveBeenCalledWith('1');
  });

  it('calls onClearAlerts when clicking clear all button', () => {
    render(
      <SecurityAlertsDashboard
        alerts={mockAlerts}
        patterns={mockPatterns}
        events={mockEvents}
        onClearAlerts={mockOnClearAlerts}
        onDismissAlert={mockOnDismissAlert}
      />
    );

    // Click clear all button
    const clearButton = screen.getByText('Clear All');
    fireEvent.click(clearButton);

    // Check if onClearAlerts was called
    expect(mockOnClearAlerts).toHaveBeenCalled();
  });

  it('displays pattern summary with alert counts', () => {
    render(
      <SecurityAlertsDashboard
        alerts={mockAlerts}
        patterns={mockPatterns}
        events={mockEvents}
        onClearAlerts={mockOnClearAlerts}
        onDismissAlert={mockOnDismissAlert}
      />
    );

    // Check for pattern names and descriptions
    expect(screen.getByText('Multiple Failed Login Attempts')).toBeInTheDocument();
    expect(screen.getByText('Privilege Escalation Attempt')).toBeInTheDocument();
    expect(screen.getByText('Detects multiple failed login attempts')).toBeInTheDocument();
    expect(screen.getByText('Detects privilege escalation attempts')).toBeInTheDocument();
  });

  it('displays recent security events', () => {
    render(
      <SecurityAlertsDashboard
        alerts={mockAlerts}
        patterns={mockPatterns}
        events={mockEvents}
        onClearAlerts={mockOnClearAlerts}
        onDismissAlert={mockOnDismissAlert}
      />
    );

    // Check for event details
    expect(screen.getByText('Login attempt failed')).toBeInTheDocument();
    expect(screen.getByText('Privilege change attempt')).toBeInTheDocument();
    expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    expect(screen.getByText('Attempt to gain root privileges')).toBeInTheDocument();
  });
}); 