import { NetworkManager, PortMapping, SecurityRule, ProxyConfig } from '../NetworkManager';
import { exec, ExecException } from 'child_process';
import { promisify } from 'util';

jest.mock('child_process');

const execAsync = promisify(exec);
const mockedExec = exec as jest.MockedFunction<typeof exec>;

describe('NetworkManager', () => {
  let manager: NetworkManager;

  beforeEach(() => {
    manager = new NetworkManager();
    jest.clearAllMocks();
  });

  describe('createNetwork', () => {
    it('should create a new network', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '', '');
        }
        return {} as any;
      });

      await manager.createNetwork();

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker network create'),
        expect.any(Function)
      );
    });

    it('should handle existing network', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (command.includes('docker network ls')) {
          if (callback) {
            callback(null, 'ade-network\n', '');
          }
        } else if (callback) {
          callback(null, '', '');
        }
        return {} as any;
      });

      await manager.createNetwork();

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker network ls'),
        expect.any(Function)
      );
      expect(mockedExec).not.toHaveBeenCalledWith(
        expect.stringContaining('docker network create'),
        expect.any(Function)
      );
    });

    it('should handle network creation errors', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(new Error('Network creation failed') as ExecException, '', '');
        }
        return {} as any;
      });

      await expect(manager.createNetwork()).rejects.toThrow('Network creation failed');
    });
  });

  describe('port mappings', () => {
    const mockPortMapping: PortMapping = {
      containerPort: 3000,
      hostPort: 8080,
      protocol: 'tcp',
      description: 'Web server port'
    };

    it('should add valid port mapping', async () => {
      await manager.addPortMapping(mockPortMapping);

      // Verify the mapping was added
      const containerId = 'test-container';
      await manager.configurePortMappings(containerId);

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker container update'),
        expect.any(Function)
      );
    });

    it('should validate port mapping', async () => {
      const invalidMapping = {
        ...mockPortMapping,
        containerPort: 0
      };

      await expect(manager.addPortMapping(invalidMapping)).rejects.toThrow('Invalid container port');
    });
  });

  describe('security rules', () => {
    const mockSecurityRule: SecurityRule = {
      type: 'allow',
      protocol: 'tcp',
      source: '192.168.1.0/24',
      destination: '10.0.0.0/24',
      port: 80,
      description: 'Allow web traffic'
    };

    it('should add valid security rule', async () => {
      await manager.addSecurityRule(mockSecurityRule);

      // Verify the rule was added
      await manager.setupSecurityRules();

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('iptables'),
        expect.any(Function)
      );
    });

    it('should validate security rule', async () => {
      const invalidRule = {
        ...mockSecurityRule,
        type: 'invalid' as any
      };

      await expect(manager.addSecurityRule(invalidRule)).rejects.toThrow('Invalid rule type');
    });

    it('should validate IP ranges', async () => {
      const invalidRule = {
        ...mockSecurityRule,
        source: 'invalid-ip'
      };

      await expect(manager.addSecurityRule(invalidRule)).rejects.toThrow('Invalid source IP range');
    });
  });

  describe('proxy configuration', () => {
    const mockProxyConfig: ProxyConfig = {
      target: 'web-service',
      port: 80,
      path: '/api',
      rewrite: true,
      headers: {
        'X-Forwarded-For': '$remote_addr'
      }
    };

    it('should add valid proxy config', async () => {
      await manager.addProxyConfig(mockProxyConfig);

      // Verify the proxy was configured
      await manager.setupProxy(mockProxyConfig);

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker service create'),
        expect.any(Function)
      );
    });

    it('should validate proxy config', async () => {
      const invalidConfig = {
        ...mockProxyConfig,
        port: 0
      };

      await expect(manager.addProxyConfig(invalidConfig)).rejects.toThrow('Invalid port number');
    });

    it('should validate SSL configuration', async () => {
      const invalidConfig = {
        ...mockProxyConfig,
        ssl: {
          enabled: true
        }
      };

      await expect(manager.addProxyConfig(invalidConfig)).rejects.toThrow(
        'SSL certificate and key are required when SSL is enabled'
      );
    });
  });

  describe('cleanup', () => {
    it('should clean up all resources', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(null, '', '');
        }
        return {} as any;
      });

      await manager.cleanup();

      expect(mockedExec).toHaveBeenCalledWith(
        expect.stringContaining('docker network rm'),
        expect.any(Function)
      );
    });

    it('should handle cleanup errors', async () => {
      mockedExec.mockImplementation((command, options, callback) => {
        if (callback) {
          callback(new Error('Cleanup failed') as ExecException, '', '');
        }
        return {} as any;
      });

      await expect(manager.cleanup()).rejects.toThrow('Cleanup failed');
    });
  });
}); 