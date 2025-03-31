import { Logger } from '../logging/Logger';

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

export class AlertManager {
  private alerts: Map<string, Alert>;
  private rules: Map<string, AlertRule>;
  private notificationQueue: AlertNotification[];
  private processingInterval: NodeJS.Timeout | null;

  constructor(
    private logger: Logger,
    private notificationInterval: number = 5000
  ) {
    this.alerts = new Map();
    this.rules = new Map();
    this.notificationQueue = [];
    this.processingInterval = null;
  }

  public async start(): Promise<void> {
    this.logger.info('Starting alert manager');
    
    // Start processing notifications
    this.processingInterval = setInterval(() => {
      this.processNotificationQueue();
    }, this.notificationInterval);
  }

  public async stop(): Promise<void> {
    this.logger.info('Stopping alert manager');
    
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
      this.processingInterval = null;
    }
  }

  public addRule(rule: AlertRule): void {
    this.rules.set(rule.id, rule);
    this.logger.info('Alert rule added', { ruleId: rule.id });
  }

  public removeRule(ruleId: string): void {
    this.rules.delete(ruleId);
    this.logger.info('Alert rule removed', { ruleId });
  }

  public getAlerts(filters?: {
    type?: Alert['type'];
    severity?: Alert['severity'];
    resolved?: boolean;
  }): Alert[] {
    let alerts = Array.from(this.alerts.values());

    if (filters) {
      alerts = alerts.filter(alert => {
        if (filters.type && alert.type !== filters.type) return false;
        if (filters.severity && alert.severity !== filters.severity) return false;
        if (filters.resolved !== undefined && alert.resolved !== filters.resolved) return false;
        return true;
      });
    }

    return alerts;
  }

  public resolveAlert(alertId: string): void {
    const alert = this.alerts.get(alertId);
    if (alert) {
      alert.resolved = true;
      alert.resolvedAt = new Date();
      this.logger.info('Alert resolved', { alertId });
    }
  }

  public evaluateMetric(metric: string, value: number): void {
    for (const rule of this.rules.values()) {
      if (!rule.enabled || rule.condition.metric !== metric) continue;

      const { threshold, operator } = rule.condition;
      if (threshold === undefined || operator === undefined) continue;

      let shouldTrigger = false;
      switch (operator) {
        case 'gt':
          shouldTrigger = value > threshold;
          break;
        case 'lt':
          shouldTrigger = value < threshold;
          break;
        case 'eq':
          shouldTrigger = value === threshold;
          break;
        case 'gte':
          shouldTrigger = value >= threshold;
          break;
        case 'lte':
          shouldTrigger = value <= threshold;
          break;
      }

      if (shouldTrigger) {
        this.createAlert({
          type: rule.type,
          severity: rule.severity,
          title: `Metric Alert: ${metric}`,
          message: `Metric ${metric} ${operator} ${threshold} (current value: ${value})`,
          source: metric,
          metadata: { value, threshold, operator }
        });
      }
    }
  }

  public createAlert(alert: Omit<Alert, 'id' | 'timestamp' | 'resolved'>): void {
    const newAlert: Alert = {
      ...alert,
      id: this.generateAlertId(),
      timestamp: new Date(),
      resolved: false
    };

    this.alerts.set(newAlert.id, newAlert);
    this.logger.info('Alert created', { alertId: newAlert.id });

    // Queue notification
    this.queueNotification(newAlert);
  }

  private generateAlertId(): string {
    return `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private queueNotification(alert: Alert): void {
    const notification: AlertNotification = {
      type: 'webhook', // Default to webhook, could be configured based on alert type/severity
      target: '/api/notifications', // Default endpoint
      payload: {
        alertId: alert.id,
        type: alert.type,
        severity: alert.severity,
        title: alert.title,
        message: alert.message,
        timestamp: alert.timestamp,
        source: alert.source,
        metadata: alert.metadata
      }
    };

    this.notificationQueue.push(notification);
  }

  private async processNotificationQueue(): Promise<void> {
    while (this.notificationQueue.length > 0) {
      const notification = this.notificationQueue.shift();
      if (!notification) continue;

      try {
        await this.sendNotification(notification);
      } catch (error) {
        this.logger.error('Failed to send notification', error as Error, {
          notification
        });
        // Requeue failed notification
        this.notificationQueue.push(notification);
      }
    }
  }

  private async sendNotification(notification: AlertNotification): Promise<void> {
    switch (notification.type) {
      case 'webhook':
        await this.sendWebhookNotification(notification);
        break;
      case 'email':
        await this.sendEmailNotification(notification);
        break;
      case 'slack':
        await this.sendSlackNotification(notification);
        break;
      case 'command':
        await this.executeCommand(notification);
        break;
    }
  }

  private async sendWebhookNotification(notification: AlertNotification): Promise<void> {
    // In a real implementation, this would make an HTTP request
    this.logger.info('Sending webhook notification', {
      target: notification.target,
      payload: notification.payload
    });
  }

  private async sendEmailNotification(notification: AlertNotification): Promise<void> {
    // In a real implementation, this would send an email
    this.logger.info('Sending email notification', {
      target: notification.target,
      payload: notification.payload
    });
  }

  private async sendSlackNotification(notification: AlertNotification): Promise<void> {
    // In a real implementation, this would send a Slack message
    this.logger.info('Sending Slack notification', {
      target: notification.target,
      payload: notification.payload
    });
  }

  private async executeCommand(notification: AlertNotification): Promise<void> {
    // In a real implementation, this would execute a system command
    this.logger.info('Executing command notification', {
      target: notification.target,
      payload: notification.payload
    });
  }
} 