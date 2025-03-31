import { Logger } from '../logging/Logger';
import { Container } from '../models/project/Container';

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

export class ContainerMonitor {
  private metrics: Map<string, ContainerMetrics>;
  private healthStatus: Map<string, HealthStatus>;
  private checkIntervals: Map<string, NodeJS.Timeout[]>;
  private alertThresholds: {
    cpu: number;
    memory: number;
    disk: number;
  };

  constructor(
    private container: Container,
    private logger: Logger,
    private healthChecks: HealthCheck[] = []
  ) {
    this.metrics = new Map();
    this.healthStatus = new Map();
    this.checkIntervals = new Map();
    this.alertThresholds = {
      cpu: 80, // 80% CPU usage threshold
      memory: 85, // 85% memory usage threshold
      disk: 90 // 90% disk usage threshold
    };

    // Initialize default health checks if none provided
    if (healthChecks.length === 0) {
      this.healthChecks = [
        {
          name: 'liveness',
          type: 'liveness',
          command: 'curl -f http://localhost:8080/health || exit 1',
          interval: 30000,
          timeout: 5000,
          retries: 3,
          failureThreshold: 3,
          successThreshold: 1
        },
        {
          name: 'readiness',
          type: 'readiness',
          command: 'curl -f http://localhost:8080/ready || exit 1',
          interval: 10000,
          timeout: 3000,
          retries: 2,
          failureThreshold: 2,
          successThreshold: 1
        }
      ];
    }
  }

  public async startMonitoring(): Promise<void> {
    this.logger.info('Starting container monitoring');
    
    // Start metrics collection
    await this.startMetricsCollection();
    
    // Start health checks
    await this.startHealthChecks();
    
    // Start alert monitoring
    this.startAlertMonitoring();
  }

  public async stopMonitoring(): Promise<void> {
    this.logger.info('Stopping container monitoring');
    
    // Clear all intervals
    for (const intervals of this.checkIntervals.values()) {
      intervals.forEach(interval => clearInterval(interval));
    }
    this.checkIntervals.clear();
  }

  public getMetrics(containerId: string): ContainerMetrics | undefined {
    return this.metrics.get(containerId);
  }

  public getHealthStatus(containerId: string): HealthStatus | undefined {
    return this.healthStatus.get(containerId);
  }

  private async startMetricsCollection(): Promise<void> {
    const interval = setInterval(async () => {
      try {
        const metrics = await this.collectMetrics();
        this.metrics.set(this.container.id, metrics);
        this.logger.debug('Container metrics collected', { containerId: this.container.id, metrics });
      } catch (error) {
        this.logger.error('Failed to collect container metrics', { error });
      }
    }, 15000); // Collect metrics every 15 seconds

    this.checkIntervals.set(this.container.id, [interval]);
  }

  private async startHealthChecks(): Promise<void> {
    for (const check of this.healthChecks) {
      const interval = setInterval(async () => {
        try {
          await this.runHealthCheck(check);
        } catch (error) {
          this.logger.error(`Health check failed: ${check.name}`, { error });
        }
      }, check.interval);

      if (!this.checkIntervals.has(this.container.id)) {
        this.checkIntervals.set(this.container.id, []);
      }
      this.checkIntervals.get(this.container.id)!.push(interval);
    }
  }

  private startAlertMonitoring(): void {
    const interval = setInterval(() => {
      const metrics = this.metrics.get(this.container.id);
      if (!metrics) return;

      // Check CPU usage
      if (metrics.cpu.usage > this.alertThresholds.cpu) {
        this.logger.warn('High CPU usage detected', {
          containerId: this.container.id,
          usage: metrics.cpu.usage,
          threshold: this.alertThresholds.cpu
        });
      }

      // Check memory usage
      if (metrics.memory.usage > this.alertThresholds.memory) {
        this.logger.warn('High memory usage detected', {
          containerId: this.container.id,
          usage: metrics.memory.usage,
          threshold: this.alertThresholds.memory
        });
      }

      // Check disk usage
      if (metrics.disk.usage > this.alertThresholds.disk) {
        this.logger.warn('High disk usage detected', {
          containerId: this.container.id,
          usage: metrics.disk.usage,
          threshold: this.alertThresholds.disk
        });
      }
    }, 60000); // Check alerts every minute

    if (!this.checkIntervals.has(this.container.id)) {
      this.checkIntervals.set(this.container.id, []);
    }
    this.checkIntervals.get(this.container.id)!.push(interval);
  }

  private async collectMetrics(): Promise<ContainerMetrics> {
    // In a real implementation, this would use container runtime APIs
    // For now, we'll return mock data
    return {
      cpu: {
        usage: Math.random() * 100,
        limit: 100,
        cores: 2
      },
      memory: {
        usage: Math.random() * 100,
        limit: 1024 * 1024 * 1024, // 1GB
        swap: 0
      },
      network: {
        rxBytes: Math.random() * 1000000,
        txBytes: Math.random() * 1000000,
        rxPackets: Math.random() * 1000,
        txPackets: Math.random() * 1000
      },
      disk: {
        usage: Math.random() * 100,
        limit: 1024 * 1024 * 1024 * 10, // 10GB
        iops: {
          read: Math.random() * 1000,
          write: Math.random() * 1000
        }
      }
    };
  }

  private async runHealthCheck(check: HealthCheck): Promise<void> {
    const currentStatus = this.healthStatus.get(this.container.id) || {
      status: 'unknown',
      checks: {},
      lastUpdated: new Date()
    };

    try {
      await this.container.executeCommand(check.command);
      
      // Update check status
      currentStatus.checks[check.name] = {
        status: 'pass',
        lastCheck: new Date(),
        consecutiveFailures: 0,
        consecutiveSuccesses: (currentStatus.checks[check.name]?.consecutiveSuccesses || 0) + 1
      };
    } catch (error) {
      // Update check status
      currentStatus.checks[check.name] = {
        status: 'fail',
        lastCheck: new Date(),
        lastError: error instanceof Error ? error.message : 'Unknown error',
        consecutiveFailures: (currentStatus.checks[check.name]?.consecutiveFailures || 0) + 1,
        consecutiveSuccesses: 0
      };
    }

    // Update overall health status
    const failedChecks = Object.values(currentStatus.checks).filter(c => c.status === 'fail');
    const unknownChecks = Object.values(currentStatus.checks).filter(c => c.status === 'unknown');

    if (failedChecks.length > 0) {
      currentStatus.status = 'unhealthy';
    } else if (unknownChecks.length > 0) {
      currentStatus.status = 'degraded';
    } else {
      currentStatus.status = 'healthy';
    }

    currentStatus.lastUpdated = new Date();
    this.healthStatus.set(this.container.id, currentStatus);

    this.logger.debug('Health check completed', {
      containerId: this.container.id,
      check: check.name,
      status: currentStatus.checks[check.name].status
    });
  }
} 