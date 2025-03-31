import { Logger } from '../logging/Logger';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

const execAsync = promisify(exec);

export interface ContainerConfig {
  image: string;
  name: string;
  env: Record<string, string>;
  volumes: string[];
  ports: string[];
  restartPolicy: 'no' | 'always' | 'unless-stopped' | 'on-failure';
  healthCheck?: {
    test: string[];
    interval: string;
    timeout: string;
    retries: number;
    startPeriod: string;
  };
}

export interface BackupConfig {
  enabled: boolean;
  schedule: string;
  retention: number;
  path: string;
}

export interface ContainerState {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'paused' | 'restarting';
  health: 'healthy' | 'unhealthy' | 'starting';
  startedAt: string;
  lastBackup?: string;
}

export class ContainerLifecycleManager {
  private logger: Logger;
  private containerConfig: ContainerConfig;
  private backupConfig: BackupConfig;
  private containerState: ContainerState | null;
  private backupInterval: NodeJS.Timeout | null;

  constructor() {
    this.logger = new Logger('ContainerLifecycleManager');
    this.containerConfig = this.getDefaultContainerConfig();
    this.backupConfig = this.getDefaultBackupConfig();
    this.containerState = null;
    this.backupInterval = null;
  }

  private getDefaultContainerConfig(): ContainerConfig {
    return {
      image: '',
      name: '',
      env: {},
      volumes: [],
      ports: [],
      restartPolicy: 'unless-stopped'
    };
  }

  private getDefaultBackupConfig(): BackupConfig {
    return {
      enabled: false,
      schedule: '0 0 * * *', // Daily at midnight
      retention: 7,
      path: './backups'
    };
  }

  async createContainer(config: ContainerConfig): Promise<void> {
    try {
      this.containerConfig = config;
      const command = this.buildCreateCommand();
      const { stdout } = await execAsync(command);
      this.containerState = this.parseContainerState(stdout);
      this.logger.info(`Created container: ${config.name}`);
    } catch (error) {
      this.logger.error(`Failed to create container: ${config.name}`, error);
      throw error;
    }
  }

  private buildCreateCommand(): string {
    const { image, name, env, volumes, ports, restartPolicy, healthCheck } = this.containerConfig;
    let command = `docker create`;

    // Basic configuration
    command += ` --name ${name}`;
    command += ` --restart ${restartPolicy}`;

    // Environment variables
    Object.entries(env).forEach(([key, value]) => {
      command += ` -e ${key}=${value}`;
    });

    // Volumes
    volumes.forEach(volume => {
      command += ` -v ${volume}`;
    });

    // Ports
    ports.forEach(port => {
      command += ` -p ${port}`;
    });

    // Health check
    if (healthCheck) {
      command += ` --health-cmd "${healthCheck.test.join(' ')}"`;
      command += ` --health-interval ${healthCheck.interval}`;
      command += ` --health-timeout ${healthCheck.timeout}`;
      command += ` --health-retries ${healthCheck.retries}`;
      command += ` --health-start-period ${healthCheck.startPeriod}`;
    }

    command += ` ${image}`;
    return command;
  }

  async startContainer(): Promise<void> {
    try {
      if (!this.containerState) {
        throw new Error('No container state available');
      }

      const command = `docker start ${this.containerState.id}`;
      await execAsync(command);
      this.containerState.status = 'running';
      this.logger.info(`Started container: ${this.containerState.name}`);
    } catch (error) {
      this.logger.error('Failed to start container', error);
      throw error;
    }
  }

  async stopContainer(): Promise<void> {
    try {
      if (!this.containerState) {
        throw new Error('No container state available');
      }

      const command = `docker stop ${this.containerState.id}`;
      await execAsync(command);
      this.containerState.status = 'stopped';
      this.logger.info(`Stopped container: ${this.containerState.name}`);
    } catch (error) {
      this.logger.error('Failed to stop container', error);
      throw error;
    }
  }

  async pauseContainer(): Promise<void> {
    try {
      if (!this.containerState) {
        throw new Error('No container state available');
      }

      const command = `docker pause ${this.containerState.id}`;
      await execAsync(command);
      this.containerState.status = 'paused';
      this.logger.info(`Paused container: ${this.containerState.name}`);
    } catch (error) {
      this.logger.error('Failed to pause container', error);
      throw error;
    }
  }

  async resumeContainer(): Promise<void> {
    try {
      if (!this.containerState) {
        throw new Error('No container state available');
      }

      const command = `docker unpause ${this.containerState.id}`;
      await execAsync(command);
      this.containerState.status = 'running';
      this.logger.info(`Resumed container: ${this.containerState.name}`);
    } catch (error) {
      this.logger.error('Failed to resume container', error);
      throw error;
    }
  }

  async createBackup(): Promise<void> {
    try {
      if (!this.containerState) {
        throw new Error('No container state available');
      }

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const backupPath = path.join(this.backupConfig.path, `${this.containerState.name}-${timestamp}.tar`);

      // Ensure backup directory exists
      if (!fs.existsSync(this.backupConfig.path)) {
        fs.mkdirSync(this.backupConfig.path, { recursive: true });
      }

      // Create backup
      const command = `docker commit ${this.containerState.id} ${this.containerState.name}:backup-${timestamp} && docker save ${this.containerState.name}:backup-${timestamp} > ${backupPath}`;
      await execAsync(command);

      // Update state
      this.containerState.lastBackup = timestamp;
      this.logger.info(`Created backup: ${backupPath}`);

      // Cleanup old backups
      await this.cleanupOldBackups();
    } catch (error) {
      this.logger.error('Failed to create backup', error);
      throw error;
    }
  }

  private async cleanupOldBackups(): Promise<void> {
    try {
      const files = fs.readdirSync(this.backupConfig.path);
      const backups = files
        .filter(file => file.startsWith(this.containerState?.name || ''))
        .map(file => ({
          name: file,
          path: path.join(this.backupConfig.path, file),
          time: fs.statSync(path.join(this.backupConfig.path, file)).mtime.getTime()
        }))
        .sort((a, b) => b.time - a.time);

      // Remove old backups
      for (let i = this.backupConfig.retention; i < backups.length; i++) {
        fs.unlinkSync(backups[i].path);
        this.logger.info(`Removed old backup: ${backups[i].name}`);
      }
    } catch (error) {
      this.logger.error('Failed to cleanup old backups', error);
      throw error;
    }
  }

  async restoreBackup(backupPath: string): Promise<void> {
    try {
      if (!this.containerState) {
        throw new Error('No container state available');
      }

      // Stop container if running
      if (this.containerState.status === 'running') {
        await this.stopContainer();
      }

      // Load and restore backup
      const command = `docker load < ${backupPath} && docker tag ${this.containerState.name}:latest ${this.containerState.name}:restored`;
      await execAsync(command);

      // Update container state
      this.containerState.lastBackup = new Date().toISOString();
      this.logger.info(`Restored backup: ${backupPath}`);
    } catch (error) {
      this.logger.error('Failed to restore backup', error);
      throw error;
    }
  }

  async configureBackup(config: BackupConfig): Promise<void> {
    try {
      this.validateBackupConfig(config);
      this.backupConfig = config;

      // Clear existing backup interval
      if (this.backupInterval) {
        clearInterval(this.backupInterval);
      }

      // Set up new backup schedule if enabled
      if (config.enabled) {
        this.setupBackupSchedule();
      }

      this.logger.info('Updated backup configuration');
    } catch (error) {
      this.logger.error('Failed to configure backup', error);
      throw error;
    }
  }

  private validateBackupConfig(config: BackupConfig): void {
    if (config.retention < 1) {
      throw new Error('Backup retention must be at least 1');
    }
    if (!fs.existsSync(config.path) && !fs.mkdirSync(config.path, { recursive: true })) {
      throw new Error('Failed to create backup directory');
    }
  }

  private setupBackupSchedule(): void {
    // This is a simplified example. In a real implementation,
    // you would use a proper cron-like scheduler
    const interval = this.parseCronSchedule(this.backupConfig.schedule);
    this.backupInterval = setInterval(async () => {
      try {
        await this.createBackup();
      } catch (error) {
        this.logger.error('Scheduled backup failed', error);
      }
    }, interval);
  }

  private parseCronSchedule(schedule: string): number {
    // This is a simplified example. In a real implementation,
    // you would use a proper cron parser
    const [minute, hour] = schedule.split(' ');
    const now = new Date();
    const next = new Date(now);
    next.setHours(parseInt(hour), parseInt(minute), 0, 0);
    if (next <= now) {
      next.setDate(next.getDate() + 1);
    }
    return next.getTime() - now.getTime();
  }

  private parseContainerState(output: string): ContainerState {
    const lines = output.split('\n');
    const state: ContainerState = {
      id: '',
      name: '',
      status: 'stopped',
      health: 'starting',
      startedAt: new Date().toISOString()
    };

    lines.forEach(line => {
      if (line.includes('ID:')) {
        state.id = line.split('ID:')[1].trim();
      } else if (line.includes('Name:')) {
        state.name = line.split('Name:')[1].trim();
      } else if (line.includes('Status:')) {
        const status = line.split('Status:')[1].trim().toLowerCase();
        if (status.includes('running')) {
          state.status = 'running';
        } else if (status.includes('paused')) {
          state.status = 'paused';
        } else if (status.includes('restarting')) {
          state.status = 'restarting';
        }
      } else if (line.includes('Health:')) {
        const health = line.split('Health:')[1].trim().toLowerCase();
        if (health.includes('healthy')) {
          state.health = 'healthy';
        } else if (health.includes('unhealthy')) {
          state.health = 'unhealthy';
        }
      }
    });

    return state;
  }

  async cleanup(): Promise<void> {
    try {
      if (this.backupInterval) {
        clearInterval(this.backupInterval);
        this.backupInterval = null;
      }

      if (this.containerState) {
        await this.stopContainer();
        const command = `docker rm ${this.containerState.id}`;
        await execAsync(command);
        this.containerState = null;
      }

      this.logger.info('Container lifecycle manager cleanup completed');
    } catch (error) {
      this.logger.error('Failed to cleanup container lifecycle manager', error);
      throw error;
    }
  }
} 