import { IContainerManager, ContainerStatus, ResourceUsage, CommandResult } from './interfaces/IContainerManager';
import {
  ContainerConfig,
  ContainerTemplate,
  ProjectType,
  ResourceAllocation,
  ProjectConfig,
  ContainerState,
  ContainerHealth
} from './types';
import { Docker } from 'dockerode';
import { EventEmitter } from 'events';
import { Logger } from '../logging/Logger';

export class ContainerManager extends EventEmitter implements IContainerManager {
  private docker: Docker;
  private logger: Logger;
  private templates: Map<ProjectType, ContainerTemplate>;
  private activeContainers: Map<string, ContainerStatus>;

  constructor() {
    super();
    this.docker = new Docker();
    this.logger = new Logger('ContainerManager');
    this.templates = new Map();
    this.activeContainers = new Map();
    this.initializeTemplates();
  }

  private async initializeTemplates(): Promise<void> {
    try {
      // Load templates from configuration
      const templates = await this.loadTemplates();
      templates.forEach(template => {
        this.templates.set(template.projectType, template);
      });
      this.logger.info('Container templates initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize container templates', error);
      throw error;
    }
  }

  private async loadTemplates(): Promise<ContainerTemplate[]> {
    // TODO: Load templates from configuration files or database
    return [];
  }

  async createContainer(config: ContainerConfig): Promise<string> {
    try {
      this.logger.info(`Creating container with config: ${JSON.stringify(config)}`);
      
      const container = await this.docker.createContainer({
        Image: config.image,
        name: config.name,
        Env: config.environment.map(env => `${env.name}=${env.value}`),
        Cmd: config.command,
        WorkingDir: config.workingDir,
        User: config.user,
        HostConfig: {
          PortBindings: this.createPortBindings(config.ports),
          Binds: this.createVolumeBinds(config.volumes),
          NetworkMode: config.networks[0]?.name,
          Resources: {
            CpuPeriod: 100000,
            CpuQuota: Math.floor(config.resources.cpu.limit * 100000),
            Memory: this.parseMemoryString(config.resources.memory.limit),
            MemorySwap: this.parseMemoryString(config.resources.memory.limit),
            MemoryReservation: this.parseMemoryString(config.resources.memory.reservation)
          }
        },
        Healthcheck: config.healthCheck ? {
          Test: config.healthCheck.test,
          Interval: this.parseDuration(config.healthCheck.interval),
          Timeout: this.parseDuration(config.healthCheck.timeout),
          Retries: config.healthCheck.retries,
          StartPeriod: this.parseDuration(config.healthCheck.startPeriod)
        } : undefined
      });

      const containerId = container.id;
      await this.updateContainerStatus(containerId);
      this.emit('container:created', containerId);
      
      return containerId;
    } catch (error) {
      this.logger.error('Failed to create container', error);
      throw error;
    }
  }

  async startContainer(containerId: string): Promise<void> {
    try {
      const container = this.docker.getContainer(containerId);
      await container.start();
      await this.updateContainerStatus(containerId);
      this.emit('container:started', containerId);
    } catch (error) {
      this.logger.error(`Failed to start container ${containerId}`, error);
      throw error;
    }
  }

  async stopContainer(containerId: string): Promise<void> {
    try {
      const container = this.docker.getContainer(containerId);
      await container.stop();
      await this.updateContainerStatus(containerId);
      this.emit('container:stopped', containerId);
    } catch (error) {
      this.logger.error(`Failed to stop container ${containerId}`, error);
      throw error;
    }
  }

  async deleteContainer(containerId: string): Promise<void> {
    try {
      const container = this.docker.getContainer(containerId);
      await container.remove({ force: true });
      this.activeContainers.delete(containerId);
      this.emit('container:deleted', containerId);
    } catch (error) {
      this.logger.error(`Failed to delete container ${containerId}`, error);
      throw error;
    }
  }

  async pauseContainer(containerId: string): Promise<void> {
    try {
      const container = this.docker.getContainer(containerId);
      await container.pause();
      await this.updateContainerStatus(containerId);
      this.emit('container:paused', containerId);
    } catch (error) {
      this.logger.error(`Failed to pause container ${containerId}`, error);
      throw error;
    }
  }

  async resumeContainer(containerId: string): Promise<void> {
    try {
      const container = this.docker.getContainer(containerId);
      await container.unpause();
      await this.updateContainerStatus(containerId);
      this.emit('container:resumed', containerId);
    } catch (error) {
      this.logger.error(`Failed to resume container ${containerId}`, error);
      throw error;
    }
  }

  async getContainerStatus(containerId: string): Promise<ContainerStatus> {
    const status = this.activeContainers.get(containerId);
    if (!status) {
      throw new Error(`Container ${containerId} not found`);
    }
    return status;
  }

  async getContainerLogs(containerId: string): Promise<string> {
    try {
      const container = this.docker.getContainer(containerId);
      const logs = await container.logs({
        stdout: true,
        stderr: true,
        timestamps: true
      });
      return logs.toString();
    } catch (error) {
      this.logger.error(`Failed to get logs for container ${containerId}`, error);
      throw error;
    }
  }

  async getContainerResources(containerId: string): Promise<ResourceUsage> {
    try {
      const container = this.docker.getContainer(containerId);
      const stats = await container.stats({ stream: false });
      return this.parseContainerStats(stats);
    } catch (error) {
      this.logger.error(`Failed to get resources for container ${containerId}`, error);
      throw error;
    }
  }

  async getContainerTemplate(projectType: ProjectType): Promise<ContainerTemplate> {
    const template = this.templates.get(projectType);
    if (!template) {
      throw new Error(`No template found for project type: ${projectType}`);
    }
    return template;
  }

  async listAvailableTemplates(): Promise<ContainerTemplate[]> {
    return Array.from(this.templates.values());
  }

  async allocateResources(containerId: string, allocation: ResourceAllocation): Promise<void> {
    try {
      const container = this.docker.getContainer(containerId);
      await container.update({
        CpuPeriod: 100000,
        CpuQuota: Math.floor(allocation.cpu.limit * 100000),
        Memory: this.parseMemoryString(allocation.memory.limit),
        MemorySwap: this.parseMemoryString(allocation.memory.limit),
        MemoryReservation: this.parseMemoryString(allocation.memory.reservation)
      });
      this.emit('container:resources:updated', containerId, allocation);
    } catch (error) {
      this.logger.error(`Failed to allocate resources for container ${containerId}`, error);
      throw error;
    }
  }

  async updateResourceAllocation(containerId: string, allocation: ResourceAllocation): Promise<void> {
    await this.allocateResources(containerId, allocation);
  }

  async initializeProjectContainer(projectConfig: ProjectConfig): Promise<string> {
    try {
      const template = await this.getContainerTemplate(projectConfig.type);
      const containerConfig = this.createContainerConfigFromTemplate(template, projectConfig);
      const containerId = await this.createContainer(containerConfig);
      await this.startContainer(containerId);
      return containerId;
    } catch (error) {
      this.logger.error('Failed to initialize project container', error);
      throw error;
    }
  }

  async executeCommand(containerId: string, command: string): Promise<CommandResult> {
    try {
      const container = this.docker.getContainer(containerId);
      const exec = await container.exec({
        Cmd: command.split(' '),
        AttachStdout: true,
        AttachStderr: true
      });
      const stream = await exec.start({ hijack: true, stdin: false });
      return this.handleCommandStream(stream);
    } catch (error) {
      this.logger.error(`Failed to execute command in container ${containerId}`, error);
      throw error;
    }
  }

  async copyFileToContainer(containerId: string, sourcePath: string, targetPath: string): Promise<void> {
    try {
      const container = this.docker.getContainer(containerId);
      await container.putArchive(sourcePath, { path: targetPath });
    } catch (error) {
      this.logger.error(`Failed to copy file to container ${containerId}`, error);
      throw error;
    }
  }

  async copyFileFromContainer(containerId: string, sourcePath: string, targetPath: string): Promise<void> {
    try {
      const container = this.docker.getContainer(containerId);
      const stream = await container.getArchive({ path: sourcePath });
      // TODO: Implement file extraction from stream
    } catch (error) {
      this.logger.error(`Failed to copy file from container ${containerId}`, error);
      throw error;
    }
  }

  private async updateContainerStatus(containerId: string): Promise<void> {
    try {
      const container = this.docker.getContainer(containerId);
      const info = await container.inspect();
      const status: ContainerStatus = {
        id: containerId,
        name: info.Name,
        state: this.mapContainerState(info.State.Status),
        health: this.mapContainerHealth(info.State.Health?.Status),
        uptime: Date.now() - new Date(info.State.StartedAt).getTime(),
        lastUpdated: new Date()
      };
      this.activeContainers.set(containerId, status);
    } catch (error) {
      this.logger.error(`Failed to update container status for ${containerId}`, error);
      throw error;
    }
  }

  private createPortBindings(ports: PortMapping[]): Record<string, any> {
    return ports.reduce((acc, port) => {
      acc[`${port.containerPort}/${port.protocol}`] = [{ HostPort: port.hostPort.toString() }];
      return acc;
    }, {});
  }

  private createVolumeBinds(volumes: VolumeMount[]): string[] {
    return volumes.map(volume => `${volume.source}:${volume.target}`);
  }

  private parseMemoryString(memory: string): number {
    const units = {
      'b': 1,
      'k': 1024,
      'm': 1024 * 1024,
      'g': 1024 * 1024 * 1024
    };
    const match = memory.match(/^(\d+)([bkmg])$/i);
    if (!match) {
      throw new Error(`Invalid memory format: ${memory}`);
    }
    return parseInt(match[1]) * units[match[2].toLowerCase()];
  }

  private parseDuration(duration: string): number {
    const match = duration.match(/^(\d+)([smhd])$/i);
    if (!match) {
      throw new Error(`Invalid duration format: ${duration}`);
    }
    const units = {
      's': 1000000000,
      'm': 60000000000,
      'h': 3600000000000,
      'd': 86400000000000
    };
    return parseInt(match[1]) * units[match[2].toLowerCase()];
  }

  private mapContainerState(state: string): ContainerState {
    switch (state) {
      case 'created': return ContainerState.CREATED;
      case 'running': return ContainerState.RUNNING;
      case 'paused': return ContainerState.PAUSED;
      case 'stopped': return ContainerState.STOPPED;
      default: return ContainerState.STOPPED;
    }
  }

  private mapContainerHealth(health: string | undefined): ContainerHealth {
    switch (health) {
      case 'healthy': return ContainerHealth.HEALTHY;
      case 'unhealthy': return ContainerHealth.UNHEALTHY;
      case 'starting': return ContainerHealth.STARTING;
      default: return ContainerHealth.UNKNOWN;
    }
  }

  private parseContainerStats(stats: any): ResourceUsage {
    // TODO: Implement container stats parsing
    return {
      cpu: { usage: 0, limit: 0, percentage: 0 },
      memory: { usage: 0, limit: 0, percentage: 0 },
      disk: { usage: 0, limit: 0, percentage: 0 },
      network: { bytesReceived: 0, bytesSent: 0 }
    };
  }

  private handleCommandStream(stream: any): Promise<CommandResult> {
    return new Promise((resolve, reject) => {
      let stdout = '';
      let stderr = '';
      let exitCode = 0;

      stream.on('data', (chunk: Buffer) => {
        const header = chunk.slice(0, 8);
        const content = chunk.slice(8);
        const type = header[0];
        
        if (type === 1) {
          stdout += content.toString();
        } else if (type === 2) {
          stderr += content.toString();
        }
      });

      stream.on('end', () => {
        resolve({ exitCode, stdout, stderr });
      });

      stream.on('error', reject);
    });
  }

  private createContainerConfigFromTemplate(
    template: ContainerTemplate,
    projectConfig: ProjectConfig
  ): ContainerConfig {
    return {
      name: `${projectConfig.name}-${Date.now()}`,
      image: template.baseImage,
      projectType: projectConfig.type,
      resources: {
        ...template.defaultResources,
        ...projectConfig.resources
      },
      environment: [
        ...template.defaultEnvironment,
        ...projectConfig.environment
      ],
      ports: [
        ...template.defaultPorts,
        ...projectConfig.ports
      ],
      volumes: [
        ...template.defaultVolumes,
        ...projectConfig.volumes
      ],
      networks: [
        ...template.defaultNetworks,
        ...projectConfig.networks
      ],
      healthCheck: template.defaultHealthCheck,
      command: template.defaultCommand,
      workingDir: template.defaultWorkingDir,
      user: template.defaultUser
    };
  }
} 