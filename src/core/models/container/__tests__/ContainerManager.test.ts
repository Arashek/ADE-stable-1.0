import { ContainerManager } from '../ContainerManager';
import { TemplateLoader } from '../TemplateLoader';
import { ContainerTemplate, ProjectType, ContainerConfig, ContainerState } from '../types';
import Docker from 'dockerode';

jest.mock('dockerode');
jest.mock('../TemplateLoader');

describe('ContainerManager', () => {
  let containerManager: ContainerManager;
  let mockDocker: jest.Mocked<Docker>;
  let mockTemplateLoader: jest.Mocked<TemplateLoader>;
  const mockTemplate: ContainerTemplate = {
    id: 'test-template',
    name: 'Test Template',
    projectType: ProjectType.WEB,
    baseImage: 'node:18-alpine',
    defaultResources: {
      cpu: { limit: 2, reservation: 1 },
      memory: { limit: '4g', reservation: '2g' },
      disk: { limit: '20g', reservation: '10g' }
    },
    defaultEnvironment: [
      { name: 'NODE_ENV', value: 'development' }
    ],
    defaultPorts: [
      { hostPort: 3000, containerPort: 3000, protocol: 'tcp' }
    ],
    defaultVolumes: [
      { source: '/app', target: '/app', type: 'bind' }
    ],
    defaultNetworks: [
      { name: 'test-network', driver: 'bridge' }
    ],
    defaultHealthCheck: {
      test: ['CMD', 'curl', '-f', 'http://localhost:3000/health'],
      interval: '30s',
      timeout: '10s',
      retries: 3,
      startPeriod: '0s'
    },
    defaultCommand: ['npm', 'start'],
    defaultWorkingDir: '/app',
    defaultUser: 'node',
    description: 'Test template for unit testing',
    tags: ['test', 'web']
  };

  const mockConfig: ContainerConfig = {
    name: 'test-container',
    image: mockTemplate.baseImage,
    projectType: ProjectType.WEB,
    resources: mockTemplate.defaultResources,
    environment: mockTemplate.defaultEnvironment,
    ports: mockTemplate.defaultPorts,
    volumes: mockTemplate.defaultVolumes,
    networks: mockTemplate.defaultNetworks,
    healthCheck: mockTemplate.defaultHealthCheck,
    command: mockTemplate.defaultCommand,
    workingDir: mockTemplate.defaultWorkingDir,
    user: mockTemplate.defaultUser
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockDocker = new Docker() as jest.Mocked<Docker>;
    mockTemplateLoader = new TemplateLoader() as jest.Mocked<TemplateLoader>;
    containerManager = new ContainerManager();
  });

  describe('createContainer', () => {
    it('should create a container from a template', async () => {
      const mockContainer = {
        id: 'test-container-id',
        start: jest.fn(),
        inspect: jest.fn().mockResolvedValue({
          State: { Status: 'running' }
        })
      };

      mockDocker.createContainer.mockResolvedValue(mockContainer as any);
      mockTemplateLoader.getTemplate.mockReturnValue(mockTemplate);

      const container = await containerManager.createContainer(mockConfig);

      expect(mockDocker.createContainer).toHaveBeenCalledWith(
        expect.objectContaining({
          Image: mockTemplate.baseImage,
          name: mockConfig.name,
          Env: mockConfig.environment.map(env => `${env.name}=${env.value}`),
          WorkingDir: mockConfig.workingDir,
          User: mockConfig.user,
          Cmd: mockConfig.command,
          HostConfig: expect.objectContaining({
            PortBindings: {
              '3000/tcp': [{ HostPort: '3000' }]
            },
            Binds: mockConfig.volumes.map(vol => `${vol.source}:${vol.target}`),
            NetworkMode: mockConfig.networks[0].name,
            RestartPolicy: { Name: 'unless-stopped' },
            Resources: expect.objectContaining({
              NanoCpus: 2000000000,
              CpuPeriod: 100000,
              CpuQuota: 200000000,
              Memory: 4294967296,
              MemorySwap: 4294967296,
              MemoryReservation: 2147483648
            })
          })
        })
      );

      expect(container).toBeDefined();
      expect(container).toBe('test-container-id');
    });

    it('should handle errors when creating a container', async () => {
      const error = new Error('Failed to create container');
      mockDocker.createContainer.mockRejectedValue(error);
      mockTemplateLoader.getTemplate.mockReturnValue(mockTemplate);

      await expect(containerManager.createContainer(mockConfig))
        .rejects.toThrow(error);
    });
  });

  describe('startContainer', () => {
    it('should start a container', async () => {
      const mockContainer = {
        start: jest.fn(),
        inspect: jest.fn().mockResolvedValue({
          State: { Status: 'running' }
        })
      };

      mockDocker.getContainer.mockReturnValue(mockContainer as any);

      await containerManager.startContainer('test-container-id');

      expect(mockContainer.start).toHaveBeenCalled();
    });

    it('should handle errors when starting a container', async () => {
      const error = new Error('Failed to start container');
      const mockContainer = {
        start: jest.fn().mockRejectedValue(error)
      };

      mockDocker.getContainer.mockReturnValue(mockContainer as any);

      await expect(containerManager.startContainer('test-container-id'))
        .rejects.toThrow(error);
    });
  });

  describe('stopContainer', () => {
    it('should stop a container', async () => {
      const mockContainer = {
        stop: jest.fn(),
        inspect: jest.fn().mockResolvedValue({
          State: { Status: 'exited' }
        })
      };

      mockDocker.getContainer.mockReturnValue(mockContainer as any);

      await containerManager.stopContainer('test-container-id');

      expect(mockContainer.stop).toHaveBeenCalled();
    });

    it('should handle errors when stopping a container', async () => {
      const error = new Error('Failed to stop container');
      const mockContainer = {
        stop: jest.fn().mockRejectedValue(error)
      };

      mockDocker.getContainer.mockReturnValue(mockContainer as any);

      await expect(containerManager.stopContainer('test-container-id'))
        .rejects.toThrow(error);
    });
  });

  describe('getContainerStatus', () => {
    it('should return container status', async () => {
      const mockContainer = {
        inspect: jest.fn().mockResolvedValue({
          State: {
            Status: 'running',
            Health: { Status: 'healthy' }
          },
          Config: {
            Image: 'node:18-alpine',
            Env: ['NODE_ENV=development']
          }
        })
      };

      mockDocker.getContainer.mockReturnValue(mockContainer as any);

      const status = await containerManager.getContainerStatus('test-container-id');

      expect(status).toEqual({
        state: ContainerState.RUNNING,
        health: 'healthy',
        image: 'node:18-alpine',
        environment: ['NODE_ENV=development']
      });
    });

    it('should handle errors when getting container status', async () => {
      const error = new Error('Failed to get container status');
      const mockContainer = {
        inspect: jest.fn().mockRejectedValue(error)
      };

      mockDocker.getContainer.mockReturnValue(mockContainer as any);

      await expect(containerManager.getContainerStatus('test-container-id'))
        .rejects.toThrow(error);
    });
  });

  describe('getContainerLogs', () => {
    it('should return container logs', async () => {
      const mockContainer = {
        logs: jest.fn().mockResolvedValue('Container logs...')
      };

      mockDocker.getContainer.mockReturnValue(mockContainer as any);

      const logs = await containerManager.getContainerLogs('test-container-id');

      expect(logs).toBe('Container logs...');
    });

    it('should handle errors when getting container logs', async () => {
      const error = new Error('Failed to get container logs');
      const mockContainer = {
        logs: jest.fn().mockRejectedValue(error)
      };

      mockDocker.getContainer.mockReturnValue(mockContainer as any);

      await expect(containerManager.getContainerLogs('test-container-id'))
        .rejects.toThrow(error);
    });
  });

  describe('getContainerResources', () => {
    it('should return container resource usage', async () => {
      const mockContainer = {
        stats: jest.fn().mockResolvedValue({
          cpu_stats: {
            cpu_usage: {
              total_usage: 1000000000,
              percpu_usage: [500000000, 500000000]
            }
          },
          memory_stats: {
            usage: 2147483648,
            limit: 4294967296
          },
          blkio_stats: {
            io_service_bytes_recursive: [
              { major: 8, minor: 0, op: 'Read', value: 1024 },
              { major: 8, minor: 0, op: 'Write', value: 2048 }
            ]
          }
        })
      };

      mockDocker.getContainer.mockReturnValue(mockContainer as any);

      const resources = await containerManager.getContainerResources('test-container-id');

      expect(resources).toEqual({
        cpu: {
          usage: 1000000000,
          limit: 2000000000,
          percentage: 50
        },
        memory: {
          usage: 2147483648,
          limit: 4294967296,
          percentage: 50
        },
        disk: {
          read: 1024,
          write: 2048
        }
      });
    });

    it('should handle errors when getting container resources', async () => {
      const error = new Error('Failed to get container resources');
      const mockContainer = {
        stats: jest.fn().mockRejectedValue(error)
      };

      mockDocker.getContainer.mockReturnValue(mockContainer as any);

      await expect(containerManager.getContainerResources('test-container-id'))
        .rejects.toThrow(error);
    });
  });

  describe('executeCommand', () => {
    it('should execute a command in a container', async () => {
      const mockExec = {
        start: jest.fn().mockResolvedValue({
          output: { stdout: 'Command output' }
        })
      };

      const mockContainer = {
        exec: jest.fn().mockResolvedValue(mockExec)
      };

      mockDocker.getContainer.mockReturnValue(mockContainer as any);

      const result = await containerManager.executeCommand('test-container-id', 'ls -la');

      expect(result).toEqual({
        stdout: 'Command output',
        stderr: undefined,
        exitCode: 0
      });
    });

    it('should handle errors when executing a command', async () => {
      const error = new Error('Failed to execute command');
      const mockExec = {
        start: jest.fn().mockRejectedValue(error)
      };

      const mockContainer = {
        exec: jest.fn().mockResolvedValue(mockExec)
      };

      mockDocker.getContainer.mockReturnValue(mockContainer as any);

      await expect(containerManager.executeCommand('test-container-id', 'ls -la'))
        .rejects.toThrow(error);
    });
  });
}); 