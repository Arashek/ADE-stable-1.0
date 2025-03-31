import { Logger } from '../logging/Logger';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface ResourceLimits {
  cpu: {
    shares: number;
    period: number;
    quota: number;
  };
  memory: {
    limit: string;
    swap: string;
    reservation: string;
  };
  gpu?: {
    count: number;
    type: string;
    memory: string;
  };
  storage: {
    size: string;
    iops: number;
  };
}

export interface ResourceMetrics {
  cpu: {
    usage: number;
    limit: number;
    percentage: number;
  };
  memory: {
    usage: string;
    limit: string;
    percentage: number;
  };
  gpu?: {
    usage: number;
    limit: number;
    percentage: number;
  };
  storage: {
    usage: string;
    limit: string;
    percentage: number;
  };
}

export interface AutoScalingConfig {
  enabled: boolean;
  minInstances: number;
  maxInstances: number;
  targetCPUUtilization: number;
  targetMemoryUtilization: number;
  scaleUpThreshold: number;
  scaleDownThreshold: number;
  cooldownPeriod: number;
}

export class ResourceManager {
  private logger: Logger;
  private resourceLimits: ResourceLimits;
  private autoScalingConfig: AutoScalingConfig;
  private monitoringInterval: NodeJS.Timeout | null;

  constructor() {
    this.logger = new Logger('ResourceManager');
    this.resourceLimits = this.getDefaultResourceLimits();
    this.autoScalingConfig = this.getDefaultAutoScalingConfig();
    this.monitoringInterval = null;
  }

  private getDefaultResourceLimits(): ResourceLimits {
    return {
      cpu: {
        shares: 1024,
        period: 100000,
        quota: 100000
      },
      memory: {
        limit: '2g',
        swap: '4g',
        reservation: '1g'
      },
      storage: {
        size: '20g',
        iops: 1000
      }
    };
  }

  private getDefaultAutoScalingConfig(): AutoScalingConfig {
    return {
      enabled: false,
      minInstances: 1,
      maxInstances: 5,
      targetCPUUtilization: 70,
      targetMemoryUtilization: 80,
      scaleUpThreshold: 80,
      scaleDownThreshold: 20,
      cooldownPeriod: 300
    };
  }

  async setResourceLimits(containerId: string, limits: ResourceLimits): Promise<void> {
    try {
      this.resourceLimits = limits;
      const command = this.buildResourceLimitCommand(containerId);
      await execAsync(command);
      this.logger.info(`Set resource limits for container: ${containerId}`);
    } catch (error) {
      this.logger.error(`Failed to set resource limits for container: ${containerId}`, error);
      throw error;
    }
  }

  private buildResourceLimitCommand(containerId: string): string {
    const { cpu, memory, storage } = this.resourceLimits;
    let command = `docker update`;

    // CPU limits
    command += ` --cpu-shares ${cpu.shares}`;
    command += ` --cpu-period ${cpu.period}`;
    command += ` --cpu-quota ${cpu.quota}`;

    // Memory limits
    command += ` --memory ${memory.limit}`;
    command += ` --memory-swap ${memory.swap}`;
    command += ` --memory-reservation ${memory.reservation}`;

    // Storage limits
    command += ` --storage-opt size=${storage.size}`;
    command += ` --storage-opt iops=${storage.iops}`;

    // GPU limits if specified
    if (this.resourceLimits.gpu) {
      command += ` --gpus all`;
    }

    command += ` ${containerId}`;
    return command;
  }

  async startMonitoring(containerId: string, interval: number = 5000): Promise<void> {
    try {
      if (this.monitoringInterval) {
        clearInterval(this.monitoringInterval);
      }

      this.monitoringInterval = setInterval(async () => {
        try {
          const metrics = await this.getResourceMetrics(containerId);
          await this.handleResourceMetrics(containerId, metrics);
        } catch (error) {
          this.logger.error('Failed to monitor resources', error);
        }
      }, interval);

      this.logger.info(`Started resource monitoring for container: ${containerId}`);
    } catch (error) {
      this.logger.error('Failed to start resource monitoring', error);
      throw error;
    }
  }

  async getResourceMetrics(containerId: string): Promise<ResourceMetrics> {
    try {
      const { stdout } = await execAsync(`docker stats ${containerId} --no-stream --format "{{.CPUPerc}},{{.MemUsage}},{{.NetIO}},{{.BlockIO}}"`);
      return this.parseResourceMetrics(stdout);
    } catch (error) {
      this.logger.error('Failed to get resource metrics', error);
      throw error;
    }
  }

  private parseResourceMetrics(stats: string): ResourceMetrics {
    const [cpu, memory, network, storage] = stats.split(',');
    
    return {
      cpu: {
        usage: parseFloat(cpu),
        limit: this.resourceLimits.cpu.quota,
        percentage: parseFloat(cpu)
      },
      memory: {
        usage: memory,
        limit: this.resourceLimits.memory.limit,
        percentage: this.parseMemoryPercentage(memory)
      },
      storage: {
        usage: storage,
        limit: this.resourceLimits.storage.size,
        percentage: this.parseStoragePercentage(storage)
      }
    };
  }

  private parseMemoryPercentage(memory: string): number {
    const [used, total] = memory.split('/').map(v => this.parseMemoryValue(v));
    return (used / total) * 100;
  }

  private parseStoragePercentage(storage: string): number {
    const [used, total] = storage.split('/').map(v => this.parseStorageValue(v));
    return (used / total) * 100;
  }

  private parseMemoryValue(value: string): number {
    const match = value.match(/(\d+)([kmgt])?b/i);
    if (!match) return 0;
    
    const [, num, unit] = match;
    const multiplier = unit ? Math.pow(1024, 'kmgt'.indexOf(unit.toLowerCase()) + 1) : 1;
    return parseInt(num) * multiplier;
  }

  private parseStorageValue(value: string): number {
    const match = value.match(/(\d+)([kmgt])?b/i);
    if (!match) return 0;
    
    const [, num, unit] = match;
    const multiplier = unit ? Math.pow(1024, 'kmgt'.indexOf(unit.toLowerCase()) + 1) : 1;
    return parseInt(num) * multiplier;
  }

  private async handleResourceMetrics(containerId: string, metrics: ResourceMetrics): Promise<void> {
    if (!this.autoScalingConfig.enabled) return;

    const shouldScaleUp = this.shouldScaleUp(metrics);
    const shouldScaleDown = this.shouldScaleDown(metrics);

    if (shouldScaleUp) {
      await this.scaleUp(containerId);
    } else if (shouldScaleDown) {
      await this.scaleDown(containerId);
    }
  }

  private shouldScaleUp(metrics: ResourceMetrics): boolean {
    return (
      metrics.cpu.percentage > this.autoScalingConfig.scaleUpThreshold ||
      metrics.memory.percentage > this.autoScalingConfig.scaleUpThreshold
    );
  }

  private shouldScaleDown(metrics: ResourceMetrics): boolean {
    return (
      metrics.cpu.percentage < this.autoScalingConfig.scaleDownThreshold &&
      metrics.memory.percentage < this.autoScalingConfig.scaleDownThreshold
    );
  }

  async scaleUp(containerId: string): Promise<void> {
    try {
      const command = `docker service scale ${containerId}=${this.autoScalingConfig.maxInstances}`;
      await execAsync(command);
      this.logger.info(`Scaled up container: ${containerId}`);
    } catch (error) {
      this.logger.error(`Failed to scale up container: ${containerId}`, error);
      throw error;
    }
  }

  async scaleDown(containerId: string): Promise<void> {
    try {
      const command = `docker service scale ${containerId}=${this.autoScalingConfig.minInstances}`;
      await execAsync(command);
      this.logger.info(`Scaled down container: ${containerId}`);
    } catch (error) {
      this.logger.error(`Failed to scale down container: ${containerId}`, error);
      throw error;
    }
  }

  async configureAutoScaling(config: AutoScalingConfig): Promise<void> {
    try {
      this.validateAutoScalingConfig(config);
      this.autoScalingConfig = config;
      this.logger.info('Updated auto-scaling configuration');
    } catch (error) {
      this.logger.error('Failed to configure auto-scaling', error);
      throw error;
    }
  }

  private validateAutoScalingConfig(config: AutoScalingConfig): void {
    if (config.minInstances < 1) {
      throw new Error('Minimum instances must be at least 1');
    }
    if (config.maxInstances < config.minInstances) {
      throw new Error('Maximum instances must be greater than minimum instances');
    }
    if (config.targetCPUUtilization < 0 || config.targetCPUUtilization > 100) {
      throw new Error('Target CPU utilization must be between 0 and 100');
    }
    if (config.targetMemoryUtilization < 0 || config.targetMemoryUtilization > 100) {
      throw new Error('Target memory utilization must be between 0 and 100');
    }
    if (config.cooldownPeriod < 0) {
      throw new Error('Cooldown period must be positive');
    }
  }

  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
      this.logger.info('Stopped resource monitoring');
    }
  }

  async cleanup(): Promise<void> {
    try {
      this.stopMonitoring();
      this.logger.info('Resource manager cleanup completed');
    } catch (error) {
      this.logger.error('Failed to cleanup resource manager', error);
      throw error;
    }
  }
} 