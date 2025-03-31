import { Request, Response } from 'express';
import { BackupService, BackupProgress } from '../../services/backup/BackupService';
import { Logger } from '../../core/logging/Logger';

export class BackupController {
  constructor(
    private backupService: BackupService,
    private logger: Logger
  ) {
    // Set up event listeners for backup and restore progress
    this.backupService.on('backupProgress', this.handleBackupProgress.bind(this));
    this.backupService.on('restoreProgress', this.handleRestoreProgress.bind(this));
  }

  public async createBackup(req: Request, res: Response): Promise<void> {
    try {
      const { type, tags } = req.body;

      if (!type || !['container', 'project'].includes(type)) {
        res.status(400).json({
          error: 'Invalid backup type. Must be either "container" or "project".'
        });
        return;
      }

      const result = await this.backupService.createBackup(type, tags);
      res.status(201).json(result);
    } catch (error) {
      this.logger.error('Failed to create backup', error as Error);
      res.status(500).json({
        error: 'Failed to create backup',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }

  public async restoreBackup(req: Request, res: Response): Promise<void> {
    try {
      const { backupId } = req.params;

      if (!backupId) {
        res.status(400).json({
          error: 'Backup ID is required'
        });
        return;
      }

      const result = await this.backupService.restoreBackup(backupId);
      res.status(200).json(result);
    } catch (error) {
      this.logger.error('Failed to restore backup', error as Error);
      res.status(500).json({
        error: 'Failed to restore backup',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }

  public async listBackups(req: Request, res: Response): Promise<void> {
    try {
      const { type, status, startDate, endDate } = req.query;

      const filters: any = {};
      if (type) filters.type = type;
      if (status) filters.status = status;
      if (startDate) filters.startDate = new Date(startDate as string);
      if (endDate) filters.endDate = new Date(endDate as string);

      const backups = await this.backupService.listBackups(filters);
      res.status(200).json(backups);
    } catch (error) {
      this.logger.error('Failed to list backups', error as Error);
      res.status(500).json({
        error: 'Failed to list backups',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }

  public async deleteBackup(req: Request, res: Response): Promise<void> {
    try {
      const { backupId } = req.params;

      if (!backupId) {
        res.status(400).json({
          error: 'Backup ID is required'
        });
        return;
      }

      await this.backupService.deleteBackup(backupId);
      res.status(204).send();
    } catch (error) {
      this.logger.error('Failed to delete backup', error as Error);
      res.status(500).json({
        error: 'Failed to delete backup',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }

  public async getActiveBackups(req: Request, res: Response): Promise<void> {
    try {
      const activeBackups = this.backupService.getActiveBackups();
      res.status(200).json(activeBackups);
    } catch (error) {
      this.logger.error('Failed to get active backups', error as Error);
      res.status(500).json({
        error: 'Failed to get active backups',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }

  public async getActiveRestores(req: Request, res: Response): Promise<void> {
    try {
      const activeRestores = this.backupService.getActiveRestores();
      res.status(200).json(activeRestores);
    } catch (error) {
      this.logger.error('Failed to get active restores', error as Error);
      res.status(500).json({
        error: 'Failed to get active restores',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }

  private handleBackupProgress(progress: BackupProgress): void {
    // In a real implementation, this would send the progress update to connected clients
    // For example, using WebSocket or Server-Sent Events
    this.logger.info('Backup progress update', progress);
  }

  private handleRestoreProgress(progress: BackupProgress): void {
    // In a real implementation, this would send the progress update to connected clients
    // For example, using WebSocket or Server-Sent Events
    this.logger.info('Restore progress update', progress);
  }
} 