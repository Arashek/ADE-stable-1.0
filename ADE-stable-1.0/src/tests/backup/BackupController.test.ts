import { BackupController } from '../../controllers/backup/BackupController';
import { BackupService } from '../../services/backup/BackupService';
import { Logger } from '../../core/logging/Logger';
import { Request, Response } from 'express';

jest.mock('../../services/backup/BackupService');
jest.mock('../../core/logging/Logger');

describe('BackupController', () => {
  let backupController: BackupController;
  let backupService: jest.Mocked<BackupService>;
  let logger: jest.Mocked<Logger>;
  let mockReq: Partial<Request>;
  let mockRes: Partial<Response>;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Create mocked dependencies
    backupService = new BackupService(
      {} as any,
      {} as any,
      {} as any
    ) as jest.Mocked<BackupService>;
    logger = new Logger() as jest.Mocked<Logger>;

    // Create backup controller instance
    backupController = new BackupController(backupService, logger);

    // Setup mock request and response
    mockReq = {
      body: {},
      params: {},
      query: {}
    };
    mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
  });

  describe('createBackup', () => {
    it('should create a backup successfully', async () => {
      mockReq.body = {
        type: 'container',
        tags: ['test']
      };
      backupService.createBackup.mockResolvedValue({
        success: true,
        metadata: {
          id: 'test-backup',
          timestamp: new Date(),
          type: 'container',
          status: 'completed',
          size: 1000,
          checksum: 'test-checksum'
        },
        path: '/path/to/backup'
      });

      await backupController.createBackup(mockReq as Request, mockRes as Response);

      expect(backupService.createBackup).toHaveBeenCalledWith('container', ['test']);
      expect(mockRes.status).toHaveBeenCalledWith(201);
      expect(mockRes.json).toHaveBeenCalled();
    });

    it('should handle invalid backup type', async () => {
      mockReq.body = {
        type: 'invalid-type'
      };

      await backupController.createBackup(mockReq as Request, mockRes as Response);

      expect(mockRes.status).toHaveBeenCalledWith(400);
      expect(mockRes.json).toHaveBeenCalledWith({
        error: 'Invalid backup type. Must be either "container" or "project".'
      });
    });

    it('should handle backup creation failure', async () => {
      mockReq.body = {
        type: 'container'
      };
      backupService.createBackup.mockRejectedValue(new Error('Test error'));

      await backupController.createBackup(mockReq as Request, mockRes as Response);

      expect(mockRes.status).toHaveBeenCalledWith(500);
      expect(mockRes.json).toHaveBeenCalledWith({
        error: 'Failed to create backup',
        details: 'Test error'
      });
    });
  });

  describe('restoreBackup', () => {
    it('should restore a backup successfully', async () => {
      mockReq.params = { backupId: 'test-backup' };
      backupService.restoreBackup.mockResolvedValue({
        success: true,
        metadata: {
          id: 'test-backup',
          timestamp: new Date(),
          type: 'container',
          status: 'completed',
          size: 1000,
          checksum: 'test-checksum'
        },
        path: '/path/to/backup'
      });

      await backupController.restoreBackup(mockReq as Request, mockRes as Response);

      expect(backupService.restoreBackup).toHaveBeenCalledWith('test-backup');
      expect(mockRes.status).toHaveBeenCalledWith(200);
      expect(mockRes.json).toHaveBeenCalled();
    });

    it('should handle missing backup ID', async () => {
      mockReq.params = {};

      await backupController.restoreBackup(mockReq as Request, mockRes as Response);

      expect(mockRes.status).toHaveBeenCalledWith(400);
      expect(mockRes.json).toHaveBeenCalledWith({
        error: 'Backup ID is required'
      });
    });

    it('should handle restore failure', async () => {
      mockReq.params = { backupId: 'test-backup' };
      backupService.restoreBackup.mockRejectedValue(new Error('Test error'));

      await backupController.restoreBackup(mockReq as Request, mockRes as Response);

      expect(mockRes.status).toHaveBeenCalledWith(500);
      expect(mockRes.json).toHaveBeenCalledWith({
        error: 'Failed to restore backup',
        details: 'Test error'
      });
    });
  });

  describe('listBackups', () => {
    it('should list backups successfully', async () => {
      mockReq.query = {
        type: 'container',
        status: 'completed'
      };
      backupService.listBackups.mockResolvedValue([
        {
          id: 'test-backup',
          timestamp: new Date(),
          type: 'container',
          status: 'completed',
          size: 1000,
          checksum: 'test-checksum'
        }
      ]);

      await backupController.listBackups(mockReq as Request, mockRes as Response);

      expect(backupService.listBackups).toHaveBeenCalledWith({
        type: 'container',
        status: 'completed'
      });
      expect(mockRes.status).toHaveBeenCalledWith(200);
      expect(mockRes.json).toHaveBeenCalled();
    });

    it('should handle list backups failure', async () => {
      backupService.listBackups.mockRejectedValue(new Error('Test error'));

      await backupController.listBackups(mockReq as Request, mockRes as Response);

      expect(mockRes.status).toHaveBeenCalledWith(500);
      expect(mockRes.json).toHaveBeenCalledWith({
        error: 'Failed to list backups',
        details: 'Test error'
      });
    });
  });

  describe('deleteBackup', () => {
    it('should delete a backup successfully', async () => {
      mockReq.params = { backupId: 'test-backup' };
      backupService.deleteBackup.mockResolvedValue(undefined);

      await backupController.deleteBackup(mockReq as Request, mockRes as Response);

      expect(backupService.deleteBackup).toHaveBeenCalledWith('test-backup');
      expect(mockRes.status).toHaveBeenCalledWith(204);
    });

    it('should handle missing backup ID', async () => {
      mockReq.params = {};

      await backupController.deleteBackup(mockReq as Request, mockRes as Response);

      expect(mockRes.status).toHaveBeenCalledWith(400);
      expect(mockRes.json).toHaveBeenCalledWith({
        error: 'Backup ID is required'
      });
    });

    it('should handle delete backup failure', async () => {
      mockReq.params = { backupId: 'test-backup' };
      backupService.deleteBackup.mockRejectedValue(new Error('Test error'));

      await backupController.deleteBackup(mockReq as Request, mockRes as Response);

      expect(mockRes.status).toHaveBeenCalledWith(500);
      expect(mockRes.json).toHaveBeenCalledWith({
        error: 'Failed to delete backup',
        details: 'Test error'
      });
    });
  });

  describe('getActiveBackups', () => {
    it('should get active backups successfully', async () => {
      backupService.getActiveBackups.mockReturnValue(['test-backup']);

      await backupController.getActiveBackups(mockReq as Request, mockRes as Response);

      expect(backupService.getActiveBackups).toHaveBeenCalled();
      expect(mockRes.status).toHaveBeenCalledWith(200);
      expect(mockRes.json).toHaveBeenCalledWith(['test-backup']);
    });

    it('should handle get active backups failure', async () => {
      backupService.getActiveBackups.mockImplementation(() => {
        throw new Error('Test error');
      });

      await backupController.getActiveBackups(mockReq as Request, mockRes as Response);

      expect(mockRes.status).toHaveBeenCalledWith(500);
      expect(mockRes.json).toHaveBeenCalledWith({
        error: 'Failed to get active backups',
        details: 'Test error'
      });
    });
  });

  describe('getActiveRestores', () => {
    it('should get active restores successfully', async () => {
      backupService.getActiveRestores.mockReturnValue(['test-restore']);

      await backupController.getActiveRestores(mockReq as Request, mockRes as Response);

      expect(backupService.getActiveRestores).toHaveBeenCalled();
      expect(mockRes.status).toHaveBeenCalledWith(200);
      expect(mockRes.json).toHaveBeenCalledWith(['test-restore']);
    });

    it('should handle get active restores failure', async () => {
      backupService.getActiveRestores.mockImplementation(() => {
        throw new Error('Test error');
      });

      await backupController.getActiveRestores(mockReq as Request, mockRes as Response);

      expect(mockRes.status).toHaveBeenCalledWith(500);
      expect(mockRes.json).toHaveBeenCalledWith({
        error: 'Failed to get active restores',
        details: 'Test error'
      });
    });
  });
}); 