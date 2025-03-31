import { ContainerExporter } from '../ContainerExporter';
import Docker from 'dockerode';
import * as fs from 'fs';
import * as path from 'path';
import * as tar from 'tar';
import { PassThrough } from 'stream';

jest.mock('dockerode');
jest.mock('fs');
jest.mock('path');
jest.mock('tar');

describe('ContainerExporter', () => {
  let containerExporter: ContainerExporter;
  let mockDocker: jest.Mocked<Docker>;
  const mockContainerId = 'test-container-id';
  const mockOutputPath = '/mock/output';
  const mockContainerInfo = {
    Name: '/test-container',
    Config: {
      Image: 'test-image:latest',
      Env: ['NODE_ENV=development']
    },
    State: {
      Status: 'running'
    },
    Created: '2024-03-26T00:00:00Z',
    Mounts: {
      'test-volume': {
        Type: 'volume',
        Source: '/var/lib/docker/volumes/test-volume',
        Destination: '/data'
      }
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockDocker = new Docker() as jest.Mocked<Docker>;
    containerExporter = new ContainerExporter(mockDocker);
    
    // Mock path.join
    (path.join as jest.Mock).mockImplementation((...args) => args.join('/'));
    
    // Mock fs.promises
    (fs.promises.mkdir as jest.Mock).mockResolvedValue(undefined);
    (fs.promises.writeFile as jest.Mock).mockResolvedValue(undefined);
    (fs.promises.readFile as jest.Mock).mockResolvedValue(JSON.stringify(mockContainerInfo.Config));
    (fs.promises.rm as jest.Mock).mockResolvedValue(undefined);
    
    // Mock fs.createWriteStream
    (fs.createWriteStream as jest.Mock).mockReturnValue({
      on: jest.fn().mockReturnThis(),
      pipe: jest.fn().mockReturnThis()
    });
    
    // Mock fs.createReadStream
    (fs.createReadStream as jest.Mock).mockReturnValue({
      pipe: jest.fn().mockReturnThis()
    });
    
    // Mock tar
    (tar.create as jest.Mock).mockResolvedValue(undefined);
    (tar.extract as jest.Mock).mockResolvedValue(undefined);
  });

  describe('exportContainer', () => {
    const mockOptions = {
      includeVolumes: true,
      includeConfig: true,
      outputPath: mockOutputPath
    };

    it('should export container with all options enabled', async () => {
      const mockStream = new PassThrough();
      mockStream.end(); // End the stream
      
      const mockContainer = {
        export: jest.fn().mockResolvedValue(mockStream),
        inspect: jest.fn().mockResolvedValue(mockContainerInfo)
      };

      mockDocker.getContainer.mockReturnValue(mockContainer as any);

      const archivePath = await containerExporter.exportContainer(mockContainerId, mockOptions);

      expect(mockContainer.export).toHaveBeenCalled();
      expect(fs.promises.mkdir).toHaveBeenCalledWith(mockOutputPath, { recursive: true });
      expect(fs.promises.writeFile).toHaveBeenCalledWith(
        expect.stringContaining('container-config.json'),
        expect.any(String)
      );
      expect(tar.create).toHaveBeenCalledWith(
        expect.objectContaining({
          gzip: true,
          file: expect.stringContaining('container-export.tar.gz')
        }),
        expect.arrayContaining([
          'container.tar',
          'volumes',
          'container-config.json',
          'deployment-manifest.json'
        ])
      );
      expect(archivePath).toContain('container-export.tar.gz');
    });

    it('should handle errors during export', async () => {
      const error = new Error('Export failed');
      const mockContainer = {
        export: jest.fn().mockRejectedValue(error)
      };

      mockDocker.getContainer.mockReturnValue(mockContainer as any);

      await expect(containerExporter.exportContainer(mockContainerId, mockOptions))
        .rejects.toThrow(error);
    });
  });

  describe('deployContainer', () => {
    const mockExportPath = '/mock/export/container-export.tar.gz';
    const mockDeployOptions = {
      target: 'local' as const
    };

    it('should deploy container to local environment', async () => {
      const mockManifest = {
        containerId: mockContainerId,
        containerInfo: {
          name: 'test-container',
          image: 'test-image:latest'
        }
      };

      (fs.promises.readFile as jest.Mock).mockResolvedValue(JSON.stringify(mockManifest));

      const mockImage = {
        tag: jest.fn().mockResolvedValue(undefined)
      };

      const mockContainer = {
        start: jest.fn().mockResolvedValue(undefined)
      };

      const mockReadStream = fs.createReadStream('dummy');
      mockDocker.importImage.mockResolvedValue(mockReadStream);
      mockDocker.createContainer.mockResolvedValue(mockContainer as any);
      mockDocker.getImage.mockReturnValue(mockImage as any);

      await containerExporter.deployContainer(mockExportPath, mockDeployOptions);

      expect(tar.extract).toHaveBeenCalledWith(
        expect.objectContaining({
          file: mockExportPath
        })
      );
      expect(mockDocker.importImage).toHaveBeenCalled();
      expect(mockDocker.createContainer).toHaveBeenCalled();
      expect(mockContainer.start).toHaveBeenCalled();
    });

    it('should deploy container to remote environment', async () => {
      const mockManifest = {
        containerId: mockContainerId,
        containerInfo: {
          name: 'test-container',
          image: 'test-image:latest'
        }
      };

      const mockRemoteOptions = {
        target: 'remote' as const,
        remoteUrl: 'ssh://user@host',
        credentials: {
          username: 'testuser',
          password: 'testpass',
          registry: 'test-registry'
        }
      };

      (fs.promises.readFile as jest.Mock).mockResolvedValue(JSON.stringify(mockManifest));

      const mockStream = new PassThrough();
      mockStream.end(); // End the stream
      
      const mockImage = {
        tag: jest.fn().mockResolvedValue(undefined),
        push: jest.fn().mockResolvedValue(mockStream)
      };

      mockDocker.getImage.mockReturnValue(mockImage as any);

      await containerExporter.deployContainer(mockExportPath, mockRemoteOptions);

      expect(mockImage.tag).toHaveBeenCalledWith({
        repo: 'test-registry/testuser/test-image'
      });
      expect(mockImage.push).toHaveBeenCalledWith({
        authconfig: {
          username: 'testuser',
          password: 'testpass'
        }
      });
    });

    it('should handle errors during deployment', async () => {
      const error = new Error('Deployment failed');
      (tar.extract as jest.Mock).mockRejectedValue(error);

      await expect(containerExporter.deployContainer(mockExportPath, mockDeployOptions))
        .rejects.toThrow(error);
    });
  });
}); 