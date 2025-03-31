import { ContainerLifecycleManager, ContainerConfig, BackupConfig } from '../ContainerLifecycleManager';
import { exec, ExecException } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

jest.mock('child_process');
jest.mock('fs');
jest.mock('path');

const execAsync = promisify(exec);
const mockedExec = exec as jest.MockedFunction<typeof exec>;
const mockedFs = fs as jest.Mocked<typeof fs>;
const mockedPath = path as jest.Mocked<typeof path>;

describe('ContainerLifecycleManager', () => {
  let manager: ContainerLifecycleManager;

  beforeEach(() => {
    manager = new ContainerLifecycleManager();
    jest.clearAllMocks();
  });

  describe('container creation', () => {
    const mockConfig: ContainerConfig = {
      image: 'test-image:latest',
      name: 'test-container',
      env: {
        TEST_VAR: 'test-value'
      },
      volumes: ['/host/path:/container/path'],
      ports: ['8080:80'],
      restartPolicy: 'unless-stopped',
      healthCheck: {
        test: ['CMD', 'curl', '-f', 'http://localhost:80/health'],
        interval: '30s',
        timeout: '10s',
        retries: 3,
        startPeriod: '40s'
      }
    };

    it('should create container with config', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, 'Container ID: abc123\nName: test-container\nStatus: created', '');
        }
        return {} as any;
      });

      await manager.createContainer(mockConfig);

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker create'),
        expect.any(Function)
      );
    });

    it('should handle container creation errors', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(new Error('Failed to create container') as ExecException, '', '');
        }
        return {} as any;
      });

      await expect(manager.createContainer(mockConfig)).rejects.toThrow('Failed to create container');
    });
  });

  describe('container lifecycle', () => {
    beforeEach(() => {
      // Mock container state
      (manager as any).containerState = {
        id: 'abc123',
        name: 'test-container',
        status: 'stopped',
        health: 'starting',
        startedAt: new Date().toISOString()
      };
    });

    it('should start container', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '', '');
        }
        return {} as any;
      });

      await manager.startContainer();

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker start'),
        expect.any(Function)
      );
    });

    it('should stop container', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '', '');
        }
        return {} as any;
      });

      await manager.stopContainer();

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker stop'),
        expect.any(Function)
      );
    });

    it('should pause container', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '', '');
        }
        return {} as any;
      });

      await manager.pauseContainer();

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker pause'),
        expect.any(Function)
      );
    });

    it('should resume container', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '', '');
        }
        return {} as any;
      });

      await manager.resumeContainer();

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker unpause'),
        expect.any(Function)
      );
    });
  });

  describe('backup and restore', () => {
    const mockBackupConfig: BackupConfig = {
      enabled: true,
      schedule: '0 0 * * *',
      retention: 7,
      path: './backups'
    };

    beforeEach(() => {
      // Mock container state
      (manager as any).containerState = {
        id: 'abc123',
        name: 'test-container',
        status: 'running',
        health: 'healthy',
        startedAt: new Date().toISOString()
      };

      // Mock fs and path
      mockedFs.existsSync.mockReturnValue(true);
      mockedFs.mkdirSync.mockImplementation(() => undefined);
      mockedFs.readdirSync.mockReturnValue([
        {
          name: 'test-container-2024-01-01.tar',
          isFile: () => true,
          isDirectory: () => false,
          isSymbolicLink: () => false,
          isBlockDevice: () => false,
          isCharacterDevice: () => false,
          isFIFO: () => false,
          isSocket: () => false,
          parentPath: './backups',
          path: './backups/test-container-2024-01-01.tar'
        }
      ]);
      mockedFs.statSync.mockReturnValue({ mtime: new Date() } as any);
      mockedFs.unlinkSync.mockImplementation(() => undefined);
      mockedPath.join.mockImplementation((...args) => args.join('/'));
    });

    it('should create backup', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '', '');
        }
        return {} as any;
      });

      await manager.createBackup();

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker commit'),
        expect.any(Function)
      );
    });

    it('should restore backup', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '', '');
        }
        return {} as any;
      });

      await manager.restoreBackup('./backups/test-container-2024-01-01.tar');

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker load'),
        expect.any(Function)
      );
    });

    it('should configure backup schedule', async () => {
      await manager.configureBackup(mockBackupConfig);

      // Verify that backup interval is set
      expect(setInterval).toHaveBeenCalled();
    });

    it('should validate backup config', async () => {
      const invalidConfig = {
        ...mockBackupConfig,
        retention: 0
      };

      await expect(manager.configureBackup(invalidConfig)).rejects.toThrow('Backup retention must be at least 1');
    });

    it('should cleanup old backups', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '', '');
        }
        return {} as any;
      });

      await manager.createBackup();

      expect(mockedFs.unlinkSync).toHaveBeenCalled();
    });
  });

  describe('cleanup', () => {
    beforeEach(() => {
      // Mock container state
      (manager as any).containerState = {
        id: 'abc123',
        name: 'test-container',
        status: 'running',
        health: 'healthy',
        startedAt: new Date().toISOString()
      };
    });

    it('should cleanup resources', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '', '');
        }
        return {} as any;
      });

      await manager.cleanup();

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker rm'),
        expect.any(Function)
      );
      expect(clearInterval).toHaveBeenCalled();
    });
  });
}); 