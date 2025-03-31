export interface ContainerMetrics {
  cpu: {
    usage: number;
    limit: number;
    cores: number;
  };
  memory: {
    usage: number;
    limit: number;
    swap: number;
  };
  network: {
    rxBytes: number;
    txBytes: number;
    rxPackets: number;
    txPackets: number;
  };
  disk: {
    usage: number;
    limit: number;
    iops: {
      read: number;
      write: number;
    };
  };
}

export interface HealthCheck {
  name: string;
  type: 'liveness' | 'readiness' | 'startup';
  command: string;
  interval: number;
  timeout: number;
  retries: number;
  failureThreshold: number;
  successThreshold: number;
}

export interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'degraded';
  checks: {
    [key: string]: {
      status: 'pass' | 'fail' | 'unknown';
      lastCheck: Date;
      lastError?: string;
      consecutiveFailures: number;
      consecutiveSuccesses: number;
    };
  };
  lastUpdated: Date;
}

export interface Alert {
  id: string;
  type: 'health' | 'resource' | 'security' | 'workflow';
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  message: string;
  timestamp: Date;
  source: string;
  metadata?: Record<string, any>;
  resolved?: boolean;
  resolvedAt?: Date;
}

export interface AlertRule {
  id: string;
  type: Alert['type'];
  severity: Alert['severity'];
  condition: {
    metric?: string;
    threshold?: number;
    operator?: 'gt' | 'lt' | 'eq' | 'gte' | 'lte';
    duration?: number;
    frequency?: number;
  };
  action: {
    type: 'notification' | 'webhook' | 'command';
    target: string;
    payload?: Record<string, any>;
  };
  enabled: boolean;
}

export interface AlertNotification {
  type: 'email' | 'slack' | 'webhook' | 'command';
  target: string;
  payload: Record<string, any>;
} 