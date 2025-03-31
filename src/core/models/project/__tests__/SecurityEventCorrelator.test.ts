import { SecurityEventCorrelator } from '../SecurityEventCorrelator';
import { SecurityEvent, SecurityEventType } from '../SecurityEvent';
import { Logger } from '../../../logging/Logger';

jest.mock('../../../logging/Logger');

describe('SecurityEventCorrelator', () => {
  let correlator: SecurityEventCorrelator;
  let mockLogger: jest.Mocked<Logger>;

  beforeEach(() => {
    mockLogger = new Logger() as jest.Mocked<Logger>;
    correlator = new SecurityEventCorrelator();
  });

  describe('analyzeEvents', () => {
    it('should detect multiple failed login attempts', () => {
      const events: SecurityEvent[] = [
        {
          eventType: SecurityEventType.USER_ACCESS,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Login attempt failed',
          details: { message: 'Login failed for user admin' },
          severity: 'high'
        },
        {
          eventType: SecurityEventType.USER_ACCESS,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Login attempt failed',
          details: { message: 'Login failed for user admin' },
          severity: 'high'
        },
        {
          eventType: SecurityEventType.USER_ACCESS,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Login attempt failed',
          details: { message: 'Login failed for user admin' },
          severity: 'high'
        },
        {
          eventType: SecurityEventType.USER_ACCESS,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Login attempt failed',
          details: { message: 'Login failed for user admin' },
          severity: 'high'
        },
        {
          eventType: SecurityEventType.USER_ACCESS,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Login attempt failed',
          details: { message: 'Login failed for user admin' },
          severity: 'high'
        }
      ];

      const alerts = correlator.analyzeEvents(events);
      expect(alerts).toHaveLength(1);
      expect(alerts[0].patternId).toBe('multiple-failed-logins');
      expect(alerts[0].recommendations).toContain('Implement account lockout policies');
    });

    it('should detect privilege escalation attempts', () => {
      const events: SecurityEvent[] = [
        {
          eventType: SecurityEventType.PERMISSION_CHANGE,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Privilege change attempt',
          details: { message: 'User attempted to gain root privileges' },
          severity: 'critical'
        },
        {
          eventType: SecurityEventType.CAPABILITY_CHANGE,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Capability change attempt',
          details: { message: 'User attempted to add capabilities' },
          severity: 'critical'
        }
      ];

      const alerts = correlator.analyzeEvents(events);
      expect(alerts).toHaveLength(1);
      expect(alerts[0].patternId).toBe('privilege-escalation');
      expect(alerts[0].recommendations).toContain('Implement principle of least privilege');
    });

    it('should detect suspicious network activity', () => {
      const events: SecurityEvent[] = [
        {
          eventType: SecurityEventType.NETWORK_CHANGE,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Suspicious network connection',
          details: { message: 'Multiple connection attempts detected' },
          severity: 'high'
        },
        {
          eventType: SecurityEventType.SECURITY_VIOLATION,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Port scanning',
          details: { message: 'Port scanning detected' },
          severity: 'high'
        },
        {
          eventType: SecurityEventType.NETWORK_CHANGE,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Suspicious network connection',
          details: { message: 'Suspicious network activity detected' },
          severity: 'high'
        }
      ];

      const alerts = correlator.analyzeEvents(events);
      expect(alerts).toHaveLength(1);
      expect(alerts[0].patternId).toBe('suspicious-network-activity');
      expect(alerts[0].recommendations).toContain('Implement network segmentation');
    });

    it('should detect file system tampering', () => {
      const events: SecurityEvent[] = [
        {
          eventType: SecurityEventType.SECURITY_VIOLATION,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Unauthorized file access',
          details: { message: 'Unauthorized file access detected' },
          severity: 'high'
        },
        {
          eventType: SecurityEventType.SECURITY_VIOLATION,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Unauthorized file modification',
          details: { message: 'System file modification detected' },
          severity: 'high'
        },
        {
          eventType: SecurityEventType.SECURITY_VIOLATION,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Unauthorized file access',
          details: { message: 'Suspicious file access pattern detected' },
          severity: 'high'
        },
        {
          eventType: SecurityEventType.SECURITY_VIOLATION,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Unauthorized file modification',
          details: { message: 'Critical file modification detected' },
          severity: 'high'
        }
      ];

      const alerts = correlator.analyzeEvents(events);
      expect(alerts).toHaveLength(1);
      expect(alerts[0].patternId).toBe('file-system-tampering');
      expect(alerts[0].recommendations).toContain('Implement file integrity monitoring');
    });

    it('should detect resource exhaustion attempts', () => {
      const events: SecurityEvent[] = [
        {
          eventType: SecurityEventType.RESOURCE_LIMIT,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'High resource usage',
          details: { message: 'High resource usage detected' },
          severity: 'medium'
        },
        {
          eventType: SecurityEventType.RESOURCE_LIMIT,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'High memory usage',
          details: { message: 'Memory usage exceeded threshold' },
          severity: 'medium'
        },
        {
          eventType: SecurityEventType.RESOURCE_LIMIT,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'High CPU usage',
          details: { message: 'CPU usage exceeded threshold' },
          severity: 'medium'
        },
        {
          eventType: SecurityEventType.RESOURCE_LIMIT,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Resource exhaustion attempt',
          details: { message: 'Resource exhaustion attempt detected' },
          severity: 'medium'
        },
        {
          eventType: SecurityEventType.RESOURCE_LIMIT,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Critical memory usage',
          details: { message: 'Critical memory usage detected' },
          severity: 'medium'
        }
      ];

      const alerts = correlator.analyzeEvents(events);
      expect(alerts).toHaveLength(1);
      expect(alerts[0].patternId).toBe('resource-exhaustion');
      expect(alerts[0].recommendations).toContain('Implement resource monitoring and alerts');
    });

    it('should not generate alerts for events outside time window', () => {
      const events: SecurityEvent[] = [
        {
          eventType: SecurityEventType.USER_ACCESS,
          timestamp: new Date(Date.now() - 6 * 60 * 1000).toISOString(), // 6 minutes ago
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Login attempt failed',
          details: { message: 'Login failed for user admin' },
          severity: 'high'
        },
        {
          eventType: SecurityEventType.USER_ACCESS,
          timestamp: new Date(Date.now() - 7 * 60 * 1000).toISOString(), // 7 minutes ago
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Login attempt failed',
          details: { message: 'Login failed for user admin' },
          severity: 'high'
        }
      ];

      const alerts = correlator.analyzeEvents(events);
      expect(alerts).toHaveLength(0);
    });
  });

  describe('getAlerts', () => {
    beforeEach(() => {
      const events: SecurityEvent[] = [
        {
          eventType: SecurityEventType.USER_ACCESS,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Login attempt failed',
          details: { message: 'Login failed for user admin' },
          severity: 'high'
        },
        {
          eventType: SecurityEventType.PERMISSION_CHANGE,
          timestamp: new Date().toISOString(),
          containerId: 'container-1',
          userId: 'user-1',
          action: 'Privilege change attempt',
          details: { message: 'User attempted to gain root privileges' },
          severity: 'critical'
        }
      ];

      correlator.analyzeEvents(events);
    });

    it('should return all alerts', () => {
      const alerts = correlator.getAlerts();
      expect(alerts).toHaveLength(2);
    });

    it('should return alerts by severity', () => {
      const criticalAlerts = correlator.getAlerts().filter(alert => alert.severity === 'critical');
      expect(criticalAlerts).toHaveLength(1);
      expect(criticalAlerts[0].patternId).toBe('privilege-escalation');
    });

    it('should return alerts by pattern', () => {
      const loginAlerts = correlator.getAlerts().filter(alert => alert.patternId === 'multiple-failed-logins');
      expect(loginAlerts).toHaveLength(1);
    });

    it('should clear alerts', () => {
      correlator.clearAlerts();
      const alerts = correlator.getAlerts();
      expect(alerts).toHaveLength(0);
    });
  });
}); 