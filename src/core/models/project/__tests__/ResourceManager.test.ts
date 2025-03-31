import { ResourceManager, ResourceLimits, AutoScalingConfig } from '../ResourceManager';
import { exec, ExecException } from 'child_process';
import { promisify } from 'util';

jest.mock('child_process');

const execAsync = promisify(exec);
const mockedExec = exec as jest.MockedFunction<typeof exec>;

describe('ResourceManager', () => {
  let manager: ResourceManager;

  beforeEach(() => {
    manager = new ResourceManager();
    jest.clearAllMocks();
  });

  describe('resource limits', () => {
    const mockLimits: ResourceLimits = {
      cpu: {
        shares: 2048,
        period: 100000,
        quota: 50000
      },
      memory: {
        limit: '4g',
        swap: '8g',
        reservation: '2g'
      },
      storage: {
        size: '50g',
        iops: 2000
      }
    };

    it('should set resource limits', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '', '');
        }
        return {} as any;
      });

      await manager.setResourceLimits('test-container', mockLimits);

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker update'),
        expect.any(Function)
      );
    });

    it('should handle resource limit errors', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(new Error('Failed to set limits') as ExecException, '', '');
        }
        return {} as any;
      });

      await expect(manager.setResourceLimits('test-container', mockLimits)).rejects.toThrow('Failed to set limits');
    });
  });

  describe('resource monitoring', () => {
    it('should start monitoring', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '50%,2g/4g,1.2GB/2.4GB', '');
        }
        return {} as any;
      });

      await manager.startMonitoring('test-container');

      // Verify that monitoring interval is set
      expect(setInterval).toHaveBeenCalled();
    });

    it('should parse resource metrics', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '75%,3g/4g,2.4GB/2.4GB', '');
        }
        return {} as any;
      });

      const metrics = await manager.getResourceMetrics('test-container');

      expect(metrics.cpu.percentage).toBe(75);
      expect(metrics.memory.usage).toBe('3g/4g');
      expect(metrics.storage.usage).toBe('2.4GB/2.4GB');
    });

    it('should handle monitoring errors', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(new Error('Failed to get metrics') as ExecException, '', '');
        }
        return {} as any;
      });

      await expect(manager.startMonitoring('test-container')).rejects.toThrow('Failed to start resource monitoring');
    });
  });

  describe('auto-scaling', () => {
    const mockConfig: AutoScalingConfig = {
      enabled: true,
      minInstances: 2,
      maxInstances: 10,
      targetCPUUtilization: 70,
      targetMemoryUtilization: 80,
      scaleUpThreshold: 80,
      scaleDownThreshold: 20,
      cooldownPeriod: 300
    };

    it('should configure auto-scaling', async () => {
      await manager.configureAutoScaling(mockConfig);

      // Verify that auto-scaling is enabled
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '90%,4g/4g,2.4GB/2.4GB', '');
        }
        return {} as any;
      });

      await manager.startMonitoring('test-container');
      expect(setInterval).toHaveBeenCalled();
    });

    it('should validate auto-scaling config', async () => {
      const invalidConfig = {
        ...mockConfig,
        minInstances: 0
      };

      await expect(manager.configureAutoScaling(invalidConfig)).rejects.toThrow('Minimum instances must be at least 1');
    });

    it('should scale up when threshold is exceeded', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '90%,4g/4g,2.4GB/2.4GB', '');
        }
        return {} as any;
      });

      await manager.configureAutoScaling(mockConfig);
      await manager.startMonitoring('test-container');

      // Verify scale up command
      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker service scale'),
        expect.any(Function)
      );
    });

    it('should scale down when below threshold', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '10%,1g/4g,0.5GB/2.4GB', '');
        }
        return {} as any;
      });

      await manager.configureAutoScaling(mockConfig);
      await manager.startMonitoring('test-container');

      // Verify scale down command
      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker service scale'),
        expect.any(Function)
      );
    });
  });

  describe('cleanup', () => {
    it('should stop monitoring on cleanup', async () => {
      await manager.cleanup();
      expect(clearInterval).toHaveBeenCalled();
    });
  });
}); 