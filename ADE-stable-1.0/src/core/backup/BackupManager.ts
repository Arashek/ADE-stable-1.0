import { Logger } from '../logging/Logger';
import { Container } from '../models/project/Container';
import * as fs from 'fs';
import * as path from 'path';
import * as tar from 'tar';
import { promisify } from 'util';

export interface BackupConfig {
  backupDir: string;
  retentionDays: number;
  compressionLevel: number;
  excludePatterns: string[];
  schedule?: {
    frequency: 'daily' | 'weekly' | 'monthly';
    time: string; // HH:mm format
  };
}

export interface BackupMetadata {
  id: string;
  timestamp: Date;
  type: 'container' | 'project';
  containerId?: string;
  projectId?: string;
  size: number;
  status: 'completed' | 'failed' | 'in_progress';
  error?: string;
  checksum: string;
  tags?: string[];
}

export interface BackupResult {
  success: boolean;
  metadata: BackupMetadata;
  path: string;
  error?: string;
}

export class BackupManager {
  private backupQueue: Map<string, Promise<BackupResult>>;
  private restoreQueue: Map<string, Promise<BackupResult>>;
  private scheduleInterval: NodeJS.Timeout | null;

  constructor(
    private container: Container,
    private logger: Logger,
    private config: BackupConfig
  ) {
    this.backupQueue = new Map();
    this.restoreQueue = new Map();
    this.scheduleInterval = null;

    // Ensure backup directory exists
    if (!fs.existsSync(config.backupDir)) {
      fs.mkdirSync(config.backupDir, { recursive: true });
    }
  }

  public async start(): Promise<void> {
    this.logger.info('Starting backup manager');
    
    // Start scheduled backups if configured
    if (this.config.schedule) {
      await this.startScheduledBackups();
    }

    // Start cleanup of old backups
    await this.cleanupOldBackups();
  }

  public async stop(): Promise<void> {
    this.logger.info('Stopping backup manager');
    
    if (this.scheduleInterval) {
      clearInterval(this.scheduleInterval);
      this.scheduleInterval = null;
    }
  }

  public async createBackup(type: 'container' | 'project', tags?: string[]): Promise<BackupResult> {
    const backupId = this.generateBackupId();
    const backupPath = path.join(this.config.backupDir, `${backupId}.tar.gz`);

    // Check if backup is already in progress
    if (this.backupQueue.has(backupId)) {
      return this.backupQueue.get(backupId)!;
    }

    const backupPromise = this.performBackup(type, backupId, backupPath, tags);
    this.backupQueue.set(backupId, backupPromise);

    try {
      const result = await backupPromise;
      this.logger.info('Backup completed successfully', { backupId: result.metadata.id });
      return result;
    } catch (error) {
      this.logger.error('Backup failed', error as Error, { backupId });
      throw error;
    } finally {
      this.backupQueue.delete(backupId);
    }
  }

  public async restoreBackup(backupId: string): Promise<BackupResult> {
    const backupPath = path.join(this.config.backupDir, `${backupId}.tar.gz`);

    // Check if restore is already in progress
    if (this.restoreQueue.has(backupId)) {
      return this.restoreQueue.get(backupId)!;
    }

    const restorePromise = this.performRestore(backupId, backupPath);
    this.restoreQueue.set(backupId, restorePromise);

    try {
      const result = await restorePromise;
      this.logger.info('Restore completed successfully', { backupId: result.metadata.id });
      return result;
    } catch (error) {
      this.logger.error('Restore failed', error as Error, { backupId });
      throw error;
    } finally {
      this.restoreQueue.delete(backupId);
    }
  }

  public async listBackups(filters?: {
    type?: 'container' | 'project';
    status?: BackupMetadata['status'];
    startDate?: Date;
    endDate?: Date;
  }): Promise<BackupMetadata[]> {
    const backups: BackupMetadata[] = [];
    const files = await promisify(fs.readdir)(this.config.backupDir);

    for (const file of files) {
      if (!file.endsWith('.tar.gz')) continue;

      const backupPath = path.join(this.config.backupDir, file);
      const stats = await promisify(fs.stat)(backupPath);
      const metadata = await this.readBackupMetadata(backupPath);

      if (this.matchesFilters(metadata, filters)) {
        backups.push({
          ...metadata,
          size: stats.size
        });
      }
    }

    return backups.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  public async deleteBackup(backupId: string): Promise<void> {
    const backupPath = path.join(this.config.backupDir, `${backupId}.tar.gz`);
    
    try {
      await promisify(fs.unlink)(backupPath);
      this.logger.info('Backup deleted', { backupId });
    } catch (error) {
      this.logger.error('Failed to delete backup', error as Error, { backupId });
      throw error;
    }
  }

  private async performBackup(
    type: 'container' | 'project',
    backupId: string,
    backupPath: string,
    tags?: string[]
  ): Promise<BackupResult> {
    const metadata: BackupMetadata = {
      id: backupId,
      timestamp: new Date(),
      type,
      containerId: type === 'container' ? this.container.id : undefined,
      projectId: type === 'project' ? this.container.projectId : undefined,
      size: 0,
      status: 'in_progress',
      checksum: '',
      tags
    };

    try {
      // Create temporary directory for backup
      const tempDir = path.join(this.config.backupDir, 'temp', backupId);
      await promisify(fs.mkdir)(tempDir, { recursive: true });

      if (type === 'container') {
        await this.backupContainer(tempDir);
      } else {
        await this.backupProject(tempDir);
      }

      // Create tar archive
      await tar.create(
        {
          gzip: true,
          cwd: tempDir,
          file: backupPath,
          level: this.config.compressionLevel
        },
        ['.']
      );

      // Calculate checksum
      const checksum = await this.calculateChecksum(backupPath);

      // Update metadata
      const stats = await promisify(fs.stat)(backupPath);
      metadata.size = stats.size;
      metadata.status = 'completed';
      metadata.checksum = checksum;

      // Save metadata
      await this.saveBackupMetadata(backupPath, metadata);

      // Cleanup
      await promisify(fs.rm)(tempDir, { recursive: true, force: true });

      return {
        success: true,
        metadata,
        path: backupPath
      };
    } catch (error) {
      metadata.status = 'failed';
      metadata.error = error instanceof Error ? error.message : 'Unknown error';
      await this.saveBackupMetadata(backupPath, metadata);
      throw error;
    }
  }

  private async performRestore(backupId: string, backupPath: string): Promise<BackupResult> {
    const metadata = await this.readBackupMetadata(backupPath);
    metadata.status = 'in_progress';

    try {
      // Create temporary directory for restore
      const tempDir = path.join(this.config.backupDir, 'temp', backupId);
      await promisify(fs.mkdir)(tempDir, { recursive: true });

      // Extract backup
      await tar.extract({
        file: backupPath,
        cwd: tempDir
      });

      if (metadata.type === 'container') {
        await this.restoreContainer(tempDir);
      } else {
        await this.restoreProject(tempDir);
      }

      // Update metadata
      metadata.status = 'completed';

      // Cleanup
      await promisify(fs.rm)(tempDir, { recursive: true, force: true });

      return {
        success: true,
        metadata,
        path: backupPath
      };
    } catch (error) {
      metadata.status = 'failed';
      metadata.error = error instanceof Error ? error.message : 'Unknown error';
      await this.saveBackupMetadata(backupPath, metadata);
      throw error;
    }
  }

  private async backupContainer(tempDir: string): Promise<void> {
    // Save container configuration
    const config = await this.container.getConfig();
    await promisify(fs.writeFile)(
      path.join(tempDir, 'container-config.json'),
      JSON.stringify(config, null, 2)
    );

    // Save container state
    const state = await this.container.getState();
    await promisify(fs.writeFile)(
      path.join(tempDir, 'container-state.json'),
      JSON.stringify(state, null, 2)
    );

    // Save container logs
    const logs = await this.container.getLogs();
    await promisify(fs.writeFile)(
      path.join(tempDir, 'container-logs.txt'),
      logs
    );
  }

  private async backupProject(tempDir: string): Promise<void> {
    // Save project files
    const projectDir = path.join(tempDir, 'project');
    await promisify(fs.mkdir)(projectDir, { recursive: true });

    // In a real implementation, this would copy project files
    // For now, we'll just create a placeholder
    await promisify(fs.writeFile)(
      path.join(projectDir, 'README.md'),
      'Project backup placeholder'
    );
  }

  private async restoreContainer(tempDir: string): Promise<void> {
    // Restore container configuration
    const configPath = path.join(tempDir, 'container-config.json');
    if (await this.fileExists(configPath)) {
      const config = JSON.parse(await promisify(fs.readFile)(configPath, 'utf-8'));
      await this.container.updateConfig(config);
    }

    // Restore container state
    const statePath = path.join(tempDir, 'container-state.json');
    if (await this.fileExists(statePath)) {
      const state = JSON.parse(await promisify(fs.readFile)(statePath, 'utf-8'));
      await this.container.setState(state);
    }
  }

  private async restoreProject(tempDir: string): Promise<void> {
    const projectDir = path.join(tempDir, 'project');
    if (await this.fileExists(projectDir)) {
      // In a real implementation, this would restore project files
      // For now, we'll just log the action
      this.logger.info('Restoring project files', { projectDir });
    }
  }

  private async startScheduledBackups(): Promise<void> {
    const { frequency, time } = this.config.schedule!;
    const [hours, minutes] = time.split(':').map(Number);

    const scheduleBackup = async () => {
      const now = new Date();
      const scheduledTime = new Date();
      scheduledTime.setHours(hours, minutes, 0, 0);

      if (now >= scheduledTime) {
        try {
          await this.createBackup('container', ['scheduled']);
          await this.createBackup('project', ['scheduled']);
        } catch (error) {
          this.logger.error('Scheduled backup failed', error as Error);
        }
      }
    };

    // Run immediately if current time is past scheduled time
    await scheduleBackup();

    // Schedule future backups
    const interval = frequency === 'daily' ? 24 * 60 * 60 * 1000 :
                     frequency === 'weekly' ? 7 * 24 * 60 * 60 * 1000 :
                     30 * 24 * 60 * 60 * 1000;

    this.scheduleInterval = setInterval(scheduleBackup, interval);
  }

  private async cleanupOldBackups(): Promise<void> {
    const backups = await this.listBackups();
    const now = new Date();
    const retentionMs = this.config.retentionDays * 24 * 60 * 60 * 1000;

    for (const backup of backups) {
      if (now.getTime() - backup.timestamp.getTime() > retentionMs) {
        await this.deleteBackup(backup.id);
      }
    }
  }

  private async readBackupMetadata(backupPath: string): Promise<BackupMetadata> {
    const metadataPath = backupPath.replace('.tar.gz', '.metadata.json');
    if (await this.fileExists(metadataPath)) {
      return JSON.parse(await promisify(fs.readFile)(metadataPath, 'utf-8'));
    }
    throw new Error('Backup metadata not found');
  }

  private async saveBackupMetadata(backupPath: string, metadata: BackupMetadata): Promise<void> {
    const metadataPath = backupPath.replace('.tar.gz', '.metadata.json');
    await promisify(fs.writeFile)(
      metadataPath,
      JSON.stringify(metadata, null, 2)
    );
  }

  private async calculateChecksum(filePath: string): Promise<string> {
    // In a real implementation, this would calculate a proper checksum
    // For now, we'll return a placeholder
    return 'placeholder-checksum';
  }

  private async fileExists(filePath: string): Promise<boolean> {
    try {
      await promisify(fs.access)(filePath);
      return true;
    } catch {
      return false;
    }
  }

  private matchesFilters(
    metadata: BackupMetadata,
    filters?: {
      type?: 'container' | 'project';
      status?: BackupMetadata['status'];
      startDate?: Date;
      endDate?: Date;
    }
  ): boolean {
    if (!filters) return true;

    if (filters.type && metadata.type !== filters.type) return false;
    if (filters.status && metadata.status !== filters.status) return false;
    if (filters.startDate && metadata.timestamp < filters.startDate) return false;
    if (filters.endDate && metadata.timestamp > filters.endDate) return false;

    return true;
  }

  private generateBackupId(): string {
    return `backup-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
} 