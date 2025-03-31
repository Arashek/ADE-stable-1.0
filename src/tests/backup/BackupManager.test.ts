import { BackupManager } from '../../core/backup/BackupManager';
import { Container } from '../../core/models/project/Container';
import { Logger } from '../../core/logging/Logger';
import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';

jest.mock('fs');
jest.mock('../../core/models/project/Container');
jest.mock('../../core/logging/Logger');

describe('BackupManager', () => {
  let backupManager: BackupManager;
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
      schedule: {
        frequency: 'daily',
        time: '00:00'
      }
    };

    // Create mocked dependencies
    container = new Container() as jest.Mocked<Container>;
    logger = new Logger() as jest.Mocked<Logger>;

    // Setup container mocks
    container.getConfig.mockResolvedValue({ id: 'test-container' });
    container.getState.mockResolvedValue({ status: 'running' });
    container.getLogs.mockResolvedValue('Test logs');
    container.updateConfig.mockResolvedValue(undefined);
    container.setState.mockResolvedValue(undefined);

    // Create backup manager instance
    backupManager = new BackupManager(container, logger, config);
  });

  afterEach(async () => {
    // Cleanup test files
    if (fs.existsSync(config.backupDir)) {
      await promisify(fs.rm)(config.backupDir, { recursive: true, force: true });
    }
  });

  describe('start', () => {
    it('should create backup directory if it does not exist', async () => {
      (fs.existsSync as jest.Mock).mockReturnValue(false);
      await backupManager.start();
      expect(fs.mkdirSync).toHaveBeenCalledWith(config.backupDir, { recursive: true });
    });

    it('should not create backup directory if it exists', async () => {
      (fs.existsSync as jest.Mock).mockReturnValue(true);
      await backupManager.start();
      expect(fs.mkdirSync).not.toHaveBeenCalled();
    });
  });

  describe('createBackup', () => {
    it('should create a container backup successfully', async () => {
      const result = await backupManager.createBackup('container');
      expect(result.success).toBe(true);
      expect(result.metadata.type).toBe('container');
      expect(result.metadata.status).toBe('completed');
      expect(container.getConfig).toHaveBeenCalled();
      expect(container.getState).toHaveBeenCalled();
      expect(container.getLogs).toHaveBeenCalled();
    });

    it('should create a project backup successfully', async () => {
      const result = await backupManager.createBackup('project');
      expect(result.success).toBe(true);
      expect(result.metadata.type).toBe('project');
      expect(result.metadata.status).toBe('completed');
    });

    it('should handle backup failures', async () => {
      container.getConfig.mockRejectedValue(new Error('Test error'));
      const result = await backupManager.createBackup('container');
      expect(result.success).toBe(false);
      expect(result.metadata.status).toBe('failed');
      expect(result.metadata.error).toBe('Test error');
    });
  });

  describe('restoreBackup', () => {
    it('should restore a container backup successfully', async () => {
      // Create a test backup first
      const backupResult = await backupManager.createBackup('container');
      const backupId = backupResult.metadata.id;

      // Restore the backup
      const result = await backupManager.restoreBackup(backupId);
      expect(result.success).toBe(true);
      expect(result.metadata.status).toBe('completed');
      expect(container.updateConfig).toHaveBeenCalled();
      expect(container.setState).toHaveBeenCalled();
    });

    it('should handle restore failures', async () => {
      container.updateConfig.mockRejectedValue(new Error('Test error'));
      const result = await backupManager.restoreBackup('non-existent-backup');
      expect(result.success).toBe(false);
      expect(result.metadata.status).toBe('failed');
      expect(result.metadata.error).toBe('Test error');
    });
  });

  describe('listBackups', () => {
    it('should list all backups', async () => {
      // Create some test backups
      await backupManager.createBackup('container');
      await backupManager.createBackup('project');

      const backups = await backupManager.listBackups();
      expect(backups.length).toBe(2);
      expect(backups[0].type).toBe('project');
      expect(backups[1].type).toBe('container');
    });

    it('should filter backups by type', async () => {
      await backupManager.createBackup('container');
      await backupManager.createBackup('project');

      const backups = await backupManager.listBackups({ type: 'container' });
      expect(backups.length).toBe(1);
      expect(backups[0].type).toBe('container');
    });
  });

  describe('deleteBackup', () => {
    it('should delete a backup successfully', async () => {
      const backupResult = await backupManager.createBackup('container');
      const backupId = backupResult.metadata.id;

      await backupManager.deleteBackup(backupId);
      const backups = await backupManager.listBackups();
      expect(backups.length).toBe(0);
    });

    it('should handle deletion of non-existent backup', async () => {
      await expect(backupManager.deleteBackup('non-existent-backup')).rejects.toThrow();
    });
  });
}); 