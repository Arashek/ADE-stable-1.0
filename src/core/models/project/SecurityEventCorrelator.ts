import { SecurityEvent, SecurityEventType } from './SecurityAuditLogger';
import { Logger } from '../logging/Logger';

export interface SecurityPattern {
  id: string;
  name: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  events: SecurityEventType[];
  timeWindow: number; // in milliseconds
  threshold: number;
  correlation: (events: SecurityEvent[]) => boolean;
}

export interface SecurityAlert {
  id: string;
  patternId: string;
  severity: SecurityPattern['severity'];
  timestamp: Date;
  events: SecurityEvent[];
  description: string;
  recommendations: string[];
}

export class SecurityEventCorrelator {
  private logger: Logger;
  private patterns: SecurityPattern[];
  private alerts: SecurityAlert[];

  constructor() {
    this.logger = new Logger('SecurityEventCorrelator');
    this.patterns = this.initializePatterns();
    this.alerts = [];
  }

  analyzeEvents(events: SecurityEvent[]): SecurityAlert[] {
    const newAlerts: SecurityAlert[] = [];

    for (const pattern of this.patterns) {
      const relevantEvents = events.filter(event => 
        pattern.events.includes(event.eventType) &&
        new Date(event.timestamp).getTime() >= Date.now() - pattern.timeWindow
      );

      if (relevantEvents.length >= pattern.threshold && pattern.correlation(relevantEvents)) {
        const alert: SecurityAlert = {
          id: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          patternId: pattern.id,
          severity: pattern.severity,
          timestamp: new Date(),
          events: relevantEvents,
          description: this.generateAlertDescription(pattern, relevantEvents),
          recommendations: this.generateRecommendations(pattern, relevantEvents),
        };

        newAlerts.push(alert);
        this.alerts.push(alert);
      }
    }

    return newAlerts;
  }

  private initializePatterns(): SecurityPattern[] {
    return [
      {
        id: 'multiple-failed-logins',
        name: 'Multiple Failed Login Attempts',
        description: 'Detects multiple failed login attempts within a short time window',
        severity: 'high',
        events: ['AUTH_FAILURE' as SecurityEventType],
        timeWindow: 5 * 60 * 1000, // 5 minutes
        threshold: 5,
        correlation: (events) => {
          const failedAttempts = events.filter(e => e.details?.message?.includes('failed'));
          return failedAttempts.length >= 5;
        },
      },
      {
        id: 'privilege-escalation',
        name: 'Privilege Escalation Attempt',
        description: 'Detects attempts to gain elevated privileges',
        severity: 'critical',
        events: ['PRIVILEGE_CHANGE' as SecurityEventType, 'CAPABILITY_CHANGE' as SecurityEventType],
        timeWindow: 60 * 1000, // 1 minute
        threshold: 2,
        correlation: (events) => {
          const privilegeEvents = events.filter(e => 
            e.details?.message?.includes('privilege') || e.details?.message?.includes('capability')
          );
          return privilegeEvents.length >= 2;
        },
      },
      {
        id: 'suspicious-network-activity',
        name: 'Suspicious Network Activity',
        description: 'Detects unusual network activity patterns',
        severity: 'high',
        events: ['NETWORK_ACCESS' as SecurityEventType, 'PORT_SCAN' as SecurityEventType],
        timeWindow: 10 * 60 * 1000, // 10 minutes
        threshold: 3,
        correlation: (events) => {
          const networkEvents = events.filter(e => 
            e.details?.message?.includes('network') || e.details?.message?.includes('port')
          );
          return networkEvents.length >= 3;
        },
      },
      {
        id: 'file-system-tampering',
        name: 'File System Tampering',
        description: 'Detects unauthorized file system modifications',
        severity: 'high',
        events: ['FILE_ACCESS' as SecurityEventType, 'FILE_MODIFICATION' as SecurityEventType],
        timeWindow: 5 * 60 * 1000, // 5 minutes
        threshold: 4,
        correlation: (events) => {
          const fileEvents = events.filter(e => 
            e.details?.message?.includes('file') || e.details?.message?.includes('directory')
          );
          return fileEvents.length >= 4;
        },
      },
      {
        id: 'resource-exhaustion',
        name: 'Resource Exhaustion Attempt',
        description: 'Detects attempts to exhaust system resources',
        severity: 'medium',
        events: ['RESOURCE_USAGE' as SecurityEventType, 'MEMORY_USAGE' as SecurityEventType, 'CPU_USAGE' as SecurityEventType],
        timeWindow: 15 * 60 * 1000, // 15 minutes
        threshold: 5,
        correlation: (events) => {
          const resourceEvents = events.filter(e => 
            e.details?.message?.includes('resource') || 
            e.details?.message?.includes('memory') || 
            e.details?.message?.includes('cpu')
          );
          return resourceEvents.length >= 5;
        },
      },
    ];
  }

  private generateAlertDescription(pattern: SecurityPattern, events: SecurityEvent[]): string {
    switch (pattern.id) {
      case 'multiple-failed-logins':
        return `Multiple failed login attempts detected (${events.length} attempts in ${pattern.timeWindow / 1000} seconds)`;
      case 'privilege-escalation':
        return `Suspicious privilege escalation attempts detected (${events.length} events in ${pattern.timeWindow / 1000} seconds)`;
      case 'suspicious-network-activity':
        return `Unusual network activity detected (${events.length} events in ${pattern.timeWindow / 1000} seconds)`;
      case 'file-system-tampering':
        return `Unauthorized file system modifications detected (${events.length} events in ${pattern.timeWindow / 1000} seconds)`;
      case 'resource-exhaustion':
        return `Potential resource exhaustion attempts detected (${events.length} events in ${pattern.timeWindow / 1000} seconds)`;
      default:
        return `Security pattern detected: ${pattern.name}`;
    }
  }

  private generateRecommendations(pattern: SecurityPattern, events: SecurityEvent[]): string[] {
    switch (pattern.id) {
      case 'multiple-failed-logins':
        return [
          'Review and update authentication mechanisms',
          'Implement account lockout policies',
          'Enable two-factor authentication if not already enabled',
          'Review system logs for potential brute force attacks',
        ];
      case 'privilege-escalation':
        return [
          'Review user permissions and access controls',
          'Implement principle of least privilege',
          'Monitor and audit privilege changes',
          'Review system logs for unauthorized access attempts',
        ];
      case 'suspicious-network-activity':
        return [
          'Review network security policies',
          'Implement network segmentation',
          'Monitor and filter suspicious IP addresses',
          'Review firewall rules and access controls',
        ];
      case 'file-system-tampering':
        return [
          'Review file system permissions',
          'Implement file integrity monitoring',
          'Enable audit logging for sensitive directories',
          'Review and update access control lists',
        ];
      case 'resource-exhaustion':
        return [
          'Review resource limits and quotas',
          'Implement resource monitoring and alerts',
          'Review and optimize resource usage',
          'Consider implementing rate limiting',
        ];
      default:
        return ['Review security policies and configurations'];
    }
  }

  getAlerts(): SecurityAlert[] {
    return this.alerts;
  }

  getAlertsBySeverity(severity: SecurityPattern['severity']): SecurityAlert[] {
    return this.alerts.filter(alert => alert.severity === severity);
  }

  getAlertsByPattern(patternId: string): SecurityAlert[] {
    return this.alerts.filter(alert => alert.patternId === patternId);
  }

  clearAlerts(): void {
    this.alerts = [];
  }
} 