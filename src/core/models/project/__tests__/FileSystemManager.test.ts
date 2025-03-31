import { FileSystemManager, VolumeConfig } from '../FileSystemManager';
import * as fs from 'fs';
import * as path from 'path';
import { exec, ExecException } from 'child_process';
import { promisify } from 'util';

jest.mock('fs');
jest.mock('path');
jest.mock('child_process');

const execAsync = promisify(exec);
const mockedExec = exec as jest.MockedFunction<typeof exec>;

describe('FileSystemManager', () => {
  let manager: FileSystemManager;
  const mockProjectRoot = '/mock/project/root';

  beforeEach(() => {
    manager = new FileSystemManager(mockProjectRoot);
    jest.clearAllMocks();
  });

  describe('initialize', () => {
    it('should create workspace directories', async () => {
      await manager.initialize();

      expect(fs.promises.mkdir).toHaveBeenCalledWith(
        expect.stringContaining('src'),
        expect.any(Object)
      );
      expect(fs.promises.mkdir).toHaveBeenCalledWith(
        expect.stringContaining('dist'),
        expect.any(Object)
      );
      expect(fs.promises.mkdir).toHaveBeenCalledWith(
        expect.stringContaining('tests'),
        expect.any(Object)
      );
    });

    it('should set up permissions', async () => {
      await manager.initialize();

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('chown'),
        expect.any(Function)
      );
      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('chmod'),
        expect.any(Function)
      );
    });

    it('should handle errors during initialization', async () => {
      (fs.promises.mkdir as jest.Mock).mockRejectedValue(new Error('Failed to create directory'));

      await expect(manager.initialize()).rejects.toThrow('Failed to create directory');
    });
  });

  describe('addVolume', () => {
    const mockVolumeConfig: VolumeConfig = {
      name: 'test-volume',
      mountPath: 'data',
      type: 'volume',
      options: {
        readonly: false,
        size: '10G'
      }
    };

    it('should add a valid volume configuration', async () => {
      await manager.addVolume(mockVolumeConfig);

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker volume create'),
        expect.any(Function)
      );
    });

    it('should validate volume configuration', async () => {
      const invalidConfig = {
        ...mockVolumeConfig,
        type: 'invalid-type' as any
      };

      await expect(manager.addVolume(invalidConfig)).rejects.toThrow('Invalid volume type');
    });

    it('should handle errors when creating Docker volume', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(new Error('Docker error') as ExecException, '', '');
        }
        return {} as any;
      });

      await expect(manager.addVolume(mockVolumeConfig)).rejects.toThrow('Docker error');
    });
  });

  describe('file synchronization', () => {
    it('should start file synchronization', async () => {
      await manager.startFileSync();

      expect(fs.watch).toHaveBeenCalledWith(
        mockProjectRoot,
        expect.objectContaining({ recursive: true }),
        expect.any(Function)
      );
    });

    it('should stop file synchronization', async () => {
      const mockWatcher = {
        close: jest.fn()
      };
      (fs.watch as jest.Mock).mockReturnValue(mockWatcher);

      await manager.startFileSync();
      await manager.stopFileSync();

      expect(mockWatcher.close).toHaveBeenCalled();
    });

    it('should handle file changes', async () => {
      const mockWatcher = {
        close: jest.fn()
      };
      (fs.watch as jest.Mock).mockReturnValue(mockWatcher);

      await manager.startFileSync();

      // Simulate a file change event
      const callback = (fs.watch as jest.Mock).mock.calls[0][2];
      callback('change', 'test.txt');

      // Verify that the file change was handled
      expect(fs.promises.stat).toHaveBeenCalledWith(
        expect.stringContaining('test.txt')
      );
    });

    it('should ignore specified patterns', async () => {
      const mockWatcher = {
        close: jest.fn()
      };
      (fs.watch as jest.Mock).mockReturnValue(mockWatcher);

      await manager.startFileSync();

      // Simulate a file change event for an ignored file
      const callback = (fs.watch as jest.Mock).mock.calls[0][2];
      callback('change', 'node_modules/test.txt');

      // Verify that the file was ignored
      expect(fs.promises.stat).not.toHaveBeenCalled();
    });
  });

  describe('cleanup', () => {
    it('should clean up resources', async () => {
      const mockWatcher = {
        close: jest.fn()
      };
      (fs.watch as jest.Mock).mockReturnValue(mockWatcher);

      await manager.startFileSync();
      await manager.cleanup();

      expect(mockWatcher.close).toHaveBeenCalled();
      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker volume rm'),
        expect.any(Function)
      );
    });

    it('should handle errors during cleanup', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(new Error('Cleanup error') as ExecException, '', '');
        }
        return {} as any;
      });

      await expect(manager.cleanup()).rejects.toThrow('Cleanup error');
    });
  });
}); 