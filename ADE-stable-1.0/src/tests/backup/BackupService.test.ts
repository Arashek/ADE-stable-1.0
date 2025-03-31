import { BackupService } from '../../services/backup/BackupService';
import { Container } from '../../core/models/project/Container';
import { Logger } from '../../core/logging/Logger';
import { EventEmitter } from 'events';

jest.mock('../../core/models/project/Container');
jest.mock('../../core/logging/Logger');

describe('BackupService', () => {
  let backupService: BackupService;
  let container: jest.Mocked<Container>;
  let logger: jest.Mocked<Logger>;
  let config: any;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Create test configuration
    config = {
      backupDir: './test-backups',
      retentionDays: 7,
      compressionLevel: 6,
      excludePatterns: ['node_modules', '.git'],
      maxConcurrentBackups: 3,
      maxConcurrentRestores: 1,
      notificationEmail: 'test@example.com',
      schedule: {
        frequency: 'daily',
        time: '00:00'
      }
    };

    // Create mocked dependencies
    container = new Container() as jest.Mocked<Container>;
    logger = new Logger() as jest.Mocked<Logger>;

    // Create backup service instance
    backupService = new BackupService(container, logger, config);
  });

  describe('start', () => {
    it('should start the backup service', async () => {
      await backupService.start();
      expect(logger.info).toHaveBeenCalledWith('Starting backup service');
    });
  });

  describe('stop', () => {
    it('should stop the backup service', async () => {
      await backupService.stop();
      expect(logger.info).toHaveBeenCalledWith('Stopping backup service');
    });
  });

  describe('createBackup', () => {
    it('should create a backup successfully', async () => {
      const result = await backupService.createBackup('container');
      expect(result.success).toBe(true);
      expect(result.metadata.type).toBe('container');
      expect(result.metadata.status).toBe('completed');
      expect(logger.info).toHaveBeenCalledWith('Backup completed successfully', expect.any(Object));
    });

    it('should handle maximum concurrent backups limit', async () => {
      // Create maximum number of backups
      for (let i = 0; i < config.maxConcurrentBackups; i++) {
        await backupService.createBackup('container');
      }

      // Try to create one more backup
      await expect(backupService.createBackup('container')).rejects.toThrow(
        'Maximum number of concurrent backups reached'
      );
    });

    it('should emit backup progress events', async () => {
      const progressEvents: any[] = [];
      backupService.on('backupProgress', (event) => progressEvents.push(event));

      await backupService.createBackup('container');

      expect(progressEvents).toHaveLength(2);
      expect(progressEvents[0].status).toBe('in_progress');
      expect(progressEvents[1].status).toBe('completed');
    });
  });

  describe('restoreBackup', () => {
    it('should restore a backup successfully', async () => {
      // Create a test backup first
      const backupResult = await backupService.createBackup('container');
      const backupId = backupResult.metadata.id;

      // Restore the backup
      const result = await backupService.restoreBackup(backupId);
      expect(result.success).toBe(true);
      expect(result.metadata.status).toBe('completed');
      expect(logger.info).toHaveBeenCalledWith('Restore completed successfully', expect.any(Object));
    });

    it('should handle maximum concurrent restores limit', async () => {
      // Create and start a restore
      const backupResult = await backupService.createBackup('container');
      const backupId = backupResult.metadata.id;
      backupService.restoreBackup(backupId);

      // Try to start another restore
      await expect(backupService.restoreBackup(backupId)).rejects.toThrow(
        'Maximum number of concurrent restores reached'
      );
    });

    it('should emit restore progress events', async () => {
      const progressEvents: any[] = [];
      backupService.on('restoreProgress', (event) => progressEvents.push(event));

      // Create a test backup first
      const backupResult = await backupService.createBackup('container');
      const backupId = backupResult.metadata.id;

      // Restore the backup
      await backupService.restoreBackup(backupId);

      expect(progressEvents).toHaveLength(2);
      expect(progressEvents[0].status).toBe('in_progress');
      expect(progressEvents[1].status).toBe('completed');
    });
  });

  describe('listBackups', () => {
    it('should list all backups', async () => {
      // Create some test backups
      await backupService.createBackup('container');
      await backupService.createBackup('project');

      const backups = await backupService.listBackups();
      expect(backups.length).toBe(2);
      expect(backups[0].type).toBe('project');
      expect(backups[1].type).toBe('container');
    });

    it('should filter backups by type', async () => {
      await backupService.createBackup('container');
      await backupService.createBackup('project');

      const backups = await backupService.listBackups({ type: 'container' });
      expect(backups.length).toBe(1);
      expect(backups[0].type).toBe('container');
    });
  });

  describe('deleteBackup', () => {
    it('should delete a backup successfully', async () => {
      const backupResult = await backupService.createBackup('container');
      const backupId = backupResult.metadata.id;

      await backupService.deleteBackup(backupId);
      const backups = await backupService.listBackups();
      expect(backups.length).toBe(0);
    });
  });

  describe('getActiveBackups', () => {
    it('should return list of active backups', async () => {
      const backupPromise = backupService.createBackup('container');
      const activeBackups = backupService.getActiveBackups();
      expect(activeBackups.length).toBe(1);
      await backupPromise;
    });
  });

  describe('getActiveRestores', () => {
    it('should return list of active restores', async () => {
      const backupResult = await backupService.createBackup('container');
      const backupId = backupResult.metadata.id;
      const restorePromise = backupService.restoreBackup(backupId);
      const activeRestores = backupService.getActiveRestores();
      expect(activeRestores.length).toBe(1);
      await restorePromise;
    });
  });
}); 