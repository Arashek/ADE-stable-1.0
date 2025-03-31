import { BackupManager, BackupConfig, BackupMetadata, BackupResult } from '../../core/backup/BackupManager';
import { Container } from '../../core/models/project/Container';
import { Logger } from '../../core/logging/Logger';
import { EventEmitter } from 'events';

export interface BackupServiceConfig extends BackupConfig {
  maxConcurrentBackups: number;
  maxConcurrentRestores: number;
  notificationEmail?: string;
}

export interface BackupProgress {
  backupId: string;
  type: 'container' | 'project';
  status: 'in_progress' | 'completed' | 'failed';
  progress: number;
  error?: string;
}

export class BackupService extends EventEmitter {
  private backupManager: BackupManager;
  private activeBackups: Set<string>;
  private activeRestores: Set<string>;

  constructor(
    private container: Container,
    private logger: Logger,
    private config: BackupServiceConfig
  ) {
    super();
    this.backupManager = new BackupManager(container, logger, config);
    this.activeBackups = new Set();
    this.activeRestores = new Set();
  }

  public async start(): Promise<void> {
    this.logger.info('Starting backup service');
    await this.backupManager.start();
  }

  public async stop(): Promise<void> {
    this.logger.info('Stopping backup service');
    await this.backupManager.stop();
  }

  public async createBackup(type: 'container' | 'project', tags?: string[]): Promise<BackupResult> {
    // Check if we've reached the maximum number of concurrent backups
    if (this.activeBackups.size >= this.config.maxConcurrentBackups) {
      throw new Error('Maximum number of concurrent backups reached');
    }

    const backupId = `backup-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    this.activeBackups.add(backupId);

    try {
      // Emit progress event
      this.emit('backupProgress', {
        backupId,
        type,
        status: 'in_progress',
        progress: 0
      });

      const result = await this.backupManager.createBackup(type, tags);

      // Emit completion event
      this.emit('backupProgress', {
        backupId,
        type,
        status: 'completed',
        progress: 100
      });

      // Send notification if configured
      if (this.config.notificationEmail) {
        await this.sendBackupNotification(result);
      }

      return result;
    } catch (error) {
      // Emit error event
      this.emit('backupProgress', {
        backupId,
        type,
        status: 'failed',
        progress: 0,
        error: error instanceof Error ? error.message : 'Unknown error'
      });

      throw error;
    } finally {
      this.activeBackups.delete(backupId);
    }
  }

  public async restoreBackup(backupId: string): Promise<BackupResult> {
    // Check if we've reached the maximum number of concurrent restores
    if (this.activeRestores.size >= this.config.maxConcurrentRestores) {
      throw new Error('Maximum number of concurrent restores reached');
    }

    this.activeRestores.add(backupId);

    try {
      // Emit progress event
      this.emit('restoreProgress', {
        backupId,
        status: 'in_progress',
        progress: 0
      });

      const result = await this.backupManager.restoreBackup(backupId);

      // Emit completion event
      this.emit('restoreProgress', {
        backupId,
        status: 'completed',
        progress: 100
      });

      // Send notification if configured
      if (this.config.notificationEmail) {
        await this.sendRestoreNotification(result);
      }

      return result;
    } catch (error) {
      // Emit error event
      this.emit('restoreProgress', {
        backupId,
        status: 'failed',
        progress: 0,
        error: error instanceof Error ? error.message : 'Unknown error'
      });

      throw error;
    } finally {
      this.activeRestores.delete(backupId);
    }
  }

  public async listBackups(filters?: {
    type?: 'container' | 'project';
    status?: BackupMetadata['status'];
    startDate?: Date;
    endDate?: Date;
  }): Promise<BackupMetadata[]> {
    return this.backupManager.listBackups(filters);
  }

  public async deleteBackup(backupId: string): Promise<void> {
    await this.backupManager.deleteBackup(backupId);
  }

  public getActiveBackups(): string[] {
    return Array.from(this.activeBackups);
  }

  public getActiveRestores(): string[] {
    return Array.from(this.activeRestores);
  }

  private async sendBackupNotification(result: BackupResult): Promise<void> {
    // In a real implementation, this would send an email notification
    // For now, we'll just log the action
    this.logger.info('Sending backup notification', {
      email: this.config.notificationEmail,
      backupId: result.metadata.id,
      status: result.metadata.status
    });
  }

  private async sendRestoreNotification(result: BackupResult): Promise<void> {
    // In a real implementation, this would send an email notification
    // For now, we'll just log the action
    this.logger.info('Sending restore notification', {
      email: this.config.notificationEmail,
      backupId: result.metadata.id,
      status: result.metadata.status
    });
  }
} 