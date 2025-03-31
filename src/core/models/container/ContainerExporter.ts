import { Logger } from '../logging/Logger';
import Docker from 'dockerode';
import * as fs from 'fs';
import * as path from 'path';
import * as tar from 'tar';
import { ContainerConfig } from './types';

export interface ExportOptions {
  includeVolumes: boolean;
  includeConfig: boolean;
  outputPath: string;
}

export interface DeploymentOptions {
  target: 'local' | 'remote';
  remoteUrl?: string;
  credentials?: {
    username: string;
    password: string;
    registry?: string;
  };
}

export class ContainerExporter {
  private logger: Logger;
  private docker: Docker;

  constructor(docker: Docker) {
    this.logger = new Logger('ContainerExporter');
    this.docker = docker;
  }

  /**
   * Export a container and its contents to a tar archive
   */
  async exportContainer(containerId: string, options: ExportOptions): Promise<string> {
    try {
      this.logger.info(`Exporting container ${containerId}`);
      
      // Create output directory if it doesn't exist
      await fs.promises.mkdir(options.outputPath, { recursive: true });
      
      const container = this.docker.getContainer(containerId);
      const containerInfo = await container.inspect();
      
      // Export container filesystem
      const containerStream = await container.export();
      const containerTarPath = path.join(options.outputPath, 'container.tar');
      await this.writeStreamToFile(containerStream, containerTarPath);
      
      // Export volumes if requested
      if (options.includeVolumes) {
        await this.exportVolumes(containerId, options.outputPath);
      }
      
      // Export container configuration if requested
      if (options.includeConfig) {
        const configPath = path.join(options.outputPath, 'container-config.json');
        await fs.promises.writeFile(
          configPath,
          JSON.stringify(containerInfo.Config, null, 2)
        );
      }
      
      // Create a deployment manifest
      const manifest = {
        containerId,
        exportDate: new Date().toISOString(),
        options,
        containerInfo: {
          name: containerInfo.Name,
          image: containerInfo.Config.Image,
          state: containerInfo.State.Status,
          created: containerInfo.Created
        }
      };
      
      await fs.promises.writeFile(
        path.join(options.outputPath, 'deployment-manifest.json'),
        JSON.stringify(manifest, null, 2)
      );
      
      // Create final archive
      const archivePath = path.join(options.outputPath, 'container-export.tar.gz');
      await tar.create(
        {
          gzip: true,
          file: archivePath,
          cwd: options.outputPath
        },
        ['container.tar', 'volumes', 'container-config.json', 'deployment-manifest.json']
      );
      
      this.logger.info(`Container exported successfully to ${archivePath}`);
      return archivePath;
    } catch (error) {
      this.logger.error(`Failed to export container ${containerId}`, error);
      throw error;
    }
  }

  /**
   * Export container volumes to a specified directory
   */
  private async exportVolumes(containerId: string, outputPath: string): Promise<void> {
    const container = this.docker.getContainer(containerId);
    const containerInfo = await container.inspect();
    
    const volumesPath = path.join(outputPath, 'volumes');
    await fs.promises.mkdir(volumesPath, { recursive: true });
    
    for (const [volumeName, volumeInfo] of Object.entries(containerInfo.Mounts)) {
      if (volumeInfo.Type === 'volume') {
        const volumePath = path.join(volumesPath, volumeName);
        await fs.promises.mkdir(volumePath, { recursive: true });
        
        // Create a temporary container to copy volume contents
        const tempContainer = await this.docker.createContainer({
          Image: 'alpine',
          Cmd: ['sh', '-c', `cp -r ${volumeInfo.Source}/* /export/`],
          Volumes: {
            '/export': {}
          },
          HostConfig: {
            Binds: [`${volumePath}:/export`]
          }
        });
        
        await tempContainer.start();
        await tempContainer.wait();
        await tempContainer.remove();
      }
    }
  }

  /**
   * Deploy a container to a target environment
   */
  async deployContainer(exportPath: string, options: DeploymentOptions): Promise<void> {
    try {
      this.logger.info('Starting container deployment');
      
      // Extract the export archive
      const extractPath = path.join(path.dirname(exportPath), 'deploy-temp');
      await fs.promises.mkdir(extractPath, { recursive: true });
      
      await tar.extract({
        file: exportPath,
        cwd: extractPath
      });
      
      // Read deployment manifest
      const manifest = JSON.parse(
        await fs.promises.readFile(
          path.join(extractPath, 'deployment-manifest.json'),
          'utf8'
        )
      );
      
      if (options.target === 'local') {
        await this.deployToLocal(extractPath, manifest);
      } else if (options.target === 'remote') {
        await this.deployToRemote(extractPath, manifest, options);
      }
      
      // Cleanup
      await fs.promises.rm(extractPath, { recursive: true, force: true });
      
      this.logger.info('Container deployed successfully');
    } catch (error) {
      this.logger.error('Failed to deploy container', error);
      throw error;
    }
  }

  /**
   * Deploy container to local Docker environment
   */
  private async deployToLocal(extractPath: string, manifest: any): Promise<void> {
    // Import container image
    const imageStream = fs.createReadStream(path.join(extractPath, 'container.tar'));
    await this.docker.importImage(imageStream);
    
    // Create and start container
    const containerConfig = JSON.parse(
      await fs.promises.readFile(
        path.join(extractPath, 'container-config.json'),
        'utf8'
      )
    );
    
    const container = await this.docker.createContainer({
      ...containerConfig,
      name: `${manifest.containerInfo.name}-deployed`
    });
    
    await container.start();
  }

  /**
   * Deploy container to remote environment
   */
  private async deployToRemote(
    extractPath: string,
    manifest: any,
    options: DeploymentOptions
  ): Promise<void> {
    if (!options.remoteUrl || !options.credentials) {
      throw new Error('Remote URL and credentials are required for remote deployment');
    }
    
    // Tag and push container image
    const image = manifest.containerInfo.image;
    const registry = options.credentials.registry || 'docker.io';
    const taggedImage = `${registry}/${options.credentials.username}/${path.basename(image)}`;
    
    await this.docker.getImage(image).tag({ repo: taggedImage });
    
    // Push image to registry
    const pushStream = await this.docker.getImage(taggedImage).push({
      authconfig: {
        username: options.credentials.username,
        password: options.credentials.password
      }
    });
    
    await this.waitForStream(pushStream);
    
    // Deploy to remote environment (implementation depends on the target platform)
    // This could involve:
    // 1. SSH into remote server
    // 2. Pull and run container
    // 3. Set up networking and volumes
    // 4. Configure environment variables
    // 5. Start the application
    
    // Example using SSH (requires additional implementation)
    // await this.deployViaSSH(options.remoteUrl, taggedImage, manifest);
  }

  /**
   * Helper method to write a stream to a file
   */
  private async writeStreamToFile(stream: NodeJS.ReadableStream, filePath: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const writeStream = fs.createWriteStream(filePath);
      stream.pipe(writeStream);
      writeStream.on('finish', resolve);
      writeStream.on('error', reject);
    });
  }

  /**
   * Helper method to wait for a stream to complete
   */
  private async waitForStream(stream: NodeJS.ReadableStream): Promise<void> {
    return new Promise((resolve, reject) => {
      stream.on('end', resolve);
      stream.on('error', reject);
    });
  }
} 